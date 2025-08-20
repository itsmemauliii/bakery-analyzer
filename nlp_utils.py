from textblob import TextBlob
from collections import Counter
import re
import subprocess
import sys
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

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
