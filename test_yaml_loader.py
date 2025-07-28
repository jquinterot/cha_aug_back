import sys
import os
from pathlib import Path
import yaml

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.document_service import DocumentProcessor

def test_yaml_loading():
    """Test loading and processing a YAML file."""
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Path to our test YAML file
    yaml_path = str(Path(__file__).parent / "test_data.yaml")
    
    print(f"Loading YAML file: {yaml_path}")
    
    # First, let's show the raw YAML content
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
            print("\nRaw YAML content:")
            print("-" * 50)
            print(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))
            print("-" * 50)
    except Exception as e:
        print(f"Error reading YAML file: {str(e)}")
        return
    
    # Now test loading with our document processor
    try:
        print("\nLoading with DocumentProcessor...")
        documents = processor.load_documents(file_path=yaml_path)
        print(f"Successfully loaded {len(documents)} document(s) from YAML file.")
        
        # Process the documents
        chunks = processor.split_documents(documents)
        print(f"Split into {len(chunks)} chunks.")
        
        # Display the chunks
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print("-" * 50)
            print(chunk.page_content)
            print("-" * 50)
            print(f"Metadata: {chunk.metadata}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_yaml_loading()
