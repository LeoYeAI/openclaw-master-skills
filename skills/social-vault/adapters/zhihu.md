---
platform_id: "zhihu"
platform_name: "知乎"
auth_methods:
  - type: "cookie_paste"
    priority: 1
    label: "浏览器 Cookie 粘贴"
capabilities:
  - read_feed
  - read_post
  - search
  - write_reply
  - like
cookie_guide: "guides/cookie-export-zhihu.md"
session_check:
  method: "api"
  endpoint: "https://www.zhihu.com/api/v4/me"
  success_indicator: "\"id\""
estimated_session_duration_days: 30
auto_refresh_supported: true
rate_limits:
  views_per_hour: 60
  searches_per_hour: 20
  comments_per_day: 30
  likes_per_day: 100
---

## 认证流程

### Cookie 粘贴认证

知乎 Web 端需要以下关键 Cookie 字段：

**必要 Cookie 字段**：
- `z_c0`：主认证 Token，JWT 格式，有效期约 30 天
- `d_c0`：设备标识 Cookie，用于请求签名

`z_c0` 是核心认证凭证，缺少则所有需要登录的操作均无法进行。`d_c0` 用于生成 `x-zse-96` 签名参数。

**Cookie 获取步骤**：参见 guides/cookie-export-zhihu.md

**特殊说明**：
- 知乎 Cookie 有效期约 30 天
- 知乎部分 API 需要 `x-zse-96` 签名参数，该签名基于 `d_c0` 和请求 URL 计算
- 简单的验证请求（如 `/api/v4/me`）不需要签名，只需 `z_c0`

## 登录态验证

### API 验证（默认）

通过知乎个人信息接口验证登录态：

1. 发送 GET 请求到 `https://www.zhihu.com/api/v4/me`，携带 Cookie
2. 解析 JSON 响应

判定逻辑：
- 响应 JSON 中包含 `"id"` 字段 → `healthy`（包含用户 ID、昵称等信息）
- 响应 401 → `expired`（Cookie 已失效）
- 响应 403 → `degraded`（可能被限流）
- 响应不包含预期标志 → `degraded`
- 网络错误 → `unknown`

**注意**：知乎 API 对服务器 IP 有一定限制，高频访问可能触发验证码。

### Browser 验证（备选）

使用 OpenClaw browser 工具：

1. 注入已存储的 Cookie 到 `.zhihu.com` 域名
2. 导航至 `https://www.zhihu.com`
3. 等待页面加载

判定逻辑：
- 页面右上角显示用户头像和消息图标 → `healthy`
- 页面弹出登录窗口 → `expired`
- 页面加载超时或异常 → `unknown`

## 操作指令

### read_feed

```
GET https://www.zhihu.com/api/v4/recommend_feeds
Cookie: z_c0=xxx
```

返回首页推荐信息流。需要 `x-zse-96` 签名。

### read_post

**问题详情**：
```
GET https://www.zhihu.com/api/v4/questions/{question_id}
Cookie: z_c0=xxx
```

**回答详情**：
```
GET https://www.zhihu.com/api/v4/answers/{answer_id}
Cookie: z_c0=xxx
```

### search

```
GET https://www.zhihu.com/api/v4/search_v3?t=general&q={keyword}
Cookie: z_c0=xxx
```

搜索问题、回答、文章等内容。需要 `x-zse-96` 签名。

### write_reply

**回答问题**：
```
POST https://www.zhihu.com/api/v4/questions/{question_id}/answers
Cookie: z_c0=xxx
Content-Type: application/json

{"content": "<p>回答内容</p>"}
```

**评论回答**：
```
POST https://www.zhihu.com/api/v4/comments
Cookie: z_c0=xxx
Content-Type: application/json

{"content": "评论内容", "resource_type": "answer", "resource_id": "{answer_id}"}
```

### like

**赞同回答**：
```
POST https://www.zhihu.com/api/v4/answers/{answer_id}/voters
Cookie: z_c0=xxx
Content-Type: application/json

{"type": "up"}
```

`type`: `up` = 赞同，`down` = 反对，`neutral` = 取消。

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 浏览/API 请求 | ≤ 60 次/小时 | 高频访问触发验证码 |
| 搜索 | ≤ 20 次/小时 | 搜索接口限制较严 |
| 回答/评论 | ≤ 30 条/天 | 重复内容会被识别 |
| 赞同 | ≤ 100 次/天 | 短时间大量操作可能被风控 |

**操作间隔建议**：每次操作间隔 3-8 秒随机延迟。

## 已知问题

1. **x-zse-96 签名**：知乎部分 API（推荐流、搜索）需要 `x-zse-96` 请求头，该签名算法基于 `d_c0` Cookie 和请求 URL。通过 browser 工具操作可自动绕过签名要求。
2. **反爬策略**：知乎对高频访问有验证码机制，VPS IP 可能触发更频繁的验证。
3. **内容审核**：知乎对回答和评论有严格的内容审核，不符合社区规范的内容会被自动折叠或删除。
4. **新号限制**：新注册或低信用的账号在回答和评论方面有更多限制。
5. **盐选会员内容**：部分内容仅对盐选会员可见，非会员账号无法获取完整内容。
6. **IP 限制**：知乎对非住宅 IP 有一定限制，可能需要更频繁地更新 Cookie。
