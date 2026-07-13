# API Reference

## 企业微信专用接口（`/api/wecom`）

企业微信 API 插件鉴权方式与 OpenClaw 不同，需使用 Header/Query 传递 `X-API-Key` 与 `userid`。详见 `job/wechat_enterprise/README.md`。

- `GET /api/wecom/health`：健康检查
- `POST /api/wecom/stock/message`：股票消息（Header: `X-API-Key`, `X-User-Id`；Body: `message` / `query` / `content`）
- `POST /api/wecom/stock/query`：自然语言搜股（Header: `X-API-Key`, `X-User-Id`；Body: `message` / `query` / `content`）
- `GET /api/wecom/stock/limit-up`：涨停股专用查询（Header/Query: `X-API-Key`, `X-User-Id` / `userid`）
- `GET /api/wecom/stock/monitor/stream`：实时监控流模板（Header/Query: `X-API-Key`, `X-User-Id` / `userid`）

---

## `GET /api/openclaw/health`

用于健康检查与快速发现接口入口。

### 响应示例

```json
{
  "ok": true,
  "service": "stockClaw-yingyan",
  "platform_hint": "ClawHub",
  "base_url": "https://yingyan.chatface.com",
  "endpoints": {
    "message": "https://yingyan.chatface.com/api/openclaw/stock/message"
  },
  "demo_page": "https://yingyan.chatface.com/web/openclaw_demo.html"
}
```

## `POST /api/openclaw/stock/message`

统一入口，根据用户消息自动判断是生成量化图还是返回行情数据。

### 请求体

```json
{
  "message": "000001",
  "user_id": "your_user_id",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY",
  "start_date": "2025-03-01",
  "end_date": "2026-03-01",
  "initial_capital": 1000000
}
```

### 识别规则
- 仅股票名称或股票代码：`intent=chart`
- 包含"行情"关键词：`intent=market_query`
- 其他输入：`ok=false` 且 `error.code=invalid_message`

### 鉴权要求
- 必须传 `user_id`
- 必须传 `apikey`（**HTTP 参数名**；取值须为会员中心 **OpenClaw** 卡片保存的 12 位 Key，即 `config.json` 的 `openclawCredentials.openClaw_api_key`）
- 图表服务已使用 `Agg` 后端，适合服务端无界面部署

### 缺失 `user_id` 或 OpenClaw Key 时
- OpenClaw 不应在缺少 `user_id` 或有效 **`openClaw_api_key`**（请求里仍放在字段 `apikey`）的情况下直接请求本接口。
- **优先**从本 Skill 同目录 `config.json` 的 `openclawCredentials` 读取 `user_id`、`openClaw_api_key`；二者均有效则用于请求体中的 `user_id` 与 `apikey`。
- **监控 WebSocket** 使用另一字段 `monitor_api_key`，见下文 monitor/stream 与 SKILL.md；不需要监控可不配置 `monitor_api_key`。
- 用户在本轮对话中提供或更新凭证时，将最终值**写回** `openclawCredentials`，保留文件内其他键。
- 获取路径：鹰眼量化「用户中心」→「开放 API」`https://yingyan.chatface.com/`

建议提示文案（缺必填项时）：

```text
继续之前需要 user_id 与 openClaw_api_key（请求里 apikey 填该值）。
在鹰眼量化「用户中心」→「开放 API」获取；提供后写入 config.json 的 openclawCredentials。
```

### 用户修改凭证
- **对话**：用户粘贴新 Key/`user_id` 时，用新值调用接口并写回 `openclawCredentials`（含 `openClaw_api_key`、`monitor_api_key` 等被更新的字段）。
- **文件**：用户直接编辑 `config.json` 后，OpenClaw 须以文件为准读取。
- **禁止**：`user_id` 与 `openClaw_api_key` 已有效时，不得无故重复索要。

### 成功响应示例：量化图

```json
{
  "ok": true,
  "intent": "chart",
  "message": "平安银行",
  "stock_query": "平安银行",
  "image_url": "https://yingyan.chatface.com/chart_img/abcd1234.png",
  "image_path": "/chart_img/abcd1234.png",
  "render_markdown": "## 量化图\n- 标的：`平安银行`\n- 图片地址：https://yingyan.chatface.com/chart_img/abcd1234.png\n\n![平安银行 量化图](https://yingyan.chatface.com/chart_img/abcd1234.png)"
}
```

### 成功响应示例：行情问答

```json
{
  "ok": true,
  "intent": "market_query",
  "message": "平安银行行情",
  "stock_query": "平安银行",
  "stock": {
    "code": "000001",
    "name": "平安银行",
    "industry": "银行",
    "region": "深圳"
  },
  "stock_context": {
    "identity": { "code": "000001", "name": "平安银行", "industry": "银行", "region": "深圳" },
    "evaluation": {
      "short_bias": "震荡",
      "medium_bias": "偏强",
      "confidence": "中",
      "short_score": 2,
      "medium_score": 3,
      "usable_signal_count": 14,
      "conflicts": []
    },
    "snapshot_lines": ["现价：12.50", "当日涨幅：0.80%", "..."],
    "short_term_lines": ["当日涨幅：0.80%", "量比：1.2，量能暂无明显失真。", "..."],
    "medium_term_lines": ["中期区间表现：20日涨幅%：5.2%，60日涨幅%：12.1%，...", "..."],
    "capital_and_fundamental_lines": ["主力资金：净额 1200万，净比 0.5%。", "..."],
    "risk_flags": ["当前未见极端透支信号，但仍需继续观察量能与资金承接能否延续。"]
  },
  "system_prompt": "你是一个只基于给定 TDX 股票字段和规则摘要进行推理的 A 股趋势诊断器...",
  "user_prompt": "请基于下面这份结构化股票诊断信息完成趋势判断。\n\n【诊断对象】\n- 股票：平安银行（000001）\n..."
}
```

行情问答返回的 `system_prompt` 和 `user_prompt` 由 OpenClaw 大模型直接使用来生成趋势诊断，API 本身不调用大模型，避免超时。

### 失败响应示例

```json
{
  "ok": false,
  "intent": "market_query",
  "message": "平安行情",
  "stock_query": "平安",
  "error": {
    "code": "multiple",
    "message": "找到多个与"平安"相关的股票，请输入更完整的代码或名称。",
    "candidates": [
      {
        "code": "000001",
        "name": "平安银行"
      }
    ]
  }
}
```

### 常见错误码
- `invalid_message`
- `apikey 校验失败`
- `chart_generation_failed`
- `multiple`
- `not_found`
- `data_missing`
- `missing_api_key`
- `insufficient_balance`

## `POST /api/openclaw/stock/query`

OpenClaw 专用的自然语言 AI 搜股接口。它参考 `web/query/queryFundamentals.html` 的自然语言理解逻辑，但**不复用**网页端的 `POST /api/query/tdx` 接口。

设计目标：
- 面向 OpenClaw 的对话式选股
- 只返回轻量结果
- 最多返回 20 只股票
- 固定字段集合，避免返回超大表

### 请求体

```json
{
  "query": "涨幅超过8%的半导体股票，按换手率从高到低排序，取前20只",
  "user_id": "your_user_id",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

### 意图说明
- 适用于用户使用自然语言描述选股条件，而不是指定单只股票。
- 支持筛选、排序、区间、排除、前 N 名等表达。
- 典型示例：
  - `涨幅超过10%的股票`
  - `换手率高的科技股`
  - `近20日涨幅靠前的深圳股票`
  - `剔除ST和北交所，取活跃度前20`

### 与网页端自然语言选股的区别
- 网页端入口：`web/query/queryFundamentals.html`
- 网页端接口：`POST /api/query/tdx`
- OpenClaw 不直接调用该接口，而是调用本专用接口
- OpenClaw 版本只返回固定字段、最多 20 条，适合聊天场景快速展示

### 返回字段限制
成功响应中的 `data` 每条记录仅允许包含以下字段：
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

### 成功响应示例

```json
{
  "ok": true,
  "intent": "stock_query",
  "query": "涨幅超过8%的半导体股票，按换手率从高到低排序，取前20只",
  "total": 2,
  "limit": 20,
  "fields": [
    "代码",
    "名称",
    "涨幅%",
    "现价",
    "涨跌",
    "换手%",
    "细分行业",
    "活跃度",
    "连涨天",
    "昨涨幅%",
    "3日涨幅%",
    "5日涨幅%",
    "10日涨幅%",
    "20日涨幅%",
    "60日涨幅%",
    "一年涨幅%",
    "月初至今%",
    "年初至今%",
    "近日指标提示"
  ],
  "data": [
    {
      "代码": "688001",
      "名称": "示例科技",
      "涨幅%": "9.21",
      "现价": "32.55",
      "涨跌": "2.75",
      "换手%": "7.88",
      "细分行业": "半导体",
      "活跃度": "82",
      "连涨天": "3",
      "昨涨幅%": "2.18",
      "3日涨幅%": "12.40",
      "5日涨幅%": "15.62",
      "10日涨幅%": "21.88",
      "20日涨幅%": "29.33",
      "60日涨幅%": "48.10",
      "一年涨幅%": "66.50",
      "月初至今%": "13.20",
      "年初至今%": "24.80",
      "近日指标提示": "放量上攻"
    }
  ]
}
```

### 失败响应示例

```json
{
  "ok": false,
  "intent": "stock_query",
  "query": "帮我找一些不错的票",
  "error": {
    "code": "invalid_query",
    "message": "未识别出明确的自然语言选股条件，请补充筛选条件、排序方式或目标范围。"
  }
}
```

### 建议错误码
- `invalid_query`
- `apikey 校验失败`
- `missing_api_key`
- `insufficient_balance`
- `stock_query_failed`

## `GET /api/openclaw/stock/limit-up`

OpenClaw 专用的涨停股查询接口。适用于用户明确询问"今天涨停股有哪些"、"涨停股票列表"等场景。

### 请求参数
- `user_id`：必填
- `apikey`：必填，12 位 **OpenClaw** API Key（与监控 Key 不同）

### 请求示例

```text
GET /api/openclaw/stock/limit-up?user_id=your_user_id&apikey=YOUR_OPENCLAW_12_CHAR_KEY
```

### 识别规则
- 该接口不是通用自然语言搜股，而是涨停股专用通道
- 当用户明确提到"涨停股"、"今日涨停股票"、"今天有哪些涨停股"时，应优先调用本接口
- 不要误走 `POST /api/openclaw/stock/query`

### 识别逻辑
- 主板/中小板：约 `9.9%`
- 创业板/科创板：约 `19.9%`
- 北交所：约 `29.9%`
- `ST`：约 `4.9%`

### 返回字段
成功响应中的 `data` 每条记录仅包含以下字段：
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

### 成功响应示例

```json
{
  "ok": true,
  "intent": "limit_up",
  "total": 2,
  "fields": [
    "代码",
    "名称",
    "涨幅%",
    "现价",
    "涨跌",
    "换手%",
    "细分行业",
    "活跃度",
    "连涨天",
    "昨涨幅%",
    "3日涨幅%",
    "5日涨幅%",
    "10日涨幅%",
    "20日涨幅%",
    "60日涨幅%",
    "一年涨幅%",
    "月初至今%",
    "年初至今%",
    "近日指标提示"
  ],
  "data": [
    {
      "代码": "000001",
      "名称": "示例股票",
      "涨幅%": "10.02",
      "现价": "12.50",
      "涨跌": "1.14",
      "换手%": "6.35",
      "细分行业": "银行",
      "活跃度": "71",
      "连涨天": "2",
      "昨涨幅%": "2.18",
      "3日涨幅%": "12.40",
      "5日涨幅%": "15.62",
      "10日涨幅%": "21.88",
      "20日涨幅%": "29.33",
      "60日涨幅%": "48.10",
      "一年涨幅%": "66.50",
      "月初至今%": "13.20",
      "年初至今%": "24.80",
      "近日指标提示": "放量上攻"
    }
  ],
  "filename": "20260306172622.csv",
  "criteria": "按股票代码/名称对应的涨停阈值识别：主板约10%，创业板/科创板约20%，北交所约30%，ST约5%。"
}
```

### 建议错误码
- `apikey 校验失败`
- `data_missing`
- `limit_up_failed`

## `GET /api/openclaw/stock/monitor/stream`

返回 WebSocket 实时监控的连接信息。客户端根据返回的模板地址建立 WebSocket 长连接，即可接收与 `monitor.html` 相同的监控信号广播推送。

### 请求参数
- `user_id`: 选填，仅用于回显

### 响应示例

```json
{
  "ok": true,
  "ws_path": "/ws/monitor/open",
  "ws_url_template": "wss://yingyan.chatface.com/ws/monitor/open?apikey={apikey}&user_id={user_id}",
  "required_query_params": ["apikey", "user_id"],
  "message": "使用 WebSocket 连接接收与 monitor.html 相同的实时监控信号推送。",
  "data_format": {
    "type": "JSON Array",
    "fields": ["ticker", "name", "prev_rating", "latest_rating", "close", "zhangdie", "latest_time"],
    "example": [
      {
        "ticker": "000001",
        "name": "平安银行",
        "prev_rating": "持有",
        "latest_rating": "买入",
        "close": 12.5,
        "zhangdie": 0.02,
        "latest_time": "2026-03-10 10:30:00"
      }
    ]
  }
}
```

将模板中的 `{apikey}` 替换为 **`monitor_api_key`**（会员中心「监控信号」Key）；`{user_id}` 替换为真实用户 ID。不要使用 `openClaw_api_key` 连接监控 WebSocket。

### WebSocket 推送数据格式

连接成功后，服务端会以 JSON 数组形式推送监控信号变化：

```json
[
  {
    "ticker": "000001",
    "name": "平安银行",
    "prev_rating": "持有",
    "latest_rating": "买入",
    "close": 12.5,
    "zhangdie": 0.02,
    "latest_time": "2026-03-10 10:30:00"
  }
]
```

字段说明：
- `ticker`：股票代码
- `name`：股票名称
- `prev_rating`：原评级（如 持有、买入、卖出、await）
- `latest_rating`：新评级（不会出现 `await`，见下方过滤规则）
- `close`：最新价
- `zhangdie`：涨跌幅比例（0.02 = 2%）
- `latest_time`：信号时间

### 信号过滤规则
- 当评级变为 `await`（等待）时，**服务端不推送通知**
- 仅当 `latest_rating` 为具有实际买卖意义的信号（如 买入、卖出、持有 等）且与 `prev_rating` 不同时才会推送
- 因此收到的每条推送都代表一个有效的买卖信号变化

### 鉴权说明
- WebSocket 连接需在 URL 中携带 `apikey` 和 `user_id`
- URL 中的 `apikey` 必须与会员中心 **「监控信号」** 卡片保存的 12 位 Key 一致（即 `config.json` 的 `monitor_api_key`）
- 连接建立后无需额外认证，服务端持续推送至连接断开

### OpenClaw 推荐接入方式
- 推荐顺序：先校验凭证可用，再读取 `ws_url_template`，最后直接使用原生 WebSocket 客户端连接。
- 推荐先用 `POST /api/openclaw/stock/message` 做一次轻量验证，避免把鉴权失败误判为 WebSocket 异常。
- 不建议把安装 `wscat`、`websocat` 或其他命令行客户端作为默认步骤；它们只适合人工排障，不适合作为技能默认工作流。
- 浏览器或平台原生 WebSocket 客户端连接成功后，即可视为实时监控已配置完成。
- 连接监控前若缺 `user_id` 或 **监控** Key（`monitor_api_key`），应提示用户到「开放 API」保存监控信号 Key；不要直接尝试连接。不需要监控的用户可不配置 `monitor_api_key`。

### 成功判定
- WebSocket 握手成功，连接处于打开状态，即为成功。
- 连接成功后短时间内没有消息，**仍然是成功状态**。
- 原因是服务端不会发送欢迎消息；只有监控信号发生变化时才会推送数据。
- 若当前变化后的评级为 `await`，服务端也不会推送通知。

### 失败判定与常见原因
- 若连接被服务端立即关闭，优先检查 **监控** `apikey`（`monitor_api_key`）、`user_id`、会员状态和权限等级。
- 常见策略拒绝关闭码为 `1008`，通常表示鉴权失败、会员未激活，或等级不足以访问 `monitor.html` 对应资源。
- 监控 URL 中的 `apikey` 须与会员中心「监控信号」保存值完全一致（12 位字母或数字）。
- 如果只做了健康检查 `GET /api/openclaw/health`，并不能证明 WebSocket 鉴权一定通过。

### 建议给用户的说明话术
- "WebSocket 连接已建立，当前正在等待实时监控信号。"
- "暂时没有收到推送是正常现象，服务端只在评级发生有效变化时推送。"
- "如果后续出现买入/卖出/持有等有效信号切换，你会立即收到 JSON 数组格式的推送数据。"

## ClawHub 导入文件

- `manifest.json`
- `config.json`
- `CLAWHUB_UPLOAD.md`
- `openapi.json`

Demo 页面：
- `/web/openclaw_demo.html`

补充说明：
- ClawHub 上传页当前可见的是网页表单字段与文件夹上传，不是公开的标准 manifest schema
- 可直接参考 `CLAWHUB_UPLOAD.md` 中对应上传页字段的填写建议
