"""
Model Service - Unified interface for different model backends
"""
from enum import Enum
from typing import Optional, Dict, Any
from fastapi import HTTPException
import os

from .local_model_service import get_local_model_response
from .openai_service import get_openai_response
from ..schemas.chat import ModelType

class ModelService:
    """Handles model inference across different backends"""
    
    def __init__(self):
        self.available_models = self._get_available_models()
    
    def _get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available models and their configurations"""
        return {
            "local": {
                "type": ModelType.LOCAL,
                "default_model": "llama-3.2-3b-instruct",
                "description": "Local model running in LM Studio"
            },
            "openai": {
                "type": ModelType.OPENAI,
                "default_model": "gpt-3.5-turbo",
                "description": "OpenAI API"
            },
            "rag": {
                "type": ModelType.RAG,
                "default_model": "local",  # Uses local by default but can be overridden
                "description": "Retrieval Augmented Generation"
            }
        }
    
    async def get_response(
        self,
        message: str,
        model_type: ModelType = ModelType.LOCAL,
        model_name: Optional[str] = None,
        system_message: str = "You are a helpful assistant.",
        **kwargs
    ) -> str:
        """
        Get a response from the specified model type
        
        Args:
            message: User message
            model_type: Type of model to use (local, openai, rag)
            model_name: Specific model name to use (optional)
            system_message: System message to set model behavior
            **kwargs: Additional parameters for the model
            
        Returns:
            str: Model's response
        """
        # Get model config
        model_config = self.available_models.get(model_type.value)
        if not model_config:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model type: {model_type}. Available types: {list(self.available_models.keys())}"
            )
        
        # Use provided model name or default
        model_name = model_name or model_config["default_model"]
        
        # Route to the appropriate model handler
        if model_type == ModelType.LOCAL:
            return await get_local_model_response(
                user_message=message,
                system_message=system_message,
                model=model_name,
                **kwargs
            )
            
        elif model_type == ModelType.OPENAI:
            if not os.getenv("OPENAI_API_KEY"):
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
                )
            return await get_openai_response(
                user_message=message,
                system_message=system_message,
                model=model_name,
                **kwargs
            )
            
        elif model_type == ModelType.RAG:
            # For RAG, we'll use the local model by default unless specified
            rag_model_type = ModelType.LOCAL if model_name == "local" else ModelType.OPENAI
            
            # Import here to avoid circular imports
            from .rag_service import RAGService
            
            rag = RAGService()
            return await rag.get_response(
                query=message,
                model_type=rag_model_type,
                **kwargs
            )
        
        raise HTTPException(
            status_code=400,
            detail=f"Model type not implemented: {model_type}"
        )

# Create a singleton instance
model_service = ModelService()
