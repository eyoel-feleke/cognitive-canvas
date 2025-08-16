# ContentGraph MCP Server

A Model Context Protocol (MCP) server for personal content management, quizzing, and retrieval. Integrates with Claude Desktop and supports local vector search with ChromaDB.

## Features

- Store and manage content from URLs, text, and code snippets
- Local vector embeddings using sentence transformers
- Semantic search with ChromaDB
- AI-powered content categorization
- Quiz generation from stored content
- Claude Desktop integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/eyoel-feleke/cognitive-canvas.git
cd cognitive-canvas/contentgraph-mcp
```

2. Install dependencies:
```bash
pip install -e .

# Or install with test dependencies
pip install -e ".[test]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Testing

The project uses pytest for testing with comprehensive coverage.

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests with specific markers
pytest -m unit
pytest -m integration
```

### Test Structure

The test suite includes:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Mock fixtures**: Comprehensive mocking for external dependencies
- **Coverage reporting**: HTML and terminal coverage reports

### Test Files

- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_models.py` - Data model validation tests
- `tests/test_content_extractor.py` - Content extraction service tests
- `tests/test_embedding_service.py` - Embedding generation tests
- `tests/test_vector_database.py` - Vector database operations tests
- `tests/test_mcp_tools.py` - MCP tool integration tests

### Test Configuration

Test configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--cov=src", "--cov-report=html", "--cov-report=term-missing"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]
```

### Writing Tests

When adding new features:

1. Add unit tests for new functions/classes
2. Use the provided fixtures in `conftest.py`
3. Mock external dependencies (OpenAI, web requests, file I/O)
4. Follow the existing test naming conventions
5. Add integration tests for component interactions

Example test:

```python
def test_my_function(sample_content_record, mock_openai_client):
    """Test my function with mocked dependencies."""
    result = my_function(sample_content_record)
    assert result.status == "success"
    mock_openai_client.assert_called_once()
```

## Usage

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "contentgraph": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/contentgraph-mcp"
    }
  }
}
```

### Available Tools

1. **store_content**: Save content from URLs or text
2. **query_content**: Search stored content by category/date
3. **generate_quiz**: Create quizzes from your content

## Development

### Code Quality

```bash
# Run linting
flake8 src tests

# Run type checking
mypy src

# Format code
black src tests
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
