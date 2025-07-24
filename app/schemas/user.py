from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr

class UserInDB(BaseModel):
    id: Optional[str]
    username: str
    password: str
    email: EmailStr
    createdAt: datetime
    modifiedAt: datetime

class UserResponse(BaseModel):
    id: Optional[str]
    username: str
    email: EmailStr
    createdAt: datetime
    modifiedAt: datetime

class UserLogin(BaseModel):
    login: str  # can be username or email
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
