import streamlit as st
import requests, re
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

st.set_page_config(page_title="🍰 Your Bakery Helper", layout="wide")
st.title("🍞 Your Bakery Helper – Smart Bakery Store Analyzer")

option = st.radio("Choose Input Method:", ["🌐 Website URL", "📂 Upload CSV"])

# ---------------- Website Analysis ---------------- #
if option == "🌐 Website URL":
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.bakingo.com")

    if st.button("🔍 Analyze Website"):
        try:
            html = requests.get(url, timeout=8).text
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True).lower()

            items = ["cake","cakes","cookies","pastry","pastries","bread",
                     "cupcake","brownie","pizza","bun","biscuits","gift"]

            found = {i: len(re.findall(rf"\b{i}\b", text)) for i in items if re.search(rf"\b{i}\b", text)}
            sentiment = sia.polarity_scores(text)
            health = int((sentiment["pos"] * 100))

            col1, col2 = st.columns([1.3,1])
            with col1:
                st.subheader("🎂 Items Found")
                df = pd.DataFrame(found.items(), columns=["Item","Count"]).sort_values("Count", ascending=False)
                st.dataframe(df, use_container_width=True)

                st.subheader("☁️ Word Cloud")
                wc = WordCloud(width=500, height=300, background_color="black").generate(" ".join(df["Item"].repeat(df["Count"])))
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
                st.pyplot(fig)

            with col2:
                st.subheader("📊 Sentiment")
                st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                st.metric("Negative 😞", f"{sentiment['neg']*100:.1f}%")

                st.subheader("🏆 Bakery Health Score")
                st.progress(health); st.success(f"{health}/100")

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- CSV Analysis ---------------- #
else:
    file = st.file_uploader("📂 Upload CSV (with 'review' or 'product' column)", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        st.write("Preview of Data:", df.head())

        text = " ".join(df.astype(str).sum(axis=1)).lower()
        sentiment = sia.polarity_scores(text)
        health = int(sentiment["pos"]*100)

        st.subheader("📊 Sentiment from CSV")
        st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
        st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
        st.metric("Negative 😞", f"{sentiment['neg']*100:.1f}%")

        st.subheader("🏆 Bakery Health Score")
        st.progress(health); st.success(f"{health}/100")

        st.subheader("☁️ Word Cloud from Data")
        wc = WordCloud(width=600, height=300, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
        st.pyplot(fig)
