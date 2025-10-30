import os
import json
import datetime
from collections import defaultdict
import math

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs", "monthly")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "daily")

os.makedirs(DOCS_DIR, exist_ok=True)

def nonlinear_score_github(stars, forks):
    return (stars ** 0.7) * 1.2 + (forks ** 0.6) * 1.0

def nonlinear_score_qiita(likes):
    return (likes ** 0.65) * 1.1

def nonlinear_score_zenn(likes):
    return (likes ** 0.6) * 1.1

def load_daily_data():
    """日次保存済みのJSONデータを全件ロード"""
    data = defaultdict(list)
    if not os.path.exists(DATA_DIR):
        print("No daily data directory found.")
        return data

    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            try:
                day_data = json.load(f)
                for key in ["qiita", "zenn", "github"]:
                    if key in day_data:
                        data[key].append(day_data[key])
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return data

def aggregate_monthly(data, year, month):
    month_str = f"{year}-{month:02d}"
    monthly_scores = {}
    for key in ["qiita", "zenn", "github"]:
        items = [d for d in data.get(key, []) if d.get("date", "").startswith(month_str)]
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
        monthly_scores[key] = scores[:5]
    return monthly_scores

def save_monthly_md(scores, year, month):
    out_path = os.path.join(DOCS_DIR, f"{year}-{month:02d}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {year}年{month}月 トレンド集計\n\n")
        f.write(f"集計日: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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
    print(f"Saved monthly report: {out_path}")

if __name__ == "__main__":
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    data = load_daily_data()
    scores = aggregate_monthly(data, now.year, now.month)
    save_monthly_md(scores, now.year, now.month)
