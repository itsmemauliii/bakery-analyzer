# Bakery Analyzer

**AI-powered insights for bakery businesses.**
A Streamlit web app that performs website content analysis, customer sentiment analysis, and feedback visualization for bakeries, with beautiful UI and modern design.

---

## Overview

**Bakery Analyzer** helps bakeries, cafes, and pastry shops gain quick insights from:

* Their **websites** (content health, SEO keywords, sentiment tone)
* **Customer feedback datasets (CSVs)**, analyzing sentiment and generating visualizations
* **Bakery data submissions** for benchmarking and model training

It’s built with a blend of **Streamlit**, **BeautifulSoup**, **NLTK**, and **WordCloud**, wrapped in a custom warm-toned UI inspired by classic bakery aesthetics.

---

## Features

### Website Analyzer

* Scrapes and cleans website text using `BeautifulSoup`
* Counts bakery-related keywords and categories
* Runs sentiment analysis via NLTK’s VADER model
* Generates content quality score & improvement recommendations

### CSV Feedback Analyzer

* Upload a CSV of customer feedback or reviews
* Runs sentiment analysis across review text
* Displays metrics (positive/negative/neutral ratio)
* Generates a dynamic **Word Cloud** for frequent terms

### Bakery Data Uploader

* Collects structured info from bakery owners (type, products, ratings)
* Calculates summary metrics and displays aggregated stats
* Helps train and benchmark industry-level models

---

## UI & Design Highlights

* Enhanced **CSS theming** for bakery-inspired colors (`#FF7043`, `#FFF3E0`, `#E64A19`)
* Gradient buttons, shadowed cards, and soft borders
* Animated progress bars and responsive layout
* Consistent typography and section styling

---

## Tech Stack

| Component          | Library / Framework     |
| ------------------ | ----------------------- |
| Frontend           | Streamlit               |
| Styling            | Custom CSS + HTML       |
| Data Handling      | pandas                  |
| Sentiment Analysis | NLTK (VADER)            |
| Visualization      | Matplotlib, WordCloud   |
| Web Scraping       | BeautifulSoup, requests |

---

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/itsmemauliii/bakery-analyzer.git
cd bakery-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have NLTK data installed yet:

```bash
python -m nltk.downloader vader_lexicon
```

### 3️. Run the Streamlit app

```bash
streamlit run app.py
```

Then open your browser at **[http://localhost:8501](http://localhost:8501)**

---

## Project Structure

```
bakery-analyzer
 ┣ app.py               # Main Streamlit app
 ┣ requirements.txt     # Python dependencies
 ┣ README.md            # You’re reading this file
 ┗ assets/ (optional)   # WordClouds, screenshots, or dataset samples
```

---

## Example Use Cases

| Use Case                | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| **Bakery Owners**       | Quickly analyze your website and customer feedback       |
| **Marketing Teams**     | Track sentiment around product launches                  |
| **Students / Analysts** | Learn NLP and sentiment analysis with an applied dataset |

---

## Author

**Developed by [Mauli Patel](https://github.com/maulipatel)**
* AI & Data Science enthusiast | Streamlit + NLP Projects

---

## License

MIT License © 2025 - Mauli Patel
Feel free to use, remix, and learn from this project. Just give credit where it’s due.
