---
name: openclaw-workflow
description: OC-Flow：为你的 OpenClaw 注入"确定性"灵魂。OC-Flow 完全嵌入在 OpenClaw 体系内，赋予 Agent 完整的流程控制能力：条件分支、循环遍历、精准等待、状态管理。通过 YAML 剧本实现固定流程、多步循环、严苛逻辑的任务。适用场景：财务办公、开发运维、个人助理。
metadata: {"openclaw":{"emoji":"🔀","requires":{"bins":["python3"]}}}
---

# OpenClaw Workflow — 确定性工作流引擎

在不破坏 OpenClaw 灵活性的前提下，按 YAML 剧本执行 100% 确定性逻辑：判断、循环、脚本、LLM 调用、Skill 调用。

这是一个符合 OpenClaw / AgentSkills 目录约定的 Skill：
- `SKILL.md`：触发条件与使用说明
- `scripts/`：可执行入口与运行时代码
- `references/`：参考文档与示例工作流

## 使用方法

> **重要**: 脚本内置了 stdout 行缓冲，不需要额外设置 `PYTHONUNBUFFERED`。

```bash
# 运行工作流
python3 {baseDir}/scripts/openclaw_workflow.py execute <workflow.yaml>

# 验证工作流语法
python3 {baseDir}/scripts/openclaw_workflow.py validate <workflow.yaml>

# 列出可用工作流
python3 {baseDir}/scripts/openclaw_workflow.py list

# 查看历史运行
python3 {baseDir}/scripts/openclaw_workflow.py runs

# 从断点恢复
python3 {baseDir}/scripts/openclaw_workflow.py resume <run_id>

# 可视化面板
python3 {baseDir}/scripts/openclaw_workflow.py dashboard
```

## 工作流文件放在哪里

推荐目录（OpenClaw 自建/自维护流程）：

```bash
~/.openclaw/workspace/workflows
```

面板与 CLI 会优先发现以下位置：

1. `{baseDir}/references/examples`
2. `~/.openclaw/workspace/workflows`

说明：面板只扫描固定目录，不会递归读取整个 `~/.openclaw/workspace`。

**示例:**
```bash
# 运行示例工作流
python3 {baseDir}/scripts/openclaw_workflow.py execute {baseDir}/references/examples/basic_test.yaml

# 运行深度集成测试
python3 {baseDir}/scripts/openclaw_workflow.py execute {baseDir}/references/examples/deep_integration.yaml

# 查看补充设计说明
cat {baseDir}/references/readme.md
```

## 输出格式

JSON 运行记录，包含：
- `run_id` — 运行唯一 ID
- `flow_id` — 工作流名称
- `status` — `success` | `failed` | `aborted`
- `steps` — 每步执行结果（状态、输出、耗时、重试次数）
- `started_at` / `finished_at` — 起止时间

终端同时输出人可读的步骤进度日志。

## OpenClaw 深度绑定

- `llm` / `agent` / `skill` 节点通过 **Gateway RPC** 调用，不是本地直连模型。
- 同一工作流运行内所有调用共享同一个 **session**，Agent 拥有完整对话上下文。
- 模型由 OpenClaw Agent/Provider 配置统一管理，无需在工作流中指定。

## 工作流 YAML 格式

```yaml
name: "我的流程"
steps:
  - id: fetch
    type: script
    command: "curl -s https://api.example.com/data"

  - id: analyze
    type: llm
    prompt: "分析: {{fetch.output}}"

  - id: delegate
    type: subagent
    task: "根据以下分析结果生成一份详细报告: {{analyze.text}}"
    label: "报告生成器"
    wait: true
    timeout: 300

  - id: notify
    type: message
    channel: imessage
    target: "+861760051xxxx"
    message: "结果: {{delegate.result}}"
```

## 节点类型速查

| 类型 | 说明 | 关键参数 |
|------|------|----------|
| `script` | Shell/Python 脚本 | `command`, `inline`, `timeout` |
| `llm` | LLM 推理 (Gateway session) | `prompt`, `thinking`, `session` |
| `agent` | Agent 调用 (Gateway session) | `message`, `thinking`, `deliver` |
| `subagent` | 创建子代理执行独立任务 | `task`, `label`, `model`, `wait` |
| `wait_subagents` | 等待多个 Subagent 完成并收集结果 | `tracker`, `max_wait`, `poll_interval` |
| `skill` | 调用 OpenClaw Skill (Gateway session) | `action`, `args`, `instruction` |
| `condition` | If-Else 分支 | `if`, `then`, `else` |
| `loop` | 循环遍历 | `foreach`/`times`, `as`, `do` |
| `set` | 设置变量 | `var`, `value` |
| `log` | 日志输出 | `message`, `level` |
| `http` | HTTP 请求 | `url`, `method`, `headers`, `body` |
| `code` | 内联 Python (沙箱) | `python` |
| `wait` | 延时/等待条件 | `seconds`, `until` |
| `message` | 发送消息 | `channel`, `target`, `message` |

## 变量传递

- `{{variable}}` — 全局变量
- `{{step_id.output}}` / `{{step_id.text}}` — 步骤输出
- `{{item}}` — 循环当前元素
- `{{env.HOME}}` — 环境变量

## 错误处理

每步可配置: `retry: 3`, `retry_delay: 10`, `on_error: retry|skip|stop`

## 典型场景

- **每日简报**: 获取数据 → AI 分析 → 格式化 → 发送
- **发票归档**: 扫描邮件 → 识别发票 → 上传 NAS
- **固件打包**: 拉取代码 → 构建 → 测试 → 打包 → 通知
- **数据监控**: 定时检查 → 条件判断 → 告警
- **并行研究**: 创建多个 subagent 分头调研 → 汇总结果

## Subagent 节点

`subagent` 节点通过 OpenClaw `sessions_spawn` 工具创建独立子代理。

**与 agent 节点的区别:**
- `agent`: 在共享 session 中调用主 Agent，同一上下文
- `subagent`: 创建独立子代理，有自己的 session、系统提示和模型配置

### 创建流程

每个 subagent 的创建需要两层 session:

1. **Spawn session** — 用于承载 `sessions_spawn` 工具调用的"载体 session"
2. **Child session** — 由 `sessions_spawn` 在 Gateway 侧创建的实际子代理 session (`agent:main:subagent:<uuid>`)

`sessions_spawn` 是 Agent 工具 (不是 Gateway 直接 RPC)，所以必须通过 `agent_call` 在某个 session 中触发。spawn session 本身只是工具调用的容器，子代理真正执行任务的是 child session。

### 两种 Spawn Session 模式

#### 模式 A: 传统模式 (独立 session)

每个 spawn 创建一个临时的 `spawn:<hex>` session → `agent_call` 让 Agent 调用 `sessions_spawn` → 提取 childSessionKey → 立即删除 spawn session。

- **Session 数**: N 个 spawn (瞬态，创建后立删) + N 个 child = 持久 N 个
- **并发**: session 独立，天然支持并行
- **上下文**: 每次全新 session，无膨胀问题

#### 模式 B: 工厂模式 (共享 session) — 当前默认

所有 spawn 复用同一个 `factory:<hex>` session → 每 20 次轮换新 session → 用 `factory_lock` 序列化访问。

- **Session 数**: ~ceil(N/20) 个 factory + N 个 child ≈ N + 几个
- **并发**: `factory_lock` **强制所有 spawn 串行执行**，即使在并行循环中
- **上下文**: 累积增长，需要定期轮换

### ✅ 已解决问题 (2026-03-17 → 2026-03-18)

**原问题 1: 循环中工厂模式强制串行**

已通过批量 spawn 解决。循环中自动检测并使用批量创建。

**原问题 2: Gmail 24 封邮件超时**

批量 spawn 10 个 subagent 仅需 ~77s，24 个预计 ~90-120s，远低于超时限制。

**2026-03-18 架构更新: 子会话模式**

非循环场景下的单个 subagent 节点不再通过 sessions_spawn 间接创建，而是直接创建新会话执行任务。
会话就是 subagent，省去了 spawn 中间层。

**参数:**
| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `task` | ✅ | — | 子代理要执行的任务描述 |
| `label` | — | (空) | 子代理显示名称 |
| `model` | — | (继承) | 覆盖使用的模型 |
| `thinking` | — | (关) | 思考级别: off/minimal/low/medium/high |
| `timeout` | — | 300 | 超时秒数 |
| `wait` | — | false | 是否等待子代理完成 |
| `poll_interval` | — | 15 | 等待时轮询间隔 (秒) |
| `mode` | — | run | `run` (一次性) 或 `session` (持久) |
| `cleanup` | — | auto | `keep` (保留) 或 `auto` (wait 完成后自动删除 session) |
| `throttle_timeout` | — | 300 | 并发等待超时 (秒)，达到 maxConcurrent 限制时等待空位 |
| `spawn_timeout` | — | 120000 | Gateway 调用超时 (ms) |
| `spawn_retries` | — | 2 | Gateway timeout 重试次数 |

**示例 — fire-and-forget:**
```yaml
- type: subagent
  task: "整理今天的新闻摘要"
  label: "新闻助手"
```

**示例 — 等待结果:**
```yaml
- id: research
  type: subagent
  task: "研究 {{topic}} 并写一份 500 字的分析报告"
  label: "研究员"
  wait: true
  timeout: 600
  poll_interval: 20

- type: log
  message: "研究结果: {{research.result}}"
```

## Wait Subagents 节点

`wait_subagents` 节点实现标准的 subagent fan-in (汇合) 模式:
- 在 loop 中通过 `subagent` 节点 (wait: false) 创建多个并行子代理
- 用 code 节点在 loop 中收集 spawn 信息到 tracker 列表
- `wait_subagents` 节点轮询所有子代理的 JSONL completion event，全部完成后返回结果列表

### 完成检测 (两级策略)

- **策略 A (精确)**: 读取 spawn session 的 JSONL，查找 auto-announce completion event。仅在 spawn session 未被清理时可用 (wait=true 或工厂模式)
- **策略 B (直读)**: 直接读取 child session 的 JSONL，检查是否有 assistant 回复。这是 wait=false 模式的主要检测路径，因为 spawn session 在创建后立即清理

### 自动清理 (三层保障)

- **即时清理:** 子会话模式 `wait=true` 完成后立即删除 child session
- **汇合清理:** `wait_subagents` 节点完成后批量清理所有 child session (cleanup: auto)
- **兆底清理:** 工作流结束时 (无论成功/失败/中断)，engine.py 的 finally 块会清理:
  - 工作流主 session (`agent:main:openclaw-workflow:<ns>`)
  - 所有残留的 spawn/factory/child session
  - tracker 中记录的 child session
  - 工厂模式内部追踪的 child session (via `get_factory_child_session_keys`)

### 并发控制

`subagent` 节点在创建时会检查两个配置:
- `agents.defaults.subagents.maxConcurrent` (子代理专属限制，默认 20)
- `agents.defaults.maxConcurrent` (Gateway 全局嵌入式运行并发限制，默认 4)

取两者较小值作为实际限制。并发计数仅统计 `:spawn:` session (瞬态占位)，不统计 `:subagent:` session (因为完成后仍残留在 sessions.json 中会导致误判)。

### 内置重试

`subagent` 节点对 Gateway timeout 错误内置 2 次重试 (spawn_retries=2)，spawn 超时时间 120s (spawn_timeout=120000ms)。

**参数:**
| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `tracker` | ✅ | — | spawn 信息列表 (需包含 spawn_session_key, child_session_key) |
| `max_wait` | — | 600 | 最大等待秒数 |
| `poll_interval` | — | 5 | 轮询间隔秒数 |
| `extra_fields` | — | [] | 从 tracker item 透传到结果中的额外字段名 |
| `cleanup` | — | auto | Session 清理策略: `auto` (全部清理), `completed` (仅清理已完成的), `keep` (不清理) |

**示例 — 并行分类:**
```yaml
# 1) 初始化 tracker
- id: init_tracker
  type: code
  python: "result = []"

# 2) loop 中 fire-and-forget spawn + 收集信息
- type: loop
  foreach: "{{items}}"
  as: item
  do:
    - id: spawn_task
      type: subagent
      task: "分析: {{item.data}}"
      wait: false
    - id: collect
      type: code
      python: |
        tracker = init_tracker if isinstance(init_tracker, list) else []
        tracker.append({
            "item_id": item.get("id", ""),
            "spawn_session_key": spawn_task.get("spawn_session_key", ""),
            "child_session_key": spawn_task.get("child_session_key", ""),
        })
        result = tracker

# 3) 等待全部完成
- id: wait_all
  type: wait_subagents
  tracker: "{{init_tracker}}"
  max_wait: 600
  poll_interval: 5
  extra_fields:
    - item_id

# 4) 使用结果
- type: agent
  message: "汇总: {{wait_all}}"
```

## 全节点详解（参数 + 示例）

下面补全每个节点的常用写法，优先覆盖实际引擎支持的字段。

### 通用字段（所有节点都可用）

| 字段 | 说明 |
|------|------|
| `id` | 步骤唯一标识，建议填写，便于引用 `{{step_id.output}}` |
| `name` | 人类可读名称，仅用于日志 |
| `type` | 节点类型 |
| `retry` | 失败重试次数 |
| `retry_delay` | 每次重试间隔（秒） |
| `on_error` | `retry` / `skip` / `stop` |

---

### 1) `script` 节点

执行 shell 命令或内联 Python。

**支持字段：**
- `command` / `script` / `file`：三选一
- `inline`：内联 Python 代码（会写入临时 `.py` 执行）
- `timeout`：默认 300 秒
- `cwd`：工作目录
- `env`：环境变量字典

```yaml
- id: fetch_data
  type: script
  command: "curl -s https://api.example.com/data"
  timeout: 30

- id: build_report
  type: script
  inline: |
    import json
    print(json.dumps({"ok": True, "ts": "{{env.HOME}}"}, ensure_ascii=False))
```

---

### 2) `llm` 节点

通过 Gateway 调用模型推理，默认复用当前工作流会话。

**支持字段：**
- `prompt`（必填）
- `thinking`：`off|minimal|low|medium|high`
- `timeout`：秒，默认 120
- `session`：`shared`（默认）或 `isolated`

```yaml
- id: summarize
  type: llm
  prompt: "请总结以下内容：{{fetch_data.output}}"
  thinking: low
  session: shared
```

---

### 3) `agent` 节点

调用主 Agent。与 `llm` 相比，支持投递能力（deliver）。

**支持字段：**
- `message`（必填）
- `thinking`
- `timeout`：默认 300
- `deliver`：是否自动投递
- `deliver_channel` / `deliver_target`

```yaml
- id: agent_reply
  type: agent
  message: "根据 {{summarize.text}} 输出客户可读版本"
  deliver: true
  deliver_channel: imessage
  deliver_target: "+8617600510003"
```

---

### 4) `skill` 节点

让 Agent 在当前会话中调用已有 Skill。

**支持字段：**
- `action`（必填）
- `args`：参数对象
- `instruction`：自定义指令（有则优先）
- `timeout`：默认 300

```yaml
- id: call_tool_skill
  type: skill
  action: "transmission.add"
  args:
    url: "magnet:?xt=..."
  instruction: "请添加该任务并返回任务ID"
```

---

### 5) `condition` 节点

条件分支，执行 `then` 或 `else` 子步骤。

**支持字段：**
- `if`（必填）：Python 表达式字符串
- `then`：条件为真时执行的步骤数组
- `else`：条件为假时执行的步骤数组

```yaml
- id: check_items
  type: condition
  if: "len(load_emails) > 0"
  then:
    - type: log
      message: "有邮件"
  else:
    - type: log
      message: "无邮件"
```

---

### 6) `loop` 节点

循环执行子步骤，支持 `foreach` 或 `times`。

**支持字段：**
- `foreach`：列表/可解析为列表的值
- `times`：整数次数（与 `foreach` 二选一）
- `as` / `var`：循环变量名，默认 `item`
- `do` / `steps`：子步骤数组

```yaml
- id: iterate
  type: loop
  foreach: "{{items}}"
  as: item
  do:
    - type: log
      message: "当前: {{item}}"

- id: retry_three_times
  type: loop
  times: 3
  as: i
  do:
    - type: log
      message: "第 {{i}} 次"
```

---

### 7) `set` 节点

设置全局变量。

**支持字段：**
- `var`（必填）
- `value`（必填）

```yaml
- id: set_topic
  type: set
  var: topic
  value: "PiSugar"
```

---

### 8) `log` 节点

写运行日志。

**支持字段：**
- `message`（必填）
- `level`：默认 `INFO`

```yaml
- type: log
  level: "WARN"
  message: "当前数据为空，进入降级路径"
```

---

### 9) `http` 节点

发送 HTTP 请求。

**支持字段：**
- `url`（必填）
- `method`：默认 `GET`
- `headers`
- `params`：Query 参数
- `body`：可为对象/数组/字符串
- `timeout`：默认 30

```yaml
- id: request_api
  type: http
  method: POST
  url: "https://api.example.com/v1/report"
  headers:
    Authorization: "Bearer {{token}}"
  body:
    title: "日报"
    content: "{{summarize.text}}"
```

---

### 10) `code` 节点

执行沙箱 Python。将当前变量与历史步骤输出注入运行环境。

**支持字段：**
- `python`（必填）

**结果约定：**
- 优先取变量 `result` 作为节点输出
- 若无 `result`，则返回 `print` 输出文本

```yaml
- id: calc_stats
  type: code
  python: |
    items = load_emails if isinstance(load_emails, list) else []
    result = {
      "count": len(items),
      "subjects": [x.get("subject", "") for x in items[:5] if isinstance(x, dict)]
    }
```

---

### 11) `wait` 节点

固定延时或轮询等待条件。

**支持字段：**
- `seconds`：固定等待秒数
- `until`：条件表达式（与 `seconds` 二选一）
- `poll_interval`：默认 5
- `max_wait`：默认 300

```yaml
- type: wait
  seconds: 10

- type: wait
  until: "task_done == True"
  poll_interval: 3
  max_wait: 180
```

---

### 12) `message` 节点

发送消息。默认通过 Agent 代发，`direct: true` 时走 CLI 直发。

**支持字段：**
- `channel`：默认 `imessage`
- `target`（必填）
- `message` / `media`：至少一个
- `account`：可选账号
- `direct`：默认 `false`
- `when`：条件守卫，不满足则跳过

```yaml
- id: notify
  type: message
  channel: imessage
  target: "+8617600510003"
  message: "📬 报告如下：{{agent_reply.text}}"
  when: "len(agent_reply.text) > 0"
```

---

### 13) `subagent` 节点

创建子代理执行独立任务，支持异步或等待模式。

**支持字段：**
- `task`（必填）
- `label` / `model` / `thinking`
- `timeout`：默认 300
- `wait`：默认 `false`
- `poll_interval`：默认 5
- `mode`：`run`（默认）/ `session`
- `cleanup`：`auto`（默认）/ `keep`
- `throttle_timeout`：并发等待超时，默认 300
- `spawn_timeout`：Gateway 调用超时 (ms)，默认 120000
- `spawn_retries`：Gateway timeout 重试次数，默认 2

```yaml
- id: classify_one
  type: subagent
  task: "请分类此邮件：{{email.body}}"
  label: "邮件分类器"
  wait: true
  timeout: 120
  cleanup: auto
```

---

### 14) `wait_subagents` 节点

汇合多个 `wait: false` 子代理，集中等待并收集结果。

**支持字段：**
- `tracker`（必填）
- `max_wait`：默认 600
- `poll_interval`：默认 5
- `extra_fields`：透传字段
- `cleanup`：`auto`（默认）/ `completed` / `keep`

```yaml
- id: wait_all
  type: wait_subagents
  tracker: "{{init_tracker}}"
  extra_fields: [email_id, subject]
  cleanup: auto
```

---

## 最佳实践

1. 为每个步骤加 `id`，避免后续引用困难。  
2. `loop + subagent(wait:false) + code(collect) + wait_subagents` 是推荐并行模式。Engine 会自动检测此模式并使用**批量 spawn**（单次 agent_call 并行创建多个 subagent），无需额外配置。  
3. 面向生产流程建议显式写 `timeout`、`retry` 和 `on_error`。  
4. 需要会话隔离时，用 `llm.session: isolated` 或 `subagent`。  
5. 结果给下游节点使用时，优先在 `code` 节点输出结构化 `result`。  
6. 大批量 subagent (>10) 可通过 `spawn_batch_size` 调整每批数量，默认 8。  

## 架构备忘 (内部)

### Subagent 批量 Spawn (Batch Spawn) — 2026-03-17 实现

**核心思路**: OpenClaw Agent 在单次对话回复中可以并行调用多次 `sessions_spawn` 工具。利用这一点，engine 在一次 `agent_call` 中指示 Agent 同时创建 N 个 subagent，而不是每个 subagent 单独调一次。

**自动触发条件**: `_execute_loop()` 会自动检测循环体是否符合 "subagent(wait=false) + code(collect)" 模式。如果符合且 `len(items) > 1`，自动走批量 spawn 路径，无需任何 YAML 配置变更。

**批量 spawn 流程**:
1. `engine._detect_batch_spawn_pattern(sub_steps)` → 检测循环体结构
2. `engine._execute_loop_batch_spawn()` → 开 factory session → 分批调用 `batch_spawn_subagents()`
3. `nodes.batch_spawn_subagents(items, step_template, ctx, log, bridge, batch_size)`:
   - 将 items 按 `batch_size` (默认 8) 分批
   - 每批构造一条指令：要求 Agent 在一次响应中并行调用 N 次 `sessions_spawn`
   - 通过 `bridge.agent_call()` 发送到 factory session
   - 用 `bridge.extract_all_spawn_info_from_session_log()` 从 JSONL 提取所有 `childSessionKey`
4. 所有 spawn 完成后，逐个执行 collect step (记录 spawn 信息到 tracker)
5. 关闭 factory session

**性能对比**:

| 模式 | 10 个 subagent | 24 个 subagent (Gmail) | Session 开销 |
|------|---------------|----------------------|-------------|
| 子会话模式 (单个) | ~25s | N/A (非循环) | 1 child |
| subagent 串行 | ~250s (25s×10) | ~600s (超时❌) | N + 几个 |
| **批量 spawn** | **~77s** ✅ | **预计 ~90-120s** ✅ | N + 1 factory |

**实测数据** (batch_test10, 2026-03-17):
- 10 个 subagent, batch_size=5, 共 2 批
- 第 1 批 [1-5]: 30s, 第 2 批 [6-10]: 47s
- 总耗时 77s (含 factory 开启/关闭)
- Factory session 仅 1 个, 10/10 全部成功

**关键代码路径**:
- `engine.py` `_detect_batch_spawn_pattern()` → 模式检测
- `engine.py` `_execute_loop_batch_spawn()` → 批量执行入口
- `nodes.py` `batch_spawn_subagents()` → 核心批量 spawn 逻辑
- `bridge.py` `extract_all_spawn_info_from_session_log()` → 从 JSONL 提取全部 spawn 结果
- `bridge.py` 工厂 session 管理 (open/close/rotate/track) — 仍然使用

**参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `spawn_batch_size` | 8 | 每批并行创建的 subagent 数量 (YAML step 级别可配) |
| `spawn_timeout` | 180000ms | 批量 spawn 的 Gateway 超时 (比单个 spawn 的 120000ms 更长) |
| `spawn_retries` | 2 | Gateway timeout 重试次数 |

**注意事项**:
- `sessions_spawn` 的 `cleanup` 字段只接受 `"delete"` 或 `"keep"`，不接受 `"auto"`
- 如果 Agent 实际创建的 subagent 数 < 批次要求数，会自动重试或降级
- 并发限制仍然生效: `min(subagents.maxConcurrent=20, maxConcurrent=8)`
- 非批量场景 (单个 subagent、wait=true) 走子会话模式 (直接执行)
