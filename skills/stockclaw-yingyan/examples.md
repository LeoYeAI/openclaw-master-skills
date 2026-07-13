# Examples

## 0. `openclawCredentials`：从 config.json 读取与持久化

`config.json` → `openclawCredentials` 含 **`user_id`**、**`openClaw_api_key`**、**`monitor_api_key`**。

- **`user_id` + `openClaw_api_key`**：**必填**，用于所有需鉴权的 **HTTP** 接口（请求里参数名仍为 `apikey`，取值用 `openClaw_api_key`）。
- **`monitor_api_key`**：**选填**；仅 **WebSocket 实时监控** 需要。不需要监控可留空。

场景：用户想用量化图、行情、搜股、涨停等，但对话里未粘贴凭证。

OpenClaw 应：
1. **先读** `openclawCredentials.user_id` 与 `openClaw_api_key`；二者均有效则用于 HTTP，**不要**重复询问。
2. 若用户本轮提供了新值：合并后**写回** `config.json`（保留其他键）。
3. 仍缺 **`user_id` 或 `openClaw_api_key`** 时，提示补充（见 SKILL.md 必填提示）；**不要**要求用户必须填 `monitor_api_key`，除非用户要连监控。

示例提示（仅缺必填项时）：

```text
继续之前需要配置 user_id 与 openClaw_api_key（HTTP 请求里的 apikey 填后者）。

获取：鹰眼量化「用户中心」→「开放 API」https://yingyan.chatface.com/

保存到本 Skill 的 config.json（openclawCredentials）后可自动沿用。
```

## 0b. 用户要修改或更换凭证

场景：用户说换 Key、换账号、粘贴新的 12 位 Key 等。

处理：
1. 用新值覆盖 `user_id` / `openClaw_api_key` / `monitor_api_key` 中用户明确要改的项，其余保留 config 原值。
2. 可选：用 `user_id` + `openClaw_api_key` 调用 `POST /api/openclaw/stock/message` 做 HTTP 侧验证。
3. **写回** `openclawCredentials` 到 `config.json`。
4. 告知已保存；配置有效时勿重复索要。

用户**手动编辑** `config.json` 后：下次执行**必须先读文件**，以文件为准。

## 1. 用户发送自然语言选股条件

请求：

```http
POST /api/openclaw/stock/query
Content-Type: application/json

{
  "query": "涨幅超过8%的半导体股票，按换手率从高到低排序，取前20只",
  "user_id": "68b26718213929ab1d78aae5",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=stock_query`
- 最多返回 20 条股票记录
- 只返回固定字段，不返回网页端那种大字段全集
- 适合在 OpenClaw 对话中直接渲染成精简表格

## 2. 用户只发股票代码

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "000001",
  "user_id": "68b267182139",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=chart`
- 读取 `render_markdown`
- 将量化图 markdown 直接渲染到聊天界面

## 3. 用户只发股票名称

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安银行",
  "user_id": "68b26718213929",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=chart`
- 读取 `render_markdown`

## 4. 用户发送"股票+行情"

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安银行行情",
  "user_id": "68b267182139",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=market_query`
- 返回 `stock_context`（TDX 截面数据结构化信息）
- 返回 `system_prompt` 和 `user_prompt`
- OpenClaw 大模型使用 `system_prompt` 作为系统角色、`user_prompt` 作为用户消息，生成趋势诊断并返回给用户

## 5. 股票匹配到多个候选

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安行情",
  "user_id": "68b267182139",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `ok=false`
- `error.code=multiple`
- 提示用户从 `error.candidates` 中选择更精确的股票

## 6. 获取实时监控接入信息

请求：

```http
GET /api/openclaw/stock/monitor/stream?user_id=68b2671
```

预期：
- 返回 `ws_url_template`
- 将模板中 **`apikey` 占位** 填为 **`monitor_api_key`**（监控信号 Key），`user_id` 填真实 ID，再连 WebSocket

## 7. 建立 WebSocket 实时监控连接

连接地址（由 `ws_url_template` 拼接，**URL 中 apikey = monitor_api_key**）：

```text
wss://yingyan.chatface.com/ws/monitor/open?apikey=YOUR_MONITOR_12_CHAR_KEY&user_id=68b2671825
```

预期：
- 连接成功后持续接收 JSON 数组格式的监控信号推送
- 每条推送包含 `ticker`、`name`、`prev_rating`、`latest_rating`、`close`、`zhangdie`、`latest_time`
- 连接断开后可自动重连

补充说明：
- 建议直接使用原生 WebSocket 客户端连接，不要默认先安装 `wscat`、`websocat`。
- 连接建立后如果暂时没有消息，属于正常现象；服务端不会先发送欢迎包。
- 只有监控信号发生有效变化时才会推送；若最新评级变为 `await`，不会推送。

## 8. OpenClaw 配置实时监控的推荐流程

步骤 1：先验证凭证

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "000001",
  "user_id": "68b26718213929ab1d78aae5",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

预期：
- 返回 `ok=true`
- 说明 `user_id` 与 **OpenClaw** Key（请求字段 `apikey`）对消息接口鉴权有效

如果缺 **`user_id` 或 `openClaw_api_key`**：
- 不要继续走步骤 2 和步骤 3
- 先按 SKILL.md 补全必填项

若用户要连监控但缺 **`monitor_api_key`**：
- 提示到「开放 API」保存**监控信号** Key，勿用 OpenClaw Key 顶替

步骤 2：获取监控流模板

```http
GET /api/openclaw/stock/monitor/stream?user_id=68b26718213929ab1d78aae5
```

预期：
- 返回 `ws_url_template`
- 模板类似 `wss://.../ws/monitor/open?apikey={apikey}&user_id={user_id}`，其中 `{apikey}` 替换为 **`monitor_api_key`**

步骤 3：直接建立 WebSocket 连接

```text
wss://yingyan.chatface.com/ws/monitor/open?apikey=YOUR_MONITOR_12_CHAR_KEY&user_id=68b26718213929ab1d78aae5
```

预期：
- WebSocket 握手成功即表示连接成功
- 若连接后暂无消息，不应判定为失败
- 应向用户说明："连接正常，当前正在等待实时监控信号变化"

## 9. WebSocket 成功但没有立即收到消息

现象：
- 连接已经建立
- 一段时间内没有收到任何 JSON 消息

正确结论：
- 这是正常现象，不代表连接失败
- 服务端只在监控信号变化时推送
- 当评级变为 `await` 时不会推送

错误做法：
- 因为短时间没有消息，就反复改用 `wscat`、`websocat`、`curl` 等工具
- 把"连接后暂无消息"误判成"WebSocket 不可用"

## 10. OpenClaw 自然语言搜股与网页端选股的区别

网页端：
- 页面：`web/query/queryFundamentals.html`
- 接口：`POST /api/query/tdx`
- 返回可能较多列，偏完整分析表

OpenClaw：
- 接口：`POST /api/openclaw/stock/query`
- 最多只返回 20 只
- 只返回以下字段：
  - `代码`
  - `名称`
  - `涨幅%`
  - `现价`
  - `涨跌`
  - `换手%`
  - `细分行业`
  - `活跃度`
  - `连涨天`
  - `昨涨幅%`
  - `3日涨幅%`
  - `5日涨幅%`
  - `10日涨幅%`
  - `20日涨幅%`
  - `60日涨幅%`
  - `一年涨幅%`
  - `月初至今%`
  - `年初至今%`
  - `近日指标提示`

## 11. 健康检查

请求：

```http
GET /api/openclaw/health
```

预期：
- 返回 `service`、`endpoints`、`demo_page`
- 可用于平台接入前自检

## 12. 打开 demo 页面

地址：

```text
https://yingyan.chatface.com/web/openclaw_demo.html
```

预期：
- 可直接点按测试健康检查、消息入口、WebSocket 实时监控
