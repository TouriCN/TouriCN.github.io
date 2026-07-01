import os
import markdown

SRC_DIR = "src"

def compile_markdown():
    # 遍历 src 目录
    for filename in os.listdir(SRC_DIR):
        if filename.endswith(".md"):
            md_path = os.path.join(SRC_DIR, filename)
            html_filename = filename.replace(".md", ".html")
            html_path = html_filename  # ✅ 直接输出到根目录

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # 纯 HTML 转换（无扩展）
            html_body = markdown.markdown(md_content, extensions=[])

            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename.replace('.md', '')}</title>
</head>
<body>
{html_body}
</body>
</html>
"""

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            print(f"Generated {html_path}")

if __name__ == "__main__":
    compile_markdown()
