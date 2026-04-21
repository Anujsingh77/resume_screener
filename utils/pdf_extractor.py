"""
PDF text extraction using PyMuPDF (fitz).
Fallback to pdfplumber if needed.
"""

def extract_text_from_pdf(filepath: str) -> str:
    """Extract all text from a PDF file."""
    text = ""

    # Primary: PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        doc.close()
        if text.strip():
            return text.strip()
    except ImportError:
        pass

    # Fallback: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        pass

    return "Could not extract text from PDF. Please ensure PyMuPDF or pdfplumber is installed."
