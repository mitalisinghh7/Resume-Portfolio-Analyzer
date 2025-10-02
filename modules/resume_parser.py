import pdfplumber
import docx

def extract_text_from_pdf(file):
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text.append(page_text)
    return clean_text("\n".join(text))

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return clean_text(text)

def clean_text(text: str) -> str:
    """Cleanup: keep line breaks, remove extra spaces, add spacing between sections."""
    lines = [line.strip() for line in text.splitlines()]

    cleaned_lines = []
    prev_empty = False

    for line in lines:
        if line == "":
            if not prev_empty:
                cleaned_lines.append("")
            prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False

    return "\n".join(cleaned_lines).strip()