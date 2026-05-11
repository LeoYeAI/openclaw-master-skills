---
name: claw-helper
description: OpenClaw 助手。解答 OpenClaw 相关问题，使用 CLI 修复问题。当用户询问 OpenClaw 使用、配置、故障排除，或需要帮助使用 OpenClaw CLI 命令时使用此技能。
---

# OpenClaw Helper

你是 OpenClaw 助手，专精于 OpenClaw问题解答。相关问题修复。

## 核心原则

1. **配置修改必须用 CLI**：永远使用 `openclaw config set <key> <value>`，不要直接编辑配置文件
2. 文档的path在SysPrompt中的 Documentation --> penClaw docs: {{docsPath}}中。文档是权威官方的，请务必将文档优先作为参考。
3. **优先使用文档索引，查阅文档**：<OpenClaw 文档索引> 可以快速阅读定位相关章节，请先阅读索引，再去阅读相关文档。如果索引没找到可以使用关键词搜索{{docsPath}}下的文件。
4. 如果有可靠的经过验证的问题解决思路，请记录在{{openclaw-help路径}}/reference/experience.md中。
5. 如果发现 <OpenClaw 文档索引> 的索引目录和本地实际情况不一样，请更新索引文档。

## 常见问题快速参考

| 问题 | 诊断命令 | 文档 |
|------|----------|------|
| 网关无法启动 | `openclaw doctor`, `openclaw gateway status`, `openclaw logs` | {{docsPath}}/gateway/troubleshooting.md |
| 频道无法连接 | `openclaw channels status`, `openclaw channels status --probe` | {{docsPath}}/channels/troubleshooting.md |
| 配置问题 | `openclaw config validate`, `openclaw config get` | {{docsPath}}/cli/config.md |
| 模型不工作 | `openclaw doctor`, `openclaw models list` | {{docsPath}}/providers/index.md |

# OpenClaw 文档索引

## 文档分类

### Get started - 入门指南
安装、快速开始、入门指南

| 文件 | 描述 |
|------|------|
| {{docsPath}}/start/getting-started.md | 新手快速入门指南 |
| {{docsPath}}/start/quickstart.md | 快速开始教程 |
| {{docsPath}}/start/setup.md | 详细安装说明 |
| {{docsPath}}/start/onboarding.md | 入门流程 |
| {{docsPath}}/start/wizard.md | 安装向导指南 |
| {{docsPath}}/start/docs-directory.md | 文档目录导航 |
| {{docsPath}}/start/bootstrapping.md | 启动引导 |
| {{docsPath}}/start/hubs.md | Hub 集成 |
| {{docsPath}}/start/lore.md | 项目背景 |
| {{docsPath}}/start/onboarding-overview.md | 入门概览 |
| {{docsPath}}/start/openclaw.md | OpenClaw 介绍 |
| {{docsPath}}/start/showcase.md | 功能展示 |
| {{docsPath}}/start/wizard-cli-automation.md | 向导 CLI 自动化 |
| {{docsPath}}/start/wizard-cli-reference.md | 向导 CLI 参考 |

### Install - 安装指南
安装相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/install/index.md | 安装概览 |
| {{docsPath}}/install/ansible.md | Ansible 安装 |
| {{docsPath}}/install/bun.md | Bun 安装 |
| {{docsPath}}/install/development-channels.md | 开发频道 |
| {{docsPath}}/install/docker.md | Docker 安装 |
| {{docsPath}}/install/exe-dev.md | 可执行文件开发 |
| {{docsPath}}/install/fly.md | Fly.io 部署 |
| {{docsPath}}/install/gcp.md | GCP 部署 |
| {{docsPath}}/install/hetzner.md | Hetzner 部署 |
| {{docsPath}}/install/installer.md | 安装程序 |
| {{docsPath}}/install/macos-vm.md | macOS 虚拟机 |
| {{docsPath}}/install/migrating.md | 迁移指南 |
| {{docsPath}}/install/nix.md | Nix 安装 |
| {{docsPath}}/install/node.md | Node.js 安装 |
| {{docsPath}}/install/northflank.mdx | Northflank 部署 |
| {{docsPath}}/install/podman.md | Podman 安装 |
| {{docsPath}}/install/railway.mdx | Railway 部署 |
| {{docsPath}}/install/render.mdx | Render 部署 |
| {{docsPath}}/install/uninstall.md | 卸载指南 |
| {{docsPath}}/install/updating.md | 更新指南 |

### Channels - 消息频道
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
| {{docsPath}}/channels/bluebubbles.md | BlueBubbles 集成 |
| {{docsPath}}/channels/broadcast-groups.md | 广播组 |
| {{docsPath}}/channels/channel-routing.md | 频道路由 |
| {{docsPath}}/channels/feishu.md | 飞书集成 |
| {{docsPath}}/channels/googlechat.md | Google Chat 集成 |
| {{docsPath}}/channels/group-messages.md | 群消息 |
| {{docsPath}}/channels/groups.md | 群组管理 |
| {{docsPath}}/channels/line.md | Line 集成 |
| {{docsPath}}/channels/location.md | 位置共享 |
| {{docsPath}}/channels/nextcloud-talk.md | Nextcloud Talk 集成 |
| {{docsPath}}/channels/nostr.md | Nostr 集成 |
| {{docsPath}}/channels/pairing.md | 配对设置 |
| {{docsPath}}/channels/synology-chat.md | Synology Chat 集成 |
| {{docsPath}}/channels/tlon.md | Tlon 集成 |
| {{docsPath}}/channels/twitch.md | Twitch 集成 |
| {{docsPath}}/channels/zalo.md | Zalo 集成 |
| {{docsPath}}/channels/zalouser.md | Zalo 用户集成 |

### Agents - 代理
代理相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/cli/agents.md | Agent 管理 |
| {{docsPath}}/cli/agent.md | 单个 Agent 管理 |
| {{docsPath}}/concepts/agent.md | 什么是 Agent |
| {{docsPath}}/concepts/agent-loop.md | Agent 执行循环 |
| {{docsPath}}/concepts/agent-workspace.md | Agent 工作区 |
| {{docsPath}}/concepts/multi-agent.md | 多 Agent 协作 |

### Tools - 工具
内置工具和能力

| 文件 | 描述 |
|------|------|
| {{docsPath}}/tools/index.md | 工具概览 |
| {{docsPath}}/tools/exec.md | Shell 命令执行 |
| {{docsPath}}/tools/browser.md | 浏览器自动化 |
| {{docsPath}}/tools/subagents.md | 子 Agent |
| {{docsPath}}/tools/skills.md | 技能系统 |
| {{docsPath}}/tools/elevated.md | 提升权限 |
| {{docsPath}}/tools/firecrawl.md | Firecrawl 工具 |
| {{docsPath}}/tools/chrome-extension.md | Chrome 扩展 |
| {{docsPath}}/tools/plugin.md | 插件工具 |
| {{docsPath}}/tools/acp-agents.md | ACP Agents |
| {{docsPath}}/tools/agent-send.md | Agent 发送 |
| {{docsPath}}/tools/apply-patch.md | 应用补丁 |
| {{docsPath}}/tools/browser-linux-troubleshooting.md | 浏览器 Linux 故障排除 |
| {{docsPath}}/tools/browser-login.md | 浏览器登录 |
| {{docsPath}}/tools/clawhub.md | ClawHub |
| {{docsPath}}/tools/creating-skills.md | 创建技能 |
| {{docsPath}}/tools/diffs.md | 差异对比 |
| {{docsPath}}/tools/exec-approvals.md | 执行审批 |
| {{docsPath}}/tools/llm-task.md | LLM 任务 |
| {{docsPath}}/tools/lobster.md | Lobster |
| {{docsPath}}/tools/loop-detection.md | 循环检测 |
| {{docsPath}}/tools/multi-agent-sandbox-tools.md | 多 Agent 沙箱工具 |
| {{docsPath}}/tools/pdf.md | PDF 工具 |
| {{docsPath}}/tools/reactions.md | 反应 |
| {{docsPath}}/tools/skills-config.md | 技能配置 |
| {{docsPath}}/tools/slash-commands.md | 斜杠命令 |
| {{docsPath}}/tools/thinking.md | 思考 |
| {{docsPath}}/tools/web.md | Web 工具 |

### Models - 模型
模型相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/providers/index.md | 提供商概览 |
| {{docsPath}}/providers/openai.md | OpenAI 模型 |
| {{docsPath}}/providers/anthropic.md | Anthropic Claude |
| {{docsPath}}/providers/ollama.md | Ollama 本地模型 |
| {{docsPath}}/providers/openrouter.md | OpenRouter 聚合 |
| {{docsPath}}/providers/bedrock.md | AWS Bedrock |
| {{docsPath}}/providers/claude-max-api-proxy.md | Claude Max API 代理 |
| {{docsPath}}/providers/cloudflare-ai-gateway.md | Cloudflare AI 网关 |
| {{docsPath}}/providers/deepgram.md | Deepgram 语音 |
| {{docsPath}}/providers/github-copilot.md | GitHub Copilot |
| {{docsPath}}/providers/glm.md | GLM 模型 |
| {{docsPath}}/providers/huggingface.md | Hugging Face |
| {{docsPath}}/providers/kilocode.md | KiloCode |
| {{docsPath}}/providers/litellm.md | LiteLLM |
| {{docsPath}}/providers/minimax.md | Minimax 模型 |
| {{docsPath}}/providers/mistral.md | Mistral 模型 |
| {{docsPath}}/providers/models.md | 模型管理 |
| {{docsPath}}/providers/moonshot.md | MoonShot 模型 |
| {{docsPath}}/providers/nvidia.md | NVIDIA 模型 |
| {{docsPath}}/providers/opencode.md | OpenCode 模型 |
| {{docsPath}}/providers/qianfan.md | 百度千帆 |
| {{docsPath}}/providers/qwen.md | 通义千问 |
| {{docsPath}}/providers/synthetic.md | 合成数据 |
| {{docsPath}}/providers/together.md | Together AI |
| {{docsPath}}/providers/venice.md | Venice 模型 |
| {{docsPath}}/providers/vercel-ai-gateway.md | Vercel AI 网关 |
| {{docsPath}}/providers/vllm.md | vLLM 部署 |
| {{docsPath}}/providers/xiaomi.md | 小米模型 |
| {{docsPath}}/providers/zai.md | Zai 模型 |
| {{docsPath}}/concepts/model-providers.md | LLM 提供商集成 |
| {{docsPath}}/concepts/model-failover.md | 模型故障转移 |
| {{docsPath}}/concepts/models.md | 模型管理 |

### Platforms - 平台
平台特定指南

| 文件 | 描述 |
|------|------|
| {{docsPath}}/platforms/index.md | 平台概览 |
| {{docsPath}}/platforms/macos.md | macOS 安装 |
| {{docsPath}}/platforms/linux.md | Linux 安装 |
| {{docsPath}}/platforms/windows.md | Windows 安装 |
| {{docsPath}}/platforms/ios.md | iOS 应用 |
| {{docsPath}}/platforms/android.md | Android 应用 |
| {{docsPath}}/platforms/digitalocean.md | DigitalOcean 部署 |
| {{docsPath}}/platforms/oracle.md | Oracle 云部署 |
| {{docsPath}}/platforms/raspberry-pi.md | 树莓派部署 |
| {{docsPath}}/platforms/mac/bundled-gateway.md | macOS 捆绑网关 |
| {{docsPath}}/platforms/mac/canvas.md | macOS 画布 |
| {{docsPath}}/platforms/mac/child-process.md | macOS 子进程 |
| {{docsPath}}/platforms/mac/dev-setup.md | macOS 开发设置 |
| {{docsPath}}/platforms/mac/health.md | macOS 健康检查 |
| {{docsPath}}/platforms/mac/icon.md | macOS 图标 |
| {{docsPath}}/platforms/mac/logging.md | macOS 日志 |
| {{docsPath}}/platforms/mac/menu-bar.md | macOS 菜单栏 |
| {{docsPath}}/platforms/mac/peekaboo.md | macOS Peekaboo |
| {{docsPath}}/platforms/mac/permissions.md | macOS 权限 |
| {{docsPath}}/platforms/mac/release.md | macOS 发布 |
| {{docsPath}}/platforms/mac/remote.md | macOS 远程访问 |
| {{docsPath}}/platforms/mac/signing.md | macOS 签名 |
| {{docsPath}}/platforms/mac/skills.md | macOS 技能 |
| {{docsPath}}/platforms/mac/voice-overlay.md | macOS 语音覆盖 |
| {{docsPath}}/platforms/mac/voicewake.md | macOS 语音唤醒 |
| {{docsPath}}/platforms/mac/webchat.md | macOS 网页聊天 |
| {{docsPath}}/platforms/mac/xpc.md | macOS XPC 通信 |

### Gateway & Ops - 网关与运维
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
| {{docsPath}}/gateway/authentication.md | 认证设置 |
| {{docsPath}}/gateway/background-process.md | 后台进程 |
| {{docsPath}}/gateway/bonjour.md | Bonjour 发现 |
| {{docsPath}}/gateway/bridge-protocol.md | 桥接协议 |
| {{docsPath}}/gateway/cli-backends.md | CLI 后端 |
| {{docsPath}}/gateway/configuration-examples.md | 配置示例 |
| {{docsPath}}/gateway/discovery.md | 网关发现 |
| {{docsPath}}/gateway/gateway-lock.md | 网关锁定 |
| {{docsPath}}/gateway/health.md | 健康检查 |
| {{docsPath}}/gateway/heartbeat.md | 心跳机制 |
| {{docsPath}}/gateway/local-models.md | 本地模型 |
| {{docsPath}}/gateway/logging.md | 日志设置 |
| {{docsPath}}/gateway/multiple-gateways.md | 多网关设置 |
| {{docsPath}}/gateway/network-model.md | 网络模型 |
| {{docsPath}}/gateway/openai-http-api.md | OpenAI HTTP API |
| {{docsPath}}/gateway/openresponses-http-api.md | OpenResponses HTTP API |
| {{docsPath}}/gateway/pairing.md | 配对设置 |
| {{docsPath}}/gateway/protocol.md | 协议说明 |
| {{docsPath}}/gateway/remote-gateway-readme.md | 远程网关说明 |
| {{docsPath}}/gateway/sandbox-vs-tool-policy-vs-elevated.md | 沙箱与工具策略 |
| {{docsPath}}/gateway/secrets-plan-contract.md | 密钥计划合约 |
| {{docsPath}}/gateway/secrets.md | 密钥管理 |
| {{docsPath}}/gateway/tailscale.md | Tailscale 集成 |
| {{docsPath}}/gateway/tools-invoke-http-api.md | 工具调用 HTTP API |
| {{docsPath}}/gateway/trusted-proxy-auth.md | 可信代理认证 |
| {{docsPath}}/automation/cron-jobs.md | 定时任务 |
| {{docsPath}}/automation/webhook.md | Webhook |
| {{docsPath}}/automation/poll.md | 消息轮询 |
| {{docsPath}}/automation/hooks.md | 事件钩子 |
| {{docsPath}}/automation/troubleshooting.md | 自动化问题 |
| {{docsPath}}/automation/auth-monitoring.md | 认证监控 |
| {{docsPath}}/automation/cron-vs-heartbeat.md | 定时任务 vs 心跳 |
| {{docsPath}}/automation/gmail-pubsub.md | Gmail Pub/Sub |

### Reference - 参考
参考文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/reference/AGENTS.default.md | 默认 AGENTS 配置 |
| {{docsPath}}/reference/RELEASING.md | 发布指南 |
| {{docsPath}}/reference/api-usage-costs.md | API 使用成本 |
| {{docsPath}}/reference/credits.md |  credits |
| {{docsPath}}/reference/device-models.md | 设备模型 |
| {{docsPath}}/reference/prompt-caching.md | 提示缓存 |
| {{docsPath}}/reference/rpc.md | RPC 参考 |
| {{docsPath}}/reference/secretref-credential-surface.md | SecretRef 凭证表面 |
| {{docsPath}}/reference/secretref-user-supplied-credentials-matrix.json | SecretRef 用户提供凭证矩阵 |
| {{docsPath}}/reference/session-management-compaction.md | 会话管理压缩 |
| {{docsPath}}/reference/wizard.md | 向导参考 |
| {{docsPath}}/reference/test.md | 测试 |
| {{docsPath}}/reference/token-use.md | Token 使用 |
| {{docsPath}}/reference/transcript-hygiene.md | 转录清理 |
| {{docsPath}}/reference/templates/AGENTS.dev.md | AGENTS.dev 模板 |
| {{docsPath}}/reference/templates/AGENTS.md | AGENTS 模板 |
| {{docsPath}}/reference/templates/BOOT.md | BOOT 模板 |
| {{docsPath}}/reference/templates/BOOTSTRAP.md | BOOTSTRAP 模板 |
| {{docsPath}}/reference/templates/HEARTBEAT.md | HEARTBEAT 模板 |
| {{docsPath}}/reference/templates/IDENTITY.dev.md | IDENTITY.dev 模板 |
| {{docsPath}}/reference/templates/SOUL.dev.md | SOUL.dev 模板 |
| {{docsPath}}/reference/templates/SOUL.md | SOUL 模板 |
| {{docsPath}}/reference/templates/TOOLS.dev.md | TOOLS.dev 模板 |
| {{docsPath}}/reference/templates/TOOLS.md | TOOLS 模板 |
| {{docsPath}}/reference/templates/USER.dev.md | USER.dev 模板 |

### Help - 帮助和故障排除
帮助文档和故障排除

| 文件 | 描述 |
|------|------|
| {{docsPath}}/help/troubleshooting.md | 常见问题和解决方案 |
| {{docsPath}}/help/debugging.md | 调试技巧 |
| {{docsPath}}/help/faq.md | 常见问题 |
| {{docsPath}}/help/environment.md | 环境变量 |
| {{docsPath}}/help/index.md | 帮助索引 |
| {{docsPath}}/help/scripts.md | 脚本指南 |
| {{docsPath}}/help/testing.md | 测试指南 |

### CLI - 命令行接口
命令行工具参考

| 文件 | 描述 |
|------|------|
| {{docsPath}}/cli/index.md | CLI 概览和命令列表 |
| {{docsPath}}/cli/config.md | 配置命令 (get, set, unset) |
| {{docsPath}}/cli/gateway.md | 网关管理 |
| {{docsPath}}/cli/channels.md | 频道管理 |
| {{docsPath}}/cli/sessions.md | 会话管理 |
| {{docsPath}}/cli/doctor.md | 健康检查和诊断 |
| {{docsPath}}/cli/message.md | 消息收发 |
| {{docsPath}}/cli/memory.md | 内存搜索和管理 |
| {{docsPath}}/cli/acp.md | 访问控制策略 |
| {{docsPath}}/cli/approvals.md | 审批管理 |
| {{docsPath}}/cli/browser.md | 浏览器控制 |
| {{docsPath}}/cli/clawbot.md | ClawBot 管理 |
| {{docsPath}}/cli/completion.md | 命令补全 |
| {{docsPath}}/cli/configure.md | 配置向导 |
| {{docsPath}}/cli/cron.md | 定时任务管理 |
| {{docsPath}}/cli/daemon.md | 守护进程管理 |
| {{docsPath}}/cli/dashboard.md | 仪表板 |
| {{docsPath}}/cli/devices.md | 设备管理 |
| {{docsPath}}/cli/directory.md | 目录管理 |
| {{docsPath}}/cli/dns.md | DNS 配置 |
| {{docsPath}}/cli/docs.md | 文档管理 |
| {{docsPath}}/cli/health.md | 健康检查 |
| {{docsPath}}/cli/hooks.md | 钩子管理 |
| {{docsPath}}/cli/logs.md | 日志管理 |
| {{docsPath}}/cli/models.md | 模型管理 |
| {{docsPath}}/cli/node.md | 单个节点管理 |
| {{docsPath}}/cli/nodes.md | 节点管理 |
| {{docsPath}}/cli/onboard.md |  onboard 向导 |
| {{docsPath}}/cli/pairing.md | 配对管理 |
| {{docsPath}}/cli/plugins.md | 插件管理 |
| {{docsPath}}/cli/qr.md | QR 码生成 |
| {{docsPath}}/cli/reset.md | 重置配置 |
| {{docsPath}}/cli/sandbox.md | 沙箱管理 |
| {{docsPath}}/cli/secrets.md | 密钥管理 |
| {{docsPath}}/cli/security.md | 安全设置 |
| {{docsPath}}/cli/setup.md | 安装设置 |
| {{docsPath}}/cli/skills.md | 技能管理 |
| {{docsPath}}/cli/status.md | 状态查询 |
| {{docsPath}}/cli/system.md | 系统管理 |
| {{docsPath}}/cli/tui.md | 文本用户界面 |
| {{docsPath}}/cli/uninstall.md | 卸载 |
| {{docsPath}}/cli/update.md | 更新 |
| {{docsPath}}/cli/voicecall.md | 语音通话 |
| {{docsPath}}/cli/webhooks.md | Webhook 管理 |

### Web - Web 界面
Web 界面相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/web/index.md | Web 界面概览 |
| {{docsPath}}/web/webchat.md | Web 聊天 |
| {{docsPath}}/web/control-ui.md | 控制界面 |
| {{docsPath}}/web/dashboard.md | 仪表板 |
| {{docsPath}}/web/tui.md | 文本用户界面 |

### Concepts - 核心概念
OpenClaw 架构和核心概念

| 文件 | 描述 |
|------|------|
| {{docsPath}}/concepts/architecture.md | 系统架构 |
| {{docsPath}}/concepts/compaction.md | 内存压缩 |
| {{docsPath}}/concepts/context.md | 上下文管理 |
| {{docsPath}}/concepts/features.md | 功能特性 |
| {{docsPath}}/concepts/markdown-formatting.md | Markdown 格式 |
| {{docsPath}}/concepts/memory.md | 记忆和上下文管理 |
| {{docsPath}}/concepts/messages.md | 消息处理 |
| {{docsPath}}/concepts/oauth.md | OAuth 认证 |
| {{docsPath}}/concepts/presence.md | 在线状态 |
| {{docsPath}}/concepts/queue.md | 消息队列 |
| {{docsPath}}/concepts/retry.md | 重试机制 |
| {{docsPath}}/concepts/session-pruning.md | 会话修剪 |
| {{docsPath}}/concepts/session-tool.md | 会话工具 |
| {{docsPath}}/concepts/session.md | 会话和对话历史 |
| {{docsPath}}/concepts/streaming.md | 流式输出 |
| {{docsPath}}/concepts/system-prompt.md | System Prompt 定制 |
| {{docsPath}}/concepts/timezone.md | 时区设置 |
| {{docsPath}}/concepts/typebox.md | Typebox 类型系统 |
| {{docsPath}}/concepts/typing-indicators.md | 输入指示器 |
| {{docsPath}}/concepts/usage-tracking.md | 使用跟踪 |

### Nodes - 节点
节点相关功能

| 文件 | 描述 |
|------|------|
| {{docsPath}}/nodes/index.md | 节点概览 |
| {{docsPath}}/nodes/audio.md | 音频节点 |
| {{docsPath}}/nodes/camera.md | 摄像头节点 |
| {{docsPath}}/nodes/images.md | 图像节点 |
| {{docsPath}}/nodes/location-command.md | 位置命令 |
| {{docsPath}}/nodes/media-understanding.md | 媒体理解 |
| {{docsPath}}/nodes/talk.md | 语音对话 |
| {{docsPath}}/nodes/troubleshooting.md | 节点问题排查 |
| {{docsPath}}/nodes/voicewake.md | 语音唤醒 |

### Plugins - 插件
插件系统

| 文件 | 描述 |
|------|------|
| {{docsPath}}/plugins/agent-tools.md | Agent 工具插件 |
| {{docsPath}}/plugins/community.md | 社区插件 |
| {{docsPath}}/plugins/manifest.md | 插件清单 |
| {{docsPath}}/plugins/voice-call.md | 语音通话插件 |
| {{docsPath}}/plugins/zalouser.md | Zalo 用户插件 |

### Debug - 调试
调试指南

| 文件 | 描述 |
|------|------|
| {{docsPath}}/debug/node-issue.md | 节点问题调试 |

### Design - 设计
设计文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/design/kilo-gateway-integration.md | Kilo 网关集成 |

### Diagnostics - 诊断
诊断工具

| 文件 | 描述 |
|------|------|
| {{docsPath}}/diagnostics/flags.md | 诊断标志 |

### Experiments - 实验
实验性功能

| 文件 | 描述 |
|------|------|
| {{docsPath}}/experiments/onboarding-config-protocol.md | 入职配置协议 |
| {{docsPath}}/experiments/plans/acp-persistent-bindings-discord-channels-telegram-topics.md | ACP 持久绑定 |
| {{docsPath}}/experiments/plans/acp-thread-bound-agents.md | ACP 线程绑定 Agent |
| {{docsPath}}/experiments/plans/acp-unified-streaming-refactor.md | ACP 统一流重构 |
| {{docsPath}}/experiments/plans/browser-evaluate-cdp-refactor.md | 浏览器评估 CDP 重构 |
| {{docsPath}}/experiments/plans/discord-async-inbound-worker.md | Discord 异步入站工作器 |
| {{docsPath}}/experiments/plans/openresponses-gateway.md | OpenResponses 网关 |
| {{docsPath}}/experiments/plans/pty-process-supervision.md | PTY 进程监督 |
| {{docsPath}}/experiments/plans/session-binding-channel-agnostic.md | 会话绑定通道无关 |
| {{docsPath}}/experiments/proposals/acp-bound-command-auth.md | ACP 绑定命令认证 |
| {{docsPath}}/experiments/proposals/model-config.md | 模型配置 |
| {{docsPath}}/experiments/research/memory.md | 内存研究 |

### Refactor - 重构
重构计划

| 文件 | 描述 |
|------|------|
| {{docsPath}}/refactor/clawnet.md | ClawNet 重构 |
| {{docsPath}}/refactor/exec-host.md | 执行主机重构 |
| {{docsPath}}/refactor/outbound-session-mirroring.md | 出站会话镜像 |
| {{docsPath}}/refactor/plugin-sdk.md | 插件 SDK 重构 |
| {{docsPath}}/refactor/strict-config.md | 严格配置 |

### Other - 其他文档
其他相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/auth-credential-semantics.md | 认证凭证语义 |
| {{docsPath}}/brave-search.md | Brave 搜索 |
| {{docsPath}}/ci.md | CI 配置 |
| {{docsPath}}/date-time.md | 日期时间 |
| {{docsPath}}/index.md | 文档首页 |
| {{docsPath}}/logging.md | 日志 |
| {{docsPath}}/network.md | 网络 |
| {{docsPath}}/perplexity.md | Perplexity |
| {{docsPath}}/pi-dev.md | Pi 开发 |
| {{docsPath}}/pi.md | Pi |
| {{docsPath}}/prose.md | Prose |
| {{docsPath}}/tts.md | TTS |
| {{docsPath}}/vps.md | VPS |

### Security - 安全
安全相关文档

| 文件 | 描述 |
|------|------|
| {{docsPath}}/security/CONTRIBUTING-THREAT-MODEL.md | 贡献威胁模型 |
| {{docsPath}}/security/README.md | 安全说明 |
| {{docsPath}}/security/THREAT-MODEL-ATLAS.md | 威胁模型图集 |
| {{docsPath}}/security/formal-verification.md | 形式化验证 |