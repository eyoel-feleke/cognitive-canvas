import pytest
from bs4 import BeautifulSoup
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError
from src.services.content_extractor import ContentExtractor

@pytest.fixture
def extractor():
    return ContentExtractor()

@pytest.fixture
def mock_html():
    return """
    <html>
        <head>
            <title>Test Article</title>
            <meta name="author" content="John Doe">
            <meta property="article:published_time" content="2024-01-01">
        </head>
        <body>
            <article>
                <h1>Main Heading</h1>
                <p>This is the main content.</p>
                <script>alert('test');</script>
                <style>.test { color: red; }</style>
            </article>
        </body>
    </html>
    """

@pytest.fixture
def sample_text():
    return "  This is some sample   text  with extra   spaces.  "

@pytest.fixture
def sample_code():
    return """
    def test_function():
        # Test comment
        print("hello")
        
    """

def test_extract_from_url_success(extractor, requests_mock, mock_html):
    url = "http://example.com/article"
    requests_mock.get(url, text=mock_html)
    
    result = extractor.extract_from_url(url)
    
    assert result["title"] == "Test Article", "Title was not extracted correctly"
    assert "Main Heading" in result["content"], "Main heading content not found in extracted text"
    assert "This is the main content" in result["content"], "Main content not found in extracted text"
    assert result["url"] == url, "URL was not preserved in result"
    assert result["domain"] == "example.com", "Domain was not extracted correctly"
    assert result["metadata"]["author"] == "John Doe", "Author metadata not extracted correctly"
    assert result["metadata"]["date"] == "2024-01-01", "Date metadata not extracted correctly"

def test_extract_from_url_timeout(extractor, requests_mock):
    url = "http://example.com/timeout"
    requests_mock.get(url, exc=Timeout)
    
    result = extractor.extract_from_url(url)
    assert "error" in result, "Timeout error not reported in result"
    assert "timed out" in result["error"].lower(), "Incorrect error message for timeout"

def test_extract_from_url_connection_error(extractor, requests_mock):
    url = "http://example.com/connection-error"
    requests_mock.get(url, exc=ConnectionError)
    
    result = extractor.extract_from_url(url)
    assert "error" in result, "Connection error not reported in result"
    assert "connection failed" in result["error"].lower(), "Incorrect error message for connection failure"

def test_extract_from_url_http_error(extractor, requests_mock):
    url = "http://example.com/not-found"
    requests_mock.get(url, status_code=404)
    
    result = extractor.extract_from_url(url)
    assert "error" in result, "HTTP error not reported in result"
    assert "http error" in result["error"].lower(), "Incorrect error message for HTTP error"

def test_extract_from_text(extractor, sample_text):
    result = extractor.extract_from_text(sample_text)
    
    assert result["title"] == "Extracted text", "Incorrect title for text extraction"
    assert result["content"] == "This is some sample text with extra spaces.", "Text content not cleaned properly"
    assert result["metadata"]["type"] == "text", "Incorrect metadata type for text content"

def test_extract_from_code(extractor, sample_code):
    result = extractor.extract_from_code(sample_code)
    
    assert result["title"] == "Code snippet", "Incorrect title for code snippet"
    assert "def test_function():" in result["content"], "Code content not preserved"
    assert result["metadata"]["type"] == "code", "Incorrect metadata type for code content"

def test_extract_main_content(extractor, mock_html):
    soup = BeautifulSoup(mock_html, 'html.parser')
    content = extractor._extract_main_content(soup)
    
    assert "Main Heading" in content, "Main heading not found in extracted content"
    assert "This is the main content" in content, "Main content not found in extracted content"
    assert "alert('test')" not in content, "Script content was not removed"
    assert ".test { color: red; }" not in content, "Style content was not removed"

def test_extract_metadata(extractor, mock_html):
    soup = BeautifulSoup(mock_html, 'html.parser')
    metadata = extractor._extract_metadata(soup)
    
    assert metadata["author"] == "John Doe", "Author metadata not extracted correctly"
    assert metadata["date"] == "2024-01-01", "Date metadata not extracted correctly"

def test_clean_text(extractor):
    text = "  This  is   some \n  messy    text  \n\n  "
    cleaned = extractor.clean_text(text)
    assert cleaned == "This is some messy text", "Text not cleaned properly"

def test_clean_code(extractor):
    code = "\n\ndef test():\n    print('hello')\n\n"
    cleaned = extractor.clean_code(code)
    assert cleaned == "def test():\n    print('hello')", "Code not cleaned properly"

# New test cases for edge cases
def test_extract_from_empty_url_content(extractor, requests_mock):
    """Test extraction from URL that returns empty content"""
    url = "http://example.com/empty"
    requests_mock.get(url, text="")
    
    result = extractor.extract_from_url(url)
    assert result["title"] == "No title Found", "Empty page should return default title"
    assert result["content"] == "", "Empty page should return empty content"
    assert result["domain"] == "example.com", "Domain should still be extracted from empty page"

def test_extract_metadata_missing_fields(extractor):
    """Test metadata extraction when fields are missing"""
    html = """
    <html>
        <head>
            <title>Test</title>
            <!-- No metadata tags -->
        </head>
        <body>
            <p>Content</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    metadata = extractor._extract_metadata(soup)
    
    assert metadata == {}, "Metadata should be empty when no meta tags present"

def test_extract_from_text_with_special_chars(extractor):
    """Test text extraction with special characters and emojis"""
    text = "  Hello 👋 \n  World! @#$%  \t"
    result = extractor.extract_from_text(text)
    
    assert "👋" in result["content"], "Special characters/emojis should be preserved"
    assert result["content"] == "Hello 👋 World! @#$%", "Special characters not cleaned properly"
