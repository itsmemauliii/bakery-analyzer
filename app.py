import matplotlib
matplotlib.use("Agg")  # safe backend for Streamlit Cloud

import streamlit as st
import pandas as pd
from scraper import scrape_website
from nlp_utils import clean_text, extract_keywords, sentiment_analysis, readability, extract_products, extract_entities, detect_seasonal_specials
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Bakery Website Analyzer", layout="wide")
st.title("🍩 Bakery Website NLP Analyzer")
st.write("Paste your bakery website URL and let’s see what flavors your words reveal!")

# PDF builder
def build_pdf(url, df, polarity, subjectivity, avg_word_len, summary, suggestions, wc_png_bytes, products, entities, seasonal):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 2 * cm
    y = height - 2 * cm

    def line(txt, font="Helvetica", size=11, gap=0.5*cm):
        nonlocal y
        c.setFont(font, size)
        max_chars = 95
        words = txt.split()
        current = ""
        for w in words:
            if len(current) + len(w) + 1 > max_chars:
                c.drawString(left, y, current)
                y -= gap
                current = w
            else:
                current = (current + " " + w).strip()
        if current:
            c.drawString(left, y, current)
            y -= gap

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, y, "Bakery Website NLP Report")
    y -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(left, y, f"URL: {url}")
    y -= 0.5 * cm
    c.drawString(left, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 1 * cm

    # Products
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Items Found")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    for item, freq in products:
        line(f"{item.capitalize()} – {freq} mentions")

    # Sentiment
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Tone & Readability")
    y -= 0.7 * cm
    line(f"Polarity {polarity:.2f}, Subjectivity {subjectivity:.2f}, Avg word length {avg_word_len:.2f}")

    # Entities
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Brand Mentions / Entities")
    y -= 0.7 * cm
    for e in entities:
        line(f"- {e}")

    # Seasonal
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Seasonal Specials")
    y -= 0.7 * cm
    if seasonal:
        for word, tip in seasonal:
            line(f"{word}: {tip}")
    else:
        line("No seasonal specials found.")

    # Suggestions
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Marketing Suggestions")
    y -= 0.7 * cm
    for s in suggestions:
        line(f"• {s}")

    # WordCloud
    y -= 1 * cm
    try:
        img = ImageReader(BytesIO(wc_png_bytes))
        c.drawImage(img, left, y-8*cm, width=12*cm, height=8*cm)
    except:
        line("WordCloud unavailable")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# MAIN
url = st.text_input("Enter Bakery Website URL", "https://www.example.com")

if st.button("Analyze"):
    with st.spinner("Scraping & analyzing..."):
        text = scrape_website(url)
        if text.startswith("Error"):
            st.error(text)
        else:
            cleaned = clean_text(text)

            # Extract products
            products = extract_products(cleaned)
            st.subheader("🥐 Items Available")
            if products:
                df_products = pd.DataFrame(products, columns=["Item", "Mentions"])
                st.table(df_products)
            else:
                st.write("No bakery items clearly found.")

            # Keywords
            keywords = extract_keywords(cleaned, top_n=15)
            df_keywords = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
            st.subheader("🔑 Top Keywords")
            st.table(df_keywords)

            # Sentiment
            polarity, subjectivity = sentiment_analysis(cleaned)
            st.subheader("💬 Sentiment Analysis")
            sentiment_label = "😊 Positive" if polarity > 0 else "😐 Neutral" if polarity == 0 else "☹️ Negative"
            st.write(f"Polarity: {polarity:.2f} → {sentiment_label}")
            st.write(f"Subjectivity: {subjectivity:.2f}")

            # Readability
            avg_len = readability(cleaned)
            st.subheader("📖 Readability Check")
            st.write(f"Average word length: {avg_len:.2f}")

            # Entities
            entities = extract_entities(cleaned)
            st.subheader("🏷 Brand Mentions / Entities")
            st.write(entities)

            # Seasonal Specials
            seasonal = detect_seasonal_specials(cleaned)
            st.subheader("🎉 Seasonal Specials")
            if seasonal:
                for word, tip in seasonal:
                    st.markdown(f"- **{word}** → {tip}")
            else:
                st.write("No seasonal promotions detected.")

            # WordCloud
            wc = WordCloud(width=800, height=400, background_color="white").generate(cleaned)
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            wc_png_bytes = buf.getvalue()

            # Suggestions
            st.subheader("📊 Marketing Suggestions")
            suggestions = []
            if polarity < 0:
                suggestions.append("Tone feels negative — use warmer wording.")
            if subjectivity < 0.3:
                suggestions.append("Very factual — add testimonials.")
            if "cake" not in [i for i, _ in products]:
                suggestions.append("Highlight cakes more, customers look for them.")
            if "chocolate" not in [i for i, _ in products]:
                suggestions.append("Add chocolate items to attract dessert lovers.")
            if not suggestions:
                suggestions.append("Looks balanced. Keep it up!")

            for s in suggestions:
                st.markdown(f"- {s}")

            # PDF download
            pdf_bytes = build_pdf(url, df_keywords, polarity, subjectivity, avg_len,
                                  "Summary", suggestions, wc_png_bytes, products, entities, seasonal)
            st.download_button("📄 Download PDF Report", data=pdf_bytes,
                               file_name="bakery_nlp_report.pdf", mime="application/pdf")
