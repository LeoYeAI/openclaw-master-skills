# Platform Adapter 开发规范

## 一、概述

Platform Adapter 是 SocialVault 的平台扩展机制。每个适配器是一个 Markdown 文件，描述如何对接某个社交平台的认证和操作。Agent 阅读适配器内容后即可操作对应平台，无需额外代码。

## 二、文件位置

官方适配器放在 `adapters/` 目录下，用户自建适配器放在 `adapters/custom/` 目录下。文件名格式为 `平台标识.md`，如 `bilibili.md`、`v2ex.md`。

## 三、Frontmatter 必填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| platform_id | string | 唯一标识，小写字母和连字符 | `bilibili` |
| platform_name | string | 展示名称 | `哔哩哔哩` |
| auth_methods | array | 认证方式列表，每项含 type、priority、label | 见下方 |
| capabilities | string[] | 支持的操作列表 | `[read_post, search]` |
| session_check.method | string | 验证方式 | `api` 或 `browser` |
| session_check.endpoint | string | 验证 URL | `https://...` |
| session_check.success_indicator | string | 成功判定标志 | `name` |
| estimated_session_duration_days | number | 预估 session 有效天数 | `14` |
| auto_refresh_supported | boolean | 是否支持活跃续期 | `true` |

## 四、Frontmatter 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cookie_guide | string | Cookie 导出教程文件路径 |
| rate_limits | object | 频率限制参考值 |

## 五、auth_methods 结构

```yaml
auth_methods:
  - type: "cookie_paste"       # cookie_paste / api_token / qrcode
    priority: 1                # 数字越小优先级越高
    label: "浏览器 Cookie 粘贴"  # 展示给用户的描述
```

### type 可选值

| 值 | 说明 |
|------|------|
| cookie_paste | 用户手动导出浏览器 Cookie 粘贴导入 |
| api_token | 通过平台 API 获取 Token |
| qrcode | 扫码登录（通过 headless browser 获取二维码） |

## 六、capabilities 可选值

| 值 | 说明 |
|------|------|
| read_feed | 读取信息流 |
| read_post | 读取指定帖子 |
| search | 搜索内容 |
| write_reply | 发表回复/评论 |
| write_post | 发表新帖子 |
| like | 点赞/收藏 |
| send_dm | 发送私信 |

## 七、正文结构

正文使用二级标题（`##`）组织，以下段落为推荐结构：

### ## 认证流程

按 `auth_methods` 中的每种方式分别描述操作步骤。
- API Token 方式需说明端点、参数、返回值处理。
- Cookie 方式需说明必要的 Cookie 字段。
- 扫码方式需说明登录页 URL 和二维码区域定位方法。

### ## 登录态验证

描述如何判断当前凭证是否有效。
- API 方式：说明请求方式和成功判定逻辑。
- Browser 方式：说明访问哪个页面、检查什么内容。

### ## 操作指令

为 `capabilities` 中列出的每个操作编写指令。
- 对 API 平台给出端点和参数。
- 对无 API 平台描述 browser 操作步骤。

### ## 频率控制

列出该平台的安全操作频率建议。说明超频可能导致的后果（限流、封号等）。

### ## 已知问题

该平台的特殊注意事项，如反自动化策略、Cookie 行为异常等。

## 八、示例

参考 `adapters/bilibili.md` 或 `adapters/xiaohongshu.md` 作为完整示例。

## 九、开发新适配器

1. 复制 `adapters/_template.md`
2. 填写所有 `{{占位符}}` 标记的内容
3. 官方适配器放在 `adapters/` 下，用户自建放在 `adapters/custom/` 下
4. 完成后可通过 `socialvault add <platform>` 测试
