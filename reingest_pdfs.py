import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from app.services.document_service import DocumentProcessor
from app.services.vector_store_service import VectorStoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def reingest_pdfs(pdf_dir: str):
    """
    Re-ingest all PDFs from the specified directory using the enhanced document processor.
    """
    # Initialize services
    doc_processor = DocumentProcessor()
    vector_store = VectorStoreService()
    
    # Get all PDF files in the directory
    pdf_dir_path = Path(pdf_dir)
    if not pdf_dir_path.exists() or not pdf_dir_path.is_dir():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return False
    
    pdf_files = list(pdf_dir_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in directory: {pdf_dir}")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing PDF: {pdf_file.name}")
            
            # Load and process the document
            documents = doc_processor._load_pdf(str(pdf_file))
            
            if not documents:
                logger.warning(f"No content extracted from {pdf_file.name}")
                continue
            
            # Split into chunks
            chunks = doc_processor.split_documents(documents)
            
            if not chunks:
                logger.warning(f"No valid chunks created from {pdf_file.name}")
                continue
            
            logger.info(f"Adding {len(chunks)} chunks to vector store from {pdf_file.name}")
            
            # Add to vector store
            vector_store.add_documents(chunks)
            
            logger.info(f"Successfully processed {pdf_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}", exc_info=True)
            continue
    
    # Save the updated vector store
    vector_store.save()
    logger.info("Vector store updated successfully")
    return True

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get PDF directory from command line or use default
    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else "rag_pdf_data"
    
    logger.info(f"Starting PDF re-ingestion from directory: {pdf_dir}")
    
    if reingest_pdfs(pdf_dir):
        logger.info("PDF re-ingestion completed successfully")
    else:
        logger.error("PDF re-ingestion failed")
        sys.exit(1)
