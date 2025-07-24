import httpx
from app.core.config import OPENAI_API_KEY

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

async def get_openai_response(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 256,
        "temperature": 0.7
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            print(f"OpenAI API error {response.status_code}: {response.text}")
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
