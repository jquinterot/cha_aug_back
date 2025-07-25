from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Literal, Optional
from bson import ObjectId
from pydantic import BaseConfig

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

class BaseMongoModel(BaseModel):
    class Config(BaseConfig):
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ChatMessage(BaseMongoModel):
    role: Literal['user', 'assistant', 'system']
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseMongoModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = []

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    error: Optional[str] = None
