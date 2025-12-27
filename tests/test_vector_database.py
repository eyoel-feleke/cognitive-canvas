import pytest
from src.services.vector_database import VectorDatabase
from datetime import datetime
import tempfile
import shutil

@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db = VectorDatabase(persist_directory=temp_dir)
    yield db
    shutil.rmtree(temp_dir)

def test_store_and_retrieve(temp_db):
    embedding = [0.1, 0.2, 0.3]
    content = {
        "content": "Test content",
        "title": "Test Title",
        "tags": ["test", "demo"],
        "summary": "Test summary"
    }
    
    doc_id = temp_db.store( content, "Education")
    assert doc_id is not None
    
    results = temp_db.get_by_category("Education")
    assert len(results['ids']) > 0

def test_similarity_search(temp_db):
    embedding1 = [0.1, 0.2, 0.3]
    embedding2 = [0.15, 0.25, 0.35]
    
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
