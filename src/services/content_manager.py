"""
Content Manager Service - Orchestrates all other services to handle complete workflows.

This service provides high-level operations that coordinate:
- Content extraction
- Embedding generation
- Categorization
- Vector database storage
- Quiz generation

It implements retry logic, error handling, and transaction-like behavior for complex operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.services.content_extractor import ContentExtractor
from src.services.embedding_service import EmbeddingService, EmbeddingModels
from src.services.categorization_service import CategorizationService
from src.services.vector_database import VectorDatabase
from src.services.quiz_service import QuizService
from src.models.content import ContentRecord, ContentMetadata
from src.models.quiz import Quiz
from src.core.exceptions import (
    URLFormatException, 
    NullContentException, 
    InvalidContentException,
    MetadataExtractionException
)

logger = logging.getLogger(__name__)


class ContentManagerException(Exception):
    """Base exception for ContentManager operations."""
    pass


class ContentStorageException(ContentManagerException):
    """Exception raised when content storage fails."""
    pass


class ContentRetrievalException(ContentManagerException):
    """Exception raised when content retrieval fails."""
    pass


class QuizGenerationException(ContentManagerException):
    """Exception raised when quiz generation fails."""
    pass


class ContentManager:
    """
    Orchestrates all content-related operations across multiple services.
    
    This service implements the facade pattern to provide a simple interface
    for complex multi-service workflows.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        chroma_db_path: str = "./data/chroma_db",
        embedding_model: EmbeddingModels = EmbeddingModels.MINI_LM_L6_V2
    ):
        """
        Initialize the ContentManager with all required services.
        
        Args:
            openai_api_key: API key for OpenAI services
            chroma_db_path: Path to ChromaDB persistent storage
            embedding_model: Model to use for generating embeddings
        """
        self.content_extractor = ContentExtractor()
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.categorization_service = CategorizationService(api_key=openai_api_key)
        self.vector_database = VectorDatabase(persist_directory=chroma_db_path)
        self.quiz_service = QuizService(api_key=openai_api_key)
        
        logger.info("ContentManager initialized with all services")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def store_content_from_url(
        self, 
        url: str,
        custom_category: Optional[str] = None,
        custom_tags: Optional[List[str]] = None
    ) -> ContentRecord:
        """
        Complete workflow to extract, process, and store content from a URL.
        
        This method orchestrates:
        1. Content extraction from URL
        2. Embedding generation
        3. AI-powered categorization (if custom_category not provided)
        4. Storage in vector database
        
        Args:
            url: URL to extract content from
            custom_category: Optional category override
            custom_tags: Optional tags to add to content
            
        Returns:
            ContentRecord: The stored content record
            
        Raises:
            ContentStorageException: If any step in the workflow fails
        """
        logger.info(f"Starting content storage workflow for URL: {url}")
        
        try:
            # Step 1: Extract content
            logger.debug("Extracting content from URL")
            # Implement content extraction logic
            extracted_content = self.content_extractor.extract_from_url(url)
            if not isinstance(extracted_content, dict):
                raise ContentStorageException("Content extraction failed: Invalid content format")
            if extracted_content.get("error"):
                raise ContentStorageException(f"Content extraction failed: {extracted_content['error']}")
            title = extracted_content.get("title", "No Title")
            content_text = (extracted_content.get("content") or "").strip()
            if not content_text:
                raise ContentStorageException("No content extracted")

            # Step 2: Generate embedding
            logger.debug("Generating embedding for content")
            # Implement embedding generation logic
            embedding = self.embedding_service.generate_embedding(extracted_content)

            # Step 3: Categorize content
            logger.debug("Categorizing content with AI")
            # Implement categorization logic with AI and handle custom_category
            cat_result = self.categorization_service.categorize_content(extracted_content)
            if custom_category is not None:
                category = custom_category
                tags = custom_tags if custom_tags is not None else []
            else:
                category = cat_result.get('category')
                tags = custom_tags if custom_tags is not None else cat_result.get('tags', [])
            summary = cat_result.get("summary", "")
            
            # Step 4: Create metadata
            logger.debug("Creating content metadata")
            # Implement metadata extraction logic
            raw_metadata = extracted_content.get("metadata", {})
            metadata = ContentMetadata(
                title=title,
                author=raw_metadata.get("author", "Unknown"),
                abstract=raw_metadata.get("abstract", ""),
                keywords=raw_metadata.get("keywords", []),
                date_published=raw_metadata.get("date_published", datetime.now())
            )
            # Step 5: Create content record
            # Implement ContentRecord creation logic
            logger.debug("Creating content record")
            record = extracted_content.get("content", "")
            content_record = ContentRecord(
                original_content=record,
                content_type="url",
                title=title,
                category=category,
                summary=summary,
                tags=tags,
                embedding=embedding,
                timestamp=datetime.now(),
                source_url=url,
                metadata=metadata
            )
            # Step 6: Store in vector database
            logger.debug("Storing content in vector database")
            # Implement vector_database.store() method
            self.vector_database.store(content_record)
            
            logger.info(f"Successfully stored content from URL: {url}")
            # return the created content_record
            return content_record
            
        except (URLFormatException, NullContentException, InvalidContentException) as e:
            logger.error(f"Content extraction error: {str(e)}")
            raise ContentStorageException(f"Failed to extract content: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in content storage workflow: {str(e)}")
            raise ContentStorageException(f"Content storage failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def store_content_from_text(
        self,
        text: str,
        title: Optional[str] = None,
        custom_category: Optional[str] = None,
        custom_tags: Optional[List[str]] = None
    ) -> ContentRecord:
        """
        Complete workflow to process and store text content.
        
        Args:
            text: Raw text content
            title: Optional title for the content
            custom_category: Optional category override
            custom_tags: Optional tags to add to content
            
        Returns:
            ContentRecord: The stored content record
            
        Raises:
            ContentStorageException: If any step fails
        """
        logger.info("Starting content storage workflow for text input")
        
        try:
            # Step 1: Extract/clean text
            logger.debug("Extracting/cleaning text")
            # Implement text extraction logic
            extracted_text = self.content_extractor.extract_from_text(text)
            text = (extracted_text.get("content") or "").strip()
            if not text:
                raise ContentStorageException("No valid text content provided")
            title = extracted_text.get("title", "No Title")
            # Step 2: Generate embedding
            logger.debug("Generating embedding for text")
            # Implement embedding generation logic
            embedding = self.embedding_service.generate_embedding(text)
            # Step 3: Categorize
            logger.debug("Categorizing text with AI")
            # Implement categorization logic with AI and handle custom_category
            cat_result = self.categorization_service.categorize_content(extracted_text)
            if custom_category is not None:
                category = custom_category
                tags = custom_tags if custom_tags is not None else []
            else:
                category = cat_result.get('category')
                tags = custom_tags if custom_tags is not None else cat_result.get('tags', [])
            summary = extracted_text.get("summary", "")
            # Step 4: Create metadata
            logger.debug("Creating content metadata")
            # Implement metadata creation logic
            raw_metadata = extracted_text.get("metadata", {})
            metadata = ContentMetadata(
                title=title,
                author=raw_metadata.get("author", "Unknown"),
                abstract=raw_metadata.get("abstract", ""),
                keywords=raw_metadata.get("keywords", []),
                date_published=raw_metadata.get("date_published", datetime.now())
            )
            # Step 5: Create content record
            logger.debug("Creating content record")
            # Implement ContentRecord creation logic
            record = extracted_text.get("content", "")
            content_record = ContentRecord(
                original_content=record,
                content_type="text",
                text = text,
                title=title,
                category=category,
                summary=summary,
                tags=tags,
                embedding=embedding,
                timestamp=datetime.now(),
                source_url=None,
                metadata=metadata
            )
            # Step 6: Store in vector database
            logger.debug("Storing text content in vector database")
            # Implement vector_database.store() method
            self.vector_database.store(content_record)
            
            logger.info("Successfully stored text content")
            # return the created content_record
            return content_record
            
        except Exception as e:
            logger.error(f"Error in text storage workflow: {str(e)}")
            raise ContentStorageException(f"Text storage failed: {str(e)}")
    
    def store_bulk_urls(
        self,
        urls: List[str],
        custom_category: Optional[str] = None,
        custom_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store multiple URLs in bulk with parallel processing.
        
        Args:
            urls: List of URLs to process
            custom_category: Optional category for all URLs
            custom_tags: Optional tags for all URLs
            
        Returns:
            Dict containing success/failure counts and results
        """
        logger.info(f"Starting bulk storage for {len(urls)} URLs")
        
        # Implement bulk storage logic
        # - Initialize results dictionary with success/failed lists
        # - Iterate through URLs and call store_content_from_url for each
        # - Collect success and failure information
        # - Return results summary with counts and details
        results = {
            'success_count': 0,
            'failed_count': 0,
            'total': len(urls),
            'success': [],
            'failed': []
        }
        for url in urls:
            try:
                record = self.store_content_from_url(
                    url,
                    custom_category,
                    custom_tags
                )
                results['success_count']+= 1
                results['success'].append({'url': url, 'content_id': str(record.content_id)})
            except ContentStorageException as e:
                results['failed_count']+= 1
                results['failed'].append({'url': url, 'error': str(e)})

        logger.info(f"Bulk storage complete: {results['success_count']} succeeded, {results['failed_count']} failed")
        return results
    
    def retrieve_content_by_category(
        self,
        category: str,
        limit: Optional[int] = None
    ) -> List[ContentRecord]:
        """
        Retrieve all content records for a specific category.
        
        Args:
            category: Category to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of ContentRecord objects
            
        Raises:
            ContentRetrievalException: If retrieval fails
        """
        logger.info(f"Retrieving content for category: {category}")
        
        try:
            # Implement vector_database.get_by_category() method
            result = self.vector_database.get_by_category(category, limit)

            content_records = []
            for i in range(len(result['ids'])):
                
                content_metadata = ContentMetadata(
                    title=result['metadatas'][i]['title'],
                    author=result['metadatas'][i].get('author', 'Unknown'),
                    abstract=result['metadatas'][i].get('abstract', ''),
                    keywords=result['metadatas'][i].get('keywords', []),
                    date_published=datetime.fromtimestamp(result['metadatas'][i].get('date_published', datetime.now().timestamp()))
                )

                content_record = ContentRecord(
                    content_id=result['ids'][i],
                    original_content=result['documents'][i],
                    content_type=result['metadatas'][i].get('content_type', 'unknown'),
                    title=result['metadatas'][i]['title'],
                    summary=result['metadatas'][i].get('summary', ''),
                    category=category,
                    tags=result['metadatas'][i].get('tags', []),
                    embedding=result['embeddings'][i],
                    timestamp=datetime.fromtimestamp(result['metadatas'][i].get('timestamp', datetime.now().timestamp())),
                    source_url=result['metadatas'][i].get('url', None),
                    metadata=content_metadata
                )
                content_records.append(content_record)
            return content_records
            # raise NotImplementedError("Vector database get_by_category not yet implemented")
        except Exception as e:
            logger.error(f"Failed to retrieve content by category: {str(e)}")
            raise ContentRetrievalException(f"Content retrieval failed: {str(e)}")
    
    def retrieve_content_by_date_range(
        self,
        start_date: datetime,   
        end_date: datetime,
        category: Optional[str] = None
    ) -> List[ContentRecord]:
        """
        Retrieve content records within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            category: Optional category filter
            
        Returns:
            List of ContentRecord objects
            
        Raises:
            ContentRetrievalException: If retrieval fails
        """
        logger.info(f"Retrieving content from {start_date} to {end_date}")
        
        try:
            # Implement vector_database.query_by_date_range() method
          return self.vector_database.query_by_date_range(start_date, end_date, category)
           # raise NotImplementedError("Vector database query_by_date_range not yet implemented")
        except Exception as e:
            logger.error(f"Failed to retrieve content by date range: {str(e)}")
            raise ContentRetrievalException(f"Content retrieval failed: {str(e)}")
    
    def similarity_search(
        self,
        query_text: str,
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search on stored content.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            category_filter: Optional category to filter results
            
        Returns:
            List of content records with similarity scores
            
        Raises:
            ContentRetrievalException: If search fails
        """
        logger.info(f"Performing similarity search for: {query_text[:50]}...")
        
        try:
            # Step 1: Generate embedding for query
            logger.debug("Generating embedding for query text")
            #: Implement query embedding generation
            # query_embedding = self.embedding_service.generate_embedding(query_text)
            # Step 2: Perform similarity search in vector database
            logger.debug("Searching vector database")
            #: Implement vector_database.similarity_search() method
            
            results = self.vector_database.similarity_search(
                query_texts=query_text, k=top_k, category=category_filter
            )
            return results
            # raise NotImplementedError("Vector database similarity_search not yet implemented")
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise ContentRetrievalException(f"Similarity search failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def generate_quiz_from_category(
        self,
        category: str,
        num_questions: int = 5,
        difficulty: str = "mixed",
        quiz_type: str = "mcq"
    ) -> Quiz:
        """
        Generate a quiz from content in a specific category.
        
        This method:
        1. Retrieves content from the category
        2. Extracts summaries
        3. Generates quiz using AI
        
        Args:
            category: Category to generate quiz from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard, mixed)
            quiz_type: Type of quiz (mcq, fill_in_blank, true_false)
            
        Returns:
            Quiz object with generated questions
            
        Raises:
            QuizGenerationException: If quiz generation fails
        """
        logger.info(f"Generating {quiz_type} quiz for category: {category}")
        
        try:
            # Step 1: Retrieve content from category
            logger.debug("Retrieving content from category")
            # Implement content retrieval by category
            content_records = self.retrieve_content_by_category(category)
            if not content_records:
                raise QuizGenerationException(f"No content found for category: {category}")
            
            # Step 2: Extract summaries from content
            logger.debug("Extracting summaries from content")
            # Extract summaries from retrieved content records
            content_summaries = [record.summary for record in content_records if record.summary]
            if not content_summaries:
                raise QuizGenerationException("No content found")
            # Step 3: Generate quiz based on quiz_type
            logger.debug(f"Generating {quiz_type} quiz")
            # Implement quiz generation logic
            # - Handle mcq, fill_in_blank, and true_false quiz types
            # - Call appropriate quiz_service method
            # - Validate quiz_type and raise exception for unsupported types
            if quiz_type == "mcq":
                quiz = self.quiz_service.generate_mcq_quiz(
                    content_summaries, category, num_questions, difficulty
                )
            elif quiz_type == "fill_in_blank":
                quiz = self.quiz_service.generate_fill_in_blank_quiz(
                    content_summaries, category, num_questions, difficulty
                )
            elif quiz_type == "true_false":
                quiz = self.quiz_service.generate_true_false_quiz(
                    content_summaries, category, num_questions, difficulty
                )
            else:
                raise QuizGenerationException(f"Unsupported quiz type: {quiz_type}")
            logger.info(f"Successfully generated quiz")
            # return the generated quiz
            return quiz
            
        except ContentRetrievalException as e:
            logger.error(f"Failed to retrieve content for quiz: {str(e)}")
            raise QuizGenerationException(f"Quiz generation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise QuizGenerationException(f"Quiz generation failed: {str(e)}")
    
    def generate_quiz_from_content_ids(
        self,
        content_ids: List[str],
        num_questions: int = 5,
        difficulty: str = "mixed",
        quiz_type: str = "mcq"
    ) -> Quiz:
        """
        Generate a quiz from specific content IDs.
        
        Args:
            content_ids: List of content IDs to generate quiz from
            num_questions: Number of questions to generate
            difficulty: Difficulty level
            quiz_type: Type of quiz
            
        Returns:
            Quiz object
            
        Raises:
            QuizGenerationException: If generation fails
        """
        logger.info(f"Generating quiz from {len(content_ids)} content items")
        
        try:
            #content_ids = self.vector_database.get_by_ids(content_ids)
            #if not content_ids:
            raise QuizGenerationException("No content IDs provided")
            # Implement vector_database.get_by_ids() method
            
        except Exception as e:
            logger.error(f"Error generating quiz from content IDs: {str(e)}")
            raise QuizGenerationException(f"Quiz generation failed: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored content.
        
        Returns:
            Dictionary containing various statistics
        """
        logger.info("Retrieving content statistics")
        
        try:
            # Implement statistics gathering from vector database
            # - Get total content count
            # - Get content grouped by categories
            # - Get content grouped by types
            # - Get date range of stored content
            stats = self.vector_database.get_statistics()
            stats = {
                'total_content': 0,
                'categories': {},
                'content_types': {},
                'date_range': None
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
