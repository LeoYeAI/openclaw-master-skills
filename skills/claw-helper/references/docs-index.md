# OpenClaw 文档索引

## 文档分类

### start - 入门指南
安装、快速开始、入门指南

| 文件 | 描述 |
|------|------|
| {{docsPath}}/start/getting-started.md | 新手快速入门指南 |
| {{docsPath}}/start/quickstart.md | 快速开始教程 |
| {{docsPath}}/start/setup.md | 详细安装说明 |
| {{docsPath}}/start/onboarding.md | 入门流程 |
| {{docsPath}}/start/wizard.md | 安装向导指南 |
| {{docsPath}}/start/docs-directory.md | 文档目录导航 |

### cli - CLI 命令参考
所有 OpenClaw CLI 命令

| 文件 | 描述 |
|------|------|
| {{docsPath}}/cli/index.md | CLI 概览和命令列表 |
| {{docsPath}}/cli/config.md | 配置命令 (get, set, unset) |
| {{docsPath}}/cli/gateway.md | 网关管理 |
| {{docsPath}}/cli/channels.md | 频道管理 |
| {{docsPath}}/cli/agents.md | Agent 管理 |
| {{docsPath}}/cli/sessions.md | 会话管理 |
| {{docsPath}}/cli/doctor.md | 健康检查和诊断 |
| {{docsPath}}/cli/message.md | 消息收发 |
| {{docsPath}}/cli/memory.md | 内存搜索和管理 |

### channels - 消息频道
支持的即时通讯平台

| 文件 | 描述 |
|------|------|
| {{docsPath}}/channels/index.md | 频道概览 |
| {{docsPath}}/channels/telegram.md | Telegram 机器人设置 |
| {{docsPath}}/channels/discord.md | Discord 机器人设置 |
| {{docsPath}}/channels/whatsapp.md | WhatsApp 集成 |
| {{docsPath}}/channels/slack.md | Slack 机器人设置 |
| {{docsPath}}/channels/signal.md | Signal 通讯 |
| {{docsPath}}/channels/irc.md | IRC 网络 |
| {{docsPath}}/channels/imessage.md | Mac iMessage |
| {{docsPath}}/channels/msteams.md | Microsoft Teams |
| {{docsPath}}/channels/mattermost.md | Mattermost |
| {{docsPath}}/channels/matrix.md | Matrix 协议 |
| {{docsPath}}/channels/troubleshooting.md | 频道问题排查 |

### concepts - 核心概念
OpenClaw 架构和核心概念

| 文件 | 描述 |
|------|------|
| {{docsPath}}/concepts/agent.md | 什么是 Agent |
| {{docsPath}}/concepts/agent-loop.md | Agent 执行循环 |
| {{docsPath}}/concepts/agent-workspace.md | Agent 工作区 |
| {{docsPath}}/concepts/session.md | 会话和对话历史 |
| {{docsPath}}/concepts/memory.md | 记忆和上下文管理 |
| {{docsPath}}/concepts/messages.md | 消息处理 |
| {{docsPath}}/concepts/model-providers.md | LLM 提供商集成 |
| {{docsPath}}/concepts/system-prompt.md | System Prompt 定制 |

### gateway - 网关
网关配置和部署

| 文件 | 描述 |
|------|------|
| {{docsPath}}/gateway/index.md | 网关概览 |
| {{docsPath}}/gateway/configuration.md | 网关配置选项 |
| {{docsPath}}/gateway/configuration-reference.md | 配置参考 |
| {{docsPath}}/gateway/security/index.md | 安全设置 |
| {{docsPath}}/gateway/remote.md | 远程网关访问 |
| {{docsPath}}/gateway/sandboxing.md | 沙箱模式 |
| {{docsPath}}/gateway/doctor.md | 网关诊断 |
| {{docsPath}}/gateway/troubleshooting.md | 网关问题 |

### providers - 模型提供商
LLM 提供商集成

| 文件 | 描述 |
|------|------|
| {{docsPath}}/providers/index.md | 提供商概览 |
| {{docsPath}}/providers/openai.md | OpenAI 模型 |
| {{docsPath}}/providers/anthropic.md | Anthropic Claude |
| {{docsPath}}/providers/ollama.md | Ollama 本地模型 |
| {{docsPath}}/providers/openrouter.md | OpenRouter 聚合 |
| {{docsPath}}/providers/bedrock.md | AWS Bedrock |

### tools - 工具
内置工具和能力

| 文件 | 描述 |
|------|------|
| {{docsPath}}/tools/index.md | 工具概览 |
| {{docsPath}}/tools/exec.md | Shell 命令执行 |
| {{docsPath}}/tools/browser.md | 浏览器自动化 |
| {{docsPath}}/tools/subagents.md | 子 Agent |
| {{docsPath}}/tools/skills.md | 技能系统 |
| {{docsPath}}/tools/elevated.md | 提升权限 |

### platforms - 平台
平台特定指南

| 文件 | 描述 |
|------|------|
| {{docsPath}}/platforms/index.md | 平台概览 |
| {{docsPath}}/platforms/macos.md | macOS 安装 |
| {{docsPath}}/platforms/linux.md | Linux 安装 |
| {{docsPath}}/platforms/windows.md | Windows 安装 |
| {{docsPath}}/platforms/ios.md | iOS 应用 |
| {{docsPath}}/platforms/android.md | Android 应用 |

### automation - 自动化
自动化功能

| 文件 | 描述 |
|------|------|
| {{docsPath}}/automation/cron-jobs.md | 定时任务 |
| {{docsPath}}/automation/webhook.md | Webhook |
| {{docsPath}}/automation/poll.md | 消息轮询 |
| {{docsPath}}/automation/hooks.md | 事件钩子 |
| {{docsPath}}/automation/troubleshooting.md | 自动化问题 |

### help - 帮助和故障排除
帮助文档和故障排除

| 文件 | 描述 |
|------|------|
| {{docsPath}}/help/troubleshooting.md | 常见问题和解决方案 |
| {{docsPath}}/help/debugging.md | 调试技巧 |
| {{docsPath}}/help/faq.md | 常见问题 |
| {{docsPath}}/help/environment.md | 环境变量 |

---

## 常见问题快速参考

| 问题 | 诊断命令 | 文档 |
|------|----------|------|
| 网关无法启动 | `openclaw doctor`, `openclaw gateway status`, `openclaw logs` | {{docsPath}}/gateway/troubleshooting.md |
| 频道无法连接 | `openclaw channels status`, `openclaw channels status --probe` | {{docsPath}}/channels/troubleshooting.md |
| 配置问题 | `openclaw config validate`, `openclaw config get` | {{docsPath}}/cli/config.md |
| 模型不工作 | `openclaw doctor`, `openclaw models list` | {{docsPath}}/providers/index.md |
