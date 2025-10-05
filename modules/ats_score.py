import json
import os

DEFAULT_JOB_DATA = {
    "Python Developer": ["Python", "Django", "Flask", "SQL", "APIs"],
    "Java Developer": ["Java", "Spring Boot", "Hibernate", "Microservices", "SQL"],
    "Data Scientist": ["Python", "Machine Learning", "Pandas", "Numpy", "SQL", "Deep Learning"],
    "Full Stack Developer": ["JavaScript", "React", "Node.js", "MongoDB", "Express", "MERN"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "Scikit-learn", "Machine Learning", "Deep Learning"]
}

def load_job_descriptions():

    current_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        os.path.join(current_dir, "job_descriptions.json"),
        os.path.join(current_dir, "data", "job_descriptions.json"),
        os.path.join(current_dir, "data", "job_descriptions", "job_descriptions.json"),
        os.path.join(os.path.dirname(current_dir), "data", "job_descriptions", "job_descriptions.json"),
        os.path.join(os.path.dirname(current_dir), "job_descriptions.json"),]

    for p in candidates:
        p = os.path.normpath(p)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    pass

    target = os.path.join(current_dir, "job_descriptions.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_JOB_DATA, f, indent=4)

    return DEFAULT_JOB_DATA

def calculate_ats_score(resume_text, job_title):
    """Calculate ATS score for a specific job role (0-100)."""
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