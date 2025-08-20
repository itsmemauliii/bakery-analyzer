import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import re

nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

# Simple UI configuration
st.set_page_config(page_title="🍰 Realistic Bakery Analyzer", layout="wide", page_icon="🍞")
st.title("🍞 Realistic Bakery Analyzer")
st.markdown("### Get honest insights about bakery websites")

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
    st.header("🌐 Website Content Analysis")
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.example.com")
    
    if st.button("🔍 Analyze Website", type="primary"):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for element in soup(["script", "style", "meta", "link"]):
                element.decompose()
            
            # Get clean text
            text = soup.get_text(separator=' ', strip=True)
            
            # Look for obvious product listings
            potential_products = []
            
            # Method 1: Look for common product listing patterns
            product_patterns = [
                'product', 'item', 'menu', 'listing', 'card', 'grid'
            ]
            
            for pattern in product_patterns:
                elements = soup.find_all(class_=re.compile(pattern))
                for element in elements:
                    product_text = element.get_text(strip=True)
                    if 10 < len(product_text) < 100:
                        potential_products.append(product_text)
            
            # Method 2: Look for headings that might be product categories
            headings = soup.find_all(['h2', 'h3', 'h4'])
            for heading in headings:
                heading_text = heading.get_text(strip=True)
                if 5 < len(heading_text) < 50:
                    potential_products.append(heading_text)
            
            # Method 3: Simple text analysis for bakery terms
            bakery_terms = [
                'cake', 'pastry', 'bread', 'cookie', 'pie', 'tart', 
                'muffin', 'donut', 'brownie', 'croissant', 'bagel'
            ]
            
            found_terms = {}
            for term in bakery_terms:
                count = text.lower().count(term)
                if count > 0:
                    found_terms[term] = count
            
            # Sentiment analysis
            sentiment = sia.polarity_scores(text)
            health_score = min(100, max(0, int(sentiment["pos"] * 80 + 20)))
            
            # Display results
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Content Analysis")
                
                if potential_products:
                    st.write("**Potential products found:**")
                    for i, product in enumerate(potential_products[:10], 1):
                        st.write(f"{i}. {product}")
                    
                    if len(potential_products) > 10:
                        st.info(f"... and {len(potential_products) - 10} more items")
                else:
                    st.info("No specific product listings detected.")
                
                if found_terms:
                    st.write("**Bakery terms mentioned:**")
                    for term, count in found_terms.items():
                        st.write(f"- {term}: {count} mentions")
            
            with col2:
                st.subheader("📊 Sentiment Analysis")
                
                st.metric("Positive Content", f"{sentiment['pos']*100:.1f}%")
                st.metric("Neutral Content", f"{sentiment['neu']*100:.1f}%")
                st.metric("Negative Content", f"{sentiment['neg']*100:.1f}%")
                
                st.subheader("🏆 Content Quality Score")
                if health_score >= 70:
                    st.success(f"{health_score}/100")
                elif health_score >= 40:
                    st.warning(f"{health_score}/100")
                else:
                    st.error(f"{health_score}/100")
                st.progress(health_score/100)
            
            # Realistic assessment
            st.subheader("💡 Realistic Assessment")
            
            if not potential_products and not found_terms:
                st.warning("Could not extract specific product information.")
                st.info("""
                This is common because:
                - Modern websites often load content dynamically with JavaScript
                - Product information might be in images rather than text
                - The website might use complex structures
                """)
            elif found_terms and not potential_products:
                st.info("Found bakery-related content but no specific product listings.")
            else:
                st.success("Found some product information.")
        
        except Exception as e:
            st.error(f"Could not analyze website: {str(e)}")

# CSV Analysis Section
else:
    st.header("📊 CSV Analysis")
    file = st.file_uploader("Upload your bakery data (CSV with 'review' or 'product' column)", type=["csv"])
    
    if file is not None:
        try:
            df = pd.read_csv(file)
            st.write("Preview of Data:", df.head())
            
            # Find text columns for analysis
            text_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in 
                          ['review', 'text', 'comment', 'feedback', 'product', 'description'])]
            
            if text_columns:
                text = " ".join(df[text_columns[0]].astype(str))
            else:
                text = " ".join(df.astype(str).sum(axis=1))
                
            sentiment = sia.polarity_scores(text)
            health_score = min(100, max(0, int(sentiment["pos"]*100)))
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Sentiment Analysis")
                st.metric("Positive Content", f"{sentiment['pos']*100:.1f}%")
                st.metric("Neutral Content", f"{sentiment['neu']*100:.1f}%")
                st.metric("Negative Content", f"{sentiment['neg']*100:.1f}%")
                
                st.subheader("🏆 Content Quality Score")
                if health_score >= 70:
                    st.success(f"{health_score}/100")
                elif health_score >= 40:
                    st.warning(f"{health_score}/100")
                else:
                    st.error(f"{health_score}/100")
                st.progress(health_score/100)
            
            with col2:
                st.subheader("☁️ Word Cloud")
                wc = WordCloud(width=600, height=300, background_color="white").generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            
            # Additional insights
            st.subheader("💡 Customer Feedback Insights")
            if health_score > 70:
                st.success("Overall positive sentiment in the feedback!")
            elif health_score > 40:
                st.info("Mixed sentiment in the feedback.")
            else:
                st.warning("Generally negative sentiment in the feedback.")
                
        except Exception as e:
            st.error(f"Error analyzing CSV: {str(e)}")
