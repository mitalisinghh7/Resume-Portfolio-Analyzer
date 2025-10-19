from typing import List
from collections import Counter
import re
import io

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