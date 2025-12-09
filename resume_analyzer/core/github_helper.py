# core/github_helper.py
import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

def search_github_repos(keywords, token=None, per_page=5):
    """
    Basic GitHub repository search by keywords.
    If you have a GitHub token, pass it to increase rate limits.
    Returns a list of dicts: {name, url, description}
    """
    q = "+".join(keywords.split())
    params = {"q": q + " in:name,description,readme", "sort": "stars", "order": "desc", "per_page": per_page}
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        r = requests.get(GITHUB_SEARCH_URL, params=params, headers=headers, timeout=8)
        data = r.json()
        items = data.get("items", []) if isinstance(data, dict) else []
    except Exception:
        items = []
    results = []
    for it in items:
        results.append({
            "name": it.get("full_name"),
            "url": it.get("html_url"),
            "description": it.get("description") or ""
        })
    return results
