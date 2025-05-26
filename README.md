# Quant Trading Bot

A secure, cloud-deployable trading bot that integrates TradingView alerts with IBKR and Discord using Azure services.

## ✅ Features
- TradingView webhook receiver
- Secure IBKR trade execution
- Discord trade notifications
- Azure Key Vault integration
- Deployable to Azure App Service

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yourname/quant-trading-bot.git
cd quant-trading-bot
pip install -r requirements.txt
```

### 2. Setup Azure Key Vault with:
- `DISCORD-WEBHOOK-URL`
- `WEBHOOK-TOKEN`

### 3. Run locally

```bash
python app.py
```

Or deploy to Azure App Service with `startup.sh`.

### 4. Test using Postman or TradingView

Webhook endpoint:
```
https://yourapp.azurewebsites.net/webhook?token=YOUR_TOKEN
```
