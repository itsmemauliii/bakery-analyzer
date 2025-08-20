from textblob import TextBlob
from collections import Counter
import re
import nltk

# Ensure stopwords are available
nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words("english"))

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_keywords(text, top_n=10):
    words = [
        w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text)
        if w.lower() not in STOPWORDS
    ]
    common_words = Counter(words).most_common(top_n)
    return common_words

def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def readability(text):
    words = text.split()
    avg_len = sum(len(w) for w in words) / len(words) if words else 0
    return round(avg_len, 2)
