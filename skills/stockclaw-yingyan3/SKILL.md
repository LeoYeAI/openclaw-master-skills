---
name: stockClaw-yingyan
description: 为该股票量化项目提供 OpenClaw 接入说明，支持股票量化图生成、股票行情问答、自然语言 AI 搜股与 WebSocket 实时监控信号推送。凭证须从与本 Skill 同目录的 config.json 中 openclawCredentials 读取：user_id 与 openClaw_api_key 为必填（用于所有需鉴权的 HTTP 接口，请求体/查询参数中字段名仍为 apikey）；monitor_api_key 为选填，仅 WebSocket 实时监控需要，不订阅监控可不配置。首次配置或用户在对话中修改后写回 config.json；禁止在配置已有效时重复索要；用户也可直接编辑 config.json 修改凭证。
---

# stockClaw-yingyan

## 适用场景
- 用户只发送股票名称或股票代码
- 用户发送"股票名称/股票代码 + 行情"
- 用户发送自然语言选股条件，想搜索某一类股票
- 用户要查询今天有哪些涨停股
- 用户要接收实时监控信号推送

## 输入规则
1. 如果消息只包含股票名称或股票代码，调用 `POST /api/openclaw/stock/message`
2. 如果消息包含"行情"关键词，调用 `POST /api/openclaw/stock/message`
3. 如果消息是自然语言选股条件，调用 `POST /api/openclaw/stock/query`
4. 如果用户明确要查询涨停股股票列表，调用 `GET /api/openclaw/stock/limit-up`
5. 如果要接收实时信号推送，先调用 `GET /api/openclaw/stock/monitor/stream` 获取 WebSocket 连接模板

### 自然语言 AI 搜股意图识别
满足以下特征时，应优先判断为"自然语言 AI 搜股"：
- 用户在描述一类股票，而不是单只股票，例如："涨幅超过 8% 的科技股"、"换手率高的深圳股票"、"近 20 日涨幅靠前的半导体股票"
- 用户带有筛选、排序、区间、排除、前 N 名等表达，例如："大于"、"小于"、"区间"、"按涨幅排序"、"取前 20 只"、"剔除 ST"
- 用户意图是"找股票列表"，而不是生成单只股票量化图，也不是诊断单只股票行情

不要误判为自然语言 AI 搜股的场景：
- 纯股票名称或代码：如 `平安银行`、`000001`
- 明确包含"行情"并指向单只股票诊断：如 `平安银行行情`
- 明确要求查询"涨停股"、"今日涨停股票"、"今天涨停股有哪些"
- 仅要求连接实时监控、订阅监控信号

## 凭证持久化（config.json，必读）

本 Skill 目录下与本文件同级的 `config.json` 中设有对象 **`openclawCredentials`**，包含三个字符串字段：

| 字段 | 是否必填 | 用途 |
|------|----------|------|
| **`user_id`** | **必填** | 所有接口的用户标识 |
| **`openClaw_api_key`** | **必填** | 量化图、行情问答、自然语言搜股、涨停股、`rating-changes-to-await` 等 **HTTP** 鉴权；调用接口时请求体/Query 里参数名仍为 **`apikey`**，取值必须为本字段 |
| **`monitor_api_key`** | **选填** | **仅** WebSocket 实时监控：`/ws/monitor/open?apikey=...` 中的 `apikey` 须填会员中心「监控信号」Key，即本字段。若用户不需要实时监控，**可不设置**（留空字符串即可） |

### 读取顺序（每次调用前执行）

1. **读取** `config.json` 的 `openclawCredentials.user_id`、`openClaw_api_key`、`monitor_api_key`（仅含空格的字符串视为未配置）。
2. **若用户在当轮对话中提供了新凭证**（粘贴 key、更换账号等），以当轮值为准，并**写回** `config.json`（见「写回规则」）。
3. **合并**：文件中的非空值为默认；当轮用户输入覆盖对应字段。
4. **HTTP 能力**（规则 1～4 及 `rating-changes-to-await`）：合并后 **`user_id` 与 `openClaw_api_key` 均须为有效 12 位字母数字**，方可请求；满足后**不得**再索要这两项。
5. **WebSocket 实时监控**（规则 5）：除 `user_id` 外，还须 **`monitor_api_key` 有效**；若用户要连监控但该字段空，**单独提示**其到会员中心「开放API」→「监控信号」保存 Key，**不要**与 OpenClaw Key 混淆。
6. **强约束（防重复索要）**：只要 `user_id` + `openClaw_api_key` 已有效，调用 HTTP 接口时**禁止**以新会话、换话题等理由再次索要；`monitor_api_key` 同理——仅在用户要连 WS 且该字段缺失/无效时再提示。

### 写回规则（持久保存）

- 首次凑齐必填项或用户主动更新任一字段后，将当前合并结果**写回** `config.json` 的 `openclawCredentials`（`user_id`、`openClaw_api_key`、`monitor_api_key` 按需更新），**保留**其余顶层键不变；合法 JSON，勿写多余注释。
- 后续会话**优先读文件**。

### 用户修改凭证

1. **对话中修改**：用户粘贴新 Key 或新 `user_id` 时，覆盖对应字段并写回 `config.json`；未提及的字段保留原 config。
2. **手动编辑 `config.json`**：下次执行须以文件为准，勿因对话未出现而重复索要。

### HTTP 与 URL 中的 `apikey` 名对照（避免搞混）

- **POST/GET 的 JSON 或 Query 参数名**统一叫 **`apikey`**，其值 = 合并后的 **`openClaw_api_key`**。
- **WebSocket** URL 查询参数名也叫 **`apikey`**，其值 = 合并后的 **`monitor_api_key`**（与 HTTP 不是同一把 Key 时两者不同）。

### 仍缺必填凭证时的提示（user_id / openClaw_api_key）

仅在 **`user_id` 或 `openClaw_api_key` 缺失或非法**时提示（与是否使用监控无关）：

```text
使用股票量化图、行情问答、自然语言搜股或涨停查询前，必须配置 user_id 与 openClaw_api_key（均为 12 位 OpenClaw Key 对应会员中心「OpenClaw」卡片）。

获取方式：鹰眼量化网站「用户中心」→「开放API」：https://yingyan.chatface.com/

配置后我会写入本 Skill 的 config.json（openclawCredentials），之后 HTTP 调用无需重复填写。
```

### 仅缺监控 Key 时的提示（要连 WebSocket 时）

当用户明确要求实时监控，但 **`monitor_api_key` 为空或无效**时：

```text
连接实时监控还需要「监控信号」API Key（会员中心「开放API」页面第一个卡片）。若你不需要 WebSocket 推送，可忽略此项。

请配置 monitor_api_key 后写入 config.json，或到上述页面保存监控 Key 后再试连接。
```

### 鉴权失败时

- HTTP 报错多与 **`openClaw_api_key`** 或 `user_id` 不一致有关，请核对会员中心 **OpenClaw** 卡片。
- WebSocket 关闭码 `1008` 等多与 **`monitor_api_key`**、会员等级或 `monitor.html` 权限有关，请核对 **监控信号** Key 与权限。

## 调用约定
（以下请求体中的 **`apikey`** 取值均为合并后的 **`openClaw_api_key`**，字段名与 HTTP API 一致。）

### 1. 量化图
请求：

```json
{
  "message": "平安银行",
  "user_id": "your_user_id",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

处理规则：
- `intent=chart`：返回量化图 URL
- `ok=false`：读取 `error.code` 与 `error.message`

### 2. 行情问答
请求：

```json
{
  "message": "平安银行行情",
  "user_id": "your_user_id",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

处理规则：
- `intent=market_query`：返回结构化 TDX 截面数据、`system_prompt`、`user_prompt`
- 收到响应后，**你（OpenClaw 大模型）必须使用返回的 `system_prompt` 和 `user_prompt` 来生成趋势诊断**
- `ok=false`：读取 `error.code` 与 `error.message`

### 3. 自然语言 AI 搜股
请求：

```json
{
  "query": "涨幅超过8%的半导体股票，按换手率从高到低排序，取前20只",
  "user_id": "your_user_id",
  "apikey": "YOUR_OPENCLAW_12_CHAR_KEY"
}
```

处理规则：
- 调用 `POST /api/openclaw/stock/query`
- 该能力参考 `web/query/queryFundamentals.html` 的自然语言理解思路，但**不要复用**网页端 `POST /api/query/tdx` 接口
- OpenClaw 场景只返回轻量结果，**最多 20 只**
- 返回结果仅允许包含以下字段：
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
- OpenClaw 应直接把结构化股票列表返回给用户；如果接口同时返回摘要字段，可优先使用摘要，再附表格结果
- `ok=false`：读取 `error.code` 与 `error.message`

### 4. 涨停股专用查询
请求：

```text
GET /api/openclaw/stock/limit-up?user_id=your_user_id&apikey=YOUR_OPENCLAW_12_CHAR_KEY
```

处理规则：
- 当用户明确要查"今天涨停股有哪些"、"涨停股票列表"时，优先调用该专用接口
- 不要把这类请求误走通用自然语言搜股 `POST /api/openclaw/stock/query`
- 该接口按股票代码和名称对应的涨停阈值识别结果：主板约 10%，创业板/科创板约 20%，北交所约 30%，ST 约 5%
- 返回结果为结构化股票列表，可直接展示给用户

### 5. WebSocket 实时监控
请求：

```text
GET /api/openclaw/stock/monitor/stream?user_id=your_user_id
```

处理规则：
- 返回 `ws_url_template`，模板中查询参数名为 `apikey`、`user_id`（占位符可能写作 `{apikey}` 与 `{user_id}`）
- **URL 中的 `apikey` 必须填入 `monitor_api_key`**（监控信号 Key），**不要**填 `openClaw_api_key`
- `user_id` 填合并后的用户 ID
- 连接地址示例：`wss://yingyan.chatface.com/ws/monitor/open?apikey=<monitor_api_key>&user_id=<user_id>`
- 连接成功后将持续接收监控信号变化推送（JSON 数组格式）
- 每条推送包含：`ticker`（代码）、`name`（名称）、`prev_rating`（原评级）、`latest_rating`（新评级）、`close`（现价）、`zhangdie`（涨跌幅比例）、`latest_time`（时间）
- **信号过滤**：当评级变为 `await`（等待）时，服务端不会推送通知，仅推送有实际买卖意义的信号变化

### 6. OpenClaw 自然语言 AI 搜股的执行要求
- 若用户输入明显是选股条件，应调用 `POST /api/openclaw/stock/query`，不要误走单股量化图或单股行情诊断。
- 搜股接口返回的是股票列表，不是自由发挥的分析长文；应以结构化结果为主。
- 默认最多返回 20 只股票；即使用户要求更多，也应以接口上限为准。
- 不要自行扩充返回字段，严格使用接口定义的固定字段集合。
- 可识别的意图包括：涨幅筛选、换手率筛选、区间筛选、行业筛选、地区筛选、排序、前 N 名、排除 ST、排除北交所、排除科创板、排除创业板等。
- 如果用户明确要的是"涨停股列表"，应改走涨停股专用接口，而不是通用搜股接口。

### 7. OpenClaw 连接实时监控的推荐执行顺序
当用户要求"连接实时监控"、"配置 WebSocket 监控"、"接收实时监控信号"时，OpenClaw 应按以下顺序执行：

1. 确认合并后的 **`user_id`、`monitor_api_key` 均有效**；若缺 `monitor_api_key`，使用上文「仅缺监控 Key 时的提示」，**不要**用 `openClaw_api_key` 冒充监控 Key。
2. （可选）用 `user_id` + **`openClaw_api_key`** 调用一次 `POST /api/openclaw/stock/message` 验证 HTTP 凭证；此步**不能**代替监控 Key 校验。
3. 调用 `GET /api/openclaw/stock/monitor/stream` 获取 `ws_url_template`。
4. 将模板中 **`apikey` 占位替换为 `monitor_api_key`**，`user_id` 占位替换为真实 `user_id`，再建立 WebSocket。
5. **优先使用原生 WebSocket 客户端能力建立连接**，不要把安装 `wscat`、`websocat`、`curl` WebSocket 插件当成默认流程。
6. WebSocket `onopen` 或等价握手成功后，就应判定为"实时监控连接成功"。
7. 连接成功后保持等待；如果暂时没有收到任何消息，不能据此判定失败。

### 8. OpenClaw 在实时监控场景下的强约束
- 不要默认先尝试安装或调用 `wscat`、`websocat`、`curl` 特殊模式；这些只可作为人工排障兜底方案，不是首选接入路径。
- 若平台本身支持 WebSocket 客户端，应直接连接 `ws_url_template` 替换后的正式地址。
- 服务端**不会**在连接建立后主动发送欢迎包、首包或心跳说明；连接后暂时沉默是正常现象。
- 只有监控信号发生变化时，服务端才会推送 JSON 数组消息。
- 当最新评级变为 `await` 时，服务端不会推送，所以"已连接但暂时无消息"通常代表当前没有有效买卖信号变化。
- 如果连接被关闭且关闭码为策略拒绝（常见为 `1008`），应优先检查：**`monitor_api_key`** 是否与会员中心「监控信号」Key 一致、`user_id` 是否正确、会员状态是否有效、会员等级是否满足 `monitor.html` 权限要求（不要用 OpenClaw Key 连监控 WS）。

### 9. 连接成功后的用户反馈要求
- 一旦握手成功，应明确告诉用户："WebSocket 连接已成功建立，当前正在等待实时监控信号。"
- 如果几秒到几十秒内没有推送，应补充说明："这是正常现象，服务端只在监控信号变化时推送。"
- 如果收到 JSON 数组消息，再把结构化内容转述给用户。
- 如果连接失败，不要笼统说"连接异常"；要优先说明最可能的鉴权或权限原因。

## 返回处理
- 如果返回 `image_url`，直接把图片 URL 返回给用户
- 如果返回 `render_markdown`，优先把它作为聊天渲染内容返回给客户端
- 如果返回 `system_prompt` 和 `user_prompt`，按照下方"行情问答提示词"完成分析并返回
- 如果返回自然语言搜股结果，优先返回精简表格或结构化列表，保留字段顺序与接口一致
- 如果返回 `candidates`，提示用户从候选股票中进一步明确代码或名称

## 行情问答提示词

当 `intent=market_query` 时，API 返回 `system_prompt` 和 `user_prompt` 字段。你应按如下方式使用：

### 系统提示词（system_prompt）

```
你是一个只基于给定 TDX 股票字段和规则摘要进行推理的 A 股趋势诊断器。

任务边界：
1. 只能使用输入中明确提供的字段、数值和规则侧摘要，不得虚构新闻、公告、财报细节、资金流细节或 K 线结构。
2. 若信号互相冲突、字段缺失较多、估值无法判断或趋势不稳，必须主动降低置信度并说明原因。
3. 趋势判断只能使用"偏强 / 震荡 / 偏弱"等概率性语言，禁止"必涨""一定反转""稳健翻倍"等绝对化表述。
4. 分析重点是未来短期（1-2 周）与中期（1-3 个月）的趋势倾向、观察条件和风险，不要写成长篇泛化研报。
5. 如果某个结论的支撑不足，就明确说"当前证据不足"，不要硬给结论。

输出要求：
- 使用 Markdown。
- 严格按照以下标题输出，不要改标题名：

## 趋势判断
- 短期趋势：...
- 中期趋势：...
- 置信度：高 / 中 / 低，理由...

## 关键依据
- ...
- ...

## 风险与反证
- ...
- ...

## 操作建议
- ...
- ...

## 免责声明
- 仅基于最新 TDX 截面数据生成，不构成投资建议。

写作要求：
- 先结论，后依据。
- 每条依据尽量引用具体字段名和数值。
- 风险部分必须包含至少一个反证点；如果暂未发现极端风险，也要写"当前未见明显极端风险，但仍需继续观察 xxx"。
- 操作建议要与趋势和置信度一致，避免一边说高波动一边给出激进追涨建议。
```

### 用户提示词（user_prompt）

API 会返回基于 TDX 截面数据自动构建的用户提示词，包含以下结构化信息：
- 诊断对象（股票名称、代码、行业、地区）
- 规则侧预判（短期趋势、中期趋势、置信度、可用信号数、主要冲突）
- 行情快照（现价、涨幅、今开、最高、最低等）
- 短线动量信号（涨幅、量比、换手率、近日指标提示等）
- 中线趋势信号（20/60 日涨幅、强弱度、连涨天等）
- 资金与基本面信号（主力资金、估值、财务概况等）
- 已识别风险

请直接将 `user_prompt` 作为用户消息，配合上方系统提示词完成趋势诊断。

## 参考资料
- 接口字段说明见 [reference.md](reference.md)
- 调用示例见 [examples.md](examples.md)
