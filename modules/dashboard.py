import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from keyword_analysis import analyze_keywords
from feedback import generate_feedback
from ats_score import calculate_ats_score
from ui_helpers import (display_resume_preview, display_keyword_analysis, display_feedback, show_summary, load_job_roles, select_job_role,
                        )
from report_generator import generate_pdf_report

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
        display_resume_preview(resume_text)

        job_roles = load_job_roles()
        if job_roles:
            role, keywords = select_job_role(job_roles)

            st.write(f"📌 Selected Role: **{role}**")

            result = analyze_keywords(resume_text, keywords)
            display_keyword_analysis(result)

            found = result.get("found", [])
            missing = result.get("missing", [])
            feedback = generate_feedback(found, missing)
            display_feedback(feedback)

            show_summary(result)

            # display ATS score
            try:
                ats_score = calculate_ats_score(resume_text, role)
                st.subheader("📊 ATS Score")
                st.progress(int(ats_score))
                st.write(f"⭐ Your resume scored **{ats_score}/100** for the role: **{role}**")

                #  PDF Export
                if st.button("📄 Download PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        pdf_path = generate_pdf_report(role, found, missing, feedback, ats_score)
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Click here to download your report",
                                data=f,
                                file_name=pdf_path,
                                mime="application/pdf"
                            )

            except Exception as e:
                st.error(f"Could not compute ATS score: {e}")