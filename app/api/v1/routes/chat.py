from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.mongo_service import (
    create_chat_session,
    get_chat_session,
    add_message_to_session,
    get_session_messages
)
from app.services.openai_service import get_openai_response

router = APIRouter()

def format_messages_for_openai(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert MongoDB messages to OpenAI API format, ensuring all values are strings."""
    formatted_messages = []
    for msg in messages:
        formatted_msg = {
            "role": str(msg.get("role", "user")),
            "content": str(msg.get("content", "")),
        }
        formatted_messages.append(formatted_msg)
    return formatted_messages

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    # Get or create session
    session_id = chat_request.session_id
    if not session_id:
        session_id = await create_chat_session(chat_request.user_id)
    
    # Verify session exists
    session = await get_chat_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Add user message to session
    await add_message_to_session(
        session_id=session_id,
        role="user",
        content=chat_request.message
    )
    
    # Get conversation history and format for OpenAI
    messages = await get_session_messages(session_id)
    formatted_messages = format_messages_for_openai(messages)
    
    try:
        # Generate AI response
        print(f"Sending message to OpenAI: {chat_request.message}")
        print(f"With conversation history: {formatted_messages}")
        
        ai_response = await get_openai_response(chat_request.message, formatted_messages)
        
        if not ai_response:
            raise ValueError("Received empty response from OpenAI API")
            
        print(f"Received AI response: {ai_response}")
        
        # Add AI response to session
        await add_message_to_session(
            session_id=session_id,
            role="assistant",
            content=ai_response
        )
        
        # Get updated messages
        updated_messages = await get_session_messages(session_id)
        
        return ChatResponse(
            session_id=session_id,
            messages=updated_messages
        )
        
    except Exception as e:
        error_msg = f"Error processing chat request: {str(e)}"
        print(error_msg)
        
        # Return the conversation so far, even if there was an error
        current_messages = await get_session_messages(session_id)
        
        return ChatResponse(
            session_id=session_id,
            messages=current_messages,
            error=error_msg
        )

@router.get("/{session_id}", response_model=ChatResponse)
async def get_chat(session_id: str):
    session = await get_chat_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = await get_session_messages(session_id)
    return ChatResponse(
        session_id=session_id,
        messages=messages
    )
