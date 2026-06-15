---
name: team-dispatch
description: Use when a request requires multi-agent workflow orchestration (task decomposition + dependency/DAG + parallel execution), needs durable task tracking across context compaction, or needs retries/fallbacks and completion notifications.
metadata:
  openclaw:
    emoji: "🚀"
    i18n:
      default: "en"
      supported: ["en", "zh"]
---

# 🚀 Team Dispatch v1.0.8 — Multi-Agent Workflow Orchestration

**一句需求 → 自动分析 → 智能拆解 → DAG 派发 → 故障重试 → 自动交付。**

---

## ⚡ 第〇步：自动安装与环境检测（必须首先执行）

### 真实项目代码空间（默认）

- 默认真实项目/仓库目录：`~/work`（可通过 `<SKILL_DIR>/config.json` 或 `~/.openclaw/configs/team-dispatch.json` 的 `paths.projectsRoot` 修改）
- 约定：每个项目在 `paths.projectsRoot/<project>` 下创建与产出代码（而不是放在 `~/.openclaw/workspace/`）
- `setup.sh` 会自动创建该目录（若不存在）

> **Agent 读到本文件后，必须先执行以下检测流程，确认系统就绪后再处理用户需求。**
> **新用户首次安装、或已有用户技能更新后，均走此流程。**

### SKILL_DIR 解析

`<SKILL_DIR>` = 本 SKILL.md 文件所在的目录。
Agent 应从自身读取本文件的路径自动推导，例如：
- 若从 `/Users/xxx/skills/team-dispatch/SKILL.md` 读取，则 `SKILL_DIR=/Users/xxx/skills/team-dispatch`
- 若从软连接 `~/.openclaw/skills/team-dispatch/SKILL.md` 读取，用 `readlink` 解析真实路径

### 一键安装

直接运行安装脚本即可完成全部配置：

```bash
bash <SKILL_DIR>/scripts/setup.sh
```

如果遇到模型 404/quota 问题，可追加基线模型参数：

```bash
bash <SKILL_DIR>/scripts/setup.sh --baseline-models
```

### 安装脚本自动完成的 8 项配置

`setup.sh` 会自动检测并配置以下所有项目，已存在的不覆盖：

| # | 配置项 | 说明 |
|---|--------|------|
| 1 | **软连接** | `~/.openclaw/skills/team-dispatch → <SKILL_DIR>` |
| 2 | **任务目录（使用安装用户的主工作区）** | `~/.openclaw/workspace/tasks/{active,done,templates}`（不会创建额外的 main 工作区） |
| 3 | **项目模板** | 复制 `project.json` 到 templates/ |
| 4 | **用户配置** | 生成 `~/.openclaw/configs/team-dispatch.json`（语言、通知策略、团队显示名） |
| 5 | **子 Agent agentDir 模板** | 全新安装：`cp -R <SKILL_DIR>/assets/agents/<id> ~/.openclaw/agents/<id>`（内含 workspace 模板 + 预置文件） |
| 6 | **补齐缺失文件** | 已有 `~/.openclaw/agents/<id>`：仅补齐 `workspace/` 下缺失文件，不覆盖用户改动；并创建 `sessions/` |
| 7 | **写入 openclaw.json** | 在 `agents.list` 中确保存在 `main`（dispatcher/root）并配置 `main.subagents.allowAgents: ["*"]`；同时写入 7 个子 Agent 配置（含 workspace、identity、model），已存在的补齐缺失字段 |
| 8 | **重启 Gateway** | 配置写入后自动重启 Gateway 使生效 |

### 子 Agent 完整配置规范

在 `openclaw.json` 的 `agents.list` 中：**必须存在 main（dispatcher/root）**，并在 main 上配置 `subagents.allowAgents`。

### main agent 配置示例（安装时应确保存在/补齐）

```json
{
  "id": "main",
  "default": true,
  "name": "main",
  "workspace": "/Users/vvusu/.openclaw/workspace",
  "agentDir": "/Users/vvusu/.openclaw/agents/main/agent",
  "model": "openai-codex/gpt-5.4",
  "identity": {
    "name": "调度台",
    "emoji": "🎯"
  },
  "subagents": {
    "allowAgents": ["*"]
  }
}
```

### 子 Agent 配置示例

```json
{
  "id": "<agentId>",
  "name": "<中文名>",
  "workspace": "~/.openclaw/agents/<agentId>/workspace",
  "model": {
    "primary": "<见下方模型选择策略>",
    "fallbacks": ["bailian/qwen3.5-plus", "bailian/kimi-k2.5", "zai/glm-4.7"]
  },
  "tools": { "profile": "<coding|full>" },
  "skills": [],
  "identity": {
    "name": "<中文名>",
    "emoji": "<角色 emoji>",
    "theme": "<英文角色描述>"
  }
}
```

### 模型选择策略

- `coder` → `openai-codex/gpt-5.3-codex`（OAuth，专为编码优化）
- 其他 Agent → `openai-codex/gpt-5.4`（OAuth，通用稳定）
- fallbacks 从用户已配置的 providers 中选取，确保不会 404

### 工具集分配

- `coder`, `tester` → `"coding"`
- `product`, `research`, `trader`, `writer` → `"full"`

### 子 Agent Workspace 结构

每个子 Agent 拥有独立的 **agentDir + workspace + sessions**（符合 OpenClaw 多 Agent 目录规范），互不干扰。

### 全新安装（您指定的逻辑）

```bash
cp -R <SKILL_DIR>/assets/agents/<id> ~/.openclaw/agents/<id>
```

模板目录结构为：

```
<SKILL_DIR>/assets/agents/<id>/
└── workspace/
        ├── AGENTS.md
        ├── SOUL.md
        ├── IDENTITY.md
        ├── USER.md
        ├── TOOLS.md
        ├── HEARTBEAT.md
        ├── BOOTSTRAP.md
        └── .openclaw/workspace-state.json
```

安装后运行时会在以下位置写入会话与状态：

```
~/.openclaw/agents/<id>/sessions/
```

### 已有安装（升级/补齐）

- 若 `~/.openclaw/agents/<id>` 已存在：只补齐 `workspace/` 下缺失文件，不覆盖用户已修改的文件
- `sessions/` 若缺失会自动创建（本技能脚本也会 `mkdir -p`）

> 注：子 Agent 通过 `sessions_spawn` 启动时只注入 `AGENTS.md` + `TOOLS.md`，但完整的 workspace 文件在 Agent 作为独立 agent（而非 subagent）运行时会全部加载。

### 团队成员一览

| agentId | 中文名 | Emoji | workspace | 工具集 | 角色定位 |
|---------|--------|-------|-----------|--------|---------|
| `coder` | 闪电 | ⚡️ | workspace-coder | coding | 编码开发专家 |
| `product` | 诺娃 | 🧭 | workspace-product | full | 产品规划专家 |
| `tester` | 亚特拉斯 | 🔍 | workspace-tester | coding | 测试验证专家 |
| `research` | 露娜 | 🔭 | workspace-research | full | 调研搜索专家 |
| `trader` | 泰坦 | 📈 | workspace-trader | full | 投资分析专家 |
| `writer` | 萊拉 | ✒️ | workspace-writer | full | 内容写作专家 |
| `shield` | 盾卫 | 🛡️ | workspace-shield | full | 安全审计专家 |

### 检测通过后的输出

安装脚本或 Agent 检测全部通过后，向用户确认：

```
✅ Team Dispatch 环境就绪！
- 软连接：✅
- 任务目录：✅
- 项目模板：✅
- 用户配置：✅（语言：zh/en）
- 子 Agent Workspace：✅（7 个独立工作目录 + AGENTS.md）
- 子 Agent 配置：✅（workspace + identity + model 完整）
- Gateway：✅（已重启生效）

系统已准备好接收任务，请告诉我您想要完成什么？
```

### 常见安装问题与自动修复

| 问题 | 原因 | 修复方式 |
|------|------|---------|
| 子 Agent 没有独立 workspace | 旧版技能未配置 | 重新运行 setup.sh，自动创建并补齐 |
| 子 Agent 没有角色指令 | 缺少 AGENTS.md | setup.sh 从 assets/agents/ 复制模板 |
| 子 Agent 不知道自己是谁 | 缺少 identity 配置 | setup.sh 自动写入 identity 字段 |
| 用户配置不完整 | 手动创建了简化版 | 用 <SKILL_DIR>/config.json 覆盖 |
| 模型 404 / quota 错误 | 模型不可用 | 运行 `setup.sh --baseline-models` |

---

## 🌍 国际化（i18n）

默认英文，通过 `~/.openclaw/configs/team-dispatch.json` 中 `"language": "zh"` 切换中文。

---

## 📊 任务分级

收到需求后，先判断复杂度：

| 级别 | 判断标准 | 处理方式 |
|------|---------|---------|
| **S** | 单 Agent 可完成 | 直接 `sessions_spawn`，不建文件 |
| **M** | 2-3 个 Agent，线性依赖 | 自动建 DAG + 追踪 |
| **L** | 4+ Agent，有并行分支 | 自动建 DAG + 追踪 + 进度汇报 |
| **XL** | 跨多领域，需多轮迭代 | DAG + 分阶段交付 + 用户确认点 |

---

## 🔀 拆解模板

根据需求类型自动选择：

### 开发类
```
product(PRD) → coder(编码) → tester(测试) → shield(安全审计)
                             → writer(文档)
```

### 安全敏感类（带部署）
```
product(PRD) → coder(编码) → tester(测试) → shield(安全审计) → writer(文档)
```

### 研究类
```
research(调研) → product(分析框架) → writer(成文)
```

### 全栈类
```
research(调研) → product(PRD) → coder(编码) → tester(测试) → shield(安全审计) → writer(文档)
```

### 分析类
```
research(数据收集) → trader(分析) → writer(报告)
                   → product(策略建议)
```

### 内容类
```
research(素材收集) → writer(初稿) → product(审核优化)
```

---

## ⚠️ 重要限制：sessions_spawn 可能不允许指定 agentId

在某些运行环境/工具策略下，`sessions_spawn` 可能会拒绝 `agentId` 参数（错误类似：`agentId is not allowed for sessions_spawn (allowed: none)`）。

**此时 Team Dispatch 必须自动降级为“单 Agent 多角色模拟”模式：**
- 仍然按 DAG 拆解任务
- 派发时不传 `agentId`（让 subagent 继承当前 agent 身份）
- 在 task prompt 顶部注入角色指令（例如“你现在扮演 coder/product/tester…”）来模拟团队分工
- 结果收集、依赖解锁、重试逻辑保持不变

如果你有权限配置并希望启用真实多 Agent 派发：
- 在 `openclaw.json` 中设置 `agents.defaults.subagents.allowAgents: ["*"]`（或允许列表）
- 重启 Gateway

---

## ⚙️ 核心调度流程

> **⚠️ 关键行为约定：事件驱动的自动调度循环**
>
> 当你通过 `sessions_spawn` 派发任务后，OpenClaw 会在 subagent 完成时自动向你的会话推送一条 completion event（以 user message 形式到达）。
>
> **你必须在收到每一条 completion event 后，立刻执行完整的调度循环：**
> 1. 从 event 中提取 label，匹配到对应的 task
> 2. 更新该 task 的 status/result/completedAt，写入 JSON
> 3. 扫描所有 pending 任务，找出依赖已全部 done 的任务
> 4. 立刻派发这些就绪的任务（sessions_spawn）
> 5. 检查项目是否全部完成，若完成则归档并通知用户
>
> **不要等待用户指令，不要等待其他事件，不要跳过这个循环。每收到一条 completion event 就执行一次。**
>
> 这是 Team Dispatch 的核心机制——事件驱动的级联派发。如果你不执行这个循环，任务就会"卡住"。

### Step 1: 首次派发

扫描项目 JSON 中所有 `status=pending` 且依赖全部 `done`（或无依赖）的任务，批量派发：

```
for each task where status=="pending" && allDepsAreDone(task):
  task.status = "in-progress"
  task.startedAt = now()
  prompt = buildPrompt(task)
  sessions_spawn(agentId=task.agentId, task=prompt,
                 runTimeoutSeconds=task.timeoutSeconds,
                 label="{project}:{taskId}")
  task.sessionKey = response.childSessionKey
  writeJSON()
```

### Step 2: 收到 completion event → 立刻执行调度循环

当 subagent completion event 到达时（OpenClaw 自动推送，格式为 "✅ Subagent {agentId} finished\n{result}"），**你必须立刻执行以下完整流程，不需要用户指令**：

```
# ① 识别完成的任务
task = findByLabel(event.label)   # 或从 event 内容匹配 agentId + 上下文

# ② 更新状态
task.result = summarize(event.result)
task.status = "done"
task.completedAt = now()
writeJSON()

# ③ 扫描并派发就绪的下游任务（关键！）
dispatchReady():
  for each t where t.status=="pending" && allDepsAreDone(t):
    t.status = "in-progress"
    t.startedAt = now()
    prompt = buildPrompt(t)  # 含上游结果注入
    sessions_spawn(agentId=t.agentId, task=prompt, ...)
    t.sessionKey = response.childSessionKey
    writeJSON()

# ④ 检查项目是否全部完成
checkProjectDone():
  if all tasks are done/skipped:
    project.status = "completed"
    moveToArchive()          # tasks/active → tasks/done
    finalizeAndNotify()      # 向用户发送最终交付清单
```

> **再次强调**：Step 2 是一个自动触发的循环。你不需要也不应该等用户说"继续"或"下一步"。每收到一个 completion event，就执行一轮 ②→③→④。这样任务会像多米诺骨牌一样自动级联推进，直到全部完成。

### Step 3: Prompt 构建 — 结果注入

下游 Agent 自动获得上游输出：

```
buildPrompt(task):
  prompt = task.description
  if task.dependsOn:
    prompt += "\n\n--- 上游任务结果 ---"
    for depId in task.dependsOn:
      dep = findTask(depId)
      prompt += "\n\n[{dep.id}] ({dep.agentId}): {dep.result}"
  return prompt
```

### Step 4: 并行派发注意事项

当多个任务同时就绪时（如 t4-tests 和 t5-docs 都依赖 t3-core），应**同时派发**所有就绪任务，而非逐个等待：

```
# 错误做法 ❌：派发 t4，等 t4 完成，再派发 t5
# 正确做法 ✅：同时派发 t4 和 t5，各自独立完成后触发下游
```

---

## 🛡️ 故障处理

### 故障类型与自动恢复

| 类型 | 触发条件 | 自动处理 |
|------|---------|---------|
| 超时 | 超过 timeoutSeconds | 超时 × 1.5 后重试 |
| 失败 | Agent 返回 failed | 重试（最多 retryLimit 次） |
| 拒绝 | 并发上限 | 进入 queued，自动出队 |
| 模型错误 | 模型不可用(404等) | 检查修正模型配置 |

### 降级策略（onFailure 字段）

| 策略 | 值 | 行为 |
|------|---|------|
| 阻塞 | `"block"` | 中止项目，通知用户（默认） |
| 跳过 | `"skip"` | 标记 skipped，下游继续 |
| 降级 | `"fallback"` | 换备选 Agent 重试 |
| 人工 | `"manual"` | 暂停，等用户提供结果 |

---

## 📈 状态机

### 项目状态
```
active → completed    (全部 done/skipped)
active → blocked      (关键任务失败，重试耗尽)
active → cancelled    (用户取消)
blocked → active      (用户干预后恢复)
```

### 任务状态
```
pending → in-progress → done
       → queued       → in-progress   (并发满)
       → in-progress  → failed → pending (重试)
                               → skipped (跳过)
```

---

## 🔒 并发控制

- 并发上限由 `agents.defaults.subagents.maxChildrenPerAgent/maxConcurrent` 决定（默认 5，建议 10）
- 超出时任务进入 `queued` 状态，有 Agent 完成后自动出队
- 优先级：关键路径 > 依赖链长 > 声明顺序

---

## 🔗 依赖模式

| 模式 | 图示 | 场景 |
|------|------|------|
| 线性 | `A → B → C` | Bug 修复、简单功能 |
| 扇出 | `A → B, C, D` | 一个输入多个并行处理 |
| 扇入 | `B, C → D` | 多个结果汇合 |
| 菱形 | `A → B, C → D` | 先分后合 |

---

## ⏸️ 用户确认点（XL 级）

关键节点暂停等用户审核：

```json
{
  "id": "review-prd",
  "agentId": null,
  "description": "请用户确认 PRD 是否符合预期",
  "status": "pending",
  "dependsOn": ["prd"],
  "type": "checkpoint"
}
```

`checkpoint` 类型不派发 Agent，暂停并通知用户。

---

## 📁 项目文件

存储路径：`<workspace>/tasks/`

```
tasks/
├── active/          # 进行中
│   └── <project>.json
├── done/            # 已完成
│   └── <project>.json
└── templates/
    └── project.json  # 任务模板
```

---

## 🔧 运维工具

| 脚本 | 用途 | 命令 |
|------|------|------|
| `scripts/setup.sh` | 一键安装/配置 | `bash <SKILL_DIR>/scripts/setup.sh` |
| `scripts/setup.sh --baseline-models` | 切换稳定基线模型 | 解决 404/quota 问题 |
| `scripts/setup-config.sh` | 生成用户配置 | 自动跳过已存在 |
| `scripts/doctor.sh` | 环境健康检查 | `bash <SKILL_DIR>/scripts/doctor.sh` |
| `scripts/demo-project.sh` | 生成闭环自测 Demo 项目（product → coder → tester） | `bash <SKILL_DIR>/scripts/demo-project.sh` |
| `scripts/watch.sh` | 低频巡检卡死任务（前台运行） | `INTERVAL=300 GRACE=20 bash <SKILL_DIR>/scripts/watch.sh` |
| `scripts/watch-install.sh` | 安装 watcher（后台常驻，跨平台：macOS/Linux；Windows见ps1） | `bash <SKILL_DIR>/scripts/watch-install.sh` |
| `scripts/watch-uninstall.sh` | 卸载 watcher（后台常驻） | `bash <SKILL_DIR>/scripts/watch-uninstall.sh` |
| `assets/windows/watch-install.ps1.txt` | Windows 安装 watcher（Scheduled Task） | `copy <SKILL_DIR>\\assets\\windows\\watch-install.ps1.txt watch-install.ps1; powershell -ExecutionPolicy Bypass -File .\\watch-install.ps1` |
| `scripts/demo-project.sh` | 生成协作开发测试 Demo 项目（写入 tasks/active） | `bash <SKILL_DIR>/scripts/demo-project.sh` |

### ✅ 闭环自测（最小协作链路）

1) 生成一个带 3 个任务的 Demo DAG（写入 `~/.openclaw/workspace/tasks/active/`）：

```bash
bash <SKILL_DIR>/scripts/demo-project.sh
```

2) 然后在 **main agent** 对话中说：

- “请用 team-dispatch 跑一下刚生成的 demo-collab-loop 项目（product → coder → tester），并在完成后归档到 tasks/done。”

> 预期：main 会按依赖顺序依次 `sessions_spawn(product/coder/tester)`，并把结果写回项目 JSON，最终移动到 `tasks/done/` 并汇总汇报。

---

## ✅ 闭环自测（协作开发测试 Demo）

生成一个最小可验证的协作开发 DAG 项目（默认 `team-mvp-1`），写入：`~/.openclaw/workspace/tasks/active/`：

```bash
bash <SKILL_DIR>/scripts/demo-project.sh
```

生成后，在主 Agent 里发一句话触发调度（示例）：

> 请用 team-dispatch 跑一下刚生成的 team-mvp-1 demo 项目，按 DAG 依赖派发 product/coder/tester/writer，完成后归档到 tasks/done。

---

## 📋 完整调度示例

### 输入
```
用户: "帮我调研 AI Agent 市场，写一篇分析报告"
```

### 自动处理
```
1. 分析: 研究类，L 级
2. 拆解: research → product(框架) → writer(成文) + coder(可视化)
3. 建 DAG: tasks/active/ai-report.json
4. 派发: research（无依赖）
5. research done → 派发 product（注入 research 结果）
6. product done → 并行派发 writer + coder（注入上游结果）
7. 全部完成 → 归档 tasks/done/ → 汇报用户
```

### 输出
```
✅ 项目完成！
- 📝 分析报告: [内容]
- 📊 可视化: ~/work/ai-report/index.html
- 🔎 预览方式: open ~/work/ai-report/index.html
```
