import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

def _safe_int(s):
    try:
        return int(str(s).replace(",", "").strip())
    except Exception:
        return 0

def analyze_github_profile(username: str):
    if not username or not str(username).strip():
        return {"error": "GitHub username cannot be empty."}

    api_url = f"https://api.github.com/users/{username}"
    contrib_url = f"https://github.com/users/{username}/contributions"

    try:
        res = requests.get(api_url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return {"error": f"Profile not found: {username}"}
        data = res.json()
        repositories = _safe_int(data.get("public_repos", 0))
        followers = _safe_int(data.get("followers", 0))

        contributions = 0
        try:
            html = requests.get(contrib_url, headers=HEADERS, timeout=8).text
            m = re.search(r'([0-9][0-9,]*)\s+contributions\s+in\s+the\s+last\s+year', html, re.I)
            if m:
                contributions = _safe_int(m.group(1))
            else:
                counts = re.findall(r'data-count="(\d+)"', html)
                if counts:
                    contributions = sum(int(c) for c in counts)
                else:
                    nums = re.findall(r'([0-9][0-9,]*)\s+contributions', html, re.I)
                    if nums:
                        contributions = max(_safe_int(x) for x in nums)
        except Exception:
            contributions = 0

        feedback_lines = []
        if repositories < 5:
            feedback_lines.append("Consider adding more repositories to showcase your work.")
        if followers < 20:
            feedback_lines.append("Engage with the community to increase visibility (follow, star, comment).")
        if contributions < 100:
            feedback_lines.append("Increase commit activity to show consistent progress.")
        if not feedback_lines:
            feedback_lines.append("Nice portfolio — keep contributing and polishing projects!")

        feedback_text = " ".join(feedback_lines)

        return {
            "username": username,
            "repositories": repositories,
            "followers": followers,
            "contributions": contributions,
            "feedback": feedback_lines,
            "feedback_text": feedback_text
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}