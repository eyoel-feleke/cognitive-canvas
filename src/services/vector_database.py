import chromadb
from chromadb.api.types import GetResult, QueryResult
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
        """  
        Store a content item in the vector database with associated metadata.  

        Args:  
            content_dict (Dict[str, Any]): A dictionary containing content details. Expected keys include  
                ``'content'``, ``'title'``, ``'tags'``, ``'summary'``, and optionally ``'source_url'``.  
            category (str): The category to associate with the content item. 
        Returns:  
            str: The unique identifier assigned to the stored content item.
        Raises:  
            VectorDatabaseError: If the storage operation fails for any reason (for example, if the  
            underlying collection add method raises an exception).
        """  
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
    
    def similarity_search(self,
                         query_texts: Optional[List[str]] = None,
                         where: Optional[Dict] = None,
                         k: int = 5) -> Dict[str, Any]:
        """
        Perform a similarity search in the vector database.
        Args:
            query_texts (Optional[List[str]], optional): List of query texts to search against. Defaults to None.
            where (Optional[Dict], optional): Metadata filter for the search. Defaults to None.
            k (int, optional): Number of top similar results to return. Defaults to 5.
        Returns:
            Dict[str, Any]: A dictionary of results as returned by the underlying collection.
        Raises:
            VectorDatabaseError: If the similarity search fails.
        """ 
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
        """
        Query documents within a specific date range.
        Args:
            start_date (datetime): The start date for the query range.
            end_date (datetime): The end date for the query range.
            k (int, optional): Maximum number of results to return. Defaults to 10.
            offset (int, optional): Number of results to skip for pagination. Defaults to 0.
        Returns:
            Dict[str, Any]: A dictionary of results as returned by the underlying collection.
        Raises:
            VectorDatabaseError: If the date range query fails.
        """
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
        """
        Retrieve documents by category.
        Args:
            category (str): The category to filter documents by.
            limit (int, optional): Maximum number of results to return. Defaults to 10.
        Returns:
            Dict[str, Any]: A dictionary of results as returned by the underlying collection.
        Raises:
            VectorDatabaseError: If fetching by category fails.
        """
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit
            )
            return results
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get by category: {str(e)}")
    
    def get_all_categories(self, batch_size: int = 1000) -> List[str]:
        """
        List all unique categories.
        Args:
            batch_size (int, optional): Number of records to fetch per batch.
                Defaults to 1000.
        Returns:
            List[str]: Sorted list of unique categories.
        Raises:
            VectorDatabaseError: If fetching categories fails.
        """
        try:
            categories: set[str] = set()
            offset = 0

            while True:
                batch = self.collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=["metadatas"]
                )

                if not batch or not batch.get("metadatas"):
                    break

                for meta in batch["metadatas"]:
                    category = meta.get("category", "")
                    if category:
                        categories.add(category)

                ids = batch.get("ids") or []
                if len(ids) < batch_size:
                    break

                offset += batch_size

            return sorted(categories)
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get categories: {str(e)}")
    
    def get_all_tags(self, batch_size: int = 1000) -> List[str]:
        """
        List all unique tags.
        Args:
            batch_size (int, optional): Number of records to fetch per batch.
                Defaults to 1000.
        Returns:
            List[str]: Sorted list of unique tags.
        Raises:
            VectorDatabaseError: If fetching tags fails.
        """
        try:
            tags: set[str] = set()
            offset = 0

            while True:
                batch = self.collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=["metadatas"]
                )

                if not batch or not batch.get("metadatas"):
                    break

                for meta in batch["metadatas"]:
                    tag_str = meta.get("tags", "")
                    if tag_str:
                        tags.update(t.strip() for t in tag_str.split(',') if t.strip())

                ids = batch.get("ids") or []
                if len(ids) < batch_size:
                    break

                offset += batch_size

            return sorted(tags)
        except Exception as e:
            raise VectorDatabaseError(f"Failed to get tags: {str(e)}")
    
    def close(self) -> None:
        """Close the underlying database client, if supported."""
        try:
            client = getattr(self, "client", None)
            if client is not None and hasattr(client, "close") and callable(getattr(client, "close", None)):
                client.close()
                # Optionally clear references after successful close
                self.collection = None
        except Exception as e:
            raise VectorDatabaseError(f"Failed to close database client: {str(e)}")



if __name__ == "__main__":

    # Example usage
    db = VectorDatabase()
    
    # for _ in range(5):
    #     content = {
    #         "content": f"This is a sample content {_} for testing.",
    #         "title": f"Sample Content {_}",
    #         "tags": ["test", "sample"],
    #         "summary": "A brief summary of the sample content.",
    #         "source_url": "http://example.com/sample"
    #     }
    #     category = f"TestCategory {_}"
    #     content_id = db.store(content, category)
    #     print(f"Stored content with ID: {content_id}")

    
    category_results = db.get_by_category("TestCategory 1", limit=2)
    print("Category Results:", category_results)

    db.close()