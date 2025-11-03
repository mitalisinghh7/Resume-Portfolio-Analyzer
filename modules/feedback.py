import json
import os

def load_templates():
    path = os.path.join(os.path.dirname(__file__), "feedback_templates.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

TEMPLATES = load_templates()

def generate_feedback(found, missing):
    feedback_sections = []

    if missing:
        missing_lines = ["⚠️ **Consider improving your resume with these:**"]
        for skill in missing:
            suggestion = TEMPLATES.get(skill.lower(), f"Add more details about **{skill}**.")
            missing_lines.append(f"{skill} → {suggestion}")
        feedback_sections.append("\n".join(missing_lines))

    if found:
        found_lines = ["💡 **Make these skills stand out more:**"]
        for skill in found:
            suggestion = TEMPLATES.get(skill.lower(), f"Show achievements, projects, or certifications where you applied **{skill}**.")
            found_lines.append(f"{skill} → {suggestion}")
        feedback_sections.append("\n".join(found_lines))

    if not missing and not found:
        feedback_sections.append("✅ Great! Your resume already includes all key skills for this role.")

    return "\n\n".join(feedback_sections)