import httpx
import time
import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOCAL_MODEL_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_TIMEOUT = 300  # 5 minutes for initial response
MAX_RETRIES = 3

class LocalModelError(Exception):
    """Custom exception for local model errors"""
    pass

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True
)
async def get_local_model_response(
    user_message: str,
    system_message: str = "You are a helpful assistant.",
    model: str = "llama-3.2-3b-instruct",
    temperature: float = 0.7,
    max_tokens: int = 256,
    timeout: int = DEFAULT_TIMEOUT
) -> str:
    """
    Get a response from the local LM Studio model with retry logic.
    
    Args:
        user_message: The user's message
        system_message: The system message to set the assistant's behavior
        model: The model to use (must match the model loaded in LM Studio)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate (-1 for no limit)
        timeout: Timeout in seconds for the request
        
    Returns:
        str: The generated response text
        
    Raises:
        HTTPException: If there's an error getting a response from the local model
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": max(0.1, min(1.0, temperature)),  # Clamp between 0.1 and 1.0
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "stream": False
    }
    
    try:
        logger.info(f"Sending request to local model: {model}")
        
        timeout_config = httpx.Timeout(timeout, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.post(
                LOCAL_MODEL_URL,
                headers=headers,
                json={k: v for k, v in payload.items() if v is not None}
            )
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("choices") or not isinstance(data["choices"], list):
                raise LocalModelError("Invalid response format from local model")
                
            return data["choices"][0]["message"]["content"].strip()
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error from local model: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=502,
            detail=f"Error from local model service: {error_msg}"
        ) from e
        
    except httpx.RequestError as e:
        error_msg = f"Request to local model failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=503,
            detail="Local model service is unavailable. Please ensure LM Studio is running and the API is accessible."
        ) from e
        
    except Exception as e:
        error_msg = f"Unexpected error with local model: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request with local model: {error_msg}"
        ) from e
    except Exception as e:
        print(f"Error calling local model: {str(e)}")
        raise
