import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.document_service import DocumentProcessor

def test_json_loading():
    """Test loading and processing a JSON file."""
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Path to our test JSON file
    json_path = str(Path(__file__).parent / "test_data.json")
    
    print(f"Loading JSON file: {json_path}")
    
    # Load the JSON file
    try:
        documents = processor.load_documents(file_path=json_path)
        print(f"\nSuccessfully loaded {len(documents)} document(s) from JSON file.")
        
        # Process the documents
        chunks = processor.split_documents(documents)
        print(f"Split into {len(chunks)} chunks.")
        
        # Display the first chunk
        if chunks:
            print("\nFirst chunk content:")
            print("-" * 50)
            print(chunks[0].page_content)
            print("-" * 50)
            print(f"Metadata: {chunks[0].metadata}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_loading()
