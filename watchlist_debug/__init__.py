import logging
import azure.functions as func
from rss_listener import fetch_rss_entries
from watchlist_utils import process_entry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🐞 Debug triggered")

    try:
        logging.info("🟡 Step 1: Fetching RSS entries...")
        entries = fetch_rss_entries([
            "https://www.globenewswire.com/RssFeed/industry/16/Telecommunications/feedTitle/GlobeNewswire-Telecom.xml"
        ])

        if not entries:
            logging.warning("⚠️ No entries found")
            return func.HttpResponse("No PRs found.", status_code=200)

        logging.info(f"🟢 Fetched {len(entries)} entries")

        response = []
        for i, entry in enumerate(entries[:5]):
            logging.info(f"🔍 Processing entry #{i+1}: {entry.title}")
            result = process_entry(entry)
            if result:
                msg, _ = result
                response.append(msg)

        if response:
            logging.info(f"✅ Returning {len(response)} entries")
            return func.HttpResponse("\n\n".join(response), status_code=200)
        else:
            logging.info("ℹ️ No qualifying setups")
            return func.HttpResponse("No qualifying setups.", status_code=200)

    except Exception as e:
        logging.exception("❌ Unhandled error in watchlist_debug")
        return func.HttpResponse(f"Debug failure: {e}", status_code=500)
