# ContentGraph MCP Server: Design Document

## **Executive Summary**

ContentGraph is a Model Context Protocol (MCP) server that enables users to store, organize, and quiz themselves on content they consume online. The system integrates seamlessly with Claude Desktop, providing a conversational interface for content management without requiring a separate UI.

## **System Architecture Overview**

The ContentGraph MCP server follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│              Claude Desktop                  │
│         (User Interface Layer)               │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────┐
│            MCP Server Layer                  │
│         (main.py + mcp_server.py)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│             Tools Layer                      │
│    (store_content, query_content, quiz)     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Services Layer                     │
│  (Content Processing, AI, Database)         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Data Layer                        │
│        (ChromaDB, SQLite, Files)            │
└─────────────────────────────────────────────┘
```

## **Directory Structure Breakdown**

### **Root Level Files**

#### **`main.py`** - Application Entry Point
**Purpose:** The primary entry point for the MCP server
**Responsibilities:**
- Initialize the MCP server
- Set up environment and configuration
- Start the server process and handle shutdown

**Why Here:** Standard convention for Python applications; provides a clear starting point for the application

#### **`requirements.txt`** - Dependency Management
**Purpose:** Lists all Python package dependencies
**Contents:** MCP SDK, AI libraries, web scraping tools, database drivers

#### **`.env.example` & Configuration Files**
**Purpose:** Template for environment variables and configuration
**Why Important:** Keeps secrets out of version control while documenting required configuration

---

### **`config/` - Configuration Management**

#### **`settings.py`**
**Purpose:** Centralized configuration management using Pydantic settings
**Responsibilities:**
- Environment variable loading
- Configuration validation
- Default value management
- Type-safe configuration access

**Example Structure:**
```python
class Settings(BaseSettings):
    openai_api_key: str
    chroma_db_path: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    log_level: str = "INFO"
```

#### **`mcp_config.json`**
**Purpose:** MCP-specific configuration for Claude Desktop integration
**Contents:** Server name, tool definitions, capabilities

**Why Separate:** MCP configuration follows specific JSON schema requirements different from application config

---

### **`src/` - Source Code**

The `src/` directory contains the core application code, organized by responsibility:

#### **`src/models/` - Data Models**

**Purpose:** Define the data structures used throughout the application using Pydantic

**`content.py`**
- `ContentRecord`: Main content data model
- `ContentMetadata`: Additional content information
- `ContentType`: Enumeration of supported content types

**`quiz.py`**
- `QuizQuestion`: Individual quiz question structure
- `Quiz`: Complete quiz with multiple questions
- `QuizResult`: User quiz performance tracking

**`responses.py`**
- `ToolResponse`: Standardized MCP tool response format
- `ErrorResponse`: Error handling data structures
- `SuccessResponse`: Success response templates

**Why Important:** Pydantic models provide:
- Type safety and validation
- Automatic JSON serialization
- Clear data contracts between components
- Runtime type checking

#### **`src/services/` - Business Logic Layer**

This directory contains the core business logic, each service handling a specific domain:

**`content_extractor.py`**
- **Purpose:** Extract clean text content from various sources
- **Responsibilities:** 
  - Web scraping with robust error handling
  - Content cleaning and normalization
  - Metadata extraction (title, author, date)
  - Support for multiple content formats

**`embedding_service.py`**
- **Purpose:** Generate and manage vector embeddings locally
- **Responsibilities:**
  - Load and manage sentence transformer models
  - Generate embeddings for content
  - Similarity calculations
  - Model caching and optimization

**`vector_database.py`**
- **Purpose:** Interface with ChromaDB for vector operations
- **Responsibilities:**
  - Store content with embeddings
  - Semantic search capabilities
  - Metadata filtering and querying
  - Database connection management

**`categorization_service.py`**
- **Purpose:** AI-powered content analysis and categorization
- **Responsibilities:**
  - Content categorization using LLMs
  - Summary generation
  - Tag extraction
  - Confidence scoring

**`quiz_service.py`**
- **Purpose:** Generate educational quizzes from stored content
- **Responsibilities:**
  - Question generation using AI
  - Difficulty level adjustment
  - Answer validation
  - Performance tracking

**`content_manager.py`**
- **Purpose:** Orchestrate all services for complete workflows
- **Responsibilities:**
  - Coordinate service interactions
  - Handle complex business logic
  - Manage transactions across services
  - Error recovery and retry logic

**Why Service Layer:** 
- Separates business logic from presentation
- Enables easy testing and mocking
- Promotes reusability across different interfaces
- Clear dependency management

#### **`src/tools/` - MCP Tool Implementations**

**Purpose:** Implement the specific tools that Claude Desktop can call

**`store_content.py`**
- **MCP Tool:** `store_content`
- **Function:** Process user content input and store in database
- **Input Validation:** URL/text validation, content type checking
- **Output:** Formatted confirmation with categorization results

**`query_content.py`**
- **MCP Tool:** `query_content`
- **Function:** Retrieve and format stored content by date/category
- **Features:** Date range filtering, category grouping, summary formatting

**`generate_quiz.py`**
- **MCP Tool:** `generate_quiz`
- **Function:** Create quizzes from stored content
- **Features:** Difficulty adjustment, question type variety, performance tracking

**Why Separate Tools:**
- Each tool has specific MCP requirements
- Independent testing and validation
- Clear separation of user-facing functionality
- Easy to add new tools without affecting existing ones

#### **`src/utils/` - Shared Utilities**

**`logging_config.py`**
- **Purpose:** Centralized logging configuration
- **Features:** Structured logging, file rotation, different log levels per component

**`error_handlers.py`**
- **Purpose:** Standardized error handling and recovery
- **Features:** Custom exception types, error formatting for MCP responses, retry logic

**`validators.py`**
- **Purpose:** Input validation helpers
- **Features:** URL validation, content type detection, sanitization functions

#### **`src/mcp_server.py` - MCP Server Implementation**

**Purpose:** Main MCP server that ties everything together
**Responsibilities:**
- Implement MCP protocol handlers
- Route tool calls to appropriate implementations
- Handle MCP-specific message formatting
- Manage server lifecycle

---

### **`tests/` - Testing Infrastructure**

#### **Test Organization**
**`conftest.py`** - Shared test configuration and fixtures
**`test_*.py`** - Individual component tests matching source structure
**`fixtures/`** - Test data and mock responses

#### **Testing Strategy**
- **Unit Tests:** Each service tested in isolation
- **Integration Tests:** Tool workflows tested end-to-end
- **Mock Data:** Realistic test content for consistent testing

**Why Comprehensive Testing:**
- MCP servers must be reliable for production use
- Complex AI integrations need validation
- Prevents regressions during development

---

### **`data/` - Persistent Storage**

#### **`chroma_db/`**
**Purpose:** ChromaDB vector database storage
**Contents:** Embeddings, metadata, indexes
**Why Local:** Privacy, performance, cost control

#### **`logs/`**
**Purpose:** Application log storage
**Organization:** Rotated logs by date, separate error logs
**Benefits:** Debugging, monitoring, performance analysis

---

### **`scripts/` - Automation and Utilities**

#### **`setup_environment.py`**
**Purpose:** Automated environment setup
**Functions:** Download models, create directories, validate configuration

#### **`test_integration.py`**
**Purpose:** Manual integration testing without Claude Desktop
**Benefits:** Faster development cycles, easier debugging

#### **`migrate_data.py`**
**Purpose:** Data migration and backup utilities
**Features:** Export/import content, database schema updates

---

### **`docs/` - Documentation**

#### **User Documentation**
- **`installation.md`:** Step-by-step setup guide
- **`usage_examples.md`:** Real-world usage scenarios
- **`troubleshooting.md`:** Common issues and solutions

#### **Developer Documentation**
- **`api_reference.md`:** MCP tools documentation
- **Architecture diagrams and design decisions**

---

## **Data Flow Architecture**

### **Content Storage Flow**
```
User Input → Content Extraction → Embedding Generation → 
AI Categorization → Vector Database Storage → User Confirmation
```

### **Content Query Flow**
```
User Query → Database Filter → Result Formatting → 
Response Generation → User Display
```

### **Quiz Generation Flow**
```
Category Selection → Content Retrieval → AI Quiz Generation → 
Question Formatting → User Interaction
```

## **Key Design Principles**

### **Modularity**
Each component has a single responsibility and clear interfaces, making the system maintainable and testable.

### **Privacy-First**
Local embedding generation and vector storage ensure user content remains private.

### **Error Resilience**
Comprehensive error handling ensures the system gracefully handles network issues, API failures, and invalid inputs.

### **Extensibility**
New content types, AI models, or tools can be added without modifying existing code.

### **Performance**
Local operations where possible, efficient caching, and optimized database queries ensure responsive user experience.

## **Technology Integration Points**

### **MCP Protocol Integration**
- Standardized tool definitions
- JSON schema validation
- Async operation support
- Error handling compliance

### **AI Service Integration**
- OpenAI API for categorization and quiz generation
- Local sentence transformers for embeddings
- Structured output using Instructor library

### **Database Integration**
- ChromaDB for vector operations
- SQLite for metadata (if needed)
- Efficient indexing and querying

This design provides a robust, scalable foundation for personal content management while maintaining simplicity and clear separation of concerns.