import os
import sys
import pickle
from dotenv import load_dotenv
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.append(project_root)

from app.services.vector_store_service import VectorStoreService, VECTOR_STORE_DIR

def check_vector_store():
    """Check the current state of the vector store."""
    try:
        print(f"Checking vector store in: {VECTOR_STORE_DIR}")
        
        # Check if the vector store directory exists
        if not os.path.exists(VECTOR_STORE_DIR):
            print(f"Vector store directory does not exist: {VECTOR_STORE_DIR}")
            return
            
        # List all files in the vector store directory
        print("\nFiles in vector store directory:")
        for f in os.listdir(VECTOR_STORE_DIR):
            print(f"- {f} (size: {os.path.getsize(os.path.join(VECTOR_STORE_DIR, f))} bytes)")
        
        # Try to load the vector store directly
        vector_store_path = os.path.join(VECTOR_STORE_DIR, "vector_index.pkl")
        if not os.path.exists(vector_store_path):
            print(f"\nNo vector store found at: {vector_store_path}")
            return
            
        print(f"\nFound vector store at: {vector_store_path}")
        print(f"Size: {os.path.getsize(vector_store_path) / (1024*1024):.2f} MB")
        
        # Try to load the vector store
        try:
            with open(vector_store_path, "rb") as f:
                vector_store = pickle.load(f)
                print("\nSuccessfully loaded vector store")
                
                # Try to get the number of vectors in the index
                if hasattr(vector_store, 'index') and hasattr(vector_store.index, 'ntotal'):
                    print(f"Number of vectors in index: {vector_store.index.ntotal}")
                
                # Try to get document count from docstore
                if hasattr(vector_store, 'docstore') and hasattr(vector_store.docstore, 'dict'):
                    docstore = vector_store.docstore
                    doc_ids = list(docstore._dict.keys())
                    print(f"Number of documents in docstore: {len(doc_ids)}")
                    
                    # Show some sample documents
                    if doc_ids:
                        print("\nSample documents:")
                        for doc_id in doc_ids[:3]:  # Show first 3 documents
                            doc = docstore.search(doc_id)
                            if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                                preview = doc.page_content[:100] + '...' if len(doc.page_content) > 100 else doc.page_content
                                print(f"- ID: {doc_id}")
                                print(f"  Content: {preview}")
                                print(f"  Metadata: {doc.metadata}")
                                print()
                            
        except Exception as e:
            print(f"\nError loading vector store: {str(e)}")
            
    except Exception as e:
        print(f"Error checking vector store: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check the vector store
    check_vector_store()
