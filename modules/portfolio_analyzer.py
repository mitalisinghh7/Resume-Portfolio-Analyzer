import requests
from bs4 import BeautifulSoup

def analyze_github_profile(username):
    """
    Get GitHub profile stats:
    - Number of repositories
    - Followers
    - Contributions in the last year
    """
    url = f"https://github.com/{username}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Could not fetch profile for {username}"}

    soup = BeautifulSoup(response.text, "html.parser")

    # repositories
    repo_tag = soup.find("span", {"class": "Counter"})
    repos = repo_tag.text.strip() if repo_tag else "0"

    # followers
    followers_tag = soup.find("a", {"href": f"/{username}?tab=followers"})
    followers = followers_tag.text.strip() if followers_tag else "0"

    # contributions
    contrib_tag = soup.find("h2", string=lambda text: text and "contributions" in text)
    contrib = contrib_tag.text.strip().split(" ")[0] if contrib_tag else "0"

    return {
        "username": username,
        "repositories": repos,
        "followers": followers,
        "contributions": contrib
    }