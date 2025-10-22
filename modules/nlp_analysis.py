from typing import List
from collections import Counter
import re
import io
import pandas as pd

_STOPWORDS = {"and", "the", "for", "with", "from", "that", "this", "you", "are", "was", "have",
    "has", "will", "not", "your", "but", "our", "they", "their", "them", "about", "which",
    "when", "what", "where", "why", "how", "all", "any", "also", "use", "used", "using", "one",
    "can", "may", "should", "a", "an", "in", "on", "of", "to"}

def __simple_tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9\-\+#]+", text)

def extract_keywords(text: str, top_n: int = 30) -> List[str]:
    if not text:
        return []
    tokens = [t.lower() for t in __simple_tokenize(text)]
    filtered = [t for t in tokens if len(t) > 2 and t not in _STOPWORDS]
    counts = Counter(filtered)
    return [tok for tok, _ in counts.most_common(top_n)]

def get_top_skills(text: str, top_n: int = 5) -> List[str]:

    TECHNICAL_SKILLS = {"python", "java", "c++", "sql", "pandas", "numpy", "matplotlib",
        "tensorflow", "scikit-learn", "machine", "learning", "deep", "django",
        "flask", "react", "aws", "docker", "html", "css", "javascript"}

    tokens = [t.lower() for t in __simple_tokenize(text)]
    filtered = [
        t for t in tokens
        if len(t) > 2 and t not in _STOPWORDS and not t.isdigit() and t in TECHNICAL_SKILLS]

    counts = Counter(filtered)
    return [tok for tok, _ in counts.most_common(top_n)]

def get_skill_frequencies(text: str):
    if not text:
        return pd.DataFrame(columns=["Skill", "Count"])

    TECHNICAL_SKILLS = {"python", "java", "c++", "sql", "pandas", "numpy", "matplotlib",
        "tensorflow", "scikit-learn", "machine", "learning", "deep", "django",
        "flask", "react", "aws", "docker", "html", "css", "javascript"}

    tokens = [t.lower() for t in __simple_tokenize(text)]
    filtered = [t for t in tokens if t in TECHNICAL_SKILLS]
    if not filtered:
        return pd.DataFrame(columns=["Skill", "Count"])

    counts = Counter(filtered)
    df = pd.DataFrame(counts.items(), columns=["Skill", "Count"]).sort_values(by="Count", ascending=False)
    return df.reset_index(drop=True)

def calculate_skill_match_percentage(text: str, required_skills: List[str]):

    if not required_skills:
        return 0, 0, 0, []

    text_lower = text.lower()
    matched = []

    for skill in required_skills:
        if not skill or not isinstance(skill, str):
            continue
        skill_norm = skill.strip().lower()

        try:
            pattern = r"\b" + re.escape(skill_norm) + r"\b"
            if re.search(pattern, text_lower):
                matched.append(skill)
                continue
        except re.error:
            pass

        if skill_norm in text_lower:
            matched.append(skill)
            continue

    total = len(required_skills)
    matched_count = len(matched)
    percent = int(round((matched_count / total) * 100)) if total > 0 else 0
    return percent, matched_count, total, matched

def generate_wordcloud_bytes(text: str, max_words: int = 150) -> bytes:
    if not text:
        return None

    try:
        from wordcloud import WordCloud
    except Exception:
        return None

    try:
        keywords = extract_keywords(text, top_n=max_words)
        cloud_text = " ".join(keywords) if keywords else text

        wc = WordCloud(
            width=900,
            height=400,
            background_color="white",
            collocations=False,
            max_words=max_words
        ).generate(cloud_text)

        img = wc.to_image()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None