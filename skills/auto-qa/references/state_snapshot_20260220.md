# AutoQA 状态快照（优化前后）

## 快照时间

- 日期：2026-02-20
- 基线 run：`/Users/chikakochou/.openclaw/workspace/demo/reports/run-20260220T112057Z/report.json`

## 当前可用能力

- 自动执行网页场景步骤（open/wait/snapshot/screenshot/assert 等）
- 自动采证（steps/console/network/screenshots）
- 自动生成报告（report.json/report.html）
- 自动修复提示包（fix_plan.json/next_window_prompt.md/standby_prompt.txt）
- 稳定性增强（重试、断点续跑、健康检查、失败分类）

## 主要问题（待优化）

1. `console.json` 与 `network.json` 当前仅做采证，不做默认门禁断言。
2. 出现同域资源 404（例如 `https://wehub.us/index.css`）时仍可能给出 `GO`。
3. trace 在当前运行环境中存在 profile 路由异常，暂不作为本轮优先修复项。
4. 报告结构仍偏“执行日志摘要”，尚未完全对齐 CTO 决策页结构。

## 本轮优化目标（先聚焦报告）

1. 增加默认门禁断言：

- console `error` -> 违规
- 同域 network `4xx/5xx` -> 违规

2. 报告新增决策字段：

- `gateViolations`
- `riskLevel`
- `releaseDecision`（GO / CONDITIONAL_GO / NO_GO）

3. 产出 1 份示例报告供人工审查。

## 范围约束

- 本轮不优先修 trace。
- 不改动最终交互目标（仍支持 Discord 自然语言触发 OpenClaw 自动运行）。

## 优化后结果（2026-02-20）

- 新增默认门禁断言并已落地到执行器：
  - console `error` -> `critical`
  - 同域 network `4xx` -> `critical`
  - 同域 network `5xx` -> `blocker`
- 报告新增决策字段并已输出：
  - `gateViolations`
  - `gateViolationCountsBySeverity`
  - `riskLevel`
  - `releaseDecision`（GO / CONDITIONAL_GO / NO_GO）
- `fix_plan.json` 已支持“仅门禁违规也产出修复任务”。
- `report.html` 已升级为 CTO 决策视图（结论卡片 + 风险拆解 + 阻断项 + 门禁违规清单）。

### 示例 run（供人工审查）

- runId：`wehub-gate-sample-20260220-v2`
- 报告：
  - `/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-gate-sample-20260220-v2/report.json`
  - `/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-gate-sample-20260220-v2/report.html`
- 关键结论：
  - `releaseDecision = NO_GO`
  - `riskLevel = high`
  - 门禁违规 2 条（console error + 同域 network 404）

## Trace 修复结果（2026-02-21）

- 问题现象：
  - `trace start failed: Chrome extension relay is running, but no tab is connected (profile "chrome")`
  - 即使命令传入 `--browser-profile openclaw`，trace 子命令仍误落到默认 `chrome` profile。
- 根因：
  - CLI 在多级子命令（`browser trace start/stop`）中仅读取一层 `cmd.parent?.opts()`，
    未正确继承 `browser` 根命令上的 `--browser-profile`。
- 修复：
  - 在 `src/cli/browser-cli.ts` 增加父命令链选项合并逻辑，确保嵌套子命令继承 profile/json/gateway 参数。
  - 增加回归测试：`src/cli/browser-cli.test.ts`（nested subcommands case）。
- 验证：
  - `pnpm --dir /Users/chikakochou/OpenClaw/src openclaw browser --browser-profile openclaw --json trace start` 成功。
  - `pnpm --dir /Users/chikakochou/OpenClaw/src openclaw browser --browser-profile openclaw --json trace stop --out /Users/chikakochou/.openclaw/workspace/demo/artifacts/trace-smoke-20260221.zip` 成功。
  - AutoQA 示例 run：`wehub-trace-fix-20260221-v1`
    - 报告：`/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-trace-fix-20260221-v1/report.json`
    - `warnings = []`
    - `evidence.tracePath` 存在且可用。

## Checkpoint（2026-02-21 / 第二轮改进前）

- 已确认当前最新 run（`run-20260221T011057Z`）运行结果符合“步骤通过 + 门禁拦截”预期。
- 已确认 trace 文件完整可解析（`trace.zip` 内含 `trace.trace`/`trace.network`/`resources/*`）。
- 待实现三项改进：
  1. 减少 `about:blank` 首屏干扰（特别是 trace 启动阶段）。
  2. 提供可视化演示场景（可见滚动/点击/跳转）。
  3. 输出步骤与 trace 时间线对齐文件（`step_trace_map.json`）。
- 待实现附加动作：
  - 自动截取 `report.html` 全页图并自动发送到当前聊天频道。

## 第二轮改进落地结果（2026-02-21）

### 已落地能力

1. `trace 启动时机控制`

- 参数：`--trace-start-mode <auto|immediate|after-first-step>`
- 默认 `auto`：首步为 `open/navigate` 时延后启动 trace，减少 `about:blank` 干扰。

2. `步骤-Trace 对齐文件`

- 新增输出：`step_trace_map.json`
- 作用：按步骤时间窗聚合 trace/network 事件，快速完成“步骤 -> 证据”回溯。

3. `报告全页截图 + 频道自动通知`

- 新增输出：`report_full.png`
- 参数：`--notify-channel/--notify-target/--notify-account/--notify-message`
- 规则：仅传 `--notify-channel` 时，自动从 `openclaw status --json` 最近会话推断目标（当前对话频道优先）。

### 实跑验证（当前频道自动发送）

- runId：`wehub-visual-notify-20260221-v1`
- 报告目录：`/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-visual-notify-20260221-v1`
- 关键结果：
  - `report_full.png` 已生成
  - `step_trace_map.json` 已生成（`status = ok`）
  - 通知发送成功：`notification.sent = true`
  - 目标：`channel:1474363113766650043`（来自最近会话推断）

## 第三轮修正（2026-02-21 / 新窗口自动行为对齐）

### 背景问题

- 用户在“最新一轮”观察到频道有截图消息，但 `report.json` 中 `notifications.requested=false`、`reportScreenshotPath=null`，造成“是否自动”的认知冲突。

### 修正内容

1. `报告截图`默认总是生成

- 每次 run 结束后都会尝试生成报告全页图：
  - 主文件：`report_full.png`
  - 兼容文件：`report_screenshot.png`
- 并写入 `report.json`：
  - `evidence.reportScreenshotPath`
  - `evidence.reportScreenshotCompatPath`

2. `当前会话自动发送`默认开启

- 新增默认行为：未显式传 `--notify-channel/--notify-target` 时，也会尝试根据最近会话自动推断频道并发送。
- 推断规则：
  - 从 `openclaw status --json` 的 `sessions.recent` 取最新匹配项
  - 默认只使用 30 分钟内活跃会话（可用参数调整）

3. `显式参数仍优先`

- 传了 `--notify-channel` / `--notify-target` 时优先按显式值发送，不会被自动推断覆盖。
- 可用 `--no-notify-auto-current-channel` 关闭默认自动发送。

### 实跑验证（无 notify 参数）

- runId：`wehub-auto-current-session-20260221-v1`
- 命令特征：未传 `--notify-channel` / `--notify-target`
- 结果：
  - `evidence.reportScreenshotPath` 已写入 `report_full.png`
  - `evidence.reportScreenshotCompatPath` 已写入 `report_screenshot.png`
  - `notifications.requested = true`
  - `notifications.sent = true`
  - `notifications.target = channel:1474363113766650043`

## 第四轮改进（2026-02-21 / 强可视化动作场景）

### 目标

- 解决“前端看不到明显翻页/点击/跳转动作”的观感问题。

### 动作改造

- 将 `wehub_visual_demo.json` 升级为强可视化动作链：
  1. 首页首屏截图
  2. 明显下翻（带断言）
  3. 下翻后截图
  4. 点击并跳转到任一同域目标页（带断言）
  5. 跳转后页面全页截图
  6. 返回首页并结束截图

### 说明

- 场景仍保留门禁检测与证据采集，保证“炫酷动作”与“可决策报告”同时成立。

## Checkpoint（2026-02-21 / 泛化改造前）

- 当前工作区存在一版“动作观感增强草案”，其中跳转步骤使用了 `status` 关键词与 `wehub.us/status` 断言，属于站点特化实现。
- 本轮改造目标：保留“可见动作链”能力，但将跳转逻辑改为“同域通用跳转”，避免对单站点页面结构和文案的硬编码依赖。
- 约束：先完成 checkpoint 提交，再进行场景与文档泛化改造。

## 第五轮结果（2026-02-21 / 泛化动作落地）

### 已落地

- `wehub_visual_demo.json` 改为“同域通用跳转”逻辑：
  - 不再写死 `status` 文案/路径断言；
  - 跳转断言改为“同域且 URL 发生变化”。
- 动作链保持可见：
  - 首屏截图 -> 下翻 -> 下翻后截图 -> 同域跳转 -> 目标页全页截图 -> 返回首页截图。

### 验证 run

- runId：`wehub-visual-generic-20260221-v3`
- 结果：
  - `steps passed = 14/14`
  - 关键步骤通过：`step-007`（同域目标页点击跳转）、`step-009`（同域 URL 变化断言）
  - 报告截图已生成并发送（显式 target）
  - 备注：本次 trace 存在“already running”告警，为环境残留状态，不影响动作链与报告输出。
- 路径：
  - `/Users/chikakochou/.openclaw/workspace/demo/reports/run-wehub-visual-generic-20260221-v3/report.json`
