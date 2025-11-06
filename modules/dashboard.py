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
from analysis_history_manager import update_last_analysis, get_last_analysis
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

init_db()
try:
    recalc_all_points()
except Exception:
    pass

def generate_ai_summary(role, ats_score, found_skills, missing_skills, portfolio_data):
    try:
        # github top language
        top_lang = None
        if portfolio_data and "top_languages" in portfolio_data and portfolio_data["top_languages"]:
            top_lang = max(portfolio_data["top_languages"], key=portfolio_data["top_languages"].get)

        summary = "💬 “Your resume demonstrates "
        if found_skills:
            summary += f"strong proficiency in {', '.join(found_skills[:2])}"
        else:
            summary += "a growing skill foundation"

        if top_lang:
            summary += f", complemented by consistent GitHub activity in {top_lang} development"
        summary += "."

        summary += f" With an ATS score of {ats_score}, "
        if ats_score >= 75:
            summary += "your profile shows strong alignment with the role"
        elif ats_score >= 50:
            summary += "you’re moderately aligned, with potential to improve further"
        else:
            summary += "there’s room for better keyword optimization"

        if missing_skills:
            summary += f". Consider strengthening skills in {', '.join(missing_skills[:2])}"
        summary += ". Overall, your profile reflects solid technical depth and practical exposure.”"

        return summary
    except Exception:
        return "💬 “Unable to generate personalized summary insight.”"

st.set_page_config(page_title="Resume & Portfolio Analyzer", layout="wide")
st.title("🎓 Resume & Portfolio Analyzer")
st.write("Welcome! Upload your resume to get started.")

for k in ["resume_text", "role", "result", "feedback", "ats_score", "last_saved_profile", "portfolio_data"]:
    if k not in st.session_state:
        st.session_state[k] = None

# layout of tabs
tab_resume, tab_portfolio, tab_progress, tab_leaderboard = st.tabs(
    ["📄 Resume", "🌐 Portfolio", "📈 Progress", "🏆 Leaderboard"])

# resume uploader & analysis
with tab_resume:
    st.header("📄 Resume Analyzer")
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

                # nlp insights
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

                # wordcloud
                wc_bytes = None
                try:
                    wc_bytes = generate_wordcloud_bytes(resume_text)
                except Exception:
                    wc_bytes = None

                if wc_bytes:
                    show_wordcloud(wc_bytes, title="🌥️ Resume WordCloud")
                else:
                    st.info("WordCloud unavailable (install 'wordcloud' package to enable).")

                # top 5 skills
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

                    st.markdown("### 📋 Skill Coverage Summary")
                    found_count, missing_count, coverage = calculate_skill_coverage(resume_text, keywords)
                    st.write(f"- ✅ Found Skills: {found_count}")
                    st.write(f"- ❌ Missing Skills: {missing_count}")
                    st.write(f"- 📊 Coverage: {coverage}%")

                except Exception as e:
                    st.warning(f"Could not compute skill match or insights: {e}")

# portfolio analyzer
with tab_portfolio:
    st.header("🌐 Portfolio Analyzer")
    st.write("Enter your GitHub username to analyze your public portfolio.")
    username = st.text_input("GitHub Username", placeholder="e.g., torvalds")

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        uploaded_flag = "Yes" if st.session_state.get("resume_text") else "No"
        st.metric("Resume Uploaded", uploaded_flag)
    with col_r2:
        st.metric("Selected Role", st.session_state.get("role", "N/A"))
    with col_r3:
        st.metric("Last ATS Score", st.session_state.get("ats_score", 0))
    with col_r4:
        st.metric("Alignment (%)", "N/A")

    if username:
        # show last analyzed time
        last_time = get_last_analysis(username)
        st.info(f"🕒 Last analyzed on: **{last_time}**")

        with st.spinner("Fetching GitHub data..."):
            data = analyze_github_profile(username)

        if "error" in data:
            st.error(data["error"])
        else:
            st.success(f"✅ GitHub data fetched for **{data['username']}**")

            update_last_analysis(username)

            st.session_state["portfolio_data"] = data

            # small stats row
            subcol1, subcol2, subcol3 = st.columns(3)
            subcol1.metric("🧰 Repositories", data["repositories"])
            subcol2.metric("👥 Followers", data["followers"])
            subcol3.metric("🔥 Contributions", data["contributions"])

            display_portfolio_feedback(data.get("feedback", data.get("feedback_text", [])))

            # resume ↔ gitHub skill alignment
            st.markdown("---")
            st.subheader("🤝 Resume ↔ GitHub Skill Alignment")

            try:
                resume_text = st.session_state.get("resume_text", "")
                github_langs = data.get("top_languages", {})

                if resume_text and github_langs:
                    langs_in_github = [lang.lower() for lang in github_langs.keys()]

                    resume_keywords = extract_keywords(resume_text, top_n=50)
                    resume_keywords = [k.lower() for k in resume_keywords]

                    matched = [lang for lang in langs_in_github if lang in resume_keywords]
                    missing = [lang for lang in langs_in_github if lang not in resume_keywords]

                    align_percent = int((len(matched) / len(langs_in_github)) * 100) if langs_in_github else 0

                    col_r4.metric("Alignment (%)", f"{align_percent}%")

                    st.metric(label="Alignment (%)", value=f"{align_percent}%")
                    st.write(f"✅ **Matched Skills:** {', '.join(matched) if matched else 'None'}")
                    st.write(f"❌ **Missing from Resume:** {', '.join(missing) if missing else 'None'}")

                    st.markdown("#### 💻 Top GitHub Languages")
                    for lang, count in github_langs.items():
                        st.write(f"- {lang}: {count:,} lines of code")

                    # combined resume & portfolio visualization
                    st.markdown("---")
                    st.subheader("📊 Resume & Portfolio Combined Visualization")
                    try:
                        col1, col2 = st.columns(2)
                        # resume skill distribution (pie chart)
                        with col1:
                            st.markdown("#### Resume Skill Distribution")
                            from nlp_analysis import get_skill_frequencies

                            resume_skill_df = get_skill_frequencies(resume_text)
                            if not resume_skill_df.empty:
                                fig1, ax1 = plt.subplots()
                                ax1.pie(
                                    resume_skill_df["Count"],
                                    labels=resume_skill_df["Skill"],
                                    autopct="%1.1f%%",
                                    startangle=90
                                )
                                ax1.axis("equal")
                                st.pyplot(fig1)
                            else:
                                st.info("No skills found in resume for visualization.")

                        # gitHub language distribution (bar chart)
                        with col2:
                            st.markdown("#### GitHub Language Distribution")
                            if github_langs:
                                fig2, ax2 = plt.subplots()
                                langs = list(github_langs.keys())
                                lines = list(github_langs.values())
                                ax2.bar(langs, lines)
                                ax2.set_xlabel("Languages")
                                ax2.set_ylabel("Lines of Code")
                                ax2.set_title("GitHub Language Distribution")
                                plt.xticks(rotation=45)
                                st.pyplot(fig2)
                            else:
                                st.info("No GitHub languages available for visualization.")

                        st.success(
                            "✅ Insight: The closer the resume skill ratio matches GitHub language ratio, "
                            "the stronger your profile alignment.")

                    except Exception as e:
                        st.warning(f"Could not generate combined visualization: {e}")

                    # top github language vs resume focus
                    st.markdown("### 📊 GitHub Language vs Resume Focus")
                    try:
                        top_lang = max(github_langs, key=github_langs.get)
                        resume_top_skills = get_top_skills(resume_text, top_n=1)
                        resume_focus = resume_top_skills[0] if resume_top_skills else "Unknown"

                        st.write(f"**🏆 Top GitHub Language:** {top_lang}")
                        st.write(f"**🧠 Resume Focus Area:** {resume_focus}")

                        if top_lang.lower() == resume_focus.lower():
                            st.success("Perfect alignment — your GitHub projects reflect your resume focus! 🎯")
                        else:
                            st.info("Partial alignment — consider adding GitHub projects related to your resume focus.")

                            # ai summary insight
                            st.markdown("---")
                            st.subheader("🧠 AI Summary Insight")

                            try:
                                role = st.session_state.get("role", "N/A")
                                ats_score = st.session_state.get("ats_score", 0)
                                result = st.session_state.get("result", {"found": [], "missing": []})
                                portfolio_data = st.session_state.get("portfolio_data", {})

                                summary_text = generate_ai_summary(
                                    role=role,
                                    ats_score=ats_score,
                                    found_skills=result.get("found", []),
                                    missing_skills=result.get("missing", []),
                                    portfolio_data=portfolio_data)

                                st.markdown(
                                    f"<p style='font-size:17px; color:#E0E0E0; background-color:#262730; padding:12px; border-radius:10px;'>{summary_text}</p>",
                                    unsafe_allow_html=True)
                            except Exception as e:
                                st.warning(f"Could not generate AI summary: {e}")

                    except Exception as e:
                        st.warning(f"Could not analyze GitHub vs Resume focus: {e}")

                else:
                    st.info("Upload your resume and enter your GitHub username to view alignment insights.")

            except Exception as e:
                st.warning(f"Could not compute Resume ↔ GitHub alignment: {e}")

            # save analysis
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

            # export pdf
            if st.button("📄 Export combined PDF report"):
                with st.spinner("Generating PDF..."):
                    try:
                        from nlp_analysis import get_skill_frequencies

                        resume_skill_df = get_skill_frequencies(st.session_state.get("resume_text", ""))
                        filename = generate_pdf_report(
                            role=st.session_state.get("role", "N/A"),
                            result=st.session_state.get("result", {"found": [], "missing": []}),
                            feedback=st.session_state.get("feedback", []),
                            ats_score=st.session_state.get("ats_score", 0),
                            portfolio_data=data,
                            resume_skill_df=resume_skill_df)

                        st.success("✅ PDF report generated successfully!")
                        with open(filename, "rb") as pdf_file:
                            st.download_button("⬇️ Download Report", data=pdf_file, file_name=filename, mime="application/pdf")
                    except Exception as e:
                        st.error(f"Could not generate PDF: {e}")

# progress history
with tab_progress:
    st.header("📈 Progress History")
    st.write("Track your ATS score history and improvements over time.")
    username_for_history = st.text_input("History: Enter GitHub username to view progress", value="")

    if username_for_history:
        try:
            history = get_user_history(username_for_history)
        except sqlite3.OperationalError as exc:
            st.error(f"Database error while fetching history: {exc}")
            history = []
        except Exception as exc:
            st.warning(f"Could not fetch history: {exc}")
            history = []

        if history:
            import plotly.graph_objects as go

            df = pd.DataFrame(history, columns=["Role", "ATS Score", "Repositories", "Followers", "Contributions", "Points", "Date"])

            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            highest_score = df["ATS Score"].max()
            total_uploads = len(df)
            st.markdown(
                f"<h5 style='text-align:center; color:#1E90FF;'>"
                f"Your highest score is <b>{highest_score}</b>, over your last {total_uploads} uploads."
                f"</h5>",
                unsafe_allow_html=True
            )

            # plotly chart
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df["Date"],
                    y=df["ATS Score"],
                    mode="lines+markers",
                    line=dict(color="#8B5CF6", width=3),
                    marker=dict(size=10, color="#8B5CF6"),
                    fill="tozeroy",
                    fillcolor="rgba(139,92,246,0.15)",
                    hovertemplate="<b>Date:</b> %{x|%b %d, %Y}<br>"
                                  "<b>ATS Score:</b> %{y}<extra></extra>"
                )
            )

            # layout
            fig.update_layout(
                xaxis=dict(
                    title="Date",
                    tickformat="%b %d",
                    showgrid=False,
                    zeroline=False
                ),
                yaxis=dict(
                    title="ATS Score",
                    range=[0, max(100, df["ATS Score"].max() + 10)],
                    fixedrange=True,
                    showgrid=True,
                    gridcolor="rgba(200,200,200,0.25)"
                ),
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=40, l=40, r=40),
                height=400
            )

            fig.update_yaxes(range=[0, max(100, df["ATS Score"].max() + 10)], fixedrange=True)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No progress history yet — analyze a resume to start tracking your growth!")

    # clear history
    st.markdown("---")
    st.subheader("🧹 Manage Your Data")
    if st.button("Clear My History"):
        if username_for_history:
            try:
                conn = sqlite3.connect("analysis_history.db")
                c = conn.cursor()
                c.execute("DELETE FROM history WHERE username=?", (username_for_history,))
                conn.commit()
                conn.close()
                st.success("✅ History cleared successfully!")
            except Exception as e:
                st.error(f"Could not clear history: {e}")
        else:
            st.warning("Enter the username above to clear that user's history.")

# leaderboard
with tab_leaderboard:
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