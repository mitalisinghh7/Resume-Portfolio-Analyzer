def analyze_keywords(resume_text, keywords):
    """
    Check which keywords are present and which are missing in the resume text.
    """
    found = []
    missing = []

    text_lower = resume_text.lower()

    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
        else:
            missing.append(kw)

    return {
        "found": found,
        "missing": missing}