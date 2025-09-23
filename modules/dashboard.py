import streamlit as st

def run_dashboard():
    st.title("🎓 Resume & Portfolio Analyzer")
    st.write("Welcome! This is the starting point of our dashboard.")

    st.header("📄 Resume Analysis")
    st.success("✅ Keywords Found: ['Python', 'SQL']")
    st.error("❌ Keywords Missing: ['Django', 'MERN']")

    st.header("📊 ATS Score")
    st.info("Python Developer: 75%")
    st.info("Data Scientist: 60%")

    st.header("🌐 Portfolio Analysis")
    st.warning("GitHub Repositories: 10")
    st.warning("Followers: 5")
    st.warning("Contributions: 50 this year")

if __name__ == "__main__":
    run_dashboard()