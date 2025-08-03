from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import tempfile
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

from app.schemas.rag import AddDocumentsRequest, QueryRequest, QueryResponse, DocumentSourceType
from app.services.rag_service import RAGService

router = APIRouter(redirect_slashes=False)
rag_service = RAGService()

@router.post("/documents", response_model=dict)
async def add_documents(request: AddDocumentsRequest):
    """
    Add documents to the knowledge base from a file or URLs
    """
    try:
        rag_service.add_documents(
            file_path=request.file_path,
            urls=[str(url) for url in request.urls] if request.urls else None
        )
        return {"status": "success", "message": "Documents added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document file to add to the knowledge base
    """
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Add to knowledge base
        rag_service.add_documents(file_path=temp_file_path)
        
        # Clean up
        os.unlink(temp_file_path)
        
        return {"status": "success", "message": f"Document {file.filename} uploaded and processed"}
    except Exception as e:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base with a question and return answer with sources
    """
    try:
        # Get response from RAG service with sources
        rag_response = await rag_service.generate_response(
            query=request.query,
            chat_history=request.chat_history,
            top_k=4,  # Number of documents to retrieve
            score_threshold=0.5  # Minimum similarity score
        )
        
        # Convert sources to the expected format
        sources = [
            {
                "content": src.get("content", ""),
                "source": src.get("source", "unknown"),
                "metadata": {
                    **src.get("metadata", {}),
                    "score": src.get("score", 0.0)
                }
            }
            for src in rag_response.sources
        ]
        
        return QueryResponse(
            answer=rag_response.answer,
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error querying knowledge base: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
