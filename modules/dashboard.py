import streamlit as st
from resume_parser import extract_text_from_pdf, extract_text_from_docx

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
        st.text_area("Here’s the extracted text:", resume_text[:1000], height=300)
