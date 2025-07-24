from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.openai_service import get_openai_response
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def chat_message(message: ChatMessageCreate):
    response_text = await get_openai_response(message.message)
    return ChatMessageResponse(
        id=1,
        user=message.user,
        message=response_text,
        timestamp=datetime.utcnow()
    )
