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

# Improved UI configuration
st.set_page_config(page_title="🍰 Smart Bakery Analyzer", layout="wide", page_icon="🍞")
st.title("🍞 Smart Bakery Analyzer")
st.markdown("### Analyze bakery websites and customer feedback with AI-powered insights")

# Sidebar for navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose Input Method:", ["🌐 Website Analysis", "📊 CSV Analysis", "📝 Data Collection"])

# Google Forms integration for data collection
if option == "📝 Data Collection":
    st.header("📝 Help Us Improve Our Service")
    st.markdown("""
    We're constantly working to improve our bakery analysis tools. 
    Please take a moment to share your bakery data or feedback with us.
    """)
    
    # Google Form embed (replace with your actual form URL)
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe.../viewform?embedded=true"
    st.components.v1.iframe(google_form_url, width=640, height=800, scrolling=True)
    
    st.info("Your responses will help us train better models for bakery analysis!")

# Website Analysis Section
elif option == "🌐 Website Analysis":
    st.header("🌐 Website Analysis")
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.bakingo.com")
    
    if st.button("🔍 Analyze Website", type="primary"):
        with st.spinner("Analyzing website content..."):
            try:
                html = requests.get(url, timeout=8).text
                text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True).lower()
                
                # Enhanced bakery items list
                items = ["cake","cakes","cookie","cookies","pastry","pastries","bread",
                         "cupcake","brownie","pizza","bun","biscuit","biscuits","gift",
                         "muffin","donut","croissant","bagel","tart","pie"]
                
                found = {i: len(re.findall(rf"\b{i}\b", text)) for i in items if re.search(rf"\b{i}\b", text)}
                sentiment = sia.polarity_scores(text)
                health = int((sentiment["pos"] * 100))
                
                # Improved layout
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.subheader("🎂 Bakery Items Found")
                    df = pd.DataFrame(found.items(), columns=["Item", "Count"]).sort_values("Count", ascending=False)
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    # Enhanced word cloud
                    st.subheader("☁️ Product Word Cloud")
                    if len(found) > 0:
                        word_freq = " ".join([item for item, count in found.items() for _ in range(count)])
                        wc = WordCloud(width=600, height=300, background_color="white", 
                                    colormap="autumn", collocations=False).generate(word_freq)
                        fig, ax = plt.subplots()
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        st.pyplot(fig)
                    else:
                        st.info("No bakery items detected on this website")
                
                with col2:
                    st.subheader("📊 Sentiment Analysis")
                    
                    # Sentiment gauges
                    cols_metrics = st.columns(3)
                    with cols_metrics[0]:
                        st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                    with cols_metrics[1]:
                        st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                    with cols_metrics[2]:
                        st.metric("Negative 😞", f"{sentiment['neg']*100:.1f}%")
                    
                    # Health score with color coding
                    st.subheader("🏆 Bakery Health Score")
                    if health >= 70:
                        st.success(f"{health}/100")
                    elif health >= 40:
                        st.warning(f"{health}/100")
                    else:
                        st.error(f"{health}/100")
                    st.progress(health/100)
                    
                    # Additional insights
                    st.subheader("💡 Insights")
                    if health > 70:
                        st.info("This bakery website has very positive content!")
                    elif health > 40:
                        st.info("This bakery website has neutral to moderately positive content.")
                    else:
                        st.warning("This bakery website may need content improvements.")
            
            except Exception as e:
                st.error(f"Error analyzing website: {e}")

# CSV Analysis Section
else:
    st.header("📊 CSV Analysis")
    file = st.file_uploader("Upload your bakery data (CSV with 'review' or 'product' column)", type=["csv"])
    
    if file is not None:
        with st.spinner("Analyzing your data..."):
            df = pd.read_csv(file)
            st.write("Preview of Data:", df.head())
            
            # Find text columns for analysis
            text_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['review', 'text', 'comment', 'feedback'])]
            
            if text_columns:
                text = " ".join(df[text_columns[0]].astype(str)).lower()
            else:
                text = " ".join(df.astype(str).sum(axis=1)).lower()
                
            sentiment = sia.polarity_scores(text)
            health = int(sentiment["pos"]*100)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Sentiment Analysis")
                cols_metrics = st.columns(3)
                with cols_metrics[0]:
                    st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                with cols_metrics[1]:
                    st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                with cols_metrics[2]:
                    st.metric("Negative 😞", f"{sentiment['neg']*100:.1f}%")
                
                st.subheader("🏆 Bakery Health Score")
                if health >= 70:
                    st.success(f"{health}/100")
                elif health >= 40:
                    st.warning(f"{health}/100")
                else:
                    st.error(f"{health}/100")
                st.progress(health/100)
            
            with col2:
                st.subheader("☁️ Word Cloud")
                wc = WordCloud(width=600, height=300, background_color="white", 
                             colormap="viridis").generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            
            # Additional insights
            st.subheader("💡 Customer Feedback Insights")
            if health > 70:
                st.success("Your customers are very satisfied! Keep up the good work.")
            elif health > 40:
                st.info("Your customers are generally satisfied but there's room for improvement.")
            else:
                st.warning("Your customers seem dissatisfied. Consider making improvements.")
                
            st.info("Want to improve your scores? Consider collecting more data through our form in the Data Collection section!")
