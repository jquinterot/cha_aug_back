from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ModelType(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"
    RAG = "rag"

class ChatMessageCreate(BaseModel):
    user: str
    message: str
    model_type: Optional[ModelType] = ModelType.OPENAI  # Changed default to OPENAI
    chat_history: Optional[list] = []

class SourceDocument(BaseModel):
    content: str
    source: str
    metadata: Optional[dict] = None

class ChatMessageResponse(BaseModel):
    id: int
    user: str
    message: str
    timestamp: datetime
    model_used: str
    sources: list[SourceDocument] = []
