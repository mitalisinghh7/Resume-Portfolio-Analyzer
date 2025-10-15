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
from wordcloud import WordCloud
import sqlite3
from datetime import datetime

init_db()

st.set_page_config(page_title="Resume & Portfolio Analyzer", layout="wide")
st.title("🎓 Resume & Portfolio Analyzer")
st.write("Welcome! Upload your resume to get started.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
resume_text = ""
username = ""

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

            try:
                ats_score = calculate_ats_score(resume_text, role)
                st.subheader("📊 ATS Score")
                st.progress(int(ats_score))
                st.write(f"⭐ Your resume scored **{ats_score}/100** for the role: **{role}**")
            except Exception as e:
                st.error(f"Could not compute ATS score: {e}")

            if found:
                st.subheader("🌟 Strengths Word Cloud")
                wordcloud_text = " ".join(found)
                wc = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wc, interpolation="bilinear")
                ax_wc.axis("off")
                st.pyplot(fig_wc)

st.markdown("---")
st.header("🌐 Portfolio Analyzer")
username = st.text_input("GitHub Username", placeholder="e.g., torvalds")

if username:
    with st.spinner("Fetching GitHub data..."):
        data = analyze_github_profile(username)

    if "error" in data:
        st.error(data["error"])
    else:
        st.success(f"✅ GitHub data fetched for **{data['username']}**")

        st.subheader("📊 Portfolio Summary")
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
                role=role if 'role' in locals() else "N/A",
                ats_score=ats_score if 'ats_score' in locals() else 0,
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

        st.subheader("🌟 GitHub Highlights Word Cloud")
        gh_words = []
        if int(data["repositories"]) > 0:
            gh_words.append("Repositories")
        if int(data["followers"]) > 0:
            gh_words.append("Followers")
        if int(data["contributions"]) > 0:
            gh_words.append("Contributions")

        if gh_words:
            gh_wc_text = " ".join(gh_words)
            gh_wc = WordCloud(width=800, height=400, background_color="white").generate(gh_wc_text)
            fig_gh, ax_gh = plt.subplots(figsize=(10, 5))
            ax_gh.imshow(gh_wc, interpolation="bilinear")
            ax_gh.axis("off")
            st.pyplot(fig_gh)

        st.markdown("---")
        st.subheader("📈 Progress History")
        history = get_user_history(username)
        if history:
            df = pd.DataFrame(history, columns=["Role", "ATS Score", "Repositories", "Followers", "Contributions", "Date"])
            st.dataframe(df)

            st.markdown("#### ATS Score Trend")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df["Date"], df["ATS Score"], marker="o", linestyle="-", color="royalblue", linewidth=2)
            ax.set_xlabel("Date")
            ax.set_ylabel("ATS Score")
            ax.set_title("ATS Score Over Time")
            plt.xticks(rotation=45)
            ax.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("No progress history yet — analyze a resume to start tracking your growth!")

        st.markdown("---")
        st.header("🏆 Leaderboard")
        leaderboard = get_leaderboard()
        if leaderboard:
            st.write("Top performers across Codeunia:")
            st.table(
                {
                    "Rank": [i + 1 for i in range(len(leaderboard))],
                    "Username": [row[0] for row in leaderboard],
                    "Avg ATS Score": [round(row[1], 2) for row in leaderboard],
                    "Total Contributions": [row[2] for row in leaderboard],
                }
            )
        else:
            st.info("No leaderboard data yet — as more users analyze their resumes, this will fill up!")

        st.markdown("---")
        st.subheader("🧹 Manage Your Data")
        if st.button("Clear My History"):
            conn = sqlite3.connect("analysis_history.db")
            c = conn.cursor()
            c.execute("DELETE FROM history WHERE username=?", (username,))
            conn.commit()
            conn.close()

st.markdown("---")
st.subheader("📝 Generate PDF Report")
if st.button("Download My Report"):
    try:
        report_path = generate_pdf_report(
            username=username if username else "Guest",
            resume_text=resume_text if resume_text else "N/A",
            role=role if 'role' in locals() else "N/A",
            ats_score=ats_score if 'ats_score' in locals() else 0,
            keyword_result=result if 'result' in locals() else {},
            portfolio_data=data if 'data' in locals() else {}
        )
        with open(report_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name=f"{username}_analysis_report.pdf",
                mime="application/pdf"
            )
        st.success("✅ PDF report generated successfully!")
    except Exception as e:
        st.error(f"Could not generate report: {e}")
