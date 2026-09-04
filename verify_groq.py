import httpx
import json

RENDER_URL = "https://tradingview-gemini-bridge-ii1w.onrender.com"

print("=" * 60)
print("GROQ API REFACTOR - END-TO-END VERIFICATION")
print("=" * 60)
print(f"Target URL: {RENDER_URL}\n")

# Test 1: GET /
print("--- Test 1: GET / ---")
try:
    resp = httpx.get(f"{RENDER_URL}/", timeout=15)
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Body: {json.dumps(data, indent=2)}")
    assert resp.status_code == 200
    assert data["message"] == "TradingView-Gemini-Telegram Bridge is live"
    print("PASS\n")
except Exception as e:
    print(f"FAIL: {e}\n")

# Test 2: GET /health
print("--- Test 2: GET /health ---")
try:
    resp = httpx.get(f"{RENDER_URL}/health", timeout=15)
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Body: {json.dumps(data, indent=2)}")
    assert resp.status_code == 200
    assert data["status"] == "ok"
    assert data["service"] == "tradingview-gemini-bridge"
    print("PASS\n")
except Exception as e:
    print(f"FAIL: {e}\n")

# Test 3: POST /webhook with valid secret token
print("--- Test 3: POST /webhook (valid secret token) ---")
payload = {
    "ticker": "NSE:RELIANCE",
    "exchange": "NSE",
    "interval": "1H",
    "price": "2950.50",
    "indicator_signal": "EMA 20/50 Bullish Crossover",
    "secret_token": "test_token_123"
}
try:
    resp = httpx.post(
        f"{RENDER_URL}/webhook",
        json=payload,
        headers={"X-Secret-Token": "test_token_123"},
        timeout=30
    )
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Status field: {data.get('status')}")
    report = data.get("report", "")
    print(f"Report snippet: {report[:200]}...")
    if resp.status_code == 200 and data.get("status") == "success":
        print("PASS - Full pipeline: webhook -> Groq AI -> Telegram ✅\n")
    else:
        print(f"Result: {resp.status_code} {data.get('status')}\n")
except Exception as e:
    print(f"FAIL: {e}\n")

# Test 4: POST /webhook with invalid secret token
print("--- Test 4: POST /webhook (invalid secret token) ---")
payload_invalid = {
    "ticker": "NSE:RELIANCE",
    "exchange": "NSE",
    "interval": "1H",
    "price": "2950.50",
    "indicator_signal": "Test",
    "secret_token": "wrong-token"
}
try:
    resp = httpx.post(
        f"{RENDER_URL}/webhook",
        json=payload_invalid,
        headers={"X-Secret-Token": "wrong-token"},
        timeout=15
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 401:
        print("PASS - Invalid token correctly rejected with 401 ✅\n")
    else:
        print(f"(Status: {resp.status_code}, expected 401)\n")
except Exception as e:
    print(f"FAIL: {e}\n")

print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)