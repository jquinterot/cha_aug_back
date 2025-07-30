# RAG System Configuration and Implementation

This document outlines the configuration and implementation details of the Retrieval-Augmented Generation (RAG) system used in this project.

## Core Components

### 1. Vector Store Service (`vector_store_service.py`)
- **Purpose**: Manages document storage and retrieval using FAISS
- **Key Features**:
  - Uses FAISS for efficient similarity search
  - Implements document chunking and embedding
  - Handles vector store persistence
  - Supports incremental updates

### 2. RAG Service (`rag_service.py`)
- **Purpose**: Orchestrates the retrieval and generation pipeline
- **Key Features**:
  - Manages document retrieval
  - Handles query processing
  - Integrates with language models
  - Implements relevance filtering

### 3. Response Formatter (`response_formatter.py`)
- **Purpose**: Formats responses for consistency and politeness
- **Key Features**:
  - Standardizes response format
  - Implements polite fallbacks
  - Handles source attribution

## Document Processing Pipeline

### Chunking Strategy
- Uses `RecursiveCharacterTextSplitter` from LangChain
- **Chunk Size**: 500 tokens (configurable via environment variables)
- **Chunk Overlap**: 100 tokens
- **Separators**: ["\n\n", "\n", ". ", " ", ""]

### Embedding Model
- **Model**: `sentence-transformers/all-mpnet-base-v2`
- **Features**:
  - 768-dimensional embeddings
  - Optimized for semantic search
  - Good performance on technical documentation

## Response Generation

### Polite Response Handling
1. **Fallback Responses**: Custom polite messages when no relevant information is found
2. **Confidence Handling**: Different response styles based on confidence levels
3. **Source Attribution**: Proper citation of document sources

### Prompt Engineering
- Uses structured prompts with clear instructions
- Includes context and examples
- Maintains professional yet friendly tone

## Performance Optimizations

1. **Document Filtering**:
   - Minimum document length: 50 characters
   - Score threshold: 0.45 (configurable)
   - Term ratio threshold: 0.35 (configurable)

2. **Caching**:
   - Vector store caching
   - Embedding caching

## Environment Configuration

Required environment variables:
```
# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Chunking configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Vector store
VECTOR_STORE_DIR=./vector_store
INDEX_NAME=vector_index

# OpenAI (for generation)
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4-turbo
```

## Development Notes

### Testing
- Use `test_rag_improvements.py` for testing RAG functionality
- `inspect_vector_store.py` for debugging vector store contents

### Common Issues
1. **Low Relevance Scores**:
   - Check document chunking
   - Verify embedding model compatibility
   - Adjust score thresholds

2. **Slow Performance**:
   - Check embedding model loading
   - Verify FAISS index optimization
   - Consider reducing chunk size

## Dependencies

Core libraries:
- `langchain`: Document processing and RAG pipeline
- `sentence-transformers`: Text embeddings
- `faiss-cpu`/`faiss-gpu`: Vector similarity search
- `openai`: Response generation
- `pypdf`: PDF processing
- `python-dotenv`: Environment management
