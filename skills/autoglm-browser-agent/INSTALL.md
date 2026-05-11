# AutoGLM Browser Agent — 安装指南

本文档说明首次安装所需的全部步骤。安装完成后日常使用请参阅 `SKILL.md`。

---

## 0. macOS 解除安全限制

首次下载后，macOS 会阻止未签名的二进制文件运行。执行以下命令解除：

```bash
xattr -d com.apple.quarantine {baseDir}/dist/relay {baseDir}/dist/mcp_server
```

---

## 1. 安装浏览器扩展

在 Chrome / Edge / Brave 等 Chromium 内核浏览器中安装 AutoClaw 扩展：

**Chrome Web Store 安装**（推荐）：

打开链接安装：[AutoClaw 扩展](https://chromewebstore.google.com/detail/jelniggicmclhfgnlapbkgfibmgelfnp)

> Edge 用户也可以从 Chrome Web Store 安装——浏览器会提示"允许来自其他商店的扩展"，点击允许即可。

**安装后验证**：

1. 打开 `chrome://extensions/`
2. 确认 AutoClaw 扩展已出现且开关为**开启状态**（蓝色）
3. 如果扩展被禁用，点击开关启用

---

## 2. 安装 mcporter

```bash
# macOS / Linux
command -v mcporter || npm install -g mcporter
```

**Windows 注意**：PowerShell 默认执行策略会拦截 npm 全局安装的 `.ps1` 包装脚本，导致 `mcporter` 无法直接运行。推荐用 cmd（而非 PowerShell）执行后续所有命令。

```bat
:: Windows — 用 cmd 安装
where mcporter 2>nul || npm install -g mcporter
```

---

## 3. 注册 MCP Server

```bash
# macOS / Linux
mcporter config add autoglm-browser-agent --stdio "{baseDir}/dist/mcp_server --start_url https://www.bing.com --window_width 1456 --window_height 819 --resize_width 1456 --resize_height 819 --max_steps 100 --log_dir {baseDir}/mcp_output --if_subagent"
```

**Windows**：

由于 PowerShell 执行策略限制，推荐用 `node ... cli.js` 方式注册：

```bat
:: Windows — 用 cmd 执行，将 {baseDir} 替换为实际路径
node "%APPDATA%\npm\node_modules\mcporter\dist\cli.js" config add autoglm-browser-agent --command "{baseDir}\dist\mcp_server.exe" --arg --start_url --arg https://www.bing.com --arg --window_width --arg 1456 --arg --window_height --arg 819 --arg --resize_width --arg 1456 --arg --resize_height --arg 819 --arg --max_steps --arg 100 --arg --log_dir --arg "{baseDir}\mcp_output" --arg --if_subagent
```

> **为什么用 `node ... cli.js` 而不是直接 `mcporter`**：PowerShell 执行策略禁止运行 `.ps1`，但 `node` 直接运行 `.js` 不受限制。

验证注册成功：
```bash
# macOS / Linux
mcporter list autoglm-browser-agent --schema
```
```bat
:: Windows
node "%APPDATA%\npm\node_modules\mcporter\dist\cli.js" list autoglm-browser-agent --schema
```

---

## 4. 启动 WS Relay Daemon

Relay 保持 Chrome 扩展的 WebSocket 长连接，防止 mcporter call 结束后 Chrome 窗口关闭。

```bash
# macOS / Linux
{baseDir}/dist/relay
```
```bat
:: Windows
{baseDir}\dist\relay.exe
```

日志输出到 `{baseDir}/mcp_output/relay.log`。

---

## 5. 配置信任模式（auto_approve）

信任模式控制敏感操作（发评论、点赞、发帖、发消息等）是否自动执行：
- **关闭（默认）**：每次敏感操作暂停询问用户确认后才执行
- **开启**：敏感操作自动执行，不再逐次确认
- **无论开关，登录和验证码始终需要用户手动操作**

**询问用户是否开启信任模式**，根据回答写入配置：

```bash
# macOS / Linux — 用户同意开启
mkdir -p ~/.openclaw-autoclaw && echo '{"auto_approve": true}' > ~/.openclaw-autoclaw/config.json

# macOS / Linux — 用户拒绝（默认关闭）
mkdir -p ~/.openclaw-autoclaw && echo '{"auto_approve": false}' > ~/.openclaw-autoclaw/config.json
```

```bat
:: Windows — 用户同意开启
if not exist "%USERPROFILE%\.openclaw-autoclaw" mkdir "%USERPROFILE%\.openclaw-autoclaw"
echo {"auto_approve": true} > "%USERPROFILE%\.openclaw-autoclaw\config.json"

:: Windows — 用户拒绝（默认关闭）
if not exist "%USERPROFILE%\.openclaw-autoclaw" mkdir "%USERPROFILE%\.openclaw-autoclaw"
echo {"auto_approve": false} > "%USERPROFILE%\.openclaw-autoclaw\config.json"
```

> 后续使用中用户可随时说"开启/关闭信任模式"来切换。
