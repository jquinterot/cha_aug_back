from app.services.rag_service import RAGService
import os

def index_test_documents():
    # Initialize RAG service
    rag_service = RAGService()
    
    # List of test documents to index
    test_docs = [
        "test_rag_document.pdf",  # Original Zyxoria test document
        "weird_test_document.pdf"  # Our new weird test document
    ]
    
    for doc_path in test_docs:
        if not os.path.exists(doc_path):
            print(f"Warning: Document not found at {doc_path}")
            continue
            
        print(f"\nIndexing document: {doc_path}")
        num_docs = rag_service.add_documents(file_path=doc_path)
        print(f"Successfully indexed {num_docs} chunks from {doc_path}")
    
    print("\nAll documents have been indexed!")
    print("You can now query the knowledge base about:")
    print("- Zyxoria (from test_rag_document.pdf)")
    print("- Quantum Fluffernutter (from weird_test_document.pdf)")
    print("- Time-traveling llamas (from weird_test_document.pdf)")
    print("- Other weird facts!")

if __name__ == "__main__":
    index_test_documents()
