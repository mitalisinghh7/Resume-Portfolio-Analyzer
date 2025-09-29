def generate_feedback(found, missing):
    """Generate personalized resume improvement feedback."""

    feedback = []

    if missing:
        feedback.append("⚠️ Consider learning or adding these skills to strengthen your resume:")
        for skill in missing:
            if skill.lower() == "sql":
                feedback.append("- SQL → Mention database projects or coursework.")
            elif skill.lower() == "machine learning":
                feedback.append("- Machine Learning → Add academic projects or Kaggle experience.")
            elif skill.lower() == "mern":
                feedback.append("- MERN → Highlight web development experience if you have it.")
            else:
                feedback.append(f"- {skill}")
    else:
        feedback.append("✅ Excellent! Your resume already includes all key skills.")

    if found:
        feedback.append("\n💡 Make sure these skills stand out clearly in your resume:")
        for skill in found:
            feedback.append(f"- {skill} → Highlight projects or achievements where you applied this.")

    return "\n".join(feedback)