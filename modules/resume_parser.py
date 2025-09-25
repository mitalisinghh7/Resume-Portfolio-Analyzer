import pdfplumber
import docx

def extract_text_from_pdf(file):
    """Extract text from a PDF file while keeping line breaks."""
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def extract_text_from_docx(file):
    """Extract text from a DOCX file."""
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
