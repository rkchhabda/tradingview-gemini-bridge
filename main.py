from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from services.gemini_service import analyze_market_signal  # Groq API v2
from services.telegram_service import send_telegram_message

app = FastAPI(title="TradingView-Gemini-Telegram Webhook")


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "tradingview-gemini-bridge"})


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse({
        "message": "TradingView-Gemini-Telegram Bridge is live",
        "health_check": "/health",
        "documentation": "/docs"
    })


def verify_secret_token(request: Request) -> None:
    secret_token = request.headers.get("X-Secret-Token")
    if not secret_token or secret_token != SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing secret token",
        )


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    verify_secret_token(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    required_fields = ["ticker", "exchange", "interval", "price", "indicator_signal"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing fields: {', '.join(missing)}",
        )

    try:
        report = analyze_market_signal(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI API error: {str(e)}",
        )

    try:
        sent = await send_telegram_message(report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Telegram send error: {str(e)}",
        )

    if not sent:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send Telegram message",
        )

    return JSONResponse({"status": "success", "report": report})