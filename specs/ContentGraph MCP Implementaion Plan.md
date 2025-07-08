# ContentGraph MCP Server: Implementation Plan

## **Project Overview**
Build an MCP (Model Context Protocol) server that integrates with Claude Desktop or VSCode to manage personal content consumption. Users can store content they've read and query/quiz themselves on it.

## **Functional Requirements**
1. **Content Storage**: Store links/content with embeddings, categories, timestamps
2. **Content Retrieval**: Query content by date range with categories and summaries
3. **Quiz Generation**: Create quizzes based on stored content by category

---

## **Week 1: MCP Server Foundation & Content Storage**

### **Day 1-2: MCP Server Setup**

**Resources:**
- [MCP Official Documentation](https://modelcontextprotocol.io/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)

**Step-by-Step Implementation:**

1. **Initialize MCP Server Project** (2 hours)
   ```bash
   # Create project structure
   mkdir contentgraph-mcp
   cd contentgraph-mcp
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install mcp python-dotenv requests beautifulsoup4 chromadb sentence-transformers openai instructor pydantic
   ```

2. **Basic MCP Server Structure** (3 hours)
   ```python
   # main.py
   from mcp.server import Server
   from mcp.server.stdio import stdio_server
   from mcp.types import Tool, TextContent
   
   server = Server("contentgraph")
   
   @server.list_tools()
   async def list_tools():
       return [
           Tool(
               name="store_content",
               description="Store content (URL or text) with metadata",
               inputSchema={
                   "type": "object",
                   "properties": {
                       "content": {"type": "string", "description": "URL or text content"},
                       "content_type": {"type": "string", "enum": ["url", "text", "code", "image"]}
                   },
                   "required": ["content", "content_type"]
               }
           ),
           Tool(
               name="query_content",
               description="Query stored content by date range",
               inputSchema={
                   "type": "object",
                   "properties": {
                       "start_date": {"type": "string", "format": "date"},
                       "end_date": {"type": "string", "format": "date"},
                       "category": {"type": "string", "description": "Optional category filter"}
                   },
                   "required": ["start_date", "end_date"]
               }
           ),
           Tool(
               name="generate_quiz",
               description="Generate quiz based on stored content",
               inputSchema={
                   "type": "object", 
                   "properties": {
                       "category": {"type": "string", "description": "Category to quiz on"},
                       "num_questions": {"type": "integer", "default": 5}
                   },
                   "required": ["category"]
               }
           )
       ]
   ```

3. **Database Schema Design** (2 hours)
   ```python
   # models.py
   from pydantic import BaseModel
   from datetime import datetime
   from typing import List, Optional
   
   class ContentRecord(BaseModel):
       id: str
       original_content: str
       content_type: str  # url, text, code, image
       title: str
       summary: str
       category: str
       tags: List[str]
       embedding: List[float]
       timestamp: datetime
       source_url: Optional[str] = None
       metadata: dict = {}
   ```

**Documentation Links:**
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python SDK Reference](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md)

### **Day 3-4: Content Processing Pipeline**

**Resources:**
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

**Implementation:**

1. **Content Extraction Service** (4 hours)
   ```python
   # content_extractor.py
   import requests
   from bs4 import BeautifulSoup
   from urllib.parse import urlparse
   import re
   
   class ContentExtractor:
       def __init__(self):
           self.headers = {
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
           }
       
       def extract_from_url(self, url: str) -> dict:
           """Extract content from URL"""
           try:
               response = requests.get(url, headers=self.headers, timeout=10)
               soup = BeautifulSoup(response.content, 'html.parser')
               
               # Extract title
               title = soup.find('title')
               title = title.text.strip() if title else "No Title"
               
               # Extract main content (customize based on common patterns)
               content = self._extract_main_content(soup)
               
               return {
                   'title': title,
                   'content': content,
                   'url': url,
                   'domain': urlparse(url).netloc
               }
           except Exception as e:
               return {'error': str(e)}
       
       def _extract_main_content(self, soup):
           # Remove script and style elements
           for script in soup(["script", "style"]):
               script.decompose()
           
           # Try common content selectors
           content_selectors = [
               'article', '.content', '.post-content', 
               '.entry-content', 'main', '.main-content'
           ]
           
           for selector in content_selectors:
               element = soup.select_one(selector)
               if element:
                   return element.get_text(strip=True)
           
           # Fallback to body text
           return soup.get_text(strip=True)
   ```

2. **Local Embedding Service** (3 hours)
   ```python
   # embedding_service.py
   from sentence_transformers import SentenceTransformer
   import numpy as np
   
   class EmbeddingService:
       def __init__(self, model_name="all-MiniLM-L6-v2"):
           self.model = SentenceTransformer(model_name)
       
       def generate_embedding(self, text: str) -> List[float]:
           """Generate embedding for text"""
           embedding = self.model.encode(text)
           return embedding.tolist()
       
       def similarity_search(self, query_embedding: List[float], 
                           stored_embeddings: List[List[float]], 
                           top_k: int = 5) -> List[int]:
           """Find most similar embeddings"""
           query_array = np.array(query_embedding)
           stored_array = np.array(stored_embeddings)
           
           # Calculate cosine similarity
           similarities = np.dot(stored_array, query_array) / (
               np.linalg.norm(stored_array, axis=1) * np.linalg.norm(query_array)
           )
           
           # Return indices of top-k most similar
           return np.argsort(similarities)[::-1][:top_k].tolist()
   ```

**Testing Resources:**
- Test URLs: Use articles from different domains
- [Sentence Transformers Model Hub](https://www.sbert.net/docs/pretrained_models.html)

### **Day 5-7: Vector Database & Categorization**

**Resources:**
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API for Categorization](https://platform.openai.com/docs/guides/text-generation)

**Implementation:**

1. **Vector Database Setup** (4 hours)
   ```python
   # vector_db.py
   import chromadb
   from chromadb.config import Settings
   import uuid
   from typing import List, Dict, Optional
   
   class VectorDatabase:
       def __init__(self, persist_directory="./chroma_db"):
           self.client = chromadb.PersistentClient(path=persist_directory)
           self.collection = self.client.get_or_create_collection(
               name="content_records",
               metadata={"hnsw:space": "cosine"}
           )
       
       def store_content(self, content_record: ContentRecord):
           """Store content with embedding"""
           self.collection.add(
               embeddings=[content_record.embedding],
               documents=[content_record.summary],
               metadatas=[{
                   "title": content_record.title,
                   "category": content_record.category,
                   "timestamp": content_record.timestamp.isoformat(),
                   "content_type": content_record.content_type,
                   "source_url": content_record.source_url,
                   "tags": ",".join(content_record.tags)
               }],
               ids=[content_record.id]
           )
       
       def query_by_date_range(self, start_date: str, end_date: str, 
                              category: Optional[str] = None) -> List[Dict]:
           """Query content by date range"""
           where_clause = {
               "timestamp": {"$gte": start_date, "$lte": end_date}
           }
           if category:
               where_clause["category"] = category
           
           results = self.collection.get(where=where_clause)
           return self._format_results(results)
       
       def similarity_search(self, query_embedding: List[float], 
                           n_results: int = 5) -> List[Dict]:
           """Search for similar content"""
           results = self.collection.query(
               query_embeddings=[query_embedding],
               n_results=n_results
           )
           return self._format_results(results)
   ```

2. **Categorization Service** (3 hours)
   ```python
   # categorization_service.py
   from openai import OpenAI
   import instructor
   from pydantic import BaseModel
   from typing import List
   
   class CategoryResult(BaseModel):
       category: str
       confidence: float
       tags: List[str]
       summary: str
   
   class CategorizationService:
       def __init__(self, api_key: str):
           self.client = instructor.from_openai(OpenAI(api_key=api_key))
       
       def categorize_content(self, title: str, content: str) -> CategoryResult:
           """Categorize content using LLM"""
           prompt = f"""
           Analyze the following content and provide:
           1. A primary category (e.g., Technology, Science, Business, etc.)
           2. Confidence score (0-1)
           3. 3-5 relevant tags
           4. A 2-sentence summary
           
           Title: {title}
           Content: {content[:1000]}...
           """
           
           result = self.client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": prompt}],
               response_model=CategoryResult
           )
           
           return result
   ```

**Documentation Links:**
- [ChromaDB Getting Started](https://docs.trychroma.com/getting-started)
- [Instructor Library](https://python.useinstructor.com/)

---

## **Week 2: MCP Tool Implementation & Integration**

### **Day 8-10: Implement MCP Tools**

**Resources:**
- [MCP Tools Documentation](https://modelcontextprotocol.io/docs/concepts/tools)
- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)

**Implementation:**

1. **Complete MCP Server Implementation** (6 hours)
   ```python
   # mcp_server.py
   import asyncio
   from mcp.server import Server
   from mcp.server.stdio import stdio_server
   from mcp.types import Tool, TextContent
   import json
   from datetime import datetime
   
   # Import your services
   from content_extractor import ContentExtractor
   from embedding_service import EmbeddingService
   from vector_db import VectorDatabase
   from categorization_service import CategorizationService
   
   class ContentGraphMCP:
       def __init__(self):
           self.extractor = ContentExtractor()
           self.embedder = EmbeddingService()
           self.vector_db = VectorDatabase()
           self.categorizer = CategorizationService(api_key="your-openai-key")
           
       async def store_content(self, content: str, content_type: str):
           """Store content with full processing pipeline"""
           try:
               # Extract content based on type
               if content_type == "url":
                   extracted = self.extractor.extract_from_url(content)
                   if 'error' in extracted:
                       return f"Error extracting URL: {extracted['error']}"
                   
                   title = extracted['title']
                   text_content = extracted['content']
                   source_url = content
               else:
                   title = f"{content_type.title()} Content"
                   text_content = content
                   source_url = None
               
               # Generate embedding
               embedding = self.embedder.generate_embedding(text_content)
               
               # Categorize content
               category_result = self.categorizer.categorize_content(title, text_content)
               
               # Create record
               record = ContentRecord(
                   id=str(uuid.uuid4()),
                   original_content=content,
                   content_type=content_type,
                   title=title,
                   summary=category_result.summary,
                   category=category_result.category,
                   tags=category_result.tags,
                   embedding=embedding,
                   timestamp=datetime.now(),
                   source_url=source_url
               )
               
               # Store in vector database
               self.vector_db.store_content(record)
               
               return f"✅ Stored: {title}\n📂 Category: {category_result.category}\n📝 Summary: {category_result.summary}"
               
           except Exception as e:
               return f"❌ Error storing content: {str(e)}"
   
   # Initialize MCP server
   server = Server("contentgraph")
   content_graph = ContentGraphMCP()
   
   @server.call_tool()
   async def call_tool(name: str, arguments: dict):
       if name == "store_content":
           return await content_graph.store_content(
               arguments["content"], 
               arguments["content_type"]
           )
       elif name == "query_content":
           return await content_graph.query_content(
               arguments["start_date"],
               arguments["end_date"], 
               arguments.get("category")
           )
       elif name == "generate_quiz":
           return await content_graph.generate_quiz(
               arguments["category"],
               arguments.get("num_questions", 5)
           )
   ```

2. **Quiz Generation Service** (4 hours)
   ```python
   # quiz_service.py
   from openai import OpenAI
   import instructor
   from pydantic import BaseModel
   from typing import List, Dict
   
   class QuizQuestion(BaseModel):
       question: str
       options: List[str]
       correct_answer: int
       explanation: str
   
   class Quiz(BaseModel):
       title: str
       questions: List[QuizQuestion]
   
   class QuizService:
       def __init__(self, api_key: str):
           self.client = instructor.from_openai(OpenAI(api_key=api_key))
       
       def generate_quiz(self, content_summaries: List[str], 
                        category: str, num_questions: int = 5) -> Quiz:
           """Generate quiz from content summaries"""
           combined_content = "\n\n".join(content_summaries)
           
           prompt = f"""
           Create a {num_questions}-question multiple choice quiz based on the following content from the {category} category.
           
           Content:
           {combined_content}
           
           Requirements:
           - Each question should have 4 options
           - Include explanations for correct answers
           - Mix of difficulty levels
           - Focus on key concepts and facts
           """
           
           quiz = self.client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": prompt}],
               response_model=Quiz
           )
           
           return quiz
   ```

### **Day 11-12: Testing & Integration**

**Resources:**
- [MCP Testing Guide](https://modelcontextprotocol.io/docs/tools/testing)
- [Claude Desktop Configuration](https://claude.ai/docs/mcp-setup)

**Implementation:**

1. **Local Testing Script** (3 hours)
   ```python
   # test_mcp.py
   import asyncio
   from mcp_server import content_graph
   
   async def test_workflow():
       # Test content storage
       result = await content_graph.store_content(
           "https://example.com/article", 
           "url"
       )
       print("Store Result:", result)
       
       # Test content query
       result = await content_graph.query_content(
           "2024-01-01", 
           "2024-12-31"
       )
       print("Query Result:", result)
       
       # Test quiz generation
       result = await content_graph.generate_quiz("Technology", 3)
       print("Quiz Result:", result)
   
   if __name__ == "__main__":
       asyncio.run(test_workflow())
   ```

2. **Claude Desktop Integration** (3 hours)
   ```json
   # claude_desktop_config.json
   {
     "mcpServers": {
       "contentgraph": {
         "command": "python",
         "args": ["/path/to/your/mcp_server.py"],
         "env": {
           "OPENAI_API_KEY": "your-key-here"
         }
       }
     }
   }
   ```

**Testing Checklist:**
- [ ] URL content extraction works
- [ ] Text content storage works
- [ ] Content categorization is accurate
- [ ] Date range queries return correct results
- [ ] Quiz generation produces valid questions
- [ ] MCP server responds to Claude Desktop

### **Day 13-14: Documentation & Deployment**

**Implementation:**

1. **Project Documentation** (4 hours)
   ```markdown
   # ContentGraph MCP Server
   
   ## Setup Instructions
   1. Clone repository
   2. Install dependencies: `pip install -r requirements.txt`
   3. Set environment variables
   4. Configure Claude Desktop
   
   ## Usage Examples
   - Store URL: "Store this article: https://example.com"
   - Query content: "Show me what I read about AI last week"
   - Generate quiz: "Quiz me on Technology articles"
   ```

2. **Error Handling & Logging** (2 hours)
   ```python
   # Add comprehensive error handling and logging
   import logging
   
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

---

## **Additional Resources**

### **Essential Documentation:**
- [MCP Official Specification](https://spec.modelcontextprotocol.io/)
- [Claude Desktop MCP Setup](https://claude.ai/docs/mcp)
- [VSCode MCP Extension](https://marketplace.visualstudio.com/items?itemName=ModelContext.mcp)

### **Learning Resources:**
- [MCP Tutorial Series](https://modelcontextprotocol.io/tutorials)
- [Building MCP Servers](https://modelcontextprotocol.io/docs/building-servers)

### **Development Tools:**
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Debug MCP servers
- [MCP Test Client](https://github.com/modelcontextprotocol/test-client) - Test MCP functionality

### **Deployment Options:**
- Local development with Claude Desktop
- Docker containerization for cloud deployment
- GitHub Actions for CI/CD

### **Sample Data for Testing:**
- Tech articles: TechCrunch, Hacker News, ArsTechnica
- Academic papers: arXiv.org
- Documentation: Python docs, API references
- Code snippets: GitHub repositories

## **Success Criteria**

**Week 1 Completion:**
- [ ] MCP server responds to basic commands
- [ ] Content extraction works for URLs and text
- [ ] Local vector database stores content with embeddings
- [ ] Categorization produces reasonable results

**Week 2 Completion:**
- [ ] Full integration with Claude Desktop
- [ ] All three main tools work reliably
- [ ] Quiz generation creates valid questions
- [ ] Content queries return formatted results
- [ ] Error handling prevents crashes

**Final Deliverables:**
- Working MCP server with all three tools
- Integration with Claude Desktop or VSCode
- Documentation for setup and usage
- Test suite for core functionality