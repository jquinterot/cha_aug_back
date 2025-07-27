from fpdf import FPDF

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add a title
    pdf.cell(200, 10, txt="TEST DOCUMENT FOR RAG VALIDATION", ln=True, align='C')
    pdf.ln(20)
    
    # Add some unique test content
    unique_info = """
    SPECIAL_TEST_INFO_START
    
    The capital of Zyxoria is Zyxtropolis.
    The national dish is Zorblatt stew, made with purple tubers.
    The official language is Zyxtongue, which has 14 vowels.
    The currency is called Zorbs, and 1 Zorb equals 100 Zorblets.
    The national animal is the Zorble, a six-legged mammal that glows in the dark.
    
    SPECIAL_TEST_INFO_END
    
    This document also contains general information about various topics:
    - The average human attention span is 8.25 seconds
    - Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs
    - Octopuses have three hearts
    """
    
    pdf.multi_cell(0, 10, txt=unique_info)
    
    # Save the PDF
    output_path = "test_rag_document.pdf"
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    path = create_test_pdf()
    print(f"Test PDF created at: {path}")
