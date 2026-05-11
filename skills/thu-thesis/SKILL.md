---
name: thu-thesis
description: 清华大学毕业论文 Word → PDF 一键格式规范化工具。输入任意 Word (.docx) 格式的清华毕业论文，自动转换为符合清华 thuthesis 官方 LaTeX 模板规范的高质量 PDF。适用于所有清华学位论文（MBA/学硕/专硕），一条命令搞定。功能：自动提取章节结构、中英文摘要、参考文献（自动生成 BibTeX）、图片（含 caption）、表格（含表头和标题）、致谢、个人简历；自动生成符号和缩略语说明（含孤儿缩略语检测与正文首次出现处自动补写）；自动生成插图清单和附表清单；输出完整 thuthesis LaTeX 项目并编译为 PDF。运行时依赖：python-docx、jinja2、xelatex/bibtex（TeX Live）；setup.sh 会从 GitHub 克隆 thuthesis 到 /tmp/thuthesis-latest。Use when: 用户需要把 Word 格式的清华毕业论文转为规范 PDF，或需要对毕业论文做格式规范化处理。
---

# 清华 MBA 论文 Word → PDF 一键转换

## ⚠️ 核心操作原则（不得违反）

> **只从 Word 中提取信息，不修改 thuthesis 模板格式。**
>
> - thuthesis 的封面、页眉、目录、参考文献、图表样式等，全部由 `thuthesis.cls` 自动生成
> - 脚本只负责把 Word 里的内容（标题、摘要、章节、图表、参考文献等）提取出来填入 `.tex` 文件
> - 若 Word 中某字段缺失，对应 LaTeX 字段留空，**不删除**、不跳过、不用占位符替代
> - 任何格式上的"改进"都必须以 `assets/databk/` 中的官方示例为准，不得自行发挥

## 架构：新三层 AI-native 流程

```
Word 文件
  ↓ [extract_raw.py]  纯机械提取，无 LLM
raw_xxx.json + 文档骨架（段落 idx + 样式 + 文字）
  ↓ [我（AI）阅读骨架]  理解章节结构
struct_xxx.json（章节划分、段落 idx 映射）
  ↓ [build_parsed.py]  纯 Python 组装，无 LLM
parsed_xxx.json
  ↓ [render.py]        填充 thuthesis LaTeX 模板
LaTeX 项目目录
  ↓ [xelatex + bibtex] 编译
thesis.pdf ✅
  ↓ [我（AI）Rubric 评测]  阅读产物，逐项打分 + 自动修复
evaluation_report.md
```

**关键设计原则：Python 脚本不调用任何 LLM，不持有 API key。AI 在两个关键环节介入：(1) 阅读骨架生成 struct.json；(2) Rubric 评测 + 自动修复。**

## 依赖

```bash
pip3 install python-docx jinja2 matplotlib
# 需要已安装 TeX Live
```

## 格式参考：assets/databk/

`assets/databk/` 是从官方 thuthesis 项目备份的原始示例 data 文件，是本工具一切格式决策的**黄金标准**：

| 文件 | 参考内容 |
|------|----------|
| `chap01.tex` ~ `chap04.tex` | 正文章节、三线表、图片、公式格式 |
| `abstract.tex` | 中英文摘要格式 |
| `denotation.tex` | 缩略语/符号说明格式 |
| `acknowledgements.tex` | 致谢格式 |
| `resume.tex` | 个人简历格式 |

**遇到任何格式问题，先查 `databk/` 里的对应文件，再动代码。**

## 初次使用 / 更新格式参考

```bash
# SKILL_DIR = 本 skill 的根目录（thu-thesis/）
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"   # 在 scripts/ 内执行时
# 或直接写绝对路径，例如：
# SKILL_DIR="/path/to/skills/thu-thesis"
bash "$SKILL_DIR/scripts/setup.sh" "$SKILL_DIR"
```

`setup.sh` 做三件事：
1. 从 GitHub clone（首次）或 `git pull`（已有）最新 [thuthesis](https://github.com/tuna/thuthesis) 到 `/tmp/thuthesis-latest`
2. 编译生成 `thuthesis.cls`（如尚未生成）
3. **`rm -rf assets/databk/ && cp -r data/ assets/databk/`** → 保持格式参考始终为最新版本

**每次 thuthesis 版本有重大更新时，重跑 `setup.sh` 即可刷新 databk。**

## 输出路径规范

**LaTeX 工程输出位置：与输入 `.docx` 同目录，子文件夹命名为 `<原文件名去扩展>-latex`。**

例如：输入 `/path/to/foo.docx`，则 LaTeX 工程输出到 `/path/to/foo-latex/`。

- 中间临时文件（raw/struct/parsed JSON）放在 workspace 临时目录，转换完成后可清理
- 最终交付给用户的是 `-latex/` 目录（含 `thesis.pdf`）

## 完整转换流程

### Step 1：机械提取（同时创建 LaTeX 工程目录）

```bash
# SKILL_DIR = 本 skill 根目录，按实际安装路径设置
SKILL_DIR="/path/to/skills/thu-thesis"

python3 "$SKILL_DIR/scripts/convert.py" extract /path/to/论文.docx output/
```

**extract 会立即做两件事：**
1. 在 `.docx` **同目录**创建 `<stem>-latex/` 工程目录（项目开始即确定输出位置）
2. 机械提取，输出 `output/raw_xxx.json` + 终端骨架

终端输出示例：
```
📄 输入: /path/to/foo.docx
📁 中间文件: output/
📁 LaTeX 工程: /path/to/foo-latex/      ← 已创建
📊 图片: 5 张  | para_idx: [102, 115, ...]
📊 表格: 3 张  | before_para: [88, 134, ...]
```

### Step 2：AI 阅读骨架，生成 struct.json

AI（我）读取骨架，识别：
- 摘要范围（`abstract_cn_range`, `abstract_en_range`）
- 各章节标题段落 idx（`title_para`）、正文范围（`content_range`）
- 各级小节（sections）的 idx 和编号
- 参考文献、致谢、简历的范围

**如何输出**：使用 Write 工具，把 struct.json 写到与 `raw_xxx.json` **同一目录**，命名为 `struct_<论文标题>.json`（与 raw 文件保持同级）：

```
output/
  raw_论文标题.json      ← Step 1 生成
  struct_论文标题.json   ← AI 用 Write 工具写到这里  ✅
  figures/               ← Step 1 提取的图片
```

**写入前必须检查**（防图表丢失）：
1. 列出 `raw_xxx.json` 中所有图片的 `para_idx` → 确保每个都落在某章 `content_range` 内
2. 列出所有表格的 `before_para` → 确保都 ≥ 第一章 `content_range[0]` 且在某章范围内
3. 相邻章节 `content_range` **不能有间隙**

输出 `struct_xxx.json`，格式：

```json
{
  "cover": {
    "abstract_cn_range": [27, 31],
    "abstract_en_range": [35, 44],
    "keywords_cn_para": 31,
    "keywords_en_para": 44
  },
  "chapters": [
    {
      "number": "第1章",
      "title": "引言",
      "title_para": 109,
      "content_range": [110, 142],
      "sections": [
        {"level": 2, "number": "1.1", "title": "选题背景", "title_para": 110},
        {"level": 3, "number": "1.1.1", "title": "子节标题", "title_para": 115}
      ]
    }
  ],
  "references_range": [388, 409],
  "acknowledgements_range": [412, 412],
  "resume_range": [423, 428]
}
```

### Step 3-5：组装、渲染、编译

Step 1 已经创建好 LaTeX 工程目录，直接指向它：

```bash
SKILL_DIR="/path/to/skills/thu-thesis"
DOCX="/path/to/foo.docx"

python3 "$SKILL_DIR/scripts/convert.py" build \
  output/raw_foo.json \
  output/struct_foo.json \
  "$(dirname "$DOCX")/foo-latex"
```

自动完成：
- `build_parsed.py`：raw + struct → parsed JSON（含表格、图片正确插入）
- `render.py`：parsed JSON → LaTeX 项目
- `xelatex + bibtex`：编译 PDF（3~4 次，保证目录稳定）

### Step 6：AI Rubric 评测 + 自动修复

编译完成后，我（AI）逐项检查转换质量，详见下方「Rubric 评测细则」。可自动修复的问题直接修复并重新编译，最多 **3 轮**；不可修复的问题在报告中标注。最终输出 `evaluation_report.md` 到 LaTeX 工程目录。

## 文件说明

| 路径 | 说明 |
|------|------|
| `scripts/convert.py` | 入口，`extract` / `build` 两个子命令 |
| `scripts/extract_raw.py` | Word → raw JSON（纯机械提取，段落/表格/图表） |
| `scripts/build_parsed.py` | raw + struct → parsed JSON（纯 Python，无 LLM） |
| `scripts/render.py` | parsed JSON → LaTeX 项目（填充模板，生成 BibTeX） |
| `assets/templates/*.j2` | Jinja2 模板 |
| `assets/databk/` | **thuthesis 官方格式示例，格式决策唯一参考** |

## Rubric 评测细则（AI 执行）

> **评测由 AI 直接完成，不使用 Python 脚本。** AI 阅读生成产物（parsed JSON、.tex 文件、refs.bib、thesis.log、thesis.pdf），按下方 Rubric 逐项打分，可修复问题直接修改后重新编译（最多 3 轮），最终输出 `evaluation_report.md`。

### 评测流程

1. **读取产物**：`parsed_xxx.json`、`data/*.tex`、`ref/refs.bib`、`thesis.log`、`thesis.pdf`（检查是否存在及大小）
2. **逐项评分**：按下方 38 项 Rubric 逐一检查，给出 PASS / WARN / FAIL + 原因
3. **自动修复**：对可修复的 FAIL/WARN 项直接修改 `.tex` 文件，然后重新 `xelatex + bibtex` 编译（最多 3 轮）
4. **输出报告**：生成 `evaluation_report.md`，含总分、维度得分、所有扣分项明细

### 评分制度

| 类型 | 满分 | PASS | WARN | FAIL |
|------|------|------|------|------|
| 必要项 | 3 | 3 | 1.5 | 0 |
| 重要项 | 2 | 2 | 1 | 0 |
| 亮点项 | 1 | 1 | 0.5 | 0 |
| 失误扣分项 | 0 | — | — | 每处扣1分，最多扣10 |

**评级标准**：总分/满分 → 优秀≥90% / 良好≥75% / 合格≥60% / 不合格<60%

### 可自动修复 vs 不可修复

| 可自动修复（直接改文件重编译） | 不可自动修复（报告中标注） |
|---|---|
| `.bbl` 出现 `佚名` → 读 refs.bib 找对应条目，手工补全 author 字段，然后重跑 bibtex+xelatex | 表格/图片无 caption（Word 原文没有，不可凭空生成） |
| author 字段被截断（如 `美国旅游协会（U.S`）→ 直接修 refs.bib 中该条目的 author 字段 | 文献只有 `\nocite`（正文本来就没有引用，是原文问题） |
| author-year 引用未转 `\cite` → 在 .tex 中手工补 `\cite{key}` | author-year 匹配失败（姓名简称无法映射，原文限制） |
| LaTeX 编译报错（`\&` 转义等）→ 修 .tex 中的特殊字符 | committee/comments/resolution 占位（答辩后才有内容） |
| `\listoffigures` / `\listoftables` 缺失 → 补入 `thesis.tex` | — |

### Rubric 明细（38项，满分 90 分）

#### A. 元信息（11项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| A1 | 中文标题 | 必要 | 检查 `thusetup.tex` 中 `title` 字段。PASS：非空且≥5字。FAIL：缺失 |
| A2 | 英文标题 | 必要 | 检查 `title*` 字段。PASS：非空且≥10字符。FAIL：缺失 |
| A3 | 作者姓名 | 必要 | 检查 `author` 字段。PASS：非空。FAIL：缺失 |
| A4 | 英文作者名 | 重要 | 检查 `author*` 字段。PASS：非空。WARN：缺失（可人工补充） |
| A5 | 导师信息 | 必要 | 检查 `supervisor` 字段。PASS：非空且含职称（教授/研究员/副教授/讲师）。WARN：有名无职称。FAIL：缺失 |
| A6 | 培养单位 | 重要 | 检查 `department` 字段。PASS：非空。WARN：缺失 |
| A7 | 日期格式 | 重要 | 检查 `date` 字段。PASS：格式为 `YYYY-MM`。WARN：缺失或格式异常 |
| A8 | 中文摘要 | 必要 | 检查 `abstract.tex` 中文摘要内容。PASS：≥50字。WARN：<50字。FAIL：缺失 |
| A9 | 英文摘要 | 必要 | 检查英文摘要内容。PASS：≥100字符。WARN：<100字符。FAIL：缺失 |
| A10 | 中文关键词 | 必要 | 检查 `thusetup.tex` 中 `keywords` 字段。PASS：≥2个。WARN：仅1个。FAIL：缺失 |
| A11 | 英文关键词 | 重要 | 检查 `keywords*` 字段。PASS：≥2个。WARN：仅1个。FAIL：缺失 |

#### B. 正文（5项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| B1 | 章节结构 | 必要 | 检查 parsed JSON 中 chapters。PASS：≥3章且每章≥2个内容块。WARN：有章内容极少（<2块）。FAIL：<3章 |
| B2 | 章节 .tex 文件 | 必要 | 检查 `data/chap*.tex` 文件。PASS：所有文件存在且≥200字符。WARN：文件过短。FAIL：文件缺失 |
| B3 | 正文文字总量 | 必要 | 统计所有章节文本字数。PASS：≥8000字。WARN：3000-8000字。FAIL：<3000字（可能解析失败） |
| B4 | 节级标题 | 重要 | 检查 .tex 中是否有 `\section`/`\subsection`。PASS：存在多个节级标题。WARN：未检测到 |
| B5 | 目录一致性 | 重要 | 编译后检查 `thesis.toc`：章标题与 .tex 文件一致，无残留编号（如标题中出现 `1.1` 前缀）。PASS：一致。WARN：有不一致 |

#### C. 参考文献（7项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| C1 | 参考文献列表 | 必要 | 检查 parsed JSON 中 references。PASS：≥10条。WARN：<10条。FAIL：为空 |
| C2 | refs.bib 生成 | 必要 | 检查 `ref/refs.bib` 文件。PASS：存在且有 `@article`/`@book`/`@misc` 等 BibTeX 条目。FAIL：不存在或为空 |
| C3 | BibTeX 字段质量 | 必要 | **必须同时检查 `refs.bib` 和 `thesis.bbl` 两个文件，逐条核查：**<br>①读取 `refs.bib`，统计 `author` 字段为空 `{}` 的条目数；<br>②读取 `thesis.bbl`，搜索 `佚名` 字样（bibtex 给无 author 条目的默认值），每出现一次表示有一条参考文献无法正确显示；<br>③检查 `refs.bib` 中 author 值是否存在截断（如以 `（` 结尾、或机构名中间被切断如 `美国旅游协会（U.S`）；<br>④检查 title 字段是否异常短（<5字符）或与实际文献标题明显不符。<br>PASS：所有条目 author/title 非空，`.bbl` 无 `佚名`，无截断。WARN：有1-2个问题条目（列出）。FAIL：≥3个问题条目，**或 `.bbl` 中出现 `佚名`** |
| C4 | PDF 文献完整 | 必要 | 比较 BibTeX 条目数与 Word 原文参考文献条数。**同时读取 `thesis.bbl`，检查每条 `\bibitem` 的内容是否合理**（作者/年份/标题是否看起来正确，而不仅是数量匹配）。PASS：条目数一致，`.bbl` 内容合理。WARN：条目数一致但有个别条目内容异常。FAIL：BibTeX 条目少于原文 |
| C5 | 引用覆盖率 | 重要 | **严格区分 `\cite{}` 和 `\nocite{}`**：<br>①统计章节 .tex 文件（`data/chap*.tex`）中 `\cite{key}` 的唯一 key 集合（正文有引用）；<br>②统计 `thesis.tex` 中 `\nocite{key}`（只进入参考文献列表，正文无引用）；<br>③对每个 bib key 归类：有 `\cite` / 只有 `\nocite` / 都没有。<br>PASS：所有 key 都有正文 `\cite`。WARN：有 key 只在 `\nocite`（列出这些 key，说明正文缺少引用）。FAIL：有 key 既无 `\cite` 也无 `\nocite` |
| C6 | cite 关联性 | 扣分 | 随机抽取 5-10 处 `\cite{key}`，阅读上下文与对应文献，判断是否内容相关。不相关每处扣1分，最多扣10分。抽检样本须列入报告供人工复核 |
| C7 | author-year 引用 | 亮点 | 检查正文中 `曹玉（2025）`、`Smith (2020)` 等行文引用是否已转为 `\cite{key}`。PASS：无遗漏。WARN：有少量遗漏（列出原文片段）。FAIL：大量未转换 |

#### D. 图片（4项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| D1 | 图片提取数量 | 重要 | 比较 `figures/` 目录文件数与 parsed JSON 图片数。PASS：一致。WARN：不一致 |
| D2 | 图片 caption | 重要 | 检查 .tex 中图片是否有 `\caption{}`。PASS：全部有。WARN：部分无 caption |
| D3 | LaTeX 渲染 | 必要 | 检查 .tex 中有对应的 `\includegraphics`。PASS：图片均被引用。FAIL：有图片但未渲染 |
| D4 | 插图清单 | 重要 | 检查 `thesis.tex` 是否含 `\listoffigures`。PASS：存在且所有图有 caption → 清单完整。WARN：存在但部分图无 caption。FAIL：缺少 `\listoffigures`（应自动修复） |

#### E. 表格（4项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| E1 | 表格提取数量 | 重要 | 检查 parsed JSON 中表格数量是否合理。PASS：数量合理 |
| E2 | 三线表格式 | 必要 | 检查 .tex 中表格是否使用 `tabularx` + `booktabs`（`\toprule`/`\midrule`/`\bottomrule`），无竖线。PASS：格式合规。FAIL：不合规 |
| E3 | 表格 caption | 重要 | 检查表格是否有 `\caption{}`。PASS：全部有。WARN：部分无 caption |
| E4 | 附表清单 | 重要 | 检查 `thesis.tex` 是否含 `\listoftables`。PASS：存在且所有表有 caption → 清单完整。WARN：存在但部分表无 caption。FAIL：缺少 `\listoftables`（应自动修复） |

#### F. 缩略语（2项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| F1 | 缩略语表 | 重要 | 检查 `data/denotation.tex`。PASS：存在且有 `\item[...]` 条目。WARN：无条目。FAIL：文件不存在 |
| F2 | 孤儿缩略语 | 亮点 | 检查缩略语表中是否有正文未出现的"孤儿"。PASS：无孤儿。WARN：有孤儿但已标注 |

#### G. 附件（2项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| G1 | 致谢 | 重要 | 检查 `data/acknowledgements.tex`。PASS：有实质内容（>50字）。WARN：缺失或过短 |
| G2 | 个人简历 | 重要 | 检查 `data/resume.tex`。PASS：有实质内容（>50字）。WARN：缺失或过短 |

#### H. 编译（3项）

| ID | 检查项 | 类型 | 评判标准 |
|----|--------|------|----------|
| H1 | PDF 已生成 | 必要 | 检查 `thesis.pdf` 是否存在。PASS：存在且≥50KB。WARN：文件过小（<50KB）。FAIL：不存在 |
| H2 | 无 LaTeX Error | 必要 | 检查 `thesis.log`。PASS：无 `LaTeX Error`。WARN：有 `Overfull \hbox` 警告。FAIL：有 Error |
| H3 | thusetup 格式 | 重要 | 检查 `thusetup.tex` 是否含 MBA 专业硕士配置（degree=master, degree-type=professional）。PASS：配置正确。WARN：配置异常 |

### 报告格式

评测报告 `evaluation_report.md` 须包含：

1. **总分**：`XX / 90 分（XX%）— 评级`
2. **维度得分表**：每个维度（A~H）的得分/满分/得分率
3. **扣分明细**：所有 FAIL / WARN 项列出 ID、检查项、扣分原因（**不截断**）
4. **C6 抽检样本**：随机抽取的 cite 关联性样本（文献信息 + 上下文），供人工核查
5. **完整明细表**：38 项逐一列出 ID、类型、满分、得分、说明

## 参考文献处理

- Word 原文参考文献列表 → `ref/refs.bib`（自动解析为 BibTeX）
- 正文 `[10]` → `\cite{key}`，支持 `[1,2,3]` 和 `[1-3]`
- **Author-year 行文引用自动补 `\cite`**：
  - `曹玉（2025）分析了...` → `曹玉（2025）\cite{cao2025aigc}分析了...`
  - 支持中文全角 `（年）`、英文半角 `(年)`
  - 匹配失败时保留原文，rubric C7 会警告
- 未被引用文献：关键词匹配补 `\cite`；无匹配用 `\nocite` 兜底

## 图片和表格处理全链路

> **图表丢失是最常见的转换问题。** 根本原因几乎总是 Step 2（AI 生成 struct.json）时 `content_range` 设定不准，导致图表所在段落被排除在章节范围之外。

### 完整流程

```
Step 1  extract_raw.py
  ├── 图片：扫描段落 XML 的 a:blip（普通图）/ c:chart（图表对象）
  │         记录 {filename, para_idx}，文件存入 output/figures/
  └── 表格：扫描 body 元素顺序，记录 {rows, before_para}
            before_para = 表格紧跟在哪个段落之后的 idx

Step 2  AI 生成 struct.json
  └── ⚠️ 关键：content_range 必须覆盖图表所在的 para_idx！

Step 3  build_parsed.py
  ├── 图片分配：figures_by_para[para_idx] → 章节的 content_range 内 → 插入
  │   caption 检测：图片 para_idx 后 0-2 段内匹配 ^图\s*\d
  ├── 表格分配：before_para 落在 content_range 内 → 插入
  │   before_para < first_chap_start → 跳过（封面/目录页表格）
  │   before_para 不在任何章节范围 → 分配给最近章节末尾（extra_tables）
  │   caption 检测：before_para 后 0-2 段内匹配 ^表\s*\d
  └── figures/ 目录拷贝至 output_dir/figures/

Step 4  render.py
  ├── 图片：type=figure → \begin{figure}...\includegraphics{figures/xxx}\caption{}\end{figure}
  │   SVG 跳过并警告；\caption 自动去掉"图X-X "前缀（thuthesis 自动编号）
  ├── 表格：type=table → render_table() 生成三线表 raw_latex 块
  │   列宽：内容≤12字符宽 → l；>12字符 → X；至少一列为 X
  │   \caption 自动去掉"表X-X "前缀；\caption 在表格上方
  └── 扫描生成的 .tex：有 \begin{figure} → 加 \listoffigures；有 \begin{table} → 加 \listoftables
```

### ⚠️ 图表丢失的常见原因及修复

#### 原因 1（最常见）：struct.json 的 content_range 设定偏窄，图表 para_idx 在范围外

**排查方法**：检查 `raw_xxx.json` 中图片/表格的 `para_idx` / `before_para`，与 struct.json 的 `content_range` 对比：

```python
import json
raw = json.load(open('output/raw_xxx.json'))
print("图片 para_idx:", [(f['filename'], f['para_idx']) for f in raw['figures']])
print("表格 before_para:", [(t['idx'], t['before_para']) for t in raw['tables']])
```

**修复**：重新生成 struct.json，确保每章 `content_range[1]`（结束 idx）足够大，覆盖该章所有图表段落，然后重跑 `build` 命令。

#### 原因 2：图片/表格出现在章节之间的"间隙"段落

两章 `content_range` 之间可能有空隙（如过渡段落 idx 130-135 不在任何章节范围内）。`build_parsed.py` 会把这些表格用 `extra_tables` 附到最近章节末尾，但图片无此兜底，**直接丢失**。

**修复**：struct.json 相邻章节的 `content_range` 不能有间隙，确保：
```
第1章 content_range[1] + 1 ≥ 第2章 content_range[0]
```

#### 原因 3：图片的 `para_idx` 为 0 或 None

Word 中图片有时嵌在空段落、文本框或表格单元格中，导致 `extract_raw.py` 无法找到对应段落。此时 `para_idx=0`，图片会被分配到第 0 段落，不在任何章节 `content_range` 内，丢失。

**排查**：`raw_xxx.json` 中 `figures` 里 `para_idx=0` 且文档实际有图的，属于此类。

**修复**：在 struct.json 中找到该图片实际所在的段落（根据骨架文本目视定位），手动在对应章节的 `content_range` 里调整，或在 `parsed_xxx.json` 中手动插入 figure 块后重跑 render。

#### 原因 4：caption 未被识别（图/表无编号）

caption 检测依赖 `^图\s*\d` / `^表\s*\d` 正则：

- Word 中 caption 写法是 `图1-1 标题` → 可识别
- 写法是 `图一 标题`（中文数字）、`Figure 1` 或 caption 与图片不在相邻段落 → **识别失败，caption 为空**

caption 为空不影响图表出现在 PDF，但插图清单/附表清单会不完整（D4/E4 WARN）。

### AI 在 Step 2 生成 struct.json 的图表注意事项

> **生成 struct.json 时必须执行以下检查，否则极可能导致图表丢失：**

1. **对照 raw_xxx.json 的图片 `para_idx` 列表**，确认每张图的 `para_idx` 都落在某章的 `content_range` 内
2. **对照表格的 `before_para` 列表**，确认每个 `before_para` 都 ≥ `first_chap_start`（第一章 `content_range[0]`）且落在某章范围内
3. 相邻章节的 `content_range` **不能有间隙**，末尾章节的 `content_range[1]` 要覆盖到参考文献段之前

### 表格格式（三线表）

```latex
\begin{table}[htbp]
  \caption{表题}
  \begin{tabularx}{\linewidth}{l X}
    \toprule
    短列头 & 长文本列头 \\
    \midrule
    内容1 & 内容2 \\
    \bottomrule
  \end{tabularx}
\end{table}
```

- 无竖线，三线（`\toprule` / `\midrule` / `\bottomrule`）
- 短列（≤12字符宽）用 `l`，长文本列用 `X`；至少一列为 `X`
- `\caption` 在 `\begin{tabularx}` **上方**（thuthesis 规范：表题在上）
- `render.py` 自动去掉 caption 里的"表X-X "前缀，由 thuthesis 自动编号

### 图片格式

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.9\linewidth]{figures/image1.png}
  \caption{图题}
  \label{fig:xxx}
\end{figure}
```

- 图片文件放在 LaTeX 工程的 `figures/` 目录
- `render.py` 自动去掉 caption 里的"图X-X "前缀，由 thuthesis 自动编号
- SVG 跳过，需手动转 PNG/PDF 后补入
- chart 对象（Excel 图表）由 matplotlib 重绘为 PNG，自动纳入流程

## 已知限制

- SVG 图片跳过（需手动转为 PNG/PDF 后补入）
- committee.tex / comments.tex / resolution.tex 为占位，需手工填写（答辩后）

### ⚠️ .doc 格式必须用 Word 转换，不能用 textutil

**唯一可靠方法：用 Microsoft Word 打开 .doc 文件，另存为 .docx。**

macOS `textutil`、Python `docx2txt` 等工具**会把表格压平为普通段落**，导致：
- `extract` 步骤报告"0 表格"
- 表格数据变成一行行普通文字进入正文
- 图片和封面元信息也可能丢失

**判断转换是否正确的方法**：运行 `extract` 后，看终端输出的"📊 表格 X 张"行：

| 输出 | 原因 | 处理 |
|------|------|------|
| `表格: N 张` N > 0 | 转换正确，表格保留 | 正常继续 |
| `表格: 0 张` 但论文明显有表 | 转换工具破坏了表格结构 | **必须重新用 Word 另存为 .docx** |

如果没有 Word，可在 macOS 用 LibreOffice（需安装）：
```bash
soffice --headless --convert-to docx /path/to/论文.doc --outdir /path/to/
```

**LibreOffice 保留表格结构，textutil 不保留。**

## thuthesis 配置（MBA 专业硕士）

```latex
\thusetup{
  degree = {master},
  degree-type = {professional},
  degree-category = {工商管理硕士},
  degree-category* = {Master of Business Administration},
  department = {经济管理学院},
}
```
