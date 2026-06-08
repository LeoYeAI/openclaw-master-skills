# 知乎 Cookie 导出教程

## 适用场景

Cookie 粘贴是使用知乎的推荐方式。知乎 Cookie 有效期约 30 天。

## 前置要求

- 一台能打开浏览器的电脑
- Chrome 或 Firefox 浏览器
- 已登录的知乎账号

## 方法一：使用 Cookie-Editor 插件（推荐）

### 第 1 步：安装 Cookie-Editor 插件

- Chrome：在 Chrome 应用商店搜索 "Cookie-Editor" 并安装
- Firefox：在 Firefox 附加组件中搜索 "Cookie-Editor" 并安装

### 第 2 步：打开知乎并确认登录

1. 在浏览器中打开 https://www.zhihu.com
2. 确认已登录（右上角能看到你的头像和消息图标）
3. 如果未登录，点击"登录"，使用手机验证码或密码登录

### 第 3 步：导出 Cookie

1. 点击浏览器工具栏中的 Cookie-Editor 图标
2. 确认显示的是 zhihu.com 的 Cookie
3. 点击 "Export" → 选择 "Export as JSON"
4. Cookie 自动复制到剪贴板

### 第 4 步：粘贴给 SocialVault

将复制的内容粘贴给 SocialVault Agent 即可。Agent 会自动验证登录态。

## 方法二：使用开发者工具 Application 面板

### 第 1 步：打开开发者工具

1. 在 zhihu.com 页面按 `F12`
2. 切换到 "Application"（Chrome）或 "Storage"（Firefox）标签

### 第 2 步：找到关键 Cookie

在 Cookies → `https://www.zhihu.com` 下找到以下 Cookie：

| Cookie 名 | 说明 | 必需 |
|-----------|------|------|
| `z_c0` | 主认证 Token（JWT 格式） | 是 |
| `d_c0` | 设备标识，用于签名计算 | 推荐 |

### 第 3 步：快速复制

在 Console 标签中运行：

```
document.cookie
```

复制输出内容粘贴给 SocialVault。

## 方法三：从网络请求头中获取

当其他方法导入后验证失败时，可从网络请求中获取最完整的 Cookie：

1. 按 `F12` 打开开发者工具
2. 切换到 **"Network"**（网络）标签
3. 刷新知乎页面
4. 在过滤栏输入 `zhihu.com/api` 快速筛选
5. 找到任意一个发往 `www.zhihu.com/api` 的请求（推荐 `/api/v4/me`）
6. 在 "Headers" 中找到 `Cookie` 请求头
7. 右键 → 复制值
8. 粘贴给 SocialVault

## 注意事项

1. **有效期较长**：知乎 Cookie 约 30 天有效，到期前 SocialVault 会提前提醒。
2. **不要退出登录**：导出 Cookie 后不要在浏览器中退出知乎登录。
3. **z_c0 是核心**：`z_c0` 是 JWT 格式的认证 Token，是最关键的 Cookie。
4. **d_c0 推荐导出**：`d_c0` 用于部分 API 的签名计算，建议一并导出。
5. **多账号**：使用浏览器的隐身模式或不同 Profile 分别登录和导出。
