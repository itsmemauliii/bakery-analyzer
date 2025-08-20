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
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.examplebakery.com")
    
    if st.button("🔍 Analyze Website", type="primary"):
        with st.spinner("Analyzing website content..."):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                }
                
                response = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove scripts, styles, and other non-content elements
                for element in soup(["script", "style", "meta", "link", "nav", "footer", "header"]):
                    element.decompose()
                
                # Get clean text
                text = soup.get_text(" ", strip=True).lower()
                
                # Enhanced bakery items detection with better patterns
                bakery_keywords = {
                    'cake': r'\b(cakes?|cupcakes?|cheesecakes?|birthday cakes?|wedding cakes?)\b',
                    'cookie': r'\b(cookies?|biscuits?|bakes?)\b',
                    'pastry': r'\b(pastries|pastry|croissants?|éclairs?|danishes?)\b',
                    'bread': r'\b(breads?|loaves|baguettes?|buns?|rolls?|bagels?)\b',
                    'dessert': r'\b(desserts?|sweets?|treats?|puddings?|mousses?)\b',
                    'pie': r'\b(pies?|tarts?|quiches?)\b',
                    'muffin': r'\b(muffins?|scones?)\b',
                    'brownie': r'\b(brownies?|blondies?)\b',
                    'donut': r'\b(donuts?|doughnuts?)\b',
                    'specialty': r'\b(gluten-free|vegan|sugar-free|organic|artisan|handcrafted)\b'
                }
                
                # Find products by looking for common product elements
                product_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'a', 'div', 'span'], 
                                               class_=re.compile(r'(product|item|menu|title|name)', re.I))
                
                found_products = {}
                detailed_products = []
                
                # Extract products from page structure
                for element in product_elements:
                    element_text = element.get_text().strip()
                    if len(element_text) > 3 and len(element_text) < 50:  # Reasonable product name length
                        for category, pattern in bakery_keywords.items():
                            if re.search(pattern, element_text.lower()):
                                if category in found_products:
                                    found_products[category] += 1
                                else:
                                    found_products[category] = 1
                                detailed_products.append(element_text)
                                break
                
                # Also search in the text content as fallback
                if not found_products:
                    for category, pattern in bakery_keywords.items():
                        matches = re.findall(pattern, text)
                        if matches:
                            found_products[category] = len(matches)
                
                # Get sentiment from the main content
                main_content = soup.find_all(['p', 'div', 'section'], 
                                           class_=re.compile(r'(content|description|about|main)', re.I))
                
                content_text = " ".join([elem.get_text() for elem in main_content]) if main_content else text
                sentiment = sia.polarity_scores(content_text)
                health = min(100, max(0, int((sentiment["pos"] * 100) + 20)))  # Adjusted scoring
                
                # Improved layout
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.subheader("🎂 Bakery Items Found")
                    if found_products:
                        df = pd.DataFrame(found_products.items(), columns=["Category", "Count"]).sort_values("Count", ascending=False)
                        st.dataframe(df, use_container_width=True, height=300)
                        
                        if detailed_products:
                            st.subheader("📋 Product Names Detected")
                            for i, product in enumerate(detailed_products[:10]):  # Show first 10 products
                                st.write(f"{i+1}. {product}")
                        
                        # Enhanced word cloud
                        st.subheader("☁️ Product Word Cloud")
                        word_freq = " ".join([cat for cat, count in found_products.items() for _ in range(count)])
                        if word_freq:
                            wc = WordCloud(width=600, height=300, background_color="white", 
                                        colormap="autumn", collocations=False).generate(word_freq)
                            fig, ax = plt.subplots()
                            ax.imshow(wc, interpolation="bilinear")
                            ax.axis("off")
                            st.pyplot(fig)
                    else:
                        st.warning("No bakery items detected on this website.")
                        st.info("""
                        **Tips for better detection:**
                        - Make sure the website has product information
                        - Try a different bakery website
                        - Some websites may block automated access
                        """)
                
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
                        st.success("This bakery website has very positive content! Great marketing.")
                    elif health > 40:
                        st.info("This bakery website has neutral to moderately positive content.")
                    else:
                        st.warning("This bakery website may need content improvements.")
            
            except Exception as e:
                st.error(f"Error analyzing website: {str(e)}")
                st.info("This website might be blocking automated access. Try a different website or method.")

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
            health = min(100, max(0, int(sentiment["pos"]*100 + 20)))
            
            # Extract bakery items from CSV text
            bakery_keywords = {
                'cake': r'\b(cakes?|cupcakes?|cheesecakes?)\b',
                'cookie': r'\b(cookies?|biscuits?)\b',
                'pastry': r'\b(pastries|pastry|croissants?)\b',
                'bread': r'\b(breads?|baguettes?|buns?)\b',
                'dessert': r'\b(desserts?|sweets?)\b',
                'pie': r'\b(pies?|tarts?)\b'
            }
            
            bakery_items = {}
            for category, pattern in bakery_keywords.items():
                matches = re.findall(pattern, text)
                if matches:
                    bakery_items[category] = len(matches)
            
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
                
                if bakery_items:
                    st.subheader("🍞 Mentioned Bakery Items")
                    for item, count in bakery_items.items():
                        st.write(f"- {item}: {count} mentions")
            
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
