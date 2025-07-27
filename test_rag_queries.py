import requests
import json

def test_rag_query(question):
    """Test querying the RAG system with a question."""
    url = "http://localhost:8000/api/v1/chat/"
    
    # Prepare the request payload
    payload = {
        "user": "test_user",
        "message": question,
        "model_type": "local",
        "use_rag": True,
        "chat_history": []  # Add empty chat history
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
        "What percentage of Earth's atmosphere is nitrogen?",
        "What is the speed of light?"
    ]
    
    for question in questions:
        test_rag_query(question)
