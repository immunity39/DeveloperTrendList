from datetime import datetime

def generate_html_page(title, items, sidebar_links, output_path):
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
.navbar a {{ margin-right: 15px; }}
.sidebar {{ float: right; width: 20%; background: #f9f9f9; padding: 10px; border-radius: 8px; }}
.content {{ width: 75%; float: left; }}
.article {{ margin-bottom: 1em; }}
</style>
</head>
<body>
<nav class="navbar">
  <a href="../index.html">Today</a>
  <a href="../weekly/">Weekly</a>
  <a href="../monthly/">Monthly</a>
  <a href="../yearly/">Yearly</a>
  <a href="../log/">Logs</a>
  <a href="../info.html">Info</a>
</nav>

<div class="content">
<h1>{title}</h1>
{"".join(f"<div class='article'><a href='{i['url']}'><b>{i['title']}</b></a><br><small>{i.get('desc','')}</small></div>" for i in items)}
</div>

<div class="sidebar">
<h3>過去データ</h3>
{"<br>".join(f"<a href='{link['path']}'>{link['label']}</a>" for link in sidebar_links)}
</div>

</body>
</html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
