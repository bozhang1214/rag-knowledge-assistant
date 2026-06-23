from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UploadResponse(BaseModel):
    filename: str
    chunk_count: int
    message: str

class DocumentInfo(BaseModel):
    filename: str
    chunk_count: int

class AskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class Source(BaseModel):
    filename: str
    chunk: str
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    tokens: Dict[str, int]   # {prompt_tokens, completion_tokens, total_tokens, embedding_tokens}
