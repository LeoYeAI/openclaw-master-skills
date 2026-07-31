---
name: claw-multi-agent
description: "Multi-agent parallel orchestration for OpenClaw. Spawn AI agents as a team — parallel research, multi-model comparison, code pipelines. Proven 50-65% time savings. Trigger words: multi-agent, parallel agents, swarm, spawn multiple agents, parallel research, compare models, deep research, comprehensive research, detailed investigation, thorough analysis, research multiple topics, 多智能体, 多个Agent, 并行调研, 并行搜索, 同时搜索, 同时调研, 深度调研, 详细调研, 全面调研, 深度研究, 详细检索, 多角度分析, 全面分析, 多个模型, 让多个AI, 分别搜索, 同时搜索, 组建团队, Agent小队, 多Agent."
---

# claw-multi-agent 🐝

> **Replace one AI with a team of AIs. Turn serial into parallel. Turn hours into minutes.**

---

## What can it do?

| Scenario | Example | Speedup |
|----------|---------|---------|
| **Parallel research** | Search 5 frameworks simultaneously, each writes a report | ~65% ⚡ |
| **Multi-model compare** | Ask Claude, Gemini, Kimi the same question at the same time | ~50% ⚡ |
| **Code pipeline** | Plan → Code → Review, auto hand-off in sequence | Quality ↑ |
| **Batch processing** | Translate / analyze / summarize multiple docs in parallel | Scales linearly |

---

## ⚡ Get started in 30 seconds

Just say something like:

- "Research LangChain, CrewAI, and AutoGen in parallel"
- "Have multiple agents search these topics and write a combined report"
- "Compare how Claude and Gemini answer this question"
- "Use multi-agent mode to do this research"

---

## 🎭 Interaction Style — How to Talk to the User

This is the recommended pattern. Every multi-agent run must follow this interaction pattern.

### Step 0 — Announce skill activation FIRST

**⚠️ Iron rule: The activation announcement must be your FIRST reply after receiving the task — before reading any files, before investigating, before spawning.**

**Why this matters**: Reading files, researching background, and spawning all take time. If you do those first, users see long silence. Worse: context compression can happen during that time, and the announcement will never be sent.

**Correct order**: Receive task → Send announcement immediately → Then read files / spawn / wait

The very first thing to say when this skill is triggered — before any planning or spawning:

```
🐝 **claw-multi-agent 已唤醒**
多智能体并行模式启动，我来组建 Agent 小队处理这个任务。
```

This tells the user the skill is active and sets expectations for what's about to happen.

### Before spawning — announce the plan

Right after the activation announcement, present the plan BEFORE calling sessions_spawn:

```
🚀 [N]个方向同时开搞，全面覆盖你的问题。

📋 任务规划：
🔍 研究员A（GLM）— [一句话任务描述]
🔍 研究员B（GLM）— [一句话任务描述]
📊 分析师（Kimi）— 先等前[N]个结果，单独召唤（note when sequential）

模式：🎯 指挥官模式（联网搜索）
预计耗时：~[X]s（[N] Agent 并行[，分析师串行跟进]）
正在派出 Agent 小队...
```

**Role emoji reference:**
| Role | Emoji | Example |
|------|-------|---------|
| Researcher | 🔍 | 🔍 研究员A（GLM）— Research XX |
| Analyst | 📊 | 📊 分析师（Kimi）— Deep comparison |
| Writer | ✍️ | ✍️ 写作者（Gemini）— Draft the report |
| Coder | 💻 | 💻 程序员（Kimi）— Implement the logic |
| Reviewer | 🔎 | 🔎 审核员（GLM）— Quality check |
| Planner | 📋 | 📋 规划师（Sonnet）— Break down tasks |

**Key rules:**
- ✅ Always list each agent with: emoji + role + **model name** + one-line task
- ✅ State the mode (指挥官/流水线/混合) and estimated time
- ✅ End announcement with: `正在派出 Agent 小队...`
- ✅ Note sequential agents as: "先等前N个结果，单独召唤"
- ❌ Never silently call sessions_spawn without announcing

### While waiting — brief note

After spawning, say one line:
```
⏳ 子 Agent 已全部出发，等结果回来...
```

### After results — structured output (not raw dump)

**Never paste sub-agent raw output directly.** Always digest and restructure by content logic — NOT by agent order.

**Recommended output order:**

```
1. 执行统计卡 ← 先让用户知道跑了什么
2. 核心结论（3-5条最重要发现）← 最有价值的放最前面
3. 分主题展开细节（按内容逻辑组织，不按子Agent顺序）← 读起来是一篇完整文章
4. 下一步行动建议 ← 落地结尾
```

**统计卡格式：**
```
## 📊 执行统计
| Agent | 模型 | 耗时 | 状态 |
|-------|------|------|------|
| 🔍 研究员A | GLM | 58s | ✅ |
| 🔍 研究员B | GLM | 62s | ✅ |
| 📊 分析师  | Kimi | 45s | ✅ |
串行需要约 165s → 并行实际 62s，节省 **62%** ⚡
```

**❌ Wrong — agent order:**
```
子Agent1的结果...
子Agent2的结果...
子Agent3的结果...  ← 读者要自己拼图，体验差
```

**✅ Right — content logic:**
```
## 核心结论
1. 最重要发现A（来自多个Agent综合）
2. 最重要发现B
...

## 详细分析：[主题1]
...（整合所有相关Agent的内容）

## 详细分析：[主题2]
...

## 下一步建议
...
```

**The main agent rewrites everything in its own words.** Sub-agent outputs are raw material, not the final answer.

### After results — deliver the report (channel-aware)

**Always save to file first. Then deliver based on the current channel.**

```python
# Step 1: Always save to file first
write("/workspace/projects/{topic-slug}/report.md", content)
```

**Then choose delivery method by channel:**

| Channel | Delivery method |
|---------|----------------|
| **feishu** + has `feishu-all-operations` skill | Create Feishu doc → send link (best UX) |
| **feishu** + no Feishu skill | `message(filePath=..., filename="report.md")` — send as attachment |
| **Discord / Telegram / Slack** | `message(message=...)` — Markdown renders normally |
| **Other / unknown** | Save file + tell the user the path |

**Why this matters:** Feishu chat does NOT render Markdown. Sending raw Markdown text shows `##`, `|---|` symbols. Always use attachment or doc link on Feishu.

```python
# Feishu (no Feishu doc skill): send as attachment
message(action="send", filePath="/workspace/projects/{topic-slug}/report.md", filename="report.md")

# Discord/Telegram: send markdown directly
message(action="send", message=report_content)
```

**End with one line:**
```
需要调整某个方向，或推送到飞书文档吗？
```

**Rules:**
- ✅ Always save `.md` file first — regardless of channel
- ✅ Check current channel before deciding how to send
- ❌ Never paste >300 words of Markdown text on Feishu — it won't render
- ❌ Never just say "报告已保存至 /path/xxx" — user can't open server paths
- ❌ Never ask "要不要我帮你整理成文档？" — just do it

### Sequential vs parallel — analyst must wait for researchers

**Critical:** Agents spawned in the same round run in parallel and share NO context with each other.

```
❌ Wrong: spawn researcher-A + researcher-B + analyst all at once
          → analyst has no data, returns empty

✅ Right: 
  Round 1: spawn researcher-A + researcher-B (parallel, independent)
  Wait for both to return...
  Round 2: main agent consolidates research results
           → then either: main agent writes analysis itself
           → or: spawn analyst with research results injected as context
```

**Best practice: Any agent that depends on another agent's output should be spawned in a later round, after collecting the dependency.**

---

## 🤖 Model Selection Guide — Which Model for Which Role

Always pick the right model for each agent. State the model explicitly in the announcement.

### Model roster

| 模型 | 别名 | 特点 | 适合角色 |
|------|------|------|---------|
| `glm` | GLM | 便宜、速度快、中文好 | 搜索、简单调研、状态检查 |
| `kimi` | Kimi | 长上下文（128k）、代码强 | 深度分析、代码、长文整合 |
| `gemini` | Gemini | 创意好、多模态 | 写作、文案、图像理解 |
| `sonnet` | Claude Sonnet | 均衡、工具调用稳 | 复杂推理、规划、审核 |
| `opus` | Claude Opus | 最强推理 | 极复杂分析、架构设计 |

### Role → Model mapping (default)

| 角色 | 默认模型 | 原因 |
|------|---------|------|
| 🔍 研究员 / Researcher | **GLM** | 轻量搜索，够用且便宜 |
| 📊 分析师 / Analyst | **Kimi** | 长上下文，处理大量资料 |
| ✍️ 写作者 / Writer | **Gemini** | 创意写作效果最好 |
| 💻 程序员 / Coder | **Kimi** | 长上下文代码理解 |
| 🔎 审核员 / Reviewer | **GLM** | 简单判断，不需重炮 |
| 📋 规划师 / Planner | **Sonnet** | 结构化规划能力强 |
| 🧐 批评者 / Critic | **Sonnet** | 逻辑严谨，挑战假设 |

### When to override defaults

- 任务很简单 → 降级到 GLM（省成本）
- 需要最高质量 → 升级到 Opus
- 用户明确指定模型 → 照用户说的来
- 多模型对比场景 → 每个 Agent 用不同模型，在公告里说明

### Always announce the model

In the pre-spawn announcement, every agent line must include the model:
```
✅ 这样：🔍 研究员A（GLM）— 调研 LangChain
❌ 这样：🔍 研究员A — 调研 LangChain
```

---

## Step 0: Always plan first (dynamic agent count)

**Never hardcode how many agents to spawn.** The right number depends on the task complexity. Always start with a planning step:

```
1. Analyze the task → identify subtopics / dimensions
2. Decide: how many agents? which roles? which mode?
3. Spawn accordingly (could be 2, could be 10)
4. Consolidate results
```

**Example planning output:**
```
Task: "Research the top AI agent frameworks"
→ Plan: 5 researchers (one per framework) + 1 analyst for comparison
→ Mode: Orchestrator (needs web search)
→ Spawn: 5 parallel sub-agents
```

**The number of agents should match the task, not a template.**

---

## Three modes — auto-routed by intent

**You don't need to say which mode.** Just describe the task. The skill reads these two signals:

1. **Need web search / real-time info?** → use sessions_spawn (has tools)
2. **Want multiple draft versions to compare?** → spawn parallel writers

```
User says anything
        ↓
  Wants multiple versions / drafts / angles?
        YES ──→ Also needs web search?
        │              YES → 🔀 Hybrid Mode   (search first, then N drafts)
        │              NO  → 🔄 Pipeline Mode (N drafts in parallel, pure text)
        │
        NO  ──→ Needs web search / file ops?
                       YES → 🎯 Orchestrator Mode (sessions_spawn, parallel)
                       NO  → 🔄 Pipeline Mode     (pure text, faster)
```

**Trigger signals the skill listens for:**

| Signal | Examples | Mode triggered |
|--------|---------|---------------|
| Multi-draft intent | "几个版本", "多个角度", "让我挑", "各自写", "different styles" | Pipeline or Hybrid |
| Search intent | "搜索", "最新", "调研", "联网", "search", "latest" | Orchestrator or Hybrid |
| Both | "搜索后给我几版报告", "research then write multiple drafts" | **Hybrid** |
| Neither | "翻译", "分析", "写作", plain text tasks | Pipeline |

You can also check with the router directly:
```bash
python scripts/router.py mode "搜索竞品资料，帮我写3个版本的分析"
# → 🔀 HYBRID
python scripts/router.py mode "调研LangChain并写一份报告"
# → 🎯 ORCHESTRATOR
python scripts/router.py mode "用三个角度分析这个方案"
# → 🔄 PIPELINE
```

---

## 🎯 Orchestrator Mode (with tools, truly parallel)

Sub-agents launched via `sessions_spawn`. Each has full OpenClaw tools: web search, file read/write, code execution.

**⚡ How parallelism works:**
Call multiple `sessions_spawn` in the **same tool-call round** — OpenClaw executes them simultaneously. All sub-agents run at once; the main agent collects all results when they finish.

```
Same round → parallel execution:

sessions_spawn(task="Search LangChain...") ──┐
sessions_spawn(task="Search CrewAI...")    ──┤→ all run simultaneously
sessions_spawn(task="Search AutoGen...")   ──┘
sessions_spawn(task="Search LangGraph...") ─┘

↓  (all finish, main agent receives all 4 results)

Main agent consolidates → writes full report
```

**Sequential = spawn one, wait for result, then spawn next.** Use this only when a later task depends on an earlier result (e.g. write report AFTER research is done).

**How to spawn — always include role, model hint, and what to return:**

```python
# Parallel research: spawn all 4 in the same round → they run simultaneously
sessions_spawn({
    "task": "[CONTEXT] Comparing AI agent frameworks for a tech team report.\n\n[YOUR TASK] Search LangChain: architecture, pros/cons, GitHub stars, latest version. Return 5 bullet points ≤100 words each. Do NOT write a full report.",
    "label": "🔍 researcher-langchain [model: default]"
})
sessions_spawn({
    "task": "[CONTEXT] Same report.\n\n[YOUR TASK] Search CrewAI: architecture, pros/cons, GitHub stars, latest version. Return 5 bullet points ≤100 words each.",
    "label": "🔍 researcher-crewai [model: default]"
})
sessions_spawn({
    "task": "[CONTEXT] Same report.\n\n[YOUR TASK] Search AutoGen: architecture, pros/cons, GitHub stars, latest version. Return 5 bullet points ≤100 words each.",
    "label": "🔍 researcher-autogen [model: default]"
})
sessions_spawn({
    "task": "[CONTEXT] Same report.\n\n[YOUR TASK] Search LangGraph: architecture, pros/cons, GitHub stars, latest version. Return 5 bullet points ≤100 words each.",
    "label": "🔍 researcher-langgraph [model: default]"
})
# All 4 run in parallel → when all return, main agent consolidates and writes report
```

**Mixed: parallel then sequential** (most common pattern):
```python
# Phase 1: parallel research (spawn all at once)
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search LangChain. 5 bullets ≤100 words.", "label": "🔍 researcher-langchain"})
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search CrewAI. 5 bullets ≤100 words.", "label": "🔍 researcher-crewai"})
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search AutoGen. 5 bullets ≤100 words.", "label": "🔍 researcher-autogen"})

# Phase 2: after all 3 return → main agent writes report (sequential, depends on research)
# (main agent does this directly, no need to spawn a writer)
```

**Key rules:**
- ✅ **Same round = parallel**: spawn multiple agents at once for independent tasks
- ✅ **Sequential**: spawn one, wait for result, then spawn next — only when tasks depend on each other
- ✅ Sub-agents return **summaries only** (≤100 words per point)
- ✅ Main agent **writes the full report** (avoids token limit failures)
- ✅ Label each agent clearly: role + what model it's using
- ❌ Don't ask a sub-agent to both search AND write a long report

---

## 🔄 Pipeline Mode (pure text, any task)

Runs agents via Python CLI. **No web search, but works for any pure-text task**: writing, analysis, translation, multi-model comparison, brainstorming, code generation.

```bash
cd ~/.openclaw/skills/claw-multi-agent

# Parallel: multiple agents tackle different angles simultaneously
python run.py --mode parallel \
  --agents "fast:🔍 researcher:summarize the pros of microservice architecture" \
           "fast:🔍 researcher:summarize the cons of microservice architecture" \
           "fast:🔍 researcher:list real-world companies using microservices and outcomes" \
           "smart:📊 analyst:compare microservices vs monolith for a 10-person startup" \
  --aggregation synthesize

# Sequential: chain agents, each builds on the previous output
python run.py --mode sequential \
  --agents "fast:📋 planner:break down how to build a REST API in Python" \
           "smart:💻 coder:implement the API based on the plan above" \
           "fast:🔎 reviewer:review the code for bugs and security issues" \
  --aggregation last

# Auto-route: router classifies task and picks tiers automatically
python run.py --auto-route --task "write a technical blog post about GRPO vs PPO"

# Dry-run: preview the plan without executing
python run.py --dry-run \
  --agents "fast:researcher:research X" "smart:writer:write report"
```

**Pipeline mode works great for:**
- Multi-angle analysis (spawn one agent per dimension)
- Multi-model comparison (same task, different models)
- Code pipeline (plan → code → review)
- Batch writing (translate/summarize N documents in parallel)

---

## 🔀 Hybrid Mode (search + multi-draft)

Best of both worlds: sub-agents search the web (with tools), then multiple writers generate parallel drafts from the research.

**When it kicks in:** user wants both real-time research AND multiple versions to compare.

```
Phase 1 (Orchestrator — with tools, parallel):
  sessions_spawn(search topic A) ──┐
  sessions_spawn(search topic B) ──┤ → all run simultaneously
  sessions_spawn(search topic C) ──┘
  ↓ research summaries collected

Phase 2 (Pipeline — pure text, parallel):
  openclaw agent (writer style 1) ──┐
  openclaw agent (writer style 2) ──┤ → all run simultaneously
  openclaw agent (writer style 3) ──┘
  ↓ 3 draft versions returned

Main agent: compare drafts → pick best or synthesize
```

**CLI usage:**
```bash
# Auto: router detects hybrid intent and runs both phases
python run.py --mode hybrid --task "调研主流AI框架，给我3个不同风格的对比报告" --num-drafts 3

# Auto-mode: let router decide the mode automatically
python run.py --auto-mode --task "搜索竞品资料后写几个版本的分析"
```

**In conversation (sessions_spawn approach):**
```python
# Phase 1: parallel research (spawn all at once)
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search LangChain. 5 bullets.", "label": "🔍 research-langchain"})
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search CrewAI. 5 bullets.", "label": "🔍 research-crewai"})
sessions_spawn({"task": "[CONTEXT] ...\n\n[TASK] Search AutoGen. 5 bullets.", "label": "🔍 research-autogen"})

# After all 3 return → Phase 2: main agent writes 3 draft versions itself
# (or spawn 3 pipeline agents with research as context)
```

---

## Smart Router

Built-in task classifier. Auto-picks the right tier based on keywords:

```bash
python scripts/router.py classify "write a Python web scraper"
# → Tier: CODE  (routes to smart model)

python scripts/router.py classify "research the latest LLM papers"
# → Tier: RESEARCH  (routes to fast model)

python scripts/router.py spawn --json --multi "research X and write a report"
# → splits into 2 tasks: RESEARCH + CREATIVE
```

| Tier | Model | Used for |
|------|-------|---------|
| `FAST` | default (light) | Simple queries, status, translation, search |
| `CODE` | default (smart) | Programming, debugging, implementation |
| `RESEARCH` | default (light) | Research, search, compare, survey |
| `CREATIVE` | default (smart) | Writing, articles, documentation |
| `REASONING` | default (best) | Architecture, logic, complex analysis |

---

## contextSharing: Give sub-agents background

Sub-agents start as fresh sessions — they don't know your goal. Add a `[CONTEXT]` block.

**Pattern 1: recent** (recommended — works for 95% of cases)
```
[CONTEXT] User is comparing AI agent frameworks for a team report. Audience: engineers.

[YOUR TASK] Search LangChain pros and cons. Return 5 bullet points ≤100 words each.
```

**Pattern 2: summary** (sequential tasks — pass prior results forward)
```
[PRIOR FINDINGS]
- LangChain: richest ecosystem, steep curve
- CrewAI: clean role separation...

[YOUR TASK] Based on above, search AutoGen. Return 3 unique points not covered above.
```

**Pattern 3: full** (complex background — let agent read a file)
```
[CONTEXT FILE] Read /workspace/research/context.md for full background.

[YOUR TASK] Search latest Test-Time Compute Scaling advances. Return 3 summaries.
```

**Reuse context across parallel agents:**
```python
BG = "Researching RL post-training for ML engineers. Topics: GRPO/DAPO/PPO, veRL."

sessions_spawn({"task": f"[CONTEXT] {BG}\n\n[TASK] Search GRPO vs PPO benchmarks. 5 bullets ≤100 words.", "label": "🔍 researcher-grpo [model: default]"})
sessions_spawn({"task": f"[CONTEXT] {BG}\n\n[TASK] Search DAPO design. 5 bullets ≤100 words.", "label": "🔍 researcher-dapo [model: default]"})
sessions_spawn({"task": f"[CONTEXT] {BG}\n\n[TASK] Search veRL architecture. 5 bullets ≤100 words.", "label": "🔍 researcher-verl [model: default]"})
```

---

## Execution summary — always output this

After every multi-agent run, print a standard card:

```
## 📊 Execution Summary

Mode: 🎯 Orchestrator Mode (sessions_spawn, with tools)

| Agent | Role | Model | Time | Status |
|-------|------|-------|------|--------|
| 🔍 researcher-langchain | Researcher | default | 22s | ✅ |
| 🔍 researcher-crewai    | Researcher | default | 19s | ✅ |
| 🔍 researcher-autogen   | Researcher | default | 24s | ✅ |
| 🔍 researcher-langgraph | Researcher | default | 21s | ✅ |
| ✍️ main (consolidate)   | Writer     | default | 38s | ✅ |

Agents spawned: 4  |  Parallel time: ~24s  |  Serial equivalent: ~86s  |  Saved: ~62s (72%)
```

**Always include:**
- Mode (Orchestrator / Pipeline + Sequential/Parallel)
- Each agent's role emoji + name + model used
- Actual elapsed time per agent
- Total parallel time vs serial equivalent

---

## Preset roles

| Role | Emoji | Best for |
|------|-------|---------|
| `researcher` | 🔍 | Web search, info gathering |
| `writer` | ✍️ | Reports, documentation, articles |
| `coder` | 💻 | Code writing, debugging, implementation |
| `analyst` | 📊 | Data analysis, comparison, statistics |
| `reviewer` | 🔎 | Code / content review, QA |
| `planner` | 📋 | Task planning, decomposition |
| `critic` | 🧐 | Risk analysis, devil's advocate |

---

## ⚠️ Gotchas

### Gotcha 0: Reading files before announcing (most common mistake)
Investigating context before sending the activation announcement causes long silence and risks losing the announcement entirely due to context compression.

- ❌ Receive task → read operators.py → read README → announce → spawn
- ✅ Receive task → **announce immediately** (can say "analyzing task...") → read files → spawn

### Gotcha 1: Sub-agent output token limit
Sub-agents have a ~4096 token output cap. Exceeded → tool args truncated → file writes silently fail.

- ❌ "search AND write a 2000-word report"
- ✅ Sub-agent returns summaries; **main agent writes the report**

### Gotcha 2: Orchestrator Mode has no tools in Pipeline Mode
`python run.py` processes have no `web_search`, `exec`, etc.

- ❌ Pipeline mode: "search the latest news on X"
- ✅ Anything needing real web access → Orchestrator Mode

### Gotcha 3: Parallel agents can't depend on each other
Agents spawned in the same round run simultaneously.

- ❌ Agent-2: "based on Agent-1's results..."
- ✅ Parallel = independent; sequential = chained

### Gotcha 4: Don't hardcode agent count
Match agents to the task, not to a template.

- ❌ Always spawn exactly 3 agents
- ✅ Plan first, then decide: simple task → 2 agents, complex → 8+ agents

---

## Pipeline mode quick reference

```bash
python run.py
  --mode parallel|sequential
  --agents "tier_or_model:🎭role:task description"   # repeatable, any number
  --aggregation synthesize|compare|concatenate|last
  --timeout 300
  --dry-run          # preview without executing
  --auto-route       # router picks tiers automatically
  --list-models      # show current model config
```

| Aggregation | Effect |
|-------------|--------|
| `synthesize` | Main agent summarizes all outputs (default) |
| `compare` | Side-by-side of each agent's output |
| `concatenate` | Outputs joined in order |
| `last` | Final agent's output only (sequential) |
