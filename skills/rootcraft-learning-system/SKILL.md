---
name: rootcraft-learning-system
version: 1.1.4
author: 张权 (Zhang Quan)
author_website: https://www.luckydesigner.space
author_brand: Luckydesigner（行运设计师）
author_pen_name: 伯衡君
name_display: 格物本质赋能学习法
description: RootCraft Learning System - An integrated learning methodology combining First Principles Thinking, Taxonomy-Based Classification, Feynman Technique, and Recursive Questioning for deep knowledge mastery and "aha moment" discovery. Includes Anki memory cards generation based on Ebbinghaus forgetting curve. Chinese name: 格物本质赋能学习法.
trigger_keywords: learning method, first principles, taxonomy classification, feynman technique, recursive questioning, aha moment, efficient learning, study system, knowledge mastery, how to learn, learn about, 格物致知, 学习方法, 啊哈时刻, 如何学习, 想学习, 帮我学习, 我想学习, 学习教程, 教学, 培训
---

# RootCraft Learning System (格物本质赋能学习法)

---

## 🎓 User Guide / 使用指南

> When user asks "how to use this skill" or "如何使用", show this guide.

### 中文引导 (Chinese Guide)

```
🎓 欢迎使用格物本质赋能学习法！

这是一个高效学习系统，帮你从"学了就忘"变成"学了就懂"。

┌─────────────────────────────────────────────────────────────┐
│  📚 核心方法                                              │
├─────────────────────────────────────────────────────────────┤
│  🔍 第一性原理    →  追问本质，挖到不能再挖为止           │
│  📊 分类学        →  系统拆解，构建 MECE 结构             │
│  🎤 费曼 technique →  讲给别人听，发现知识缺口            │
│  ❓ 递归追问      →  层层深挖，追到"啊哈"时刻            │
└─────────────────────────────────────────────────────────────┘

📋 9 步学习流程：
1. 设定目标 & 评估标准
2. 应用第一性原理
3. 分类学拆解
4. 费曼 + 递归追问（核心）
5. 多视角学习
6. 实践应用
7. 反馈与迭代
8. 持续复习
9. 思维导图与笔记

🚀 快速开始：
• 直接说"我想学习【主题】" → 直接开始完整学习流程
• 或说"帮我用格物本质赋能学习法学习【内容】"
• 说"我想制定学习计划"让我帮你规划

⚡ **直接学习模式**：
当用户说"我想学习XX"时，直接输出完整的9步学习流程，不要问问题！

流程模板：
```
🎓 好的，让我们开始学习【主题】！

--- 9步学习流程 ---

1. 设定目标 & 评估标准
（直接给出该主题的学习目标和评估标准）

2. 第一性原理
（解释该主题的本质是什么）

3. 分类学拆解（MECE）
（系统化拆解该主题的知识体系）

4. 费曼 + 递归追问
（核心概念检验 + 追问链）

5. 多视角学习
（从数学、工程、应用等角度分析）

6. 实践应用
（给出一个最小可运行的代码示例）

7. 反馈与迭代
（含**试卷生成**功能）
```
🎯 试卷生成：根据所学内容自动生成测试题

题型包括：
• 选择题（3-5题）- 检验概念理解
• 填空题（3-5题）- 检验关键术语记忆
• 简答题（2-3题）- 检验逻辑表达能力
• 操作题（1-2题）- 检验实际应用能力

每道题标注：难度等级、知识点归属、参考答案
```

8. 持续复习
（艾宾浩斯遗忘曲线复习计划）

9. 思维导图与笔记
（输出知识图谱）

💡 Aha Moment记录
📦 Anki卡片

--- 自动保存详细内容 ---
⚠️ 必须将上述9步的详细内容保存到文件，而不是只保存模板！

保存方式：
```python
import sys
sys.path.insert(0, '/root/.openclaw/skills/rootcraft-learning-system')
from study_writer import create_study_files

# 将详细内容保存到文件
content = {
    "goals": """# 学习目标\n\n（详细内容）""",
    "first_principles": """# 第一性原理\n\n（详细内容）""",
    # ... 其他步骤的详细内容\n}
result = create_study_files('主题', content, anki_cards)
```

> 💡 **内容质量提示**：为了生成高质量文档，请在content中提供详细、完整的内容。\n> \n> **详细模板示例**：\n```python\ncontent = {\n    'goals': \"\"\"# 学习目标\n\n## 短期目标（1-4周）\n- 理解AI的基本概念和核心原理\n- 掌握机器学习基础知识\n\n## 中期目标（1-3个月）\n- 深入理解机器学习核心理论\n- 能够独立完成ML项目\n\n## 长期目标（3-12个月）\n- 达到专业水平\n- 能够创新和解决问题\n\n## 评估标准\n- [ ] 掌握核心概念≥10个\n- [ ] 完成项目≥3个\n- [ ] 学习时长≥100小时\n\"\"\",\n    \n    'first_principles': \"\"\"# 第一性原理\n\n## 核心公理\n\n### 公理1：机器学习是函数拟合\n- 输入x → f(x) → 输出y\n- 关键是找到最好的f\n\n### 公理2：数据决定模型上限\n- Garbage In, Garbage Out\n- 特征工程决定效果\n\n### 公理3：没有免费午餐\n- 没有最优算法\n\n### 公理4：奥卡姆剃刀\n- 简单模型往往更好\n\n## 核心定义\nAI的本质是[填写]\n\n## 关键洞察\n> 一句话总结核心领悟\n\"\"\",\n    \n    'taxonomy': \"\"\"# 知识分类体系\n\n## 算法分类\n\n### 监督学习\n| 类型 | 算法 | 场景 |\n|------|------|------|\n| 分类 | 逻辑回归、SVM | 分类预测 |\n| 回归 | 线性回归、GBDT | 数值预测 |\n\n### 无监督学习\n| 类型 | 算法 | 场景 |\n|------|------|------|\n| 聚类 | K-Means | 用户分群 |\n| 降维 | PCA | 可视化 |\n\n### 深度学习\n| 模型 | 应用场景 |\n|------|------|\n| CNN | 图像 |\n| Transformer | NLP |\n\"\"\",\n    \n    'feynman': \"\"\"# 费曼检验\n\n## 核心概念检验\n\n### Q1: 什么是梯度下降？\nA: 像下山找最低点，每次往低处走一点\n\n### Q2: 过拟合是什么？\nA: 记住题库而不是学会做题\n\n## 递归追问链\n- 最根本的原因是什么？\n- 还有更基础的原因吗？\n\n## Aha Moment\n记录你的领悟时刻\n\"\"\",\n    \n    'multi_perspective': \"\"\"# 多视角学习\n\n## 技术视角\n- 算法原理\n- 实现方法\n- 优缺点\n\n## 应用视角\n- CV、NLP、推荐系统\n- 行业案例\n\n## 历史视角\n- 发展历程\n- 关键里程碑\n\n## 哲学视角\n- 思维方式\n- 底层逻辑\n\"\"\",\n    \n    'practice': \"\"\"# 实践应用\n\n## 最小可运行方案\n\n### 环境准备\n```bash\npip install numpy pandas scikit-learn\n```\n\n### 核心代码\n```python\nimport numpy as np\nfrom sklearn.linear_model import LinearRegression\n\n# 示例代码\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\n```\n\n## 实战项目\n- 项目1：入门级\n- 项目2：进阶级\n\"\"\",\n    \n    'feedback': \"\"\"# 反馈与迭代\n\n## 常见问题\n\n### Q1: 数学不够怎么办？\nA: 够用即可：梯度、矩阵、概率\n\n### Q2: 调参玄学怎么办？\nA: 网格搜索→贝叶斯优化\n\n## 解决方案\n1. 制定计划\n2. 定期复盘\n\"\"\",\n    \n    'review': \"\"\"# 复习计划\n\n## 艾宾浩斯复习表\n\n| 时间点 | 内容 |\n|--------|------|\n| 10分钟 | 核心概念 |\n| 1天 | 基础知识点 |\n| 3天 | 进阶知识 |\n| 7天 | 整体串联 |\n| 14天 | 重点强化 |\n| 30天 | 全面复盘 |\n\n## 记忆技巧\n- 联想记忆\n- 间隔重复\n\"\"\",\n    \n    'mindmap': \"\"\"# 思维导图\n\n## 中心主题\n机器学习\n\n## 一级分支\n- 基础：数学、Python\n- 算法：监督、无监督、深度学习\n- 工程：数据处理、模型训练、部署\n- 应用：CV、NLP、推荐\n\n## 关键连接\n- 基础→算法→应用\n\"\"\"\n}\n```\n
✅ 文件保存到 /root/.openclaw/workspace/study/{主题}/
✅ 包含12个md文件 + anki_cards.csv
✅ 新增：08-exam.md（试卷文件）

⚠️ **重要**：每次学习流程结束后，必须调用文件生成模块：
```python
import sys
sys.path.insert(0, '/root/.openclaw/skills/rootcraft-learning-system/study_writer')
from study_writer import generate_and_save, quality_check, print_quality_report, save_exam_paper

# 1. 生成学习文件
result = generate_and_save('主题名称')

# 2. 手动生成试卷（可选）
exam_path = save_exam_paper('主题名称')

# 3. 执行质检
qc_result = quality_check('主题名称')
print_quality_report(qc_result)
```

📋 **质检模块** (Quality Check) - v1.1.1:
每次学习流程结束后，系统检查以下内容：

| 检查项 | 文件 | 说明 |
|--------|------|------|
| ✅ 学习目标 | 01-goals.md | 1.设定目标&评估标准 |
| ✅ 第一性原理 | 02-first-principles.md | 2.第一性原理分析 |
| ✅ 分类学拆解 | 03-taxonomy.md | 3.MECE结构拆解 |
| ✅ 费曼+追问 | 04-feynman.md | 4.核心概念检验 |
| ✅ 多视角学习 | 05-multi-perspective.md | 5.多角度分析 |
| ✅ 实践应用 | 06-practice.md | 6.最小可运行示例 |
| ✅ 反馈与迭代 | 07-feedback.md | 7.常见问题+试卷 |
| ✅ 持续复习 | 08-review.md | 8.艾宾浩斯计划 |
| ✅ 思维导图 | 09-mindmap.md | 9.知识图谱 |
| ✅ Aha Moment | 10-aha-moment.md | 啊哈时刻记录 |
| ✅ Anki卡片 | anki_cards.csv | 可导入的记忆卡片 |
| ⭐ **试卷文件** | 08-exam.md | **选择题+填空题+简答题+操作题** |

**质检函数**：
```python
from study_writer import quality_check, print_quality_report

qc = quality_check('主题名称')
print_quality_report(qc)
```

**试卷生成函数**：
```python
from study_writer import save_exam_paper

exam_file = save_exam_paper('主题名称')
print(f"试卷已保存: {exam_file}")
```

💡 特色产出：
• Aha Moment 记录本（追踪每个"啊哈"时刻）
• 知识分类树（系统化拆解）
• ⭐ **自动试卷生成**（选择题+填空题+简答题+操作题）
• ⭐ 新增：Anki 记忆卡片生成（基于艾宾浩斯遗忘曲线）
• 递归追问链（问题链条）

📦 **记忆卡片功能** (Memory Cards)：
- 说「生成【主题】的Anki卡片」→ 自动生成可导入 Anki 的卡片
- 说「查看我的复习计划」→ 显示基于记忆曲线的复习安排
- 说「导出生词卡片」→ 导出 CSV 文件，可在 Anki 中导入使用
- 支持中英文
```

### English Guide

```
🎓 Welcome to RootCraft Learning System!

An efficient learning methodology that transforms "learn and forget" into "learn and understand."

┌─────────────────────────────────────────────────────────────┐
│  📚 Core Methods                                           │
├─────────────────────────────────────────────────────────────┤
│  🔍 First Principles    →  Ask why until reaching essence  │
│  📊 Taxonomy            →  Systematically decompose (MECE) │
│  🎤 Feynman Technique   →  Teach to find knowledge gaps    │
│  ❓ Recursive Questioning →  Dig deeper to find "aha!"      │
└─────────────────────────────────────────────────────────────┘

📋 9-Step Learning Flow:
1. Define Goals & Evaluation
2. Apply First Principles
3. Taxonomy-Based Classification
4. Feynman + Recursive Questioning (Core)
5. Multi-Perspective Learning
6. Practice & Application
7. Feedback & Iteration
8. Continuous Review
9. Mind Mapping & Notes

🚀 Quick Start:
• Just say "I want to learn【topic】" → Directly start full learning flow
• Or "Help me learn【content】using this method"
• Say "I want to create a study plan" for guidance

⚡ **Direct Learning Mode**:
When user says "I want to learn XX", directly output the complete 9-step learning flow - NO QUESTIONS ASKED!

Template:
```
🎓 Alright! Let's learn 【topic】!

--- 9-Step Learning Flow ---

1. Goals & Evaluation
2. First Principles
3. Taxonomy (MECE)
4. Feynman + Recursive Questioning
5. Multi-Perspective
6. Practice Application
7. Feedback & Iteration
8. Continuous Review
9. Mind Map & Notes

💡 Aha Moment
📦 Anki Cards
```

💡 Key Outputs:
• Aha Moment Log (track every "aha!" moment)
• Knowledge Taxonomy Tree (systematic decomposition)
• ⭐ NEW: Anki Memory Cards (Ebbinghaus forgetting curve based)
• ⭐ NEW: Exam Paper Generation (Multiple Choice + Fill-in + Short Answer + Practice)
• Recursive Question Chains (question chains)
• 🤖 AI Question Chain Generator (Bilingual)

📋 **Quality Check Module** (v1.1.1):
After learning completes, run quality check:

```python
import sys
sys.path.insert(0, '/root/.openclaw/skills/rootcraft-learning-system/study_writer')
from study_writer import generate_and_save, quality_check, print_quality_report, save_exam_paper

# 1. Generate study files
result = generate_and_save('topic')

# 2. Generate exam paper (optional)
exam_path = save_exam_paper('topic')

# 3. Run quality check
qc_result = quality_check('topic')
print_quality_report(qc_result)
```

**Quality Check Files (12 total)**:

| # | Check Item | File | Description |
|---|------------|------|-------------|
| 1 | Goals | 01-goals.md | Goal setting & evaluation |
| 2 | First Principles | 02-first-principles.md | Core axioms analysis |
| 3 | Taxonomy | 03-taxonomy.md | MECE decomposition |
| 4 | Feynman | 04-feynman.md | Concept validation |
| 5 | Multi-Perspective | 05-multi-perspective.md | Multi-angle analysis |
| 6 | Practice | 06-practice.md | Code examples |
| 7 | Feedback | 07-feedback.md | FAQ + exam |
| 8 | Review | 08-review.md | Ebbinghaus schedule |
| 9 | Mind Map | 09-mindmap.md | Knowledge graph |
| 10 | Aha Moment | 10-aha-moment.md | Aha records |
| 11 | Anki Cards | anki_cards.csv | Importable cards |
| 12 | ⭐ Exam Paper | 08-exam.md | MC+Fill+QA+Practice |

📦 **Memory Cards Feature**:
- Say "Generate Anki cards for [topic]" → Auto-generate Anki-importable cards
- Say "Show my review schedule" → Display memory curve-based review plan
- Say "Export vocabulary cards" → Export CSV for Anki import
- Supports Chinese & English
```

---

## Core Principle

A high-efficiency learning methodology that integrates **First Principles Thinking**, **Taxonomy-Based Classification**, **Feynman Technique**, and **Recursive Questioning** into a closed-loop system:

1. **First Principles** → Trace to fundamental facts and concepts
2. **Classification** → Systematically decompose and structure
3. **Feynman Technique** → Validate through output, identify gaps
4. **Recursive Questioning** → Chase "aha moments" through layered inquiry

## Learning Flow (9 Steps)

When users mention learning, exam prep, or skill acquisition, guide them through this process:

### Step 1: Define Goals & Evaluation Criteria
- Clarify learning objectives (target proficiency level)
- Establish evaluation standards (how to measure mastery)
- Set timelines and milestones

### Step 2: Apply First Principles
- Break down problems to find fundamental facts
- Keep asking "why" until reaching irreducible truths
- Distinguish between assumptions and verified facts

### Step 3: Use Taxonomy-Based Classification
- Divide topics into distinct subtopics/categories
- Build classification systems (preferably MECE: Mutually Exclusive, Comprehensively Encompassing)
- Clarify relationships between categories

### Step 4: Apply Feynman Technique with Recursive Questioning

**Core Process (5 Sub-Steps)**:

#### 4.1 Start with a Real Problem
- Begin with concrete, practical challenge
- Example: "Write a diffusion model code" or "Implement this algorithm"
- Ground learning in tangible context

#### 4.2 Generate Questions Through Practice
- While working, note every confusion point
- Ask: "Why does this work?" "What does this term mean?"
- Record questions without immediately seeking answers

#### 4.3 Recursive Downward Questioning
- For each unclear concept, ask deeper questions
- Pattern: "What do you mean by X?" → "Why is X necessary?" → "What happens without X?"
- Continue until reaching intuitive understanding
- Example chain:
  - "What is 'gradient descent'?" →
  - "Why do we need to minimize loss?" →
  - "What is 'loss' actually measuring?" →
  - "Why is measuring error useful?" →
  - **Aha!** "Loss is just a compass pointing toward better answers"

#### 4.4 Restate in Your Own Words
- After each answer, rephrase to confirm understanding
- Use: "So my understanding is... Is this correct?"
- If explanation feels forced or unclear, return to 4.3
- Valid understanding = can explain to a 10-year-old

#### 4.5 Chase the "Aha!" Moments
- Recognize the click: "Oh! That's why!"
- These moments mark true comprehension milestones
- Document each aha moment with:
  - What was unclear before
  - What clicked
  - Why it matters
- **Key insight**: One deep aha > Ten shallow memorizations

### Step 5: Multi-Perspective Learning
- Use diverse resources (books/videos/courses/practical exercises)
- Cross-validate information across sources
- Find the optimal personal learning path

### Step 6: Practice & Application
- Select relevant projects for hands-on practice
- Analyze real-world case studies
- Connect theory with practical application
- Apply recursive questioning to new challenges

### Step 7: Feedback & Iteration
- Regular review of learned content
- Seek peer feedback (teach, question, evaluate)
- Adjust learning strategy based on insights
- Revisit aha moments to reinforce understanding

**📝 Exam Paper Generation** (NEW in v1.1.1):
```
🎯 Auto-generate exam questions based on learning content

Question types:
• Multiple Choice (3-5) - Concept understanding
• Fill in the Blank (3-5) - Key term memory
• Short Answer (2-3) - Logical expression
• Practical/Code (1-2) - Application ability

Each question includes: difficulty level, knowledge point, reference answer
```

### Step 8: Continuous Learning & Review
- Periodically revisit mastered content (spaced repetition)
- Follow Ebbinghaus Forgetting Curve for reviews
- Expand into related knowledge domains
- Apply recursive questioning to advanced topics

### Step 9: Mind Mapping & Notes
- Use mind mapping tools to organize knowledge structure
- Build systematic note-taking systems (Cornell Notes method)
- Maintain traceable and updatable notes
- **Special**: Create "Aha Moment Log" tracking breakthrough insights

## Trigger Scenarios

When users say (English):
- "I want to learn..."
- "How to learn efficiently..."
- "Is there a good learning method..."
- "Help me create a study plan..."
- "This concept is unclear..."
- "Want to systematically master..."
- "Why does this work?"
- "I don't understand..."

当用户说 (Chinese/中文):
- "我想学习..."
- "怎么高效学习？"
- "有什么好的学习方法？"
- "帮我制定学习计划..."
- "这个概念不清楚..."
- "想系统掌握..."
- "为什么是这样？"
- "我不懂..."

→ 主动推荐此学习方法 / Proactively recommend this method

---

## Multi-Language Response (Bilingual Support)

This skill supports **bilingual responses** based on user's language preference. The response language should match the user's input language.

### Language Detection Logic

| User Input Language | Response Language | Example Trigger |
|---------------------|-------------------|-----------------|
| English | English | "I want to learn machine learning" |
| 中文/Chinese | Chinese (中文) | "我想学习机器学习" |
| Mixed | Use dominant language | If majority is Chinese → Chinese |

### Response Template

**When user speaks English:**
```
# RootCraft Learning System

This is a high-efficiency learning methodology...

[English content following the 9-step flow]
```

**When user speaks Chinese:**
```
# 格物本质赋能学习法 (RootCraft Learning System)

这是一个融合第一性原理、分类学、费曼 technique 与递归追问的高效学习系统...

[中文内容，遵循 9 步流程]
```

### Key Bilingual Elements

| Element | English | Chinese |
|---------|---------|---------|
| Skill Name | RootCraft Learning System | 格物本质赋能学习法 |
| Core Concept | First Principles | 第一性原理 |
| Key Term | Aha Moment | 啊哈时刻 |
| Method | Feynman Technique | 费曼 technique |
| Framework | Taxonomy Classification | 分类学拆解 |
| Process | Recursive Questioning | 递归追问 |

### Practical Guidelines

1. **Detect language** from user's first message
2. **Switch language** only at conversation start, maintain consistency
3. **Bilingual output** for skill description sections (both languages)
4. **User guidance** always in user's detected language
5. **Technical terms** can remain in English (e.g., MECE, Feynman) with Chinese explanation

---


---

## 🤖 AI-Assisted Question Chain Generation

> 自动生成递归追问链 / Auto-generate recursive questioning chains

This skill can automatically generate **recursive questioning chains** for any topic using AI. The question chain helps users dig deeper until reaching the "aha moment".

### Trigger Commands / 触发指令

| 中文指令 | English Command |
|----------|-----------------|
| 帮我生成关于【主题】的追问链 | Generate a question chain for 【topic】 |
| 用 AI 深挖【概念】 | Dig deeper into 【concept】 with AI |
| 自动追问【主题】 | Auto-question 【topic】 |
| 生成追问链 | Create question chain |

### How It Works / 工作原理

```
用户输入 → 检测意图（生成追问链）
         → 提取主题
         → 调用 LLM 生成（中英文双语）
         → 格式化输出
         → 建议用户"继续深挖"或"记录 Aha"
```

### Prompt Template (Bilingual) / 提示词模板

#### 中文版本

```
你是一个专业的学习教练，擅长用递归追问法帮助学生理解任何概念。

请为「{topic}」生成一个 {depth} 层的递归追问链。

## 格式要求

### Level 1: 基础定义
- 问题要简洁明了
- 答案要用通俗语言，像在和 10 岁小孩说话

### Level 2: 原理追问
- 问"为什么"
- 给出技术解释

### Level 3: 本质挖掘
- 问到最底层的"为什么"
- 区分假设和事实

### Level 4: 边界测试
- 问"如果没有 X 会怎样"
- 探索反例

### Level 5: 啊哈时刻
- 用一句话总结本质
- 用一个比喻让 10 岁小孩也能懂

## 输出格式

### Q1: [问题]
**A1**: [答案]

### Q2: [问题]
**A2**: [答案]

...

💡 **AHA MOMENT**: [一句话本质总结 + 通俗比喻]
```

#### English Version

```
You are a professional learning coach, skilled at using recursive questioning to help students understand any concept.

Please generate a {depth}-level recursive questioning chain for "{topic}".

## Format Requirements

### Level 1: Basic Definition
- Questions should be concise and clear
- Answers should use simple language, like explaining to a 10-year-old

### Level 2: Principle Inquiry
- Ask "why"
- Provide technical explanation

### Level 3: Essence Mining
- Ask the deepest "why"
- Distinguish between assumptions and facts

### Level 4: Boundary Testing
- Ask "what if X didn't exist?"
- Explore counterexamples

### Level 5: Aha Moment
- Summarize the essence in one sentence
- Use a metaphor a 10-year-old can understand

## Output Format

### Q1: [Question]
**A1**: [Answer]

### Q2: [Question]
**A2**: [Answer]

...

💡 **AHA MOMENT**: [One-sentence essence summary + simple metaphor]
```

### Example Output / 示例输出

**Input / 输入**: topic = "梯度下降" / "gradient descent"

**Output / 输出**:

```
## 追问链：梯度下降 / Question Chain: Gradient Descent

### Q1: 什么是梯度下降？ / What is gradient descent?
**A1**: 梯度下降是一种优化算法，用来找到函数的最小值。就像下山时每一步都往最陡的下坡走。

### Q2: 为什么要用"梯度"？ / Why use "gradient"?
**A2**: 梯度指向函数上升最快的方向。反过来，沿着梯度的相反方向走，就是下降最快的方向。

### Q3: 为什么一定要"下降"？ / Why must it "descend"?
**A3**: 因为我们的目标是找到最小值（最优解）。下降是逼近最小值的方式。

### Q4: 如果不用梯度，还有什么方法？ / If not gradient, what else?
**A4**: 还有牛顿法（用二阶导数）、随机搜索、遗传算法等。但梯度下降是最简单高效的。

### Q5: 梯度下降的本质是什么？ / What's the essence of gradient descent?
**A5**: 梯度下降的本质是"贪心策略"——每一步都做当前最优选择，虽然不一定全局最优，但足够实用。

💡 **AHA MOMENT**:
梯度下降 = "每步都往下走一走"
本质 = 贪心算法在优化问题上的应用
比喻 = 像盲人下山，每步都摸一下坡度，往最陡的方向走
```

### Supported Parameters / 支持参数

| Parameter | 说明 / Description | Default / 默认值 |
|-----------|-------------------|-----------------|
| topic | 学习主题 / Learning topic | Required / 必填 |
| depth | 追问深度 / Question depth | 5 |
| focus | 重点方向（可选）/ Focus area (optional) | None |
| language | 输出语言 / Output language | auto-detect |

### Post-Generation Actions / 生成后操作

1. **建议继续深挖** / Suggest continuing:
   - "要针对某一层继续追问吗？"
   - "Want to dig deeper into any specific level?"

2. **建议记录 Aha** / Suggest recording:
   - "可以把你的 Aha Moment 记录下来，要我帮你写进去吗？"
   - "Would you like me to record your Aha Moment?"

3. **生成追问链卡片** / Generate shareable card:
   - 可生成图片/文本格式的追问链卡片
   - Can generate image/text format question chain cards

## Output Format Suggestions

Can generate for users:
- Learning goal checklist
- Knowledge taxonomy tree
- Feynman explanation template
- **Recursive questioning script** (question chain template)
- **Aha moment tracker** (breakthrough log)
- Review schedule table
- Mind mapping structure

## File Organization

✅ **自动保存**：学习资料会自动保存到以下路径

路径：`/root/.openclaw/workspace/study/{主题}/`

示例：
```
/root/.openclaw/workspace/study/机器学习/
├── 01-goals.md              # 学习目标和评估标准
├── 02-first-principles.md   # 第一性原理分析
├── 03-taxonomy.md           # 知识分类体系
├── 04-feynman.md            # 费曼 Technique 笔记
├── 04b-recursive-questions.md # 递归追问链
├── 04c-aha-moments.md       # Aha Moment 记录
├── 05-resources.md          # 学习资源列表
├── 06-projects.md           # 实践项目代码
├── 07-feedback.md           # 反馈与迭代记录
├── 08-review.md             # 复习计划
└── 09-mindmap.md            # 思维导图源文件
```

**自动生成内容**：
1. 9步学习流程的完整笔记（11个md文件）
2. Anki记忆卡片（anki_cards.csv，与笔记同目录）
3. 复习计划表

**文件用途**：
- 可直接在本地查阅
- 可导入Notion/Obsidian等工具
- Anki卡片可导入Anki用于复习

## Recommended Tools

- Mind Mapping: XMind, MindNode, Obsidian
- Note-taking: Notion, Obsidian, Evernote
- Spaced Repetition: Anki, RemNote
- Pomodoro Timer: Forest, Focus
- Question Tracking: Obsidian Daily Notes, Notion Database

## Version History

| Version | Date       | Changes |
|---------|------------|---------|
| 1.1.2   | 2026-05-04 | Fix: 试卷生成选择题选项修复，改为有意义的学习相关选项 |
| 1.1.0   | 2026-05-02 | Fixed: Save detailed learning content to files instead of templates |
| 1.0.5   | 2026-05-02 | Added Anki memory cards generation based on Ebbinghaus forgetting curve - supports Chinese & English |
| 1.0.4   | 2026-05-01 | Added AI-assisted question chain generation (bilingual: Chinese & English) |
| 1.0.3   | 2026-05-01 | Added detailed user guide / onboarding section for easy start |
| 1.0.2   | 2026-05-01 | Added multi-language response support - responses now adapt to user's language (English/Chinese) |
| 1.0.1   | 2026-05-01 | Added Chinese name "格物本质赋能学习法" as display name, updated trigger keywords |
| 1.0.0   | 2026-04-30 | Official release - Integrated First Principles, Taxonomy Classification, Feynman Technique, and Recursive Questioning into 9-step learning flow with "Aha Moment" tracking |
| 0.1.0   | 2024-XX-XX | Original Chinese version "格物本质赋能学习法" launched |

## Example: Learning Diffusion Models

### Step 1: Set Goals
- **Goal**: Understand and implement a basic diffusion model
- **Evaluation**: Can explain forward/reverse process and generate images
- **Time**: 2-3 weeks

### Step 2: First Principles
Diffusion essence = Gradual noise addition + Learned denoising
- Why add noise gradually?
- What does "learned denoising" mean?
- How does this connect to thermodynamics?

### Step 3: Taxonomy
```
Diffusion Models
├── Forward Process (noise scheduling)
├── Reverse Process (denoising network)
├── Training Objective (noise prediction)
├── Sampling (iterative denoising)
└── Applications (image generation, inpainting)
```

### Step 4: Recursive Questioning in Action

**Question Chain Example**:
```
Q: "Why do we add noise gradually?"
→ A: "To create a tractable path between data and noise"

Q: "What does 'tractable path' mean?"
→ A: "A path we can reverse mathematically"

Q: "Why do we need to reverse it?"
→ A: "Because generation = going from noise back to data"

Q: "Why start from noise at all?"
→ A: "Noise is easy to sample; data is hard to model directly"

💡 AHA! "Diffusion is like unscrambling an egg - we practice scrambling 
   so much we learn to unscramble!"
```

### Step 5: Multi-Perspective
- Paper: "Denoising Diffusion Probabilistic Models"
- Video: Lilian Weng's blog explanation
- Code: Hugging Face Diffusers library

### Step 6: Practice
- Implement simple 1D diffusion
- Use diffusers for 2D image generation
- Modify noise schedule and observe effects

### Step 7: Feedback
- Explain to colleague/peer
- Write blog post on understanding
- Compare with other generative models

### Step 8: Review
- Revisit aha moments weekly
- Connect to VAEs, GANs, flows
- Apply to new domains (audio, video)

### Step 9: Mind Map
```
Diffusion Models
├── Core Insight: "Learned unscrambling"
├── Forward: Data → Noise (easy)
├── Reverse: Noise → Data (learned)
└── Aha: "Practice destroying to learn creating"
```