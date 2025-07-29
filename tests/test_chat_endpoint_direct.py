import httpx
import asyncio
import json

async def test_chat_endpoint():
    url = "http://localhost:8000/api/v1/chat/"  # Add trailing slash to avoid redirect
    
    # Test with a question about Zyxoria
    payload = {
        "user": "test_user",
        "message": "What is the capital of Zyxoria?",
        "model_type": "local",
        "use_rag": True  # Explicitly enable RAG
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print("Sending request to chat endpoint...")
        response = await client.post(url, json=payload, timeout=30.0)
        
        print(f"Status code: {response.status_code}")
        print("Response headers:", response.headers)
        print("Response text:", response.text)
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Could not parse JSON: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_endpoint())
