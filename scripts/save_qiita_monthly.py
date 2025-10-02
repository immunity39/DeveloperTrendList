import requests
import datetime
import os
import json

def fetch_qiita_monthly(top_n=10):
    today = datetime.datetime.utcnow()
    month_ago = today - datetime.timedelta(days=30)
    url = f"https://qiita.com/api/v2/items?page=1&per_page={top_n}&query=created:>{month_ago.strftime('%Y-%m-%d')}"
    r = requests.get(url)
    items = r.json()

    results = []
    for rank, item in enumerate(items, start=1):
        results.append({
            "rank": rank,
            "score": top_n - rank + 1,
            "title": item["title"],
            "url": item["url"]
        })
    return results

def save_monthly_data(data, out_dir="data/qiita_monthly"):
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.datetime.utcnow()
    filename = today.strftime("%Y-%m") + ".json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} Qiita articles to {path}")

if __name__ == "__main__":
    data = fetch_qiita_monthly()
    save_monthly_data(data)
