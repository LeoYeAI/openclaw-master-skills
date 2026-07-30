"""
reformat.py — 一键重排版：读取任意 .docx → 输出规范排版的新 .docx

用法：
    python3 reformat.py input.docx [output.docx] [--type TECH_MANUAL] [--dry-run]

参数：
    input.docx    输入文件（任意 Word 文档）
    output.docx   输出文件（可选，默认为 input_reformatted.docx）
    --type        强制指定文档类型（可选，默认自动推断）
    --dry-run     只打印提取的 Markdown，不生成文档（用于验证提取结果）
    --show-md     生成文档后也打印 Markdown

OpenClaw 集成用法（Skill 内调用）：
    from reformat import reformat
    result = reformat("input.docx", "output.docx", doc_type="TECH_MANUAL")
"""

import sys
import os
import argparse
from pathlib import Path

_SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(_SKILL_DIR))

from docx_reader import extract, to_markdown, summary
from converter import DocxConverter, DOC_TYPE_MAP


# ══════════════════════════════════════════════════════════════
# 核心：提取内容 → 构建 DocxConverter → 输出
# ══════════════════════════════════════════════════════════════

def reformat(input_path: str,
             output_path: str = None,
             doc_type: str = None,
             dry_run: bool = False,
             show_md: bool = False) -> dict:
    """
    读取 input_path (.docx)，重新排版后输出到 output_path。

    返回 dict：
        success    bool
        output     输出路径
        doc_type   使用的文档类型
        stats      提取统计
        markdown   生成的 Markdown（show_md=True 时）
    """
    input_path  = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在：{input_path}")

    # 默认输出路径
    if output_path is None:
        output_path = input_path.parent / (input_path.stem + "_reformatted.docx")
    output_path = Path(output_path)

    # ── 第一步：提取 ────────────────────────────────────────
    print(f"📖 读取：{input_path.name}")
    extracted = extract(str(input_path))
    print(f"   提取结果：{summary(extracted)}")

    # ── 第二步：确定文档类型 ────────────────────────────────
    if doc_type is None:
        doc_type = extracted["doc_hint"]
        print(f"   自动推断类型：{doc_type}")
    else:
        print(f"   指定类型：{doc_type}")

    # ── 第三步：构建 DocxConverter 并填充内容 ───────────────
    conv = DocxConverter(doc_type)
    blocks = extracted["blocks"]

    # 标题
    title_block = next((b for b in blocks if b["type"]=="heading" and b["level"]==0), None)
    if title_block:
        conv.title(title_block["text"])
    elif extracted["title"]:
        conv.title(extracted["title"])

    # 收集副标题（第一个 level=1 之前的正文，通常是副标题/简介）
    first_h1_idx = next((i for i,b in enumerate(blocks) if b["type"]=="heading" and b["level"]==1), len(blocks))
    pre_blocks = [b for b in blocks[:first_h1_idx] if b["type"]=="body" and b.get("level",0)==0]
    if pre_blocks:
        conv.subtitle(pre_blocks[0]["text"])

    # 主体内容
    i = 0
    while i < len(blocks):
        b = blocks[i]
        t = b["type"]

        if t == "heading":
            lvl = b["level"]
            text = b["text"]
            if lvl == 0:
                i += 1; continue  # 已处理
            elif lvl == 1: conv.h1(text)
            elif lvl == 2: conv.h2(text)
            elif lvl == 3: conv.h3(text)
            else:          conv.h4(text)

        elif t == "body":
            text = b["text"]
            # 跳过已作为副标题处理的段落
            if i < first_h1_idx and text == (pre_blocks[0]["text"] if pre_blocks else None):
                i += 1; continue
            # 检测警告/注意段落
            if re.match(r'^(注意|警告|警示|⚠|注|Warning|Caution)[：:！!]', text):
                conv.warning(text)
            # 检测摘要
            elif re.match(r'^摘要[：:]', text):
                # 提取关键词（下一个 block 如果是"关键词："开头）
                kw = None
                if i+1 < len(blocks) and re.match(r'^关键词[：:]', blocks[i+1].get("text","")):
                    kw = blocks[i+1]["text"]
                    i += 1
                conv.abstract(re.sub(r'^摘要[：:]','',text).strip(), keywords=kw)
            # 检测落款/签名行
            elif re.match(r'.*(签字|盖章|日期|年.*月.*日|签名|落款)', text) and len(text) < 60:
                conv.signature_block(text)
            else:
                conv.body(text)

        elif t == "bullet":
            conv.bullet(b["text"], level=b.get("level",0))

        elif t == "numbered":
            conv.numbered(b["text"], level=b.get("level",0))

        elif t == "code":
            # 尝试识别语言
            lang = _detect_lang(b["text"])
            conv.code_block(b["text"], lang=lang)

        elif t == "table":
            # 检测前一个是否为表题
            caption = None
            if i > 0 and blocks[i-1]["type"] == "body":
                prev = blocks[i-1]["text"]
                if re.match(r'^表\d|^Table', prev):
                    caption = prev
            conv.table(b["headers"], b["rows"], caption=caption)

        elif t == "divider":
            conv.divider()

        i += 1

    # ── Dry run：只打印 Markdown ────────────────────────────
    md = conv.to_markdown()
    if dry_run:
        print("\n" + "─"*60)
        print("Markdown 预览（dry-run）：")
        print("─"*60)
        print(md)
        return {"success": True, "output": None, "doc_type": doc_type,
                "stats": extracted["stats"], "markdown": md}

    if show_md:
        print("\n" + "─"*60 + "\nMarkdown:\n" + "─"*60)
        print(md[:2000] + ("..." if len(md)>2000 else ""))

    # ── 第四步：生成输出 ────────────────────────────────────
    print(f"\n🔄 排版中 → {output_path.name}")
    conv.save(str(output_path))

    return {
        "success":  True,
        "output":   str(output_path),
        "doc_type": doc_type,
        "stats":    extracted["stats"],
        "markdown": md if show_md else None,
    }


import re

def _detect_lang(code: str) -> str:
    """简单代码语言检测"""
    if re.search(r'\bimport\b|\bdef\b|\bclass\b|\bprint\b\(', code): return "python"
    if re.search(r'\bfunction\b|\bconst\b|\blet\b|\bvar\b|\bconsole\.', code): return "javascript"
    if re.search(r'\bpublic\b|\bprivate\b|\bvoid\b|\bString\b', code): return "java"
    if re.search(r'^\s*#include|^\s*int main', code, re.M): return "c"
    if re.search(r'\bSELECT\b|\bFROM\b|\bWHERE\b', code, re.I): return "sql"
    if re.search(r'^\s*\$|^\s*apt|^\s*pip|^\s*conda|^\s*git', code, re.M): return "bash"
    return ""


# ══════════════════════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="重排版 Word 文档：读取任意 .docx，输出规范排版的新 .docx",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 reformat.py report.docx                          # 自动推断类型
  python3 reformat.py report.docx out.docx --type GOV_DOC  # 指定类型
  python3 reformat.py report.docx --dry-run                # 只预览提取结果
  python3 reformat.py report.docx --show-md                # 生成并显示 Markdown

支持的文档类型：
  GOV_DOC / GOV_JUDICIAL / BUSINESS_CONTRACT / BUSINESS_TENDER /
  BUSINESS_PLAN / ACADEMIC_PAPER / ACADEMIC_LESSON / TECH_SRS /
  TECH_MANUAL / MEDICAL_RECORD / MEDICAL_DRUG / MARKETING_PLAN /
  MARKETING_ANALYSIS / LEGAL_OPINION / LEGAL_LITIGATION /
  FINANCE_REPORT / ENGINEERING_DOC / GENERAL_DOC
        """
    )
    parser.add_argument("input",  help="输入 .docx 文件路径")
    parser.add_argument("output", nargs="?", help="输出 .docx 文件路径（可选）")
    parser.add_argument("--type", dest="doc_type", default=None,
                        help="强制指定文档类型（可选，默认自动推断）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印提取的 Markdown，不生成文档")
    parser.add_argument("--show-md", action="store_true",
                        help="生成文档后也打印 Markdown 内容")

    args = parser.parse_args()

    try:
        result = reformat(
            input_path  = args.input,
            output_path = args.output,
            doc_type    = args.doc_type,
            dry_run     = args.dry_run,
            show_md     = args.show_md,
        )
        if result["success"] and result["output"]:
            print(f"\n✅ 完成！输出：{result['output']}")
            print(f"   类型：{result['doc_type']} | 统计：{result['stats']}")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
