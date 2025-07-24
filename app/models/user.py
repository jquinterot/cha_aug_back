from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str]
    username: str
    password: str
    email: EmailStr
    createdAt: datetime
    modifiedAt: datetime
