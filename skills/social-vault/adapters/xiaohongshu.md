---
platform_id: "xiaohongshu"
platform_name: "小红书"
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
cookie_guide: "guides/cookie-export-xiaohongshu.md"
session_check:
  method: "api"
  endpoint: "https://www.xiaohongshu.com/explore"
  success_indicator: "userId"
estimated_session_duration_days: 7
auto_refresh_supported: true
rate_limits:
  views_per_hour: 60
  searches_per_hour: 20
  comments_per_day: 30
  likes_per_day: 100
---

## 认证流程

### Cookie 粘贴认证

小红书 Web 端需要以下关键 Cookie 字段：

**必要 Cookie 字段**：
- `a1`：用户标识 Cookie，是多数 API 请求签名计算的输入
- `web_session`：会话 Cookie，用于维持登录状态
- `webId`：网页端 ID

以上三个字段缺一不可。

**Cookie 获取步骤**：参见 guides/cookie-export-xiaohongshu.md

**特殊说明**：
- 小红书的 Cookie 有效期较短，通常约 7 天
- 长时间不活跃可能导致 Cookie 更快过期
- 小红书 Web 端的 API 请求需要额外的签名参数（`x-s`、`x-t` 等），这些由 browser 工具自动处理

### 扫码登录认证（P1，VPS 环境）

对于纯 CLI 环境，通过 headless browser 打开小红书登录页，截取二维码并推送给用户手机端扫码。

**流程**：
1. 使用 OpenClaw browser 工具打开 `https://www.xiaohongshu.com`
2. 点击登录按钮，切换到扫码登录标签
3. 截取二维码图片
4. 在 Agent 对话中直接向用户展示二维码截图
5. 用户使用小红书 APP 扫码确认
6. 检测到登录成功后导出 Cookie
7. 加密存储

**安全机制**：
- 二维码 5 分钟过期
- 一次性使用
- 完成后立即关闭临时页面

## 登录态验证

### API 验证（默认，适合 VPS 环境）

通过 HTTP 请求验证：

1. 发送 GET 请求到 `https://www.xiaohongshu.com/user/profile/me`，携带 Cookie
2. 检查响应内容

判定逻辑：
- 响应包含 "个人主页" → `healthy`
- 响应 401/403 → `expired`
- 响应不包含预期标志 → `degraded`
- 网络错误 → `unknown`

### Browser 验证（备选，需 Agent 交互）

使用 OpenClaw browser 工具：

1. 注入已存储的 Cookie 到 `.xiaohongshu.com` 域名
2. 导航至 `https://www.xiaohongshu.com/user/profile/me`
3. 等待页面加载

判定逻辑：
- 页面正常展示个人主页内容 → `healthy`
- 页面重定向到登录页面或弹出登录窗口 → `expired`
- 页面加载但显示"请登录" → `expired`
- 页面加载超时或返回错误 → `unknown`

## 操作指令

所有操作均通过 browser 工具执行。小红书 Web 端 API 有严格的签名校验，由 browser 自动处理。

### read_feed

1. 导航至 `https://www.xiaohongshu.com/explore`
2. 等待信息流加载
3. 提取笔记卡片列表（标题、封面、作者、点赞数）

### read_post

1. 导航至笔记 URL（`https://www.xiaohongshu.com/explore/{note_id}`）
2. 等待笔记内容加载
3. 提取标题、正文、图片列表、评论

### search

1. 导航至 `https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_note`
2. 等待搜索结果加载
3. 可通过 URL 参数切换搜索类型：笔记/用户/商品

### write_reply

1. 导航至目标笔记页面
2. 滚动到评论区
3. 在评论输入框中输入内容
4. 点击发送按钮

### like

1. 在笔记页面或信息流中找到点赞按钮（❤️ 图标）
2. 点击操作

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 浏览页面 | ≤ 60 次/小时 | 过快浏览触发风控验证码 |
| 搜索 | ≤ 20 次/小时 | 高频搜索可能被临时限制 |
| 评论 | ≤ 30 条/天 | 重复内容会被识别为垃圾评论 |
| 点赞 | ≤ 100 次/天 | 短时间大量点赞可能被限制 |

**操作间隔建议**：每次操作间隔 3-10 秒随机延迟，模拟真人行为。

## 已知问题

1. **Cookie 有效期短**：小红书 Cookie 约 7 天有效，建议开启活跃续期功能。
2. **签名校验**：小红书 Web 端 API 使用 `x-s`、`x-s-common`、`x-t` 等签名参数，这些由页面 JS 生成。直接 HTTP 请求无法绕过，必须通过 browser 工具操作。
3. **风控敏感**：小红书的反自动化策略较为激进，异常行为（高频操作、固定时间间隔、非常规设备指纹）可能导致账号被限流甚至封禁。
4. **IP 限制**：部分 VPS IP 可能被小红书识别并限制。
5. **登录页面变化**：小红书登录页面的元素选择器可能随版本更新而变化，扫码登录流程需定期验证。
6. **图片验证码**：异常操作可能触发滑块验证码，需要人工干预或使用验证码识别服务。
