"""
Test script to verify RAG system only responds with knowledge base information
for relevant queries and falls back to the base model for unrelated queries.
"""
import pytest
from typing import Dict, Any

# Test cases for RAG relevance
test_cases = [
    {
        "query": "What specific information is in the knowledge base about the project?",
        "expected_source": "rag"
    },
    {
        "query": "What is the capital of France?",
        "expected_source": "model"
    },
    {
        "query": "Can you explain the RAG implementation in this project?",
        "expected_source": "rag"
    },
    {
        "query": "Tell me a joke",
        "expected_source": "model"
    }
]

@pytest.mark.parametrize("test_case", test_cases)
def test_rag_relevance(test_client, test_case: Dict[str, Any]):
    """
    Test that the RAG system only responds with knowledge base information
    for relevant queries and falls back to the base model for unrelated queries.
    """
    query = test_case["query"]
    expected_source = test_case["expected_source"]
    
    # Send the query to the chat endpoint
    response = test_client.post(
        "/api/v1/chat/",
        json={
            "user": "test_user",
            "message": query,
            "use_rag": True
        }
    )
    
    # Verify the response
    assert response.status_code == 200, f"Request failed with status {response.status_code}"
    result = response.json()
    
    # Check if the response source matches expectations
    actual_source = result.get("model_used", "unknown").lower()
    
    if expected_source == "rag":
        assert actual_source == "rag", f"Expected RAG response but got {actual_source} response"
    else:
        assert actual_source != "rag", f"Expected model response but got RAG response"

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
        result = test_query(test_client, query, expected_source)
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

def test_query(test_client, query, expected_source):
    # Send the query to the chat endpoint
    response = test_client.post(
        "/api/v1/chat/",
        json={
            "user": "test_user",
            "message": query,
            "use_rag": True
        }
    )
    
    # Verify the response
    assert response.status_code == 200, f"Request failed with status {response.status_code}"
    result = response.json()
    
    return result

if __name__ == "__main__":
    print("Starting RAG relevance tests...")
    print("This will test that the RAG system only responds with knowledge base")
    print("information for relevant queries and falls back to the base model for others.\n")
    
    run_tests(test_client)
    print("\nTests completed!")
