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
st.set_page_config(page_title="🍰 Precise Bakery Product Extractor", layout="wide", page_icon="🍞")
st.title("🍞 Precise Bakery Product Extractor")
st.markdown("### Extract only genuine bakery products from websites")

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
    st.header("🌐 Precise Product Extraction")
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.bakerywebsite.com")
    
    if st.button("🔍 Extract Products", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch the website
            status_text.text("Step 1/4: Fetching website content...")
            progress_bar.progress(25)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Extract structured product information
            status_text.text("Step 2/4: Extracting product information...")
            progress_bar.progress(50)
            
            # Comprehensive list of actual bakery products (not just keywords)
            bakery_products = set()
            
            # Look for product listings in common e-commerce patterns
            product_selectors = [
                '.product', '.item', '.menu-item', '.product-name', '.item-name',
                '.product-title', '.food-item', '.bakery-item', '.cake-item',
                '.pastry-item', '.bread-item', '.cookie-item'
            ]
            
            for selector in product_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if 3 <= len(text) <= 80:  # Reasonable product name length
                        bakery_products.add(text)
            
            # Look for headings that might contain product categories
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                text = heading.get_text(strip=True)
                # Only add if it looks like a product category
                if (5 <= len(text) <= 50 and 
                    any(keyword in text.lower() for keyword in ['cake', 'pastry', 'bread', 'cookie', 'pie', 'tart', 'muffin'])):
                    bakery_products.add(text)
            
            # Look for list items that might be products
            list_items = soup.find_all('li')
            for item in list_items:
                text = item.get_text(strip=True)
                # Only add if it looks like a product
                if (5 <= len(text) <= 60 and 
                    any(keyword in text.lower() for keyword in ['cake', 'pastry', 'bread', 'cookie', 'pie', 'tart', 'muffin', 'donut', 'brownie'])):
                    bakery_products.add(text)
            
            # Step 3: Filter and categorize only genuine bakery products
            status_text.text("Step 3/4: Filtering genuine bakery products...")
            progress_bar.progress(75)
            
            # Define categories with specific product types
            categories = {
                'Cakes': ['cake', 'cupcake', 'cheesecake', 'birthday cake', 'wedding cake'],
                'Pastries': ['pastry', 'croissant', 'danish', 'éclair', 'puff', 'palmier'],
                'Breads': ['bread', 'baguette', 'loaf', 'bun', 'roll', 'bagel', 'ciabatta'],
                'Cookies & Biscuits': ['cookie', 'biscuit', 'macaron', 'biscotti', 'shortbread'],
                'Desserts': ['pie', 'tart', 'muffin', 'donut', 'brownie', 'scone', 'éclair'],
                'Specialty Items': ['vegan', 'gluten-free', 'sugar-free', 'custom', 'artisan']
            }
            
            # Filter out non-product items
            genuine_products = set()
            for product in bakery_products:
                product_lower = product.lower()
                # Check if it contains bakery-related terms
                is_bakery_product = any(
                    bakery_term in product_lower for bakery_term in [
                        'cake', 'pastry', 'bread', 'cookie', 'biscuit', 'pie', 'tart',
                        'muffin', 'donut', 'brownie', 'croissant', 'baguette', 'bagel',
                        'cupcake', 'cheesecake', 'danish', 'éclair', 'scone', 'macaron'
                    ]
                )
                
                # Check if it's not a navigation or common website term
                is_not_website_term = not any(
                    term in product_lower for term in [
                        'home', 'about', 'contact', 'menu', 'shop', 'cart', 'account',
                        'login', 'sign', 'search', 'filter', 'sort', 'price', 'quantity',
                        'checkout', 'payment', 'shipping', 'policy', 'terms', 'privacy'
                    ]
                )
                
                if is_bakery_product and is_not_website_term:
                    genuine_products.add(product)
            
            # Categorize the genuine products
            categorized_products = {category: [] for category in categories.keys()}
            
            for product in sorted(genuine_products):
                product_lower = product.lower()
                categorized = False
                
                for category, keywords in categories.items():
                    for keyword in keywords:
                        if keyword in product_lower:
                            categorized_products[category].append(product)
                            categorized = True
                            break
                    if categorized:
                        break
            
            # Step 4: Analyze sentiment
            status_text.text("Step 4/4: Analyzing sentiment...")
            progress_bar.progress(100)
            
            # Get sentiment from the main content
            main_content = soup.find_all(['p', 'div'])[:5]
            content_text = " ".join([elem.get_text() for elem in main_content]) if main_content else ""
            sentiment = sia.polarity_scores(content_text)
            health = min(100, max(0, int((sentiment["pos"] * 100) + 30)))
            
            status_text.text("Analysis complete!")
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            
            # Display results
            st.subheader("🎯 Genuine Bakery Products Found")
            
            if any(categorized_products.values()):
                total_count = sum(len(products) for products in categorized_products.values())
                st.success(f"✅ Found {total_count} genuine bakery products")
                
                for category, products in categorized_products.items():
                    if products:
                        with st.expander(f"🍞 {category} ({len(products)} products)"):
                            for i, product in enumerate(sorted(products), 1):
                                st.write(f"{i}. {product}")
            else:
                st.warning("No genuine bakery products found. This could be because:")
                st.info("""
                - The website doesn't have a standard product listing
                - The website uses JavaScript to load products
                - The bakery specializes in custom orders not listed on the website
                - The website structure is non-standard
                """)
            
            # Sentiment analysis
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
        
        except Exception as e:
            st.error(f"Error analyzing website: {str(e)}")

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
