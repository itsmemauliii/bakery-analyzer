import re
import nltk
from collections import Counter
from textblob import TextBlob

# Ensure required NLTK data is available
for pkg in ["punkt", "punkt_tab", "averaged_perceptron_tagger"]:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.lower()

def extract_keywords(text, top_n=20):
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    freq = Counter(words)
    return freq.most_common(top_n)

def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def readability(text):
    words = text.split()
    if not words:
        return 0
    return sum(len(w) for w in words) / len(words)

def extract_products(text):
    """Extract probable bakery items (nouns only)."""
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    # keep only nouns
    nouns = [word.lower() for word, pos in tagged if pos.startswith("NN")]

    # filter with bakery food dictionary
    food_terms = [
        "cake","cakes","cookie","cookies","bread","breads","bun","buns",
        "pastry","pastries","pizza","khari","biscuit","biscuits",
        "puff","sandwich","donut","muffin","brownie","croissant","roll",
        "toast","pie","tart","cupcake","bagel"
    ]

    matches = [w for w in nouns if w in food_terms]
    return Counter(matches).most_common()

def extract_entities(text):
    blob = TextBlob(text)
    return blob.noun_phrases[:10]

def detect_seasonal_specials(text):
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
