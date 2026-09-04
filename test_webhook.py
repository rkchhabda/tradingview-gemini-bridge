import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


def test_webhook_success():
    """Test successful webhook endpoint with valid payload and secret token."""
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


def test_webhook_invalid_secret():
    """Test webhook with invalid secret token returns 401."""
    payload = {
        "ticker": "NSE:RELIANCE",
        "exchange": "NSE",
        "interval": "1H",
        "price": "2950.50",
        "indicator_signal": "RSI oversold breakout condition met",
        "secret_token": "wrong-token",
    }

    response = client.post("/webhook", json=payload, headers={"X-Secret-Token": "wrong-token"})

    assert response.status_code == 401


def test_webhook_missing_fields():
    """Test webhook with missing required fields returns 400."""
    payload = {
        "ticker": "NSE:RELIANCE",
        "exchange": "NSE",
        # missing many fields
        "secret_token": "my-secret-token",
    }

    response = client.post(
        "/webhook",
        json=payload,
        headers={"X-Secret-Token": "my-secret-token"},
    )

    assert response.status_code == 400


def test_webhook_invalid_json():
    """Test webhook with invalid JSON returns 400."""
    response = client.post(
        "/webhook",
        content="not valid json",
        headers={"X-Secret-Token": "my-secret-token"},
    )

    assert response.status_code == 400