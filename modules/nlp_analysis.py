from typing import List, Dict
from collections import Counter
import io

def extract_keywords(text: str, top_n: int = 30) -> List[str]:

    if not text:
        return []
    words = [w.lower() for w in __simple_tokenize(text)]
    stop = set(["and", "the", "a", "to", "in", "for", "of", "with", "on", "is", "are", "by", "as", "that", "this"])
    filtered = [w for w in words if len(w) > 2 and w not in stop]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(top_n)]

def __simple_tokenize(text: str):
    import re
    return re.findall(r"[A-Za-z0-9\-\+#]+", text)

def generate_wordcloud_image(text: str):

    try:
        from wordcloud import WordCloud
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        img = wc.to_image()
        b = io.BytesIO()
        img.save(b, format="PNG")
        b.seek(0)
        return b.getvalue()
    except Exception:
        return None