---
platform_id: "tieba"
platform_name: "百度贴吧"
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
cookie_guide: "guides/cookie-export-tieba.md"
session_check:
  method: "api"
  endpoint: "https://tieba.baidu.com/f/user/json_userinfo"
  success_indicator: "user_name_show"
estimated_session_duration_days: 180
auto_refresh_supported: false
rate_limits:
  views_per_hour: 120
  searches_per_hour: 30
  replies_per_day: 50
  likes_per_day: 200
---

## 认证流程

### Cookie 粘贴认证

百度贴吧使用百度通用账号体系，需要以下关键 Cookie 字段：

**必要 Cookie 字段**：
- `BDUSS`：百度核心认证 Cookie，所有百度服务共享，有效期通常数月
- `STOKEN`：安全 Token，部分写操作需要

`BDUSS` 是最核心的认证凭证，单独拥有即可完成大部分读操作和登录态验证。

**Cookie 获取步骤**：参见 guides/cookie-export-tieba.md

**特殊说明**：
- `BDUSS` 有效期很长（通常 6 个月以上），是所有平台中最长的
- `BDUSS` 是百度全平台通用的，同时适用于百度贴吧、百度网盘、百度知道等
- 退出任何百度产品的登录都会使 `BDUSS` 失效

## 登录态验证

### API 验证（默认）

通过贴吧用户信息接口验证登录态：

1. 发送 GET 请求到 `https://tieba.baidu.com/f/user/json_userinfo`，携带 Cookie
2. 解析 JSON 响应

判定逻辑：
- 响应 JSON 中包含 `"user_name_show"` 字段 → `healthy`
- 响应不包含用户信息或返回错误 → `expired`
- 网络错误 → `unknown`

**优势**：百度贴吧 API 对服务器 IP 限制较宽松，通常无需代理。

### Browser 验证（备选）

使用 OpenClaw browser 工具：

1. 注入已存储的 Cookie 到 `.baidu.com` 域名
2. 导航至 `https://tieba.baidu.com`
3. 等待页面加载

判定逻辑：
- 页面顶部显示用户名和头像 → `healthy`
- 页面显示"登录"按钮 → `expired`
- 页面加载超时或异常 → `unknown`

## 操作指令

### read_feed

```
GET https://tieba.baidu.com/f?kw={贴吧名}&ie=utf-8
Cookie: BDUSS=xxx
```

返回指定贴吧的帖子列表。

### read_post

```
GET https://tieba.baidu.com/p/{帖子ID}
Cookie: BDUSS=xxx
```

返回指定帖子的内容和回复。

### search

```
GET https://tieba.baidu.com/f/search/res?qw={关键词}&ie=utf-8
Cookie: BDUSS=xxx
```

搜索帖子内容。

### write_reply

```
POST https://tieba.baidu.com/f/commit/post/add
Cookie: BDUSS=xxx; STOKEN=xxx
Content-Type: application/x-www-form-urlencoded

fid={吧ID}&tid={帖子ID}&content={回复内容}&tbs={tbs_token}
```

`tbs` 参数需要从 `https://tieba.baidu.com/dc/common/tbs` 获取。

### like

```
POST https://tieba.baidu.com/mo/q/sign
Cookie: BDUSS=xxx
Content-Type: application/x-www-form-urlencoded

kw={贴吧名}&tbs={tbs_token}
```

贴吧的"点赞"实际为签到（一键签到）。

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 浏览/API 请求 | ≤ 120 次/小时 | 限制相对宽松 |
| 搜索 | ≤ 30 次/小时 | 高频搜索可能触发验证码 |
| 回复 | ≤ 50 条/天 | 重复内容会被拦截，新号限制更严 |
| 签到 | ≤ 200 个吧/天 | 一键签到不受严格限制 |

**操作间隔建议**：每次操作间隔 2-5 秒随机延迟。

## 已知问题

1. **tbs Token**：回帖等写操作需要先获取 `tbs` 反跨站 Token，通过 `https://tieba.baidu.com/dc/common/tbs` 接口获取。
2. **BDUSS 全平台共享**：退出百度任何产品（贴吧、网盘等）的登录都会使 BDUSS 失效。
3. **验证码**：高频操作或异常行为可能触发百度验证码。
4. **等级限制**：部分贴吧对低等级用户有发帖限制。
5. **内容审核**：百度对敏感内容有严格审核，违规内容会被自动删除。
6. **IP 友好**：百度贴吧 API 对服务器 IP 无严格限制。
