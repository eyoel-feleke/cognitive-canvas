from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContentRecord(BaseModel):
    id: str
    original_content: str
    content_type: str  # url, text, code, image
    title: str
    summary: str
    category: str
    tags: List[str]
    embedding: List[float]
    timestamp: datetime
    source_url: Optional[str] = None
    metadata: dict = {}
