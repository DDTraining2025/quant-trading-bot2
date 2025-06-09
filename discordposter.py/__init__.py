def send_no_news_message(reason="No qualifying PRs found."):
    """
    Posts a heartbeat message to Discord if no alerts were sent.
    """
    if not DISCORD_WEBHOOK_URL:
        logging.error("[DISCORD] ❌ Webhook URL not set for no-news message.")
        return

    try:
        payload = {
            "content": f"⚠️ No PR alerts sent.\n📄 Reason: {reason}"
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code == 204:
            logging.info("[DISCORD] ✅ No-news message sent")
        else:
            logging.warning(f"[DISCORD] ⚠️ No-news message failed: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"[DISCORD] ❌ Error sending no-news message: {e}")
