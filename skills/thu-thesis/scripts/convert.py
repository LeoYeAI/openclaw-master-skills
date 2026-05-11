#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert.py - 清华 MBA 论文 Word → PDF 转换器

新三层架构（AI-native 流程）：
  Step 1: extract_raw.py  → raw_xxx.json（纯机械提取，无 LLM）
  Step 2: AI（Claude）    → struct_xxx.json（阅读骨架，理解章节结构）
  Step 3: build_parsed.py → parsed_xxx.json（纯 Python 组装）
  Step 4: render.py       → LaTeX 项目
  Step 5: xelatex + bibtex → thesis.pdf
  Step 6: AI Rubric 评测  → evaluation_report.md

用法：
  # 第一步：机械提取，输出骨架供 AI 阅读
  python3 convert.py extract <input.docx> [output_dir]

  # 第三步（AI 生成 struct.json 后）：完成转换
  python3 convert.py build <raw_json> <struct_json> [latex_dir]

  # 或一步调用（需要已有 struct.json）：
  python3 convert.py build raw_xxx.json struct_xxx.json ./my-thesis

AI（Claude）负责：
  - 读取 extract 输出的骨架
  - 生成 struct_xxx.json（章节划分、段落 idx 映射）
  - 调用 build 命令完成剩余步骤
"""

import sys
import os
import re
import subprocess
from pathlib import Path


# ── 自动补全未引用文献 ──────────────────────────────────────────────────────────

def _auto_cite_missing(latex_dir: Path):
    """检测 refs.bib 中未被正文引用的文献，关键词匹配补 \\cite；无匹配用 \\nocite 兜底。"""
    bib_file = latex_dir / 'ref' / 'refs.bib'
    if not bib_file.exists():
        return

    bib_text = bib_file.read_text(encoding='utf-8')
    entries = {}
    for m in re.finditer(r'@\w+\{(\w+),(.*?)^\}', bib_text, re.MULTILINE | re.DOTALL):
        key = m.group(1)
        block = m.group(2)
        title_m = re.search(r'title\s*=\s*\{(.+?)\}', block, re.DOTALL)
        author_m = re.search(r'author\s*=\s*\{(.+?)\}', block, re.DOTALL)
        year_m = re.search(r'year\s*=\s*\{(\d+)\}', block)
        entries[key] = {
            'title': title_m.group(1).replace('\n', ' ').strip() if title_m else '',
            'author': author_m.group(1).replace('\n', ' ').strip() if author_m else '',
            'year': year_m.group(1) if year_m else '',
        }

    if not entries:
        return

    chap_files = sorted(latex_dir.glob('data/chap*.tex'))
    cited_keys = set()
    for cf in chap_files:
        for m in re.finditer(r'\\cite\{([^}]+)\}', cf.read_text(encoding='utf-8')):
            for k in m.group(1).split(','):
                cited_keys.add(k.strip())

    missing = [k for k in entries if k not in cited_keys]
    if not missing:
        print(f'   ✅ 所有 {len(entries)} 条文献均已被引用')
        return

    print(f'   发现 {len(missing)} 条未引用文献，进行关键词匹配...')

    def _extract_keywords(key):
        e = entries[key]
        text = e['title'] + ' ' + e['author']
        zh_words = re.findall(r'[\u4e00-\u9fff]{3,}', text)
        stopwords = {'with', 'from', 'that', 'this', 'their', 'have', 'been', 'into',
                     'drug', 'price', 'pricing', 'china', 'market', 'company', 'strategy'}
        en_words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', text)
                    if w.lower() not in stopwords]
        return zh_words[:3] + en_words[:3]

    inserted = {}
    used_sentences = set()
    for key in missing:
        keywords = _extract_keywords(key)
        if not keywords:
            continue
        best_match = None
        best_score = 0
        for cf in chap_files:
            content = cf.read_text(encoding='utf-8')
            for line_m in re.finditer(r'^([^%\\][^\n]{10,}[。！？])', content, re.MULTILINE):
                line = line_m.group(1)
                if line in used_sentences:
                    continue
                score = sum(1 for kw in keywords if kw.lower() in line.lower())
                if score > best_score:
                    best_score = score
                    best_match = (cf, line)
        if best_match and best_score > 0:
            cf, matched_line = best_match
            last_punct = max(matched_line.rfind('。'), matched_line.rfind('！'), matched_line.rfind('？'))
            if last_punct < 0:
                continue
            prefix = matched_line[:last_punct]
            suffix = matched_line[last_punct:]
            existing_cite_m = re.search(r'\\cite\{([^}]+)\}$', prefix)
            if existing_cite_m:
                old_cite = existing_cite_m.group(0)
                new_cite = old_cite.replace('}', f',{key}}}')
                new_line = prefix[:existing_cite_m.start()] + new_cite + suffix
            else:
                new_line = prefix + f'\\cite{{{key}}}' + suffix
            inserted[key] = (cf, matched_line, new_line)
            used_sentences.add(matched_line)

    success = 0
    for key, (cf, old_text, new_text) in inserted.items():
        content = cf.read_text(encoding='utf-8')
        if old_text in content:
            cf.write_text(content.replace(old_text, new_text, 1), encoding='utf-8')
            print(f'   ✓ {key}: 插入 → {cf.name}')
            success += 1

    still_missing = [k for k in missing if k not in inserted]
    if still_missing:
        print(f'   {len(still_missing)} 条无关键词匹配，用 \\nocite 强制输出...')
        thesis_tex = latex_dir / 'thesis.tex'
        if thesis_tex.exists():
            content = thesis_tex.read_text(encoding='utf-8')
            nocite_lines = '\n'.join(f'\\nocite{{{k}}}' for k in still_missing)
            marker = '\\bibliographystyle{'
            if marker in content:
                content = content.replace(marker, nocite_lines + '\n' + marker, 1)
                thesis_tex.write_text(content, encoding='utf-8')

    print(f'   完成：{success + len(still_missing)}/{len(missing)} 条文献已补全引用')


# ── 编译 PDF ──────────────────────────────────────────────────────────────────

def compile_pdf(latex_dir: Path) -> Path:
    """运行 xelatex + bibtex 完整编译流程，返回 PDF 路径。"""
    _tex_bin = os.environ.get('XELATEX_PATH', '')
    if _tex_bin:
        extra_path = str(Path(_tex_bin).parent)
    elif Path('/Library/TeX/texbin/xelatex').exists():
        extra_path = '/Library/TeX/texbin'
    elif Path('/usr/local/texlive/2025basic/bin/universal-darwin/xelatex').exists():
        extra_path = '/usr/local/texlive/2025basic/bin/universal-darwin'
    else:
        extra_path = ''

    env = os.environ.copy()
    if extra_path:
        env['PATH'] = extra_path + ':' + env.get('PATH', '')

    def xelatex():
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', 'thesis.tex'],
            cwd=latex_dir, env=env,
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if any(k in line for k in ['Error', 'error', 'Fatal', '!']):
                if 'Font Warning' not in line and 'microtype' not in line:
                    print(f'   {line}')
        return result.returncode

    def toc_hash():
        import hashlib
        toc = latex_dir / 'thesis.toc'
        return hashlib.md5(toc.read_bytes()).hexdigest() if toc.exists() else ''

    print('   第 1 次编译（生成 .aux）...')
    xelatex()

    print('   运行 bibtex...')
    subprocess.run(['bibtex', 'thesis'], cwd=latex_dir, env=env,
                   capture_output=True, text=True)

    print('   第 2 次编译（写入参考文献）...')
    xelatex()
    h2 = toc_hash()

    print('   第 3 次编译（稳定目录）...')
    xelatex()
    h3 = toc_hash()

    if h3 != h2:
        print('   第 4 次编译（目录稳定中）...')
        xelatex()

    return latex_dir / 'thesis.pdf'


# ── 子命令：extract ────────────────────────────────────────────────────────────

def cmd_extract(args):
    """
    Step 1: Word → raw_xxx.json（机械提取）
    同时确定并创建 LaTeX 工程目录（<docx同目录>/<stem>-latex/），
    输出骨架文本供 AI 阅读，生成 struct.json 后调用 build。
    """
    if not args:
        print('用法: python3 convert.py extract <input.docx> [output_dir]')
        sys.exit(1)

    docx_path = Path(args[0]).resolve()
    if not docx_path.exists():
        print(f'❌ 找不到文件: {docx_path}')
        sys.exit(1)

    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    output_dir = Path(args[1]).resolve() if len(args) >= 2 else project_root / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 在项目开始时就确定并创建 LaTeX 工程目录 ──
    stem = docx_path.stem
    latex_dir = docx_path.parent / f'{stem}-latex'
    latex_dir.mkdir(parents=True, exist_ok=True)

    print(f'\n{"="*60}')
    print(f'📄 输入: {docx_path}')
    print(f'📁 中间文件: {output_dir}')
    print(f'📁 LaTeX 工程: {latex_dir}')
    print(f'{"="*60}\n')

    print('【Step 1】机械提取 Word 文档...')
    result = subprocess.run(
        [sys.executable, str(scripts_dir / 'extract_raw.py'), str(docx_path), str(output_dir)],
        capture_output=False
    )
    if result.returncode != 0:
        print('❌ extract_raw.py 失败')
        sys.exit(1)

    # 找输出的 raw json
    raw_files = sorted(output_dir.glob('raw_*.json'), key=lambda f: f.stat().st_mtime, reverse=True)
    if not raw_files:
        print('❌ 未找到 raw_*.json 输出')
        sys.exit(1)
    raw_path = raw_files[0]

    # 打印骨架供 AI 阅读
    print(f'\n{"="*60}')
    print(f'✅ 提取完成: {raw_path.name}')
    print(f'{"="*60}')
    print('\n📋 文档骨架（供 AI 阅读，生成 struct.json）：\n')

    import json
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    paras = raw.get('paragraphs', [])
    figures = raw.get('figures', [])
    tables = raw.get('tables', [])
    skip_styles = {'toc 1', 'toc 2', 'toc 3', 'toc1', 'toc2', 'toc3', 'toc'}
    for p in paras:
        style = p.get('style', '').strip().lower()
        if style in skip_styles:
            continue
        text = p.get('text', '').strip()
        if not text:
            continue
        print(f"{p['idx']:04d} [{p.get('style', ''):18s}] {text[:70]}")

    print(f'\n{"="*60}')
    print(f'📊 图片: {len(figures)} 张  | 图片 para_idx: {[f["para_idx"] for f in figures]}')
    print(f'📊 表格: {len(tables)} 张  | 表格 before_para: {[t["before_para"] for t in tables]}')

    # ── 检测 .doc 转换工具是否破坏了表格结构 ──
    if len(tables) == 0:
        # 检测骨架里是否有疑似表格的段落（如"序号"+"股东名称"相邻或含多个数字列）
        table_hint_patterns = ['序号', '表头', '合计', '股东名称', '持股', '占比', '金额（万元）']
        tbl_hint_count = sum(1 for p in paras if any(kw in p.get('text','') for kw in table_hint_patterns))
        if tbl_hint_count >= 3:
            print(f'\n{"!"*60}')
            print('⚠️  警告：提取到 0 张表格，但骨架中检测到疑似表格内容（如"序号"、"合计"等）！')
            print('   这通常是因为用了 textutil 等工具转换 .doc，表格被压平成了普通段落。')
            print('   这些表格内容将以纯文本形式出现在正文中，严重影响论文质量。')
            print('   解决方案：用 Microsoft Word 打开 .doc，另存为 .docx，然后重新运行 extract。')
            print(f'{"!"*60}')
        elif len(figures) == 0:
            print('   ℹ️  论文无图片和表格（纯文字论文），属于正常情况。')
    print(f'{"="*60}')
    print(f'\n📝 下一步：')
    print(f'   1. AI 读取上方骨架，生成 struct.json（写到 {output_dir}/struct_{stem}.json）')
    print(f'      ⚠️  确保所有图片 para_idx 和表格 before_para 都在 content_range 内！')
    print(f'   2. 运行 build：')
    print(f'      python3 convert.py build {raw_path} {output_dir}/struct_{stem}.json {latex_dir}')
    print(f'{"="*60}\n')


# ── 子命令：build ─────────────────────────────────────────────────────────────

def cmd_build(args):
    """
    Step 3-6: raw_json + struct_json → parsed_json → LaTeX → PDF → 评测
    """
    if len(args) < 2:
        print('用法: python3 convert.py build <raw_json> <struct_json> [latex_dir]')
        sys.exit(1)

    raw_path = Path(args[0]).resolve()
    struct_path = Path(args[1]).resolve()
    if not raw_path.exists():
        print(f'❌ 找不到: {raw_path}')
        sys.exit(1)
    if not struct_path.exists():
        print(f'❌ 找不到: {struct_path}')
        sys.exit(1)

    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    output_dir = project_root / 'output'

    # latex_dir 默认用 struct 文件名推断
    stem = raw_path.stem.removeprefix('raw_')
    latex_dir = Path(args[2]).resolve() if len(args) >= 3 else Path(f'./{stem}-latex')

    print(f'\n{"="*60}')
    print(f'📄 raw:    {raw_path.name}')
    print(f'📄 struct: {struct_path.name}')
    print(f'📁 输出:   {latex_dir}')
    print(f'{"="*60}\n')

    # Step 3: build_parsed
    print('【Step 3】组装 parsed JSON...')
    result = subprocess.run(
        [sys.executable, str(scripts_dir / 'build_parsed.py'),
         str(raw_path), str(struct_path), str(output_dir)],
        capture_output=False
    )
    if result.returncode != 0:
        print('❌ build_parsed.py 失败')
        sys.exit(1)

    parsed_files = sorted(output_dir.glob('parsed_*.json'),
                          key=lambda f: f.stat().st_mtime, reverse=True)
    if not parsed_files:
        print('❌ 未找到 parsed_*.json')
        sys.exit(1)
    parsed_path = parsed_files[0]
    print(f'   → {parsed_path.name}')

    # Step 4: render
    print('\n【Step 4】渲染 LaTeX 项目...')
    result = subprocess.run(
        [sys.executable, str(scripts_dir / 'render.py'), str(parsed_path), str(latex_dir)],
        capture_output=False
    )
    if result.returncode != 0:
        print('❌ render.py 失败')
        sys.exit(1)

    # Step 4.5: 自动补全未引用文献
    print('\n【Step 4.5】检测未引用文献并自动补全 \\cite{}...')
    _auto_cite_missing(latex_dir)

    # Step 5: 编译 PDF
    print('\n【Step 5】编译 PDF...')
    pdf_path = compile_pdf(latex_dir)

    if not pdf_path.exists():
        print(f'\n❌ PDF 未生成，请检查 {latex_dir}/thesis.log')
        sys.exit(1)

    size_kb = pdf_path.stat().st_size // 1024
    print(f'\n{"="*60}')
    print(f'✅ 完成！PDF 已生成: {pdf_path}  ({size_kb} KB)')
    print(f'{"="*60}\n')

    # Step 6: Rubric 评测由 AI 执行，此处仅提示路径
    print('\n【Step 6】Rubric 评测（由 AI 执行）')
    print(f'   parsed JSON : {parsed_path}')
    print(f'   LaTeX 工程  : {latex_dir}')
    print('   请 AI 按 SKILL.md 中的 Rubric 细则逐项评测，并输出 evaluation_report.md')

    import platform
    if platform.system() == 'Darwin':
        subprocess.run(['open', str(pdf_path)], check=False)


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    subcmd = sys.argv[1]
    rest = sys.argv[2:]

    if subcmd == 'extract':
        cmd_extract(rest)
    elif subcmd == 'build':
        cmd_build(rest)
    else:
        print(f'❌ 未知子命令: {subcmd}')
        print('可用命令: extract | build')
        sys.exit(1)


if __name__ == '__main__':
    main()
