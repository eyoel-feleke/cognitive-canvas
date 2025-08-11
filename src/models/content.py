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

# Example of proper model usage and serialization
if __name__ == "__main__":
    # Create metadata instance
    metadata = ContentMetadata(
        title="Sample Metadata",
        author="Author Name",
        abstract="This is a synopsis of the sample metadata.",  
        keywords=["keyword1", "keyword2"],
        date_published=datetime.now()
    )
    
    # Create content record instance
    content_record = ContentRecord(
        original_content="This is a sample content.",
        content_type="text",
        title="Sample Content",
        summary="This is a summary of the sample content.",
        category="General",
        tags=["sample", "content"],
        embedding=[0.1, 0.2, 0.3],
        timestamp=datetime.now(),
        metadata=metadata
    )
    
    # Test serialization
    metadata_json = metadata.model_dump_json()
    content_json = content_record.model_dump_json()
    print("Metadata JSON:", metadata_json)
    print("Content JSON:", content_json)
    # Test deserialization
    deserialized_metadata = ContentMetadata.model_validate_json(metadata_json)
    deserialized_content = ContentRecord.model_validate_json(content_json)
    print("Deserialized Metadata:", deserialized_metadata)
    print("Deserialized Content:", deserialized_content)