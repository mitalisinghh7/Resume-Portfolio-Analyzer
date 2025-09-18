from modules.resume_parser import extract_text_from_pdf, extract_text_from_docx
from modules.keyword_analysis import analyze_keywords

pdf_path = "data/resumes/sample_resume.pdf"
docx_path = "data/resumes/sample_resume.docx"

resume_text = extract_text_from_pdf(pdf_path)

keywords = ["Python", "Java", "SQL", "Machine Learning", "Django", "MERN"]

# Run keyword analysis
result = analyze_keywords(resume_text, keywords)

# Print output
print("✅ Keywords Found:", result["found"])
print("❌ Keywords Missing:", result["missing"])