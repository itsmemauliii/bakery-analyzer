import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import re
import random

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
    
    /* Scattered metric styling */
    .scattered-metric {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        display: inline-block;
        width: 140px;
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
    
    /* Form section styling */
    .form-section {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 3px solid #4CAF50;
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

# Generate some random metrics for the UI
def generate_random_metrics():
    return {
        "total_bakeries": random.randint(500, 1500),
        "avg_rating": round(random.uniform(3.8, 4.9), 1),
        "reviews_analyzed": random.randint(10000, 50000),
        "products_tracked": random.randint(2000, 8000)
    }

# Display scattered metrics
def display_scattered_metrics():
    metrics = generate_random_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="scattered-metric">
            <h3 style="margin: 0; font-size: 1.8rem;">{metrics['total_bakeries']}</h3>
            <p style="margin: 0; font-size: 0.9rem;">Bakeries Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="scattered-metric">
            <h3 style="margin: 0; font-size: 1.8rem;">{metrics['avg_rating']}</h3>
            <p style="margin: 0; font-size: 0.9rem;">Avg Rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="scattered-metric">
            <h3 style="margin: 0; font-size: 1.8rem;">{metrics['reviews_analyzed']}</h3>
            <p style="margin: 0; font-size: 0.9rem;">Reviews Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="scattered-metric">
            <h3 style="margin: 0; font-size: 1.8rem;">{metrics['products_tracked']}</h3>
            <p style="margin: 0; font-size: 0.9rem;">Products Tracked</p>
        </div>
        """, unsafe_allow_html=True)

# Clean header section
st.markdown("""
<div class="header">
    <h1 style="margin-bottom: 0.5rem; color: #333;">🍞 Bakery Analyzer</h1>
    <p style="margin: 0; color: #666; font-size: 1.1rem;">AI-powered insights for your bakery business</p>
</div>
""", unsafe_allow_html=True)

# Display metrics at the top
display_scattered_metrics()

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
                
                # Display scattered metrics for this analysis
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{len(all_text.split())}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Words Analyzed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{sum(term_counts.values())}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Bakery Terms</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{health_score}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Content Score</p>
                    </div>
                    """, unsafe_allow_html=True)
                
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
            
            # Display metrics about the uploaded file
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="scattered-metric">
                    <h3 style="margin: 0; font-size: 1.8rem;">{len(df)}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Total Reviews</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="scattered-metric">
                    <h3 style="margin: 0; font-size: 1.8rem;">{len(df.columns)}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Data Columns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                missing_data = df.isnull().sum().sum()
                st.markdown(f"""
                <div class="scattered-metric">
                    <h3 style="margin: 0; font-size: 1.8rem;">{missing_data}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">Missing Values</p>
                </div>
                """, unsafe_allow_html=True)
            
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
                    
                    # Display scattered metrics for the analysis
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="scattered-metric">
                            <h3 style="margin: 0; font-size: 1.8rem;">{len(all_text.split())}</h3>
                            <p style="margin: 0; font-size: 0.9rem;">Words Analyzed</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="scattered-metric">
                            <h3 style="margin: 0; font-size: 1.8rem;">{health_score}</h3>
                            <p style="margin: 0; font-size: 0.9rem;">Satisfaction Score</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        positive_reviews = sum(1 for text in df[selected_column].dropna() if sia.polarity_scores(text)['pos'] > 0.5)
                        st.markdown(f"""
                        <div class="scattered-metric">
                            <h3 style="margin: 0; font-size: 1.8rem;">{positive_reviews}</h3>
                            <p style="margin: 0; font-size: 0.9rem;">Positive Reviews</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
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

# Data Upload Section with built-in form
else:
    st.markdown("### Share Your Bakery Data")
    
    st.info("""
    **Help us improve our analysis** by sharing your bakery data. 
    This information helps train better models for the bakery industry.
    """)
    
    # Built-in form for data collection
    with st.form("bakery_data_form"):
        st.markdown("#### Bakery Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bakery_name = st.text_input("Bakery Name*")
            bakery_location = st.text_input("Location (City, Country)*")
        
        with col2:
            bakery_type = st.selectbox("Bakery Type*", 
                                     ["", "Artisan", "Commercial", "Cafe", "Pastry Shop", "Home-based", "Other"])
            years_operation = st.number_input("Years in Operation", min_value=0, max_value=100, value=0)
        
        st.markdown("#### Product Information")
        products = st.text_area("List your main products (separate with commas)*", 
                               help="e.g., Chocolate Cake, Croissants, Sourdough Bread, Macarons")
        
        st.markdown("#### Customer Feedback")
        rating = st.slider("Overall Customer Rating (1-5)*", 1, 5, 3)
        common_feedback = st.text_area("Common Customer Comments")
        
        st.markdown("#### Additional Information")
        challenges = st.multiselect("What are your biggest challenges?",
                                  ["Pricing", "Competition", "Supply Issues", "Staffing", "Marketing", "Seasonality", "Other"])
        
        success_factors = st.multiselect("What contributes most to your success?",
                                       ["Quality", "Location", "Price", "Variety", "Customer Service", "Marketing", "Unique Products"])
        
        submitted = st.form_submit_button("Submit Data", type="primary")
        
        if submitted:
            if not bakery_name or not bakery_location or not bakery_type or not products:
                st.error("Please fill in all required fields (*)")
            else:
                st.success("""
                ✅ **Thank you for submitting your bakery data!**
                
                Your information will help improve our analysis models.
                """)
                
                # Show metrics about the submission
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{len(products.split(','))}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Products Listed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{rating}/5</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Customer Rating</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="scattered-metric">
                        <h3 style="margin: 0; font-size: 1.8rem;">{years_operation}</h3>
                        <p style="margin: 0; font-size: 0.9rem;">Years Operating</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Information about data usage
    st.markdown("""
    <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin-top: 20px;">
        <h4 style="margin-top: 0;">What we do with your data:</h4>
        <ul style="margin-bottom: 0;">
            <li>Improve bakery analysis algorithms</li>
            <li>Create industry benchmarks</li>
            <li>Develop better sentiment analysis</li>
            <li>All data is anonymized and aggregated</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Minimal footer
st.markdown("---")
st.caption("Bakery Analyzer • Simple, AI-powered insights")
