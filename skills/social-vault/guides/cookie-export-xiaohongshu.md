# 小红书 Cookie 导出教程

## 适用场景

Cookie 粘贴是在有 GUI 环境下使用小红书的推荐方式。如果你的服务器没有图形界面，可以使用扫码登录方式。

> 注意：小红书 Cookie 有效期约 7 天，比其他平台短。建议开启 SocialVault 的活跃续期功能自动延长有效期。

## 前置要求

- 一台能打开浏览器的电脑
- Chrome 或 Firefox 浏览器
- 已登录的小红书账号

## 方法一：从网络请求头中获取（推荐）

> **为什么推荐这种方式？**  Cookie-Editor 等插件可能导出不完整的 Cookie，或者导出浏览器扩展附加的额外字段，导致服务端无法正确识别。从实际网络请求头中复制 Cookie 是最准确、最可靠的方式。

### 第 1 步：打开开发者工具

1. 在浏览器中打开 https://www.xiaohongshu.com 并确认已登录
2. 按 `F12` 打开开发者工具
3. 切换到 **"Network"**（网络）标签

### 第 2 步：触发请求

1. 刷新页面（`F5` 或 `Ctrl+R`）
2. 等待页面加载完成，左侧会出现大量请求

### 第 3 步：复制 Cookie

1. 在请求列表中找到任意一个发往 `www.xiaohongshu.com` 或 `edith.xiaohongshu.com` 的请求
2. 点击该请求，在右侧面板中切换到 **"Headers"**（标头）标签
3. 向下滚动找到 **"Request Headers"**（请求标头）部分
4. 找到 `Cookie:` 字段
5. 右键点击 Cookie 值 → **复制值**（或全选后 `Ctrl+C`）
6. 粘贴给 SocialVault Agent

### 小贴士

- 推荐找 `api` 开头的子域名请求（如 `edith.xiaohongshu.com`），这些请求的 Cookie 最完整
- 如果请求太多，可以在 Network 标签的过滤栏输入 `edith` 快速筛选
- 复制出来的是一长串 `key=value; key=value` 格式的字符串，直接粘贴即可

## 方法二：使用开发者工具 Application 面板

### 第 1 步：打开开发者工具

1. 在 xiaohongshu.com 页面按 `F12`
2. 切换到 "Application"（Chrome）或 "Storage"（Firefox）标签

### 第 2 步：找到关键 Cookie

在 Cookies → `https://www.xiaohongshu.com` 下找到以下 Cookie：

| Cookie 名 | 说明 | 必需 |
|-----------|------|------|
| `a1` | 用户标识，用于签名计算 | 是 |
| `web_session` | 会话令牌 | 是 |
| `webId` | 网页端 ID | 是 |

### 第 3 步：快速复制

在 Console 标签中运行：

```
document.cookie
```

复制输出内容粘贴给 SocialVault。

## 方法三：使用 Cookie-Editor 插件

> **注意**：Cookie-Editor 导出的内容可能不完整或包含多余字段。如果使用此方法导入后验证失败，请改用方法一。

### 第 1 步：安装 Cookie-Editor 插件

- Chrome：在 Chrome 应用商店搜索 "Cookie-Editor" 并安装
- Firefox：在 Firefox 附加组件中搜索 "Cookie-Editor" 并安装

### 第 2 步：打开小红书并确认登录

1. 在浏览器中打开 https://www.xiaohongshu.com
2. 确认已登录（能看到首页推荐信息流和你的头像）
3. 如果未登录，点击右上角登录，推荐使用手机扫码方式

### 第 3 步：导出 Cookie

1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 确认显示的是 xiaohongshu.com 的 Cookie
3. 点击 "Export" → 选择 "Export as JSON"
4. Cookie 自动复制到剪贴板

### 第 4 步：粘贴给 SocialVault

将复制的内容粘贴给 SocialVault Agent 即可。Agent 会自动验证登录态。

## 注意事项

1. **有效期短**：小红书 Cookie 约 7 天有效。到期前 SocialVault 会提前提醒你更新。
2. **推荐从请求头获取**：Cookie-Editor 等插件导出的 Cookie 可能不完整，建议优先使用方法一从网络请求头中复制。
3. **不要退出登录**：导出 Cookie 后不要在浏览器中退出小红书登录。
4. **不要清理浏览器数据**：清理 Cookie 会导致导出的 Cookie 立即失效。
5. **关键字段**：`a1`、`web_session` 和 `webId` 是必需的，缺少任何一个都会导致操作失败。
6. **活跃续期**：建议在 SocialVault 中开启活跃续期功能，自动访问小红书页面延长 Cookie 有效期。
7. **多账号**：如果有多个小红书账号，需要分别登录并导出 Cookie。可以使用浏览器的隐身模式或不同浏览器 Profile。
