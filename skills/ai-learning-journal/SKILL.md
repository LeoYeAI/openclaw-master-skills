---
name: ai-learning-journal
description: "AI 学习记录与成长追踪工具。用于记录 AI/LLM 学习笔记、使用心得、Prompt 技巧、工具体验等，并提供学习指导和规划。当用户提到以下任何话题时都应使用此 skill：AI 学习记录、学习笔记、AI 使用心得、Prompt 工程学习、模型对比体验、AI 工具使用记录、LLM 学习、RAG 学习、Agent 学习、MCP 学习、AI 微调实践、AI 学习规划、怎么学 AI、AI 入门、学习路线推荐、从零学 AI、推荐学习资源、AI 学习方向、如何系统学习 AI、学习方法建议、回顾学习记录、学习总结、AI 知识整理。即使用户只是随口提了一句\"今天试了一下 Claude\"或\"学了个新的 prompt 技巧\"，也应当触发此 skill 帮助用户结构化记录。This skill also triggers for English queries such as: AI learning notes, learning journal, AI study plan, how to learn AI, AI learning roadmap, prompt engineering tips, model comparison, AI tool review, LLM learning, RAG tutorial, agent development notes, fine-tuning practice, AI learning recommendations, review my learning history, learning summary, AI knowledge base. Even casual mentions like \"tried Claude today\" or \"learned a new prompting trick\" should trigger this skill."
---

# AI 学习记录与成长追踪

帮助用户系统化记录 AI 学习历程，提供学习指导与规划建议。所有记录以 Markdown 文件形式持久化存储，支持回溯查阅与知识总结。

## 存储规范

所有学习记录保存在本 skill 目录下的 `records/` 文件夹中。

```
records/
├── index.md                    # 全局索引（每次新增/修改记录后自动更新）
├── plans/                      # 学习规划文件
│   └── YYYY-MM-DD-规划主题.md
├── summaries/                  # 知识总结报告
│   └── YYYY-MM-月度总结.md
└── YYYY-MM/                    # 按年月组织的学习记录
    └── YYYY-MM-DD-主题关键词.md
```

路径说明：
- 本 skill 的根目录位于用户的 `~/.copilot/skills/ai-learning-journal/`
- `records/` 的绝对路径即 `~/.copilot/skills/ai-learning-journal/records/`
- 使用 `create_file` 创建新记录，使用 `replace_string_in_file` 更新已有记录和 index.md

---

## 功能一：结构化记录

### 触发场景

用户描述了一段 AI 相关的学习经历或使用体验，例如：
- "今天学了 RAG 的原理"
- "试了一下 Claude 的 MCP，感觉很强"
- "记录一下我用 Cursor 写代码的心得"
- "分享一下我对 GPT-4o 和 Claude 的对比感受"

### 交互流程

1. **理解用户输入**：用户可能以口语化、零散的方式描述学习内容，耐心提取关键信息
2. **补充提问**（仅在信息明显不足时）：轻量地询问 1-2 个关键问题，不要变成问卷调查。例如：
   - "你是在什么场景下用的？效果怎么样？"
   - "有没有遇到什么坑或意外发现？"
3. **生成结构化记录**：将用户输入整理成以下模板格式
4. **保存文件**：写入 `records/YYYY-MM/` 目录
5. **更新索引**：在 `records/index.md` 中追加一行记录

### 记录模板

```markdown
# 学习记录: [主题]

- **日期**: YYYY-MM-DD
- **领域**: [见下方领域分类]
- **标签**: [关键词1, 关键词2, ...]
- **难度**: [入门 / 进阶 / 高阶]

## 学习内容

[用户学到了什么，核心概念和要点]

## 使用场景

[在什么场景/项目中使用或学到的]

## 关键发现与心得

[用户的个人感悟、对比思考、最佳实践]

## 遇到的问题

[学习过程中的困惑、踩过的坑、未解决的疑问]

## 参考资源

[相关链接、文档、教程、论文等]
```

### 领域分类

记录的领域从以下类别中选取（可多选）：
- **Prompt Engineering**：提示词设计、技巧、模式
- **RAG**：检索增强生成、向量数据库、Embedding
- **Agent & Tool Use**：AI Agent、MCP、Function Calling、工具集成
- **模型使用与对比**：ChatGPT、Claude、Gemini、开源模型等使用体验
- **AI 编程工具**：Cursor、Copilot、Windsurf 等 AI 辅助编程
- **Fine-tuning**：模型微调、LoRA、数据准备
- **AI 基础理论**：机器学习、深度学习、Transformer、注意力机制
- **多模态**：图像生成、语音识别、视频理解
- **AI 安全与对齐**：安全性、对齐问题、伦理
- **生产部署**：模型推理优化、API 集成、成本控制
- **AI 产品与设计**：AI 产品思维、用户体验、商业化

### 索引更新

每次新增记录后，在 `records/index.md` 的记录表格中追加一行：

```
| YYYY-MM-DD | [主题] | [领域] | [标签] | [一句话摘要] |
```

---

## 功能二：历史回溯

### 触发场景

- "回顾一下我的学习记录"
- "我之前学过什么"
- "上个月我都学了啥"
- "关于 RAG 我之前记录过什么"

### 交互流程

1. 读取 `records/index.md` 获取全局视图
2. 根据用户需求进行筛选：
   - **按时间**：读取对应月份目录下的文件
   - **按领域**：从索引中筛选领域匹配的记录
   - **按标签/关键词**：搜索匹配的记录
3. 呈现学习时间线：以清晰的列表或表格形式展示匹配的记录概要
4. 按需深入：如果用户想看某条记录的细节，读取并展示完整内容

### 输出格式

```
📚 你的 AI 学习历程

期间：YYYY-MM 至 YYYY-MM
共 N 条记录，覆盖 X 个领域

| 日期 | 主题 | 领域 | 关键收获 |
|------|------|------|----------|
| ...  | ...  | ...  | ...      |

最活跃领域：[领域名] (N 条记录)
最近关注：[最近几条记录的主题]
```

---

## 功能三：学习指导

### 触发场景

- "这个怎么用比较好？"（在记录某个技术后追问）
- "有什么最佳实践吗？"
- "给我一些进阶建议"
- 用户记录中"遇到的问题"部分有未解决的疑问

### 交互流程

1. 基于用户刚才记录的内容，或读取指定的历史记录
2. 针对具体技术/工具给出：
   - **使用建议**：最佳实践、常见模式、效率技巧
   - **避坑指南**：常见误区、性能陷阱、安全注意事项
   - **进阶方向**：当前知识点的延伸学习方向
3. 如果用户记录中提到了问题，主动给出解决思路
4. 指导内容直接在对话中呈现，不单独存储为文件（除非用户要求保存）

---

## 功能四：学习规划

### 触发场景

- "根据我的记录，下一步学什么好？"
- "帮我制定一个学习计划"
- "我接下来应该深入哪个方向？"

### 交互流程

1. 读取 `records/index.md` 和近期记录，分析用户已掌握的知识
2. 参照下方"AI 知识领域图谱"，定位用户当前所处阶段
3. 识别知识薄弱环节和自然的下一步方向
4. 生成个性化学习规划
5. 将规划保存到 `records/plans/YYYY-MM-DD-规划主题.md`

### 规划模板

```markdown
# AI 学习规划

- **生成日期**: YYYY-MM-DD
- **用户当前阶段**: [基于已有记录的评估]
- **推荐路线**: [应用者 / 开发者 / 产品运营]

## 已掌握的知识领域

[从历史记录中提取，标注掌握程度]

## 阶段一：[主题]（预计 X 周）

### 学习目标
[具体、可衡量的目标]

### 推荐资源
[课程/文档/项目，标注难度和预计时长]

### 实战项目
[一个可动手做的小项目]

### 学习方法建议
[针对该阶段的具体学习方法]

## 阶段二：[主题]（预计 X 周）
...

## 长期方向建议
[3-6 个月的大方向展望]
```

---

## 功能五：知识总结

### 触发场景

- "总结一下我这个月的学习"
- "生成一份学习报告"
- "回顾一下我的 AI 知识体系"

### 交互流程

1. 读取指定时间段的所有记录（默认为最近一个月）
2. 分析学习模式：频率、领域分布、深度变化
3. 提取核心收获和知识关联
4. 生成结构化总结报告
5. 保存到 `records/summaries/YYYY-MM-总结主题.md`

### 总结模板

```markdown
# AI 学习总结

- **期间**: YYYY-MM-DD 至 YYYY-MM-DD
- **记录数**: N 条
- **覆盖领域**: [领域列表]

## 学习概览

[时间分布、频率分析、领域占比]

## 核心收获

[提炼最重要的 3-5 个知识点或心得]

## 知识图谱进展

[用户在 AI 知识体系中的覆盖情况和成长路径]

## 待深入领域

[识别出的知识缺口和建议补强的方向]

## 下一步建议

[基于总结给出的短期学习建议]
```

---

## 功能六：主动学习咨询

### 触发场景

用户主动询问 AI 学习方向，不依赖已有记录即可使用：
- "我想学 AI，从哪里开始？"
- "怎么系统学习 AI？"
- "AI 学习路线推荐"
- "零基础能学 AI 吗？"
- "学 AI 有什么好方法？"
- "想转行做 AI，怎么入手？"

### 交互流程

1. **了解用户背景**（简短对话，2-3 个问题即可）：
   - 技术基础：有无编程经验？熟悉哪些语言？数学基础如何？
   - 学习目标：兴趣探索 / 工作提效 / 职业转型 / 做 AI 产品？
   - 可投入时间：每周大约几小时？
2. **推荐匹配的学习路线**（从下方三条路线中选取）
3. **输出结构化学习规划**（用规划模板）
4. **给出具体学习方法建议**
5. **如果用户有历史记录**，读取后标注已掌握的部分，避免重复推荐

### 三条学习路线

#### 路线 A：AI 应用者（非技术背景或想快速上手）

适合人群：产品经理、运营、设计师、学生、非技术岗位希望用 AI 提效的人。

```
第一阶段：AI 认知与基础工具（2-3 周）
├── 理解 AI/LLM 的基本原理（不需要数学，概念层面）
├── 熟练使用 ChatGPT / Claude 等对话式 AI
├── 学会基本的 Prompt 编写技巧
└── 实战：用 AI 完成一个实际工作任务

第二阶段：Prompt Engineering 进阶（3-4 周）
├── 系统学习 Prompt 设计模式（角色设定、Few-shot、CoT 等）
├── 学会构建复杂的 Prompt 工作流
├── 了解不同模型的特点与适用场景
└── 实战：设计一套解决特定工作场景的 Prompt 模板

第三阶段：AI 工具生态（3-4 周）
├── AI 编程工具：Cursor / Copilot（即使非程序员也能用）
├── AI 图像工具：Midjourney / DALL-E / Stable Diffusion
├── AI 写作与文档工具
├── AI 自动化工具：Zapier AI / Make
└── 实战：搭建一个 AI 辅助的个人工作流

第四阶段：Agent 与高级应用（4-6 周）
├── 理解 AI Agent 的概念与架构
├── 学习 MCP（Model Context Protocol）
├── 了解 RAG 的应用场景（作为用户而非开发者）
├── 探索 AI 在行业中的落地案例
└── 实战：设计或搭建一个 AI Agent 工作流
```

#### 路线 B：AI 开发者（有编程基础）

适合人群：软件工程师、数据分析师、有 Python 基础的技术人员。

```
第一阶段：AI/ML 基础（4-6 周）
├── Python 数据科学栈（NumPy, Pandas, Matplotlib）
├── 机器学习基础概念（监督/无监督/强化学习）
├── 经典 ML 算法实践（sklearn）
├── 深度学习入门（神经网络、反向传播）
└── 实战：完成一个 ML 分类或回归项目

第二阶段：NLP 与 LLM（4-6 周）
├── NLP 基础（文本处理、词向量、序列模型）
├── Transformer 架构原理
├── LLM 的工作原理（预训练、RLHF、推理）
├── API 调用实践（OpenAI API / Anthropic API）
├── Prompt Engineering（开发者视角）
└── 实战：构建一个基于 LLM API 的应用

第三阶段：RAG 与 Agent 开发（4-6 周）
├── Embedding 与向量数据库（Pinecone / Chroma / FAISS）
├── RAG 架构设计与优化
├── Function Calling / Tool Use
├── Agent 框架（LangChain / LlamaIndex / CrewAI）
├── MCP 协议开发
└── 实战：构建一个 RAG 应用或 AI Agent

第四阶段：微调与部署（6-8 周）
├── Fine-tuning 方法论（LoRA / QLoRA / Full Fine-tuning）
├── 训练数据准备与清洗
├── 模型评估与基准测试
├── 推理优化（量化、蒸馏）
├── 生产部署（API 服务化、成本优化）
└── 实战：微调一个模型并部署上线
```

#### 路线 C：AI 产品与运营

适合人群：产品经理、项目经理、创业者、运营人员。

```
第一阶段：AI 产品认知（2-3 周）
├── AI 技术全景图（能做什么、不能做什么）
├── AI 产品形态与商业模式
├── 体验主流 AI 产品，建立产品感
└── 实战：分析 3 个 AI 产品的核心竞争力

第二阶段：AI 产品设计（3-4 周）
├── AI-Native 产品设计思维
├── 用户需求与 AI 能力的匹配
├── Prompt 策略设计（产品视角）
├── AI 产品的用户体验设计
└── 实战：设计一个 AI 产品的 PRD

第三阶段：AI 产品实战（4-6 周）
├── 使用 no-code/low-code 搭建 AI 原型
├── AI 产品的数据指标体系
├── 用户反馈与模型迭代
├── AI 内容运营策略
└── 实战：搭建一个 AI 产品原型并做用户测试

第四阶段：AI 战略与商业化（4-6 周）
├── AI 行业趋势分析
├── AI 产品的成本与 ROI 分析
├── AI 合规与伦理
├── 团队 AI 能力建设
└── 实战：撰写一份 AI 产品商业化方案
```

### 具体学习方法建议

根据用户情况，从以下方法中选取适合的推荐：

1. **项目驱动学习法**：不要只看教程，每个阶段都动手做一个小项目。哪怕很简单、很粗糙，做过一遍比看十遍教程更有效。如果没有项目灵感，从解决自己工作/生活中的实际问题出发。

2. **费曼学习法**：学完一个知识点后，用自己的话写下来（正好利用本 skill 的结构化记录功能）。如果写不清楚，说明还没真正理解，回去再学。这些记录日积月累就是你的个人知识库。

3. **对比学习法**：学习 AI 工具和模型时，用同一个任务测试不同工具/模型，记录结果差异（利用本 skill 的记录功能）。理解各工具的长短板比死记参数更重要。

4. **间隔复习**：每周花 15 分钟用本 skill 的"历史回溯"功能回顾最近的学习记录。隔一段时间再看自己之前的笔记，会有新的理解。

5. **社区融入法**：参与 AI 相关社区讨论（GitHub、Twitter/X、Reddit r/LocalLLaMA、知乎 AI 话题、各种 Discord 社群）。看别人怎么用 AI，获取灵感，同时在社区输出也能倒逼学习。

6. **碎片化学习 + 系统整理**：日常碎片时间可以看文章、刷视频、试工具，但每周抽出一块完整时间做系统整理（利用本 skill 的"知识总结"功能）。碎片化获取信息，系统化构建知识。

---

## AI 知识领域图谱

用于学习规划时定位用户当前阶段和推荐下一步方向。每个节点标注前置依赖和难度。

```
AI 知识体系
│
├── 🟢 基础认知层（入门，无前置要求）
│   ├── AI/ML 基本概念
│   ├── LLM 工作原理（概念层面）
│   └── AI 产品形态认知
│
├── 🟡 应用实践层（入门→进阶）
│   ├── Prompt Engineering ← 基础认知
│   ├── AI 工具使用（ChatGPT/Claude/Cursor 等）← 基础认知
│   ├── AI 图像/音频/视频工具 ← 基础认知
│   └── AI 辅助工作流搭建 ← Prompt Engineering + 工具使用
│
├── 🟠 技术开发层（进阶，需编程基础）
│   ├── Python 数据科学 ← 编程基础
│   ├── ML/DL 算法实践 ← Python 数据科学 + 数学基础
│   ├── NLP 基础 ← ML/DL 基础
│   ├── LLM API 开发 ← 编程基础 + Prompt Engineering
│   ├── RAG 系统开发 ← LLM API + 向量数据库
│   ├── Agent 开发 ← LLM API + Tool Use
│   ├── MCP 开发 ← Agent 开发
│   └── Fine-tuning ← ML/DL 基础 + LLM 原理
│
├── 🔴 高阶专业层（高阶）
│   ├── 模型架构设计 ← 深度学习
│   ├── 训练优化 ← Fine-tuning + 算法基础
│   ├── 推理优化与部署 ← 模型原理 + 工程能力
│   ├── 多模态系统 ← NLP + CV 基础
│   └── AI 安全与对齐 ← LLM 原理
│
└── 💼 产品商业层（进阶，无技术前置要求）
    ├── AI 产品设计 ← 基础认知 + 产品思维
    ├── AI 商业化 ← AI 产品设计
    └── AI 团队能力建设 ← AI 产品经验
```

---

## 使用语言 / Language

本 skill 完整支持中文和英文双语交互。

**语言自动适配原则：**
- 始终使用与用户相同的语言进行交互。用户说中文就全程用中文，用户说英文就全程用英文
- 记录文件的标题、正文内容跟随用户的输入语言
- 文件名使用用户语言的关键词（中文用拼音或中文，英文用英文），但目录结构中的固定部分（`records/`, `plans/`, `summaries/`）保持英文
- 记录模板的字段标签也跟随语言切换，例如：
  - 中文模板：`日期`、`领域`、`标签`、`学习内容`、`关键发现与心得`
  - English template: `Date`, `Domain`, `Tags`, `What I Learned`, `Key Insights`
- `index.md` 的表头保持双语兼容：`日期/Date | 主题/Topic | 领域/Domain | 标签/Tags | 摘要/Summary`

**English record template:**

```markdown
# Learning Note: [Topic]

- **Date**: YYYY-MM-DD
- **Domain**: [see domain categories]
- **Tags**: [keyword1, keyword2, ...]
- **Level**: [Beginner / Intermediate / Advanced]

## What I Learned

[Core concepts and key points]

## Use Case / Context

[Where and how this was applied or discovered]

## Key Insights

[Personal reflections, comparisons, best practices]

## Challenges & Questions

[Difficulties encountered, unresolved questions]

## References

[Links, docs, tutorials, papers]
```

**English learning plan template:**

```markdown
# AI Learning Plan

- **Generated**: YYYY-MM-DD
- **Current Level**: [assessment based on history]
- **Recommended Track**: [Practitioner / Developer / Product & Strategy]

## Knowledge Already Covered

[Extracted from history, with proficiency notes]

## Phase 1: [Topic] (Est. X weeks)

### Learning Goals
### Recommended Resources
### Hands-on Project
### Study Tips

## Phase 2: ...

## Long-term Direction
```

**English summary template:**

```markdown
# AI Learning Summary

- **Period**: YYYY-MM-DD to YYYY-MM-DD
- **Records**: N entries
- **Domains Covered**: [list]

## Overview
## Key Takeaways
## Knowledge Map Progress
## Gaps to Fill
## Next Steps
```

## 交互原则

1. **低门槛**：用户随口说一句也能帮助记录，不要把交互搞成问卷调查
2. **高价值**：每次交互结束后，用户应该获得结构化的记录文件或有用的指导建议
3. **有连续性**：主动关联历史记录，帮用户看到自己的学习脉络和成长
4. **重实践**：给建议时优先推荐"动手做"而非"被动学"
5. **不啰嗦**：掌握好信息密度，关键信息讲透，次要信息点到为止
