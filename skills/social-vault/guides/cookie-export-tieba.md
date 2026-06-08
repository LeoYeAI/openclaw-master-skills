# 百度贴吧 Cookie 导出教程

## 适用场景

Cookie 粘贴是使用百度贴吧的推荐方式。`BDUSS` 有效期通常长达 6 个月以上，是所有平台中最长的。

## 前置要求

- 一台能打开浏览器的电脑
- Chrome 或 Firefox 浏览器
- 已登录的百度账号

## 方法一：从网络请求头中获取（推荐）

> **为什么推荐这种方式？**  Cookie-Editor 等插件导出的是 `BDUSS_BFESS`（跨站安全版本），而贴吧 API 实际需要的是 `BDUSS`。两者值不同，使用 `BDUSS_BFESS` 会导致验证失败。从实际网络请求头中复制 Cookie 是最准确的方式。

### 第 1 步：打开开发者工具

1. 在浏览器中打开 https://tieba.baidu.com 并确认已登录
2. 按 `F12` 打开开发者工具
3. 切换到 **"Network"**（网络）标签

### 第 2 步：触发请求

1. 刷新页面（`F5` 或 `Ctrl+R`）
2. 等待页面加载完成

### 第 3 步：复制 Cookie

1. 在请求列表中找到任意一个发往 `tieba.baidu.com` 的请求
2. 点击该请求，在右侧面板中切换到 **"Headers"**（标头）标签
3. 向下滚动找到 **"Request Headers"**（请求标头）部分
4. 找到 `Cookie:` 字段
5. 右键点击 Cookie 值 → **复制值**（或全选后 `Ctrl+C`）
6. 粘贴给 SocialVault Agent

### 小贴士

- 复制的 Cookie 字符串中应包含 `BDUSS=...` 而不是 `BDUSS_BFESS=...`
- 如果请求太多，可以在 Network 标签的过滤栏输入 `tieba` 快速筛选
- 推荐选择 `tieba.baidu.com/f/user/json_userinfo` 等 API 请求，Cookie 最完整

## 方法二：使用开发者工具 Application 面板

### 第 1 步：打开开发者工具

1. 在 tieba.baidu.com 页面按 `F12`
2. 切换到 "Application"（Chrome）或 "Storage"（Firefox）标签

### 第 2 步：找到关键 Cookie

在 Cookies → `https://tieba.baidu.com` 下找到以下 Cookie：

| Cookie 名 | 说明 | 必需 |
|-----------|------|------|
| `BDUSS` | 百度核心认证 Cookie，很长的字符串 | 是 |
| `STOKEN` | 安全 Token，写操作需要 | 推荐 |

> **重要**：请确保复制的是 `BDUSS` 而非 `BDUSS_BFESS`。`BDUSS_BFESS` 是带 SameSite 属性的跨站版本，值与 `BDUSS` 不同，用于服务端验证会失败。

### 第 3 步：快速复制

在 Console 标签中运行：

```
document.cookie
```

复制输出内容粘贴给 SocialVault。

> **注意**：`document.cookie` 可能无法读取 HttpOnly 的 Cookie。如果输出中没有 `BDUSS`，请使用方法一从网络请求头获取。

## 方法三：使用 Cookie-Editor 插件

> **注意**：Cookie-Editor 导出的百度 Cookie 中通常只有 `BDUSS_BFESS` 而没有 `BDUSS`。`BDUSS_BFESS` 的值与 `BDUSS` 不同，直接使用会导致验证失败。**强烈建议使用方法一。**

### 第 1 步：安装 Cookie-Editor 插件

- Chrome：在 Chrome 应用商店搜索 "Cookie-Editor" 并安装
- Firefox：在 Firefox 附加组件中搜索 "Cookie-Editor" 并安装

### 第 2 步：打开贴吧并确认登录

1. 在浏览器中打开 https://tieba.baidu.com
2. 确认已登录（页面顶部能看到你的用户名和头像）
3. 如果未登录，点击"登录"，使用手机号或百度账号密码登录

### 第 3 步：导出 Cookie

1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 确认显示的是 baidu.com 的 Cookie
3. 点击 "Export" → 选择 "Export as JSON"
4. Cookie 自动复制到剪贴板

### 第 4 步：粘贴给 SocialVault

将复制的内容粘贴给 SocialVault Agent。如果验证失败，请改用方法一。

## 常见问题

### BDUSS 和 BDUSS_BFESS 有什么区别？

| | `BDUSS` | `BDUSS_BFESS` |
|---|---------|---------------|
| **用途** | 百度核心认证 Cookie | 跨站安全版本（SameSite=None） |
| **值** | 原始 Cookie 值 | 不同的值，不可互换 |
| **获取方式** | 网络请求头、Application 面板 | Cookie-Editor 通常导出此项 |
| **API 验证** | 有效 | 无效 |

### 为什么 Cookie-Editor 导出的 Cookie 无法验证？

百度使用了两套 Cookie 机制：`BDUSS` 用于同站请求，`BDUSS_BFESS` 用于跨站请求。Cookie-Editor 插件在导出时通常只能获取到 `BDUSS_BFESS`，而 SocialVault 的 API 调用需要 `BDUSS`。这就是为什么推荐从网络请求头中获取完整 Cookie。

## 注意事项

1. **有效期极长**：`BDUSS` 通常有效 6 个月以上，几乎不需要更新。
2. **必须使用 BDUSS**：不要使用 `BDUSS_BFESS`，两者不可互换。推荐从网络请求头获取完整 Cookie。
3. **不要退出登录**：退出百度任何产品（贴吧、网盘、知道等）的登录都会使 BDUSS 失效。
4. **全平台共享**：`BDUSS` 是百度全平台通用的，同一个 Cookie 适用于所有百度产品。
5. **STOKEN 推荐导出**：虽然只读操作不需要 STOKEN，但回帖等写操作需要。
6. **多账号**：使用浏览器的隐身模式或不同 Profile 分别登录和导出。
