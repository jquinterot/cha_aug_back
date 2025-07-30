import os
import pickle
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.absolute())
sys.path.append(project_root)

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_vector_store(file_path):
    """Inspect the contents of a vector store file"""
    try:
        logger.info(f"Inspecting vector store file: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # in MB
        logger.info(f"File size: {file_size:.2f} MB")
        
        # Load the vector store
        with open(file_path, "rb") as f:
            vector_store = pickle.load(f)
        
        # Print basic information
        logger.info(f"Vector store type: {type(vector_store).__name__}")
        
        # Check if it's a FAISS index
        if hasattr(vector_store, 'index') and hasattr(vector_store.index, 'ntotal'):
            logger.info(f"Number of vectors: {vector_store.index.ntotal}")
            
            # Try to get some sample documents if available
            if hasattr(vector_store, 'docstore') and hasattr(vector_store.docstore, '_dict'):
                docs = list(vector_store.docstore._dict.values())
                logger.info(f"Number of documents in docstore: {len(docs)}")
                
                if docs:
                    logger.info("Sample documents:")
                    for i, doc in enumerate(docs[:3]):  # Show first 3 docs
                        if hasattr(doc, 'page_content'):
                            preview = doc.page_content[:200].replace('\n', ' ').strip()
                            source = doc.metadata.get('source', 'unknown')
                            logger.info(f"  {i+1}. Source: {source}")
                            logger.info(f"     Content: {preview}...")
                        else:
                            logger.info(f"  {i+1}. [No page_content attribute]")
            
            return True
        else:
            logger.warning("Vector store doesn't have expected FAISS index structure")
            return False
            
    except Exception as e:
        logger.error(f"Error inspecting vector store: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Path to the vector store directory
    vector_store_dir = os.path.join(project_root, "vector_store")
    
    # Find all .pkl files in the vector store directory
    pkl_files = [f for f in os.listdir(vector_store_dir) if f.endswith('.pkl')]
    
    if not pkl_files:
        logger.warning("No .pkl files found in the vector store directory")
        sys.exit(1)
    
    # Inspect each .pkl file
    for pkl_file in pkl_files:
        file_path = os.path.join(vector_store_dir, pkl_file)
        print("\n" + "="*80)
        print(f"INSPECTING: {pkl_file}")
        print("="*80)
        inspect_vector_store(file_path)
        print("="*80 + "\n")
