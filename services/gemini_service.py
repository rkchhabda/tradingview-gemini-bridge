from openai import OpenAI

# Experimental hardcoded Groq configuration for ultra-fast inference
GROQ_API_KEY = "GROQ_API_KEY_EXPERIMENTAL"
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)


def analyze_market_signal(payload: dict) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert quantitative financial analyst providing actionable market insights."},
            {"role": "user", "content": f"Analyze this TradingView alert signal: {payload}"},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content