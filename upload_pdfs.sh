#!/bin/bash

# Set the directory containing the PDFs
PDF_DIR="rag_pdf_data"

# API endpoint
API_URL="http://localhost:8000/api/v1/rag/upload"

# Check if the directory exists
if [ ! -d "$PDF_DIR" ]; then
  echo "Error: Directory $PDF_DIR does not exist."
  exit 1
fi

# Loop through all PDF files in the directory
for pdf_file in "$PDF_DIR"/*.pdf; do
  if [ -f "$pdf_file" ]; then
    echo "Uploading $pdf_file..."
    curl -X POST "$API_URL" \
      -H "accept: application/json" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@$pdf_file;type=application/pdf"
    echo -e "\n---\n"
  fi
done

echo "All PDFs have been uploaded."
