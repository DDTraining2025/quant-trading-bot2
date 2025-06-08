import spacy
from transformers import pipeline, Pipeline
from logger import log_error

# Initialize sentiment pipeline (FinBERT) once
try:
    sentiment_pipeline: Pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
except Exception as e:
    log_error("Error loading FinBERT sentiment pipeline", e)
    sentiment_pipeline = pipeline("sentiment-analysis")

# Load spaCy model once, disabling unused components for performance
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except Exception as e:
    log_error("Error loading spaCy model", e)
    nlp = spacy.blank("en")

def analyze_sentiment(text: str) -> tuple[str, float]:
    """
    Analyze sentiment of the input text using FinBERT.

    Args:
        text: The text to analyze.

    Returns:
        A tuple containing (label, confidence_score).
    """
    try:
        truncated = text[:512]  # Truncate to pipeline limit
        result = sentiment_pipeline(truncated)[0]
        label = result.get("label", "")
        score = float(result.get("score", 0.0))
        return label, score
    except Exception as e:
        log_error("Error during sentiment analysis", e)
        return "", 0.0

def tag_keywords(text: str) -> list[str]:
    """
    Extract specific keywords from the text using spaCy.

    Args:
        text: The text to process.

    Returns:
        A list of unique keywords found.
    """
    try:
        doc = nlp(text.lower())
        keywords = {
            token.text
            for token in doc
            if token.text in {"contract", "approval", "acquisition", "merger", "fda", "patent", "partnership"}
        }
        return list(keywords)
    except Exception as e:
        log_error("Error during keyword extraction", e)
        return []
