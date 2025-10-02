import feedparser
import datetime
import os
import json

def fetch_zenn_monthly(top_n=10):
    feed = feedparser.parse("https://zenn.dev/feed")
    today = datetime.datetime.utcnow()
    month_ago = today - datetime.timedelta(days=30)
    entries = [e for e in feed.entries if datetime.datetime(*e.published_parsed[:6]) > month_ago]

    results = []
    for rank, e in enumerate(entries[:top_n], start=1):
        results.append({
            "rank": rank,
            "score": top_n - rank + 1,
            "title": e.title,
            "url": e.link
        })
    return results

def save_monthly_data(data, out_dir="data/zenn_monthly"):
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.datetime.utcnow()
    filename = today.strftime("%Y-%m") + ".json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} Zenn articles to {path}")

if __name__ == "__main__":
    data = fetch_zenn_monthly()
    save_monthly_data(data)
