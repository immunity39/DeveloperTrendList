import requests
import feedparser
import datetime
from bs4 import BeautifulSoup

def fetch_qiita_monthly(top_n=10):
    today = datetime.datetime.utcnow()
    month_ago = today - datetime.timedelta(days=30)
    url = f"https://qiita.com/api/v2/items?page=1&per_page=100&query=created:>{month_ago.strftime('%Y-%m-%d')}"
    r = requests.get(url)
    items = r.json()
    items.sort(key=lambda x: x["likes_count"], reverse=True)
    return [{"title": item["title"], "url": item["url"]} for item in items[:top_n]]

def fetch_zenn_monthly(top_n=10):
    feed = feedparser.parse("https://zenn.dev/feed")
    today = datetime.datetime.utcnow()
    month_ago = today - datetime.timedelta(days=30)
    entries = [e for e in feed.entries if datetime.datetime(*e.published_parsed[:6]) > month_ago]
    return [{"title": e.title, "url": e.link} for e in entries[:top_n]]

def fetch_github_monthly(top_n=10):
    url = "https://github.com/trending?since=monthly"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    repos = soup.select("article.Box-row")[:top_n]

    results = []
    for repo in repos:
        link = repo.select_one("h2 a")
        full_name = link.get_text(strip=True).replace(" / ", "/")
        href = "https://github.com" + link["href"]

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

    content = f"""# 月間エンジニア記事トレンド

集計日: {today}

## Qiita (Top {len(qiita)})
""" + "\n".join([f"- [{x['title']}]({x['url']})" for x in qiita]) + """

## Zenn (Top {len(zenn)})
""" + "\n".join([f"- [{x['title']}]({x['url']})" for x in zenn]) + """

## GitHub Trending (Top {len(github)})
""" + "\n".join([f"- [{x['title']}]({x['url']})\n  - {x['desc']}" for x in github]) + """
"""
    with open("MONTHLY.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    qiita = fetch_qiita_monthly()
    zenn = fetch_zenn_monthly()
    github = fetch_github_monthly()
    update_readme(qiita, zenn, github)
