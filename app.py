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

# Page configuration
st.set_page_config(page_title="🍰 Complete Bakery Analyzer", layout="wide", page_icon="🍞")
st.title("🍞 Complete Bakery Analyzer")
st.markdown("### Comprehensive analysis for bakery websites and customer feedback")

# Sidebar navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose Analysis Type:", 
                         ["🌐 Website Analysis", "📊 CSV Analysis", "📝 Submit Bakery Data"])

# Google Forms integration
if option == "📝 Submit Bakery Data":
    st.header("📝 Share Your Bakery Data")
    st.markdown("""
    Help us improve our bakery analysis tools by sharing your data. 
    This information will help train better models for bakery industry analysis.
    """)
    
    # Create a custom form since we can't embed an actual Google Form
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
            # Basic validation
            if not bakery_name or not bakery_location or not bakery_type or not products:
                st.error("Please fill in all required fields (*)")
            else:
                # In a real implementation, this would connect to Google Forms
                # For this demo, we'll just show a success message
                st.success("""
                ✅ Thank you for submitting your bakery data!
                
                Your information will help improve our analysis models. 
                In a real implementation, this data would be sent to our Google Form for processing.
                """)
                
                # Show a preview of what would be submitted
                with st.expander("Preview of Submitted Data"):
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
    
    # Information about what happens with the data
    st.info("""
    **What happens with your data?**
    - Your information helps train better bakery analysis models
    - Data is anonymized for analysis purposes
    - We never share personally identifiable information
    - You contribute to the bakery industry's growth
    """)

# Website Analysis Section
elif option == "🌐 Website Analysis":
    st.header("🌐 Bakery Website Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.examplebakery.com")
        
        if st.button("🔍 Analyze Website", type="primary", use_container_width=True):
            with st.spinner("Analyzing website content..."):
                try:
                    # Fetch website content
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(url, timeout=10, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Clean up the HTML
                    for element in soup(["script", "style", "meta", "link"]):
                        element.decompose()
                    
                    # Extract all text
                    all_text = soup.get_text(separator=' ', strip=True)
                    
                    # Analyze bakery-specific content
                    bakery_keywords = {
                        'Cakes': ['cake', 'cupcake', 'cheesecake', 'birthday cake', 'wedding cake'],
                        'Pastries': ['pastry', 'croissant', 'danish', 'éclair', 'puff pastry'],
                        'Breads': ['bread', 'baguette', 'sourdough', 'ciabatta', 'whole wheat'],
                        'Cookies': ['cookie', 'biscuit', 'macaron', 'shortbread', 'biscotti'],
                        'Desserts': ['pie', 'tart', 'muffin', 'brownie', 'donut', 'scone']
                    }
                    
                    # Count keyword occurrences
                    keyword_counts = {category: 0 for category in bakery_keywords}
                    text_lower = all_text.lower()
                    
                    for category, keywords in bakery_keywords.items():
                        for keyword in keywords:
                            keyword_counts[category] += text_lower.count(keyword)
                    
                    # Filter out categories with zero counts
                    keyword_counts = {k: v for k, v in keyword_counts.items() if v > 0}
                    
                    # Sentiment analysis
                    sentiment = sia.polarity_scores(all_text)
                    health_score = int(sentiment["pos"] * 100)
                    
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📋 Content", "💡 Insights"])
                    
                    with tab1:
                        st.subheader("Bakery Content Analysis")
                        
                        if keyword_counts:
                            # Create dataframe for visualization
                            df = pd.DataFrame({
                                'Category': list(keyword_counts.keys()),
                                'Count': list(keyword_counts.values())
                            })
                            
                            # Display bar chart
                            fig, ax = plt.subplots()
                            ax.bar(df['Category'], df['Count'], color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99FF'])
                            plt.xticks(rotation=45, ha='right')
                            plt.title('Bakery Content Distribution')
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            st.info("No specific bakery content detected.")
                    
                    with tab2:
                        st.subheader("Content Details")
                        
                        if keyword_counts:
                            for category, count in keyword_counts.items():
                                st.metric(f"{category} Mentions", count)
                        else:
                            st.warning("Could not identify specific bakery content.")
                            
                        # Show text sample
                        st.subheader("Text Sample")
                        sample_text = all_text[:500] + "..." if len(all_text) > 500 else all_text
                        st.text(sample_text)
                    
                    with tab3:
                        st.subheader("Website Insights")
                        
                        # Sentiment analysis
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Positive", f"{sentiment['pos']*100:.1f}%", help="Percentage of positive content")
                        with col2:
                            st.metric("Neutral", f"{sentiment['neu']*100:.1f}%", help="Percentage of neutral content")
                        with col3:
                            st.metric("Negative", f"{sentiment['neg']*100:.1f}%", help="Percentage of negative content")
                        
                        # Health score
                        st.subheader("Website Health Score")
                        if health_score >= 70:
                            st.success(f"{health_score}/100")
                        elif health_score >= 40:
                            st.warning(f"{health_score}/100")
                        else:
                            st.error(f"{health_score}/100")
                        st.progress(health_score/100)
                        
                        # Recommendations
                        st.subheader("Recommendations")
                        if health_score >= 70:
                            st.success("Great website content! Keep up the good work.")
                        elif health_score >= 40:
                            st.info("Good content. Consider adding more product details and descriptions.")
                        else:
                            st.warning("Consider improving website content with more product information.")
                
                except Exception as e:
                    st.error(f"Error analyzing website: {str(e)}")
    
    with col2:
        st.info("""
        **Website Analysis Features:**
        - Content categorization
        - Sentiment analysis
        - Health scoring
        - Keyword analysis
        - Visual reporting
        """)

# CSV Analysis Section
else:
    st.header("📊 Customer Feedback Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV file with customer feedback", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Find text columns
            text_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['review', 'feedback', 'comment', 'text']):
                    text_columns.append(col)
            
            if text_columns:
                selected_column = st.selectbox("Select text column for analysis:", text_columns)
                
                if st.button("Analyze Feedback", type="primary"):
                    # Combine all text
                    all_text = " ".join(df[selected_column].dropna().astype(str))
                    
                    # Sentiment analysis
                    sentiment = sia.polarity_scores(all_text)
                    health_score = int(sentiment["pos"] * 100)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Sentiment Analysis")
                        
                        # Sentiment metrics
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Positive", f"{sentiment['pos']*100:.1f}%")
                        with metrics_col2:
                            st.metric("Neutral", f"{sentiment['neu']*100:.1f}%")
                        with metrics_col3:
                            st.metric("Negative", f"{sentiment['neg']*100:.1f}%")
                        
                        # Health score
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
                        
                        # Generate word cloud
                        wordcloud = WordCloud(
                            width=600, 
                            height=400, 
                            background_color='white',
                            colormap='viridis'
                        ).generate(all_text)
                        
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    
                    # Insights
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

# Footer
st.markdown("---")
st.caption("Bakery Analyzer Tool • Mauli Patel | Data Analyst")
