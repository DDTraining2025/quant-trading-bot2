import os
import httpx
from logger import log_error

# Finnhub API configuration
API_KEY = os.getenv("finnhub")
BASE_URL = "https://finnhub.io/api/v1"

def get_quote(ticker: str) -> dict:
    """
    Fetches real-time quote data for a given ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        JSON response with keys like:
        - c: current price
        - h: high price of day
        - l: low price of day
        - o: open price of day
        - pc: previous close
    """
    url = f"{BASE_URL}/quote"
    params = {"symbol": ticker, "token": API_KEY}
    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"Error fetching quote for {ticker}", e)
        return {}

def get_company_profile(ticker: str) -> dict:
    """
    Fetches company profile data for a given ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        JSON response with company details, including marketCapitalization.
    """
    url = f"{BASE_URL}/stock/profile2"
    params = {"symbol": ticker, "token": API_KEY}
    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"Error fetching company profile for {ticker}", e)
        return {}

def get_float_and_shares_outstanding(ticker: str) -> dict:
    """
    Fetches float and shares outstanding metrics for a given ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dict with keys 'float' and 'shares_outstanding'
    """
    url = f"{BASE_URL}/stock/metric"
    params = {"symbol": ticker, "metric": "all", "token": API_KEY}
    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("metric", {})
        return {
            "float": data.get("float"),
            "shares_outstanding": data.get("sharesOutstanding")
        }
    except Exception as e:
        log_error(f"Error fetching float data for {ticker}", e)
        return {}

def get_daily_high_low_close(ticker: str) -> tuple[float | None, float | None]:
    """
    Retrieves the high and close prices of the current trading day.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Tuple of (high, close), or (None, None) on error.
    """
    try:
        quote = get_quote(ticker)
        return quote.get("h"), quote.get("c")
    except Exception as e:
        log_error(f"Error fetching daily high/close for {ticker}", e)
        return None, None
