---
platform_id: "bilibili"
platform_name: "哔哩哔哩"
auth_methods:
  - type: "cookie_paste"
    priority: 1
    label: "浏览器 Cookie 粘贴"
  - type: "qrcode"
    priority: 2
    label: "扫码登录（适合 VPS 环境）"
capabilities:
  - read_feed
  - read_post
  - search
  - write_reply
  - like
cookie_guide: "guides/cookie-export-bilibili.md"
session_check:
  method: "api"
  endpoint: "https://api.bilibili.com/x/web-interface/nav"
  success_indicator: "\"isLogin\":true"
estimated_session_duration_days: 30
auto_refresh_supported: true
rate_limits:
  views_per_hour: 120
  searches_per_hour: 30
  comments_per_day: 50
  likes_per_day: 200
---

## 认证流程

### Cookie 粘贴认证

B站 Web 端需要以下关键 Cookie 字段：

**必要 Cookie 字段**：
- `SESSDATA`：主会话 Cookie，URL 编码格式，有效期约 30 天
- `bili_jct`：CSRF Token，所有 POST 请求必须携带
- `DedeUserID`：用户 UID

以上三个字段缺一不可。`SESSDATA` 用于身份认证，`bili_jct` 用于防跨站请求伪造校验。

**Cookie 获取步骤**：参见 guides/cookie-export-bilibili.md

**特殊说明**：
- B站 Cookie 有效期约 30 天，相对较长
- `SESSDATA` 值包含 URL 编码字符（如 `%2C`），解析时需保留原始编码
- POST 请求（评论、点赞等）需要将 `bili_jct` 同时作为表单参数 `csrf` 提交

### 扫码登录认证（VPS 环境）

B站提供官方扫码登录 API，流程稳定可靠。

**流程**：
1. 请求 `https://passport.bilibili.com/x/passport-login/web/qrcode/generate` 获取二维码 URL 和 `qrcode_key`
2. 将二维码 URL 生成图片展示给用户
3. 用户使用哔哩哔哩 APP 扫码确认
4. 轮询 `https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={key}` 检查扫码状态
5. 扫码成功后从响应的 `Set-Cookie` 中提取凭证
6. 加密存储

**扫码状态码**：
- `86101`：未扫码
- `86090`：已扫码未确认
- `86038`：二维码已过期
- `0`：登录成功

## 登录态验证

### API 验证（默认）

通过 B站导航栏接口验证登录态，该接口反爬宽松、响应轻量：

1. 发送 GET 请求到 `https://api.bilibili.com/x/web-interface/nav`，携带 Cookie
2. 解析 JSON 响应

判定逻辑：
- 响应 JSON 中包含 `"isLogin":true` → `healthy`
- 响应 JSON 中包含 `"isLogin":false` → `expired`
- 响应 401/403 → `expired`
- 响应不包含预期标志 → `degraded`
- 网络错误 → `unknown`

**优势**：B站 API 对服务器 IP 无特殊限制，验证稳定。

### Browser 验证（备选）

使用 OpenClaw browser 工具：

1. 注入已存储的 Cookie 到 `.bilibili.com` 域名
2. 导航至 `https://www.bilibili.com`
3. 等待页面加载

判定逻辑：
- 页面右上角显示用户头像和昵称 → `healthy`
- 页面右上角显示"登录"按钮 → `expired`
- 页面加载超时或异常 → `unknown`

## 操作指令

### read_feed

```
GET https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd
Cookie: SESSDATA=xxx
```

返回首页推荐视频列表。注意 wbi 签名接口需要额外的 `w_rid` 和 `wts` 参数，由 browser 工具自动处理。

### read_post

```
GET https://api.bilibili.com/x/web-interface/view?bvid={bvid}
Cookie: SESSDATA=xxx
```

返回指定视频的详细信息（标题、简介、播放量、弹幕数等）。

### search

```
GET https://api.bilibili.com/x/web-interface/wbi/search/all/v2?keyword={keyword}
Cookie: SESSDATA=xxx
```

搜索视频、用户、番剧等内容。wbi 签名参数同样由 browser 自动处理。

### write_reply

```
POST https://api.bilibili.com/x/v2/reply/add
Cookie: SESSDATA=xxx; bili_jct=xxx
Content-Type: application/x-www-form-urlencoded

oid={视频aid}&type=1&message={评论内容}&csrf={bili_jct}
```

`type` 参数：1=视频，12=专栏，17=动态。

### like

```
POST https://api.bilibili.com/x/web-interface/archive/like
Cookie: SESSDATA=xxx; bili_jct=xxx
Content-Type: application/x-www-form-urlencoded

aid={视频aid}&like=1&csrf={bili_jct}
```

`like`: 1=点赞，2=取消点赞。

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 浏览/API 请求 | ≤ 120 次/小时 | B站 API 限制相对宽松 |
| 搜索 | ≤ 30 次/小时 | 高频搜索可能触发验证码 |
| 评论 | ≤ 50 条/天 | 重复内容会被拦截，新号限制更严 |
| 点赞 | ≤ 200 次/天 | 短时间大量点赞可能被风控 |

**操作间隔建议**：每次操作间隔 2-5 秒随机延迟。

## 已知问题

1. **wbi 签名**：B站部分 API（推荐流、搜索）使用 wbi 签名机制，需要从 nav 接口获取 `img_key` 和 `sub_key` 计算签名参数。通过 browser 工具操作可自动处理。
2. **SESSDATA 编码**：`SESSDATA` 值包含 URL 编码字符，部分 Cookie 解析器可能错误解码，需保留原始编码。
3. **风控验证码**：高频操作或异常行为可能触发极验验证码（geetest），需人工干预。
4. **新号限制**：B站对新注册账号（等级 < 2）在评论和弹幕方面有更严格的限制。
5. **CSRF 必填**：所有写操作（评论、点赞、投币等）必须在请求体中包含 `csrf` 参数，值为 `bili_jct` Cookie。
6. **IP 友好**：B站 API 对服务器 IP 无特殊限制，是 SocialVault 中最容易验证的平台。
