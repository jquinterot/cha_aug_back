from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ModelType(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"

class ChatMessageCreate(BaseModel):
    user: str
    message: str
    model_type: Optional[ModelType] = ModelType.LOCAL

class ChatMessageResponse(BaseModel):
    id: int
    user: str
    message: str
    timestamp: datetime
    model_used: str
