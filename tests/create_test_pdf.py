from fpdf import FPDF
import os

def create_test_pdf():
    # Create PDF object
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add content
    pdf.cell(200, 10, txt="Test Document for RAG System", ln=True, align='C')
    pdf.ln(10)
    
    # Add some content
    content = """This is a test PDF document for the RAG system. 
    
It contains information about artificial intelligence and machine learning. 

Key points:
- The capital of France is Paris
- The largest planet in our solar system is Jupiter
- Water boils at 100 degrees Celsius at sea level
- The Earth's atmosphere is 78% nitrogen
- The speed of light is approximately 300,000 km/s

This document is used to test the RAG system's ability to extract and use information from PDFs."""
    
    # Add multi-cell text
    pdf.multi_cell(0, 10, txt=content)
    
    # Save the PDF
    output_path = "test_document.pdf"
    pdf.output(output_path)
    
    print(f"Created test PDF at: {os.path.abspath(output_path)}")
    return os.path.abspath(output_path)

if __name__ == "__main__":
    create_test_pdf()
