import matplotlib
matplotlib.use("Agg")  # ✅ fix for Streamlit Cloud (no GUI backend)

import streamlit as st
from scraper import scrape_website
from nlp_utils import clean_text, extract_keywords, sentiment_analysis, readability
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bakery Website Analyzer", layout="wide")

st.title("🍰 Bakery Website NLP Analyzer")
st.write("Paste your bakery website URL and let’s see what flavors your words reveal!")

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

            import pandas as pd
            import matplotlib.pyplot as plt

            df = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
            st.table(df)

            # Bar chart of keywords
            st.bar_chart(df.set_index("Keyword"))

            # Sentiment
            polarity, subjectivity = sentiment_analysis(cleaned)
            st.subheader("💬 Sentiment Analysis")
            sentiment_label = "😊 Positive" if polarity > 0 else "😐 Neutral" if polarity == 0 else "☹️ Negative"
            st.write(f"Polarity: {polarity:.2f} → {sentiment_label}")
            st.write(f"Subjectivity: {subjectivity:.2f} (0 = objective, 1 = personal opinion)")

            # Readability
            st.subheader("📖 Readability Check")
            st.write(f"Average word length: {readability(cleaned)}")

            # WordCloud
            st.subheader("☁️ WordCloud of Bakery Words")
            wc = WordCloud(width=800, height=400, background_color="white").generate(cleaned)
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

st.markdown("---")
st.markdown("Built with ❤️ by Mauli Patel")
