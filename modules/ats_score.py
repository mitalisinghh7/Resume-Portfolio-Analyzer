import json
import os

# Load job descriptions from JSON
def load_job_descriptions():
    file_path = os.path.join("data", "job_description", "job_descriptions.json")
    with open(file_path, "r") as f:
        job_data = json.load(f)
    return job_data

# Calculate ATS score for a single job
def calculate_ats_score(resume_text, job_title):
    job_data = load_job_descriptions()
    keywords = job_data.get(job_title, [])
    if not keywords:
        return 0