import logging
import azure.functions as func
from rss_listener import fetch_rss_entries
from watchlist_utils import process_entry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🐞 Debug triggered")

    try:
        entries = fetch_rss_entries([
            "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml"
        ])
        if not entries:
            return func.HttpResponse("No PRs found.", status_code=200)

        response = []
        for entry in entries[:5]:  # test first 5 entries
            result = process_entry(entry)
            if result:
                msg, _ = result
                response.append(msg)

        if response:
            return func.HttpResponse("\n\n".join(response), status_code=200)
        else:
            return func.HttpResponse("No qualifying setups.", status_code=200)

    except Exception as e:
        logging.exception("❌ Debug function failed")
        return func.HttpResponse("Debug failure", status_code=500)
