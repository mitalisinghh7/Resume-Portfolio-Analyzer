import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from keyword_analysis import analyze_keywords
from feedback import generate_feedback
from ats_score import calculate_ats_score, load_job_descriptions
from ui_helpers import (
    display_resume_preview,
    display_keyword_analysis,
    display_feedback,
    show_summary,
    display_score,
    load_job_roles,
    select_job_role,
)

st.set_page_config(page_title="Resume & Portfolio Analyzer", layout="wide")

st.title("🎓 Resume & Portfolio Analyzer")
st.write("Welcome! Upload your resume to get started.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

resume_text = ""

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type!")

    if resume_text:
        st.subheader("📄 Extracted Resume Text (Preview)")
        st.markdown(f"```\n{resume_text}\n```")

        job_roles = load_job_roles()
        if job_roles:
            role, keywords = select_job_role(job_roles)

            st.write(f"📌 Selected Role: **{role}**")
            result = analyze_keywords(resume_text, keywords)

            display_keyword_analysis(result)

            st.subheader("📝 Personalized Feedback")
            job_data = load_job_descriptions()
            keywords = job_data.get(role, [])

            found = [kw for kw in keywords if kw.lower() in resume_text.lower()]
            missing = [kw for kw in keywords if kw.lower() not in resume_text.lower()]

            feedback = generate_feedback(found, missing)
            if feedback:
                st.write(feedback)
            else:
                st.write("✅ Great job! Your resume covers most of the important keywords.")

            show_summary(result)

            ats_score = calculate_ats_score(resume_text, role)
            st.subheader("📊 ATS Score")
            st.write(f"⭐ Your resume scored **{ats_score}/100** based on keyword coverage.")