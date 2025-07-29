from fpdf import FPDF
import os

def create_weird_test_pdf():
    # Create PDF object
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="Weird Test Document for RAG System", ln=True, align='C')
    pdf.ln(10)
    
    # Add some unusual content
    content = """SPECIAL_TEST_INFO_START

WEIRD_ENTRY_1: The Quantum Fluffernutter is a theoretical particle that tastes like peanut butter.
WEIRD_ENTRY_2: In the year 3033, time-traveling llamas will establish the first intergalactic postal service.
WEIRD_ENTRY_3: The lost city of Zyxoria was actually made of sentient cheese that could predict the weather.
WEIRD_ENTRY_4: The rarest element, Unobtainium-999, is only found in the dreams of sleeping robots.
WEIRD_ENTRY_5: The Great Spaghetti Monster's favorite programming language is Python, but it types with meatballs.

SPECIAL_TEST_INFO_END

Additional weird facts:
- The average cloud weighs about 1.1 million pounds (but don't worry, they're very fluffy)
- Bananas are berries, but strawberries aren't
- A group of flamingos is called a 'flamboyance'
- Octopuses have three hearts and blue blood
- The shortest war in history was between Britain and Zanzibar in 1896 (38-45 minutes)

This document contains intentionally strange and unique information to test the RAG system's ability to handle unusual queries and retrieve specific information."""
    
    # Add multi-cell text
    pdf.multi_cell(0, 10, txt=content)
    
    # Save the PDF
    output_path = "weird_test_document.pdf"
    pdf.output(output_path)
    
    print(f"Created weird test PDF at: {os.path.abspath(output_path)}")
    return os.path.abspath(output_path)

if __name__ == "__main__":
    create_weird_test_pdf()
