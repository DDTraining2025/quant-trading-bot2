from flask import Flask, request, jsonify
from ib_insync import IB, Stock, MarketOrder
import threading
import asyncio
import requests
import os
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("tradebot.log"),
        logging.StreamHandler()
    ]
)

# === Azure Key Vault Setup ===
KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME")
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URI, credential=credential)

DISCORD_WEBHOOK_URL = client.get_secret("DISCORD-WEBHOOK-URL").value
WEBHOOK_TOKEN = client.get_secret("WEBHOOK-TOKEN").value

def notify_discord(message: str):
    try:
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        if response.status_code != 204:
            logging.warning(f"Discord notification failed: {response.status_code} {response.text}")
    except Exception as e:
        logging.error("Error sending Discord notification: %s", e)


# === Flask App ===
app = Flask(__name__)
ib = IB()
last_buy_qty = {}

# === Proper IBKR Async Connection ===
def connect_ib():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(ib.connectAsync('127.0.0.1', 7497, clientId=1))
        logging.info("Connected to IBKR")
    except Exception as e:
        logging.error("Could not connect to IBKR: %s", e)
    finally:
        loop.close()

threading.Thread(target=connect_ib, daemon=True).start()

# === Webhook Handler ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Quant Trading Bot is running. Use POST /webhook with a token to send trade requests."

@app.route('/webhook', methods=['POST'])
def webhook():
    global last_buy_qty

    data = request.get_json()
    if not data:
        logging.warning("No JSON received in request")
        return jsonify({'error': 'Invalid payload'}), 400

    token = data.get("token")
    if token != WEBHOOK_TOKEN:
        logging.warning("Unauthorized access attempt with token: %s", token)
        return jsonify({"error": "Unauthorized"}), 403

    if not ib.isConnected():
        warning_msg = f"⚠️ IBKR NOT CONNECTED – Simulated trade: {data.get('action')} {data.get('quantity')} {data.get('symbol')}"
        logging.warning(warning_msg)
        notify_discord(warning_msg)
        return jsonify({"warning": "IBKR not connected – Discord notified"}), 202
        
    try:
        action = data['action'].upper()
        symbol = data['symbol'].upper()
        quantity = int(data.get("quantity", 0))

        logging.info(f"Received trade request: {action} {quantity} {symbol}")

        notify_discord(f"📈 Trade Request: **{action} {quantity} {symbol}**")


        return jsonify({
            "status": "Trade accepted",
            "symbol": symbol,
            "action": action,
            "quantity": quantity
        })

    except KeyError as e:
        return jsonify({'error': f'Missing key in payload: {e}'}), 400
