import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import time
import re

nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

# Improved UI configuration
st.set_page_config(page_title="🍰 Complete Bakery Product Extractor", layout="wide", page_icon="🍞")
st.title("🍞 Complete Bakery Product Extractor")
st.markdown("### Extract EVERY product from bakery websites with advanced analysis")

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
    st.header("🌐 Complete Website Product Extraction")
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.bakerywebsite.com")
    
    if st.button("🔍 Extract All Products", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch the website
            status_text.text("Step 1/5: Fetching website content...")
            progress_bar.progress(20)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Extract all text content
            status_text.text("Step 2/5: Extracting all text content...")
            progress_bar.progress(40)
            
            # Remove unwanted elements but keep structure
            for element in soup(["script", "style", "meta", "link"]):
                element.decompose()
            
            # Get all text with context
            all_text = soup.get_text(separator='\n', strip=True)
            
            # Step 3: Advanced product extraction
            status_text.text("Step 3/5: Advanced product extraction...")
            progress_bar.progress(60)
            
            # Comprehensive bakery product patterns
            bakery_patterns = [
                # Cake patterns
                r'\b([A-Z][a-z]+\s+[Cc]ake|[A-Z][a-z]+\s+[Cc]akes)\b',
                r'\b([A-Z][a-z]+\s+[Cc]upcake|[A-Z][a-z]+\s+[Cc]upcakes)\b',
                r'\b([A-Z][a-z]+\s+[Cc]heesecake|[A-Z][a-z]+\s+[Cc]heesecakes)\b',
                # Pastry patterns
                r'\b([A-Z][a-z]+\s+[Pp]astry|[A-Z][a-z]+\s+[Pp]astries)\b',
                r'\b([A-Z][a-z]+\s+[Cc]roissant|[A-Z][a-z]+\s+[Cc]roissants)\b',
                # Bread patterns
                r'\b([A-Z][a-z]+\s+[Bb]read|[A-Z][a-z]+\s+[Bb]reads)\b',
                r'\b([A-Z][a-z]+\s+[Bb]aguette|[A-Z][a-z]+\s+[Bb]aguettes)\b',
                # Cookie patterns
                r'\b([A-Z][a-z]+\s+[Cc]ookie|[A-Z][a-z]+\s+[Cc]ookies)\b',
                r'\b([A-Z][a-z]+\s+[Bb]iscuit|[A-Z][a-z]+\s+[Bb]iscuits)\b',
                # General patterns
                r'\b([A-Z][a-z]+\s+[Dd]onut|[A-Z][a-z]+\s+[Dd]onuts)\b',
                r'\b([A-Z][a-z]+\s+[Mm]uffin|[A-Z][a-z]+\s+[Mm]uffins)\b',
                r'\b([A-Z][a-z]+\s+[Pp]ie|[A-Z][a-z]+\s+[Pp]ies)\b',
                r'\b([A-Z][a-z]+\s+[Tt]art|[A-Z][a-z]+\s+[Tt]arts)\b',
                # Single word products (capitalized)
                r'\b([A-Z][a-z]{3,20})\b(?=\s*(?:cake|pastry|bread|cookie|pie|tart|muffin|donut)?)'
            ]
            
            # Extract products using patterns
            all_products = set()
            for pattern in bakery_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    if isinstance(match, tuple):
                        match = ' '.join(match)
                    if len(match) > 3 and not any(word in match.lower() for word in ['menu', 'contact', 'about', 'home', 'shop']):
                        all_products.add(match.strip())
            
            # Additional extraction from lists and headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                text = heading.get_text(strip=True)
                if 3 <= len(text) <= 50 and not any(word in text.lower() for word in ['menu', 'contact', 'about', 'home']):
                    all_products.add(text)
            
            # Extract from list items
            list_items = soup.find_all(['li', 'dt', 'dd'])
            for item in list_items:
                text = item.get_text(strip=True)
                if 5 <= len(text) <= 60 and not any(word in text.lower() for word in ['menu', 'contact', 'about', 'home']):
                    all_products.add(text)
            
            # Step 4: Categorize products
            status_text.text("Step 4/5: Categorizing products...")
            progress_bar.progress(80)
            
            # Define categories
            categories = {
                'Cakes': ['cake', 'cupcake', 'cheesecake'],
                'Pastries': ['pastry', 'croissant', 'danish', 'éclair'],
                'Breads': ['bread', 'baguette', 'loaf', 'bun', 'roll'],
                'Cookies': ['cookie', 'biscuit', 'macaron'],
                'Desserts': ['pie', 'tart', 'muffin', 'donut', 'brownie'],
                'Other': []  # For uncategorized items
            }
            
            categorized_products = {category: [] for category in categories.keys()}
            uncategorized_products = []
            
            for product in sorted(all_products):
                product_lower = product.lower()
                categorized = False
                
                for category, keywords in categories.items():
                    if category == 'Other':
                        continue
                    for keyword in keywords:
                        if keyword in product_lower:
                            categorized_products[category].append(product)
                            categorized = True
                            break
                    if categorized:
                        break
                
                if not categorized:
                    uncategorized_products.append(product)
            
            # Step 5: Analyze sentiment
            status_text.text("Step 5/5: Analyzing sentiment...")
            progress_bar.progress(100)
            
            # Get sentiment from the main content
            main_content = soup.find_all(['p', 'div'])
            content_text = " ".join([elem.get_text() for elem in main_content[:5]]) if main_content else all_text[:1000]
            sentiment = sia.polarity_scores(content_text)
            health = min(100, max(0, int((sentiment["pos"] * 100) + 30)))
            
            status_text.text("Analysis complete!")
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["📋 All Products", "📊 Analysis", "🔍 Raw Data"])
            
            with tab1:
                st.subheader("🎯 All Extracted Products")
                
                total_count = sum(len(products) for products in categorized_products.values()) + len(uncategorized_products)
                st.success(f"✅ Total products extracted: {total_count}")
                
                if categorized_products:
                    for category, products in categorized_products.items():
                        if products:
                            with st.expander(f"🍞 {category} ({len(products)} products)"):
                                for i, product in enumerate(sorted(products), 1):
                                    st.write(f"{i}. {product}")
                
                if uncategorized_products:
                    with st.expander(f"❓ Other Items ({len(uncategorized_products)} items)"):
                        for i, product in enumerate(sorted(uncategorized_products), 1):
                            st.write(f"{i}. {product}")
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Sentiment Analysis")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                    with col2:
                        st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                    with col3:
                        st.metric("Negative 😞", f"{sentiment['neg']*100:.1f}%")
                    
                    st.subheader("🏆 Website Health Score")
                    if health >= 70:
                        st.success(f"{health}/100")
                    elif health >= 40:
                        st.warning(f"{health}/100")
                    else:
                        st.error(f"{health}/100")
                    st.progress(health/100)
                
                with col2:
                    st.subheader("📈 Product Categories Distribution")
                    if categorized_products:
                        category_counts = {cat: len(prods) for cat, prods in categorized_products.items() if prods}
                        if category_counts:
                            fig, ax = plt.subplots()
                            ax.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%')
                            ax.axis('equal')
                            st.pyplot(fig)
            
            with tab3:
                st.subheader("🔍 Raw Extraction Data")
                st.text_area("All extracted text content (first 2000 chars):", 
                            all_text[:2000] + "..." if len(all_text) > 2000 else all_text, 
                            height=300)
        
        except Exception as e:
            st.error(f"Error analyzing website: {str(e)}")
            st.info("""
            **If extraction failed, try:**
            - A different bakery website
            - Checking if the website is accessible
            - The website might have anti-scraping protection
            """)

# CSV Analysis Section
else:
    st.header("📊 CSV Analysis")
    file = st.file_uploader("Upload your bakery data (CSV with 'review' or 'product' column)", type=["csv"])
    
    if file is not None:
        with st.spinner("Analyzing your data..."):
            df = pd.read_csv(file)
            st.write("Preview of Data:", df.head())
            
            # Find text columns for analysis
            text_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in 
                          ['review', 'text', 'comment', 'feedback', 'product', 'description', 'name'])]
            
            if text_columns:
                text = " ".join(df[text_columns[0]].astype(str)).lower()
            else:
                text = " ".join(df.astype(str).sum(axis=1)).lower()
                
            sentiment = sia.polarity_scores(text)
            health = min(100, max(0, int(sentiment["pos"]*100 + 30)))
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Sentiment Analysis")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                with col2:
                    st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                with col3:
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
