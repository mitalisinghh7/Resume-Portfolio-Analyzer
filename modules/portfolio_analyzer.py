import requests
from bs4 import BeautifulSoup

def analyze_github_profile(username):

    if not username:
        return {"error": "GitHub username cannot be empty."}

    profile_url = f"https://github.com/{username}"
    contrib_url = f"https://github.com/users/{username}/contributions"

    try:
        profile_res = requests.get(profile_url, timeout=5)
        contrib_res = requests.get(contrib_url, timeout=5)
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

    if profile_res.status_code != 200:
        return {"error": f"Profile not found for username: {username}"}

    soup = BeautifulSoup(profile_res.text, "html.parser")
    contrib_soup = BeautifulSoup(contrib_res.text, "html.parser")

    repo_tag = soup.find("span", {"class": "Counter"})
    repositories = repo_tag.text.strip() if repo_tag else "0"

    followers_tag = soup.find("a", {"href": f"/{username}?tab=followers"})
    followers = followers_tag.text.strip() if followers_tag else "0"

    contrib_tag = contrib_soup.find("h2")
    contributions = contrib_tag.text.strip().split(" ")[0] if contrib_tag else "0"

    return {
        "username": username,
        "repositories": repositories,
        "followers": followers,
        "contributions": contributions }