from pydantic import BaseModel
from datetime import datetime

class ChatMessageCreate(BaseModel):
    user: str
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    user: str
    message: str
    timestamp: datetime
