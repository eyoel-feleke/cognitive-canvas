import pytest
from unittest.mock import MagicMock
from src.services.categorization_service import CategorizationService, CategoryResults



@pytest.fixture
def mock_service(monkeypatch):
    service = CategorizationService(api_key="fake-key")

    # Mock API response
    mock_response = CategoryResults(
        category="Technology",
        confidence=0.95,
        tags=["AI", "Machine Learning", "Automation"],
        summary="This content explains how AI is transforming automation."
    )

    # Mock create() method
    def mock_create(*args, **kwargs):
        return mock_response

    # Patch service.client.chat.completions.create
    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        mock_create
    )

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

    # Fake AI responses: first two calls fail, third succeeds
    call_log = []

    def mock_create(*args, **kwargs):
        call_log.append("called")
        if len(call_log) < 3:
            raise Exception("Transient API error")
        return CategoryResults(
            category="Science",
            confidence=0.88,
            tags=["Physics", "Quantum"],
            summary="A summary about quantum physics."
        )

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        mock_create
    )

    result = service.categorize_content("Quantum", "Quantum mechanics topic")

    assert len(call_log) == 3  # retried twice before success
    assert result.category == "Science"



def test_retry_fails(monkeypatch):
    service = CategorizationService(api_key="fake-key")

    def always_fail(*args, **kwargs):
        raise Exception("API outage")

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        always_fail
    )

    with pytest.raises(Exception):
        service.categorize_content("Bad", "This will fail")



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

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        mock_create
    )

    # Two identical calls
    r1 = service.categorize_content("Markets", "Finance data...")
    r2 = service.categorize_content("Markets", "Finance data...")

    # API should be called only once
    assert call_counter["count"] == 1
    assert r1 == r2



def test_tags_are_list(mock_service):
    result = mock_service.categorize_content("Title", "Content")

    assert isinstance(result.tags, list)
    assert all(isinstance(t, str) for t in result.tags)



def test_confidence_range(mock_service):
    result = mock_service.categorize_content("Something", "Text")

    assert 0.0 <= result.confidence <= 1.0
