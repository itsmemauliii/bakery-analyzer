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

# Apply clean, minimal CSS
def apply_clean_design():
    st.markdown("""
    <style>
    /* Clean, minimal styling */
    .main {
        background-color: #FFFFFF;
        color: #333333;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 10px 0 20px 0;
        margin-bottom: 30px;
        border-bottom: 2px solid #F0F0F0;
    }
    
    /* Card styling */
    .card {
        background-color: #FAFAFA;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #4CAF50;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stButton button:hover {
        background-color: #45a049;
    }
    
    /* Clean metric styling */
    .metric-box {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 8px 0;
        border: 1px solid #E0E0E0;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #4CAF50;
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 6px;
        border: 1px solid #E0E0E0;
        padding: 10px;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the clean CSS
apply_clean_design()

# Page configuration
st.set_page_config(page_title="Bakery Analyzer", layout="centered", page_icon="🍞")

# Clean header section
st.markdown("""
<div class="header">
    <h1 style="margin-bottom: 0.5rem; color: #333;">🍞 Bakery Analyzer</h1>
    <p style="margin: 0; color: #666; font-size: 1.1rem;">AI-powered insights for your bakery business</p>
</div>
""", unsafe_allow_html=True)

# Simple navigation
option = st.radio("Choose analysis type:", 
                 ["Website Analysis", "CSV Analysis", "Upload Data"],
                 horizontal=True,
                 label_visibility="collapsed")

# Website Analysis Section
if option == "Website Analysis":
    st.markdown("### Website Analysis")
    
    url = st.text_input("Enter bakery website URL:", "https://www.example.com")
    
    if st.button("Analyze Website", type="primary"):
        with st.spinner("Analyzing website content..."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unnecessary elements
                for element in soup(["script", "style", "meta", "link"]):
                    element.decompose()
                
                # Extract text
                all_text = soup.get_text(separator=' ', strip=True)
                
                # Simple bakery content analysis
                bakery_terms = {
                    'Bakery Products': ['bread', 'cake', 'pastry', 'cookie', 'pie', 'muffin', 'donut'],
                    'Business Info': ['about', 'contact', 'hours', 'location', 'menu', 'order'],
                    'Quality Terms': ['fresh', 'organic', 'homemade', 'artisan', 'quality', 'delicious']
                }
                
                term_counts = {}
                text_lower = all_text.lower()
                
                for category, terms in bakery_terms.items():
                    count = sum(text_lower.count(term) for term in terms)
                    if count > 0:
                        term_counts[category] = count
                
                # Sentiment analysis
                sentiment = sia.polarity_scores(all_text)
                health_score = int(sentiment["pos"] * 100)
                
                # Display results in a clean layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Content Analysis")
                    
                    if term_counts:
                        for category, count in term_counts.items():
                            st.markdown(f"""
                            <div class="metric-box">
                                <h3 style="margin: 0; color: #4CAF50;">{count}</h3>
                                <p style="margin: 0; font-weight: 500;">{category}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Limited bakery content detected.")
                
                with col2:
                    st.subheader("Sentiment Analysis")
                    
                    # Simple sentiment metrics
                    st.metric("Positive", f"{sentiment['pos']*100:.1f}%")
                    st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                    st.metric("Negative", f"{sentiment['neg']*100:.1f}%")
                    
                    # Health score
                    st.subheader("Content Quality Score")
                    if health_score >= 70:
                        st.success(f"{health_score}/100")
                    elif health_score >= 40:
                        st.warning(f"{health_score}/100")
                    else:
                        st.error(f"{health_score}/100")
                    st.progress(health_score/100)
                
                # Simple recommendations
                st.subheader("Recommendations")
                if health_score >= 70:
                    st.success("Your website has excellent bakery content. Keep up the good work!")
                elif health_score >= 40:
                    st.info("Good content. Consider adding more product details and customer testimonials.")
                else:
                    st.warning("Your website needs more bakery-specific content. Add product descriptions, about section, and customer reviews.")
            
            except Exception as e:
                st.error(f"Could not analyze website: {str(e)}")

# CSV Analysis Section
elif option == "CSV Analysis":
    st.markdown("### Customer Feedback Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV file with customer feedback", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Simple preview
            st.write("Data preview:")
            st.dataframe(df.head(3))
            
            # Find text columns
            text_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['review', 'feedback', 'comment', 'text']):
                    text_columns.append(col)
            
            if text_columns:
                selected_column = st.selectbox("Select column to analyze:", text_columns)
                
                if st.button("Analyze Feedback", type="primary"):
                    all_text = " ".join(df[selected_column].dropna().astype(str))
                    
                    # Sentiment analysis
                    sentiment = sia.polarity_scores(all_text)
                    health_score = int(sentiment["pos"] * 100)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Sentiment Analysis")
                        st.metric("Positive", f"{sentiment['pos']*100:.1f}%")
                        st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                        st.metric("Negative", f"{sentiment['neg']*100:.1f}%")
                        
                        st.subheader("Satisfaction Score")
                        if health_score >= 70:
                            st.success(f"{health_score}/100")
                        elif health_score >= 40:
                            st.warning(f"{health_score}/100")
                        else:
                            st.error(f"{health_score}/100")
                        st.progress(health_score/100)
                    
                    with col2:
                        st.subheader("Word Cloud")
                        wordcloud = WordCloud(width=400, height=300, background_color='white').generate(all_text)
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    
                    # Simple insights
                    st.subheader("Insights")
                    if health_score >= 70:
                        st.success("Customers are very satisfied with your bakery!")
                    elif health_score >= 40:
                        st.info("Moderate customer satisfaction. Some areas need improvement.")
                    else:
                        st.warning("Low customer satisfaction. Immediate attention needed.")
            
            else:
                st.warning("No review columns found. Ensure your CSV has columns like 'review', 'feedback', or 'comments'.")
                
        except Exception as e:
            st.error(f"Error analyzing CSV: {str(e)}")

# Data Upload Section with Google Form
else:
    st.markdown("### Upload Bakery Data")
    
    st.info("""
    **Help us improve our analysis** by sharing your bakery data. 
    This information helps train better models for the bakery industry.
    """)
    
    # Google Form embed code (replace with your actual form URL)
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLScEXAMPLE/viewform?embedded=true"
    
    st.components.v1.iframe(
        src=google_form_url, 
        width=640, 
        height=800, 
        scrolling=True
    )
    
    st.markdown("""
    <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin-top: 20px;">
        <h4 style="margin-top: 0;">What we collect:</h4>
        <ul style="margin-bottom: 0;">
            <li>Bakery product information</li>
            <li>Customer feedback data</li>
            <li>Business performance metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Minimal footer
st.markdown("---")
st.caption("Bakery Analyzer • Mauli Patel")
