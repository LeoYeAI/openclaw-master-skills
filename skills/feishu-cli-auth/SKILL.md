---
name: feishu-cli-auth
description: >-
  飞书 OAuth 认证和 User Access Token 管理。两步式非交互登录（AI Agent 专用）、
  Token 状态检查、scope 配置、自动刷新机制、搜索功能的 Token 依赖关系。
  当用户请求"登录飞书"、"获取 Token"、"OAuth 授权"、"auth login"、"认证"、
  "搜索需要什么权限"、"Token 过期了"、"刷新 Token"时使用。
  当遇到权限错误（如 99991679 Unauthorized）、Token 过期、state 不匹配等问题时也应使用此技能。
  也适用于：搜索命令报权限错误、Token 相关的排错、需要判断当前授权状态的场景。
  当其他飞书技能（toolkit/msg/read 等）遇到 User Access Token 相关问题时，也应参考此技能。
user-invocable: true
allowed-tools: Bash, Read
---

# 飞书 OAuth 认证与 Token 管理

feishu-cli 通过 OAuth 2.0 Authorization Code Flow 获取 User Access Token，用于搜索等需要用户身份的 API。

## 核心概念

**Token 存储位置**：所有 OAuth Token 保存在 `~/.feishu-cli/token.json`，包括 Access Token、Refresh Token、过期时间和授权 scope。登录、刷新、退出等操作都围绕此文件进行。

**两种身份**：
- **App Access Token**（应用身份）：通过 app_id/app_secret 自动获取，大多数文档操作使用此身份
- **User Access Token**（用户身份）：需 OAuth 授权，搜索 API **必须**使用此身份

**Token 生命周期**：
- Access Token：**2 小时**有效
- Refresh Token：**30 天**有效（需 `offline_access` scope）
- 过期后自动用 Refresh Token 刷新，用户无感

---

## 两步式非交互登录（AI Agent 推荐）

AI Agent 的 Bash tool 无法进行交互式 stdin 输入，因此 `--manual` 模式不可用。使用 `--print-url` + `auth callback` 两步式流程：

### 步骤 1：生成授权 URL

**始终使用最大 scope 范围授权**，一次性覆盖 feishu-cli 所有用户身份功能，避免后续因 scope 不足导致 99991679 错误：

```bash
feishu-cli auth login --print-url --scopes "offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly"
```

输出 JSON（stdout）：
```json
{
  "auth_url": "https://accounts.feishu.cn/open-apis/authen/v1/authorize?...",
  "state": "随机64字符十六进制字符串",
  "redirect_uri": "http://127.0.0.1:9768/callback"
}
```

**立即返回，不阻塞，不启动 HTTP 服务器。**

将 `auth_url` 展示给用户，请用户在浏览器中打开并完成授权。授权后浏览器会跳转到一个无法访问的页面（`127.0.0.1:9768/callback?code=xxx&state=yyy`），这是正常的——让用户复制地址栏中的完整 URL。

### 步骤 2：用回调 URL 换 Token

```bash
feishu-cli auth callback "<回调URL>" --state "<步骤1输出的state>"
```

输出 JSON（stdout）+ 人类可读信息（stderr）：
```json
{
  "status": "success",
  "expires_at": "2026-03-09T04:31:11+08:00",
  "scope": "auth:user.id:read search:docs:read search:message offline_access"
}
```

Token 自动保存到 `~/.feishu-cli/token.json`。

### auth callback 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `code has expired` | 授权 code 有效期约 5 分钟，用户复制回调 URL 太慢 | 重新执行步骤 1 获取新的授权 URL，提醒用户尽快完成 |
| `state 不匹配` | `--state` 参数与回调 URL 中的 state 不一致，或混用了不同次 `--print-url` 的结果 | 确保 `--state` 使用的是同一次 `--print-url` 输出的 state 值 |
| 网络超时 / 连接失败 | 无法访问飞书 OAuth 服务器（网络不通或代理问题） | 检查网络连通性，确认能访问 `open.feishu.cn`；如有代理需配置 `HTTPS_PROXY` |

### 完整示例

```bash
# 步骤 1（使用最大 scope 范围）
feishu-cli auth login --print-url --scopes "offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly"
# → 展示 auth_url 给用户，用户浏览器授权后复制回调 URL

# 步骤 2（用步骤 1 的 state 和用户提供的回调 URL）
feishu-cli auth callback "http://127.0.0.1:9768/callback?code=xxx&state=yyy" --state "yyy"
```

---

## Scope 配置

scope 决定了 Token 能访问哪些 API。登录时通过 `--scopes` 指定（空格分隔）。scope 名称 = 飞书开放平台开发者后台的权限名称，最多 50 个，多次授权**累加**生效。

### 默认策略：始终使用最大 scope

**每次登录都使用以下完整 scope 列表**，一次性覆盖 feishu-cli 全部用户身份功能。避免因 scope 不足导致部分命令报 99991679 错误：

```
offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly
```

### Token 使用策略

feishu-cli 命令按 Token 要求分为三类：

**必须 User Token**：搜索命令（`search docs/messages/apps`）和消息/群聊互动命令（`msg get/list/history/pins/pin/unpin/reaction/delete`、`msg search-chats`、`chat get/update/delete`、`chat member list/add/remove`）通过 `resolveRequiredUserToken` 强制使用 User Token，自动从 token.json 加载。

**可选 User Token**：wiki、calendar、task、doc export 等命令通过 `resolveOptionalUserToken` **默认使用 App Token（租户身份）**，不会自动从 token.json 加载。仅在通过 `--user-access-token` 参数或 `FEISHU_USER_ACCESS_TOKEN` 环境变量显式指定时才使用 User Token。

**仅 App Token**：文档创建/导入、消息发送/回复/转发、权限管理等命令仅使用 App Token，不支持 User Token。

### Scope 完整说明

| scope | 作用 | 对应命令 |
|-------|------|---------|
| `offline_access` | 获取 Refresh Token（30 天有效） | **必须包含**，否则 2 小时后需重新登录 |
| `search:docs:read` | 搜索云文档 | `search docs` |
| `search:message` | 搜索消息 | `search messages` |
| `drive:drive.search:readonly` | 搜索云空间文件 | `search docs`（补充权限） |
| `wiki:wiki:readonly` | 知识库读取（用户身份） | `wiki get/export/nodes` |
| `calendar:calendar:read` | 日历读取 | `calendar list/get/primary` |
| `calendar:calendar.event:read` | 日历事件读取 | `calendar event-search` |
| `calendar:calendar.event:create` | 创建日历事件 | `calendar create-event` |
| `calendar:calendar.event:update` | 更新日历事件 | `calendar event-reply` |
| `calendar:calendar.event:reply` | 回复日历事件 | `calendar event-reply` |
| `calendar:calendar.free_busy:read` | 忙闲查询 | `calendar freebusy` |
| `task:task:read` | 任务读取 | `task list/get` |
| `task:task:write` | 任务写入 | `task create/complete` |
| `task:tasklist:read` | 任务列表读取 | `tasklist list/get` |
| `task:tasklist:write` | 任务列表写入 | `tasklist create/delete` |
| `im:message:readonly` | 消息历史读取 | `msg history/get` |
| `im:message.group_msg:get_as_user` | 用户身份读取群消息 | `msg list/history`（User Token 读群消息必需） |
| `im:chat:read` | 群聊搜索（User Token） | `msg search-chats` |
| `im:chat:readonly` | 群聊信息只读（User Token） | `chat get`、`chat member list` |
| `im:chat.members:read` | 群成员列表读取（User Token） | `chat member list` |
| `im:message.pins` | 消息置顶管理（User Token） | `msg pin/unpin/pins` |
| `im:message.reactions` | 消息 Reaction 管理（User Token） | `msg reaction add/remove/list` |
| `contact:user.base:readonly` | 用户信息读取 | `user info/search` |
| `drive:drive.metadata:readonly` | 文件元数据读取 | `file list/meta` |
| `auth:user.id:read` | 用户身份信息 | 通常自动包含 |

### 前提条件

scope 中的权限必须先在飞书开放平台 → 应用详情 → 权限管理中启用。未启用的权限在授权时会被忽略或报错 20027。

### 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `error=99991679, Unauthorized` | Token 的 scope 不包含目标 API 权限 | 重新登录，使用最大 scope |
| Refresh Token 为空 | 缺少 `offline_access` scope | 重新登录，使用最大 scope |
| `error=20027` | 开发者后台未启用该权限 | 在飞书开放平台启用对应权限后重新授权 |

---

## Token 状态检查

```bash
# 人类可读格式
feishu-cli auth status

# JSON 格式（AI Agent 推荐）
feishu-cli auth status -o json
```

**当已登录且 Token 有效时：**

```json
{
  "logged_in": true,
  "access_token_valid": true,
  "access_token_expires_at": "2026-03-09T04:32:19+08:00",
  "refresh_token_valid": true,
  "refresh_token_expires_at": "2026-03-16T02:32:19+08:00",
  "scope": "auth:user.id:read search:docs:read search:message offline_access"
}
```

**当未登录时：**

```json
{"logged_in": false}
```

### 状态判断逻辑

```
logged_in=false           → 从未登录，需要 auth login
access_token_valid=true   → 正常可用
access_token_valid=false + refresh_token_valid=true → 下次调用时自动刷新，无需操作
access_token_valid=false + refresh_token_valid=false → 需要重新 auth login
scope 中无目标权限         → 需要重新登录并补充 scope
```

---

## Token 自动刷新机制

搜索、消息互动、群聊管理等**必须** User Access Token 的命令（`resolveRequiredUserToken`）通过 `ResolveUserAccessToken()` 按以下优先级链查找。其他可选命令（`resolveOptionalUserToken`）仅检查第 1、2 项，默认使用 App Token：

1. `--user-access-token` 命令行参数
2. `FEISHU_USER_ACCESS_TOKEN` 环境变量
3. `~/.feishu-cli/token.json`：
   - access_token 有效 → 直接使用
   - access_token 过期 + refresh_token 有效 → **自动刷新并保存新 Token**
   - 都过期 → 报错"已过期，请重新登录"
4. `config.yaml` 中的 `user_access_token` 静态配置
5. 全部为空 → 报错"缺少 User Access Token"，列出 4 种获取方式

**刷新过程对用户透明**：stderr 输出 `[自动刷新] 刷新成功...`，命令正常执行。

---

## User Access Token 的使用场景

### 必需 User Access Token 的命令

| 命令类别 | 需要的 scope |
|---------|-------------|
| `search docs "关键词"` | `search:docs:read` |
| `search messages "关键词"` | `search:message` |
| `search apps "关键词"` | （需确认应用是否已开通搜索应用权限） |
| `msg get` | `im:message:readonly` |
| `msg list/history` | `im:message:readonly`、`im:message.group_msg:get_as_user` |
| `msg pin/unpin/pins` | `im:message.pins` |
| `msg reaction add/remove/list` | `im:message.reactions` |
| `msg delete` | `im:message` |
| `msg search-chats` | `im:chat:read` |
| `chat get` | `im:chat:readonly` |
| `chat update/delete` | `im:chat` |
| `chat member list/add/remove` | `im:chat:readonly`、`im:chat.members:read`、`im:chat.members` |

### 可选 User Access Token 的命令

以下命令默认使用 App Token（租户身份），仅在通过 `--user-access-token` 参数或 `FEISHU_USER_ACCESS_TOKEN` 环境变量显式指定时才使用 User Token：

| 命令类别 | 需要的 scope |
|---------|-------------|
| `wiki get/export/nodes` | `wiki:wiki:readonly` |
| `calendar list/get/event-search/freebusy` | `calendar:calendar:read` 等 |
| `task create/complete/list` | `task:task:read task:task:write` |
| `tasklist create/list/delete` | `task:tasklist:read task:tasklist:write` |
| `user info/search` | `contact:user.base:readonly` |

### 登录前的检查流程

```bash
# 1. 检查是否已登录且 Token 有效
feishu-cli auth status -o json

# 2. 如果未登录或已过期，执行两步式登录（使用最大 scope）
feishu-cli auth login --print-url --scopes "offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly"
# ... 用户授权 ...
feishu-cli auth callback "<回调URL>" --state "<state>"

# 3. 登录后搜索命令自动从 token.json 读取 Token
feishu-cli search docs "产品需求"
# 其他命令默认使用 App Token，需要时可显式传 --user-access-token
feishu-cli wiki export <node_token> -o doc.md
feishu-cli task create --summary "待办事项"
```

---

## 其他登录模式

除 AI Agent 的两步式外，还有三种人类用户直接使用的模式：

```bash
# 本地桌面环境（默认）：自动打开浏览器 + 本地 HTTP 回调
feishu-cli auth login --scopes "offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly"

# 远程 SSH 环境：打印 URL，用户手动粘贴回调 URL（交互式 stdin）
feishu-cli auth login --manual --scopes "offline_access search:docs:read search:message drive:drive.search:readonly wiki:wiki:readonly calendar:calendar:read calendar:calendar.event:read calendar:calendar.event:create calendar:calendar.event:update calendar:calendar.event:reply calendar:calendar.free_busy:read task:task:read task:task:write task:tasklist:read task:tasklist:write im:message:readonly im:message.group_msg:get_as_user im:chat:read im:chat:readonly im:chat.members:read contact:user.base:readonly drive:drive.metadata:readonly"

# Device Flow：无需在飞书开放平台配置重定向 URL 白名单
feishu-cli auth login --method device

# Device Flow + 指定 scope
feishu-cli auth login --method device --scopes "offline_access search:docs:read"
```

### Authorization Code Flow 前置条件

在飞书开放平台 → 应用详情 → 安全设置 → 重定向 URL 中添加：
```
http://127.0.0.1:9768/callback
```

如果使用自定义端口（`--port 8080`），需添加对应的重定向 URL。

Device Flow（`--method device`）无需此配置。

### Device Flow 说明

`--method device` 是 Authorization Code Flow 的平替方案，区别仅在于无需配置重定向 URL 白名单：

1. 执行 `feishu-cli auth login --method device`
2. 终端显示用户码和验证链接，在浏览器中打开链接并输入用户码完成授权
3. 命令自动轮询等待授权完成，成功后保存 Token

Device Flow 支持 `--scopes` 参数指定 OAuth scope（会自动追加 `offline_access`）。未指定时默认请求 `offline_access`。

---

## 退出登录

```bash
feishu-cli auth logout
```

删除 `~/.feishu-cli/token.json`，不影响 App Access Token（app_id/app_secret）。

---

## 排错指南

| 问题 | 诊断 | 解决 |
|------|------|------|
| "缺少 User Access Token" | 从未登录 | 执行 `auth login` |
| "User Access Token 已过期" | token.json 中 access + refresh 都过期 | 重新 `auth login` |
| 搜索报 99991679 权限错误 | scope 不足 | 重新登录，加上缺失的 scope |
| Refresh Token 为空 | 未包含 `offline_access` scope | 重新登录，加上 `offline_access` |
| "state 不匹配" | `auth callback` 的 `--state` 与 URL 中的 state 不一致 | 确保使用同一次 `--print-url` 的 state |
| "端口被占用" | 9768 端口已被其他进程使用 | 使用 `--port 其他端口`，并在飞书平台添加对应回调 URL |
| `auth login --manual` 在 AI Agent 中卡住 | stdin 阻塞 | 改用 `--print-url` + `auth callback` 两步式 |
