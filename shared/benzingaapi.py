# shared/benzingaapi.py

import os
import requests
import logging
import xml.etree.ElementTree as ET

def fetch_recent_news(published_since):
    """
    Fetch recent news headlines from Benzinga News API, returned as a list of dicts.
    published_since: ISO8601 string, e.g. "2025-06-11T20:00:00"
    """
    api_key = os.getenv("BEZINGA")
    if not api_key or api_key.startswith("https://"):
        logging.error("❌ BEZINGA API key not loaded. Value: %s", repr(api_key))
        raise ValueError("BEZINGA API key is not set or is a Key Vault URI.")

    url = "https://api.benzinga.com/api/v2/news"
    params = {
        "token": api_key,
        "display_output": "full",
        "published_since": published_since
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        logging.info("Benzinga API status %s, response: %s...", resp.status_code, resp.text[:200])

        if resp.status_code != 200:
            raise Exception(f"Benzinga API error: {resp.status_code} - {resp.text[:120]}")

        news_items = []
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item"):
            news_id = item.findtext("id")
            title = item.findtext("title")
            url = item.findtext("url") or item.findtext("url1")
            created = item.findtext("created") or item.findtext("updated")
            news_items.append({
                "id": news_id,
                "title": title,
                "url": url,
                "created": created
            })
        return news_items

    except Exception as e:
        logging.exception("Error fetching or parsing Benzinga news")
        return []
