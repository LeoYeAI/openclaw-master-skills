---
name: biomedical-paper
description: |
  AI-powered biomedical manuscript generation with docx output.
  Activates when user provides Chinese draft/outline and requests full English research paper.
  Includes: Abstract, Introduction, Methods, Results, Discussion, References.
  Specialized for: GBD epidemiology, cohort studies (CHARLS/NHANES), cross-sectional mediation analyses, pharmacovigilance (FAERS).
  Also supports: Chinese graduate/doctoral thesis (学位论文) formatting.
  Features: python-docx generation, Vancouver numbered references, journal-specific formatting.
  Confidence: High (validated workflow with 30+ successful papers)
---

# Biomedical Paper Writing Skill

Produces publication-ready English biomedical manuscripts (or Chinese theses) from drafts using python-docx.

---

## 核心工作流（必读）

### Phase 1: 接收与分析
1. 用户提供中文草稿/大纲 → 确认论文类型（见下）
2. 识别所有数据（统计值、样本量、引用编号）
3. **立即执行引用预验证**：将参考文献列表中的每一条与PubMed核对，标记无法验证的条目
4. 如有引用缺失/无法验证 → **先补充验证，再生成正文**

### Phase 2: 生成正文
5. 按论文类型套用标准结构模板（见本文档各类型模板）
6. 所有统计数据（β/OR/RR/AAPC/95%CI/p值）**必须原文照录**，不得编造
7. 引用编号全程追踪：记录"引用编号映射表"（见下方规范）

### Phase 3: 生成参考文献
8. 按 Vancouver 格式逐条生成引用（见"引用生成规范"）
9. 引用编号以正文中的实际使用为准，**不沿用草稿中的旧编号**
10. 参考文献单独存 docx，并附加"引用编号映射表"说明文件

---

## 论文类型与模板

### Type 1: GBD 流行病学（疾病负担趋势分析）
- **模板文献**: SIICI (Neuroblastoma Asia, GBD 2023)
- **数据**: GBD database (ghdx.healthdata.org)
- **方法**: Joinpoint Regression, EAPC/AAPC, ASIR/ASMR/DALYs
- **关键词**: Neuroblastoma; Neonate; Disease burden; Incidence; Mortality; DALYs; Asia
- **表格**: 4张（按地区/SDI/性别/年龄分层）
- **图片**: 5张（趋势线、choropleth地图）
- **伦理**: GBD IRB豁免（University of Washington）
- **必须注明**: ICD-10 和 ICD-9 代码

### Type 2: 队列 / 登记数据库分析
- **模板文献**: CHARLS (Social participation & diabetes)
- **数据**: CHARLS, NHANES, MIMIC, SEER, FAERS 等
- **方法**: K-means聚类, logistic/linear回归, Cox比例风险, 亚组分析
- **关键词**: social participation; [disease]; incidence; [database]; K-means; mediation analysis
- **表格**: 4–13张（描述性统计、聚类轮廓、回归结果、亚组分析）
- **图片**: 5–17张（ROC曲线、K-M曲线、聚类轮廓、趋势图）
- **伦理**: 豁免IRB（去标识数据）

### Type 3: 交叉横断面 / 中介分析
- **模板文献**: GBS (Phthalates, SII, cognitive function)
- **数据**: NHANES, 横断面调查
- **方法**: Linear/logistic回归 + 中介分析（bootstrap N=1000）
- **关键词**: phthalates; systemic inflammation; Systemic Immune-Inflammation Index; cognitive function; older adults; mediation
- **表格**: 4张（人口学特征、回归β+95%CI、中介分解）
- **关键指标**: SII = 血小板×中性粒细胞/淋巴细胞; SIRI = 中性粒细胞×单核细胞/淋巴细胞

### Type 4: 学位论文（中文，硕士/博士）
- **语种**: 中文（正文）+ 英文摘要
- **格式要求**: 依各院校研究生院规范；正文宋体小四，英文Times New Roman 12pt
- **章节结构**: 前言 → 资料与方法 → 结果 → 讨论 → 结论 → 参考文献
- **引用格式**: 顺序编码制（与期刊Vancouver相同格式）
- **字数要求**: 硕士论文 ≥3万字，博士论文 ≥5万字（各校标准）
- **核心规范**: 不可有占位符（如"[此处补充数据]"）；表格内数据须与正文一致

---

## 引用预验证工作流（最关键环节）

### 操作步骤
```
Step 1: 提取用户提供的参考文献列表（全部条目）
Step 2: 对每一条执行 PubMed 搜索或 batch_web_search
        查询格式: "[第一作者] [期刊缩写] [发表年]" 或 "PMID: XXXXXXXX"
Step 3: 标记结果:
        ✅ VERIFIED (PMID匹配) → 可直接使用
        ⚠️  NEEDS_REVIEW → 作者/年份/期刊有偏差，需修正后使用
        ❌ NOT_FOUND → 无法验证，必须替换为可验证的真实文献
Step 4: 如有 NOT_FOUND 条目:
        → 搜索同一研究领域3年内（≤3年）的高质量真实文献替代
        → 记录替换原因（如：原引用#14 [虚构]，替换为 Li M等 Syst Rev 2024;13:171）
Step 5: 生成最终"引用编号映射表"（见下）
```

### 引用编号映射表（每次必须生成）
```markdown
## 引用编号映射表

| 旧编号 | 新编号 | 作者 | 期刊 | 年份 | PMID | 备注 |
|--------|--------|------|------|------|------|------|
| #1   | #1   | Lei J等 | Lancet Reg Health West Pac | 2024 | — | 替换（原文虚构） |
| #8   | #2   | Lei J等 | Lancet Reg Health West Pac | 2024 | — | 与#1合并/替换 |
| #14  | DEL  | —     | —    | —    | —    | 删除（虚构引用） |
| #15  | #14  | Li M等  | Syst Rev | 2024 | — | 重新编号 |
| ...  | ...  | ...   | ...  | ...  | ... | 递进 |
```

> ⚠️ **重要教训**：PRISm大论文（2026-03-22）中，草稿含虚构引用（#14等），导致引用需全面重编。以后所有任务必须先验证再使用，任何无法PubMed查证的引用必须替换。

---

## 标准摘要格式（所有类型通用）

```
Objective: To [verb] whether/how [exposure/topic] [association] in [population] [using data from] [database].

Methods: [Study design], [N] participants/records from [database, year range]. [Key inclusion criteria]. [Statistical methods: clustering/regression/etc.]. [Mediation/stratification if applicable].

Results: [Main cluster/profile finding] (n=%, n=%). [Key association with OR/β, 95% CI, P-value]. [Subgroup findings]. [Mediation result] (ACME proportion %).

Conclusion: [Main finding]. [Mechanism/pathway implication]. [Policy/practice recommendation].
```

- 字数: 250–350词
- **摘要内不使用小标题**（无"Background:", "Methods:"等）

---

## 标准前言格式（4段递进结构）

```
Paragraph 1 — 疾病/暴露负担:
[疾病/暴露]是一种[定义]。[全球/国家患病率，趋势]。[临床意义]。

Paragraph 2 — 流行病学背景:
流行病学研究表明[模式]。[主要危险因素]。[近期变化：COVID-19、老龄化等]。

Paragraph 3 — 研究缺口:
尽管[已有知识]，但[缺口：缺乏比较/中介/预测研究]。[地区/数据库比较]有限。

Paragraph 4 — 研究目的:
利用[数据库]，本研究旨在：(i) [目的1]；(ii) [目的2]；(iii) [目的3]。(如为学位论文，还需详述各章安排。)
```

---

## 标准方法格式

### GBD 方法
```
所有数据均从公开可用的 GBD [年份] 数据库获取（http://ghdx.healthdata.org/gbd-results-tool）。
GBD研究整合了多个流行病学数据来源——包括人口登记、调查、已发表文献、
医院记录和死因数据——并采用标准化建模框架生成跨国跨时期的可比负担估算。
[疾病]采用 ICD-10 代码 [X] 和 ICD-9 代码 [Y] 进行识别。
[结局]提取自[国家]，时间为[年份]：[列举结局]，均以每10万人表示，
并按GBD全球标准人群进行年龄标准化。
本研究使用公开可用的去标识化汇总数据，已获得华盛顿大学机构伦理审查委员会豁免；
无需额外伦理审批。
```

### 队列 / 登记数据库方法
```
本研究为[回顾性/前瞻性] [队列/登记]研究，利用[数据库名称][年份范围]数据。
[纳入标准]: [N]名参与者/记录符合[临床/人口学标准]。
[排除标准]: [因X原因排除的记录数]。
[暴露/干预]: [按X标准定义]。
结局由[临床标准/ICD代码]定义。
统计分析：[回归类型]，调整[协变量]。亚组分析按[因素]分层。
[中介/因果分析]采用[方法，bootstrap N次]。
所有分析使用[软件，版本号]完成。
```

### 交叉横断面中介方法
```
本研究为横断面研究，分析[数据库，年份范围]中[N]名[年龄范围]参与者的数据。
[暴露变量]的测量方式/定义：[详述]。
[中介变量]采用[公式/检测方法]评估。
[结局]采用[量表/测试]评估。
关联性采用[linear/logistic]回归分析，调整[协变量]。
中介分析采用[Hayes PROCESS宏/bootstrap方法]，bootstrap样本数[N]。
```

---

## 标准结果格式

```
共纳入[N]名[参与者/记录]。[描述性发现]。

[主要发现]：[关联性，含β/OR/RR、95%CI、P值]。

[次要发现]：[亚组/分层结果]。

[中介发现]：[中介变量]显著中介了[关联性]（ACME=[值]，95%CI=[范围]，P=[值]；中介比例=[%]）。

[表X–X]展示了[具体结果]。
```

### 统计报告规范（严格遵守）
- 格式: `OR=0.77 (95% CI: 0.65–0.91, P=0.002)` 或 `β=−0.13 (95% CI: −0.21 to −0.05, P=0.001)`
- P值保留3位小数（不是"P < 0.05"，而是"P=0.043"）
- 样本量: `n=1,234 (45.6%)`
- 禁止使用占位符如 `[此处数据]` 或 `[待补充]`

---

## 标准讨论格式（5个子节）

### 1. 主要发现
```
本研究利用[数据库]提供了[首个/最全面的][主题][分析]。
主要发现表明[主要关联性，含统计数据]。
```

### 2. 机制解读
```
该发现可能由[机制/通路]解释。
[引用文献]提供了支持证据。
```

### 3. 与其他研究比较
```
与[作者，年份]的研究结果一致，该研究报道了[发现]。
相比之下，[作者，年份]发现了[不同结果]，这可能归因于[原因]。
```

### 4. 局限性（≥4条，学位论文要求≥5条）
```
本研究存在以下局限性。第一，[GBD: 模型不确定性] / [队列: 回忆/报告偏倚] / [横断面: 因果推断受限]。第二，[生态学研究设计]。第三，[数据代表性局限]。第四，[特定数据缺口]。第五（如适用）：[研究设计假设]。
```

### 5. 结论
```
综上所述，[主要发现]。[机制/通路意义]。本研究结果为[目标人群的针对性预防/临床建议/政策制定]提供了[循证依据]。
```

---

## 引用生成规范

### 格式要求（Vancouver，悬挂缩进）
```
编号. 作者A, 作者B, 作者C, 等. 标题. 期刊缩写. 年份;卷(期):页码. doi:XXXXX
```
- 作者姓，名首字母（无点），最多作者显示至第3位后加", et al."
- 期刊名用标准缩写（参考 PubMed Journal List）
- 含 DOI 时必须附 DOI
- 悬挂缩进: 0.35英寸
- 字体: Times New Roman 10pt
- 段后距: 6pt

### python-docx 悬挂缩进实现
```python
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn

def add_reference(doc, number, text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(-0.35)
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(f'{number}. {text}')
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(10)
```

---

## docx XML 操作规范（进阶）

> 以下是文档内部操作的硬核规范，修改现有docx时必须遵守。

### 字体替换（完整遍历run）
```python
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

doc = Document(path)

for p in doc.paragraphs:
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
        run.font.size = Pt(11)

doc.save(path)
```

### 段落删除
```python
body = doc.element.body
for p in doc.paragraphs:
    if 'PLACEHOLDER' in p.text or p.text.strip() == '':
        body.remove(p._element)
```

### 段落插入（指定位置）
```python
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

def insert_paragraph_after(doc, ref_para, text, bold=False, font_size=11):
    """在 ref_para 之后插入新段落"""
    new_p = OxmlElement('w:p')
    # 设置格式...
    ref_idx = list(doc.element.body).index(ref_para._element)
    doc.element.body.insert(ref_idx + 1, new_p)
    return new_p
```

### 从后往前插入（避免索引偏移）
```python
# 需要在多个位置插入时，先收集所有位置，从后往前排序
positions = [idx3, idx1, idx2]  # 要插入的索引
positions.sort(reverse=True)  # 从大到小
for idx in positions:
    body.insert(idx, new_element)
```

### 段落属性设置
```python
from docx.oxml.ns import qn

p_elem = para._element
pPr = p_elem.get_or_add_pPr()
spacing = OxmlElement('w:spacing')
spacing.set(qn('w:line'), '360')    # 1.5行距 (360=单倍*240)
spacing.set(qn('w:lineRule'), 'auto')
spacing.set(qn('w:after'), '200')   # 段后间距
pPr.append(spacing)
```

---

## 学位论文专门规范（Type 4）

### 排版要求
| 项目 | 要求 |
|------|------|
| 正文字体 | 宋体小四（12pt） |
| 英文/数字 | Times New Roman 12pt |
| 行距 | 1.5倍行距 |
| 页边距 | 上下2.54cm，左右3cm |
| 一级标题 | 黑体三号，居中 |
| 二级标题 | 黑体四号 |
| 引用文献 | 顺序编码，同Vancouver格式 |

### 章节扩充工作流（扩充+30%等比例要求）
```
1. 统计原文段落数（Introduction原44段→目标59段，新增15段）
2. 识别可扩充方向：
   - 添加"近期限望变化/新指南"段落（如GOLD 2025更新）
   - 添加"研究方法路径图"说明
   - 添加"全球/区域对比"数据
   - 添加"机制假说"讨论段
3. 每扩充一段，同步更新引用列表（如有新增引用）
4. 生成扩充版后，重新运行引用编号映射
```

### 引用编号映射（学位论文特有问题）
- **插入新引用** → 后续所有编号+1
- **删除引用** → 后续所有编号-1
- **必须同步更新**：正文引用、全文交叉引用、参考文献列表
- 生成文件命名：`ch8_references_最终版.docx` = 每次修订后的最终版本

---

## 质量检查清单（每次提交前必查）

### 引用验证（最高优先级）
- [ ] 所有引用均可 PubMed 查证（含 PMID 或可验证期刊页码）
- [ ] 虚构引用已全部替换为真实文献
- [ ] 引用编号映射表已生成并保存
- [ ] 正文引用编号与参考文献列表完全对应

### 数据真实性
- [ ] 所有 AAPC/EAPC/β/OR/RR/95%CI/p 值原文照录
- [ ] 无任何占位符（`[待补充]`、`[此处数据]`等）
- [ ] 表格数据与正文数据完全一致

### 格式
- [ ] 摘要 ≤350 词，无小标题
- [ ] 前言 4 段（或各校规定段数）
- [ ] 讨论 ≥5 条局限性（学位论文）
- [ ] 参考文献：Vancouver，悬挂缩进0.35"，Times New Roman 10pt
- [ ] 图表编号连续（Table 1, Table 2...; Figure 1, Figure 2...）

### 学位论文额外检查
- [ ] 全文无中英混排标点错误
- [ ] 目录结构符合学校研究生院规范
- [ ] 字数满足学校要求（硕士≥3万字，博士≥5万字）
- [ ] 中英文摘要完整（含研究目的、方法、主要结果、结论）

---

## 常见修订模式

| 用户反馈 | 处理策略 |
|---------|---------|
| "内容不够充实" / "+30%" | 识别可扩充方向，添加最新指南段落/对比数据/机制假说 |
| "引用有误" | 先 PubMed 验证，再更新引用映射表，最后同步正文编号 |
| "占位符未清理" | 搜索所有 `[` 和 `]` 模式，逐一补充或删除 |
| "太生硬/不自然" | 添加衔接词（"Interestingly," "Notably," "In contrast,"） |
| "强调某一发现" | 扩充结果段，增加与亚组/分层数据对比 |
| "添加亚组分析" | 新增亚组分析表格 + 描述段落 + 更新引用 |
| "格式不一致" | 统一字体、行距、引用缩进，逐段检查 run.font.name |

---

## Python Docx 生成模板（完整版）

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(11)

# 设置默认中文字体
style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# ── 标题 ──────────────────────────────────────
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run('论文标题（主标题）')
r.bold = True; r.font.size = Pt(16)
r.font.name = 'Times New Roman'
r._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

# ── 英文标题（期刊用）───
sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub_p.add_run('Running Title: 英文简写标题（≤40字符）')
r.italic = True; r.font.size = Pt(10)
r.font.name = 'Times New Roman'

# ── 摘要 ──────────────────────────────────────
doc.add_heading('Abstract', level=2)
abstract_p = doc.add_paragraph()
abstract_p.paragraph_format.first_line_indent = Inches(0.3)
abstract_p.paragraph_format.space_after = Pt(6)
r = abstract_p.add_run('Objective: ... Methods: ... Results: ... Conclusion: ...')
r.font.name = 'Times New Roman'; r.font.size = Pt(11)

# 关键词
kw_p = doc.add_paragraph()
r = kw_p.add_run('Keywords: ')
r.bold = True; r.font.name = 'Times New Roman'
kw_p.add_run('keyword1; keyword2; keyword3; keyword4; keyword5.').font.name = 'Times New Roman'

# ── 中文摘要（学位论文）─────────────────────
doc.add_heading('摘要', level=2)
# ... 同理，中文宋体小四

# ── 正文章节 ──────────────────────────────────
for heading, level in [
    ('Introduction', 2),
    ('Methods', 2),
    ('Results', 2),
    ('Discussion', 2),
    ('Conclusion', 2),
    ('References', 2),
]:
    doc.add_heading(heading, level=level)

# ── 参考文献（悬挂缩进）─────────────────────
def add_ref(doc, num, text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(-0.35)
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f'{num}. {text}')
    r.font.name = 'Times New Roman'; r.font.size = Pt(10)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

# 示例
add_ref(doc, 1, 'Lei J, Zhang X, Wang Q. et al. Title. Lancet Reg Health West Pac. 2024;45:101021. doi:10.1016/j.lanwpc.2024.101021')
add_ref(doc, 2, 'Li M, Chen H, Liu G. Title. Syst Rev. 2024;13:171. doi:10.1186/s13643-024-XXX')

doc.save('/workspace/output.docx')
print('✅ Saved: /workspace/output.docx')
```

---

## 输出文件命名规范

```
期刊论文: [主题]_v1.docx → [主题]_v2.docx → [主题]_最终版.docx
学位论文章节: ch[N]_章节名.docx → ch[N]_章节名_修订版.docx → ch[N]_章节名_最终版.docx
引用列表: ch[N]_references_fixed.docx（修正编号）→ ch[N]_references_updated.docx（+新文献）→ ch[N]_references_最终版.docx
引用映射: citation_mapping_[日期].md
```

---

## 关键规则（永久有效）

| 规则 | 说明 |
|------|------|
| 引用必须先验证 | 任何无法PubMed查证的引用，必须替换为真实文献，禁止保留虚构引用 |
| 编号映射全程追踪 | 每次增删引用，同步更新正文编号和映射表 |
| 数据原文照录 | 统计值不得四舍五入改变精度，不得凭空编造 |
| 无占位符原则 | 正文和表格中不得有任何 `[待补充]` 类占位符 |
| 从后往前插入 | 多点插入时按索引从大到小操作，避免索引偏移 |
| 每次修订存档 | `xxx_v1.docx` → `xxx_v2.docx` → `xxx_最终版.docx`，不覆盖历史版本 |
