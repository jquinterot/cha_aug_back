from typing import List, Dict, Any, Optional
import httpx
from app.core.config import OPENAI_API_KEY

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

async def get_openai_response(
    user_message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 256,
    temperature: float = 0.7
) -> str:
    """
    Get a response from OpenAI's chat completion API.
    
    Args:
        user_message: The user's message
        conversation_history: List of previous messages in the conversation
        model: The OpenAI model to use
        max_tokens: Maximum number of tokens to generate
        temperature: Controls randomness (0.0 to 2.0)
    
    Returns:
        The assistant's response as a string
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare messages list with system message and conversation history
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add the new user message
    messages.append({"role": "user", "content": user_message})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        print(f"Sending request to OpenAI API with payload: {payload}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENAI_API_URL,
                headers=headers,
                json=payload
            )
            
            print(f"OpenAI API response status: {response.status_code}")
            print(f"OpenAI API response text: {response.text}")
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error {response.status_code}: {response.text}"
                print(error_msg)
                response.raise_for_status()
            
            data = response.json()
            print(f"OpenAI API response data: {data}")
            
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                print("Warning: Empty content in OpenAI response")
                return "I'm sorry, I couldn't generate a response. Please try again."
                
            return content.strip()
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Error calling OpenAI API: {str(e)}"
        print(error_msg)
        return "I'm sorry, I encountered an error while processing your request."
