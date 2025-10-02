import requests
from bs4 import BeautifulSoup
import datetime
import os
import json

def fetch_github_monthly(top_n=50):
    url = "https://github.com/trending?since=monthly"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    repos = soup.select("article.Box-row")[:top_n]

    results = []
    for rank, repo in enumerate(repos, start=1):
        link = repo.select_one("h2 a")
        full_name = link.get_text(strip=True).replace(" / ", "/")
        href = "https://github.com" + link["href"]

        desc_tag = repo.select_one("p")
        desc = desc_tag.get_text(strip=True) if desc_tag else "No description"

        results.append({
            "rank": rank,
            "score": top_n - rank + 1,   # 1位=50点, 2位=49点...
            "title": full_name,
            "url": href,
            "desc": desc
        })
    return results

def save_monthly_data(data, out_dir="data/github_monthly"):
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.datetime.utcnow()
    filename = today.strftime("%Y-%m") + ".json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} repos to {path}")

if __name__ == "__main__":
    data = fetch_github_monthly()
    save_monthly_data(data)
