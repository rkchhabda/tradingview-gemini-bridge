# TradingView-Gemini-Telegram Microservice - Deployment Guide

## Local Development

### 1. Start the server locally
```bash
# From the project root
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Verify health check
```bash
curl http://127.0.0.1:8000/health
# Expected: {"status":"ok","service":"tradingview-gemini-bridge"}
```

### 3. Smoke-test the webhook
```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: my-secret-token" \
  -d '{"ticker":"NSE:RELIANCE","exchange":"NSE","interval":"1H","price":"2950.50","indicator_signal":"RSI oversold breakout condition met","secret_token":"my-secret-token"}'
```

---

## Deployment to Render.com

### Prerequisites
- A Render.com account
- API keys configured in the Render dashboard (or via .env file)

### 1. Connect Repository
- Create a new Web Service on Render
- Select "GitHub" and connect your repository
- Root Directory: `/` (root of repo)

### 2. Service Settings
- **Name**: `tradingview-gemini-bridge`
- **Environment**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

### 3. Environment Variables
Add these as Secrets in the Render dashboard:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `TELEGRAM_BOT_TOKEN` - Your Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Your target Telegram Chat ID
- `SECRET_TOKEN` - Shared secret for TradingView webhook auth

---

## Deployment to Railway

### 1. Create New Project
- Log in to Railway and click "New Project"
- Select "Deploy from GitHub" and choose this repository

### 2. Service Configuration
- Railway automatically detects the `Dockerfile` and `procfile`
- No additional configuration needed if Docker is enabled

### 3. Environment Variables
Add vars in the Railway Dashboard:
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SECRET_TOKEN`

---

## Deployment with Docker

### 1. Build and Run
```bash
docker build -t tradingview-gemini-bridge .
docker run -p 8000:8080 \
  -e GEMINI_API_KEY=your_key \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  -e SECRET_TOKEN=your_secret \
  tradingview-gemini-bridge
```

### 2. Verify
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: your_secret" \
  -d '{"ticker":"NSE:RELIANCE","exchange":"NSE","interval":"1H","price":"2950.50","indicator_signal":"RSI oversold breakout condition met","secret_token":"your_secret"}'
```

---

## TradingView Webhook Payload Configuration

### cURL Smoke Test Command
```bash
curl -X POST YOUR_DEPLOYED_URL/webhook \
  -H "Content-Type: application/json" \
  -H "X-Secret-Token: YOUR_SECRET_TOKEN" \
  -d '{"ticker":"NSE:RELIANCE","exchange":"NSE","interval":"1H","price":"2950.50","indicator_signal":"RSI oversold breakout condition met","secret_token":"YOUR_SECRET_TOKEN"}'
```

### Exact JSON Payload for TradingView Alert
Copy and paste this block into your TradingView alert webhook URL/settings. All variables are dynamically mapped:

```json
{
  "ticker": "{{ticker}}",
  "exchange": "{{exchange}}",
  "interval": "{{interval}}",
  "price": "{{close}}",
  "indicator_signal": "{{signal}}",
  "secret_token": "<YOUR_SECURITY_TOKEN>"
}
```

### Variable Mapping Reference
| TradingView Variable | Mapped To          |
| -------------------- | ------------------ |
| `{{ticker}}`         | NSE:RELIANCE (example) |
| `{{exchange}}`       | NSE (example)      |
| `{{interval}}`       | 1H (example)       |
| `{{close}}`          | 2950.50 (example)  |
| `{{signal}}`         | RSI oversold breakout condition met (example) |
| `secret_token`       | Your shared secret |

### TradingView Alert Setup Steps
1. In TradingView, create a new alert with your strategy conditions
2. Click the "Webhook URL" button
3. Set the URL to: `https://your-service-url.onrender.com/webhook` (or your deployed endpoint)
4. Copy the JSON payload above into the "Message Template" or alert note
5. Set the `secret_token` in TradingView to match your `.env SECRET_TOKEN`
6. Save the alert