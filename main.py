import os
from modules.resume_parser import extract_text_from_pdf, extract_text_from_docx
from modules.keyword_analysis import analyze_keywords
from modules.ats_score import get_all_scores
from modules.portfolio_analyzer import analyze_github_profile

resume_file = "data/resumes/sample_resume.pdf"

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

print("\n🔎 Keyword Analysis")
print("✅ Keywords Found:", result["found"])
print("❌ Keywords Missing:", result["missing"])

print("\n📊 ATS Scores by Job Role")
scores = get_all_scores(resume_text)
for job, score in scores.items():
    print(f"- {job}: {score}%")

print("\n🌐 Portfolio Analysis (GitHub)")
github_username = "mitalisinghh7"
github_stats = analyze_github_profile(github_username)

if "error" in github_stats:
    print("❌", github_stats["error"])
else:
    print(f"GitHub Username: {github_stats['username']}")
    print(f"Repositories: {github_stats['repositories']}")
    print(f"Followers: {github_stats['followers']}")
    print(f"Contributions (this year): {github_stats['contributions']}")