---
name: auto-qa
description: 在 OpenClaw 平台执行网页自动 QA 测试（自动操作 + 采证 + 报告 + 修复提示包）。当用户要求做自动化回归、演示级测试、失败证据归档或生成可直接交给下一窗口的修复 Prompt 时使用。
---

# Auto QA (OpenClaw Browser)

用于一期 MVP：

- 自动执行网页关键路径
- 自动采集失败证据（截图、console、network、trace）
- 自动输出 CTO 可读报告与修复任务包
- 自动重试、断点续跑、健康检查与失败分类（环境/产品）

## 实际组件构成（一期 MVP）

1. `场景定义组件`

- 位置：`demo/scenarios/*.json`
- 作用：声明测试步骤、断言条件、期望结果。
- 输入：业务路径（P0 场景）。
- 输出：可执行步骤序列（供执行编排器读取）。

2. `执行编排器`

- 位置：`src/skills/auto-qa/scripts/run_autoqa.py`
- 作用：读取场景并调用 `openclaw browser` 执行动作。
- 输入：场景 JSON、浏览器 profile、run_id。
- 输出：步骤结果、证据文件、汇总报告与修复提示包。

3. `浏览器执行器（OpenClaw 内置能力）`

- 位置：OpenClaw CLI `openclaw browser ...`
- 作用：点击、输入、等待、快照、截图、日志与 trace。
- 输入：编排器下发的步骤参数。
- 输出：结构化 JSON 结果和调试数据。

4. `证据归档组件`

- 位置：`demo/artifacts/run-<run_id>/`
- 作用：按 run 归档步骤明细、截图、console、network、trace。
- 输入：执行过程中的实时证据。
- 输出：可追溯的失败证据包。

5. `报告生成组件`

- 位置：`demo/reports/run-<run_id>/report.json`、`demo/reports/run-<run_id>/report.html`
- 作用：给出通过率、阻断项、Go/No-Go 判定。
- 输入：步骤结果 + 证据统计。
- 输出：机器可读（JSON）与演示可读（HTML）报告。

6. `修复任务包生成组件`

- 位置：`demo/reports/run-<run_id>/fix_plan.json`、`next_window_prompt.md`、`standby_prompt.txt`
- 作用：将"测试失败证据"转成"可直接执行的修复任务"。
- 输入：失败步骤、console、network、trace 路径。
- 输出：根因假设、检查方向、修改方向、验收标准、下一窗口提示词。

7. `稳定性增强组件`

- 位置：`src/skills/auto-qa/scripts/run_autoqa.py`
- 作用：减少"主画面外运行"时的抖动风险，提升演示稳定度。
- 能力：
  - 步骤自动重试（默认每步 1 次重试）
  - 断点续跑（从失败步骤继续）
  - 健康检查（off/on-failure/each-step）
  - 失败分类（environment/product/unknown）

8. `门禁断言组件`

- 位置：`src/skills/auto-qa/scripts/run_autoqa.py`
- 作用：将采证数据升级为发布门禁判定，防止"假 GO"。
- 默认规则：
  - console `error` -> 违规（critical）
  - 同域 network `4xx` -> 违规（critical）
  - 同域 network `5xx` -> 违规（blocker）
- 报告输出：
  - `gateViolations`
  - `gateViolationCountsBySeverity`
  - `riskLevel`
  - `releaseDecision`（GO / CONDITIONAL_GO / NO_GO）
  - `reviewStatus`（consistent / needs_inspection）
  - `reviewConclusion`（复核一致 / 复核需进一步检验）
  - `reviewFindings`（需进一步检验时的具体项）

9. `Trace 对齐组件`

- 位置：`demo/reports/run-<run_id>/step_trace_map.json`
- 作用：把步骤时间窗与 trace 时间线自动对齐，便于"步骤 -> 证据"快速追溯。
- 输出：每个步骤对应的 trace 事件计数、帧计数、console/API/network 样本。

10. `报告通知组件`

- 位置：`src/skills/auto-qa/scripts/run_autoqa.py`（运行参数触发）
- 作用：自动截取 `report.html` 全页图并发送到聊天频道。
- 规则：
  - 传入 `--notify-channel` 时触发。
  - 未传 `--notify-target` 时，自动从 `openclaw status --json` 最近会话推断目标（当前频道优先）。

## 一期范围（防跑偏）

- 仅网页 P0 场景（3-5 条关键路径）
- 证据四件套：`screenshot + console + network + trace`
- 交付最小集合：
  - `report.json`
  - `report.html`
  - `fix_plan.json`
  - `next_window_prompt.md`
  - `standby_prompt.txt`

## 目录约定

```text
demo/
  scenarios/
    mvp_smoke.json
    _generated/          ← agent 智能生成的临时 scenario 存放目录
  artifacts/
    run-<run_id>/
      steps.json
      console.json
      network.json
      health_checks.json
      trace.zip
      screenshots/
  reports/
    run-<run_id>/
      report.json
      report.html
      report_full.png
      step_trace_map.json
      fix_plan.json
      next_window_prompt.md
      standby_prompt.txt
```

## 场景 JSON（最小格式）

```json
{
  "name": "MVP Smoke",
  "autoScreenshot": true,
  "continueOnFailure": false,
  "steps": [
    { "id": "step-001", "action": "open", "url": "https://example.com", "expected": "页面可访问" },
    { "id": "step-002", "action": "wait", "text": "Example Domain", "expected": "标题出现" },
    {
      "id": "step-003",
      "action": "assert_text_contains",
      "value": "Example Domain",
      "expected": "正文包含关键字"
    }
  ]
}
```

## 场景 JSON（门禁规则示例）

```json
{
  "name": "WeHub Smoke",
  "gates": {
    "enabled": true,
    "minPassRate": 95,
    "console": {
      "errorAsFailure": true,
      "ignoreMessagePatterns": ["known harmless error"]
    },
    "network": {
      "sameOrigin4xxAsFailure": true,
      "sameOrigin5xxAsFailure": true,
      "thirdParty5xxAsFailure": false,
      "ignoreUrlPatterns": ["/favicon.ico"],
      "ignoreStatusCodes": [401]
    }
  },
  "steps": []
}
```

## 场景 JSON（动作展示配置示例）

```json
{
  "name": "Visual Demo",
  "visual": {
    "enabled": true,
    "focusTabBeforeStep": true,
    "preActionWaitMs": 220,
    "postActionWaitMs": 420,
    "highlightBeforeClick": true,
    "highlightBeforeType": true,
    "highlightWaitMs": 480
  },
  "steps": []
}
```

说明：

- `focusTabBeforeStep`：每步前尽量聚焦受控 tab，减少后台节流导致的观感抖动。
- `preActionWaitMs/postActionWaitMs`：动作前后节奏等待，提升"可见点击/跳转"观感。
- `highlightBeforeClick/highlightBeforeType`：动作前高亮目标元素。

## 支持动作（MVP）

- `open`
- `navigate`
- `snapshot`
- `click`
- `hover`
- `type`
- `press`
- `back`
- `scroll`
- `click_link_same_origin`
- `wait`
- `evaluate`
- `assert_url_contains`
- `assert_text_contains`
- `screenshot`
- `noop`

## 场景 JSON 校验层（安全网）

`run_autoqa.py` 在加载 scenario 时自动执行 pre-flight 校验：

1. **JSON 语法**：解析失败会报告精确行号/列号
2. **必须字段**：每个 step 必须含 `action` 字段
3. **动作白名单**：`action` 值必须在上述"支持动作"列表内，否则报错并列出全部合法值
4. **参数完整性**：`open`/`navigate` 须含 `url`；`click`/`hover`/`type` 须含 `ref`；`assert_*` 须含 `value`

校验在执行前触发，出错时给出明确的 step 索引和原因——不会默默失败。

生成 scenario 时请确保遵守上述约束。`id` 字段建议保留（格式 `step-NNN`），缺省时引擎会自动补全。

## 场景 JSON（探索配置与返回边覆盖）

```json
{
  "exploration": {
    "enabled": true,
    "maxDepth": 3,
    "maxChildrenPerNode": 5,
    "maxPages": 30,
    "maxDurationMinutes": 15,
    "sameOriginOnly": true
  },
  "steps": [
    { "id": "step-010", "action": "click_link_same_origin", "depth": 2 },
    { "id": "step-011", "action": "back", "returnEdge": true, "depth": 2 }
  ]
}
```

说明：

- `depth`：步骤所属探索层级（用于覆盖统计）。
- `returnEdge=true`：该步骤计入"返回边"覆盖统计（`back` 动作默认计入）。

## 运行方式

在仓库根目录执行：

```bash
python3 src/skills/auto-qa/scripts/run_autoqa.py \
  --scenario-id wehub_demo \
  --browser-profile openclaw \
  --auto-start-browser
```

## 执行协议（强约束）

当用户表达"跑 QA / 再测一次 / 做自动回归 / 开始测试"等执行意图时，默认进入**直接执行**，不先回复"计划确认"。

### 场景生成优先级（核心规则 — 严格按此顺序执行）

正常流程**不使用预设脚本**。场景（scenario）应由 agent 智能生成。

**优先级 1：用户给了测试要求（自然语言）**

用户可能说："测一下登录功能"、"检查购物车流程"、"用以下用例做自动 QA 测试：……"。

agent 必须：

1. 用 `openclaw browser open <url>` 打开目标
2. 用 `openclaw browser snapshot --interactive --labels` 扫描页面结构
3. 理解用户的自然语言要求，对照页面上实际存在的元素（表单、按钮、链接、输入框等）
4. 生成包含用户所有要求的 scenario JSON（每条要求对应具体的 action + expected + assertion）
5. 将 scenario JSON 写入 `demo/scenarios/_generated/<run-id>.json`
6. 用 `--scenario <path> --force-direct-scenario-path` 执行

**严禁忽略用户的任何测试要求。** 如果页面上找不到用户要求的元素，在 scenario 中仍要包含该步骤并标注 expected，让执行引擎报告失败——而不是静默跳过。

**优先级 2：用户只给了 URL，没有具体要求**

agent 必须：

1. 用 `openclaw browser open <url>` 打开目标
2. 用 `openclaw browser snapshot --interactive --labels` 扫描页面结构
3. 分析页面上的所有可交互元素：链接、按钮、表单、输入框、导航菜单等
4. 智能生成覆盖以下维度的 scenario JSON：
   - 页面可访问性（navigate + assert_url）
   - 核心可交互元素（click 按钮、填写表单、点击链接）
   - 导航完整性（跳转 + 返回）
   - 内容断言（assert_text_contains 关键文案）
5. 将 scenario JSON 写入 `demo/scenarios/_generated/<run-id>.json` 并执行
6. 执行完成后，BFS 探索引擎自动补充未覆盖的同域页面

**生成的 scenario 必须基于实际页面内容，不能凭空猜测。** 每个 step 的 ref、url、text 必须来自 snapshot 的真实数据。

**优先级 3（极端后备）：snapshot 失败或浏览器不可用**

仅当以上两种方式都失败时（如浏览器无法启动、目标不可达），才回退到预设脚本：

- 使用注册表默认 `defaultScenarioId` 或 `generic_template`
- **必须向用户明确警告**："无法扫描目标，已回退到通用模板，测试覆盖度有限"

**预设脚本（scenario-id）仅用于以下场景：**

- 用户明确要求使用某个 scenario-id（调试/演示用途）
- 浏览器/网络故障导致无法扫描目标
- 开发者本地调试

### 频道与目标策略

- 不做固定频道硬编码；频道可变且应随会话上下文切换。
- 未显式指定通知目标时，沿用脚本默认"最近活跃会话自动推断"能力。

### 汇报口径

- 一旦命中执行意图，先回"已开始执行 + 本次 run 参数摘要"，随后立即落地执行。
- 执行完成后再返回报告路径与结论，不把"执行前计划说明"作为前置阻塞。

常用参数：

- `--scenario <path>`：直传 scenario JSON 路径（需配合 `--force-direct-scenario-path`）
- `--scenario-id <id>`：从注册表选择场景（仅调试/演示；默认注册表：`demo/scenarios/registry.json`）
- `--scenario-registry <path>`：指定场景注册表路径
- `--scenario-var key=value`：覆盖场景变量（可重复；用于模板场景的 `{{start_url}}/{{start_domain}}` 等占位）
- `--allow-direct-scenario-path`：允许接收 `--scenario <path>` 直传请求（默认关闭；默认会回退注册表默认场景）
- `--force-direct-scenario-path`：强制执行直传路径（智能生成场景时必须开启）
- `--run-id <id>`：手动指定 run id
- `--output-root demo`：输出根目录
- `--allow-external-scenario`：允许执行仓库 `demo/scenarios` 目录外的场景（默认关闭，防误跑）
- `--allow-legacy-scenario`：允许执行 `meta.legacy=true` 的旧场景（默认关闭）
- `--no-trace`：关闭 trace 录制
- `--browser-bin <bin>`：指定 OpenClaw 可执行名（默认 `openclaw`）
- `--browser-cmd "<cmd>"`：指定完整命令前缀（例如 `pnpm --dir src openclaw`）
- `--max-step-retries <n>`：每步默认重试次数（默认 `1`）
- `--retry-wait-ms <ms>`：重试间隔（默认 `800`）
- `--showcase-recheck`：启用复核执行并与主执行结果对照（默认开启）
- `--showcase-continue-on-failure`：复核执行遇到差异后是否继续（默认开启）
- `--showcase-max-step-retries <n>`：复核执行默认重试次数（默认 `0`）
- `--showcase-retry-wait-ms <ms>`：复核执行重试间隔（默认 `500`）
- `--showcase-time-budget-ms <ms>`：复核执行时间预算（默认 `90000`，超时即提前收口并继续产出最终报告）
- `--resume-from-step-id <stepId>`：从指定步骤开始续跑
- `--resume-from-run-id <runId>`：从某次历史失败 run 的首个失败步骤续跑
- `--resume-last-failed`：从同一场景最近一次失败 run 自动续跑
- `--health-check-interval <off|on-failure|each-step>`：健康检查频率（默认 `on-failure`）
- `--trace-start-mode <auto|immediate|after-first-step>`：trace 启动时机（默认 `auto`）
- `--notify-channel <channel>`：自动发送报告截图到指定频道（支持 `discord/.../auto/current`，不依赖固定频道名）
- `--notify-target <target>`：频道目标（不传则自动推断最近会话目标）
- `--notify-account <id>`：可选 accountId
- `--notify-message <text>`：可选通知文案
- `--notify-auto-current-channel`：未显式指定频道/目标时，自动发到最近活跃会话（默认开启）
- `--notify-max-session-age-ms <ms>`：自动推断会话的最大"最近活跃时间"（默认 30 分钟）
- `--cleanup-orphan-openclaw-processes`：运行前自动清理多余 OpenClaw 专用 Chrome 进程（默认开启）

最终形态执行约束（当前实现）：

- Analysis Pass：无视觉、全量执行、深度固定 `3`；默认"失败优先截图"（`analysisAutoScreenshot=false`），保留 `console/network/trace` 全量采证。
- Showcase Pass：只跑 Analysis 产出的主链路 + 失败链路，并按 trace 对齐复核。
- Showcase Pass 中若场景步骤是 `open`，复核执行自动改为同 tab `navigate`，避免额外新开 tab。
- 若两次执行不一致：报告标注 `needs_inspection`，不阻塞本轮交付。
- 若 Showcase 触发时间预算：标注 `partial_timeout`，并继续生成 `report.html/report_full.png` 与回传。

执行超时建议（重要）：

- 从外层 `exec` 调脚本时，必须设置 `timeout >= 900` 秒。
- 300 秒在"analysis + showcase + trace + 通知"组合下容易被外层提前杀掉，导致看起来"截图回传丢失"。

## 次佳演示模式（同机不抢主画面）

你关心的"炫酷演示 + 不打断主画面工作"建议这样跑：

```bash
python3 src/skills/auto-qa/scripts/run_autoqa.py \
  --scenario-id wehub_demo \
  --browser-profile openclaw \
  --auto-start-browser \
  --max-step-retries 1 \
  --health-check-interval on-failure
```

说明：

- 该模式可在同一台机器运行，不要求你一直把测试窗口放在主画面。
- 但若你手动频繁干预同一浏览器窗口，仍会增加波动；重试与健康检查用于兜底并在报告中标注风险归因。
- 在 `trace-start-mode=auto` 下，若首步是 `open/navigate`，trace 会延后到第一步后启动，减少 `about:blank` 首屏干扰。
- 默认会生成报告全页截图（`report_full.png`，兼容名 `report_screenshot.png`）。
- 默认会尝试把截图和结论自动发到最近活跃的当前会话频道（可用 `--no-notify-auto-current-channel` 关闭）。

## 可视化演示场景（新增）

- 文件：`/Users/chikakochou/OpenClaw/demo/scenarios/wehub_visual_demo.json`
- 特点：包含"首屏截图 -> 下翻 -> 下翻后截图 -> 点击跳转同域目标页 -> 返回首页"的强可视化动作链，适合 CTO 演示。
- 场景 ID：`wehub_demo`（演示门禁配置，已忽略已知 `index.css` 404 噪音）
- 严格门禁 ID：`wehub_release`（发布判定，不忽略已知 4xx）

运行示例（含自动发当前 Discord 频道）：

```bash
python3 src/skills/auto-qa/scripts/run_autoqa.py \
  --scenario-id wehub_demo \
  --browser-profile openclaw \
  --auto-start-browser
```

## 泛用模板场景（仅调试/演示用）

- 文件：`/Users/chikakochou/OpenClaw/demo/scenarios/generic_visual_template.json`
- 场景 ID：`generic_template`
- 模板内置变量占位：
  - `{{start_url}}`
  - `{{start_domain}}`
- **注意**：正常流程应使用智能生成（优先级 1/2），此模板仅在极端后备或调试时使用。
- 示例：

```bash
python3 src/skills/auto-qa/scripts/run_autoqa.py \
  --scenario-id generic_template \
  --scenario-var start_url=http://wehub.us/ \
  --scenario-var start_domain=wehub.us \
  --browser-profile openclaw \
  --auto-start-browser
```

## 失败到修复闭环

- 失败时自动生成 `fix_plan.json`：
  - 问题摘要
  - 高概率根因（含置信度）
  - 检查方向
  - 修改方向
  - 验收标准
  - 回滚条件
- 自动生成 `next_window_prompt.md`：可直接贴到下一窗口执行
- 自动生成 `standby_prompt.txt`：一句确认即可启动修复流程

## 最近验证样例（2026-02-20）

- runId：`wehub-gate-sample-20260220-v2`
- 报告路径：
  - `/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-gate-sample-20260220-v2/report.json`
  - `/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-gate-sample-20260220-v2/report.html`
- 结果摘要：
  - `releaseDecision = NO_GO`
  - `riskLevel = high`
  - 门禁违规命中：console error、同域 network 404

## Trace 修复记录（2026-02-21）

- 修复范围：`openclaw browser trace start/stop` 在嵌套子命令下丢失 `--browser-profile` 参数的问题。
- 根因：CLI 只读取了一层父命令选项，导致 trace 子命令回退到默认 profile（通常是 `chrome`）。
- 修复后验证：
  - `trace start/stop` 在 `--browser-profile openclaw` 下可正常生成 trace。
  - AutoQA run `wehub-trace-fix-20260221-v1` 已验证 `tracePath` 存在且报告无 trace warning。

## 工程注意事项

- 若 `openclaw browser` 无法连接，请先启动 OpenClaw 网关/浏览器服务。
- `click/type` 依赖快照 `ref`，场景需要提供稳定 `ref` 或结合 `wait/evaluate` 先定位。
- 一期先保证可执行和可追溯，不在本阶段引入跨浏览器矩阵和全量性能压测。
