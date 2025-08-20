import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

# Improved UI configuration
st.set_page_config(page_title="🍰 Complete Bakery Analyzer", layout="wide", page_icon="🍞")
st.title("🍞 Complete Bakery Analyzer")
st.markdown("### Extract EVERY product from bakery websites with detailed analysis")

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
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.examplebakery.com")
    
    if st.button("🔍 Extract All Products", type="primary"):
        with st.spinner("Completely scanning website for all products..."):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(url, timeout=15, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(["script", "style", "meta", "link", "nav", "footer", "header"]):
                    element.decompose()
                
                # COMPREHENSIVE PRODUCT EXTRACTION STRATEGY
                all_products = set()
                
                # Strategy 1: Look for common e-commerce patterns
                product_selectors = [
                    # Common e-commerce classes
                    '[class*="product"]', '[class*="item"]', '[class*="card"]', '[class*="menu"]',
                    '[class*="shop"]', '[class*="store"]', '[class*="catalog"]', '[class*="grid"]',
                    '[class*="list"]', '[class*="collection"]', 
                    # Common IDs
                    '[id*="product"]', '[id*="item"]', '[id*="menu"]',
                    # Common HTML structures
                    '.product', '.item', '.card', '.menu-item', '.shop-item', '.store-item',
                    '.product-name', '.item-name', '.product-title', '.item-title',
                    '.product-list', '.item-list', '.product-grid', '.item-grid',
                    # List items that might contain products
                    'li', 'dt', 'dd'
                ]
                
                # Try each selector to find products
                for selector in product_selectors:
                    try:
                        elements = soup.select(selector)
                        for element in elements:
                            text = element.get_text(strip=True)
                            if 5 <= len(text) <= 100:  # Reasonable product name length
                                all_products.add(text)
                    except:
                        continue
                
                # Strategy 2: Look for headings that might be product categories
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                for heading in headings:
                    text = heading.get_text(strip=True)
                    if 3 <= len(text) <= 80:
                        all_products.add(text)
                
                # Strategy 3: Look for links that might point to products
                links = soup.find_all('a', href=True)
                for link in links:
                    text = link.get_text(strip=True)
                    href = link['href']
                    # If link text looks like a product and href suggests product page
                    if (3 <= len(text) <= 100 and 
                        any(keyword in href.lower() for keyword in ['product', 'item', 'shop', 'buy', 'order', 'menu'])):
                        all_products.add(text)
                
                # Strategy 4: Look for images with alt text that might be products
                images = soup.find_all('img', alt=True)
                for img in images:
                    alt_text = img['alt'].strip()
                    if 3 <= len(alt_text) <= 100 and alt_text not in ['', ' ']:
                        all_products.add(alt_text)
                
                # Strategy 5: Extract text content and look for product-like patterns
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if 5 <= len(clean_line) <= 150:  # Product description length
                        all_products.add(clean_line)
                
                # Filter and categorize products
                bakery_keywords = [
                    'cake', 'pastry', 'cookie', 'bread', 'bun', 'muffin', 'donut', 
                    'croissant', 'bagel', 'tart', 'pie', 'brownie', 'cupcake', 
                    'cheesecake', 'éclair', 'danish', 'scone', 'biscuit', 'loaf',
                    'roll', 'baguette', 'ciabatta', 'pretzel', 'strudel', 'puff'
                ]
                
                categorized_products = {}
                uncategorized_products = []
                
                for product in sorted(all_products):
                    product_lower = product.lower()
                    categorized = False
                    
                    for keyword in bakery_keywords:
                        if keyword in product_lower:
                            if keyword not in categorized_products:
                                categorized_products[keyword] = []
                            categorized_products[keyword].append(product)
                            categorized = True
                            break
                    
                    if not categorized:
                        uncategorized_products.append(product)
                
                # Get sentiment from the main content
                main_content = soup.find_all(['p', 'div', 'section'])
                content_text = " ".join([elem.get_text() for elem in main_content[:10]]) if main_content else all_text
                sentiment = sia.polarity_scores(content_text)
                health = min(100, max(0, int((sentiment["pos"] * 100) + 30)))
                
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["📋 All Products", "📊 Analysis", "🔍 Raw Data"])
                
                with tab1:
                    st.subheader("🎯 All Extracted Products")
                    
                    if categorized_products:
                        for category, products in categorized_products.items():
                            with st.expander(f"🍞 {category.capitalize()} ({len(products)} products)"):
                                for i, product in enumerate(products, 1):
                                    st.write(f"{i}. {product}")
                    
                    if uncategorized_products:
                        with st.expander(f"❓ Unclassified Items ({len(uncategorized_products)} items)"):
                            for i, product in enumerate(uncategorized_products, 1):
                                st.write(f"{i}. {product}")
                    
                    st.success(f"✅ Total products extracted: {len(all_products)}")
                
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
                            category_counts = {cat: len(prods) for cat, prods in categorized_products.items()}
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
