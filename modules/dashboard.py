import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from keyword_analysis import analyze_keywords
from feedback import generate_feedback
from ats_score import calculate_ats_score
from ui_helpers import (display_resume_preview, display_keyword_analysis, display_feedback, show_summary, load_job_roles, select_job_role, display_portfolio_feedback, show_wordcloud)
from report_generator import generate_pdf_report
from portfolio_analyzer import analyze_github_profile
from storage_manager import (init_db, save_analysis, get_user_history, get_leaderboard, recalc_all_points)
from nlp_analysis import extract_keywords, generate_wordcloud_bytes, get_top_skills, get_skill_frequencies, calculate_skill_match_percentage
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

init_db()
try:
    recalc_all_points()
except Exception:
    pass

st.set_page_config(page_title="Resume & Portfolio Analyzer", layout="wide")
st.title("🎓 Resume & Portfolio Analyzer")
st.write("Welcome! Upload your resume to get started.")

for k in ["resume_text", "role", "result", "feedback", "ats_score", "last_saved_profile", "portfolio_data"]:
    if k not in st.session_state:
        st.session_state[k] = None

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
        st.session_state["resume_text"] = resume_text
        display_resume_preview(resume_text)

        job_roles = load_job_roles()
        if job_roles:
            role, keywords = select_job_role(job_roles)
            st.session_state["role"] = role
            st.write(f"📌 Selected Role: **{role}**")

            # keyword analysis
            result = analyze_keywords(resume_text, keywords)
            st.session_state["result"] = result
            display_keyword_analysis(result)

            found = result.get("found", [])
            missing = result.get("missing", [])
            feedback = generate_feedback(found, missing)
            st.session_state["feedback"] = feedback
            display_feedback(feedback)

            show_summary(result)

            # ats score
            try:
                ats_score = calculate_ats_score(resume_text, role)
                st.session_state["ats_score"] = ats_score
                st.subheader("📊 ATS Score")
                st.progress(int(ats_score))
                st.write(f"⭐ Your resume scored **{ats_score}/100** for the role: **{role}**")
            except Exception as e:
                st.error(f"Could not compute ATS score: {e}")

            st.markdown("---")
            st.subheader("🧠 NLP Insights")

            try:
                top_keywords = extract_keywords(resume_text, top_n=40)
                if top_keywords:
                    st.write("**Top keywords (by frequency):**", ", ".join(top_keywords[:20]))
                else:
                    st.info("No prominent keywords found.")
            except Exception as e:
                st.warning(f"Keyword extraction failed: {e}")

            # generate wordcloud bytes
            wc_bytes = None
            try:
                wc_bytes = generate_wordcloud_bytes(resume_text)
            except Exception:
                wc_bytes = None

            # show wordcloud
            if wc_bytes:
                show_wordcloud(wc_bytes, title="🌥️ Resume WordCloud")
            else:
                st.info("WordCloud unavailable (install 'wordcloud' package to enable).")

            st.markdown("---")
            st.subheader("📊 Top 5 Most Frequent Skills")
            try:
                top_skills = get_top_skills(resume_text, top_n=5)
                if top_skills:
                    st.write(", ".join([s.capitalize() for s in top_skills]))
                else:
                    st.info("No top skills found.")
            except Exception as e:
                st.warning(f"Top skills extraction failed: {e}")

            # skill frequency table and chart
            st.markdown("---")
            st.subheader("💪 Skill Frequency Strength")

            try:
                skill_df = get_skill_frequencies(resume_text)
                if not skill_df.empty:
                    st.dataframe(skill_df)

                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.barh(skill_df["Skill"], skill_df["Count"])
                    ax.invert_yaxis()
                    ax.set_xlabel("Frequency")
                    ax.set_ylabel("Skill")
                    ax.set_title("Skill Strength in Resume")
                    st.pyplot(fig)
                else:
                    st.info("No technical skills detected for frequency analysis.")
            except Exception as e:
                st.warning(f"Skill frequency analysis failed: {e}")

            # skill match %
            st.markdown("---")
            st.subheader("🔗 Skill Match Percentage")

            try:
                percent, matched_count, total_required, matched_list = calculate_skill_match_percentage(resume_text, keywords)
                st.metric(label="Match (%)", value=f"{percent}%")
                st.progress(int(percent))
                st.write(f"Matched {matched_count} out of {total_required} required keywords for **{role}**.")
                if matched_list:
                    st.write("Matched keywords:", ", ".join(matched_list))
                else:
                    st.info("No required keywords were matched in the resume.")

                # combined insights
                from ui_helpers import display_resume_insights
                from nlp_analysis import calculate_skill_coverage

                display_resume_insights(
                    match_percent=percent,
                    ats_score=st.session_state.get("ats_score", 0),
                    role=role,
                    missing_keywords=result.get("missing", [])
                )

                # skill coverage summary
                st.markdown("### 📋 Skill Coverage Summary")
                found_count, missing_count, coverage = calculate_skill_coverage(resume_text, keywords)
                st.write(f"- ✅ Found Skills: {found_count}")
                st.write(f"- ❌ Missing Skills: {missing_count}")
                st.write(f"- 📊 Coverage: {coverage}%")

            except Exception as e:
                st.warning(f"Could not compute skill match or insights: {e}")

# portfolio analyzer
st.markdown("---")
st.header("🌐 Portfolio Analyzer")
st.write("Enter your GitHub username to analyze your public portfolio.")
username = st.text_input("GitHub Username", placeholder="e.g., torvalds")

if username:
    with st.spinner("Fetching GitHub data..."):
        data = analyze_github_profile(username)

    if "error" in data:
        st.error(data["error"])
    else:
        st.success(f"✅ GitHub data fetched for **{data['username']}**")
        st.session_state["portfolio_data"] = data

        st.subheader("📊 Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🧰 Repositories", data["repositories"])
        with col2:
            st.metric("👥 Followers", data["followers"])
        with col3:
            st.metric("🔥 Contributions", data["contributions"])

        display_portfolio_feedback(data.get("feedback", data.get("feedback_text", [])))

        already_saved = st.session_state.get("last_saved_profile")
        if already_saved != data["username"]:
            try:
                save_analysis(
                    username=data["username"],
                    role=st.session_state.get("role", "N/A"),
                    ats_score=st.session_state.get("ats_score", 0),
                    repos=data["repositories"],
                    followers=data["followers"],
                    contributions=data["contributions"]
                )
                st.session_state["last_saved_profile"] = data["username"]
            except sqlite3.OperationalError as exc:
                st.error(f"Database error while saving analysis: {exc}")
            except Exception as exc:
                st.warning(f"⚠️ Could not save data: {exc}")
        else:
            st.info("Profile data already saved in this session (to avoid duplicates).")

        if st.button("📄 Export combined PDF report"):
            with st.spinner("Generating PDF..."):
                filename = generate_pdf_report(
                    role=st.session_state.get("role", "N/A"),
                    result=st.session_state.get("result", {"found": [], "missing": []}),
                    feedback=st.session_state.get("feedback", []),
                    ats_score=st.session_state.get("ats_score", 0),
                    portfolio_data=data
                )
            st.success("✅ PDF report generated successfully!")
            with open(filename, "rb") as pdf_file:
                st.download_button("⬇️ Download Report", data=pdf_file, file_name=filename, mime="application/pdf")

        # progress history
        st.markdown("---")
        st.subheader("📈 Progress History")
        try:
            history = get_user_history(username)
        except sqlite3.OperationalError as exc:
            st.error(f"Database error while fetching history: {exc}")
            history = []
        except Exception as exc:
            st.warning(f"Could not fetch history: {exc}")
            history = []

        if history:
            df = pd.DataFrame(history, columns=["Role", "ATS Score", "Repositories", "Followers", "Contributions", "Points", "Date"])
            st.dataframe(df)

            st.markdown("#### ATS Score Trend")
            fig, ax = plt.subplots(figsize=(6, 4))
            try:
                df["Date"] = pd.to_datetime(df["Date"])
            except Exception:
                pass
            ax.plot(df["Date"], df["ATS Score"], marker="o", linestyle="-", color="royalblue", linewidth=2)
            ax.set_xlabel("Date")
            ax.set_ylabel("ATS Score")
            ax.set_title("ATS Score Over Time")
            plt.xticks(rotation=45)
            ax.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("No progress history yet — analyze a resume to start tracking your growth!")

        # leaderboard
        st.markdown("---")
        st.header("🏆 Leaderboard")
        try:
            leaderboard = get_leaderboard()
        except Exception as exc:
            st.error(f"Could not load leaderboard: {exc}")
            leaderboard = []

        if leaderboard:
            leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Avg ATS Score", "Total Contributions", "Total Points"])
            leaderboard_df.index = leaderboard_df.index + 1
            st.dataframe(leaderboard_df)
        else:
            st.info("No leaderboard data yet!")
        st.markdown("---")
        st.subheader("🧹 Manage Your Data")
        if st.button("Clear My History"):
            conn = sqlite3.connect("analysis_history.db")
            c = conn.cursor()
            c.execute("DELETE FROM history WHERE username=?", (username,))
            conn.commit()
            conn.close()
            st.session_state["last_saved_profile"] = None
            st.success("✅ History cleared successfully!")