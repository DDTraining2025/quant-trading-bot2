from flask import Flask, request, jsonify
from ib_insync import IB, Stock, MarketOrder
import threading
import requests
from datetime import datetime
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

# === Flask App ===
app = Flask(__name__)
ib = IB()
last_buy_qty = {}

# === IBKR Connection ===
def connect_ib():
    try:
        ib.connect('127.0.0.1', 7497, clientId=1)
        logging.info("Connected to IBKR")
    except Exception as e:
        logging.error("Could not connect to IBKR: %s", e)

threading.Thread(target=connect_ib).start()

# === Webhook Handler ===
@app.route('/webhook', methods=['POST'])
def webhook():
    global last_buy_qty
    token = request.args.get("token")
    if token != WEBHOOK:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid payload'}), 400
        
    try:
        action = data['action'].upper()
        symbol = data['symbol'].upper()
        # ... rest of your trade logic


