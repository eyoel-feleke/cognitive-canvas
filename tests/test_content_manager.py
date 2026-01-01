"""
Unit tests for ContentManager service.

Tests the orchestration of multiple services and workflow management.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from uuid import uuid4

from src.services.content_manager import (
    ContentManager,
    ContentStorageException,
    ContentRetrievalException,
    QuizGenerationException
)
from src.models.content import ContentRecord, ContentMetadata
from src.models.quiz import Quiz, QuizQuestion
from src.services.embedding_service import EmbeddingModels


class TestContentManagerInitialization:
    """Test ContentManager initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        manager = ContentManager(openai_api_key="test-key")
        
        assert manager.content_extractor is not None
        assert manager.embedding_service is not None
        assert manager.categorization_service is not None
        assert manager.vector_database is not None
        assert manager.quiz_service is not None
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        with patch('src.services.content_manager.VectorDatabase'):
            manager = ContentManager(
                openai_api_key="test-key",
                chroma_db_path="/custom/path",
                embedding_model=EmbeddingModels.ALL_MPNET_BASE_V2
            )
            
            assert manager.content_extractor is not None
            assert manager.embedding_service is not None


class TestStoreContentFromURL:
    """Test URL content storage workflow."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager with mocked services."""
        with patch('src.services.content_manager.ContentExtractor') as mock_extractor, \
             patch('src.services.content_manager.EmbeddingService') as mock_embedding, \
             patch('src.services.content_manager.CategorizationService') as mock_categorization, \
             patch('src.services.content_manager.VectorDatabase') as mock_db, \
             patch('src.services.content_manager.QuizService') as mock_quiz:
            
            manager = ContentManager(openai_api_key="test-key")
            
            # Setup mock responses
            manager.content_extractor.extract_from_url.return_value = {
                'title': 'Test Article',
                'content': 'This is test content for the article.',
                'url': 'https://example.com/article',
                'domain': 'example.com',
                'metadata': {'author': 'Test Author'}
            }
            
            manager.embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
            
            manager.categorization_service.categorize.return_value = {
                'category': 'Technology',
                'summary': 'This is a technology article'
            }
            
            yield manager
    
    def test_store_content_from_url_success(self, manager):
        """Test successful URL content storage."""
        url = "https://example.com/article"
        
        result = manager.store_content_from_url(url)
        
        # Verify all services were called
        manager.content_extractor.extract_from_url.assert_called_once_with(url)
        manager.embedding_service.generate_embedding.assert_called_once()
        manager.categorization_service.categorize.assert_called_once()
        
        # Verify result
        assert isinstance(result, ContentRecord)
        assert result.content_type == "url"
        assert result.source_url == url
        assert result.title == "Test Article"
        assert result.category == "Technology"
    
    def test_store_content_with_custom_category(self, manager):
        """Test storing content with custom category."""
        url = "https://example.com/article"
        custom_category = "Science"
        
        result = manager.store_content_from_url(url, custom_category=custom_category)
        
        # Categorization service should not be called
        manager.categorization_service.categorize.assert_not_called()
        assert result.category == custom_category
    
    def test_store_content_with_custom_tags(self, manager):
        """Test storing content with custom tags."""
        url = "https://example.com/article"
        custom_tags = ["python", "tutorial", "testing"]
        
        result = manager.store_content_from_url(url, custom_tags=custom_tags)
        
        assert result.tags == custom_tags
    
    def test_store_content_extraction_error(self, manager):
        """Test handling of content extraction errors."""
        manager.content_extractor.extract_from_url.return_value = {
            'error': 'Request timed out'
        }
        
        with pytest.raises(ContentStorageException) as exc_info:
            manager.store_content_from_url("https://example.com/bad")
        
        assert "Content extraction failed" in str(exc_info.value)
    
    def test_store_content_empty_content(self, manager):
        """Test handling of empty content."""
        manager.content_extractor.extract_from_url.return_value = {
            'title': 'Empty Article',
            'content': '',
            'url': 'https://example.com/empty'
        }
        
        with pytest.raises(ContentStorageException) as exc_info:
            manager.store_content_from_url("https://example.com/empty")
        
        assert "No content extracted" in str(exc_info.value)
    
    def test_store_content_embedding_error(self, manager):
        """Test handling of embedding generation errors."""
        manager.embedding_service.generate_embedding.side_effect = Exception("Embedding failed")
        
        with pytest.raises(ContentStorageException) as exc_info:
            manager.store_content_from_url("https://example.com/article")
        
        assert "Content storage failed" in str(exc_info.value)


class TestStoreContentFromText:
    """Test text content storage workflow."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager with mocked services."""
        with patch('src.services.content_manager.ContentExtractor') as mock_extractor, \
             patch('src.services.content_manager.EmbeddingService') as mock_embedding, \
             patch('src.services.content_manager.CategorizationService') as mock_categorization, \
             patch('src.services.content_manager.VectorDatabase') as mock_db, \
             patch('src.services.content_manager.QuizService') as mock_quiz:
            
            manager = ContentManager(openai_api_key="test-key")
            
            manager.content_extractor.extract_from_text.return_value = {
                'title': 'Extracted text',
                'content': 'This is the cleaned text content.',
                'metadata': {'type': 'text'}
            }
            
            manager.embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
            
            manager.categorization_service.categorize.return_value = {
                'category': 'Notes',
                'summary': 'User notes'
            }
            
            yield manager
    
    def test_store_text_success(self, manager):
        """Test successful text storage."""
        text = "This is some text content to store."
        title = "My Notes"
        
        result = manager.store_content_from_text(text, title=title)
        
        assert isinstance(result, ContentRecord)
        assert result.content_type == "text"
        assert result.title == title
        assert result.source_url is None
    
    def test_store_text_without_title(self, manager):
        """Test storing text without custom title."""
        text = "This is some text content."
        
        result = manager.store_content_from_text(text)
        
        assert result.title == "Text Content"
    
    def test_store_text_with_custom_category(self, manager):
        """Test storing text with custom category."""
        text = "Custom categorized text"
        custom_category = "Personal"
        
        result = manager.store_content_from_text(text, custom_category=custom_category)
        
        manager.categorization_service.categorize.assert_not_called()
        assert result.category == custom_category


class TestBulkOperations:
    """Test bulk content storage operations."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager with mocked services."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            manager = ContentManager(openai_api_key="test-key")
            yield manager
    
    def test_store_bulk_urls_all_success(self, manager):
        """Test bulk URL storage with all successes."""
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3"
        ]
        
        with patch.object(manager, 'store_content_from_url') as mock_store:
            mock_record = Mock(spec=ContentRecord)
            mock_record.content_id = uuid4()
            mock_store.return_value = mock_record
            
            results = manager.store_bulk_urls(urls)
        
        assert results['total'] == 3
        assert results['success_count'] == 3
        assert results['failed_count'] == 0
        assert len(results['success']) == 3
        assert len(results['failed']) == 0
    
    def test_store_bulk_urls_partial_failure(self, manager):
        """Test bulk URL storage with partial failures."""
        urls = [
            "https://example.com/1",
            "https://example.com/bad",
            "https://example.com/3"
        ]
        
        with patch.object(manager, 'store_content_from_url') as mock_store:
            mock_record = Mock(spec=ContentRecord)
            mock_record.content_id = uuid4()
            
            def side_effect(url, *args, **kwargs):
                if 'bad' in url:
                    raise ContentStorageException("Failed to store")
                return mock_record
            
            mock_store.side_effect = side_effect
            
            results = manager.store_bulk_urls(urls)
        
        assert results['total'] == 3
        assert results['success_count'] == 2
        assert results['failed_count'] == 1
        assert len(results['success']) == 2
        assert len(results['failed']) == 1
    
    def test_store_bulk_urls_with_category_and_tags(self, manager):
        """Test bulk URL storage with category and tags."""
        urls = ["https://example.com/1", "https://example.com/2"]
        custom_category = "Technology"
        custom_tags = ["python", "ai"]
        
        with patch.object(manager, 'store_content_from_url') as mock_store:
            mock_record = Mock(spec=ContentRecord)
            mock_record.content_id = uuid4()
            mock_store.return_value = mock_record
            
            manager.store_bulk_urls(urls, custom_category, custom_tags)
            
            # Verify category and tags passed to each call (as positional args after url)
            assert mock_store.call_count == 2
            for call_obj in mock_store.call_args_list:
                args, kwargs = call_obj
                # Args are: (url, custom_category, custom_tags)
                assert len(args) == 3
                assert args[1] == custom_category
                assert args[2] == custom_tags


class TestContentRetrieval:
    """Test content retrieval workflows."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager with mocked services."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            manager = ContentManager(openai_api_key="test-key")
            yield manager
    
    def test_retrieve_by_category_not_implemented(self, manager):
        """Test that retrieve_by_category raises NotImplementedError."""
        with pytest.raises(ContentRetrievalException):
            manager.retrieve_content_by_category("Technology")
    
    def test_retrieve_by_date_range_not_implemented(self, manager):
        """Test that retrieve_by_date_range raises NotImplementedError."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 12, 31)
        
        with pytest.raises(ContentRetrievalException):
            manager.retrieve_content_by_date_range(start, end)
    
    def test_similarity_search_not_implemented(self, manager):
        """Test that similarity_search raises NotImplementedError."""
        with pytest.raises(ContentRetrievalException):
            manager.similarity_search("test query")


class TestQuizGeneration:
    """Test quiz generation workflows."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager with mocked services."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            manager = ContentManager(openai_api_key="test-key")
            
            # Mock content records
            mock_records = [
                Mock(spec=ContentRecord, summary="Summary 1"),
                Mock(spec=ContentRecord, summary="Summary 2")
            ]
            
            # Mock quiz
            mock_quiz = Mock(spec=Quiz)
            mock_quiz.questions = [
                Mock(spec=QuizQuestion),
                Mock(spec=QuizQuestion)
            ]
            
            manager.quiz_service.generate_mcq_quiz.return_value = mock_quiz
            manager.quiz_service.generate_fill_in_blank_quiz.return_value = mock_quiz
            manager.quiz_service.generate_true_false_quiz.return_value = mock_quiz
            
            yield manager, mock_records, mock_quiz
    
    def test_generate_quiz_from_category_mcq(self, manager):
        """Test MCQ quiz generation from category."""
        mgr, mock_records, mock_quiz = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=mock_records):
            result = mgr.generate_quiz_from_category("Technology", quiz_type="mcq")
        
        assert result == mock_quiz
        mgr.quiz_service.generate_mcq_quiz.assert_called_once()
    
    def test_generate_quiz_from_category_fill_in_blank(self, manager):
        """Test fill-in-blank quiz generation."""
        mgr, mock_records, mock_quiz = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=mock_records):
            result = mgr.generate_quiz_from_category("Science", quiz_type="fill_in_blank")
        
        mgr.quiz_service.generate_fill_in_blank_quiz.assert_called_once()
    
    def test_generate_quiz_from_category_true_false(self, manager):
        """Test true/false quiz generation."""
        mgr, mock_records, mock_quiz = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=mock_records):
            result = mgr.generate_quiz_from_category("History", quiz_type="true_false")
        
        mgr.quiz_service.generate_true_false_quiz.assert_called_once()
    
    def test_generate_quiz_no_content(self, manager):
        """Test quiz generation with no content available."""
        mgr, _, _ = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=[]):
            with pytest.raises(QuizGenerationException) as exc_info:
                mgr.generate_quiz_from_category("EmptyCategory")
            
            assert "No content found" in str(exc_info.value)
    
    def test_generate_quiz_invalid_type(self, manager):
        """Test quiz generation with invalid quiz type."""
        mgr, mock_records, _ = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=mock_records):
            with pytest.raises(QuizGenerationException) as exc_info:
                mgr.generate_quiz_from_category("Technology", quiz_type="invalid")
            
            assert "Unsupported quiz type" in str(exc_info.value)
    
    def test_generate_quiz_with_custom_params(self, manager):
        """Test quiz generation with custom parameters."""
        mgr, mock_records, mock_quiz = manager
        
        with patch.object(mgr, 'retrieve_content_by_category', return_value=mock_records):
            result = mgr.generate_quiz_from_category(
                "Technology",
                num_questions=10,
                difficulty="hard",
                quiz_type="mcq"
            )
        
        # Verify parameters passed to quiz service
        call_args = mgr.quiz_service.generate_mcq_quiz.call_args
        assert call_args[0][2] == 10  # num_questions
        assert call_args[0][3] == "hard"  # difficulty
    
    def test_generate_quiz_from_content_ids_not_implemented(self, manager):
        """Test that generate_quiz_from_content_ids is not yet implemented."""
        mgr, _, _ = manager
        
        with pytest.raises(QuizGenerationException):
            mgr.generate_quiz_from_content_ids(["id1", "id2"])


class TestStatistics:
    """Test statistics gathering."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            yield ContentManager(openai_api_key="test-key")
    
    def test_get_statistics(self, manager):
        """Test statistics retrieval."""
        stats = manager.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_content' in stats
        assert 'categories' in stats
        assert 'content_types' in stats


class TestErrorHandlingAndRetry:
    """Test error handling and retry logic."""
    
    @pytest.fixture
    def manager(self):
        """Create ContentManager."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            manager = ContentManager(openai_api_key="test-key")
            
            manager.content_extractor.extract_from_url.return_value = {
                'title': 'Test',
                'content': 'Content',
                'url': 'https://example.com'
            }
            manager.embedding_service.generate_embedding.return_value = [0.1, 0.2]
            manager.categorization_service.categorize.return_value = {
                'category': 'Test',
                'summary': 'Summary'
            }
            
            yield manager
    
    def test_error_handling_wraps_exceptions(self, manager):
        """Test that exceptions are properly wrapped in ContentStorageException."""
        manager.content_extractor.extract_from_url.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ContentStorageException) as exc_info:
            manager.store_content_from_url("https://example.com")
        
        assert "Content storage failed" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)


@pytest.mark.integration
class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""
    @pytest.fixture
    def manager(self):
        """Create ContentManager."""
        with patch('src.services.content_manager.ContentExtractor'), \
             patch('src.services.content_manager.EmbeddingService'), \
             patch('src.services.content_manager.CategorizationService'), \
             patch('src.services.content_manager.VectorDatabase'), \
             patch('src.services.content_manager.QuizService'):
            
            manager = ContentManager(openai_api_key="test-key")
            
            manager.content_extractor.extract_from_url.return_value = {
                'title': 'Integration Test',
                'content': 'Integration test content.',
                'url': 'https://example.com'
            }
            manager.embedding_service.generate_embedding.return_value = [0.1, 0.2]
            manager.categorization_service.categorize.return_value = {
                'category': 'Test',
                'summary': 'Summary'
            }
            
            yield manager
    
    @pytest.fixture
    def contentRecord(self):
        with patch('src.models.content.ContentRecord') as cr:
            contentRecord = cr(
                original_content="Integration test content.",
                content_type="url",
                title="Integration Test",
                summary="Summary",
                category="Test",
                tags=[],
                embedding=[0.1, 0.2],
                timestamp=datetime.now(),
                metadata=ContentMetadata(
                    title="Integration Test",
                    author="Tester",
                    abstract="Abstract",
                    keywords=["integration", "test"],
                    date_published=datetime.now()
                ),
                source_url="https://example.com"
            )
            yield contentRecord

    
    def test_end_to_end_url_storage_workflow(self, manager, contentRecord):
        """Test complete URL storage workflow with real services."""
        manager_recod = manager.store_content_from_url("https://example.com")
        assert isinstance(manager_recod, ContentRecord)
        assert manager_recod.title == contentRecord.title
        assert manager_recod.source_url == contentRecord.source_url
        assert manager_recod.category == contentRecord.category
    
    def test_end_to_end_quiz_generation_workflow(self, manager):
        """Test complete quiz generation workflow."""
        # This would be implemented when retrieval methods are ready
        manager.generate_quiz_from_category("Test", quiz_type="mcq")
