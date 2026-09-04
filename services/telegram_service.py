TELEGRAM_BOT_TOKEN = "8831094276:AAHs9EuDvOyMv6qz558ZbcsBXrRnOFPDD94"
TELEGRAM_CHAT_ID = "885923926"

import httpx


async def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
        )

    return response.status_code == 200