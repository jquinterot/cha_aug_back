"""
Tests for verifying the system correctly routes queries between RAG and base model.
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rag_query():
    """Test that RAG-specific queries return information from the knowledge base."""
    response = client.post(
        "/api/v1/chat/",
        params={"model_type": "local"},
        json={
            "user": "test_user",
            "message": "What is the capital of Zyxoria?",
            "use_rag": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should contain information from the RAG knowledge base
    assert "Zyxtropolis" in data["message"]
    assert "model_used" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert any("Zyxoria" in source.get("content", "") for source in data["sources"])

def test_non_rag_math_query():
    """Test that mathematical queries are handled by the base model, not RAG."""
    response = client.post(
        "/api/v1/chat/",
        params={"model_type": "local"},
        json={
            "user": "test_user",
            "message": "What is 1 + 1?",
            "use_rag": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should not contain RAG-specific markers or sources
    assert "sources" not in data or not data["sources"]
    assert "2" in data["message"]  # Simple check for correct answer

def test_general_knowledge_query():
    """Test that general knowledge queries don't use RAG when not needed."""
    response = client.post(
        "/api/v1/chat/",
        params={"model_type": "local"},
        json={
            "user": "test_user",
            "message": "What is the capital of France?",
            "use_rag": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should not contain Zyxoria information
    assert "Zyxoria" not in data["message"]
    assert "Zyxtropolis" not in data["message"]
    # Should contain the expected answer
    assert "Paris" in data["message"]

def test_rag_disabled():
    """Test that RAG is not used when explicitly disabled."""
    response = client.post(
        "/api/v1/chat/",
        params={"model_type": "local"},
        json={
            "user": "test_user",
            "message": "What is the capital of Zyxoria?",
            "use_rag": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should not contain RAG-specific information
    assert "Zyxtropolis" not in data["message"]
    assert "sources" not in data or not data["sources"]

def test_rag_enabled_but_no_relevant_info():
    """Test that when RAG is enabled but no relevant info is found, the base model responds."""
    response = client.post(
        "/api/v1/chat/",
        params={"model_type": "local"},
        json={
            "user": "test_user",
            "message": "What is the meaning of life?",
            "use_rag": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should not contain RAG-specific information for this query
    assert "Zyxoria" not in data["message"]
    assert "Zyxtropolis" not in data["message"]
    # The response should be from the base model, not RAG
    assert "sources" not in data or not data["sources"] or not any(
        "Zyxoria" in source.get("content", "") for source in data["sources"]
    )
