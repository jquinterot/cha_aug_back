# Test Suite

This directory contains all test files for the RAG Chat application. The tests are organized by functionality and cover various aspects of the application.

## Test Organization

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test the complete application flow

## Running Tests

### Run All Tests
```bash
pytest
```

### Run a Specific Test File
```bash
pytest tests/test_rag_relevance.py
```

### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

## Test Files

- `test_rag_relevance.py`: Tests for RAG relevance filtering
- `test_query_routing.py`: Tests for query routing logic
- `test_chat_endpoint.py`: Tests for the chat API endpoints
- `test_politeness.py`: Tests for response politeness filters
- `test_*_loader.py`: Tests for various document loaders

## Writing New Tests

1. Create a new test file with the prefix `test_`
2. Use descriptive test function names starting with `test_`
3. Add docstrings to explain what each test verifies
4. Use fixtures from `conftest.py` for common test setup

## Test Data

Test data files should be placed in the `tests/data/` directory.
