import streamlit as st
import json

def load_job_roles(json_file="job_descriptions.json"):
    """Load job roles and their keywords from a JSON file."""
    try:
        with open(json_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Job descriptions file not found!")
        return {}

def select_job_role(job_roles: dict):
    """Show a dropdown to select a job role and return its keywords."""
    st.subheader("💼 Select Job Role for Analysis")
    role = st.selectbox("Choose a job role:", list(job_roles.keys()))
    return role, job_roles[role]

def display_resume_preview(resume_text: str):
    """Show extracted resume text in a scrollable box."""
    st.subheader("📄 Extracted Resume Text (Preview)")
    st.text_area("Here’s the extracted text:", resume_text, height=300)

def display_keyword_analysis(result: dict):
    """Show found and missing keywords from resume analysis."""
    st.subheader("🔎 Keyword Analysis")

    found = ", ".join(result['found']) if result['found'] else "None"
    missing = ", ".join(result['missing']) if result['missing'] else "None"

    st.markdown(f"✅ **Found Keywords:** {found}")
    st.markdown(f"❌ **Missing Keywords:** {missing}")

def display_feedback(feedback: str):
    """Show resume feedback based on keyword analysis."""
    st.subheader("📝 Resume Feedback")
    st.markdown(feedback)

def show_summary(result: dict):
    """Show a summary of found vs missing skills."""
    st.subheader("📊 Skills Summary")
    st.write(f"- Found: {len(result['found'])}")
    st.write(f"- Missing: {len(result['missing'])}")

def display_score(result: dict):
    """Show a score based on found vs total keywords."""
    total = len(result['found']) + len(result['missing'])
    score = (len(result['found']) / total) * 100 if total > 0 else 0

    st.subheader("⭐ Resume Score")
    st.progress(int(score))
    st.write(f"Your resume scored **{int(score)} / 100** based on keyword coverage.")