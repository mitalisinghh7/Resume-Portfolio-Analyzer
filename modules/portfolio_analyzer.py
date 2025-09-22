import requests
from bs4 import BeautifulSoup

def analyze_github_profile(username):
    """
    Analyze GitHub profile:
    - Repositories
    - Followers
    - Contributions (this year)
    """
    profile_url = f"https://github.com/{username}"
    contrib_url = f"https://github.com/users/{username}/contributions"

    profile_res = requests.get(profile_url)
    contrib_res = requests.get(contrib_url)

    if profile_res.status_code != 200:
        return {"error": f"Could not fetch profile for {username}"}

    soup = BeautifulSoup(profile_res.text, "html.parser")
    contrib_soup = BeautifulSoup(contrib_res.text, "html.parser")

    repos = soup.find("span", {"class": "Counter"})
    followers = soup.find("a", {"href": f"/{username}?tab=followers"})
    contribs = contrib_soup.find("h2")

    return {
        "username": username,
        "repositories": repos.text.strip() if repos else "0",
        "followers": followers.text.strip() if followers else "0",
        "contributions": contribs.text.strip().split(" ")[0] if contribs else "0"
    }