import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

from src.core.exceptions import URLFormatException, NullContentException, InvalidContentException, MetadataExtractionException


class ContentExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    def extract_from_url(self, url: str) -> dict:
        """Extract content from a given URL."""
        if not url:
            raise URLFormatException(message=f"Invalid URL format. The URL cannot be empty. It needs to be of format http://<URL> or https://<URL> but got {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            if not response.content:
                return {
                    "title": "No title Found",
                    "content": "",
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "metadata": {"type": "empty"}
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip() if title else "No title Found"
            
            content = self._extract_main_content(soup)
            
            metadata = self._extract_metadata(soup)
            return {
                "title": title,
                "content": content,
                "url": url,
                "domain": urlparse(url).netloc,
                "metadata": metadata,
            }
        except UnicodeDecodeError:
                        raise InvalidContentException(message="Invalid content encoding. Unable to decode the content from the URL.")
        except Timeout:
            return {"error": "Request timed out"}
        except ConnectionError:
            return {"error": "Connection failed"}
        except HTTPError as e:
            return {"error": f"HTTP error: {e}"}
        except RequestException as e:
            return {"error": f"Request failed: {e}"}
        except Exception as e:
            return {"error": str(e)}
    def _extract_main_content(self, soup):
        """Extract the main readable content from HTML."""
        if not soup:
            raise NullContentException(message="The provided HTML content is Null or empty")
        for script in soup(["script", "style"]):
            script.decompose()
        content_selectors = [
            'article', '.content', '.post-content',
            '.main-content', '.entry-content', 'main'
        ]
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        
        return self.clean_text(soup.get_text())
    def _extract_metadata(self, soup):
        """Extract metadata like author and date."""
        metadata = {}
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["author"] = author["content"]
        date = soup.find("meta", attrs={"property": "article:published_time"})
        if date and date.get("content"):
            metadata["date"] = date["content"]
        if not metadata:
            raise MetadataExtractionException(message="Error extracting metadata. No metadata found in the content.")

        return metadata
    def extract_from_text(self, text: str) -> dict:
        """Extract Content from a given text."""
        cleaned_text = self.clean_text(text)
        return {
            'title': 'Extracted text',
            'content': cleaned_text,
            'metadata': {"type": "text"}
        }
    def extract_from_code(self, code: str) -> dict:
        """Extract code content."""
        cleaned_code = self.clean_code(code)
        return {
            'title': "Code snippet",
            'content': cleaned_code,
            'metadata': {"type": "code"}
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        text = re.sub(r'\s+', ' ', text)  
        return text.strip()
    def clean_code(self, code: str) -> str:
        """Clean code blocks (strip extra whitespace)."""
        return code.strip()
