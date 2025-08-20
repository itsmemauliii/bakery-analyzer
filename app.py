# app.py
import streamlit as st, requests, re, io
from bs4 import BeautifulSoup
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk; nltk.download("vader_lexicon", quiet=True)

st.set_page_config(page_title="Your Bakery Helper", page_icon="🍞", layout="wide")
st.title("🥐 Your Bakery Helper – Creative Store Analysis")

# --- Functions ---
def fetch_text(url):
    try: return BeautifulSoup(requests.get(url, timeout=10).text,"html.parser").get_text(" ")
    except: return ""

def extract_items(text):
    words=["cake","cakes","cookie","cookies","bread","pastry","pastries",
           "brownie","cupcake","pizza","biscuit","biscuits","gift","khari"]
    tokens=re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return Counter([t for t in tokens if t in words]).most_common(10)

def seasonal_specials(text):
    sp={"christmas":"Festive Cakes 🎄","valentine":"Valentine Offers ❤️","new year":"New Year Treats 🎉"}
    return [(k,v) for k,v in sp.items() if k in text.lower()]

def sentiment_summary(text): return SentimentIntensityAnalyzer().polarity_scores(text)

def plot_sentiment(sentiment):
    labels,vals=["Positive","Neutral","Negative"],[sentiment["pos"],sentiment["neu"],sentiment["neg"]]
    plt.pie(vals,labels=labels,autopct="%1.1f%%",startangle=90,colors=["green","gray","red"])
    buf=io.BytesIO(); plt.savefig(buf,format="PNG"); plt.close(); buf.seek(0); return buf

def recommendations(items):
    rec=[]
    if not items: return ["No products detected – add more bakery content!"]
    top=items[0][0]
    if "cake" in top: rec.append("Promote cakes with seasonal flavors (chocolate, fruit).")
    if "cookie" in [i[0] for i in items]: rec.append("Bundle cookies with beverages for upselling.")
    if "bread" in [i[0] for i in items]: rec.append("Highlight artisan breads or sourdough specials.")
    if len(items)<3: rec.append("Expand product variety on your website.")
    return rec

def generate_pdf(url,items,specials,sentiment,keywords,pie_buf):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf); styles=getSampleStyleSheet(); elems=[]
    elems+=[Paragraph("🍩 Creative Bakery Store Analysis",styles['Title']),
            Paragraph(f"Website: {url}",styles['Normal']),Spacer(1,12)]
    if items: elems.append(Paragraph("Top Items:",styles['Heading2']))
    for k,v in items: elems.append(Paragraph(f"{k.capitalize()} – {v}",styles['Normal']))
    if specials: elems.append(Paragraph("Seasonal Specials:",styles['Heading2']))
    for k,v in specials: elems.append(Paragraph(f"{k.capitalize()} → {v}",styles['Normal']))
    elems.append(Paragraph("Sentiment Scores:",styles['Heading2']))
    elems.append(Paragraph(str(sentiment),styles['Normal'])); elems.append(Image(pie_buf,300,200))
    elems.append(Paragraph("Recommendations:",styles['Heading2']))
    for r in recommendations(items): elems.append(Paragraph("• "+r,styles['Normal']))
    if keywords:
        wc=WordCloud(width=500,height=200,background_color="white").generate(" ".join(keywords))
        img=io.BytesIO(); plt.imshow(wc); plt.axis("off"); plt.savefig(img,format="PNG");plt.close()
        img.seek(0); elems.append(Image(img,400,150))
    doc.build(elems); buf.seek(0); return buf

# --- Streamlit UI ---
url=st.text_input("Enter Bakery Website URL:")
if st.button("Analyze"):
    text=fetch_text(url)
    if not text: st.error("Could not fetch website"); st.stop()
    items, specials, sentiment = extract_items(text), seasonal_specials(text), sentiment_summary(text)
    keywords=[w for w,_ in items]
    col1,col2=st.columns(2)
    with col1: st.subheader("🍰 Items Found"); st.table(items)
    with col2: st.subheader("💬 Sentiment Scores"); st.json(sentiment); pie_buf=plot_sentiment(sentiment); st.image(pie_buf)
    st.subheader("☁️ WordCloud"); wc=WordCloud(width=600,height=300,background_color="white").generate(" ".join(keywords))
    plt.imshow(wc); plt.axis("off"); st.pyplot(plt.gcf()); plt.close()
    pdf=generate_pdf(url,items,specials,sentiment,keywords,pie_buf)
    st.download_button("📥 Download PDF Report",data=pdf,file_name="bakery_report.pdf")
