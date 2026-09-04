#!/usr/bin/env python3
"""Smoke test script for TradingView-Gemini-Telegram microservice.

Usage:
    python smoke_test.py https://your-app.onrender.com
    python smoke_test.py http://127.0.0.1:8000
"""

import sys
import json
import httpx


def test_health(url: str) -> bool:
    """Test GET /health endpoint."""
    try:
        response = httpx.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "ok", f"Expected status ok, got {data}"
            assert data.get("service") == "tradingview-gemini-bridge", f"Expected service name, got {data}"
            print(f"[PASS] /health -> {data}")
            return True
        else:
            print(f"[FAIL] /health -> status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] /health -> error: {e}")
        return False


def test_webhook(url: str) -> bool:
    """Test POST /webhook with a mock TradingView payload."""
    payload = {
        "ticker": "NSE:RELIANCE",
        "exchange": "NSE",
        "interval": "1H",
        "price": "2950.50",
        "indicator_signal": "RSI oversold breakout condition met",
        "secret_token": "my-secret-token",
    }

    headers = {"X-Secret-Token": "my-secret-token", "Content-Type": "application/json"}

    try:
        response = httpx.post(f"{url}/webhook", json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"[PASS] /webhook -> success, report snippet: {data.get('report', '')[:60]}...")
                return True
            else:
                print(f"[FAIL] /webhook -> unexpected response: {data}")
                return False
        else:
            print(f"[FAIL] /webhook -> status {response.status_code}, body: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] /webhook -> error: {e}")
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python smoke_test.py <target_url>")
        sys.exit(1)

    url = sys.argv[1].rstrip("/")
    print(f"\n=== Smoke Test ===\nTarget: {url}\n")

    health_ok = test_health(url)
    webhook_ok = test_webhook(url)

    print(f"\n=== Results ===")
    print(f"  /health:    {'PASS' if health_ok else 'FAIL'}")
    print(f"  /webhook:   {'PASS' if webhook_ok else 'FAIL'}")

    if health_ok and webhook_ok:
        print("\n[SERVICE READY] - All smoke tests passed.")
        sys.exit(0)
    else:
        print("\n[SERVICE ISSUES] - Some tests failed. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()