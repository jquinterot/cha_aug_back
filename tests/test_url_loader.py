import sys
from pathlib import Path
from typing import List

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.document_service import DocumentProcessor

def test_url_loading():
    """Test loading and processing content from various URLs."""
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Test with different types of URLs
    test_urls = [
        # A Wikipedia article (web page)
        "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        
        # A direct link to a PDF
        "https://arxiv.org/pdf/2005.11401",
        
        # A direct link to a text file
        "https://www.gutenberg.org/files/1342/1342-0.txt",  # Pride and Prejudice
        
        # A JSON API endpoint
        "https://api.github.com/repos/langchain-ai/langchain/releases/latest",
        
        # A YAML file from a GitHub repository
        "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    ]
    
    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"Testing URL: {url}")
        print("="*80)
        
        try:
            # Load the URL content
            print("\nLoading content...")
            documents = processor.load_documents(urls=[url])
            print(f"Successfully loaded {len(documents)} document(s) from URL.")
            
            # Process the documents
            chunks = processor.split_documents(documents)
            print(f"Split into {len(chunks)} chunks.")
            
            # Display the first chunk
            if chunks:
                print("\nFirst chunk preview:")
                print("-" * 50)
                preview = chunks[0].page_content[:500]  # Show first 500 chars
                print(preview + ("..." if len(chunks[0].page_content) > 500 else ""))
                print("-" * 50)
                print(f"Source: {chunks[0].metadata.get('source', 'Unknown')}")
                print(f"Content type: {chunks[0].metadata.get('content_type', 'Unknown')}")
                
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_url_loading()
