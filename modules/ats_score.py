import json
import os

def load_job_descriptions():
    """Load job descriptions JSON using project root path."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "job_descriptions", "job_descriptions.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job descriptions file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        job_data = json.load(f)
    return job_data

def calculate_ats_score(resume_text, job_title):
    """Calculate ATS score for a specific job role."""
    job_data = load_job_descriptions()
    keywords = job_data.get(job_title, [])
    if not keywords:
        return 0
    found = sum(1 for kw in keywords if kw.lower() in resume_text.lower())
    score = (found / len(keywords)) * 100
    return round(score, 2)

def get_all_scores(resume_text):
    """Get ATS scores for all roles."""
    job_data = load_job_descriptions()
    scores = {}
    for job in job_data:
        scores[job] = calculate_ats_score(resume_text, job)
    return scores