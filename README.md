# FastAPI Chat with RAG

A production-ready FastAPI application featuring Retrieval-Augmented Generation (RAG) with local FAISS vector store and LM Studio model integration.

## Features

- **RAG Implementation**: Document-based question answering system
- **Multiple Document Sources**: Support for PDFs, text files, and web URLs
- **FAISS Vector Store**: Efficient local vector similarity search
- **LM Studio Integration**: Local model inference for privacy and cost-efficiency
- **Modular Architecture**: Clean separation of concerns with services and routes

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── routes/
│           ├── chat.py      # Chat endpoints
│           └── rag.py       # RAG endpoints
├── models/                 # Database models
├── schemas/                # Pydantic models
└── services/
    ├── document_service.py  # Document processing
    ├── local_model_service.py  # LM Studio integration
    ├── rag_service.py       # RAG orchestration
    └── vector_store_service.py  # MongoDB vector operations
```

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- LM Studio running locally (for local model inference)
- FAISS for vector storage (automatically installed via requirements.txt)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. **Set up a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

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