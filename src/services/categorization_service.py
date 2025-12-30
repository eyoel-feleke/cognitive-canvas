import os
import time
import hashlib
from typing import List, Optional
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
import instructor
from pydantic import BaseModel, Field

class CategoryResults(BaseModel): 
    category: str = Field(..., description="Category of the content, e.g., Technology, Science, Business, etc.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1.")
    tags: List[str] = Field(..., description="List of relevant tags related to the content.")
    summary: str = Field(..., description="A short summary of the content.")
    
class CategorizationService:
    """A categorization service that uses AI to categorize content.
    Integrates with OpenAI via instructor."""
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or via the OPENAI_API_KEY environment variable.")
        
        self.client = instructor.from_openai(OpenAI(api_key=self.api_key))
        self.cache_enabled = cache_enabled
        self._cache: dict[str, CategoryResults] = {}
    
    def _generate_cache_key(self, title: str, content: str) -> str:
        """Create a unique cache key based on title and content."""
        return hashlib.blake2b((title + content).encode("utf-8")).hexdigest()
    def categorize_content(self, title: str, content: str, max_retries: int = 3, retry_delay: int = 2) -> CategoryResults: 
        """Categorize content using LLM"""
        if not content.strip():
            raise ValueError("Cannot categorize empty content.")
        
        cache_key = self._generate_cache_key(title, content)
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        prompt = f"""
        Analyze the given content and provide: 
        1. A general category (e.g Technology, Science, Business, etc.)
        2. Confidence score between 0-1 (float)
        3. 3 to 5 relevant tags (e.g., Machine Learning, Python, etc.)
        4. A short summary that gives a brief overview of the content. 
        
        Title: {title}
        Content : 
        {content[:1500]}
        """ 
        
        for attempt in range(1, max_retries + 1):
            try:
                result = self.client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role": "user", "content": prompt}], 
                    response_model=CategoryResults
                )
                if self.cache_enabled:
                    self._cache[cache_key] = result
                
                return result
            
            except (RateLimitError, APITimeoutError) as e:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise RuntimeError(f"Retry limit reached. Failed due to transient error: {str(e)}")
            except APIError as e:
                raise RuntimeError(f"API Error occurred: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error occurred: {str(e)}")