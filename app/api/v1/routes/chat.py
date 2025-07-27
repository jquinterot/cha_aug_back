from fastapi import APIRouter, HTTPException, Query
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ModelType
from app.services.openai_service import get_openai_response
from app.services.local_model_service import get_local_model_response
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def chat_message(
    message: ChatMessageCreate,
    model_type: ModelType = Query(
        ModelType.LOCAL,
        description="The model to use for generating responses"
    )
):
    """
    Process a chat message and return a response.
    
    Args:
        message: The incoming chat message
        model_type: The model to use (local or openai)
    """
    try:
        if model_type == ModelType.OPENAI:
            response_text = await get_openai_response(message.message)
        else:  # LOCAL
            response_text = await get_local_model_response(
                user_message=message.message,
                model="llama-3.2-3b-instruct"  # Default model, can be made configurable
            )
            
        return ChatMessageResponse(
            id=1,  # In a real app, this would come from a database
            user=message.user,
            message=response_text,
            timestamp=datetime.utcnow(),
            model_used=model_type.value
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )
