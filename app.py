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
from reportlab.lib import colors

st.set_page_config(page_title="Bakery Website Analyzer", layout="wide")
st.title("🍩 Bakery Website NLP Analyzer")
st.write("Paste your bakery website URL and let’s see what flavors your words reveal!")

# ---------- PDF BUILDER ----------
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

    def draw_tag(label, x, y, bg_color, text_color=colors.white):
        c.setFillColor(bg_color)
        c.roundRect(x, y-10, len(label)*4.5, 14, 3, fill=1, stroke=0)
        c.setFillColor(text_color)
        c.setFont("Helvetica", 9)
        c.drawString(x+2, y-8, label)

    # ---------- Header ----------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, y, "Bakery Website NLP Report")
    y -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(left, y, f"URL: {url}")
    y -= 0.5 * cm
    c.drawString(left, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 1 * cm

    # ---------- Items ----------
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "🥐 Items Found")
    y -= 1 * cm
    x_pos = left
    for item, freq in products:
        draw_tag(f"{item.capitalize()} ({freq})", x_pos, y, colors.green)
        x_pos += len(item)*10 + 40
        if x_pos > width - 5*cm:
            x_pos = left
            y -= 20
    y -= 30

    # ---------- Sentiment ----------
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "💬 Tone & Readability")
    y -= 0.7 * cm
    line(f"Polarity {polarity:.2f}, Subjectivity {subjectivity:.2f}, Avg word length {avg_word_len:.2f}")

    # ---------- Entities ----------
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "🏷 Brand Mentions / Entities")
    y -= 1 * cm
    x_pos = left
    for e in entities:
        draw_tag(e.capitalize(), x_pos, y, colors.blue)
        x_pos += len(e)*10 + 40
        if x_pos > width - 5*cm:
            x_pos = left
            y -= 20
    y -= 30

    # ---------- Seasonal Specials ----------
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "🎉 Seasonal Specials")
    y -= 1 * cm
    if seasonal:
        x_pos = left
        for word, tip in seasonal:
            draw_tag(word, x_pos, y, colors.red)
            x_pos += len(word)*10 + 40
            if x_pos > width - 5*cm:
                x_pos = left
                y -= 20
        y -= 20
        for _, tip in seasonal:
            line(f"• {tip}")
    else:
        line("No seasonal specials found.")

    # ---------- Suggestions ----------
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "📊 Marketing Suggestions")
    y -= 0.7 * cm
    for s in suggestions:
        line(f"• {s}")

    # ---------- WordCloud ----------
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

# ---------- MAIN APP ----------
url = st.text_input("Enter bakery website URL:", "")

if url:
    with st.spinner("Scraping website..."):
        text = scrape_website(url)

    cleaned = clean_text(text)
    keywords = extract_keywords(cleaned)
    polarity, subjectivity = sentiment_analysis(cleaned)
    avg_len = readability(cleaned)
    products = extract_products(cleaned)
    entities = extract_entities(cleaned)
    seasonal = detect_seasonal_specials(cleaned)

    # Keywords
    st.subheader("🔑 Top Keywords")
    df_keywords = pd.DataFrame(keywords, columns=["Word", "Frequency"])
    st.table(df_keywords)

    # Items as Green Tags
    st.subheader("🍞 Items Available on Website")
    if products:
        tags_html = ""
        for item, freq in products:
            tags_html += f"""
            <span style="
                background-color:#16a34a;
                color:white;
                padding:4px 10px;
                border-radius:15px;
                margin:4px;
                display:inline-block;
                font-size:13px;
            ">{item.capitalize()} ({freq})</span>
            """
        st.markdown(tags_html, unsafe_allow_html=True)
    else:
        st.write("No clear bakery items found.")

    # Entities as Blue Tags
    st.subheader("🏷 Brand Mentions / Entities")
    if entities:
        tags_html = ""
        for e in entities:
            tags_html += f"""
            <span style="
                background-color:#2563eb;
                color:white;
                padding:4px 10px;
                border-radius:15px;
                margin:4px;
                display:inline-block;
                font-size:13px;
            ">{e.capitalize()}</span>
            """
        st.markdown(tags_html, unsafe_allow_html=True)
    else:
        st.write("No clear entities found.")

    # Seasonal Specials as Red Tags
    st.subheader("🎉 Seasonal Specials")
    if seasonal:
        tags_html = ""
        for word, tip in seasonal:
            tags_html += f"""
            <span style="
                background-color:#dc2626;
                color:white;
                padding:4px 10px;
                border-radius:15px;
                margin:4px;
                display:inline-block;
                font-size:13px;
            ">{word}</span>
            """
        st.markdown(tags_html, unsafe_allow_html=True)
        for _, tip in seasonal:
            st.markdown(f"- {tip}")
    else:
        st.write("No seasonal promotions detected.")

    # Sentiment
    st.subheader("💬 Tone & Readability")
    st.write(f"Polarity: {polarity:.2f}, Subjectivity: {subjectivity:.2f}, Avg word length: {avg_len:.2f}")

    # WordCloud
    st.subheader("☁️ WordCloud")
    wc = WordCloud(width=800, height=400, background_color="white").generate(cleaned)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # Marketing Suggestions
    st.subheader("📊 Marketing Suggestions")
    suggestions = []
    if not any("cake" in p for p, _ in products):
        suggestions.append("Consider highlighting cakes more — they are often a bakery’s signature product.")
    if not any("chocolate" in k for k, _ in keywords):
        suggestions.append("Chocolate is missing! Adding more chocolate references could attract dessert lovers.")
    if polarity < 0:
        suggestions.append("Tone seems negative — consider adding more positive wording.")
    if subjectivity < 0.3:
        suggestions.append("Your tone is very factual — consider adding personal stories or customer testimonials.")
    if subjectivity > 0.7:
        suggestions.append("Your tone is very subjective — balance with factual info.")
    if not suggestions:
        suggestions.append("Content balance looks strong. Keep it up!")

    for s in suggestions:
        st.markdown(f"- {s}")

    # PDF Export
    st.subheader("📄 Download Report")
    buf = BytesIO()
    wc_buf = BytesIO()
    wc.to_image().save(wc_buf, format="PNG")
    pdf_bytes = build_pdf(url, df_keywords, polarity, subjectivity, avg_len,
                          "Summary", suggestions, wc_buf.getvalue(), products, entities, seasonal)
    st.download_button("📥 Download PDF", data=pdf_bytes, file_name="bakery_report.pdf", mime="application/pdf")
