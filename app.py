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
    url = st.text_input("🔗 Enter Bakery Website URL:", "https://www.bakingo.com")
    
    if st.button("🔍 Analyze Website", type="primary"):
        with st.spinner("Analyzing website content..."):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Strategy 1: Look for common e-commerce product elements
                product_elements = []
                
                # Look for product cards, items, etc.
                selectors = [
                    '[class*="product"]', '[class*="item"]', '[class*="card"]', 
                    '[class*="menu"]', '.product', '.item', '.card', '.menu-item',
                    'h1', 'h2', 'h3', 'h4', 'li a', '.title', '.name'
                ]
                
                for selector in selectors:
                    product_elements.extend(soup.select(selector))
                
                # Extract text from potential product elements
                potential_products = []
                for element in product_elements:
                    text = element.get_text(strip=True)
                    if 3 < len(text) < 100:  # Reasonable product name length
                        potential_products.append(text)
                
                # Strategy 2: Look for navigation menu items (often contain categories)
                nav_elements = soup.select('nav a, .menu a, .navigation a, [class*="nav"] a')
                nav_items = [elem.get_text(strip=True) for elem in nav_elements if 2 < len(elem.get_text(strip=True)) < 50]
                
                # Strategy 3: Analyze page text for bakery-related content
                main_text = soup.get_text()
                lines = main_text.split('\n')
                content_lines = [line.strip() for line in lines if 10 < len(line.strip()) < 200]
                
                # Combine all sources
                all_text = potential_products + nav_items + content_lines
                
                # Define bakery categories and their keywords
                bakery_categories = {
                    'Cakes': ['cake', 'cupcake', 'cheesecake', 'birthday', 'anniversary', 'wedding'],
                    'Pastries': ['pastry', 'croissant', 'danish', 'éclair', 'puff', 'palmier'],
                    'Cookies': ['cookie', 'biscuit', 'macaron', 'biscotti', 'shortbread'],
                    'Breads': ['bread', 'baguette', 'loaf', 'bun', 'roll', 'bagel', 'ciabatta'],
                    'Desserts': ['dessert', 'mousse', 'pudding', 'tart', 'pie', 'flan', 'soufflé'],
                    'Specialty': ['vegan', 'gluten-free', 'sugar-free', 'organic', 'artisan', 'custom']
                }
                
                # Categorize found items
                categorized_products = {category: [] for category in bakery_categories.keys()}
                uncategorized = []
                
                for text in all_text:
                    text_lower = text.lower()
                    categorized = False
                    
                    for category, keywords in bakery_categories.items():
                        for keyword in keywords:
                            if keyword in text_lower:
                                categorized_products[category].append(text)
                                categorized = True
                                break
                        if categorized:
                            break
                    
                    if not categorized and len(text) > 3:
                        uncategorized.append(text)
                
                # Get sentiment from the main content
                main_content = soup.find_all(['p', 'div', 'section'])
                content_text = " ".join([elem.get_text() for elem in main_content[:10]]) if main_content else main_text
                sentiment = sia.polarity_scores(content_text)
                health = min(100, max(0, int((sentiment["pos"] * 100) + 30)))  # Adjusted scoring
                
                # Display results
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.subheader("🎂 Bakery Products Found")
                    
                    found_categories = False
                    for category, products in categorized_products.items():
                        if products:
                            found_categories = True
                            st.markdown(f"**{category}**")
                            for product in set(products[:5]):  # Show up to 5 unique products per category
                                st.write(f"- {product}")
                    
                    if not found_categories:
                        st.warning("No specific bakery products detected.")
                        st.info("""
                        **This could be because:**
                        - The website doesn't have a clear product listing
                        - The website structure is complex
                        - The bakery specializes in custom orders
                        """)
                    
                    # Show uncategorized items that might be products
                    if uncategorized:
                        st.subheader("📋 Other Potential Products")
                        for item in set(uncategorized[:10]):
                            st.write(f"- {item}")
                
                with col2:
                    st.subheader("📊 Sentiment Analysis")
                    
                    # Sentiment gauges
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive 😊", f"{sentiment['pos']*100:.1f}%")
                    with col2:
                        st.metric("Neutral 😐", f"{sentiment['neu']*100:.1f}%")
                    with col3:
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
                st.info("This website might be blocking automated access. Try a different website.")

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
            
            # Simple word cloud
            st.subheader("☁️ Word Cloud")
            wc = WordCloud(width=600, height=300, background_color="white", 
                         colormap="viridis").generate(text)
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
            
            # Sentiment analysis
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
            
            # Additional insights
            st.subheader("💡 Customer Feedback Insights")
            if health > 70:
                st.success("Your customers are very satisfied! Keep up the good work.")
            elif health > 40:
                st.info("Your customers are generally satisfied but there's room for improvement.")
            else:
                st.warning("Your customers seem dissatisfied. Consider making improvements.")
                
            st.info("Want to improve your scores? Consider collecting more data through our form in the Data Collection section!")
