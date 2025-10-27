import streamlit as st
import json
import os
import io
import matplotlib.pyplot as plt

# job role
def load_job_roles(json_file: str = "job_descriptions.json"):
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, json_file)
        with open(file_path, "r", encoding="utf-8") as f:
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

# resume ui
def display_resume_preview(resume_text: str):
    st.subheader("📄 Extracted Resume Text (Preview)")
    if not resume_text:
        st.info("No resume text extracted yet.")
        return
    with st.expander("Show extracted text", expanded=False):
        st.text_area("Resume Preview", resume_text, height=320, label_visibility="collapsed")

def display_keyword_analysis(result: dict):
    st.subheader("🔎 Keyword Analysis")
    found = ", ".join(result.get('found', [])) if result.get('found') else "None"
    missing = ", ".join(result.get('missing', [])) if result.get('missing') else "None"
    st.markdown(f"✅ **Found Keywords:** {found}")
    st.markdown(f"❌ **Missing Keywords:** {missing}")

def display_feedback(feedback):
    st.subheader("📝 Resume Feedback")
    if not feedback:
        st.info("No resume feedback available yet.")
        return

    if isinstance(feedback, str):
        lines = [ln.strip() for ln in feedback.splitlines() if ln.strip()]
    elif isinstance(feedback, list):
        lines = [str(ln).strip() for ln in feedback if str(ln).strip()]
    else:
        lines = [str(feedback)]

    for line in lines:
        st.markdown(f"- {line}")

def show_summary(result: dict):
    st.subheader("📊 Skills Summary")
    found_count = len(result.get('found', []))
    missing_count = len(result.get('missing', []))
    st.write(f"- Found: {found_count}")
    st.write(f"- Missing: {missing_count}")

# portfolio ui
def display_portfolio_feedback(feedback):
    st.subheader("💬 Portfolio Feedback")
    if not feedback:
        st.info("No portfolio feedback available.")
        return

    if isinstance(feedback, str):
        lines = [l.strip() for l in feedback.splitlines() if l.strip()]
    elif isinstance(feedback, list):
        lines = [str(l).strip() for l in feedback if str(l).strip()]
    else:
        lines = [str(feedback)]

    for line in lines:
        st.markdown(f"- {line}")

# wordcloud
def show_wordcloud(image_bytes: bytes = None, title: str = "🖼️ Word Cloud (resume strengths)"):
    st.subheader(title)
    if image_bytes:
        try:
            st.image(image_bytes, use_container_width=True)
        except Exception:
            try:
                buf = io.BytesIO(image_bytes)
                st.image(buf, use_container_width=True)
            except Exception:
                st.error("Could not render word cloud image.")
    else:
        st.info("Word cloud will appear here once NLP analysis is run.")

# resume insights
def display_resume_insights(match_percent: float, ats_score: float, role: str, missing_keywords: list):
    st.markdown("---")
    st.subheader("💡 Resume Insights")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("ATS Score", f"{ats_score}/100")
        st.progress(int(ats_score))
    with col2:
        st.metric("Skill Match", f"{match_percent}%")
        st.progress(int(match_percent))

    if missing_keywords:
        st.markdown("**Suggestions for improvement:**")
        for kw in missing_keywords:
            st.markdown(f"- Add or highlight: **{kw}**")
    else:
        st.success("Your resume already covers all the key skills for this role!")

    st.info(f"Role analyzed: **{role}**")

# combined visualization
def show_combined_visualization(resume_skills: dict, github_langs: dict):
    if not resume_skills or not github_langs:
        st.info("Upload your resume and connect GitHub to view combined visualization.")
        return

    st.markdown("---")
    st.header("📊 Resume & Portfolio Combined Visualization")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resume Skill Distribution")
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(resume_skills.values(), labels=resume_skills.keys(), autopct='%1.1f%%', startangle=140)
        ax1.axis("equal")
        st.pyplot(fig1)

    with col2:
        st.subheader("GitHub Language Distribution")
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.bar(github_langs.keys(), github_langs.values())
        ax2.set_xlabel("Languages")
        ax2.set_ylabel("Lines of Code")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.markdown("✅ **Insight:** The closer the resume skill ratio matches GitHub language ratio, the stronger your profile alignment.")