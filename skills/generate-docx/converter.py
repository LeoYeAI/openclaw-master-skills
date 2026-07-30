"""
converter.py — OpenClaw docx-output Skill v4.1 核心转换器
架构：Markdown（语义层）→ Pandoc + reference.docx（渲染层）→ .docx

v4.1 相对 v4.0 补全的缺口（依据《Word文档类型与风格指南》）：
  + abstract(text, keywords)     学术摘要（仿宋、左右缩进2字符）
  + module_heading(name)         药品说明书【模块名称】
  + warning(text)                警告提示（红色加粗 ⚠）
  + signature_block(*lines)      落款/签名区（仿宋四号居中）
  + figure_caption(text)         图题（置图下方，五号仿宋居中）
  + footnote_ref(text, note)     脚注引用（学术引文，小五号）
  + toc_entry(text, page, level) 目录条目（带点线前导符）
  + h4(text)                     四级标题 (1)(2)(3)（公文规范第四级）
  + highlight(text)              点缀色高亮文字
  + 英文字体规范                  正式文档用TNR，技术文档用Calibri
  + 图表自动编号                  fig_counter / tbl_counter（章节独立）
  + 首页不显示页码                模板 first_page_no_footer
"""

import os
import re
import subprocess
from pathlib import Path

_SKILL_DIR    = Path(__file__).parent
_TEMPLATE_DIR = _SKILL_DIR / "templates"

# ══════════════════════════════════════════════════════════════
# 文档类型 → 模板映射（完整19种）
# ══════════════════════════════════════════════════════════════
DOC_TYPE_MAP = {
    "GOV_DOC":            "GOV_DOC",
    "GOV_JUDICIAL":       "GOV_JUDICIAL",
    "GOV_DIPLOMATIC":     "GOV_JUDICIAL",
    "BUSINESS_CONTRACT":  "BUSINESS_CONTRACT",
    "BUSINESS_TENDER":    "BUSINESS_TENDER",
    "BUSINESS_PLAN":      "BUSINESS_PLAN",
    "ACADEMIC_PAPER":     "ACADEMIC_PAPER",
    "ACADEMIC_LESSON":    "ACADEMIC_LESSON",
    "TECH_SRS":           "TECH_MANUAL",
    "TECH_MANUAL":        "TECH_MANUAL",
    "MEDICAL_RECORD":     "MEDICAL_DOC",
    "MEDICAL_DRUG":       "MEDICAL_DOC",
    "MARKETING_PLAN":     "MARKETING_DOC",
    "MARKETING_ANALYSIS": "MARKETING_DOC",
    "LEGAL_OPINION":      "LEGAL_DOC",
    "LEGAL_LITIGATION":   "LEGAL_DOC",
    "FINANCE_REPORT":     "FINANCE_REPORT",
    "ENGINEERING_DOC":    "ENGINEERING_DOC",
    "GENERAL_DOC":        "GENERAL_DOC",
}

# ══════════════════════════════════════════════════════════════
# 各类型序号风格
# ══════════════════════════════════════════════════════════════
DOC_PREFIX = {
    "GOV_DOC":           {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "GOV_JUDICIAL":      {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "BUSINESS_CONTRACT": {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "BUSINESS_TENDER":   {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "BUSINESS_PLAN":     {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "ACADEMIC_PAPER":    {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "ACADEMIC_LESSON":   {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "TECH_MANUAL":       {"h1":"num", "h2":"num2","h3":"num3","h4":"num4"},
    "MARKETING_DOC":     {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "LEGAL_DOC":         {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "FINANCE_REPORT":    {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "ENGINEERING_DOC":   {"h1":"num", "h2":"num2","h3":"dec", "h4":"paren"},
    "MEDICAL_DOC":       {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
    "GENERAL_DOC":       {"h1":"cn",  "h2":"cn2", "h3":"dec", "h4":"paren"},
}

# ══════════════════════════════════════════════════════════════
# 智能序号检测（防止双重编号）
# ══════════════════════════════════════════════════════════════
_NUMBERING_RE = [
    re.compile(r'^[一二三四五六七八九十百]+[、．.]'),
    re.compile(r'^[（(][一二三四五六七八九十]+[）)]'),
    re.compile(r'^\d+[.．]\d+'),
    re.compile(r'^\d+[.．]\s'),
    re.compile(r'^\(\d+\)'),
    re.compile(r'^（\d+）'),
    re.compile(r'^第[一二三四五六七八九十百\d]+[章节条款]'),
    re.compile(r'^[【\[][^\]】]+[】\]]'),
    re.compile(r'^[A-Za-z][.．]\d'),
    re.compile(r'^\d+[.．][^\d\s]'),
]

def _has_number(text):
    s = text.strip()
    return any(p.match(s) for p in _NUMBERING_RE)

# 序号字符串
_CN1 = ["一","二","三","四","五","六","七","八","九","十",
        "十一","十二","十三","十四","十五"]
_CN2 = ["一","二","三","四","五","六","七","八","九","十"]

class _Counter:
    def __init__(self):
        self.reset()
    def reset(self):
        self.h1=self.h2=self.h3=self.h4=0
        self.fig=self.tbl=0          # 图表计数
        self._fn_idx=0               # 脚注计数
    def reset_sub(self):
        self.h2=self.h3=self.h4=0
    def reset_h3h4(self):
        self.h3=self.h4=0
    def reset_h4(self):
        self.h4=0

    def pfx_h1(self, style, text):
        if _has_number(text): self.reset_sub(); return text
        self.h1+=1; self.h2=self.h3=self.h4=0; n=self.h1
        if style in ("cn","gov"): return f"{_CN1[n-1]}、{text}"
        if style=="num": return f"{n}. {text}"
        return text

    def pfx_h2(self, style, text):
        if _has_number(text): self.reset_h3h4(); return text
        self.h2+=1; self.h3=self.h4=0; n=self.h2
        if style in ("cn2","gov2"): return f"（{_CN2[n-1]}）\u3000{text}"
        if style=="num2": return f"{self.h1}.{n} {text}"
        return text

    def pfx_h3(self, style, text):
        if _has_number(text): self.reset_h4(); return text
        self.h3+=1; self.h4=0; n=self.h3
        if style=="dec": return f"{n}. {text}"
        if style=="num3": return f"{self.h1}.{self.h2}.{n} {text}"
        return text

    def pfx_h4(self, style, text):
        if _has_number(text): return text
        self.h4+=1; n=self.h4
        if style=="paren": return f"（{n}）\u3000{text}"
        if style=="num4": return f"{self.h1}.{self.h2}.{self.h3}.{n} {text}"
        return text

    def next_fig(self):
        self.fig+=1; return self.fig
    def next_tbl(self):
        self.tbl+=1; return self.tbl
    def next_fn(self):
        self._fn_idx+=1; return self._fn_idx


# ══════════════════════════════════════════════════════════════
# DocxConverter 主类
# ══════════════════════════════════════════════════════════════

class DocxConverter:
    """
    将结构化内容转换为 Markdown，由 Pandoc + reference.docx 渲染为 docx。

    快速开始：
        from converter import DocxConverter
        c = DocxConverter("TECH_MANUAL")
        c.title("AI学习与开发实用手册")
        c.h1("AI学习基础篇")
        c.body("正文...")
        c.numbered("数学基础")    # → 1
        c.numbered("编程技能")    # → 2
        c.h1("机器学习")
        c.numbered("监督学习")    # → 1（自动重置！）
        c.save("output.docx")
    """

    def __init__(self, doc_type: str = "GENERAL_DOC"):
        tpl_key = DOC_TYPE_MAP.get(doc_type, "GENERAL_DOC")
        self.template = _TEMPLATE_DIR / f"template_{tpl_key}.docx"
        if not self.template.exists():
            self.template = _TEMPLATE_DIR / "template_GENERAL_DOC.docx"

        pfx = DOC_PREFIX.get(tpl_key, DOC_PREFIX["GENERAL_DOC"])
        self._p1 = pfx["h1"]; self._p2 = pfx["h2"]
        self._p3 = pfx["h3"]; self._p4 = pfx["h4"]

        self._ctr    = _Counter()
        self._blocks = []
        self._in_list   = None   # None | "bullet" | "numbered"
        self._footnotes = []     # [(anchor, text), ...]

    # ── 私有：列表边界 ───────────────────────────────────────
    def _end_list(self):
        if self._in_list:
            self._blocks.append("")
            self._in_list = None

    def _section_break(self):
        """标题/段落调用时，终止列表"""
        self._end_list()

    # ══════════════════════════════════════════════════════════
    # 公开 API
    # ══════════════════════════════════════════════════════════

    def title(self, text: str) -> "DocxConverter":
        """文档主标题"""
        self._blocks.append(f"% {text}")
        return self

    def subtitle(self, text: str) -> "DocxConverter":
        """副标题（显示为斜体段落，位于标题下方）"""
        self._blocks.append(f"\n*{text}*\n")
        return self

    def h1(self, text: str, auto_number: bool = True) -> "DocxConverter":
        self._section_break()
        d = self._ctr.pfx_h1(self._p1, text) if auto_number else text
        self._blocks.append(f"\n# {d}\n")
        return self

    def h2(self, text: str, auto_number: bool = True) -> "DocxConverter":
        self._section_break()
        d = self._ctr.pfx_h2(self._p2, text) if auto_number else text
        self._blocks.append(f"\n## {d}\n")
        return self

    def h3(self, text: str, auto_number: bool = True) -> "DocxConverter":
        self._section_break()
        d = self._ctr.pfx_h3(self._p3, text) if auto_number else text
        self._blocks.append(f"\n### {d}\n")
        return self

    def h4(self, text: str, auto_number: bool = True) -> "DocxConverter":
        """四级标题（公文规范第四层 (1)(2)(3)）"""
        self._section_break()
        d = self._ctr.pfx_h4(self._p4, text) if auto_number else text
        self._blocks.append(f"\n#### {d}\n")
        return self

    def body(self, text: str) -> "DocxConverter":
        """正文段落（支持 Markdown 行内语法：**加粗** *斜体* `代码`）"""
        self._end_list()
        self._blocks.append(f"\n{text}\n")
        return self

    def bullet(self, text: str, level: int = 0) -> "DocxConverter":
        """项目符号列表（•）"""
        if self._in_list == "numbered":
            self._end_list()
        self._in_list = "bullet"
        self._blocks.append("  " * level + f"- {text}")
        return self

    def numbered(self, text: str, level: int = 0) -> "DocxConverter":
        """
        编号列表。每次 h1/h2/h3/body 调用后，下一个 numbered 自动从1重置。
        Pandoc 对每个独立列表块天然从1计数，无需任何额外操作。
        """
        if self._in_list == "bullet":
            self._end_list()
        self._in_list = "numbered"
        self._blocks.append("   " * level + f"1. {text}")
        return self

    def abstract(self, text: str, keywords: str = None) -> "DocxConverter":
        """
        学术摘要（ACADEMIC_PAPER 专用）。
        输出小四号仿宋，左右缩进2字符，1.25倍行距。
        Pandoc 中用 blockquote 近似实现缩进效果。
        keywords 示例："数字孪生；智慧城市；物联网"
        """
        self._end_list()
        self._blocks.append(f"\n> **摘要：**{text}\n")
        if keywords:
            self._blocks.append(f"\n> **关键词：**{keywords}\n")
        return self

    def module_heading(self, name: str) -> "DocxConverter":
        """
        药品说明书专用：【模块名称】格式标题。
        示例：c.module_heading("药品名称")  →  **【药品名称】**
        """
        self._section_break()
        self._blocks.append(f"\n**【{name}】**\n")
        return self

    def warning(self, text: str) -> "DocxConverter":
        """
        警告/提示段落（用户手册、药品说明书等）。
        输出红色加粗，用 Markdown 粗体 + emoji 近似实现。
        """
        self._end_list()
        self._blocks.append(f"\n**⚠ {text}**\n")
        return self

    def signature_block(self, *lines: str) -> "DocxConverter":
        """
        落款/签名区（合同、法律文书、公文尾部）。
        仿宋四号居中，自动上方留空白。
        用 Pandoc 居中段落实现。
        示例：c.signature_block("甲方：___________", "日期：___年___月___日")
        """
        self._end_list()
        self._blocks.append("")
        for line in lines:
            self._blocks.append(f"\n::: {{.center}}\n{line}\n:::\n")
        return self

    def figure_caption(self, text: str, auto_number: bool = True) -> "DocxConverter":
        """
        图题（置于图片下方，五号仿宋居中）。
        auto_number=True 时自动生成"图N  "前缀，按文档全局计数。
        示例：c.figure_caption("系统架构示意图")  →  *图1  系统架构示意图*
        """
        self._end_list()
        if auto_number:
            n = self._ctr.next_fig()
            display = f"图{n}\u3000{text}"
        else:
            display = text
        self._blocks.append(f"\n*{display}*\n")
        return self

    def table_caption(self, text: str, auto_number: bool = True,
                      above: bool = True) -> "DocxConverter":
        """
        表题（默认置于表格上方，五号仿宋居中）。
        auto_number=True 时自动生成"表N  "前缀。
        若 above=False 则置于表格下方（图表规范：图题下置，表题上置）。
        一般在 table() 之前调用（above=True）或之后调用（above=False）。
        """
        self._end_list()
        if auto_number:
            n = self._ctr.next_tbl()
            display = f"表{n}\u3000{text}"
        else:
            display = text
        self._blocks.append(f"\n*{display}*\n")
        return self

    def footnote_ref(self, text: str, note: str) -> "DocxConverter":
        """
        脚注引用（学术论文引文）。
        在行内插入上标数字，脚注内容收集到文档末尾（Pandoc 原生支持）。
        示例：c.footnote_ref("该理论由Turing提出", "Alan Turing, 1950, Computing Machinery and Intelligence.")
        """
        self._end_list()
        # Pandoc inline footnote: text^[note content]
        self._blocks.append(f"\n{text}^[{note}]\n")
        return self

    def toc_entry(self, text: str, page: str,
                  level: int = 1) -> "DocxConverter":
        """
        目录条目（带点线前导符，右对齐页码）。
        level=1 加粗，level=2 普通，level=3 缩进。
        Markdown 中用制表符+空格近似，实际点线由 Word 模板处理。
        """
        self._end_list()
        indent = "\u3000" * (level - 1)
        bold_s = "**" if level == 1 else ""
        bold_e = "**" if level == 1 else ""
        self._blocks.append(f"{indent}{bold_s}{text}{bold_e}{'·'*4}{page}")
        return self

    def highlight(self, text: str) -> "DocxConverter":
        """
        点缀色高亮文字（60-30-10法则中的10%点缀色）。
        在 Markdown 中用行内 HTML span 实现（Pandoc 支持）。
        """
        self._end_list()
        self._blocks.append(f"\n[{text}]{{.highlight}}\n")
        return self

    def code_block(self, code: str, lang: str = "") -> "DocxConverter":
        """
        代码块。Pandoc fenced code block 完整保留缩进和空白。
        lang: 语言标注，如 "python"、"bash"、"sql"
        """
        self._end_list()
        self._blocks.append(f"\n```{lang}\n{code}\n```\n")
        return self

    def table(self, headers: list, rows: list,
              caption: str = None, bold_rows: list = None) -> "DocxConverter":
        """
        规范化表格（Pandoc pipe table）。
        caption:   表题（自动加"表N"编号，置于表格上方）
        bold_rows: 需要加粗的行序号列表（如 [0] 表示第一行数据加粗，
                   用于金融报告中关键数据加粗）
        指南规范：外框1.5pt/内框0.5pt，表头浅蓝/浅灰底色，数字右对齐
        """
        self._end_list()
        if caption:
            self.table_caption(caption)

        n = len(headers)
        # 表头行
        hdr = "| " + " | ".join(f"**{h}**" for h in headers) + " |"
        # 对齐行：检测是否为数字列（右对齐）
        aligns = []
        for col_i in range(n):
            col_vals = [str(r[col_i]) if col_i < len(r) else "" for r in rows]
            num_count = sum(1 for v in col_vals
                            if re.match(r'^[\d\+\-¥$￥€£%,，.\s]+$', v.strip()))
            aligns.append("--:" if num_count > len(col_vals)/2 and col_i > 0 else ":--")
        sep = "| " + " | ".join(aligns) + " |"

        lines = [hdr, sep]
        bold_set = set(bold_rows or [])
        for ri, row in enumerate(rows):
            cells = []
            for ci, cell in enumerate(row):
                val = str(cell)
                if ri in bold_set:
                    val = f"**{val}**"
                cells.append(val)
            lines.append("| " + " | ".join(cells) + " |")

        self._blocks.append("\n" + "\n".join(lines) + "\n")
        return self

    def quote(self, text: str) -> "DocxConverter":
        """引用/法条（Markdown blockquote，楷体悬挂缩进）"""
        self._end_list()
        self._blocks.append(f"\n> {text}\n")
        return self

    def divider(self) -> "DocxConverter":
        """水平分隔线"""
        self._end_list()
        self._blocks.append("\n---\n")
        return self

    def page_break(self) -> "DocxConverter":
        """分页符"""
        self._end_list()
        self._blocks.append('\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n')
        return self

    def spacer(self, n: int = 1) -> "DocxConverter":
        """空行"""
        for _ in range(n):
            self._blocks.append("")
        return self

    def raw_markdown(self, md: str) -> "DocxConverter":
        """直接插入原始 Markdown（高级用法）"""
        self._end_list()
        self._blocks.append(md)
        return self

    def reset_numbering(self) -> "DocxConverter":
        """重置所有计数器（多文档或多章节独立编号时使用）"""
        self._ctr.reset()
        return self

    # ── 生成 & 输出 ──────────────────────────────────────────

    def to_markdown(self) -> str:
        """返回最终 Markdown 内容（调试用）"""
        self._end_list()
        return "\n".join(self._blocks)

    def save(self, output_path: str) -> str:
        """
        生成 Markdown → Pandoc → .docx
        由 Pandoc 保证：编号正确、代码缩进保留、样式稳定。
        """
        self._end_list()
        md = "\n".join(self._blocks)
        tmp_md = str(output_path).replace(".docx", "_tmp.md")

        with open(tmp_md, "w", encoding="utf-8") as f:
            f.write(md)

        cmd = [
            "pandoc", tmp_md,
            "--from", "markdown+pipe_tables+fenced_code_blocks+inline_notes+raw_attribute",
            "--to", "docx",
            f"--reference-doc={self.template}",
            "--output", output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc 转换失败:\n{result.stderr}")

        try:
            os.unlink(tmp_md)
        except:
            pass

        size = os.path.getsize(output_path)
        tpl_name = self.template.stem
        print(f"✅ 已生成: {output_path}  ({size:,} bytes)  [模板: {tpl_name}]")
        return output_path
