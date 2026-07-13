---
name: sidecar-onestep
description: Control SidecarOneStep - A macOS Sidecar enhancement tool. One-click iPad connection, remote control, automation integration. Manage devices via MCP integration with 15 powerful tools.
homepage: https://sidecaronestep.app.murphyyi.com/
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "category": "productivity",
        "requires": { "bins": ["mcporter"], "apps": ["/Applications/SidecarOneStep.app"] },
        "install":
          [
            {
              "id": "download-app",
              "kind": "download",
              "label": "Download SidecarOneStep",
              "url": "https://github.com/yi-nology/sidecarOneStep/releases/latest"
            },
            {
              "id": "mcporter-config",
              "kind": "command",
              "label": "Configure SidecarOneStep MCP server",
              "command": "mcporter config add sidecar-onestep --command /Applications/SidecarOneStep.app/Contents/MacOS/SidecarOneStep --args mcp"
            }
          ]
      }
  }
---

# SidecarOneStep / 随航一步

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## Overview

**SidecarOneStep** is a powerful macOS Sidecar enhancement tool that makes managing iPad connections effortless. Through MCP (Model Context Protocol) integration, AI assistants like Claude, Cursor, and OpenClaw can directly control your Sidecar connections.

### 📋 System Requirements

| Platform | Version | Notes |
|----------|---------|-------|
| **macOS** | 12.0+ (Monterey) | Required for Sidecar API |
| **iPadOS** | 13.0+ | Required for Sidecar support |
| **Hardware** | 2018+ iPad models | iPad Pro, iPad Air 3rd gen+, iPad 6th gen+, iPad mini 5th gen+ |
| **Tools** | `mcporter` CLI | For MCP integration |

> ⚠️ **Prerequisites**: Both Mac and iPad must be signed into the **same iCloud account** with 2FA enabled.

### 🌟 Key Features

- 🚀 **One-Click Connection** - Instantly connect/disconnect iPad from menu bar
- 📱 **Remote Control** - Web console for controlling Sidecar from your phone
- 🔌 **Wired Mode** - Force wired connection for low-latency stability
- 🖥️ **Virtual Display** - Create virtual displays for extended workspace (v1.4.0+)
- 🛠️ **Full Automation** - Complete REST API + MCP integration (15 tools)
- 🤖 **AI Integration** - Let AI assistants manage your connections

### 📥 Installation

#### 1. Download & Install App

Download the latest version from GitHub Releases:
```
https://github.com/yi-nology/sidecarOneStep/releases/latest
```

Or direct download:
```bash
curl -L -o SidecarOneStep.dmg https://github.com/yi-nology/sidecarOneStep/releases/download/v1.3.9/SidecarOneStep_Installer.dmg
hdiutil attach SidecarOneStep.dmg
cp -R /Volumes/SidecarOneStep\ Installer/SidecarOneStep.app /Applications/
```

#### 2. Enable MCP in Settings

1. Open SidecarOneStep
2. Go to "Settings" → "Developer / Integrations"
3. Enable "MCP (stdio)"

#### 3. Configure MCP

```bash
# Add SidecarOneStep to mcporter
mcporter config add sidecar-onestep \
  --command /Applications/SidecarOneStep.app/Contents/MacOS/SidecarOneStep \
  --args mcp

# Verify configuration
mcporter list sidecar-onestep
```

Expected output:
```
sidecar-onestep — macOS Sidecar 增强工具 (10 tools)
```

### 🚀 Quick Start

#### Prerequisites Check
Before using this skill, ensure:
- [ ] SidecarOneStep.app installed in `/Applications/`
- [ ] MCP enabled in app settings (Settings → Developer/Integrations → MCP)
- [ ] `mcporter` configured: `mcporter list sidecar-onestep` should show the server
- [ ] iPad nearby, unlocked, and on same iCloud account

#### List Available Devices
```bash
mcporter call sidecar-onestep.list_devices
```

Response:
```json
["张易的iPad Pro", "iPad Air"]
```

#### Connect Device (Recommended: Async)
```bash
# Async connection (non-blocking, recommended)
mcporter call sidecar-onestep.connect_device_async device_name="张易的iPad Pro" wired=true

# Response:
{
  "id": "job_12345",
  "status": "success",
  "result": "张易的iPad Pro",
  "wired": true
}
```

#### Disconnect Device
```bash
mcporter call sidecar-onestep.disconnect_device device_name="张易的iPad Pro"
```

#### Get Status
```bash
mcporter call sidecar-onestep.get_status
```

Response:
```json
{
  "active_device": "张易的iPad Pro",
  "active_wired": true,
  "server_running": true,
  "server_port": 8765
}
```

### 🛠️ Available Tools (15)

| Tool | Description | Blocking |
|------|-------------|----------|
| `list_devices` | List available Sidecar devices | ❌ |
| `connect_device` | Connect device (synchronous) | ⚠️ Yes |
| `connect_device_async` | Connect device (async) | ❌ Recommended |
| `get_job_status` | Query async job status | ❌ |
| `cancel_job` | Cancel pending job | ❌ |
| `disconnect_device` | Disconnect device | ❌ |
| `start_http_server` | Start HTTP control server | ❌ |
| `stop_http_server` | Stop HTTP server | ❌ |
| `get_status` | Get app/connection status | ❌ |
| `get_logs` | Get recent server logs | ❌ |
| `virtual_display_status` | Get virtual display status | ❌ |
| `list_virtual_display_sizes` | List available virtual display sizes | ❌ |
| `set_virtual_display_size` | Set virtual display size | ❌ |
| `enable_virtual_display` | Enable virtual display | ❌ |
| `disable_virtual_display` | Disable virtual display | ❌ |

### 🔔 Trigger Examples (for AI Assistants)

When a user says any of the following, this skill should be activated:

**Example 1: Connect iPad**
```
User: "Connect my iPad"
User: "用有线模式连我的 iPad"
```
→ AI calls: `connect_device_async device_name="<device_name>" wired=true`

**Example 2: Check Status**
```
User: "Is my iPad connected?"
User: "看看 Sidecar 状态"
```
→ AI calls: `get_status`

**Example 3: Disconnect**
```
User: "Disconnect iPad"
User: "断开 iPad 连接"
```
→ AI calls: `disconnect_device device_name="<device_name>"`

**Example 4: Web Console**
```
User: "Start the Sidecar web console"
User: "打开 Sidecar 远程控制台"
```
→ AI calls: `start_http_server port=8765`

**Example 5: List Devices**
```
User: "Show me available Sidecar devices"
User: "列出可用的 iPad"
```
→ AI calls: `list_devices`

### 🎯 Use Cases

#### Daily Workflow
```bash
# 1. Connect iPad (async, non-blocking)
mcporter call sidecar-onestep.connect_device_async device_name="iPad Pro" wired=true

# 2. Start web console
mcporter call sidecar-onestep.start_http_server port=8765

# 3. Check status
mcporter call sidecar-onestep.get_status
```

#### Meeting Mode (Wireless)
```bash
# Wireless connection for mobility
mcporter call sidecar-onestep.connect_device_async device_name="iPad Air" wired=false
```

#### Automation Integration
```bash
# Use in scripts, Shortcuts, Raycast, Alfred, etc.
mcporter call sidecar-onestep.connect_device_async device_name="iPad Pro" wired=true
```

### 🤖 AI Assistant Integration

SidecarOneStep works seamlessly with AI assistants:

**Natural Language Commands:**
- "List my iPad devices" → `list_devices`
- "Connect to iPad Pro" → `connect_device_async`
- "Connect iPad with wired mode" → `connect_device_async wired=true`
- "Disconnect iPad" → `disconnect_device`
- "Start web console" → `start_http_server`
- "Check Sidecar status" → `get_status`

### 🔧 Troubleshooting

#### Issue: Device list is empty
**Solution:**
1. Ensure iPad and Mac use the same iCloud account
2. Ensure iPad supports Sidecar (2018 or later)
3. Ensure iPad is nearby and unlocked
4. Check "System Preferences" → "Sidecar"

#### Issue: Async connection job not found
**Note:** In stdio MCP mode, each call creates a new process. Use `connect_device_async` which now returns the complete status immediately, no need to call `get_job_status`.

#### Issue: MCP server not responding
**Solution:**
1. Verify app is installed: `ls /Applications/SidecarOneStep.app`
2. Check configuration: `mcporter list sidecar-onestep`
3. Restart mcporter daemon: `mcporter daemon restart`

### 📚 Resources

- 🏠 **Website**: https://sidecaronestep.app.murphyyi.com/
- 🐙 **GitHub**: https://github.com/yi-nology/sidecarOneStep
- 📦 **Download**: https://github.com/yi-nology/sidecarOneStep/releases
- 📖 **Documentation**: See GitHub README

### 📄 License

MIT License - Free to use

---

<a name="中文"></a>

## 概述

**SidecarOneStep（随航一步）** 是一款强大的 macOS Sidecar 增强工具，让 iPad 连接管理变得轻松简单。通过 MCP（模型上下文协议）集成，Claude、Cursor、OpenClaw 等 AI 助手可以直接控制你的 Sidecar 连接。

### 📋 系统要求

| 平台 | 版本 | 说明 |
|------|------|------|
| **macOS** | 12.0+ (Monterey) | Sidecar API 必需 |
| **iPadOS** | 13.0+ | Sidecar 支持必需 |
| **硬件** | 2018+ iPad 机型 | iPad Pro、iPad Air 第3代+、iPad 第6代+、iPad mini 第5代+ |
| **工具** | `mcporter` CLI | 用于 MCP 集成 |

> ⚠️ **前置条件**：Mac 和 iPad 必须登录**同一 iCloud 账户**并启用双重认证。

### 🌟 核心功能

- 🚀 **一键连接** - 菜单栏即时连接/断开 iPad
- 📱 **远程控制** - Web 控制台，手机管理 Sidecar
- 🔌 **有线模式** - 强制有线连接，低延迟稳定
- 🖥️ **虚拟显示器** - 创建虚拟显示器扩展工作空间（v1.4.0+）
- 🛠️ **完整自动化** - 完整 REST API + MCP 集成（15 个工具）
- 🤖 **AI 集成** - 让 AI 助手管理你的连接

### 📥 安装

#### 1. 下载并安装应用

从 GitHub Releases 下载最新版本：
```
https://github.com/yi-nology/sidecarOneStep/releases/latest
```

或直接下载：
```bash
curl -L -o SidecarOneStep.dmg https://github.com/yi-nology/sidecarOneStep/releases/download/v1.3.9/SidecarOneStep_Installer.dmg
hdiutil attach SidecarOneStep.dmg
cp -R /Volumes/SidecarOneStep\ Installer/SidecarOneStep.app /Applications/
```

#### 2. 在设置中启用 MCP

1. 打开 SidecarOneStep
2. 进入"设置" → "开发/集成"
3. 启用"MCP (stdio)"

#### 3. 配置 MCP

```bash
# 将 SidecarOneStep 添加到 mcporter
mcporter config add sidecar-onestep \
  --command /Applications/SidecarOneStep.app/Contents/MacOS/SidecarOneStep \
  --args mcp

# 验证配置
mcporter list sidecar-onestep
```

预期输出：
```
sidecar-onestep — macOS Sidecar 增强工具 (10 tools)
```

### 🚀 快速开始

#### 前置条件检查
使用此技能前，请确认：
- [ ] SidecarOneStep.app 已安装在 `/Applications/`
- [ ] 应用设置中已启用 MCP（设置 → 开发/集成 → MCP）
- [ ] `mcporter` 已配置：`mcporter list sidecar-onestep` 应显示该服务器
- [ ] iPad 在附近、已解锁、使用同一 iCloud 账户

#### 列出可用设备
```bash
mcporter call sidecar-onestep.list_devices
```

响应：
```json
["张易的iPad Pro", "iPad Air"]
```

#### 连接设备（推荐：异步）
```bash
# 异步连接（不阻塞，推荐）
mcporter call sidecar-onestep.connect_device_async device_name="张易的iPad Pro" wired=true

# 响应：
{
  "id": "job_12345",
  "status": "success",
  "result": "张易的iPad Pro",
  "wired": true
}
```

#### 断开设备
```bash
mcporter call sidecar-onestep.disconnect_device device_name="张易的iPad Pro"
```

#### 获取状态
```bash
mcporter call sidecar-onestep.get_status
```

响应：
```json
{
  "active_device": "张易的iPad Pro",
  "active_wired": true,
  "server_running": true,
  "server_port": 8765
}
```

### 🛠️ 可用工具（15 个）

| 工具 | 说明 | 阻塞 |
|------|------|------|
| `list_devices` | 列出可用 Sidecar 设备 | ❌ |
| `connect_device` | 连接设备（同步） | ⚠️ 是 |
| `connect_device_async` | 连接设备（异步） | ❌ 推荐 |
| `get_job_status` | 查询异步任务状态 | ❌ |
| `cancel_job` | 取消待处理任务 | ❌ |
| `disconnect_device` | 断开设备 | ❌ |
| `start_http_server` | 启动 HTTP 控制服务器 | ❌ |
| `stop_http_server` | 停止 HTTP 服务器 | ❌ |
| `get_status` | 获取应用/连接状态 | ❌ |
| `get_logs` | 获取最近服务器日志 | ❌ |
| `virtual_display_status` | 获取虚拟显示器状态 | ❌ |
| `list_virtual_display_sizes` | 列出可用虚拟显示器尺寸 | ❌ |
| `set_virtual_display_size` | 设置虚拟显示器尺寸 | ❌ |
| `enable_virtual_display` | 启用虚拟显示器 | ❌ |
| `disable_virtual_display` | 禁用虚拟显示器 | ❌ |

### 🔔 触发示例（AI 助手用）

当用户说以下内容时，应激活此技能：

**示例 1：连接 iPad**
```
用户："Connect my iPad"
用户："用有线模式连我的 iPad"
```
→ AI 调用：`connect_device_async device_name="<设备名>" wired=true`

**示例 2：检查状态**
```
用户："Is my iPad connected?"
用户："看看 Sidecar 状态"
```
→ AI 调用：`get_status`

**示例 3：断开连接**
```
用户："Disconnect iPad"
用户："断开 iPad 连接"
```
→ AI 调用：`disconnect_device device_name="<设备名>"`

**示例 4：Web 控制台**
```
用户："Start the Sidecar web console"
用户："打开 Sidecar 远程控制台"
```
→ AI 调用：`start_http_server port=8765`

**示例 5：列出设备**
```
用户："Show me available Sidecar devices"
用户："列出可用的 iPad"
```
→ AI 调用：`list_devices`

**示例 6：虚拟显示器**
```
用户："Enable virtual display"
用户："开启虚拟显示器"
```
→ AI 调用：`enable_virtual_display`

**示例 7：设置虚拟显示器尺寸**
```
用户："Set virtual display to iPad Pro 13 size"
用户："设置虚拟显示器为 iPad Pro 13 尺寸"
```
→ AI 调用：`set_virtual_display_size definition_id=440`

### 🎯 使用场景

#### 每日工作流
```bash
# 1. 连接 iPad（异步，不阻塞）
mcporter call sidecar-onestep.connect_device_async device_name="iPad Pro" wired=true

# 2. 启动 Web 控制台
mcporter call sidecar-onestep.start_http_server port=8765

# 3. 查看状态
mcporter call sidecar-onestep.get_status
```

#### 会议模式（无线）
```bash
# 无线连接，方便移动
mcporter call sidecar-onestep.connect_device_async device_name="iPad Air" wired=false
```

#### 自动化集成
```bash
# 在脚本、快捷指令、Raycast、Alfred 等中使用
mcporter call sidecar-onestep.connect_device_async device_name="iPad Pro" wired=true
```

#### 虚拟显示器使用
```bash
# 1. 查看可用尺寸
mcporter call sidecar-onestep.list_virtual_display_sizes

# 2. 设置尺寸（可选，默认 16:9）
mcporter call sidecar-onestep.set_virtual_display_size definition_id=440

# 3. 启用虚拟显示器
mcporter call sidecar-onestep.enable_virtual_display

# 4. 查看状态
mcporter call sidecar-onestep.virtual_display_status

# 5. 禁用虚拟显示器
mcporter call sidecar-onestep.disable_virtual_display
```

### 🤖 AI 助手集成

SidecarOneStep 与 AI 助手无缝协作：

**自然语言命令：**
- "列出我的 iPad 设备" → `list_devices`
- "连接 iPad Pro" → `connect_device_async`
- "用有线模式连接 iPad" → `connect_device_async wired=true`
- "断开 iPad 连接" → `disconnect_device`
- "启动 Web 控制台" → `start_http_server`
- "查看 Sidecar 状态" → `get_status`
- "开启虚拟显示器" → `enable_virtual_display`
- "关闭虚拟显示器" → `disable_virtual_display`
- "设置虚拟显示器尺寸" → `set_virtual_display_size`
- "查看虚拟显示器状态" → `virtual_display_status`

### 🔧 故障排查

#### 问题：设备列表为空
**解决方案：**
1. 确认 iPad 和 Mac 使用同一 iCloud 账户
2. 确认 iPad 支持 Sidecar（2018 年及之后）
3. 确认 iPad 在附近并已解锁
4. 检查"系统偏好设置" → "随航"

#### 问题：异步任务状态 not_found
**说明：** stdio MCP 模式下，每次调用都会创建新进程。`connect_device_async` 现在会立即返回完整状态，无需调用 `get_job_status`。

#### 问题：MCP 服务器未响应
**解决方案：**
1. 确认应用已安装：`ls /Applications/SidecarOneStep.app`
2. 检查配置：`mcporter list sidecar-onestep`
3. 重启 mcporter daemon：`mcporter daemon restart`

### 📚 资源

- 🏠 **官网**：https://sidecaronestep.app.murphyyi.com/
- 🐙 **GitHub**：https://github.com/yi-nology/sidecarOneStep
- 📦 **下载**：https://github.com/yi-nology/sidecarOneStep/releases
- 📖 **文档**：查看 GitHub README

### 📄 许可证

MIT License - 免费使用

---

## 🎉 Acknowledgments

Created by **MurphyYi**
Skill package by **Wednesday (OpenClaw)**

If you find this tool helpful, please ⭐️ star the [GitHub repository](https://github.com/yi-nology/sidecarOneStep)!
