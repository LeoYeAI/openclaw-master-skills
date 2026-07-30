---
name: docx-output
version: 4.1.0
description: >
  将大模型生成或修改的内容，按照对应中文文档排版国家标准与行业规范，
  输出为格式严格正确的 Word (.docx) 文档。
  支持 19 种文档类型，依据《Word文档类型与风格指南》全量实现所有排版规范，
  包括党政公文、商业文档、学术论文、技术文档、医疗文档、营销策划、
  法律文书、金融报告、工程文档等。
  v4.1 架构：Markdown 语义层 + Pandoc 渲染引擎 + 14 个专属模板，
  从根本上解决编号累加、标题污染、代码缩进、首页页码等顽固问题。
  跨平台兼容 Windows / macOS / Linux，自动适配系统字体。
  触发条件：用户要求"导出 Word"、"生成 docx"、"输出文档"、"按规范排版"等。
author: OpenClaw User
license: MIT
tags: [docx, word, pandoc, markdown, chinese-standard, cross-platform]
platform: [windows, macos, linux]
tools_required: [bash, write_file]
dependencies:
  system: [python3, pandoc]
  python: [python-docx>=1.0]
---

# DOCX 规范输出 Skill v4.1

## 架构说明

```
AI → Markdown（语义层）
   → Pandoc（渲染引擎）+ reference.docx 模板（14个，存储排版规范）
   → .docx 输出

三大保障：
  编号正确 — Pandoc 对每个独立列表块天然从1计数，无需 hack
  样式稳定 — 字体/字号/行距在模板中预定义，Word 原生渲染
  缩进保留 — Pandoc fenced code block 完整保留所有空白
```

---

## 文件结构

```
docx-output/
├── SKILL.md              ← 本文件
├── converter.py          ← 核心转换器
├── build_templates.py    ← 模板构建脚本（首次或修改规范时运行）
└── templates/            ← 14 个 reference.docx 模板
    ├── template_GOV_DOC.docx
    ├── template_GOV_JUDICIAL.docx
    ├── template_BUSINESS_CONTRACT.docx
    ├── template_BUSINESS_TENDER.docx
    ├── template_BUSINESS_PLAN.docx
    ├── template_ACADEMIC_PAPER.docx
    ├── template_ACADEMIC_LESSON.docx
    ├── template_TECH_MANUAL.docx
    ├── template_MEDICAL_DOC.docx
    ├── template_MARKETING_DOC.docx
    ├── template_LEGAL_DOC.docx
    ├── template_FINANCE_REPORT.docx
    ├── template_ENGINEERING_DOC.docx
    └── template_GENERAL_DOC.docx
```

---

## 第一步：环境检查与初始化

```bash
pandoc --version   # 需要 Pandoc >= 2.0
# 安装：macOS: brew install pandoc | Ubuntu: sudo apt install pandoc
#        Windows: choco install pandoc 或 https://pandoc.org

python3 -c "import docx" || pip install python-docx --break-system-packages

# 首次部署，构建所有模板
python3 /path/to/skill/build_templates.py
```

---

## 第二步：文档类型选择（19种）

| doc_type | 场景 | 模板 | 序号风格 |
|---|---|---|---|
| `GOV_DOC` | 党政机关公文（通知/报告/决定） | GOV_DOC | 一、（一）1.（1）四级 |
| `GOV_JUDICIAL` | 司法文书 | GOV_JUDICIAL | 一、（一）1. |
| `GOV_DIPLOMATIC` | 外交照会 | GOV_JUDICIAL | 一、（一）1. |
| `BUSINESS_CONTRACT` | 合同/协议 | BUSINESS_CONTRACT | 一、（一）1. |
| `BUSINESS_TENDER` | 标书/投标文件 | BUSINESS_TENDER | 一、（一）1. |
| `BUSINESS_PLAN` | 商业计划书/创业计划书 | BUSINESS_PLAN | 一、（一）1. |
| `ACADEMIC_PAPER` | 学术论文/研究报告 | ACADEMIC_PAPER | 一、（一）1. |
| `ACADEMIC_LESSON` | 教案/教学大纲 | ACADEMIC_LESSON | 一、（一）1. |
| `TECH_SRS` | 软件需求规格说明书 | TECH_MANUAL | 1. 1.1 1.1.1 |
| `TECH_MANUAL` | 用户手册/操作指南 | TECH_MANUAL | 1. 1.1 1.1.1 |
| `MEDICAL_RECORD` | 病历/医疗记录 | MEDICAL_DOC | 一、（一）1. |
| `MEDICAL_DRUG` | 药品说明书 | MEDICAL_DOC | 【模块名称】 |
| `MARKETING_PLAN` | 营销策划案 | MARKETING_DOC | 一、（一）1. |
| `MARKETING_ANALYSIS` | 市场分析报告 | MARKETING_DOC | 一、（一）1. |
| `LEGAL_OPINION` | 法律意见书 | LEGAL_DOC | 一、（一）1.（1）四级 |
| `LEGAL_LITIGATION` | 律师文书/诉状 | LEGAL_DOC | 一、（一）1.（1）四级 |
| `FINANCE_REPORT` | 金融/财务报告 | FINANCE_REPORT | 一、（一）1. |
| `ENGINEERING_DOC` | 工程文档/项目方案 | ENGINEERING_DOC | 1. 1.1 1. |
| `GENERAL_DOC` | 通用商务文档（兜底） | GENERAL_DOC | 一、（一）1. |

---

## 第三步：各类型排版规范速查

### GOV_DOC — 党政机关公文（GB/T 9704-2012）
```
页边距：上3.7 下3.5 左2.8 右2.6（cm）
标题：二号宋体（模拟小标宋），居中，不加粗
正文：三号仿宋，固定行距28磅（每页22行/每行28字）
序号：一、（一）1.（1）四级，第四级用 h4()
英文：Times New Roman
页码：首页不显示（模板已设置）
```

### BUSINESS_TENDER — 标书/投标文件
```
页边距：上2.6 下2.2 左右2.5（cm）
封面/目录：三号加粗微软雅黑（本类型专属字体）
正文：小四号宋体，1.5倍行距
英文：Calibri
```

### ACADEMIC_PAPER — 学术论文
```
页边距：上下2.5 左3.1 右3.2（cm）
标题：三号仿宋，前空三行后空两行，居中
摘要：小四号仿宋，1.25倍，左右缩进2字符 → abstract()
关键词：小四号仿宋，另起一行             → abstract(keywords=...)
一级标题：四号黑体，前后空一行
二级标题：小四号楷体
正文：五号宋体，1.25倍，首行缩进2字符
引文脚注：小五号，悬挂缩进1字符         → footnote_ref()
图题：五号仿宋，置图下方，自动编号       → figure_caption()
表题：五号仿宋，置表上方，自动编号       → table(caption=...)
英文：Times New Roman
```

### TECH_MANUAL — 用户手册/操作指南
```
页边距：上下2.5 左右2.5（cm）
封面：四号黑体，居中
一级标题：小四号黑体，1. 格式，左对齐
二级标题：小四号宋体加粗，1.1 格式
步骤说明：项目符号列表   → bullet()
警告提示：红色加粗 ⚠    → warning()
代码块：Courier New，灰底，保留缩进 → code_block(lang="python")
正文：五号宋体，不缩进
英文：Calibri
```

### MEDICAL_DRUG — 药品说明书
```
模块标题：【药品名称】【作用与用途】等 → module_heading()
警示语：黑体加粗红色突出              → warning()
正文：小四号宋体，1.5倍行距
英文：Times New Roman
```

### LEGAL_DOC — 法律文书
```
页边距：上下2.54 左右3.17（cm）
序号：一、（一）1.（1）严格四级
引用法条：楷体，加「」引号  → quote()
落款：仿宋四号居中           → signature_block()
英文：Times New Roman
```

### FINANCE_REPORT — 金融/财务报告
```
正文：四号宋体，固定行距28磅
数据表格：关键数据加粗 → table(bold_rows=[0,1,...])
配色：主色深蓝#2F5496，辅色浅灰，点缀橙色
英文：Times New Roman
```

---

## 第四步：生成脚本模板

```python
"""generate_doc.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from converter import DocxConverter

c = DocxConverter("TECH_MANUAL")   # ← 替换为实际类型

# 标题
c.title("文档主标题")
c.subtitle("副标题（可选）")

# 标题层级（auto_number=True 智能防双重编号）
c.h1("章节一")           # → "1. 章节一" 或 "一、章节一"（按类型）
c.h2("子章节")           # → "1.1 子章节" 或 "（一）　子章节"
c.h3("三级标题")         # → "1.1.1" 或 "1."
c.h4("四级标题")         # → "（1）　四级标题"（公文/法律类型）

# 已含序号不重复编号
c.h1("一、已有序号章节") # 检测到已有序号，直接输出不加前缀

# 正文（支持 Markdown 内联）
c.body("正文段落，支持 **加粗** *斜体* `代码`。")

# 编号列表（换章节自动重置）
c.numbered("第一项")     # → 1
c.numbered("第二项")     # → 2
c.h1("新章节")
c.numbered("又一项")     # → 1（自动重置！）
c.bullet("项目符号一")
c.bullet("  - 子项", level=1)

# === 专属 API ===

# 学术摘要
c.abstract("摘要内容...", keywords="关键词1；关键词2")

# 脚注引用
c.footnote_ref("正文内容", "脚注：作者.书名.出版社,年份.")

# 药品说明书模块标题
c.module_heading("药品名称")

# 警告提示
c.warning("此操作不可逆，请谨慎执行！")

# 图题（自动编号，置图下方）
c.figure_caption("系统架构示意图")

# 表格（表题置上，自动编号；数值列自动右对齐）
c.table(
    headers=["指标", "方法A", "数值"],
    rows=[["准确率","92.3%","0.923"],["召回率","88.7%","0.887"]],
    caption="性能对比",
    bold_rows=[0]          # 第一行加粗（金融报告关键数据）
)

# 引用/法条
c.quote("《民法典》第X条：相关法律条文内容。")

# 落款
c.signature_block("甲方：___________", "日期：___年___月___日")

# 代码块（缩进完整保留）
c.code_block("""import torch
class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 1)""", lang="python")

# 目录条目
c.toc_entry("一、章节一", "1")
c.toc_entry("1.1 子章节", "2", level=2)

# 其他
c.highlight("重点内容")  # 点缀色高亮
c.divider()              # 分隔线
c.page_break()           # 分页符
c.spacer(2)              # 空行

c.save("/mnt/user-data/outputs/输出文件名.docx")
```

---

## API 速查表

| 方法 | 说明 | 关键参数 |
|------|------|---------|
| `DocxConverter(doc_type)` | 创建转换器 | 19种类型之一 |
| `title(text)` | 主标题 | — |
| `subtitle(text)` | 副标题 | — |
| `h1/h2/h3(text, auto_number)` | 一二三级标题 | `auto_number=True` 防双重编号 |
| `h4(text, auto_number)` | **四级标题**（公文/法律规范）| 同上 |
| `body(text)` | 正文段落 | 支持 Markdown 语法 |
| `bullet(text, level)` | 项目符号列表 | `level=0/1/2` |
| `numbered(text, level)` | **编号列表，换章节自动从1重置** | `level=0/1/2` |
| `abstract(text, keywords)` | **学术摘要**（仿宋左右缩进2字符）| `keywords` 可选 |
| `footnote_ref(text, note)` | **脚注引用**（学术引文） | `note` 脚注内容 |
| `module_heading(name)` | **【模块名称】**（药品说明书） | — |
| `warning(text)` | **⚠ 警告/提示**（红色加粗） | — |
| `signature_block(*lines)` | **落款/签名区**（居中） | 多参数多行 |
| `figure_caption(text, auto_number)` | **图题**（自动"图N"，置图下方） | — |
| `table(headers, rows, caption, bold_rows)` | 规范表格 | `bold_rows` 加粗行 |
| `quote(text)` | 引用/法条（blockquote） | — |
| `code_block(code, lang)` | 代码块（缩进完整保留） | `lang="python"` |
| `toc_entry(text, page, level)` | 目录条目（带点线）| `level=1/2/3` |
| `highlight(text)` | 点缀色高亮 | — |
| `divider()` | 分隔线 | — |
| `page_break()` | 分页符 | — |
| `spacer(n)` | 空行 | `n=1` |
| `raw_markdown(md)` | 原始 Markdown | 高级用法 |
| `to_markdown()` | 返回 Markdown（调试） | — |
| `reset_numbering()` | 重置所有计数器 | — |
| `save(path)` | **生成 docx**（调用 Pandoc） | 完整路径 |

---

## 通用排版规范（原指南第八章）

### 字体规范
| 类别 | 中文 | 英文 |
|-----|------|------|
| 正式文档（公文/法律/学术） | 宋体/仿宋/黑体/楷体 | Times New Roman |
| 技术文档（SRS/手册/工程） | 宋体/黑体 | Calibri |
| 商业文档（计划书/营销） | 黑体/宋体 | Calibri |
| 特殊（标书目录） | 微软雅黑 | Calibri |

### 表格规范（原指南第八章第3节）
- 外框 1.5pt 粗线，内框 0.5pt 细线（模板中设置）
- 表头：加粗 + 主题色底色 + 白字
- 文字左对齐，数字右对齐（自动检测）
- 表题置上，图题置下（原指南明确规定）

### 配色法则（60-30-10）
| 角色 | 比例 | 颜色 |
|-----|------|------|
| 主色 | 60% | 深蓝#2F5496（商业/营销）/ 黑#000000（公文/学术） |
| 辅助色 | 30% | 浅灰#D9D9D9 |
| 点缀色 | 10% | 橙色#FFC000（商业）/ 红色#CC0000（公文/法律/警告） |

### 首页页码
- **党政公文**：首页不显示页码（`GOV_DOC` 模板已设置 `differentFirstPage=True`）
- 其他类型：页脚居中，字号见各类型规范

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `pandoc: command not found` | 安装 Pandoc |
| 模板文件不存在 | `python3 build_templates.py` |
| 中文字体异常（Linux） | `sudo apt install fonts-noto-cjk` |
| 编号未从1重置 | 确保两个列表间有 `h1/h2/body` 调用 |
| 代码缩进丢失 | 确认 Pandoc >= 2.0；使用 `code_block()` |
| 四级标题不显示 | `GOV_DOC`/`LEGAL_DOC` 类型支持 h4 |

---

---

## 扩展功能：读取已有 Word 文档并重新排版

> **说明**：此功能是独立新增模块，不影响上述所有原有功能。
> 使用前请确保 `docx_reader.py` 和 `reformat.py` 与 `converter.py` 在同一目录。

### 解决的问题

OpenClaw 无法直接读取 `.docx` 二进制文件。此模块在 Skill 内部增加**提取层**，
将二进制自动转换为结构化内容，再交给现有排版引擎处理：

```
用户的旧 .docx（二进制）
    ↓  docx_reader.py（提取层）
结构化内容块（标题/正文/列表/表格/代码块）
    ↓  reformat.py（重排版层）
DocxConverter → Pandoc + reference.docx 模板（原有排版引擎，不变）
    ↓
重新排版的新 .docx
```

### 新增文件

| 文件 | 作用 |
|------|------|
| `docx_reader.py` | 从任意 .docx 提取结构化内容（标题/正文/列表/表格/代码块）|
| `reformat.py` | 一键重排版入口：读取 → 自动推断类型 → 输出新文档 |

### 命令行用法

```bash
# 最简用法：自动推断类型，输出到同目录
python3 reformat.py 我的文档.docx

# 指定输出路径 + 强制文档类型
python3 reformat.py 旧文档.docx 新文档.docx --type GOV_DOC

# 先预览提取内容，确认正确后再生成（推荐首次使用）
python3 reformat.py 文档.docx --dry-run

# 生成文档的同时查看 Markdown 中间产物
python3 reformat.py 文档.docx --show-md
```

所有支持的 `--type` 值与上方文档类型表完全相同（19种）。

### OpenClaw Skill 内调用

```python
import sys
sys.path.insert(0, "/path/to/skill/")
from reformat import reformat

# 全自动：读取 → 推断类型 → 重排版 → 输出
result = reformat(
    input_path  = "用户的旧文档.docx",
    output_path = "/mnt/user-data/outputs/重排版后文档.docx",
    # doc_type  = "TECH_MANUAL",  # 可选：强制指定类型，覆盖自动推断
)
print(result["doc_type"])  # 实际使用的文档类型
print(result["stats"])     # {'headings':38, 'paragraphs':33, 'tables':6, ...}
```

### 自动提取能力

| 内容类型 | 提取方式 | 可靠性 |
|---------|---------|-------|
| 标题层级（h1～h4） | 优先用 Word 样式名，回退到字号+加粗启发式 | ⭐⭐⭐⭐⭐ |
| 正文段落 | 直接读取 | ⭐⭐⭐⭐⭐ |
| 项目符号列表 | 样式名 + XML numPr | ⭐⭐⭐⭐⭐ |
| 编号列表 | 样式名 + XML numPr | ⭐⭐⭐⭐ |
| 表格 | python-docx Table API | ⭐⭐⭐⭐⭐ |
| 代码块 | Courier New 字体检测 + 代码样式名 | ⭐⭐⭐⭐ |
| 文档类型自动推断 | 19种类型关键词评分 | ⭐⭐⭐⭐ |
| 警告/摘要/落款识别 | 文本正则模式匹配 | ⭐⭐⭐ |

### 局限性说明

| 局限 | 处理建议 |
|------|---------|
| 图片无法提取（二进制数据） | 排版后手动在 Word 中插入图片 |
| 文档全用 Normal 样式（无 Heading）| 先 `--dry-run` 检查，再 `--type` 强制指定类型 |
| 复杂嵌套/合并单元格表格 | 提取为扁平结构，复杂格式需手动调整 |
| 脚注/尾注内容 | 自动跳过，排版后可用 `footnote_ref()` 手动添加 |
