from app.services.rag_service import RAGService
import os

def index_test_document():
    # Initialize RAG service
    rag_service = RAGService()
    
    # Path to the test document
    test_doc_path = "test_rag_document.pdf"
    
    if not os.path.exists(test_doc_path):
        print(f"Error: Test document not found at {test_doc_path}")
        print("Please run 'python3 tests/create_test_pdf.py' first")
        return
    
    print(f"Indexing test document: {test_doc_path}")
    
    # Add the test document to the knowledge base
    num_docs = rag_service.add_documents(file_path=test_doc_path)
    
    print(f"Successfully indexed {num_docs} chunks from {test_doc_path}")
    print("You can now query the knowledge base about Zyxoria!")

if __name__ == "__main__":
    index_test_document()
