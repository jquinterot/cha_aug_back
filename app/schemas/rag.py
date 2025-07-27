from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum

class DocumentSourceType(str, Enum):
    FILE = "file"
    URL = "url"

class AddDocumentsRequest(BaseModel):
    file_path: Optional[str] = None
    urls: Optional[List[HttpUrl]] = None

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
