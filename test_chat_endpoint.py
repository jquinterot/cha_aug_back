import pytest
import requests
import json
from typing import Generator

# Test data
TEST_QUESTIONS = [
    "What is the capital of Zyxoria?",
    "Who is the current leader of Zyxoria?",
    "What is the main export of Zyxoria?",
    "What is the population of Zyxoria?",
    "What is the official language of Zyxoria?"
]

@pytest.fixture(params=TEST_QUESTIONS)
def question(request):
    return request.param

def test_chat(question):
    """Test the chat endpoint with a question."""
    url = "http://localhost:8000/api/v1/chat/"
    
    # Prepare the request payload
    payload = {
        "message": question,
        "chat_history": [],
        "model_type": "local",
        "use_rag": True,
        "user": "test_user"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\nQuestion: {question}")
        print("-" * 80)
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            print(f"Answer: {response_data.get('message', 'No answer found')}")
            
            # Print sources if available
            sources = response_data.get('sources', [])
            if sources:
                print("\nSources:")
                for i, source in enumerate(sources, 1):
                    print(f"{i}. {source.get('source', 'Unknown source')}")
                    print(f"   Content: {source.get('content', 'No content')[:200]}...")
                    print()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    # Test questions based on the PDF content
    questions = [
        "What is the capital of Zyxoria?",
        "What is the national dish of Zyxoria?",
        "What is the national animal of Zyxoria?",
        "What is the official language of Zyxoria?",
        "What is the currency of Zyxoria?"
    ]
    
    for question in questions:
        test_chat(question)
        print("\n" + "="*80 + "\n")
