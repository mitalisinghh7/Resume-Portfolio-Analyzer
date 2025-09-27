import streamlit as st

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
    st.text(feedback)

def show_summary(result: dict):
    """Show a summary of found vs missing skills."""
    st.subheader("📊 Skills Summary")
    st.write(f"- Found: {len(result['found'])}")
    st.write(f"- Missing: {len(result['missing'])}")
