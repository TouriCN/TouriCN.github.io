import re
import os
import subprocess
from datetime import datetime
import markdown
from urllib.parse import urljoin

SITE_URL = "https://touricn.github.io"
SUMMARY = "src/SUMMARY.md"
OUT_FILE = "rss.xml"
SITE_TITLE = "TouriCN"
SITE_DESCRIPTION = "这绝对是史上最神人的站点。"


def get_file_last_commit_date(filepath):
    """获取文件的最后提交时间，返回 RFC 822 格式的日期字符串"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aD", filepath],
            capture_output=True,
            text=True,
            check=True
        )
        date_str = result.stdout.strip()
        if date_str:
            return date_str
    except Exception as e:
        print(f"Warning: Could not get git date for {filepath}: {e}")
    
    # 如果获取失败，返回当前时间
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_markdown_title_and_summary(filepath):
    """读取 markdown 文件，提取标题和摘要"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取第一个标题作为文章标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
        
        # 提取前几段纯文本作为摘要
        lines = content.split('\n')
        text_lines = []
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过代码块
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            
            # 跳过标题、空行、链接、图片等
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            if stripped.startswith('![') or stripped.startswith('['):
                continue
            if stripped.startswith('-') or stripped.startswith('*') or stripped.startswith('+'):
                continue
            
            text_lines.append(stripped)
            if len(text_lines) >= 3:  # 取前3段
                break
        
        summary = ' '.join(text_lines)[:300]  # 限制300字符
        if len(text_lines) >= 3:
            summary += '...'
        
        return title, summary
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return os.path.basename(filepath), ""


def get_markdown_full_content(filepath, base_url):
    """读取 markdown 文件，转换为完整的 HTML 内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 移除评论区部分（从 # 评论区 开始到文件结束）
        content = re.sub(r'\n#\s*评论区.*$', '', content, flags=re.DOTALL)
        
        # 移除 script 标签（评论区脚本等）
        content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # 转换 markdown 为 HTML
        html_content = markdown.markdown(
            content,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )
        
        # 处理相对路径的图片，转换为绝对URL
        def replace_img_src(match):
            src = match.group(1)
            if not src.startswith('http://') and not src.startswith('https://') and not src.startswith('data:'):
                src = urljoin(base_url, src)
            return f'src="{src}"'
        
        html_content = re.sub(r'src="([^"]+)"', replace_img_src, html_content)
        
        # 处理相对路径的链接，转换为绝对URL
        def replace_href(match):
            href = match.group(1)
            if not href.startswith('http://') and not href.startswith('https://') and not href.startswith('#') and not href.startswith('mailto:'):
                href = urljoin(base_url, href)
            return f'href="{href}"'
        
        html_content = re.sub(r'href="([^"]+)"', replace_href, html_content)
        
        return html_content
    except Exception as e:
        print(f"Warning: Could not convert {filepath} to HTML: {e}")
        return ""


def main():
    if not os.path.exists(SUMMARY):
        print(f"ERROR: {SUMMARY} not found!")
        return
    
    with open(SUMMARY, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 匹配所有以 .md 结尾的链接，同时提取标题
    # 格式：- [标题](路径.md)
    pattern = r'-\s*\[(.+?)\]\((\S+\.md)\)'
    matches = re.findall(pattern, content)
    
    items = []
    for title, link in matches:
        title = title.strip()
        # 清理路径：去掉 ./ 前缀
        path = link.lstrip('./')
        full_path = os.path.join("src", path)
        
        if not os.path.exists(full_path):
            print(f"Warning: File not found: {full_path}")
            continue
        
        # 跳过占位链接（标题为 # 的）
        if title == '#':
            continue
        
        # 获取 URL
        if path.endswith('README.md'):
            # README.md 对应目录的 index.html
            url_path = os.path.dirname(path)
            if url_path:
                url = f"{SITE_URL}/{url_path}/"
            else:
                url = f"{SITE_URL}/"
        else:
            # 其他 .md 文件对应同名的 .html 文件
            url_path = os.path.splitext(path)[0]
            url = f"{SITE_URL}/{url_path}.html"
        
        # 获取最后提交时间
        pub_date = get_file_last_commit_date(full_path)
        
        # 读取文件内容，获取更准确的标题和摘要
        file_title, summary = get_markdown_title_and_summary(full_path)
        
        # 获取完整的 HTML 内容
        full_content = get_markdown_full_content(full_path, url)
        
        # 如果 SUMMARY 中的标题只是简短名称，用文件中的完整标题
        if len(file_title) > len(title) and not title.startswith('#'):
            display_title = file_title
        else:
            display_title = title
        
        items.append({
            'title': display_title,
            'link': url,
            'pubDate': pub_date,
            'description': summary,
            'content': full_content
        })
    
    # 按发布日期倒序排列（最新的在前）
    try:
        items.sort(key=lambda x: datetime.strptime(x['pubDate'], "%a, %d %b %Y %H:%M:%S %z"), reverse=True)
    except Exception as e:
        print(f"Warning: Could not sort by date: {e}")
    
    print(f"Found {len(items)} articles from SUMMARY.md:")
    for item in items:
        print(f"  - {item['title']} ({item['pubDate']})")
    
    # 确保输出目录存在
    if os.path.dirname(OUT_FILE):
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
 
    
    # 生成 RSS XML
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">\n')
        f.write('  <channel>\n')
        f.write(f'    <title>{SITE_TITLE}</title>\n')
        f.write(f'    <link>{SITE_URL}</link>\n')
        f.write(f'    <description>{SITE_DESCRIPTION}</description>\n')
        f.write(f'    <language>zh-CN</language>\n')
        f.write(f'    <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>\n')
        f.write(f'    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />\n')
        
        for item in items:
            f.write('    <item>\n')
            f.write(f'      <title><![CDATA[{item["title"]}]]></title>\n')
            f.write(f'      <link>{item["link"]}</link>\n')
            f.write(f'      <pubDate>{item["pubDate"]}</pubDate>\n')
            f.write(f'      <description><![CDATA[{item["description"]}]]></description>\n')
            if item['content']:
                f.write(f'      <content:encoded><![CDATA[{item["content"]}]]></content:encoded>\n')
            f.write('    </item>\n')
        
        f.write('  </channel>\n')
        f.write('</rss>\n')
    
    print(f"SUCCESS: Generated {OUT_FILE} with {len(items)} articles.")


if __name__ == "__main__":
    main()
  
