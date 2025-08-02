from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ModelType
from app.services.openai_service import get_openai_response
from app.services.rag_service import RAGService
from datetime import datetime
from typing import Optional, List
import re

# Create a single shared instance of RAGService
rag_service = RAGService()

router = APIRouter()

def is_knowledge_query(message: str) -> bool:
    """Determine if a message is a knowledge-base query."""
    if not message or not message.strip():
        return False
        
    message_lower = message.lower().strip()
    
    # Skip common greetings and simple phrases
    simple_phrases = [
        'hello', 'hi', 'hey', 'greetings',
        'thanks', 'thank you',
        'ok', 'okay', 'got it'
    ]
    
    if any(phrase in message_lower.split() for phrase in simple_phrases):
        return False
    
    # These patterns indicate a knowledge query
    question_words = [
        'what', 'who', 'when', 'where', 'why', 'how', 'which', 
        'tell me', 'do you know', 'can you tell me', 'what is', 'who is'
    ]
    
    # Check for question marks or question words at start of message
    if ('?' in message or 
        any(message_lower.startswith(word) for word in question_words)):
        return True
        
    # Check for question words anywhere in the message
    if any(f' {word} ' in f' {message_lower} ' for word in question_words):
        return True
        
    # If it's a very short message (1-2 words), it's likely a lookup
    if len(message.split()) <= 2:
        return True
        
    return False

@router.post("", response_model=ChatMessageResponse, include_in_schema=False)
@router.post("/", response_model=ChatMessageResponse)
async def chat_message(
    message: ChatMessageCreate,
    model_type: ModelType = Query(
        ModelType.OPENAI,
        description="The model to use for generating responses"
    ),
    use_rag: bool = Query(
        True,
        description="Whether to use the RAG system for knowledge queries"
    )
):
    """
    Process a chat message and return a response.
    
    Args:
        message: The incoming chat message
        model_type: The model to use (local or openai)
        use_rag: Whether to use RAG for knowledge queries
    """
    try:
        response_text = ""
        sources = []
        
        # Check if this is a knowledge query and RAG should be used
        if use_rag and is_knowledge_query(message.message):
            try:
                # Get response from RAG with sources
                print(f"\n[DEBUG] Sending query to RAG: {message.message}")
                rag_response = await rag_service.generate_response(
                    query=message.message,
                    chat_history=message.chat_history or [],
                    score_threshold=0.0  # Include all documents, even with low scores
                )
                
                # Debug log the RAG response
                print(f"[DEBUG] RAG Response: {rag_response}")
                
                # Extract answer and sources from RAG response
                response_text = rag_response.answer if rag_response.answer else "I couldn't find an answer to your question."
                
                # Only use RAG response if we have valid sources with content
                has_relevant_sources = any(
                    src.get('content') and len(src.get('content', '').strip()) > 10 
                    for src in rag_response.sources
                )
                
                if has_relevant_sources:
                    sources = [
                        {
                            "content": src.get("content", ""),
                            "source": src.get("source", "unknown"),
                            "metadata": {
                                "score": src.get("score", 0.0),
                                **{k: v for k, v in src.get("metadata", {}).items() 
                                  if k not in ["source", "score"]}
                            }
                        }
                        for src in rag_response.sources
                    ]
                    
                    print(f"[DEBUG] Using RAG response with {len(sources)} sources")
                    return ChatMessageResponse(
                        id=1,
                        user=message.user,
                        message=response_text,
                        timestamp=datetime.utcnow(),
                        model_used=ModelType.RAG.value,
                        sources=sources
                    )
                else:
                    print("[DEBUG] No relevant sources found, falling back to base model")
                
            except Exception as e:
                print(f"[ERROR] RAG query failed: {str(e)}")
        
        # Always use OpenAI for the base model response
        print(f"[DEBUG] Using OpenAI model for response")
        response_text = await get_openai_response(message.message)
            
        return ChatMessageResponse(
            id=1,
            user=message.user,
            message=response_text,
            timestamp=datetime.utcnow(),
            model_used=model_type.value,
            sources=sources  # Will be empty for base model responses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )
