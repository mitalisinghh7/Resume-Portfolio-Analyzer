import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from keyword_analysis import analyze_keywords
from feedback import generate_feedback
from ats_score import calculate_ats_score
from portfolio_analyzer import analyze_github_profile
from report_generator import generate_pdf_report
from storage_manager import init_db, save_analysis, get_user_history, get_leaderboard
from ui_helpers import load_job_roles, select_job_role, display_keyword_analysis, display_feedback, show_summary
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Resume & Portfolio Analyzer", layout="wide")
init_db()

session_vars = ["resume_text", "role", "feedback", "ats_score", "result", "username", "portfolio_data"]
for key in session_vars:
    if key not in st.session_state:
        st.session_state[key] = None

st.title("📊 Resume & Portfolio Analyzer")
st.caption("Analyze your resume, GitHub portfolio, and track progress — all in one dashboard.")

tabs = st.tabs(["📄 Resume", "🌐 Portfolio", "📈 Progress", "🏆 Leaderboard"])

with tabs[0]:
    st.header("📄 Resume Analyzer")

    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()
        resume_text = extract_text_from_pdf(uploaded_file) if file_type == "pdf" else extract_text_from_docx(uploaded_file)
        st.session_state["resume_text"] = resume_text

        st.subheader("📝 Resume Preview")
        st.text_area("Extracted Text", resume_text[:1500] + "...", height=250)

        job_roles = load_job_roles()
        role, keywords = select_job_role(job_roles)
        st.session_state["role"] = role

        if st.button("🔍 Analyze Resume"):
            result = analyze_keywords(resume_text, keywords)
            st.session_state["result"] = result

            found = result.get("found", [])
            missing = result.get("missing", [])
            feedback = generate_feedback(found, missing)
            st.session_state["feedback"] = feedback

            ats_score = calculate_ats_score(resume_text, role)
            st.session_state["ats_score"] = ats_score

            st.success(f"✅ Analysis complete for **{role}**")
            display_keyword_analysis(result)
            display_feedback(feedback)
            show_summary(result)

            st.subheader("📊 ATS Score")
            st.progress(int(ats_score))
            st.write(f"⭐ Your resume scored **{ats_score}/100**")

with tabs[1]:
    st.header("🌐 Portfolio Analyzer")
    username = st.text_input("GitHub Username:", value=st.session_state.get("username", "") or "")

    if st.button("📈 Analyze Portfolio"):
        if username:
            data = analyze_github_profile(username)
            if "error" in data:
                st.error(data["error"])
            else:
                st.session_state["username"] = username
                st.session_state["portfolio_data"] = data
                st.success(f"✅ Fetched data for **{username}**")

    if st.session_state["portfolio_data"]:
        data = st.session_state["portfolio_data"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Repositories", data["repositories"])
        c2.metric("Followers", data["followers"])
        c3.metric("Contributions", data["contributions"])

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
            st.warning(f"⚠️ Could not save portfolio data: {e}")

        st.subheader("💬 Portfolio Feedback")
        feedback_lines = []
        if int(data["repositories"]) < 5:
            feedback_lines.append("Add more repositories to showcase your work.")
        if int(data["contributions"]) < 100:
            feedback_lines.append("Increase activity — consistent commits show learning progress.")
        if int(data["followers"]) < 10:
            feedback_lines.append("Engage more with the community to build visibility.")
        if feedback_lines:
            for f in feedback_lines:
                st.write("•", f)
        else:
            st.write("✅ Your GitHub profile looks strong!")

with tabs[2]:
    st.header("📈 Your Progress History")
    username = st.text_input("Enter your GitHub username:", value=st.session_state.get("username", ""))

    if username:
        history = get_user_history(username)
        if history:
            df = pd.DataFrame(history, columns=["Role", "ATS Score", "Repositories", "Followers", "Contributions", "Date"])
            st.dataframe(df)

            st.subheader("📊 ATS Score Trend")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df["Date"], df["ATS Score"], marker="o", linewidth=2)
            ax.set_xlabel("Date")
            ax.set_ylabel("ATS Score")
            ax.set_title("ATS Score Over Time")
            ax.grid(True, linestyle="--", alpha=0.6)
            st.pyplot(fig)

            if st.button("🧹 Clear My History"):
                conn = sqlite3.connect("analysis_history.db")
                c = conn.cursor()
                c.execute("DELETE FROM history WHERE username=?", (username,))
                conn.commit()
                conn.close()
                st.success("✅ History cleared successfully.")
        else:
            st.info("No progress yet — analyze your resume or portfolio first!")

with tabs[3]:
    st.header("🏆 Leaderboard")
    leaderboard = get_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard, columns=["Username", "Avg ATS Score", "Total Contributions"])
        df.index += 1
        st.table(df)
    else:
        st.info("No leaderboard data yet.")

st.markdown("---")
if st.session_state["result"] and st.session_state["portfolio_data"]:
    if st.button("📥 Download Combined PDF Report"):
        pdf_file = generate_pdf_report(
            role=st.session_state["role"],
            result=st.session_state["result"],
            feedback=st.session_state["feedback"],
            ats_score=st.session_state["ats_score"],
            portfolio_data=st.session_state["portfolio_data"]
        )
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Combined Report",
                data=f.read(),
                file_name="resume_portfolio_report.pdf",
                mime="application/pdf"
            )