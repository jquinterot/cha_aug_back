import os
import requests
from pathlib import Path

# Configuration
UPLOAD_URL = "http://localhost:8000/api/v1/rag/upload"
PDF_DIR = "rag_pdf_data"

def upload_pdf(file_path):
    """Upload a single PDF file to the RAG service."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post(UPLOAD_URL, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error uploading {file_path}: {str(e)}")
        return None

def main():
    # Get all PDF files in the directory
    pdf_files = list(Path(PDF_DIR).glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {PDF_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to upload")
    
    # Upload each PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"Uploading {i}/{len(pdf_files)}: {pdf_file.name}...")
        result = upload_pdf(pdf_file)
        if result:
            print(f"  Success: {result}")
        else:
            print(f"  Failed to upload {pdf_file.name}")
    
    print("\nUpload process completed!")

if __name__ == "__main__":
    main()
