---
name: literature-reviewer-skill
description: |
  根据用户提供的论文主题，进行系统性中英文文献回顾（Literature Survey）。
  采用8阶段工作流，支持CNKI、Web of Science、ScienceDirect等主流数据库，
  无需API配置，通过浏览器自动化获取文献信息。
  输出包含GB/T 7714-2015引文、标题、摘要的Markdown文档。
  当用户提到"文献回顾"、"文献综述"、"帮我找文献"、"中英文文献搜索"、"写综述"等关键词时触发。

  NOTE: The 'examples/' folder contains sample outputs and is not included in skill installation.
---

# 文献回顾（Literature Survey）

根据用户提供的论文主题，进行系统性的中英文文献检索、整理和综述撰写。
采用 **8阶段工作流**，无需API配置，通过浏览器自动化获取文献。

---

## 8阶段工作流

```
Phase 0: Session Log      → 创建会话目录
Phase 1: Query Analysis   → 生成中英文检索策略  
Phase 2: Parallel Search  → 浏览器自动化检索
Phase 3: Deduplication    → 标题相似度去重
Phase 4: Verification     → 基础元数据校验
Phase 5: Data Export      → 导出文献信息
Phase 6: Paper Analysis   → 单篇文献深度分析
Phase 7: Citation Format  → GB/T 7714-2015格式化
Phase 8: Synthesis        → 生成综述文档
```

---

## Phase 0: Session Log（会话管理）

创建会话目录，记录工作进度。

**目录结构**：
```
sessions/{YYYYMMDD}_{topic_short}/
├── session_log.md          # 工作日志
├── metadata.json           # 会话元数据
├── papers_raw.json         # 原始检索结果
├── papers_deduplicated.json # 去重后文献
├── papers_analysis.json    # 文献分析结果
└── output/
    ├── references.md       # 文献清单（含摘要）
    ├── papers_analysis.md  # 单篇文献分析
    └── literature_review.md # 最终综述
```

---

## Phase 1: Query Analysis（查询分析）

AI 智能分析研究主题，生成相关关键词和检索策略。

### AI 提示词模板

```
You are tasked with generating relevant keywords or phrases for a given research direction.

The research direction is provided below:
<research_direction>
{{用户输入的研究主题}}
</research_direction>

To complete this task:

1. Carefully analyze the provided research direction.
2. Identify core concepts, methods, techniques, or topics in this research area.
3. Generate 5 to 8 of the most relevant and representative keywords or phrases.
4. Ensure keywords are concise, typically 1-3 words each.
5. Make sure the keywords cover different aspects of the research direction.
6. Order the keywords by importance or relevance.
7. Separate keywords with English commas (,).
8. Do not include any explanations, descriptions, or additional text.
9. Provide keywords in both Chinese and English.

Present your result in the following format:

中文关键词：keyword1, keyword2, keyword3, ...
英文关键词：english_keyword1, english_keyword2, english_keyword3, ...

Example for "人工智能在医疗诊断中的应用":
中文关键词：人工智能, 医疗诊断, 机器学习, 深度学习, 医学影像, 辅助诊断, 疾病预测, 智能诊疗
英文关键词：artificial intelligence, medical diagnosis, machine learning, deep learning, medical imaging, computer-aided diagnosis, disease prediction, intelligent diagnosis
```

### 输出格式

```yaml
研究主题: "基于深度学习的医学图像诊断研究"

中文关键词:
  - 深度学习
  - 医学图像
  - 诊断
  - 神经网络
  - 计算机辅助诊断
  
英文关键词:
  - deep learning
  - medical imaging
  - diagnosis
  - neural network
  - computer-aided diagnosis

检索策略:
  CNKI: "SU=('深度学习'+'神经网络')*('医学图像'+'影像')*('诊断'+'辅助诊断')"
  WOS: "TS=((deep learning OR neural network) AND (medical imaging) AND (diagnosis))"
```

---

## Phase 2: Parallel Search（并行检索）

**核心数据库**（无需API，浏览器自动化）：

| 数据库 | 优先级 | 检索方式 |
|--------|--------|----------|
| CNKI | 1 | 浏览器访问高级检索页面 |
| Web of Science | 2 | 浏览器访问检索页面 |
| ScienceDirect | 3 | 浏览器访问检索页面 |
| PubMed | 4 | 网页搜索 + 浏览器访问 |
| Google Scholar | 5 | 网页搜索 |

**检索步骤**：
1. 使用 `browser_navigate` 访问各数据库检索页面
2. 填充检索式，执行搜索
3. 提取前50条结果的标题、作者、期刊、年份、DOI、摘要
4. 保存到 `papers_raw.json`

**字段提取**：
```json
{
  "source_db": "cnki",
  "title": "文献标题",
  "authors": ["作者1", "作者2"],
  "journal": "期刊名称",
  "year": 2023,
  "volume": "46",
  "issue": "5",
  "pages": "1023-1035",
  "doi": "10.xxxx",
  "abstract": "摘要内容...",
  "keywords": ["关键词1", "关键词2"],
  "url": "原文链接"
}
```

---

## Phase 3: Deduplication（去重筛选）

**简化去重策略**：

1. **DOI匹配** - 相同DOI视为重复
2. **标题相似度** - Levenshtein距离 > 0.85 视为重复
3. **保留规则** - 保留信息更完整的记录

**筛选条件**：
- 时间：近10年优先
- 来源：优先保留核心期刊/高质量来源
- 数量：中英文各15-25篇，总计30-50篇

---

## Phase 4: Verification（基础验证）

简化验证流程：

1. **元数据完整性检查** - 确保标题、作者、期刊、年份存在
2. **DOI格式校验** - 检查DOI格式有效性
3. **明显错误过滤** - 排除标题为"无"或作者缺失的记录

---

## Phase 5: Data Export（数据导出）

导出文献信息到Markdown文件。

**输出文件**：`output/references.md`

**文件格式**：
```markdown
# 文献清单

## 中文文献

### C1
- **标题**: 基于深度学习的医学图像诊断研究
- **作者**: 张三, 李四, 王五
- **期刊**: 计算机学报
- **年份**: 2023
- **卷期**: 46(5): 1023-1035
- **DOI**: 10.xxxx
- **摘要**: 本文研究了...
- **来源**: CNKI

## 英文文献

### E1
- **Title**: Deep Learning for Medical Image Analysis
- **Authors**: Smith J, Johnson K, Lee M
- **Journal**: Nature Medicine
- **Year**: 2022
- **Volume/Issue**: 28(8): 1500-1510
- **DOI**: 10.1038/s41591-022-01900-0
- **Abstract**: This study presents...
- **Source**: ScienceDirect
```

---

## Phase 6: Paper Analysis（单篇文献分析）

对每篇文献进行深度分析，提取关键信息。

### AI 提示词模板

```
You are an AI assistant tasked with analyzing and interpreting academic articles.

For each article, follow these steps:

1. Identify and summarize the main research question(s) and objective(s) of the article.
2. Describe the theoretical framework or model used in the study.
3. Summarize the research methodology and design employed.
4. Extract and summarize the key findings and conclusions.
5. Highlight any innovative aspects of the study and point out potential limitations.
6. Analyze how this article relates to other research in the field.
7. Identify any controversial points or unresolved issues mentioned in the article.
8. Identify any trends or emerging directions in the research field mentioned.

Present your analysis in the following structured format:

**文章[N]：[Article Title]**
**主要观点和结论**：[Summary of main points and conclusions]
**局限性**：[Discussion of limitations]
**争议点**：[Identified controversies or disputed points]
**研究内容缺陷**：[Areas not covered by the research]
**参考文献格式**：[GB/T 7714-2015 format for this paper]

Use "---" to separate each article analysis.

Ensure that you analyze and provide output for ALL articles. Do not omit any article from your analysis.
```

### 输出格式

```markdown
# 文献深度分析

---

**文章1：基于深度学习的医学图像诊断研究**

**主要观点和结论**：
本文提出了一种基于卷积神经网络的医学图像诊断方法，在肺结节检测任务上取得了95%的准确率。研究表明深度学习方法能够有效辅助医生进行病灶识别。

**局限性**：
1. 数据集规模相对较小，仅有1000例样本
2. 缺乏多中心验证
3. 模型对少见病例的泛化能力有待验证

**争议点**：
- 深度学习模型的"黑盒"特性与医疗可解释性需求的矛盾
- 辅助诊断系统的责任归属问题

**研究内容缺陷**：
- 未涉及模型的临床部署方案
- 缺少与现有商用系统的对比
- 未讨论数据隐私保护机制

**参考文献格式**：
张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.

---
```

---

## Phase 7: Citation Format（引用格式化）

生成GB/T 7714-2015格式引文。

**中文期刊格式**：
```
[C1] 张三, 李四, 王五. 基于深度学习的医学图像诊断研究[J]. 计算机学报, 2023, 46(5): 1023-1035. DOI:10.xxxx.
```

**英文期刊格式**：
```
[E1] Smith J, Johnson K, Lee M. Deep learning for medical image analysis[J]. Nature Medicine, 2022, 28(8): 1500-1510. DOI:10.1038/s41591-022-01900-0.
```

---

## Phase 8: Synthesis（综述生成）

综述生成是文献回顾的核心环节，采用**四步迭代法**确保输出高质量学术综述。

---

### Phase 8.1: Outline（生成综述大纲）

**目标**：基于文献主题聚类，构建逻辑清晰的综述结构

**输入**：
- 研究主题
- 文献清单（含单篇分析结果）
- 目标语言

**AI 提示词模板**：

```
You are a renowned professor specializing in research methodology and academic writing.
Your task is to create a comprehensive, well-structured, and logically sound literature review outline.

Research topic:
<research_topic>
{{研究主题}}
</research_topic>

Collected literature analysis:
<collected_literature>
{{文献清单和分析}}
</collected_literature>

Target language:
<language>
{{中文/英文}}
</language>

Instructions:

1. Analyze all collected papers and identify 3-5 main themes or research directions.

2. Structure the outline as follows:
   a) Introduction (background, objectives, search strategy)
   b) Theoretical Foundation and Methods
   c) Main Body (3-5 sections based on theme clustering)
      - Domestic Research Status (Chinese literature)
      - International Research Status (English literature)
      - Or thematic sections (e.g., Algorithm Research, Clinical Applications)
   d) Discussion (comparative analysis, research gaps, trends)
   e) Conclusion
   f) References

3. For each main section, provide 3-5 specific subsections with clear titles.

4. Ensure logical flow:
   - From general to specific
   - From theory to application
   - From past to future directions

5. Allocate literature to appropriate sections:
   - Each paper should be referenced in at least one section
   - Highlight connections between papers

6. Output format:
   # Literature Review Outline: [Research Topic]
   
   ## 1 Introduction
   ### 1.1 Research Background
   ### 1.2 Research Objectives
   ### 1.3 Search Strategy
   
   ## 2 Theoretical Foundation
   ### 2.1 [Theory/Method 1]
   ### 2.2 [Theory/Method 2]
   
   ## 3 [Main Theme 1]
   ### 3.1 [Sub-theme]
   - Key papers: [C1], [E1], [E2]
   - Main arguments: ...
   ### 3.2 [Sub-theme]
   
   [Continue for all themes...]
   
   ## 4 Discussion
   ### 4.1 Comparative Analysis
   ### 4.2 Research Gaps
   ### 4.3 Future Directions
   
   ## 5 Conclusion
   
   ## References

7. Do not write any content for the sections, only the structure.

8. Ensure the outline can support a 3000-5000 word literature review.
```

**输出**：`outline.md` - 完整的综述大纲，含章节结构和文献分配

---

### Phase 8.2: Writing（撰写综述初稿）

**目标**：基于大纲撰写完整的综述内容，建立文献间的逻辑联系

**输入**：
- 综述大纲
- 文献清单和分析
- 单篇文献深度分析

**AI 提示词模板**：

```
You are a literature writing expert tasked with creating a high-quality, comprehensive academic literature review.

Input materials:
<outline>
{{综述大纲}}
</outline>

<collected_literature>
{{文献清单和摘要}}
</collected_literature>

<detailed_analysis>
{{单篇文献深度分析}}
</detailed_analysis>

Target language: {{中文/英文}}

Writing instructions:

1. Expand EACH section in the outline into detailed content:
   - Section 1 (Introduction): 300-500 words
   - Section 2 (Theoretical Foundation): 500-800 words
   - Section 3 (Main Body): 1500-2500 words (divided among subsections)
   - Section 4 (Discussion): 500-800 words
   - Section 5 (Conclusion): 200-300 words

2. For each subsection:
   - Start with a topic sentence summarizing the main point
   - Synthesize 3-5 relevant papers (do not summarize one by one)
   - Compare and contrast different studies
   - Highlight agreements and disagreements in the literature
   - Identify patterns and trends

3. Critical analysis requirements:
   - Evaluate methodological strengths and weaknesses
   - Point out inconsistencies or contradictions
   - Question assumptions and limitations
   - Suggest alternative interpretations

4. Citation format:
   - Use ([C1](url)), ([E1](url)) for in-text citations
   - Every claim should be supported by at least one citation
   - Group related citations: ([C1], [C2], [E1])

5. Writing style:
   - Academic and formal tone
   - Clear and concise sentences
   - Logical transitions between paragraphs
   - Avoid bullet points in main text (use prose)

6. Structure each paragraph:
   - Topic sentence
   - Evidence from literature (with citations)
   - Critical commentary
   - Transition to next point

7. Output the complete review in Markdown format without XML tags.

8. Do not include abstract or keywords yet (will be added in Phase 8.4).
```

**输出**：`draft.md` - 完整的综述初稿（3000-5000字）

---

### Phase 8.3: Review（质量审查与评估）

**目标**：系统性审查综述质量，识别问题和改进点

**输入**：
- 综述初稿
- 原始文献清单
- 研究主题

**AI 提示词模板**：

```
You are an experienced academic review expert specializing in literature reviews.
Conduct a comprehensive, rigorous multi-dimensional assessment of the submitted literature review.

Materials to review:
<literature_review_draft>
{{综述初稿}}
</literature_review_draft>

<original_topic>
{{研究主题}}
</original_topic>

<collected_papers>
{{原始文献清单}}
</collected_papers>

Review criteria:

a) ACCURACY AND COMPREHENSIVENESS (Weight: 25%)
   - Are all factual claims accurate?
   - Are there any misrepresentations of cited studies?
   - Does it cover all important aspects of the topic?
   - Are significant papers missing or overlooked?
   - Score: ___/10

b) LOGICAL ARGUMENTATION (Weight: 25%)
   - Is the overall structure logical and coherent?
   - Do arguments flow naturally from one to another?
   - Are all claims adequately supported by evidence?
   - Are there any logical fallacies or gaps?
   - Score: ___/10

c) LITERATURE CITATIONS (Weight: 20%)
   - Are citations accurate and properly formatted?
   - Is the citation density appropriate (not too sparse or excessive)?
   - Are cited papers relevant to the claims made?
   - Is there a balance between different sources?
   - Score: ___/10

d) CRITICAL ANALYSIS (Weight: 15%)
   - Does it go beyond mere summarization?
   - Are methodological strengths/weaknesses discussed?
   - Are contradictions and controversies identified?
   - Is there genuine synthesis (not just listing papers)?
   - Score: ___/10

e) LANGUAGE AND STYLE (Weight: 10%)
   - Is the language clear, concise, and academic?
   - Are there grammatical errors or awkward phrasing?
   - Is the tone appropriate for academic writing?
   - Score: ___/10

f) INNOVATION AND INSIGHT (Weight: 5%)
   - Does it provide new insights or perspectives?
   - Are future research directions clearly identified?
   - Is there a theoretical framework proposed?
   - Score: ___/10

Deliverables:

1. Overall Quality Score: ___/100

2. Detailed Assessment:

<review>
<major_strengths>
[List 3-5 major strengths of the review with specific examples]
</major_strengths>

<critical_issues>
[List critical issues that MUST be fixed, with specific locations (section/paragraph)]
</critical_issues>

<areas_for_improvement>
[List areas that could be improved for better quality]
</areas_for_improvement>

<missing_elements>
[List important elements missing from the review]
</missing_elements>

<specific_suggestions>
[Provide detailed, actionable suggestions for revision]
1. Section X, Paragraph Y: [Specific issue] → [Suggested fix]
2. ...
</specific_suggestions>

<citation_issues>
[Identify any citation errors or missing citations]
</citation_issues>
</review>

3. Revision Priority:
   - CRITICAL (Must fix): [List]
   - HIGH (Should fix): [List]
   - MEDIUM (Nice to have): [List]
```

**输出**：`review_report.md` - 详细的审查报告，含评分和改进建议

---

### Phase 8.4: Final（最终润色与定稿）

**目标**：根据审查报告修订并生成最终版本，添加摘要和关键词

**输入**：
- 综述初稿
- 审查报告
- 研究主题

**AI 提示词模板**：

```
You are tasked with finalizing a literature review article based on a draft and review feedback.

Input materials:
<draft>
{{综述初稿}}
</draft>

<review_report>
{{审查报告}}
</review_report>

<research_topic>
{{研究主题}}
</research_topic>

Finalization steps:

1. ADDRESS REVIEW FEEDBACK:
   - Fix all CRITICAL issues identified in the review
   - Address HIGH priority suggestions
   - Consider MEDIUM priority improvements if time permits

2. STRUCTURE AND FORMATTING:
   - Ensure proper Markdown formatting
   - Apply consistent heading levels (# Title, ## Section, ### Subsection)
   - Check that all citations use format ([X](url))
   - Verify all URLs are valid

3. CONTENT REFINEMENT:
   - Strengthen weak arguments
   - Add missing citations
   - Improve transitions between sections
   - Ensure critical analysis is present throughout
   - Balance coverage across topics

4. WRITE ABSTRACT (200-300 words):
   Structure:
   - Background (1-2 sentences): Context and importance
   - Objective (1 sentence): Purpose of the review
   - Methods (1-2 sentences): Search strategy and inclusion criteria
   - Results (2-3 sentences): Main findings and themes
   - Conclusion (1-2 sentences): Key implications

5. SELECT KEYWORDS (5-8 keywords):
   - Include main research topics
   - Include key methods/technologies
   - Include application domains
   - Separate with semicolons

6. COMPILE REFERENCES:
   - Convert in-text citations to GB/T 7714-2015 format
   - Sort by citation number ([C1], [C2]..., [E1], [E2]...)
   - Ensure all cited papers are in the reference list

7. FINAL POLISH:
   - Proofread for spelling and grammar
   - Check for consistent terminology
   - Ensure academic tone throughout
   - Verify word count (target: 3000-5000 words excluding references)

Output format:

```markdown
# [Research Topic]: A Literature Review

## Abstract

[200-300 word abstract]

**Keywords**: keyword1; keyword2; keyword3; keyword4; keyword5

---

[Main content with all revisions applied]

---

## References

[C1] ...
[C2] ...
[E1] ...
...
```

Requirements:
- Output ONLY the finalized review in Markdown
- No XML tags
- No meta-commentary about the revision process
- Ready for direct use or submission
```

**输出**：`literature_review.md` - 最终定稿的完整综述（含摘要、关键词、参考文献）

---

### Phase 8 输出文件

| 文件 | 阶段 | 内容 |
|------|------|------|
| `outline.md` | 8.1 | 综述大纲，含章节结构和文献分配 |
| `draft.md` | 8.2 | 综述初稿（3000-5000字） |
| `review_report.md` | 8.3 | 质量审查报告，含评分和改进建议 |
| `literature_review.md` | 8.4 | **最终定稿**（含摘要、关键词、参考文献） |

---

### 四步法的质量保证

| 步骤 | 质量控制点 | 常见问题 |
|------|-----------|---------|
| **Outline** | 结构逻辑性、主题覆盖度 | 章节不平衡、遗漏重要主题 |
| **Writing** | 论证深度、批判性思维 | 简单罗列、缺乏分析 |
| **Review** | 准确性、完整性 | 事实错误、引用不当 |
| **Final** | 学术规范性、可读性 | 格式混乱、语言问题 |

---

### 迭代机制

如果审查报告显示严重问题（总分<70），可以：

1. **小修**（70-85分）：直接在 Final 阶段修正
2. **中修**（60-70分）：回到 Writing 阶段重写部分章节
3. **大修**（<60分）：回到 Outline 阶段重新规划结构

**默认流程**：按 8.1 → 8.2 → 8.3 → 8.4 顺序执行一次
**迭代流程**：8.4 发现问题 → 回到对应阶段 → 重新执行后续步骤

---

## 数据库访问指南

### CNKI

**访问地址**：`https://kns.cnki.net/kns8/AdvSearch`

**字段代码**：
| 代码 | 含义 |
|------|------|
| SU | 主题 |
| TI | 篇名 |
| KY | 关键词 |
| TKA | 篇关摘 |

**来源筛选**：CSSCI、北大核心、CSCD

### Web of Science

**访问地址**：`https://www.webofscience.com/wos/woscc/advanced-search`

**常用字段**：
- TS=Topic
- TI=Title
- AB=Abstract
- SO=Source

### ScienceDirect

**访问地址**：`https://www.sciencedirect.com/search`

---

## 输出文件说明

| 文件 | 内容 | 用途 |
|------|------|------|
| `references.md` | 完整文献清单（含摘要） | 文献查阅 |
| `papers_analysis.md` | 单篇文献深度分析 | 理解每篇文献 |
| `literature_review.md` | 结构化综述（含摘要、关键词） | 直接使用 |
| `gb7714_citations.txt` | GB/T格式引文列表 | 复制到论文 |

---

## 依赖 Skills

- **docx** - 生成Word格式综述（可选）
- **web_search** - 辅助获取文献信息
- **browser** - 数据库检索自动化

---

## 使用示例

**用户**：帮我做一个关于"深度学习在肺癌早期诊断中的应用"的文献回顾

**执行流程**：
1. AI生成中英文关键词和检索策略
2. 并行检索 CNKI、WOS、ScienceDirect、PubMed
3. 整理去重，保留中英文各20篇
4. 导出 `references.md`
5. **单篇文献深度分析** → `papers_analysis.md`
6. 生成综述大纲 → 撰写 → 审查 → 润色 → `literature_review.md`
7. 输出 GB/T 7714-2015 格式引文

---

## 触发关键词

- "文献回顾"
- "文献综述"
- "帮我找文献"
- "中英文文献搜索"
- "写综述"
- "literature survey"
- "systematic review"
