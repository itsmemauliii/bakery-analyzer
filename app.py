import matplotlib
matplotlib.use("Agg")  # ✅ safe backend for Streamlit Cloud

import streamlit as st
import pandas as pd
from scraper import scrape_website
from nlp_utils import clean_text, extract_keywords, sentiment_analysis, readability
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from io import BytesIO
from datetime import datetime

# PDF bits
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Bakery Website Analyzer", layout="wide")
st.title("🍰 Bakery Website NLP Analyzer")
st.write("Paste your bakery website URL and let’s see what flavors your words reveal!")

def build_pdf(url, df, polarity, subjectivity, avg_word_len, summary, suggestions, wc_png_bytes):
    """Create a simple, clean PDF and return bytes."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 2 * cm
    right = width - 2 * cm
    y = height - 2 * cm

    def line(txt, font="Helvetica", size=11, gap=0.5*cm):
        nonlocal y
        c.setFont(font, size)
        # simple wrap
        max_chars = 95 if size <= 11 else 80
        words = txt.split()
        current = ""
        for w in words:
            if len(current) + len(w) + 1 > max_chars:
                c.drawString(left, y, current)
                y -= gap
                if y < 2*cm:
                    c.showPage(); y = height - 2*cm
                    c.setFont(font, size)
                current = w
            else:
                current = (current + " " + w).strip()
        if current:
            c.drawString(left, y, current)
            y -= gap
            if y < 2*cm:
                c.showPage(); y = height - 2*cm

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, y, "Bakery Website NLP Report")
    y -= 0.9 * cm
    c.setFont("Helvetica", 10)
    c.drawString(left, y, f"URL: {url}")
    y -= 0.5 * cm
    c.drawString(left, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.9 * cm

    # Keywords section
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Top Keywords")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    if df.empty:
        line("No keywords extracted.")
    else:
        # print two columns if space allows
        pairs = [f"{k}: {int(v)}" for k, v in df.values]
        col_split = (len(pairs) + 1) // 2
        col1 = pairs[:col_split]
        col2 = pairs[col_split:]

        max_rows = max(len(col1), len(col2))
        for i in range(max_rows):
            left_text = col1[i] if i < len(col1) else ""
            right_text = col2[i] if i < len(col2) else ""
            c.drawString(left, y, left_text)
            if right_text:
                c.drawString(left + 7*cm, y, right_text)
            y -= 0.5 * cm
            if y < 2*cm:
                c.showPage(); y = height - 2*cm
                c.setFont("Helvetica", 11)

    y -= 0.4 * cm

    # Sentiment & readability
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Tone & Readability")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    tone = "Positive" if polarity > 0 else "Neutral" if polarity == 0 else "Negative"
    line(f"Sentiment: {tone} (polarity {polarity:.2f}, subjectivity {subjectivity:.2f}).")
    line(f"Average word length: {avg_word_len:.2f}.")

    # Summary
    y -= 0.2 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Insights Summary")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    line(summary)

    # Suggestions
    y -= 0.2 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "Marketing Suggestions")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    if suggestions:
        for s in suggestions:
            line(f"• {s}")
    else:
        line("• Content balance looks strong. Keep it up!")

    # Wordcloud image
    # start a new page if not enough room
    if y < 10*cm:
        c.showPage(); y = height - 2*cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "WordCloud")
    y -= 0.7 * cm
    try:
        img = ImageReader(BytesIO(wc_png_bytes))
        # keep aspect ratio within bounds
        img_w = 14 * cm
        img_h = 8 * cm
        c.drawImage(img, left, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
        y -= (img_h + 0.5*cm)
    except Exception:
        line("WordCloud image unavailable in this session.")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

url = st.text_input("Enter Bakery Website URL", "https://www.example.com")

if st.button("Analyze"):
    with st.spinner("Scraping & analyzing..."):
        text = scrape_website(url)
        if text.startswith("Error"):
            st.error(text)
        else:
            cleaned = clean_text(text)

            # Keywords
            keywords = extract_keywords(cleaned, top_n=10)
            st.subheader("🔑 Top Keywords (Signature Flavors)")
            df = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
            st.table(df)
            st.bar_chart(df.set_index("Keyword"))  # pretty bar chart

            # Sentiment
            polarity, subjectivity = sentiment_analysis(cleaned)
            st.subheader("💬 Sentiment Analysis")
            sentiment_label = "😊 Positive" if polarity > 0 else "😐 Neutral" if polarity == 0 else "☹️ Negative"
            st.write(f"Polarity: {polarity:.2f} → {sentiment_label}")
            st.write(f"Subjectivity: {subjectivity:.2f} (0 = objective, 1 = personal opinion)")

            # Readability
            avg_len = readability(cleaned)
            st.subheader("📖 Readability Check")
            st.write(f"Average word length: {avg_len}")

            # WordCloud
            st.subheader("☁️ WordCloud of Bakery Words")
            wc = WordCloud(width=800, height=400, background_color="white").generate(cleaned)
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

            # Save wordcloud image to bytes for PDF
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            wc_png_bytes = buf.getvalue()
            buf.close()

            # Insights Summary
            st.subheader("📝 Insights Summary")
            top_word = df.iloc[0]["Keyword"] if not df.empty else "bakery"
            tone = "positive" if polarity > 0 else "neutral" if polarity == 0 else "negative"
            summary = (
                f"This bakery’s website strongly emphasizes **{top_word}**, "
                f"showing it as a key highlight in their offerings. "
                f"The overall tone of the site feels **{tone}**, "
                f"with language that leans {'towards personal storytelling' if subjectivity > 0.5 else 'more factual descriptions'}. "
                f"Average word length of {avg_len} suggests their content is written in a "
                f"{'simple, approachable style' if avg_len < 6 else 'more formal style'}."
            )
            st.write(summary)

            # Marketing Suggestions (rule-based, fast & free)
            st.subheader("📊 Marketing Suggestions")
            suggestions = []
            if not df.empty:
                top_keywords = [k.lower() for k in df["Keyword"].tolist()]
                if "cake" not in top_keywords:
                    suggestions.append("Consider highlighting cakes more — they’re a key bakery draw.")
                if "chocolate" not in top_keywords:
                    suggestions.append("Add more chocolate references; it converts dessert lovers.")
                if polarity < 0:
                    suggestions.append("Tone leans negative — use warmer, more inviting wording.")
                if subjectivity < 0.3:
                    suggestions.append("Very factual tone — sprinkle in stories or testimonials.")
                if subjectivity > 0.7:
                    suggestions.append("Very personal tone — balance with clear product details (prices, sizes).")
                # small SEO nudge
                if "wedding" not in top_keywords and "birthday" in top_keywords:
                    suggestions.append("You mention birthdays but not weddings — add wedding cakes to expand occasions.")
                if "delivery" not in top_keywords:
                    suggestions.append("If you deliver, state it clearly — ‘same-day delivery’ boosts conversions.")

            if suggestions:
                for s in suggestions:
                    st.markdown(f"- {s}")
            else:
                st.markdown("✅ Content balance looks strong. Keep it up!")

            # 📄 Download PDF report
            pdf_bytes = build_pdf(
                url=url,
                df=df,
                polarity=polarity,
                subjectivity=subjectivity,
                avg_word_len=avg_len,
                summary=summary.replace("**", ""),  # plain text for PDF
                suggestions=suggestions,
                wc_png_bytes=wc_png_bytes
            )
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="bakery_nlp_report.pdf",
                mime="application/pdf",
                type="primary",
            )

st.markdown("---")
st.markdown("Built with ❤️ by Mauli Patel")
