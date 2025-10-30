import os
import json
import datetime
from collections import defaultdict
import math

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs", "yearly")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "daily")

os.makedirs(DOCS_DIR, exist_ok=True)

def nonlinear_score_github(stars, forks):
    return (stars ** 0.7) * 1.2 + (forks ** 0.6) * 1.0

def nonlinear_score_qiita(likes):
    return (likes ** 0.65) * 1.1

def nonlinear_score_zenn(likes):
    return (likes ** 0.6) * 1.1

def load_daily_data():
    data = defaultdict(list)
    if not os.path.exists(DATA_DIR):
        return data
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
            try:
                day_data = json.load(f)
                for key in ["qiita", "zenn", "github"]:
                    if key in day_data:
                        data[key].append(day_data[key])
            except:
                pass
    return data

def aggregate_yearly(data, year):
    yearly_scores = {}
    for key in ["qiita", "zenn", "github"]:
        items = [d for d in data.get(key, []) if d.get("date", "").startswith(str(year))]
        if not items:
            continue
        scores = []
        for it in items:
            if key == "github":
                s = nonlinear_score_github(it.get("stars", 0), it.get("forks", 0))
            elif key == "qiita":
                s = nonlinear_score_qiita(it.get("likes", 0))
            else:
                s = nonlinear_score_zenn(it.get("likes", 0))
            scores.append((s, it))
        scores.sort(reverse=True, key=lambda x: x[0])
        yearly_scores[key] = scores[:10]  # 年次は上位10件
    return yearly_scores

def save_yearly_md(scores, year):
    out_path = os.path.join(DOCS_DIR, f"{year}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {year}年 年間トレンド集計\n\n")
        f.write(f"生成日: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for key, label in [("qiita", "Qiita"), ("zenn", "Zenn"), ("github", "GitHub")]:
            f.write(f"## {label}\n\n")
            if key not in scores:
                f.write("データなし\n\n")
                continue
            for rank, (score, it) in enumerate(scores[key], start=1):
                title = it.get("title", "Untitled")
                url = it.get("url", "")
                desc = it.get("desc", "")[:150]
                f.write(f"{rank}. [{title}]({url})  \n")
                f.write(f"スコア: {score:.1f}  \n{desc}\n\n")
    print(f"Saved yearly report: {out_path}")

if __name__ == "__main__":
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    data = load_daily_data()
    scores = aggregate_yearly(data, now.year)
    save_yearly_md(scores, now.year)
