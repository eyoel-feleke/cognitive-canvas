import pytest
from src.services.vector_database import VectorDatabase
import tempfile
import shutil
from datetime import datetime, timedelta

@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db = VectorDatabase(persist_directory=temp_dir)
    yield db
    if hasattr(db, "close") and callable(db.close):
        db.close()
    shutil.rmtree(temp_dir)

def test_store_and_retrieve(temp_db):
    content = {
        "content": "Test content",
        "title": "Test Title",
        "tags": ["test", "demo"],
        "summary": "Test summary"
    }
    
    doc_id = temp_db.store(content, "Education")
    assert doc_id is not None
    
    results = temp_db.get_by_category("Education")
    assert len(results['ids']) > 0

def test_similarity_search(temp_db):
    temp_db.store({"content": "First", "title": "Doc1", "tags": []}, "Tech")
    temp_db.store({"content": "Second", "title": "Doc2", "tags": []}, "Tech")
    
    results = temp_db.similarity_search(query_texts=["First"], k=2)
    assert len(results['ids'][0]) == 2

def test_get_categories(temp_db):
    temp_db.store({"content": "A", "title": "A", "tags": []}, "Cat1")
    temp_db.store({"content": "B", "title": "B", "tags": []}, "Cat2")
    
    categories = temp_db.get_all_categories()
    assert "Cat1" in categories
    assert "Cat2" in categories

def test_get_tags(temp_db):
    temp_db.store({"content": "A", "title": "A", "tags": ["tag1", "tag2"]}, "Cat")
    
    tags = temp_db.get_all_tags()
    assert "tag1" in tags
    assert "tag2" in tags

def test_query_by_date_range(temp_db):
    """Test querying content by date range."""
    # Store some content
    temp_db.store({"content": "Recent content", "title": "Recent", "tags": []}, "Test")
    
    # Query for content from the last day
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    results = temp_db.query_by_date_range(start_date=start_date, end_date=end_date, k=10)
    assert results is not None
    assert 'ids' in results
    assert len(results['ids']) > 0

def test_query_by_date_range_no_results(temp_db):
    """Test querying with date range that returns no results."""
    # Query for content from a future date range
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=1)
    
    results = temp_db.query_by_date_range(start_date=start_date, end_date=end_date, k=10)
    assert results is not None
    assert 'ids' in results
    assert len(results['ids']) == 0
