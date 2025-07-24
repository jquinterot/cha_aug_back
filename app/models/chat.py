from datetime import datetime
from pydantic import BaseModel

# For demo, using Pydantic as model; replace with SQLAlchemy for DB
class ChatMessage(BaseModel):
    id: int
    user: str
    message: str
    timestamp: datetime = datetime.utcnow()
