import os
from modules.resume_parser import extract_text_from_pdf, extract_text_from_docx
from modules.keyword_analysis import analyze_keywords

resume_file = "data/resumes/sample_resume.pdf"  # 👈 change only the filename

if not os.path.exists(resume_file):
    raise FileNotFoundError(f"File not found: {resume_file}")

if resume_file.endswith(".pdf"):
    resume_text = extract_text_from_pdf(resume_file)
elif resume_file.endswith(".docx"):
    resume_text = extract_text_from_docx(resume_file)
else:
    raise ValueError("Unsupported file format. Use PDF or DOCX.")

keywords = ["Python", "Java", "SQL", "Machine Learning", "Django", "MERN"]

result = analyze_keywords(resume_text, keywords)

print("✅ Keywords Found:", result["found"])
print("❌ Keywords Missing:", result["missing"])
