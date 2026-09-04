from google.genai import types
from google import genai

from config import settings


def create_gemini_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_market(payload: dict) -> str:
    client = create_gemini_client()

    prompt = f"""
You are a professional trading analyst. Analyze the following market data from a TradingView alert and provide a concise Markdown report.

Payload data:
- Ticker: {payload.get('ticker', 'N/A')}
- Exchange: {payload.get('exchange', 'N/A')}
- Interval: {payload.get('interval', 'N/A')}
- Price: {payload.get('price', 'N/A')}
- Indicator Signal: {payload.get('indicator_signal', 'N/A')}

Please provide:
1. Signal validity assessment (is this a trustworthy signal?)
2. Key risk levels
3. Immediate execution considerations
4. Suggested action (BUY/SELL/HOLD with reasoning)

Keep the response concise and formatted in clean Markdown.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )

    return response.text or "No response from Gemini API"