import pytest
from unittest.mock import Mock
from openai import RateLimitError
from src.services.categorization_service import CategorizationService, CategoryResults


@pytest.fixture
def mock_service(monkeypatch):
    service = CategorizationService(api_key="fake-key")

    mock_response = CategoryResults(
        category="Technology",
        confidence=0.95,
        tags=["AI", "Machine Learning", "Automation"],
        summary="This content explains how AI is transforming automation."
    )

    def mock_create(*args, **kwargs):
        return mock_response

    service.client.chat.completions.create = mock_create
    return service


def test_categorize_content_success(mock_service):
    result = mock_service.categorize_content(
        "AI and Automation",
        "Artificial intelligence is impacting automation across industries..."
    )

    assert isinstance(result, CategoryResults)
    assert result.category == "Technology"
    assert 0 <= result.confidence <= 1
    assert len(result.tags) >= 1
    assert "automation" in result.summary.lower()


def test_retry_logic(monkeypatch):
    service = CategorizationService(api_key="fake-key")
    call_log = []

    def mock_create(*args, **kwargs):
        call_log.append("called")
        if len(call_log) < 3:
            # Create a mock RateLimitError properly
            mock_response = Mock()
            mock_response.status_code = 429
            raise RateLimitError("Rate limit exceeded", response=mock_response, body=None)
        return CategoryResults(
            category="Science",
            confidence=0.88,
            tags=["Physics", "Quantum"],
            summary="A summary about quantum physics."
        )

    service.client.chat.completions.create = mock_create
    
    # Use retry_delay=0 to avoid sleeping during tests
    result = service.categorize_content(
        "Quantum", 
        "Quantum mechanics topic",
        retry_delay=0
    )

    assert len(call_log) == 3
    assert result.category == "Science"


def test_retry_fails(monkeypatch):
    service = CategorizationService(api_key="fake-key")

    def always_fail(*args, **kwargs):
        mock_response = Mock()
        mock_response.status_code = 429
        raise RateLimitError("Always failing", response=mock_response, body=None)

    service.client.chat.completions.create = always_fail

    with pytest.raises(RuntimeError, match="Retry limit reached"):
        service.categorize_content("Title", "Valid content", retry_delay=0)


def test_caching(monkeypatch):
    service = CategorizationService(api_key="fake-key")
    call_counter = {"count": 0}

    def mock_create(*args, **kwargs):
        call_counter["count"] += 1
        return CategoryResults(
            category="Business",
            confidence=0.90,
            tags=["Finance", "Markets"],
            summary="Market trends analysis."
        )

    service.client.chat.completions.create = mock_create

    r1 = service.categorize_content("Markets", "Finance data...")
    r2 = service.categorize_content("Markets", "Finance data...")

    assert call_counter["count"] == 1
    assert r1 == r2


def test_caching_disabled(monkeypatch):
    service = CategorizationService(api_key="fake-key", cache_enabled=False)
    call_counter = {"count": 0}

    def mock_create(*args, **kwargs):
        call_counter["count"] += 1
        return CategoryResults(
            category="Business",
            confidence=0.90,
            tags=["Finance"],
            summary="Summary"
        )

    service.client.chat.completions.create = mock_create

    service.categorize_content("Markets", "Finance data...")
    service.categorize_content("Markets", "Finance data...")

    assert call_counter["count"] == 2  # called twice, no caching


def test_empty_content_raises_error(mock_service):
    with pytest.raises(ValueError, match="Cannot categorize empty content"):
        mock_service.categorize_content("Title", "   ")


def test_tags_are_list(mock_service):
    result = mock_service.categorize_content("Title", "Content")
    assert isinstance(result.tags, list)
    assert all(isinstance(t, str) for t in result.tags)


def test_confidence_range(mock_service):
    result = mock_service.categorize_content("Something", "Text")
    assert 0.0 <= result.confidence <= 1.0