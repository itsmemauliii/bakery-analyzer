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

# Apply custom CSS for beautiful UI
def apply_custom_design():
    st.markdown("""
    <style>
    /* Main styling */
    .main {
        background-color: #F8F5F0;
        color: #333333;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #FF9E6D 0%, #A67C52 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(166, 124, 82, 0.2);
    }
    
    /* Card styling */
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        border-left: 5px solid #FF9E6D;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #A67C52 0%, #8B613C 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(166, 124, 82, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8E0D2;
    }
    
    .sidebar .sidebar-content {
        background-color: #F8E0D2;
    }
    
    /* Metric styling */
    .metric-card {
        background-color: #F8E0D2;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FF9E6D 0%, #A67C52 100%);
        border-radius: 10px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F8E0D2;
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #A67C52;
        color: white;
    }
    
    /* Custom classes for specific elements */
    .bakery-title {
        font-size: 2.8rem;
        color: white;
        font-weight: 800;
        margin-bottom: 5px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    
    .bakery-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0;
        margin-bottom: 15px;
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #F8E0D2;
        padding: 12px;
    }
    
    .stTextInput input:focus {
        border-color: #A67C52;
        box-shadow: 0 0 0 2px rgba(166, 124, 82, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #A67C52;
        border-radius: 12px;
        padding: 20px;
        background-color: rgba(248, 224, 210, 0.3);
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #E8F5E9;
        color: #2E7D32;
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #4CAF50;
    }
    
    /* Warning message styling */
    .stWarning {
        background-color: #FFF8E1;
        color: #F57C00;
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #FFC107;
    }
    
    /* Error message styling */
    .stError {
        background-color: #FFEBEE;
        color: #D32F2F;
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #F44336;
    }
    
    /* Info message styling */
    .stInfo {
        background-color: #E3F2FD;
        color: #1976D2;
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #2196F3;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
apply_custom_design()

# Page configuration
st.set_page_config(page_title="🍰 Bakery Analyzer", layout="wide", page_icon="🍞")

# Header section with beautiful design
st.markdown("""
<div class="header">
    <h1 class="bakery-title">🍞 Bakery Analyzer</h1>
    <p class="bakery-subtitle">AI-powered insights for your bakery business</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, #A67C52 0%, #8B613C 100%); 
                border-radius: 12px; color: white; margin-bottom: 25px; text-align: center;">
        <h2 style="margin: 0;">Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    option = st.radio("Choose Analysis Type:", 
                     ["🌐 Website Analysis", "📊 CSV Analysis", "📝 Submit Bakery Data"],
                     label_visibility="collapsed")

# Website Analysis Section
if option == "🌐 Website Analysis":
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
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        colors = ['#FF9E6D', '#A67C52', '#F8E0D2', '#FFD8C9', '#D4B896']
                        bars = ax.bar(df['Category'], df['Count'], color=colors)
                        plt.xticks(rotation=45, ha='right')
                        plt.title('Bakery Content Distribution', fontsize=16, fontweight='bold', pad=20)
                        plt.tight_layout()
                        
                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                        
                        st.pyplot(fig)
                    else:
                        st.info("No specific bakery content detected.")
                
                with tab2:
                    st.subheader("Content Details")
                    
                    if keyword_counts:
                        cols = st.columns(3)
                        for i, (category, count) in enumerate(keyword_counts.items()):
                            with cols[i % 3]:
                                st.markdown(f'''
                                <div class="metric-card">
                                    <h3 style="margin:0; color: #A67C52; font-size: 2rem;">{count}</h3>
                                    <p style="margin:0; font-weight: 600;">{category} Mentions</p>
                                </div>
                                ''', unsafe_allow_html=True)
                    else:
                        st.warning("Could not identify specific bakery content.")
                        
                    st.subheader("Text Sample")
                    sample_text = all_text[:500] + "..." if len(all_text) > 500 else all_text
                    st.text(sample_text)
                
                with tab3:
                    st.subheader("Website Insights")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive", f"{sentiment['pos']*100:.1f}%", delta="Good sentiment", delta_color="normal")
                    with col2:
                        st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                    with col3:
                        st.metric("Negative", f"{sentiment['neg']*100:.1f}%", delta="Improve content", delta_color="inverse")
                    
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
                        st.success("""
                        🎉 **Excellent website content!** 
                        - Your bakery website has strong, positive content
                        - Keep maintaining your quality standards
                        - Consider adding more product images
                        """)
                    elif health_score >= 40:
                        st.info("""
                        👍 **Good website content with room for improvement**
                        - Add more detailed product descriptions
                        - Include customer testimonials
                        - Expand your content with baking tips or recipes
                        """)
                    else:
                        st.warning("""
                        ⚠️ **Website needs content improvements**
                        - Add more bakery-specific content
                        - Include detailed product information
                        - Share your bakery's story and mission
                        - Add customer reviews and testimonials
                        """)
            
            except Exception as e:
                st.error(f"Error analyzing website: {str(e)}")
                st.info("""
                **Tips for successful analysis:**
                - Make sure the website URL is correct and accessible
                - Try a different bakery website
                - Some websites may block automated analysis
                """)
    st.markdown('</div>', unsafe_allow_html=True)

# CSV Analysis Section
elif option == "📊 CSV Analysis":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Customer Feedback Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV file with customer feedback", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.subheader("Data Preview")
            st.dataframe(df.head().style.set_properties(**{
                'background-color': '#F8F5F0',
                'color': '#333333',
                'border': '1px solid #F8E0D2'
            }))
            
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
                            st.metric("Positive", f"{sentiment['pos']*100:.1f}%", delta="Satisfied", delta_color="normal")
                        with metrics_col2:
                            st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                        with metrics_col3:
                            st.metric("Negative", f"{sentiment['neg']*100:.1f}%", delta="Concern", delta_color="inverse")
                        
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
                            colormap='autumn',
                            max_words=100
                        ).generate(all_text)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        ax.set_title('Most Frequent Words in Feedback', fontsize=16, fontweight='bold')
                        st.pyplot(fig)
                    
                    st.subheader("Feedback Insights")
                    
                    if health_score >= 70:
                        st.success("""
                        🎉 **Excellent customer satisfaction!**
                        - Customers are highly satisfied with your products and service
                        - Keep maintaining your quality standards
                        - Consider asking happy customers for testimonials
                        - Share positive reviews on your website and social media
                        """)
                    elif health_score >= 40:
                        st.info("""
                        👍 **Moderate customer satisfaction.**
                        - Some areas need improvement
                        - Consider gathering more specific feedback through surveys
                        - Look for common themes in negative reviews to address
                        - Highlight your strengths while working on weaknesses
                        """)
                    else:
                        st.warning("""
                        ⚠️ **Low customer satisfaction detected.**
                        - Immediate attention needed to address concerns
                        - Analyze negative feedback for common issues
                        - Consider a customer outreach program to understand concerns
                        - Develop an action plan to address the most critical issues
                        """)
            
            else:
                st.warning("No suitable text columns found for analysis. Please ensure your CSV has columns named 'review', 'feedback', 'comment', or 'text'.")
                
        except Exception as e:
            st.error(f"Error analyzing CSV file: {str(e)}")
            st.info("Please make sure you've uploaded a valid CSV file with the correct format.")
    
    else:
        st.info("""
        📤 **Please upload a CSV file to analyze customer feedback.**
        
        Your CSV should include columns with customer reviews, feedback, or comments.
        Supported column names: 'review', 'feedback', 'comment', or 'text'
        """)
    st.markdown('</div>', unsafe_allow_html=True)

# Data Collection Section
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📝 Share Your Bakery Data")
    st.markdown("Help us improve our bakery analysis tools by sharing your data.")
    
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
        
        submitted = st.form_submit_button("Submit Data", type="primary")
        
        if submitted:
            if not bakery_name or not bakery_location or not bakery_type or not products:
                st.error("Please fill in all required fields (*)")
            else:
                st.success("""
                ✅ **Thank you for submitting your bakery data!**
                
                Your information will help improve our analysis models and provide better insights for bakeries worldwide.
                """)
                
                with st.expander("Preview Submitted Data"):
                    st.write(f"**Bakery Name:** {bakery_name}")
                    st.write(f"**Location:** {bakery_location}")
                    st.write(f"**Website:** {bakery_website if bakery_website else 'Not provided'}")
                    st.write(f"**Bakery Type:** {bakery_type}")
                    st.write(f"**Years in Operation:** {years_operation}")
                    st.write(f"**Main Products:** {products}")
                    st.write(f"**Customer Rating:** {rating}/5")
                    st.write(f"**Common Feedback:** {common_feedback if common_feedback else 'Not provided'}")
                    st.write(f"**Challenges:** {', '.join(challenges) if challenges else 'Not specified'}")
                    st.write(f"**Success Factors:** {', '.join(success_factors) if success_factors else 'Not specified'}")
    
    st.info("""
    ℹ️ **What happens with your data?**
    - Your information helps train better bakery analysis models
    - Data is anonymized and aggregated for analysis purposes
    - We never share personally identifiable information
    - You contribute to the bakery industry's growth and knowledge
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #A67C52; padding: 20px;">
    <p style="font-weight: 600;">Bakery Analyzer Tool • Powered by NLP and Sentiment Analysis</p>
    <p style="font-size: 0.9rem; opacity: 0.7;">© 2023 Bakery Insights. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
