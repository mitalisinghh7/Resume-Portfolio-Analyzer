from modules.resume_parser import extract_text_from_pdf, extract_text_from_docx

print("🎓 Welcome to Resume & Portfolio Analyzer!")

# Example resumes for testing
pdf_resume = "data/resumes/sample_resume.pdf"
docx_resume = "data/resumes/sample_resume.docx"

try:
    print("\n📄 Extracted text from PDF:")
    print(extract_text_from_pdf(pdf_resume))

    print("\n📄 Extracted text from DOCX:")
    print(extract_text_from_docx(docx_resume))

except FileNotFoundError:
    print("⚠️ Please add sample resumes inside data/resumes/ folder to test this feature.")
