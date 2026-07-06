#!/usr/bin/env python3
"""
Markdown → 微信公众号 HTML 转换器
所有样式内联，兼容微信编辑器。纯 stdlib 实现。

功能：
- Markdown 解析（标题/段落/列表/代码/表格/引用/分割线/图片）
- 3 套主题（tech/minimal/business）
- 自动去除 H1（公众号自带标题）
- 图片自动上传微信素材库（--upload 模式）
- 本地预览（--preview）
- 纯正文 HTML 输出（--body-only，用于 API 推送）
"""
import sys, os, re, json, argparse, html, subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_ROOT / 'assets' / 'templates'

# ============ 主题加载 ============

def load_theme(name):
    path = TEMPLATES_DIR / f'{name}.json'
    if not path.exists():
        sys.stderr.write(f"主题不存在: {path}\n可用主题: tech, minimal, business\n")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)

# ============ Markdown 解析 ============

def escape(text):
    return html.escape(text)

def parse_inline(text):
    """处理行内格式：加粗、斜体、行内代码、链接、图片"""
    text = re.sub(r'`([^`]+)`', lambda m: f'<code style="{{code_inline}}">{escape(m.group(1))}</code>', text)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" style="{img}" />', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1（\2）', text)
    return text

def markdown_to_blocks(md_text):
    lines = md_text.split('\n')
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if not line.strip():
            i += 1; continue
        
        # 代码块
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            blocks.append({'type': 'code', 'lang': lang, 'content': '\n'.join(code_lines)})
            continue
        
        # 标题
        hm = re.match(r'^(#{1,6})\s+(.+)', line)
        if hm:
            level = len(hm.group(1))
            blocks.append({'type': 'heading', 'level': level, 'content': hm.group(2)})
            i += 1; continue
        
        # 分割线
        if re.match(r'^(-{3,}|_{3,}|\*{3,})\s*$', line):
            blocks.append({'type': 'hr'})
            i += 1; continue
        
        # 引用块
        if line.strip().startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            blocks.append({'type': 'blockquote', 'content': '\n'.join(quote_lines)})
            continue
        
        # 无序列表
        if re.match(r'^[\s]*[-*+]\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^[\s]*[-*+]\s+', lines[i]):
                list_items.append(re.sub(r'^[\s]*[-*+]\s+', '', lines[i]))
                i += 1
            blocks.append({'type': 'ul', 'items': list_items})
            continue
        
        # 有序列表
        if re.match(r'^[\s]*\d+\.\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^[\s]*\d+\.\s+', lines[i]):
                list_items.append(re.sub(r'^[\s]*\d+\.\s+', '', lines[i]))
                i += 1
            blocks.append({'type': 'ol', 'items': list_items})
            continue
        
        # 表格
        if '|' in line and i + 1 < len(lines) and re.match(r'^[\s]*\|?[\s]*[-:]+', lines[i+1]):
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'table', 'lines': table_lines})
            continue
        
        # 独立图片行（单独一行只有图片）
        img_match = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if img_match:
            blocks.append({'type': 'image', 'alt': img_match.group(1), 'src': img_match.group(2)})
            i += 1; continue
        
        # 普通段落
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') \
              and not lines[i].strip().startswith('```') and not lines[i].strip().startswith('>') \
              and not re.match(r'^[-*+]\s+', lines[i].strip()) and not re.match(r'^\d+\.\s+', lines[i].strip()) \
              and not re.match(r'^(-{3,}|_{3,}|\*{3,})\s*$', lines[i]):
            para_lines.append(lines[i])
            i += 1
        blocks.append({'type': 'paragraph', 'content': ' '.join(para_lines)})
    
    return blocks

def parse_table(table_lines):
    rows = []
    for idx, line in enumerate(table_lines):
        if idx == 1: continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)
    return rows

# ============ 图片上传 ============

def upload_image_to_weixin(image_path):
    """调用 utils.mjs 上传图片到微信素材库，返回 URL"""
    utils_path = SCRIPT_DIR / 'lib' / 'utils.mjs'
    script = f'''
import {{ uploadArticleImage }} from '{utils_path}';
const r = await uploadArticleImage('{image_path}');
console.log(JSON.stringify(r));
'''
    try:
        result = subprocess.run(
            ['node', '-e', script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return data.get('url', '')
    except Exception as e:
        sys.stderr.write(f"[上传失败] {image_path}: {e}\n")
    return ''

# ============ HTML 生成 ============

def blocks_to_html(blocks, theme, upload=False, base_dir=None):
    s = theme.get('styles', {})
    parts = []
    
    for block in blocks:
        t = block['type']
        
        if t == 'heading':
            level = block['level']
            if level == 1:
                continue  # 公众号自带标题，跳过 H1
            style = s.get(f'h{level}', s.get('h2', ''))
            text = parse_inline(block['content']).format(**s)
            parts.append(f'<h{level} style="{style}">{text}</h{level}>')
        
        elif t == 'paragraph':
            text = parse_inline(block['content']).format(**s)
            parts.append(f'<p style="{s.get("p", "")}">{text}</p>')
        
        elif t == 'image':
            src = block['src']
            alt = block['alt']
            # 本地图片上传
            if upload and not src.startswith('http'):
                local_path = Path(src) if Path(src).is_absolute() else (base_dir / src if base_dir else Path(src))
                if local_path.exists():
                    sys.stderr.write(f"[上传] {local_path.name}...")
                    url = upload_image_to_weixin(str(local_path))
                    if url:
                        src = url
                        sys.stderr.write(f" ✅\n")
                    else:
                        sys.stderr.write(f" ❌ 保留本地路径\n")
            img_style = s.get('img', 'max-width:100%;border-radius:8px;margin:12px 0;')
            parts.append(f'<p style="text-align:center;margin:20px 0;"><img src="{src}" alt="{escape(alt)}" style="{img_style}" /></p>')
        
        elif t == 'code':
            code = escape(block['content'])
            parts.append(f'<pre style="{s.get("pre", "")}"><code style="{s.get("code", "")}">{code}</code></pre>')
        
        elif t == 'blockquote':
            text = parse_inline(block['content']).format(**s)
            parts.append(f'<blockquote style="{s.get("blockquote", "")}">{text}</blockquote>')
        
        elif t == 'ul':
            items = ''.join(f'<li style="{s.get("li", "")}">{parse_inline(item).format(**s)}</li>' for item in block['items'])
            parts.append(f'<ul style="{s.get("ul", "")}">{items}</ul>')
        
        elif t == 'ol':
            items = ''.join(f'<li style="{s.get("li", "")}">{parse_inline(item).format(**s)}</li>' for item in block['items'])
            parts.append(f'<ol style="{s.get("ol", "")}">{items}</ol>')
        
        elif t == 'table':
            rows = parse_table(block['lines'])
            html_rows = []
            for idx, row in enumerate(rows):
                tag = 'th' if idx == 0 else 'td'
                cell_style = s.get('th', '') if idx == 0 else s.get('td', '')
                cells = ''.join(f'<{tag} style="{cell_style}">{parse_inline(c).format(**s)}</{tag}>' for c in row)
                tr_style = s.get('tr_even', '') if idx % 2 == 0 else ''
                html_rows.append(f'<tr style="{tr_style}">{cells}</tr>')
            parts.append(f'<table style="{s.get("table", "")}">{" ".join(html_rows)}</table>')
        
        elif t == 'hr':
            parts.append(f'<hr style="{s.get("hr", "")}" />')
    
    body = '\n'.join(parts)
    wrapper = s.get('wrapper', 'max-width:677px;margin:0 auto;padding:16px 0;')
    return f'<section style="{wrapper}">{body}</section>'

# ============ 主函数 ============

def main():
    parser = argparse.ArgumentParser(description='Markdown → 微信公众号 HTML')
    parser.add_argument('--input', '-i', required=True, help='输入 Markdown 文件')
    parser.add_argument('--output', '-o', help='输出 HTML 文件（默认同名 .html）')
    parser.add_argument('--theme', '-t', default='tech', choices=['tech', 'minimal', 'business'])
    parser.add_argument('--preview', '-p', action='store_true', help='转换后打开预览')
    parser.add_argument('--upload', '-u', action='store_true', help='自动上传本地图片到微信素材库')
    parser.add_argument('--body-only', action='store_true', help='只输出 body 内容（不含 html/head 标签）')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        sys.stderr.write(f"文件不存在: {input_path}\n"); sys.exit(1)
    md_text = input_path.read_text(encoding='utf-8')
    
    theme = load_theme(args.theme)
    blocks = markdown_to_blocks(md_text)
    html_content = blocks_to_html(blocks, theme, upload=args.upload, base_dir=input_path.parent)
    
    if args.body_only:
        full_html = html_content
    else:
        full_html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{input_path.stem}</title></head>
<body style="margin:0;padding:0;background:#f5f5f5;">
{html_content}
</body></html>'''
    
    output_path = Path(args.output) if args.output else input_path.with_suffix('.html')
    output_path.write_text(full_html, encoding='utf-8')
    sys.stderr.write(f"✅ 转换完成: {output_path}\n")
    sys.stderr.write(f"   主题: {args.theme} | 大小: {len(full_html)} 字符\n")
    
    if args.preview:
        import webbrowser
        webbrowser.open(f'file://{output_path.resolve()}')
    
    print(json.dumps({"success": True, "output": str(output_path), "size": len(full_html), "theme": args.theme}))

if __name__ == '__main__':
    main()
