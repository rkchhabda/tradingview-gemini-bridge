import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


def test_health_endpoint():
    """GET /health returns service health status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "tradingview-gemini-bridge"


def test_webhook_e2e_with_mocks():
    """End-to-end webhook test: payload -> Gemini -> Telegram mock."""
    payload = {
        "ticker": "NSE:RELIANCE",
        "exchange": "NSE",
        "interval": "1H",
        "price": "2950.50",
        "indicator_signal": "RSI oversold breakout condition met",
        "secret_token": "my-secret-token",
    }

    with patch("main.analyze_market") as mock_analyze, patch("main.send_telegram_message") as mock_telegram:
        mock_analyze.return_value = "# Analysis\nSignal: BUY\nReason: RSI oversold breakout"
        mock_telegram.return_value = True

        response = client.post(
            "/webhook",
            json=payload,
            headers={"X-Secret-Token": "my-secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Analysis" in data["report"]


def test_webhook_e2e_telegram_failure():
    """Webhook handles Telegram send failure gracefully."""
    payload = {
        "ticker": "NSE:RELIANCE",
        "exchange": "NSE",
        "interval": "1H",
        "price": "2950.50",
        "indicator_signal": "RSI oversold breakout condition met",
        "secret_token": "my-secret-token",
    }

    with patch("main.analyze_market") as mock_analyze, patch("main.send_telegram_message") as mock_telegram:
        mock_analyze.return_value = "# Analysis\nSignal: BUY"
        mock_telegram.return_value = False

        response = client.post(
            "/webhook",
            json=payload,
            headers={"X-Secret-Token": "my-secret-token"},
        )

    assert response.status_code == 502