"""
Test configuration and shared fixtures for pytest.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

# Add common test utilities and fixtures here
