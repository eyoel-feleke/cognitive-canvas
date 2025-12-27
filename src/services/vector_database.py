import chromadb
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Optional, Any

class VectorDatabaseError(Exception):
    """Base exception for vector database operations."""
    pass

class VectorDatabase:
    def __init__(self, persist_directory="./data/chroma_db"):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="content_embeddings",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            raise VectorDatabaseError(f"Failed to initialize database: {str(e)}")
    
    def store(self, content_dict: Dict[str, Any], category: str) -> str:
        """Store content with embedding and metadata."""
        try:
            doc_id = str(uuid4())
            self.collection.add(
                # embeddings=[embedding],
                documents=[content_dict.get('content', content_dict.get('original_content', ''))],
                metadatas=[{
                    "title": content_dict.get('title', ''),
                    "category": category,
                    "timestamp": datetime.now().timestamp(),
                    "url": content_dict.get('source_url', ''),
                    "tags": ','.join(content_dict.get('tags', [])),
                    "summary": content_dict.get('summary', '')
                }],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            raise VectorDatabaseError(f"Failed to store content: {str(e)}")
    
    def similarity_search(self, k: int = 5, 
                        query_texts: Optional[List[str]] = None,
                         where: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform semantic search with optional metadata filtering."""
        try:
            results = self.collection.query(
                # query_embeddings=[query_embedding],
                query_texts=query_texts,
                n_results=k,
                where=where,
                include=["metadatas", "documents", "embeddings"]
            )
            return results
        except Exception as e:
            raise VectorDatabaseError(f"Failed to perform similarity search: {str(e)}")
    
    def query_by_date_range(self, 
                            start_date: datetime, 
                            end_date: datetime, 
                            k: int = 10,
                            offset: int = 0) -> Dict[str, Any]:
        """Filter content by date range."""
        try:
            results = self.collection.get(
                # query_texts=[""],
                limit=k,
                offset=offset,
                where={
                    "$and": [
                        {"timestamp": {"$gte": start_date.timestamp()}},
                        {"timestamp": {"$lte": end_date.timestamp()}}
                    ]
                },
                include=["metadatas", "documents", "embeddings"]
            )
            return results
        except Exception as e:
            raise VectorDatabaseError(f"Failed to query by date range: {str(e)}")
    
    def get_by_category(self, category: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve content by category."""
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit
            )
            return results
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get by category: {str(e)}")
    
    def get_all_categories(self) -> List[str]:
        """List all unique categories."""
        try:
            all_data = self.collection.get()
            if not all_data or not all_data.get('metadatas'):
                return []
            categories = set(meta.get('category', '') for meta in all_data['metadatas'])
            return sorted([c for c in categories if c])
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get categories: {str(e)}")
    
    def get_all_tags(self) -> List[str]:
        """List all unique tags."""
        try:
            all_data = self.collection.get()
            if not all_data or not all_data.get('metadatas'):
                return []
            tags = set()
            for meta in all_data['metadatas']:
                tag_str = meta.get('tags', '')
                if tag_str:
                    tags.update(tag_str.split(','))
            return sorted(list(tags))
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get tags: {str(e)}")
