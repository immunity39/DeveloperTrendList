import requests
import feedparser
import datetime
from bs4 import BeautifulSoup
import base64
import subprocess
import sys
import os
import traceback

# --- existing fetch functions (qiita, zenn, github) ---
def fetch_qiita_top1():
    url = "https://qiita.com/api/v2/items?page=1&per_page=1&query=stocks:>10"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    item = r.json()[0]
    desc = (item.get("body") or "")[:200].replace("\n", " ") if isinstance(item, dict) else ""
    return {
        "title": item["title"],
        "url": item["url"],
        "desc": desc
    }

def fetch_zenn_top1():
    feed = feedparser.parse("https://zenn.dev/feed")
    if not feed.entries:
        return {"title": "No entry", "url": "", "desc": ""}
    entry = feed.entries[0]
    desc = getattr(entry, "summary", "")[:200].replace("\n", " ")
    return {
        "title": entry.title,
        "url": entry.link,
        "desc": desc
    }

def fetch_github_top1():
    url = "https://github.com/trending?since=daily"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    repo = soup.select_one("article.Box-row h2 a")
    if not repo:
        return {"title": "No repo", "url": "", "desc": ""}
    full_name = repo.get_text(strip=True).replace(" / ", "/")
    href = repo["href"]
    # GitHub API for description (rate limit applies)
    api_url = f"https://api.github.com/repos/{full_name}"
    try:
        repo_data = requests.get(api_url, timeout=30).json()
        description = repo_data.get("description") or ""
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
    except Exception:
        description = ""
        stars = forks = 0

    # README excerpt as fallback
    readme_excerpt = ""
    try:
        readme_api = f"https://api.github.com/repos/{full_name}/readme"
        rr = requests.get(readme_api, timeout=30)
        if rr.status_code == 200:
            readme_data = rr.json()
            import base64
            readme_content = base64.b64decode(readme_data.get("content","")).decode("utf-8", errors="ignore")
            readme_excerpt = readme_content.strip().split("\n")[0][:160]
    except Exception:
        readme_excerpt = ""

    desc = description or readme_excerpt or "No description"
    return {
        "title": full_name,
        "url": "https://github.com" + href,
        "desc": desc,
        "stars": stars,
        "forks": forks
    }

# --- update README ---
def update_readme(qiita, zenn, github):
    # The user wanted README to show "yesterday" as the displayed date,
    # but the daily job runs at JST 24:30; show previous-day label
    jst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    display_date = (jst_now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    content = f"""# 今日のエンジニア記事トレンド

最終更新: {display_date}

- **Qiita**: [{qiita['title']}]({qiita['url']})  
  📝 {qiita['desc']}

- **Zenn**: [{zenn['title']}]({zenn['url']})  
  📝 {zenn['desc']}

- **GitHub**: [{github['title']}]({github['url']})  
  ⭐ {github.get('stars',0)}  🍴 {github.get('forks',0)}  
  📝 {github['desc']}

👉 過去分やTop3/5は `docs/monthly/` に保存しています。
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated")

# --- helper to run other scripts if conditions met ---
def try_run_script(script_path, args=None):
    args = args or []
    cmd = [sys.executable, script_path] + args
    print(f"Running: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=600)
        print("Return code:", res.returncode)
        if res.stdout:
            print("stdout:", res.stdout)
        if res.stderr:
            print("stderr:", res.stderr)
        return res.returncode == 0
    except Exception as e:
        print("Exception when running script:", e)
        traceback.print_exc()
        return False

if __name__ == "__main__":
    qiita = {}
    zenn = {}
    github = {}
    try:
        qiita = fetch_qiita_top1()
    except Exception as e:
        print("Qiita fetch error:", e)
    try:
        zenn = fetch_zenn_top1()
    except Exception as e:
        print("Zenn fetch error:", e)
    try:
        github = fetch_github_top1()
    except Exception as e:
        print("GitHub fetch error:", e)

    update_readme(qiita, zenn, github)

    # --- Schedule-linked behavior (in JST) ---
    # If today (JST) is the first of the month -> run monthly script
    # If today (JST) is Jan 1 -> run yearly script after monthly
    jst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    jst_day = jst_now.day
    jst_month = jst_now.month
    print(f"JST now: {jst_now.isoformat()}, day={jst_day}, month={jst_month}")

    # run monthly on day 1 of month
    if jst_day == 1:
        print("Detected JST day 1 -> Running monthly aggregation")
        ok = try_run_script("scripts/update_monthly.py")
        if not ok:
            print("Monthly script returned error or non-zero exit")
    else:
        print("Not month-start: skipping monthly aggregation")

    # run yearly on Jan 1
    if jst_day == 1 and jst_month == 1:
        print("Detected JST Jan 1 -> Running yearly aggregation")
        ok = try_run_script("scripts/update_yearly.py")
        if not ok:
            print("Yearly script returned error or non-zero exit")
    else:
        print("Not year-start: skipping yearly aggregation")
