# Intelligent Chat with RAG (Retrieval-Augmented Generation)

A production-ready FastAPI application that combines the power of large language models with document retrieval to provide accurate, context-aware responses. This implementation supports both local and cloud-based models, with a focus on privacy and efficiency.

## 🌟 Key Features

- **Retrieval-Augmented Generation (RAG)**: Combines retrieval-based and generative approaches for accurate responses
- **Multi-Model Support**: Seamlessly switch between local (LM Studio) and cloud (OpenAI) models
- **Smart Query Routing**: Automatically determines when to use RAG or base model based on query relevance
- **Document Processing**: Supports PDFs, text files, and web URLs as knowledge sources
- **Vector Search**: Utilizes FAISS for efficient similarity search in high-dimensional spaces
- **Docker Ready**: Easy deployment with containerization
- **Comprehensive Testing**: Includes test suites for RAG relevance and query routing

## 🧠 Key AI Concepts

### Core Technologies
- **RAG (Retrieval-Augmented Generation)**: Hybrid approach that retrieves relevant documents and uses them to generate accurate responses
- **Embeddings**: Numerical representations of text that capture semantic meaning
- **Vector Database**: Stores document embeddings for efficient similarity search
- **Semantic Search**: Finds relevant documents based on meaning rather than just keywords
- **Query Understanding**: Analyzes user queries to determine the most appropriate response strategy

### Key Components
- **Relevance Threshold**: Minimum similarity score (0-1) required to consider a document relevant to a query
- **Chunking**: Process of breaking down documents into smaller, manageable pieces
- **Context Window**: Maximum amount of text (tokens) that can be processed in a single request
- **Fallback Mechanism**: Automatic switching to base model when RAG doesn't have relevant information

## 🛠️ Technical Stack

### Backend
- **Framework**: FastAPI
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: OpenAI or Sentence Transformers
- **LLM Integration**: Support for both local (LM Studio) and cloud (OpenAI) models
- **Document Processing**: PyPDF, BeautifulSoup, Unstructured

### Infrastructure
- **Containerization**: Docker
- **API Documentation**: Swagger UI & ReDoc
- **Environment Management**: python-dotenv
- **Testing**: pytest

## 📦 Project Structure

```
app/
├── api/
│   └── v1/
│       └── routes/
│           ├── chat.py      # Chat endpoints
│           └── rag.py       # RAG document management
├── models/                 # Database models and schemas
├── schemas/                # Pydantic models for request/validation
└── services/
    ├── document_service.py  # Document processing and chunking
    ├── local_model_service.py  # LM Studio integration
    ├── model_service.py     # Unified model interface
    ├── rag_service.py       # RAG orchestration
    └── vector_store_service.py  # Vector operations
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- LM Studio (for local model inference)
- OpenAI API key (for cloud-based models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chat-aug-back.git
   cd chat-aug-back
   ```

2. **Set up environment variables**
   Copy the example environment file and update the values:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Using Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

4. **Local Development Setup**
   ```bash
   # Create and activate virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on the example and configure the following:

```env
# General Settings
DEBUG=true
PORT=8000

# Model Configuration
MODEL_TYPE=local  # or 'openai' for cloud-based models
DEFAULT_MODEL=llama-3.2-3b-instruct  # Default local model

# LM Studio Settings (for local models)
LM_STUDIO_BASE_URL=http://localhost:1234

# OpenAI Settings (for cloud-based models)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# RAG Configuration
SIMILARITY_THRESHOLD=0.7  # Minimum similarity score for document relevance
CHUNK_SIZE=1000  # Number of characters per document chunk
TOP_K_RESULTS=3  # Number of relevant documents to retrieve
```

## 🚦 Running the Application

### Start the API Server

```bash
# Using Docker (recommended for production)
docker-compose up --build

# Or run locally
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📚 Usage Examples

### 1. Adding Documents to the Knowledge Base

```bash
# Add a PDF document
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/documents' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@document.pdf;type=application/pdf'

# Add a website
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/url' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

### 2. Chat with the Assistant

```python
import requests

# Simple chat
response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    json={
        "user": "test_user",
        "message": "What is this document about?",
        "use_rag": True  # Enable RAG for knowledge-based responses
    }
)
print(response.json())
```

### 3. Check System Status

```bash
curl http://localhost:8000/api/v1/health
```

## 🔍 Understanding the Flow

1. **Document Processing**
   - Documents are chunked into smaller pieces
   - Each chunk is converted into vector embeddings
   - Embeddings are stored in the vector database

2. **Query Processing**
   - User query is converted to embeddings
   - System searches for similar document chunks
   - If similarity score > threshold, relevant chunks are used as context
   - Otherwise, the base model responds without RAG context

3. **Response Generation**
   - Relevant context + user query are sent to the LLM
   - The model generates a response using the provided context
   - Response is returned to the user with source attribution

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run RAG relevance tests
pytest test_rag_relevance.py

# Run query routing tests
pytest tests/test_query_routing.py
```

## 📊 Monitoring and Logging

Logs are available in `logs/app.log` with the following levels:
- INFO: General application events
- DEBUG: Detailed processing information
- WARNING: Non-critical issues
- ERROR: Critical errors that need attention

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) for local model serving
- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [OpenAI](https://openai.com/) for their language models and embeddings

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Docker Setup

1. **Build and start the containers**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file with your configuration
   # At minimum, set OPENAI_API_KEY if using OpenAI model
   
   # Start the application with Docker Compose
   docker-compose up --build -d
   ```

2. **Verify the containers are running**
   ```bash
   docker-compose ps
   ```
   You should see both `rag_chat_app` and `mongo` services running.

3. **View logs**
   ```bash
   # View all logs
   docker-compose logs -f
   
   # View logs for a specific service
   docker-compose logs -f app
   ```

4. **Stop the application**
   ```bash
   docker-compose down
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application
PORT=8000
MODEL_TYPE=local  # or 'openai' to use OpenAI API

# OpenAI (required if MODEL_TYPE=openai)
OPENAI_API_KEY=your_openai_api_key

# MongoDB
MONGODB_URL=mongodb://mongo:27017/rag_chat

# LM Studio (for local model)
LM_STUDIO_URL=http://host.docker.internal:1234  # On Linux, use your host IP
```

> **Note**: When running in Docker, use `host.docker.internal` to connect to services on your host machine (like LM Studio). On Linux, you might need to use `--add-host=host.docker.internal:host-gateway` in your Docker command.

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with:
   ```env
   # RAG Configuration
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   VECTOR_INDEX_NAME=default_index
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   
   # Optional: Uncomment and set if you want to use MongoDB
   # MONGO_URI=your_mongodb_atlas_connection_string
   # MONGODB_DB_NAME=rag_db
   # MONGODB_COLLECTION=documents
   ```

5. **Start LM Studio**
   - Download and install [LM Studio](https://lmstudio.ai/)
   - Start the local inference server on port 1234
   - Load your preferred model (e.g., `llama-3.2-3b-instruct`)

## Running the Application

1. **Start the FastAPI server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

2. **Access the API documentation**
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Using the RAG System

### Adding Documents

#### 1. Upload a File
Supported formats: PDF, TXT

```bash
# Upload a PDF file
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/document.pdf;type=application/pdf'

# Upload a text file
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/document.txt;type=text/plain'
```

#### 2. Add Text Directly
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/text' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Your text content here", "metadata": {"source": "manual"}}'
```

### Querying the Knowledge Base

#### 1. Simple Query
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Your question here"}'
```

Example response:
```json
{
  "answer": "The answer to your question based on the knowledge base.",
  "sources": [
    {
      "content": "Relevant text from the knowledge base.",
      "source": "document.pdf"
    }
  ]
}
```

#### 2. Advanced Query with Parameters
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Your question here",
    "top_k": 3,
    "score_threshold": 0.7
  }'
```

### Managing the Knowledge Base

#### Check Health Status
```bash
curl 'http://localhost:8000/api/v1/rag/health'
```

#### List All Documents
```bash
curl 'http://localhost:8000/api/v1/rag/documents'
```

#### Delete a Document
```bash
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/rag/documents/{document_id}' \
  -H 'accept: application/json'
```

#### 2. Add from URL
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/documents' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": ["https://example.com/document"]
  }'
```

### Querying the Knowledge Base

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/rag/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What is the main topic of the document?"
  }'
```

### Example Response
```json
{
  "answer": "The document discusses...",
  "sources": [
    {
      "content": "Relevant text from the document...",
      "metadata": {
        "source": "document.pdf",
        "page": 3
      }
    }
  ]
}
```

## API Endpoints

### RAG Endpoints
- `POST /api/v1/rag/upload` - Upload a document file
- `POST /api/v1/rag/documents` - Add documents from URLs
- `POST /api/v1/rag/query` - Query the knowledge base
- `GET /api/v1/rag/health` - Check service health

### Chat Endpoints
- `POST /api/v1/chat` - Send a chat message (supports both local and OpenAI models)

## Configuration

### Environment Variables
- `MONGO_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: `rag_db`)
- `MONGODB_COLLECTION`: Collection name (default: `documents`)
- `EMBEDDING_MODEL`: Sentence transformer model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `VECTOR_INDEX_NAME`: Name for the vector index (default: `vector_index`)
- `CHUNK_SIZE`: Document chunk size (default: `1000`)
- `CHUNK_OVERLAP`: Chunk overlap size (default: `200`)

## Troubleshooting

### Common Issues
1. **LM Studio Not Running**
   - Ensure LM Studio is running with the local server active on port 1234
   - Verify the model is loaded in LM Studio

2. **MongoDB Connection Issues**
   - Check your connection string
   - Verify network access in MongoDB Atlas
   - Ensure the IP is whitelisted in MongoDB Atlas

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Development

### Running Tests
```bash
# Add your test commands here
```

### Code Style
This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

## License

[Your License Here]

source venv/bin/activate && uvicorn app.main:app --reload

pkill -f uvicorn