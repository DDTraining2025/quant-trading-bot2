import spacy
from transformers import pipeline

# Load FinBERT or use placeholder
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def analyze_sentiment(text):
    result = sentiment_pipeline(text[:512])[0]
    return result['label'], result['score']

def tag_keywords(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text.lower())
    keywords = []

    for token in doc:
        if token.text in {"contract", "approval", "acquisition", "merger", "fda", "patent", "partnership"}:
            keywords.append(token.text)
    
    return list(set(keywords))
