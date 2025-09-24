import PyPDF2
import docx

def extract_text_from_pdf(file):
    """Extracts text from a PDF file or file-like object."""
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    """Extracts text from a DOCX file or file-like object."""
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
