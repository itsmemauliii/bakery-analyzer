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

# Apply the Figma design with custom CSS
def apply_figma_design():
    st.markdown("""
    <style>
    /* Main styling to match Figma design */
    .main {
        background-color: #F8F5F0;
    }
    
    /* Header styling */
    .header {
        background-color: #FF9E6D;
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #A67C52;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stButton button:hover {
        background-color: #8B613C;
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8E0D2;
    }
    
    /* Metric styling */
    .metric {
        background-color: #F8E0D2;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #FF9E6D;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F8E0D2;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #A67C52;
        color: white;
    }
    
    /* Custom classes for specific elements */
    .bakery-title {
        font-size: 2.5rem;
        color: #A67C52;
        font-weight: 700;
        margin-bottom: 0;
    }
    
    .bakery-subtitle {
        font-size: 1.2rem;
        color: #7A7A7A;
        margin-top: 0;
        margin-bottom: 30px;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
apply_figma_design()

# Page configuration
st.set_page_config(page_title="🍰 Bakery Analyzer", layout="wide", page_icon="🍞")

# Header section matching Figma design
st.markdown('<h1 class="bakery-title">🍞 Bakery Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="bakery-subtitle">AI-powered insights for your bakery business</p>', unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px; background-color: #A67C52; border-radius: 10px; color: white; margin-bottom: 20px;">
        <h2>Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    option = st.radio("Choose Analysis Type:", 
                     ["🌐 Website Analysis", "📊 CSV Analysis", "📝 Submit Bakery Data"],
                     label_visibility="collapsed")

# Google Forms integration
if option == "📝 Submit Bakery Data":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📝 Share Your Bakery Data")
    st.markdown("""
    Help us improve our bakery analysis tools by sharing your data. 
    This information will help train better models for bakery industry analysis.
    """)
    
    # Create a custom form
    with st.form("bakery_data_form"):
        st.subheader("Bakery Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bakery_name = st.text_input("Bakery Name*")
            bakery_location = st.text_input("Location (City, Country)*")
            bakery_website = st.text_input("Website URL")
        
        with col2:
            bakery_type = st.selectbox("Bakery Type*", 
                                     ["", "Artisan", "Commercial", "Cafe", "Pastry Shop", "Home-based", "Other"])
            years_operation = st.number_input("Years in Operation", min_value=0, max_value=100, value=0)
        
        st.subheader("Product Information")
        products = st.text_area("List your main products (separate with commas)*", 
                               help="e.g., Chocolate Cake, Croissants, Sourdough Bread, Macarons")
        
        st.subheader("Customer Feedback")
        rating = st.slider("Overall Customer Rating (1-5)*", 1, 5, 3)
        common_feedback = st.text_area("Common Customer Comments")
        
        st.subheader("Additional Information")
        challenges = st.multiselect("What are your biggest challenges?",
                                  ["Pricing", "Competition", "Supply Issues", "Staffing", "Marketing", "Seasonality", "Other"])
        
        success_factors = st.multiselect("What contributes most to your success?",
                                       ["Quality", "Location", "Price", "Variety", "Customer Service", "Marketing", "Unique Products"])
        
        # Form submission
        submitted = st.form_submit_button("Submit Data", type="primary")
        
        if submitted:
            if not bakery_name or not bakery_location or not bakery_type or not products:
                st.error("Please fill in all required fields (*)")
            else:
                st.success("""
                ✅ Thank you for submitting your bakery data!
                
                Your information will help improve our analysis models. 
                """)
    st.markdown('</div>', unsafe_allow_html=True)

# Website Analysis Section
elif option == "🌐 Website Analysis":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🌐 Bakery Website Analysis")
    
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.examplebakery.com")
    
    if st.button("🔍 Analyze Website", type="primary", use_container_width=True):
        with st.spinner("Analyzing website content..."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for element in soup(["script", "style", "meta", "link"]):
                    element.decompose()
                
                all_text = soup.get_text(separator=' ', strip=True)
                
                bakery_keywords = {
                    'Cakes': ['cake', 'cupcake', 'cheesecake', 'birthday cake', 'wedding cake'],
                    'Pastries': ['pastry', 'croissant', 'danish', 'éclair', 'puff pastry'],
                    'Breads': ['bread', 'baguette', 'sourdough', 'ciabatta', 'whole wheat'],
                    'Cookies': ['cookie', 'biscuit', 'macaron', 'shortbread', 'biscotti'],
                    'Desserts': ['pie', 'tart', 'muffin', 'brownie', 'donut', 'scone']
                }
                
                keyword_counts = {category: 0 for category in bakery_keywords}
                text_lower = all_text.lower()
                
                for category, keywords in bakery_keywords.items():
                    for keyword in keywords:
                        keyword_counts[category] += text_lower.count(keyword)
                
                keyword_counts = {k: v for k, v in keyword_counts.items() if v > 0}
                
                sentiment = sia.polarity_scores(all_text)
                health_score = int(sentiment["pos"] * 100)
                
                tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📋 Content", "💡 Insights"])
                
                with tab1:
                    st.subheader("Bakery Content Analysis")
                    
                    if keyword_counts:
                        df = pd.DataFrame({
                            'Category': list(keyword_counts.keys()),
                            'Count': list(keyword_counts.values())
                        })
                        
                        fig, ax = plt.subplots()
                        colors = ['#FF9E6D', '#A67C52', '#F8E0D2', '#FFD8C9', '#D4B896']
                        ax.bar(df['Category'], df['Count'], color=colors)
                        plt.xticks(rotation=45, ha='right')
                        plt.title('Bakery Content Distribution')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("No specific bakery content detected.")
                
                with tab2:
                    st.subheader("Content Details")
                    
                    if keyword_counts:
                        cols = st.columns(3)
                        for i, (category, count) in enumerate(keyword_counts.items()):
                            with cols[i % 3]:
                                st.markdown(f'<div class="metric"><h3>{count}</h3><p>{category} Mentions</p></div>', unsafe_allow_html=True)
                    else:
                        st.warning("Could not identify specific bakery content.")
                        
                    st.subheader("Text Sample")
                    sample_text = all_text[:500] + "..." if len(all_text) > 500 else all_text
                    st.text(sample_text)
                
                with tab3:
                    st.subheader("Website Insights")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive", f"{sentiment['pos']*100:.1f}%")
                    with col2:
                        st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                    with col3:
                        st.metric("Negative", f"{sentiment['neg']*100:.1f}%")
                    
                    st.subheader("Website Health Score")
                    if health_score >= 70:
                        st.success(f"{health_score}/100")
                    elif health_score >= 40:
                        st.warning(f"{health_score}/100")
                    else:
                        st.error(f"{health_score}/100")
                    st.progress(health_score/100)
                    
                    st.subheader("Recommendations")
                    if health_score >= 70:
                        st.success("Great website content! Keep up the good work.")
                    elif health_score >= 40:
                        st.info("Good content. Consider adding more product details and descriptions.")
                    else:
                        st.warning("Consider improving website content with more product information.")
            
            except Exception as e:
                st.error(f"Error analyzing website: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# CSV Analysis Section
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Customer Feedback Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV file with customer feedback", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            text_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['review', 'feedback', 'comment', 'text']):
                    text_columns.append(col)
            
            if text_columns:
                selected_column = st.selectbox("Select text column for analysis:", text_columns)
                
                if st.button("Analyze Feedback", type="primary"):
                    all_text = " ".join(df[selected_column].dropna().astype(str))
                    
                    sentiment = sia.polarity_scores(all_text)
                    health_score = int(sentiment["pos"] * 100)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Sentiment Analysis")
                        
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Positive", f"{sentiment['pos']*100:.1f}%")
                        with metrics_col2:
                            st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                        with metrics_col3:
                            st.metric("Negative", f"{sentiment['neg']*100:.1f}%")
                        
                        st.subheader("Customer Satisfaction Score")
                        if health_score >= 70:
                            st.success(f"{health_score}/100")
                        elif health_score >= 40:
                            st.warning(f"{health_score}/100")
                        else:
                            st.error(f"{health_score}/100")
                        st.progress(health_score/100)
                    
                    with col2:
                        st.subheader("Word Cloud")
                        
                        wordcloud = WordCloud(
                            width=600, 
                            height=400, 
                            background_color='white',
                            colormap='autumn'
                        ).generate(all_text)
                        
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    
                    st.subheader("Feedback Insights")
                    
                    if health_score >= 70:
                        st.success("""
                        **Excellent customer satisfaction!**
                        - Customers are highly satisfied with your products
                        - Keep maintaining your quality standards
                        - Consider asking for testimonials
                        """)
                    elif health_score >= 40:
                        st.info("""
                        **Moderate customer satisfaction.**
                        - Some areas need improvement
                        - Consider gathering more specific feedback
                        - Look for common themes in negative reviews
                        """)
                    else:
                        st.warning("""
                        **Low customer satisfaction detected.**
                        - Immediate attention needed
                        - Analyze negative feedback for common issues
                        - Consider customer outreach program
                        """)
            
            else:
                st.warning("No suitable text columns found for analysis.")
                
        except Exception as e:
            st.error(f"Error analyzing CSV file: {str(e)}")
    
    else:
        st.info("Please upload a CSV file to analyze customer feedback.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #A67C52;"><p>Bakery Analyzer Tool • Powered by NLP and Sentiment Analysis</p></div>', unsafe_allow_html=True)
