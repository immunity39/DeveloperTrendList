import os
import datetime

MONTHLY_DIR = "docs/monthly"
YEARLY_DIR = "docs/yearly"
INDEX_PATH = "docs/index.md"

def generate_index():
    lines = ["# トレンド集計リンク一覧\n"]
    lines.append("## 月次")
    for fname in sorted(os.listdir(MONTHLY_DIR)):
        if fname.endswith(".md"):
            y, m = fname.replace(".md", "").split("-")
            lines.append(f"- [{y}年{m}月](monthly/{fname})")
    lines.append("\n## 年次")
    for fname in sorted(os.listdir(YEARLY_DIR)):
        if fname.endswith(".md"):
            y = fname.replace(".md", "")
            lines.append(f"- [{y}年](yearly/{fname})")
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Index updated.")

if __name__ == "__main__":
    generate_index()
