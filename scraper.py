import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        # collect visible text
        texts = []
        for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "span", "a"]):
            if tag.get_text().strip():
                texts.append(tag.get_text().strip())

        return " ".join(texts)

    except Exception as e:
        return f"Error: {str(e)}"
