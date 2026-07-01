import os
import re
import markdown

SRC_DIR = "src"

def preprocess_github_admonitions(md_content):
    """
    ✅ 只处理 GitHub 警告框（> [!TIP]）
    ✅ 普通引用块（>）完全原样保留
    """
    lines = md_content.split('\n')
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        if line.strip() == '> [!TIP]' or \
           line.strip() == '> [!WARNING]' or \
           line.strip() == '> [!NOTE]':
            admon_type = line.strip().split('[!')[1].split(']')[0].lower()
            title = line.strip().split('[!')[1].split(']')[0]
            i += 1

            body_parts = []
            while i < n and lines[i].strip().startswith('>'):
                content = lines[i].strip()
                if content.startswith('> '):
                    content = content[2:]
                elif content.startswith('>'):
                    content = content[1:]
                if content:
                    body_parts.append(content)
                i += 1

            body = ' '.join(body_parts)
            result.append(f'<div class="admonition {admon_type}">')
            result.append(f'  <div class="admonition-title">{title}</div>')
            result.append(f'  <div>{body}</div>')
            result.append('</div>')
            result.append('')
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)

def hide_iframes_and_objects(md_content):
    """
    ✅ 核心防护：把 iframe 和 object 藏进占位符
    """
    # 匹配 iframe 或 object 标签
    pattern = r'<(iframe|object)[^>]*>.*?</\1>'
    matches = list(re.finditer(pattern, md_content, flags=re.DOTALL | re.IGNORECASE))
    
    placeholders = {}
    for i, match in enumerate(matches):
        placeholder = f'<!--EMBED_{i}-->'
        placeholders[placeholder] = match.group(0)
        md_content = md_content.replace(match.group(0), placeholder)
    
    return md_content, placeholders

def restore_iframes_and_objects(html_content, placeholders):
    """
    ✅ 还原 iframe 和 object
    """
    for placeholder, tag in placeholders.items():
        html_content = html_content.replace(placeholder, tag)
    return html_content

def fix_internal_links(html_content, current_dir=""):
    """
    ✅ 只处理 href="xxx.md"，绝不碰 src
    """
    pattern = r'href=["\']([^"\']+\.md)["\']'
    
    def replace_link(match):
        full_match = match.group(0)
        path = match.group(1)
        if path.startswith('/'):
            path = path[1:]
        html_path = path.replace('.md', '.html')
        if current_dir:
            html_path = os.path.join(current_dir, html_path).replace('\\', '/')
        return full_match.replace(path, html_path)
    
    return re.sub(pattern, replace_link, html_content)

def compile_markdown():
    """递归编译 src 目录下的所有 .md 文件"""
    for root, dirs, files in os.walk(SRC_DIR):
        for filename in files:
            if not filename.endswith(".md"):
                continue
            
            md_path = os.path.join(root, filename)
            
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            # 1. 预处理警告框
            processed_md = preprocess_github_admonitions(md_content)
            
            # 2. ✅ 隐藏 iframe/object（防止被 Markdown 或正则破坏）
            hidden_md, placeholders = hide_iframes_and_objects(processed_md)
            
            # 3. Markdown 转 HTML
            html_body = markdown.markdown(
                hidden_md,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.sane_lists',
                ]
            )
            
            # 4. 修复内部链接
            rel_path = os.path.relpath(root, SRC_DIR)
            current_dir = '' if rel_path == '.' else rel_path.replace('\\', '/')
            html_body = fix_internal_links(html_body, current_dir)
            
            # 5. ✅ 还原 iframe/object
            html_body = restore_iframes_and_objects(html_body, placeholders)
            
            # 6. 输出文件名
            if filename == "README.md":
                html_filename = "index.html"
            else:
                html_filename = filename.replace(".md", ".html")
            
            # 7. 构建输出路径
            if current_dir:
                output_dir = current_dir
                os.makedirs(output_dir, exist_ok=True)
                html_path = os.path.join(output_dir, html_filename)
            else:
                html_path = html_filename
            
            # 8. 标题
            base_title = filename.replace('.md', '')
            full_title = f"{base_title}-TouriCN"
            
            # 9. ✅ 完整 HTML 模板（含防溢出 CSS）
            raw_md_url = f"https://touricn.github.io/{md_path.replace(os.sep, '/')}"
            
            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{full_title}</title>
    <style>
        :root {{
            color-scheme: light dark;
            --bg: Canvas;
            --text: CanvasText;
            --border: CanvasText;
        }}
        html, body {{
            margin: 0;
            padding: 0;
            max-width: 100%;
            overflow-x: hidden;
        }}
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            background: var(--bg);
            color: var(--text);
            padding: 1em;
        }}
        table {{ border-collapse: collapse; margin: 1em 0; }}
        th, td {{ border: 1px solid var(--border); padding: 6px 10px; }}
        pre, code {{ background: rgba(128,128,128,0.15); padding: 2px 6px; border-radius: 4px; }}
        
        img, video, iframe, object {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        
        pre, code {{
            white-space: pre-wrap;
            word-break: break-all;
        }}

        blockquote {{
            margin: 1em 0;
            padding: 10px 15px;
            border-left: 4px solid var(--border);
            background: rgba(128, 128, 128, 0.08);
        }}

        .admonition {{
            border-left: 4px solid var(--border);
            padding: 10px 15px;
            margin: 1em 0;
            background: rgba(128, 128, 128, 0.08);
        }}
        .admonition-title {{
            font-weight: bold;
            margin-bottom: 6px;
        }}

        .theme-switcher {{
            position: fixed; top: 10px; right: 10px; z-index: 999;
            background: var(--bg); border: 1px solid var(--border);
            padding: 4px 8px; font-size: 14px; cursor: pointer; color: var(--text);
        }}

        footer {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid var(--border);
            font-size: 0.9em;
            opacity: 0.7;
        }}
        footer a {{
            color: inherit;
        }}
        .embed-wrapper {
            position: relative;
            min-height: 80vh;
            height: auto;
            margin: 1em 0;
        }

        .embed-content {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <select class="theme-switcher" id="themeSwitcher">
        <option value="system">跟随系统</option>
        <option value="browser">浏览器默认</option>
        <option value="dark">黑色</option>
    </select>
    {html_body}
    <footer>
        <a href="{raw_md_url}" target="_blank">查看原始源码</a>
    </footer>
    <script>
        const s = document.getElementById('themeSwitcher'), r = document.documentElement;
        function setTheme(t) {{ r.setAttribute('data-theme', t); localStorage.setItem('theme', t); s.value = t; }}
        setTheme(localStorage.getItem('theme') || 'system');
        s.onchange = e => setTheme(e.target.value);
    </script>
</body>
</html>"""

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            print(f"✅ Compiled {md_path} -> {html_path}")

if __name__ == "__main__":
    compile_markdown()
