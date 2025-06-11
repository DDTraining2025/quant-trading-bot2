import requests
import os
import logging

def fetch_benzinga_news(published_since):
    api_key = os.getenv("BEZINGA")
    if not api_key or api_key.startswith("https://"):
        logging.error("🔥 BEZINGA API KEY not loaded correctly! Value: %s", repr(api_key))
        raise ValueError("BEZINGA API KEY not set or is still a Key Vault URI.")

    url = "https://api.benzinga.com/api/v2/news"
    params = {
        "token": api_key,
        "display_output": "full",
        "published_since": published_since
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        logging.info("Benzinga API status %s, response: %s...", response.status_code, response.text[:200])
        if response.status_code != 200:
            raise Exception(f"Benzinga API Error: HTTP {response.status_code} - {response.text}")

        if not response.text.strip():
            logging.warning("Benzinga API returned empty body!")
            return []
        return response.json()
    except Exception as e:
        logging.exception("Error fetching/parsing Benzinga news")
        return []
