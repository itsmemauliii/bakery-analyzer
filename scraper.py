import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text from paragraphs and headings
        texts = [p.get_text() for p in soup.find_all(["p", "h1", "h2", "h3", "li"])]
        return " ".join(texts)
    except Exception as e:
        return f"Error scraping website: {e}"
