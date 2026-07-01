import re
import os

SITE_URL = "https://touricn.github.io"
SUMMARY = "src/SUMMARY.md"
OUT_FILE = "sitemap.xml"

def main():
    if not os.path.exists(SUMMARY):
        print(f"ERROR: {SUMMARY} not found!")
        return

    with open(SUMMARY, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配所有以 .md 结尾的链接
    links = re.findall(r'\[.*?\]\((\S+\.md)\)', content)
    
    urls = []
    for link in links:
        # 清理路径：去掉 ./ 前缀
        path = link.lstrip('./')
        
        if path.endswith('README.md'):
            urls.append(f"{SITE_URL}/")
        else:
            # 去掉 .md 后缀，拼接 URL
            url_path = os.path.splitext(path)[0]
            urls.append(f"{SITE_URL}/{url_path}/")
    
    # 去重并排序
    urls = sorted(set(urls))
    
    print(f"Found {len(urls)} URLs from SUMMARY.md:")
    for u in urls:
        print(f"  - {u}")

    # 写入 sitemap.xml
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in urls:
            f.write(f"  <url><loc>{url}</loc></url>\n")
        f.write('</urlset>\n')
    
    print(f"SUCCESS: Generated {OUT_FILE} with {len(urls)} URLs.")

if __name__ == "__main__":
    main()
