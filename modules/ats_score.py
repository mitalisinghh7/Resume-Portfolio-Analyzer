import json
import os

def load_job_descriptions():
    file_path = os.path.join("data", "job_descriptions", "job_descriptions.json")
    with open(file_path, "r") as f:
        job_data = json.load(f)
    return job_data

def calculate_ats_score(resume_text, job_title):
    job_data = load_job_descriptions()
    keywords = job_data.get(job_title, [])
    if not keywords:
        return 0
    found = sum(1 for kw in keywords if kw.lower() in resume_text.lower())
    score = (found / len(keywords)) * 100
    return round(score, 2)

def get_all_scores(resume_text):
    job_data = load_job_descriptions()
    scores = {}
    for job in job_data:
        scores[job] = calculate_ats_score(resume_text, job)
    return scores