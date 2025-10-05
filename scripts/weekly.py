import requests
import feedparser
import datetime
from bs4 import BeautifulSoup
from pathlib import Path

# Qiita
def fetch_qiita_weekly(top_n=5):
    today = datetime.datetime.utcnow()
    week_ago = today - datetime.timedelta(days=7)
    url = f"https://qiita.com/api/v2/items?page=1&per_page=50&query=created:>{week_ago.strftime('%Y-%m-%d')}"
    r = requests.get(url)
    items = r.json()
    items.sort(key=lambda x: x["likes_count"], reverse=True)
    return [{"title": item["title"], "url": item["url"]} for item in items[:top_n]]

# Zenn
def fetch_zenn_weekly(top_n=5):
    feed = feedparser.parse("https://zenn.dev/feed")
    today = datetime.datetime.utcnow()
    week_ago = today - datetime.timedelta(days=7)
    entries = [e for e in feed.entries if datetime.datetime(*e.published_parsed[:6]) > week_ago]
    return [{"title": e.title, "url": e.link} for e in entries[:top_n]]

# GitHub
def fetch_github_weekly(top_n=5):
    url = "https://github.com/trending?since=weekly"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    repos = soup.select("article.Box-row")[:top_n]

    results = []
    for repo in repos:
        link = repo.select_one("h2 a")
        full_name = link.get_text(strip=True).replace(" / ", "/")
        href = "https://github.com" + link["href"]

        # description
        desc_tag = repo.select_one("p")
        desc = desc_tag.get_text(strip=True) if desc_tag else "No description"

        results.append({
            "title": full_name,
            "url": href,
            "desc": desc
        })
    return results

def update_readme(qiita, zenn, github):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    content = f"""# 週間エンジニア記事トレンド

集計日: {today}

## Qiita (Top {len(qiita)})
""" + "\n".join([f"- [{x['title']}]({x['url']})" for x in qiita]) + """

## Zenn (Top {len(zenn)})
""" + "\n".join([f"- [{x['title']}]({x['url']})" for x in zenn]) + """

## GitHub Trending (Top {len(github)})
""" + "\n".join([f"- [{x['title']}]({x['url']})\n  - {x['desc']}" for x in github]) + """
"""

    output_dir_docs = Path("docs")
    output_dir_docs.mkdir(parents=True, exist_ok=True)
    with open(output_dir_docs / "WEEKLY.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    qiita = fetch_qiita_weekly()
    zenn = fetch_zenn_weekly()
    github = fetch_github_weekly()
    update_readme(qiita, zenn, github)
