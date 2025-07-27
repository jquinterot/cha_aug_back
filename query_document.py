import requests
import json

def query_rag(question):
    url = "http://localhost:8000/api/v1/rag/query"
    headers = {"Content-Type": "application/json"}
    data = {
        "query": question,
        "chat_history": []  # Empty chat history for a new conversation
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error querying RAG system: {e}")
        return None

if __name__ == "__main__":
    # Test query - ask something that should be in the test document
    test_question = "What is the main topic of the document?"
    print(f"Querying RAG system with: {test_question}")
    
    result = query_rag(test_question)
    
    if result:
        print("\nResponse:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to get a response from the RAG system.")
