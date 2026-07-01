import os
import markdown

SRC_DIR = "src"

def compile_markdown():
    os.makedirs(SRC_DIR, exist_ok=True)
    
    for filename in os.listdir(SRC_DIR):
        if filename.endswith(".md"):
            md_path = os.path.join(SRC_DIR, filename)
            html_filename = filename.replace(".md", ".html")
            html_path = html_filename

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_body = markdown.markdown(
                md_content,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.sane_lists',
                ]
            )

            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename.replace('.md', '')}</title>

    <style>
        :root {{
            color-scheme: light dark;
        }}

        body {{
            margin: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans",
                         "Helvetica Neue", sans-serif;
            line-height: 1.6;
            background: var(--bg);
            color: var(--text);
            transition: background 0.2s, color 0.2s;
        }}

        /* 浏览器默认（不干预） */
        :root[data-theme="browser"] {{
            --bg: Canvas;
            --text: CanvasText;
        }}

        /* 跟随系统 */
        :root[data-theme="system"] {{
            /* 默认不设置，让浏览器自己决定 */
        }}

        /* 仅在系统为深色时，覆盖为纯黑 */
        @media (prefers-color-scheme: dark) {{
            :root[data-theme="system"] {{
                --bg: #0d1117;
                --text: #e6edf3;
            }}
        }}

        /* 强制黑色 */
        :root[data-theme="dark"] {{
            --bg: #000;
            --text: #e6edf3;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
        }}

        th, td {{
            border: 1px solid var(--text);
            padding: 6px 10px;
        }}

        pre, code {{
            background: rgba(128,128,128,0.15);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        blockquote {{
            margin: 1em 0;
            padding-left: 12px;
            border-left: 4px solid gray;
            opacity: 0.85;
        }}

        .theme-switcher {{
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 999;
            background: var(--bg);
            border: 1px solid var(--text);
            padding: 4px 8px;
            font-size: 14px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <select class="theme-switcher" id="themeSwitcher">
        <option value="system">跟随系统</option>
        <option value="browser">浏览器默认</option>
        <option value="dark">黑色</option>
    </select>

{html_body}

    <script>
        const switcher = document.getElementById('themeSwitcher');
        const root = document.documentElement;

        function applyTheme(theme) {{
            root.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            switcher.value = theme;
        }}

        // 初始化
        const saved = localStorage.getItem('theme');
        if (saved) {{
            applyTheme(saved);
        }} else {{
            applyTheme('system');
        }}

        switcher.addEventListener('change', e => {{
            applyTheme(e.target.value);
        }});
    </script>
</body>
</html>
"""

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            print(f"Compiled {md_path} -> {html_path}")

if __name__ == "__main__":
    compile_markdown()
