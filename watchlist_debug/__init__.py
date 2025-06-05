import unittest
from unittest.mock import patch, MagicMock
from watchlist import process_entry

class TestWatchlistProcessEntry(unittest.TestCase):
    
    @patch("watchlist.get_quote")
    @patch("watchlist.get_company_profile")
    @patch("watchlist.analyze_sentiment")
    @patch("watchlist.tag_keywords")
    def test_valid_entry(self, mock_keywords, mock_sentiment, mock_profile, mock_quote):
        # Mocked entry object
        entry = MagicMock()
        entry.title = "$ABC wins $25M telecom contract"
        entry.link = "http://example.com/pr"
        entry.summary = "Awarded major telecom infrastructure contract."

        # Mocking NLP + FinBERT
        mock_sentiment.return_value = ("Positive", 0.95)
        mock_keywords.return_value = ["contract", "telecom"]

        # Mocking API responses
        mock_quote.return_value = {"c": 0.75, "v": 500000}
        mock_profile.return_value = {"marketCapitalization": 35}

        result = process_entry(entry)

        self.assertIsNotNone(result)
        msg, log_data = result
        self.assertIn("$ABC", msg)
        self.assertEqual(log_data["ticker"], "ABC")
        self.assertGreaterEqual(log_data["mcp_score"], 0)

    def test_entry_with_no_ticker(self):
        entry = MagicMock()
        entry.title = "Company announces new partnership"
        entry.link = "http://example.com/pr"
        entry.summary = "Exciting new tech partnership."

        result = process_entry(entry)
        self.assertIsNone(result)

    @patch("watchlist.get_quote")
    @patch("watchlist.get_company_profile")
    @patch("watchlist.analyze_sentiment")
    @patch("watchlist.tag_keywords")
    def test_market_cap_filter(self, mock_keywords, mock_sentiment, mock_profile, mock_quote):
        entry = MagicMock()
        entry.title = "$XYZ releases new AI platform"
        entry.link = "http://example.com/pr"
        entry.summary = "Innovative product launch."

        mock_sentiment.return_value = ("Neutral", 0.5)
        mock_keywords.return_value = ["ai", "platform"]
        mock_quote.return_value = {"c": 1.20, "v": 100000}
        mock_profile.return_value = {"marketCapitalization": 100}  # > $50M cap

        result = process_entry(entry)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
