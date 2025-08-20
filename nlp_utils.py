import re
from collections import Counter
from textblob import TextBlob

def clean_text(text):
    """Basic cleaning."""
    text = re.sub(r"\s+", " ", text)
    return text.lower()

def extract_keywords(text, top_n=20):
    """Top keywords by frequency."""
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    freq = Counter(words)
    return freq.most_common(top_n)

def sentiment_analysis(text):
    """Polarity (-1 to 1) and Subjectivity (0 to 1)."""
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def readability(text):
    """Average word length."""
    words = text.split()
    if not words:
        return 0
    return sum(len(w) for w in words) / len(words)

def extract_products(text):
    """Detect bakery items using regex dictionary (no NLTK)."""
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    food_terms = [
        "cake","cakes","cookie","cookies","bread","breads","bun","buns",
        "pastry","pastries","pizza","khari","biscuit","biscuits",
        "puff","sandwich","donut","muffin","brownie","croissant","roll",
        "toast","pie","tart","cupcake","bagel"
    ]
    matches = [w for w in words if w in food_terms]
    return Counter(matches).most_common()

def extract_entities(text):
    """
    Lightweight entity extractor without TextBlob corpora.
    Returns top repeated capitalized words (likely brand names, places).
    """
    # Match capitalized words (not at sentence start)
    entities = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)
    common = Counter(entities).most_common(10)
    return [e for e, _ in common]

def detect_seasonal_specials(text):
    """Detect seasonal/festival keywords."""
    seasonal_words = {
        "diwali": "Highlight festive hampers and sweets for Diwali promotions.",
        "christmas": "Feature Christmas cakes, cookies, and gift boxes.",
        "new year": "Promote New Year party cakes and combos.",
        "valentine": "Push Valentine’s specials like heart-shaped cakes and chocolates.",
        "easter": "Add Easter eggs, hot cross buns, and themed pastries.",
        "summer": "Offer cold desserts like ice cream cakes and smoothies.",
        "winter": "Highlight warm bakery items like brownies, hot chocolate, and plum cake."
    }
    matches = []
    for word, tip in seasonal_words.items():
        if word in text.lower():
            matches.append((word.capitalize(), tip))
    return matches
