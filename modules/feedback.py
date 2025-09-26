def generate_feedback(found, missing):
    """Generate simple resume improvement feedback."""
    feedback = []

    if missing:
        feedback.append("⚠️ Consider adding these skills to strengthen your resume:")
        for skill in missing:
            feedback.append(f"- {skill}")
    else:
        feedback.append("✅ Great! Your resume already contains all the required skills.")

    if found:
        feedback.append("\n👍 Highlight these skills more clearly to stand out:")
        for skill in found:
            feedback.append(f"- {skill}")

    return "\n".join(feedback)