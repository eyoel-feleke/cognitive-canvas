from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class ContentMetadata(BaseModel):
    """Metadata for each content record, that can be used for indexing."""
    meta_id: UUID = Field(default_factory=uuid4, frozen=True)
    title: str
    author: str
    abstract: str = Field(description="A brief summary of the article's content.")
    keywords: List[str]
    date_published: datetime
    citation: Optional[str] = None

class ContentRecord(BaseModel):
    """ The main content records that will be stored here."""
    content_id: UUID = Field(default_factory=uuid4, frozen=True)
    original_content: str
    content_type: str  # url, text, code, image
    title: str
    summary: str
    category: str
    tags: List[str]
    embedding: List[float]
    timestamp: datetime
    source_url: Optional[str] = None
    metadata: ContentMetadata