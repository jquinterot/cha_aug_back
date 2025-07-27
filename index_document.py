import requests
import time

def index_document(file_path):
    url = "http://localhost:8000/api/v1/rag/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/pdf')}
            print(f"Uploading {file_path}...")
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            print("Document indexed successfully!")
            print("Response:", response.json())
            return True
        else:
            print(f"Error indexing document. Status code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Index the test document
    success = index_document("test_rag_document.pdf")
    
    if success:
        print("\nDocument should now be indexed. You can verify by checking the vector store.")
    else:
        print("\nFailed to index document. Please check the error message above.")
