import spacy
from textblob import TextBlob
from collections import Counter
import re

# Try loading spaCy model safely
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # last-resort fallback in case requirements.txt failed
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_keywords(text, top_n=10):
    doc = nlp(text.lower())
    words = [token.text for token in doc if token.is_alpha and not token.is_stop]
    common_words = Counter(words).most_common(top_n)
    return common_words

def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def readability(text):
    words = text.split()
    avg_len = sum(len(w) for w in words) / len(words) if words else 0
    return round(avg_len, 2)
