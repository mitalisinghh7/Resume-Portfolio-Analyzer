import json
import os

def load_templates():
    """Load feedback suggestions from JSON file."""
    path = os.path.join(os.path.dirname(__file__), "feedback_templates.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

TEMPLATES = load_templates()

def generate_feedback(found, missing):
    """Generate personalized resume improvement feedback using templates."""
    feedback = []

    if missing:
        feedback.append("⚠️ Consider improving your resume with these:")
        for skill in missing:
            suggestion = TEMPLATES.get(skill.lower(), f"Add more details about {skill}.")
            feedback.append(f"- {skill} → {suggestion}")
    else:
        feedback.append("✅ Great! Your resume already includes all the key skills for this role.")

    if found:
        feedback.append("\n💡 Make these skills stand out more:")
        for skill in found:
            suggestion = TEMPLATES.get(skill.lower(), f"Show projects where you applied {skill}.")
            feedback.append(f"- {skill} → {suggestion}")

    return "\n".join(feedback)