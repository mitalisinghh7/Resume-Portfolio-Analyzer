import streamlit as st
import json
import os

def load_job_roles(json_file="job_descriptions.json"):
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, json_file)
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Job descriptions file not found!")
        return {}
    except Exception as e:
        st.error(f"⚠️ Could not load job roles: {e}")
        return {}

def select_job_role(job_roles: dict):
    st.subheader("💼 Select Job Role for Analysis")
    role = st.selectbox("Choose a job role:", list(job_roles.keys()))
    return role, job_roles[role]

def display_resume_preview(resume_text: str):
    st.subheader("📄 Extracted Resume Text (Preview)")
    st.text_area("Here’s the extracted text:", resume_text, height=300)

def display_keyword_analysis(result: dict):
    st.subheader("🔎 Keyword Analysis")
    found = ", ".join(result['found']) if result['found'] else "None"
    missing = ", ".join(result['missing']) if result['missing'] else "None"
    st.markdown(f"✅ **Found Keywords:** {found}")
    st.markdown(f"❌ **Missing Keywords:** {missing}")

def display_feedback(feedback):

    st.subheader("📝 Resume Feedback")
    if isinstance(feedback, list):
        for line in feedback:
            st.markdown(f"- {line}")
    else:
        st.markdown(feedback)

def show_summary(result: dict):
    st.subheader("📊 Skills Summary")
    st.write(f"- Found: {len(result['found'])}")
    st.write(f"- Missing: {len(result['missing'])}")

def display_portfolio_feedback(feedback):
    st.subheader("💬 Portfolio Feedback")
    if isinstance(feedback, list):
        for line in feedback:
            st.markdown(f"- {line}")
    else:
        st.write(feedback)

def show_wordcloud(image_bytes=None):

    st.subheader("🖼️ Word Cloud (resume strengths)")
    if image_bytes:
        st.image(image_bytes)
    else:
        st.info("Word cloud will appear here once NLP analysis is run.")