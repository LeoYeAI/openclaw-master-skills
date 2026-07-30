---
title: "AI News Daily Brief - Category Taxonomy"
---

# Category Taxonomy

This file defines the category system used by the AI News Daily Brief skill.

Its purpose is to ensure that news items are classified consistently across different runs, avoid overlap between categories, and improve the readability of the final daily brief.

Unless the user explicitly requests otherwise, all selected stories should be mapped into one of the categories below.

---

## 1. Primary Categories

The skill uses the following six primary categories:

1. 模型与产品发布
2. Agent与应用落地
3. 企业与商业化动态
4. 基础设施 / 芯片 / 算力
5. 政策 / 监管 / AI安全
6. 研究进展与技术趋势

These categories should be used consistently in:
- Top 5 important news
- Full news list
- trend summaries when relevant

---

## 2. Category Definitions

### 2.1 模型与产品发布
Use this category for:
- foundation model launches
- multimodal model launches
- reasoning model launches
- major model upgrades
- API releases or major API capability changes
- product launches directly centered on AI capability
- major feature releases in AI platforms or assistants

Typical examples:
- OpenAI releases a new model
- Anthropic launches a major Claude upgrade
- Google DeepMind announces a new Gemini-related capability
- a company releases a new AI API or developer platform update

Do not use this category for:
- general business partnerships
- enterprise deployment case studies
- infrastructure-only announcements
- research-only papers without product relevance

Boundary note:
If the core event is “a new model/product/capability is officially launched,” classify it here even if media coverage focuses on business impact.

---

### 2.2 Agent与应用落地
Use this category for:
- AI agent product launches or deployments
- workflow automation tools
- AI office tools and productivity applications
- application-layer AI products
- enterprise or consumer AI usage scenarios
- RAG products, knowledge assistants, copilots, and applied AI systems
- real-world rollout of AI functionality into workflows

Typical examples:
- a company launches an agent workflow product
- an AI office assistant gains new task execution features
- a knowledge-base assistant is deployed in an enterprise workflow
- a vertical AI application enters production use

Do not use this category for:
- general model releases without application context
- chip or compute news
- funding-only stories
- broad research papers with no deployment angle

Boundary note:
If the main value of the story is “AI is being used in a real workflow, scenario, or application,” classify it here.

---

### 2.3 企业与商业化动态
Use this category for:
- funding rounds
- mergers and acquisitions
- strategic partnerships
- major enterprise contracts
- monetization changes
- pricing strategy changes
- market expansion
- organizational changes directly affecting AI business direction
- notable commercial competition moves

Typical examples:
- an AI startup raises funding
- two companies announce an AI strategic partnership
- a company changes pricing for a major AI product
- a major acquisition reshapes AI competition
- an enterprise signs a large AI platform agreement

Do not use this category for:
- official model launches where the launch itself is the main event
- infrastructure news primarily about chips or compute
- policy/regulatory developments
- research-only news

Boundary note:
If the core event is about money, market, partnership, business strategy, or commercialization, classify it here.

---

### 2.4 基础设施 / 芯片 / 算力
Use this category for:
- GPUs and AI chips
- inference systems
- training infrastructure
- compute platforms
- data centers
- networking for AI systems
- hardware-software infrastructure stacks
- deployment efficiency, inference cost, and performance-related announcements
- cloud AI infrastructure with strong compute relevance

Typical examples:
- NVIDIA announces a new inference chip platform
- a cloud provider launches AI compute infrastructure
- a company reports major changes in inference cost or training efficiency
- a data-center expansion tied to AI capacity is announced

Do not use this category for:
- application-layer agent tools
- funding-only news unless infrastructure is the core topic
- policy-only news
- pure research without infrastructure implications

Boundary note:
If the main question is “how AI systems are powered, deployed, accelerated, or scaled,” classify it here.

---

### 2.5 政策 / 监管 / AI安全
Use this category for:
- AI regulation
- government policy
- legal actions related to AI
- copyright disputes
- compliance issues
- AI safety announcements
- governance frameworks
- risk management requirements
- security incidents directly tied to AI systems

Typical examples:
- a regulator releases a new AI rule
- copyright litigation involving model training advances
- an official safety framework is announced
- a government agency issues AI governance guidance
- a major AI misuse or security concern leads to response measures

Do not use this category for:
- general product launches
- business partnerships
- infrastructure releases
- ordinary research news

Boundary note:
If the core of the story is rules, law, governance, safety, or risk control, classify it here.

---

### 2.6 研究进展与技术趋势
Use this category for:
- important AI research papers
- technical breakthroughs
- benchmark or evaluation shifts
- notable open-source technical releases
- new methods with clear future product or industry implications
- emerging technical directions that are not yet formal product launches

Typical examples:
- a breakthrough paper changes expectations around reasoning or multimodality
- a new open-source system shows strong practical performance
- a technical evaluation reveals a meaningful capability shift
- a research lab presents a method likely to influence future AI products

Do not use this category for:
- official product launches already in market use
- general business funding or partnership stories
- hardware-only news unless the story is about technical research rather than product release
- policy-only news

Boundary note:
If the main value is technical significance or directional signal rather than an immediate product/commercial event, classify it here.

---

## 3. Category Selection Rules

Each story should be assigned to one primary category only.

If a story could fit multiple categories, choose the category based on the story’s main center of gravity.

Use this priority logic:

1. What is the main event?
2. What would a reader most likely want to remember this story as?
3. Which category best reflects why the story matters?

Examples:
- A new OpenAI model launch with pricing implications → 模型与产品发布
- An enterprise deploys an agent system built on an existing model → Agent与应用落地
- A startup raises money to scale its AI business → 企业与商业化动态
- NVIDIA launches a new inference platform → 基础设施 / 芯片 / 算力
- A government issues AI compliance rules → 政策 / 监管 / AI安全
- A new paper introduces a breakthrough reasoning approach without product launch → 研究进展与技术趋势

---

## 4. Tie-Breaking Rules

If classification is ambiguous, apply these tie-breakers:

- official launch beats business framing
- real-world application beats general technical discussion
- business strategy beats generic industry commentary
- infrastructure relevance beats broad corporate reporting
- regulation/safety beats media hype framing
- research significance beats minor media interpretation

Practical examples:
- “Company launches model and announces enterprise customers” → 模型与产品发布
- “Company deploys agent internally using third-party model” → Agent与应用落地
- “Company partners with cloud vendor to sell AI service” → 企业与商业化动态
- “Cloud vendor announces AI supercluster” → 基础设施 / 芯片 / 算力

---

## 5. Output Consistency Rules

To keep the daily brief consistent:
1. Do not create temporary custom categories unless the user explicitly asks for them.
2. Do not rename categories casually across different runs.
3. Use the same category labels in both the Top 5 section and the full list.
4. Avoid duplicating a story across categories.
5. If a story does not clearly fit any category, exclude it unless it is highly important.

---

## 6. Optional Future Extensions

If the skill expands later, the taxonomy may optionally add secondary tags such as:
- 开源
- 多模态
- 推理
- 企业服务
- 消费级产品
- 开发者工具
- 合规
- 融资
- 数据中心

These should be used only as secondary tags, not as replacements for the six primary categories unless the taxonomy is explicitly updated.

---

## 7. Summary Principle

The category system exists to improve:
- consistency
- readability
- comparability across daily briefs
- usefulness for product and strategy tracking

Always classify based on the main event and the primary reason the story matters.