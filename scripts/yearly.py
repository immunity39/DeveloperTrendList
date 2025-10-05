import datetime
import os
import json
from collections import defaultdict
from pathlib import Path

def aggregate_yearly(service, top_n=25):
    base_dir = f"data/{service}_monthly"
    scores = defaultdict(int)
    info = {}

    for file in os.listdir(base_dir):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(base_dir, file), "r", encoding="utf-8") as f:
            monthly_data = json.load(f)
            for item in monthly_data:
                scores[item["title"]] += item["score"]
                info[item["title"]] = item

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [info[title] for title, _ in ranked]

def save_yearly(qiita, zenn, github, year=None):
    today = datetime.datetime.utcnow()
    year = year or today.year
    out_dir = "docs/yearly"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{year}.md")

    content = f"# {year}年 エンジニア記事 年間トレンド\n\n"

    content += "## Qiita\n"
    content += "\n".join([f"- [{x['title']}]({x['url']})" for x in qiita]) + "\n\n"

    content += "## Zenn\n"
    content += "\n".join([f"- [{x['title']}]({x['url']})" for x in zenn]) + "\n\n"

    content += "## GitHub Trending\n"
    content += "\n".join([f"- [{x['title']}]({x['url']})\n  - {x.get('desc','')}" for x in github]) + "\n"

    output_dir_docs = Path("docs")
    output_dir_docs.mkdir(parents=True, exist_ok=True)
    with open(output_dir_docs / "YEARLY.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    qiita = aggregate_yearly("qiita")
    zenn = aggregate_yearly("zenn")
    github = aggregate_yearly("github", top_n=50)  # GitHubは多め
    save_yearly(qiita, zenn, github)
