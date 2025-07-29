"""
Test script to verify query routing between RAG and base model.

This script tests that:
1. RAG-specific queries return information from the knowledge base
2. General knowledge/math queries are handled by the base model
3. RAG is not used when explicitly disabled
4. The system falls back to the base model when no relevant RAG info is found
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_query(query: str, use_rag: bool = True, model_type: str = "local") -> Dict[str, Any]:
    """Send a test query to the chat endpoint and return the response."""
    url = f"{BASE_URL}/api/v1/chat/"
    params = {"model_type": model_type}
    payload = {
        "user": "test_user",
        "message": query,
        "use_rag": use_rag
    }
    
    print(f"\nTesting query: {query}")
    print(f"RAG: {use_rag}, Model: {model_type}")
    
    try:
        response = requests.post(url, params=params, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return {}

def print_result(result: Dict[str, Any], show_sources: bool = False):
    """Print the test result in a readable format."""
    print("\n--- RESULT ---")
    print(f"Response: {result.get('message', 'No response')}")
    
    if 'model_used' in result:
        print(f"Model used: {result['model_used']}")
    
    if 'sources' in result and result['sources']:
        print(f"Sources found: {len(result['sources'])}")
        if show_sources:
            for i, source in enumerate(result['sources'], 1):
                print(f"\nSource {i}:")
                print(f"Content: {source.get('content', 'No content')[:200]}...")
                print(f"Source: {source.get('source', 'Unknown')}")
    else:
        print("No sources found (expected for non-RAG responses)")
    print("-" * 40)

def run_tests():
    """Run a series of test cases to verify query routing."""
    # Test cases: (query, use_rag, expected_to_use_rag)
    test_cases = [
        # RAG-specific queries (should use RAG when enabled)
        ("What is the capital of Zyxoria?", True, True),
        ("Tell me about Zorblatt stew.", True, True),
        
        # General knowledge (should not use RAG)
        ("What is 1 + 1?", True, False),
        ("What is the capital of France?", True, False),
        ("Who is the president of the United States?", True, False),
        
        # Explicitly disabled RAG
        ("What is the capital of Zyxoria?", False, False),
        
        # Queries with no RAG info
        ("What is the meaning of life?", True, False),
    ]
    
    for query, use_rag, expected_rag in test_cases:
        result = test_query(query, use_rag)
        
        # Check if RAG was used as expected
        rag_was_used = 'sources' in result and bool(result['sources'])
        
        print(f"\n{'✅' if rag_was_used == expected_rag else '❌'} Query: {query}")
        print(f"Expected RAG: {expected_rag}, Actual RAG: {rag_was_used}")
        
        # Print a brief result
        print(f"Response: {result.get('message', 'No response')[:100]}...")
        
        # For debugging unexpected results
        if rag_was_used != expected_rag:
            print("\n⚠️  Unexpected result! Details:")
            print(f"Query: {query}")
            print(f"Use RAG: {use_rag}")
            print(f"Result: {json.dumps(result, indent=2)}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("Starting query routing tests...\n")
    run_tests()
    print("\nTests completed!")
