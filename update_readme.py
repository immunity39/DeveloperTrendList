import requests
import feedparser
import datetime

def fetch_qiita_top1():
    url = "https://qiita.com/api/v2/items?page=1&per_page=1&query=stocks:>10"
    r = requests.get(url)
    item = r.json()[0]
    return {"title": item["title"], "url": item["url"]}

def fetch_zenn_top1():
    feed = feedparser.parse("https://zenn.dev/feed")
    entry = feed.entries[0]
    return {"title": entry.title, "url": entry.link}

def fetch_github_top1():
    url = "https://github.com/trending?since=daily"
    r = requests.get(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    repo = soup.select_one("article.Box-row h2 a")
    full_name = repo.get_text(strip=True).replace(" / ", "/")
    href = repo["href"]
    return {"title": full_name, "url": "https://github.com" + href}

def update_readme(qiita, zenn, github):
    today = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    content = f"""# 今日のエンジニア記事トレンド

最終更新: {today}

- **Qiita**: [{qiita['title']}]({qiita['url']})
- **Zenn**: [{zenn['title']}]({zenn['url']})
- **GitHub**: [{github['title']}]({github['url']})

👉 過去分やTop3/5は今後 `docs/daily/` に保存予定です。
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    qiita = fetch_qiita_top1()
    zenn = fetch_zenn_top1()
    github = fetch_github_top1()
    update_readme(qiita, zenn, github)
