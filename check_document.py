import pickle
import os
from pathlib import Path

def check_document_in_store(document_path):
    # Load the vector store
    vector_store_path = "vector_store/vector_index.pkl"
    if not os.path.exists(vector_store_path):
        print("Vector store not found at:", vector_store_path)
        return
    
    # Read the test document
    try:
        with open(document_path, 'rb') as f:
            content = f.read()
            # Try to read as text first
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                content = str(content[:1000])  # Just get first 1000 bytes for binary files
    except Exception as e:
        print(f"Error reading document: {e}")
        return
    
    # Load the vector store
    try:
        with open(vector_store_path, 'rb') as f:
            vector_store = pickle.load(f)
            
        # Check if we have any documents
        if not hasattr(vector_store, 'docstore') or not hasattr(vector_store.docstore, '_dict'):
            print("No documents found in vector store")
            return
            
        docstore = vector_store.docstore._dict
        print(f"Found {len(docstore)} documents in vector store")
        
        # Check if any document contains content from our test document
        content_sample = content[:100]  # Check first 100 chars for a match
        found = False
        
        for doc_id, doc in docstore.items():
            if content_sample in doc.page_content:
                print(f"Document found in vector store with ID: {doc_id}")
                print("Document content starts with:", doc.page_content[:200] + "...")
                found = True
                break
                
        if not found:
            print("Document content not found in vector store")
            
    except Exception as e:
        print(f"Error loading vector store: {e}")

if __name__ == "__main__":
    check_document_in_store("test_rag_document.pdf")
