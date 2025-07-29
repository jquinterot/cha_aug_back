"""
Test script to verify RAG system only responds with knowledge base information
for relevant queries and falls back to the base model for unrelated queries.
"""
import requests
import json
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000"

def test_query(query: str, expected_source: str = "model") -> dict:
    """
    Send a test query to the chat endpoint and return the response.
    
    Args:
        query: The query to test
        expected_source: Expected source of the response ('rag' or 'model')
    """
    url = f"{BASE_URL}/api/v1/chat/"
    payload = {
        "user": "test_user",
        "message": query,
        "use_rag": True
    }
    
    print(f"\nTesting query: {query}")
    print(f"Expected source: {expected_source}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Print the response
        print(f"Response: {result.get('message', 'No response')[:200]}...")
        print(f"Source: {result.get('model_used', 'unknown')}")
        
        # Check if the response source matches expectations
        if expected_source.lower() == "rag" and result.get("model_used") != "rag":
            print("❌ Expected RAG response but got model response")
        elif expected_source.lower() == "model" and result.get("model_used") == "rag":
            print("❌ Expected model response but got RAG response")
        else:
            print("✅ Response source matches expectation")
            
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

def run_tests():
    """Run a series of test cases to verify RAG relevance filtering."""
    # Test cases: (query, expected_source)
    test_cases = [
        # Queries that should use RAG (about Zyxoria)
        ("What is the capital of Zyxoria?", "rag"),
        ("Tell me about Zorblatt stew.", "rag"),
        ("What is the currency of Zyxoria?", "rag"),
        
        # Queries that should NOT use RAG (general knowledge)
        ("What is the capital of France?", "model"),
        ("Who is the president of the United States?", "model"),
        ("What is the weather like today?", "model"),
        ("Tell me about the history of the internet.", "model"),
        ("What is 2+2?", "model"),
        
        # Edge cases
        ("", "model"),  # Empty query
        ("Zyxoria", "rag"),  # Just the keyword
        ("This is a test query about nothing in particular.", "model"),
    ]
    
    results = []
    for query, expected_source in test_cases:
        result = test_query(query, expected_source)
        results.append({
            "query": query,
            "expected_source": expected_source,
            "actual_source": result.get("model_used", "unknown"),
            "response": result.get("message", "No response")[:200] + "..."
        })
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r["expected_source"].lower() == r["actual_source"].lower())
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # Print detailed results
    print("\nDETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["expected_source"].lower() == result["actual_source"].lower() else "❌"
        print(f"\n{status} Test {i}:")
        print(f"  Query: {result['query']}")
        print(f"  Expected: {result['expected_source']}")
        print(f"  Got: {result['actual_source']}")
        print(f"  Response: {result['response']}")

if __name__ == "__main__":
    print("Starting RAG relevance tests...")
    print("This will test that the RAG system only responds with knowledge base")
    print("information for relevant queries and falls back to the base model for others.\n")
    
    run_tests()
    print("\nTests completed!")
