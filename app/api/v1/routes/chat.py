from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ModelType
from app.services.openai_service import get_openai_response
from app.services.local_model_service import get_local_model_response
from app.services.rag_service import RAGService
from datetime import datetime
from typing import Optional, List
import re

# Create a single shared instance of RAGService
rag_service = RAGService()

router = APIRouter()

def is_knowledge_query(message: str) -> bool:
    """Determine if a message is a knowledge-base query."""
    # These patterns indicate a knowledge query
    question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'tell me', 'do you know']
    message_lower = message.lower()
    
    # Check for question marks or question words
    return ('?' in message or 
            any(word in message_lower for word in question_words) or
            message_lower.startswith(tuple(question_words)))

@router.post("/", response_model=ChatMessageResponse)
async def chat_message(
    message: ChatMessageCreate,
    model_type: ModelType = Query(
        ModelType.LOCAL,
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
                    chat_history=message.chat_history or []
                )
                
                # Debug log the RAG response
                print(f"[DEBUG] RAG Response: {rag_response}")
                
                # Extract answer and sources from RAG response
                response_text = rag_response.get("answer", "I couldn't find an answer to your question.")
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
                    for src in rag_response.get("sources", [])
                ]
                
                # If we have sources with good scores, use the RAG answer directly
                if any(src.get("metadata", {}).get("score", 0) > 0.5 for src in sources):
                    return ChatMessageResponse(
                        id=1,  # In a real app, this would come from a database
                        user=message.user,
                        message=response_text,
                        timestamp=datetime.utcnow(),
                        model_used="rag",
                        sources=sources
                    )
                
                # Debug log the final response
                print(f"[DEBUG] Final response text: {response_text}")
                print(f"[DEBUG] Sources: {sources}")
                
                return ChatMessageResponse(
                    message=response_text,
                    model_used=ModelType.RAG.value,
                    timestamp=datetime.utcnow(),
                    sources=sources
                )
                
            except Exception as e:
                # If RAG fails, fall back to regular response
                print(f"RAG query failed: {str(e)}")
        
        # If not a knowledge query or RAG didn't find relevant info, use the regular model
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
            model_used=model_type.value,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )
