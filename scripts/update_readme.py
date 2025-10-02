import requests
import feedparser
import datetime
from bs4 import BeautifulSoup
import base64

def fetch_qiita_top1():
    url = "https://qiita.com/api/v2/items?page=1&per_page=1&query=stocks:>10"
    r = requests.get(url)
    item = r.json()[0]
    return {
        "title": item["title"],
        "url": item["url"],
    }

def fetch_zenn_top1():
    feed = feedparser.parse("https://zenn.dev/feed")
    entry = feed.entries[0]
    return {
        "title": entry.title,
        "url": entry.link,
    }

def fetch_github_top1():
    url = "https://github.com/trending?since=daily"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    repo = soup.select_one("article.Box-row h2 a")
    full_name = repo.get_text(strip=True).replace(" / ", "/")  # "owner/repo"
    href = repo["href"]

    api_url = f"https://api.github.com/repos/{full_name}"
    repo_data = requests.get(api_url).json()

    description = "No description"
    description = repo_data.get("description", "No description")
    if description == "No description":
        # README取得
        readme_api = f"https://api.github.com/repos/{full_name}/readme"
        readme_resp = requests.get(readme_api)
        if readme_resp.status_code == 500:
            readme_data = readme_resp.json()
            readme_content = base64.b64decode(readme_data["content"]).decode("utf-8", errors="ignore")
            readme_excerpt = readme_content.strip().split("\n")[0][:50] + "..."
            description = readme_excerpt

    return {
        "title": full_name,
        "url": "https://github.com" + href,
        "desc": description if description else readme_excerpt
    }

def update_readme(qiita, zenn, github):
    today = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    content = f"""# 今日のエンジニア記事トレンド

最終更新: {today}

- **Qiita**: [{qiita['title']}]({qiita['url']})

- **Zenn**: [{zenn['title']}]({zenn['url']})

- **GitHub**: [{github['title']}]({github['url']})
description: {github['desc']}

👉 過去分やTop3/5は今後 `docs/daily/` に保存予定です。
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    qiita = fetch_qiita_top1()
    zenn = fetch_zenn_top1()
    github = fetch_github_top1()
    update_readme(qiita, zenn, github)
