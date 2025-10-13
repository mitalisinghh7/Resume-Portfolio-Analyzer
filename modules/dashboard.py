import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from keyword_analysis import analyze_keywords
from feedback import generate_feedback
from ats_score import calculate_ats_score
from ui_helpers import (display_resume_preview, display_keyword_analysis, display_feedback, show_summary, load_job_roles, select_job_role)
from report_generator import generate_pdf_report
from portfolio_analyzer import analyze_github_profile
from storage_manager import init_db, save_analysis, get_user_history, get_leaderboard
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import io

init_db()

st.set_page_config(page_title="Codeunia Resume & Portfolio Analyzer", layout="wide")

if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "feedback" not in st.session_state:
    st.session_state["feedback"] = None
if "ats_score" not in st.session_state:
    st.session_state["ats_score"] = None
if "result" not in st.session_state:
    st.session_state["result"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "📄 Resume Analyzer", "🌐 Portfolio", "📈 Progress", "🏆 Leaderboard"])

if page == "🏠 Home":
    st.title("🎓 Codeunia Resume & Portfolio Analyzer")
    st.write("""
    Welcome to **Codeunia’s Resume & Portfolio Analyzer** 🎯  
    Upload your resume, analyze your GitHub portfolio, and track your growth — all in one place!
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.markdown("---")
    st.write("Use the sidebar to get started →")

elif page == "📄 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
        resume_text = ""

        if file_type == "pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif file_type == "docx":
            resume_text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file type!")

        if resume_text:
            st.session_state["resume_text"] = resume_text
            display_resume_preview(resume_text)

            job_roles = load_job_roles()
            if job_roles:
                role, keywords = select_job_role(job_roles)
                st.session_state["role"] = role
                st.write(f"📌 Selected Role: **{role}**")

                result = analyze_keywords(resume_text, keywords)
                st.session_state["result"] = result
                display_keyword_analysis(result)

                found = result.get("found", [])
                missing = result.get("missing", [])
                feedback = generate_feedback(found, missing)
                st.session_state["feedback"] = feedback
                display_feedback(feedback)

                show_summary(result)

                try:
                    ats_score = calculate_ats_score(resume_text, role)
                    st.session_state["ats_score"] = ats_score
                    st.subheader("📊 ATS Score")
                    st.progress(int(ats_score))
                    st.write(f"⭐ Your resume scored **{ats_score}/100** for the role: **{role}**")
                except Exception as e:
                    st.error(f"Could not compute ATS score: {e}")

                st.markdown("---")
                if st.button("📥 Generate PDF Report"):
                    pdf_bytes = generate_pdf_report(
                        resume_text,
                        role,
                        result,
                        feedback,
                        ats_score
                    )
                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.download_button(
                        label="⬇️ Download Resume Report",
                        data=pdf_bytes,
                        file_name=f"{role}_analysis_report.pdf",
                        mime="application/pdf"
                    )

elif page == "🌐 Portfolio":
    st.title("🌐 Portfolio Analyzer")
    username = st.text_input("Enter your GitHub Username", placeholder="e.g., torvalds")

    if username:
        st.session_state["username"] = username
        with st.spinner("Fetching GitHub data..."):
            data = analyze_github_profile(username)

        if "error" in data:
            st.error(data["error"])
        else:
            st.success(f"✅ GitHub data fetched for **{data['username']}**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🧰 Repositories", data["repositories"])
            with col2:
                st.metric("👥 Followers", data["followers"])
            with col3:
                st.metric("🔥 Contributions", data["contributions"])

            try:
                save_analysis(
                    username=data["username"],
                    role=st.session_state.get("role", "N/A"),
                    ats_score=st.session_state.get("ats_score", 0),
                    repos=data["repositories"],
                    followers=data["followers"],
                    contributions=data["contributions"]
                )
            except Exception as e:
                st.warning(f"⚠️ Could not save data: {e}")

            st.markdown("### 💬 Portfolio Feedback")
            feedback_lines = []
            try:
                if int(data["repositories"]) < 5:
                    feedback_lines.append("Add more repositories to showcase your work.")
                if int(data["contributions"]) < 100:
                    feedback_lines.append("Increase activity — consistent commits show learning progress.")
                if int(data["followers"]) < 10:
                    feedback_lines.append("Engage with the community more to build visibility.")
            except ValueError:
                feedback_lines.append("Some GitHub stats couldn’t be parsed correctly.")

            if feedback_lines:
                for line in feedback_lines:
                    st.write(f"- {line}")
            else:
                st.write("✅ Your GitHub profile looks strong — keep contributing regularly!")

elif page == "📈 Progress":
    st.title("📈 Your Progress History")
    username = st.text_input("Enter your GitHub Username", placeholder="e.g., torvalds")

    if username:
        history = get_user_history(username)
        if history:
            df = pd.DataFrame(history, columns=["Role", "ATS Score", "Repositories", "Followers", "Contributions", "Date"])
            st.dataframe(df)

            st.markdown("#### 📊 ATS Score Trend")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df["Date"], df["ATS Score"], marker="o", color="royalblue", linewidth=2)
            ax.set_xlabel("Date")
            ax.set_ylabel("ATS Score")
            ax.set_title("ATS Score Over Time")
            plt.xticks(rotation=45)
            ax.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)

            st.markdown("---")
            if st.button("🧹 Clear My History"):
                conn = sqlite3.connect("analysis_history.db")
                c = conn.cursor()
                c.execute("DELETE FROM history WHERE username=?", (username,))
                conn.commit()
                conn.close()
                st.success("✅ Your history has been cleared successfully!")
        else:
            st.info("No progress yet — analyze a resume or portfolio to start tracking your growth!")

elif page == "🏆 Leaderboard":
    st.title("🏆 Codeunia Leaderboard")
    leaderboard = get_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard, columns=["Username", "Avg ATS Score", "Total Contributions"])
        df.index += 1
        st.table(df)
    else:
        st.info("No leaderboard data yet — as more users analyze their resumes, this will fill up!")