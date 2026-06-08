# OpenClaw Agent Skill 🦞

[English](README.md) | 中文文档

一套完整的 **Agent Skill**，用于安装、配置、运维和排障 [OpenClaw](https://github.com/openclaw/openclaw) —— 一个自托管的多通道 AI Agent 网关。

## 这是什么？

这是一个专为 AI 编程助手（如 Claude + Antigravity）设计的 Agent Skill。安装后，AI 助手会获得 OpenClaw 的深度知识，能帮你完成：

- 🔧 **安装与升级** — 安装、升级或迁移 OpenClaw
- ⚙️ **配置管理** — 编辑 `openclaw.json`、设置模型、管理密钥
- 📡 **频道管理** — 配置 WhatsApp、Telegram、Discord、Slack、iMessage 等 20+ 频道
- 🚀 **Gateway 运维** — 启动、停止、重启、健康检查、远程访问
- 🤖 **多 Agent 路由** — 配置多个 Agent，隔离工作区和会话
- 🔒 **安全加固** — 审计、访问控制、Token 和密钥管理
- 🔍 **故障排查** — 诊断和修复 CLI 及 Gateway 的常见错误

## Skill 结构

```
OpenClaw-Skill/
├── SKILL.md                     # 主入口（核心工作流、命令速查、故障签名表）
└── references/
    ├── architecture.md          # Gateway 架构、WebSocket 协议、配对、不变量
    ├── agent_runtime.md         # Agent 运行时、引导文件、Agent Loop、Hooks、超时
    ├── bonjour.md               # Bonjour/mDNS：TXT 键、广域 DNS-SD、调试
    ├── channel_routing.md       # 频道路由、Session Key、Mattermost、BlueBubbles
    ├── channels.md              # 20+ 频道配置指南（WhatsApp、Telegram、Discord 等）
    ├── clawhub.md               # ClawHub 公共 Skill 注册中心、CLI 命令
    ├── gateway_internals.md     # 网络模型、Gateway 锁、健康检查、Doctor、日志、后台执行
    ├── gateway_ops.md           # Gateway 运维、服务管理
    ├── heartbeat.md             # 心跳：配置、投递、可见性、HEARTBEAT.md
    ├── media.md                 # 媒体：相机拍摄、图像、音频/语音笔记、转录
    ├── memory.md                # 记忆系统、向量搜索、混合 BM25、QMD 后端
    ├── model_failover.md        # 模型故障转移、OAuth、认证配置、冷却策略
    ├── multi_agent.md           # 多 Agent 路由、Bindings、Agent 配置
    ├── pairing.md               # Gateway 配对：节点审批、CLI、API、自动审批
    ├── polls.md                 # 投票功能（Telegram、WhatsApp、Discord、MS Teams）
    ├── presence_discovery.md    # Presence 系统、发现机制（Bonjour/Tailscale）
    ├── providers.md             # 20+ 模型提供商（Anthropic、OpenAI、Ollama 等）
    ├── queue.md                 # 命令队列：steer/followup/collect 模式
    ├── security.md              # 认证、访问控制、加固基线
    ├── streaming.md             # 块流式传输、分块、合并、预览模式
    ├── thinking.md              # 思考级别、详细模式指令、推理可见性
    ├── tui.md                   # TUI：快捷键、斜杠命令、选择器、本地 Shell
    ├── voice.md                 # Talk Mode（语音交互）+ Voice Wake（唤醒词）
    └── ... (共 51 个参考文件)
```

**共计约 5,500+ 行**结构化参考文档，覆盖 OpenClaw 所有核心功能。

## 安装方法

### Antigravity（Claude）用户

将 Skill 文件夹复制到 Antigravity 的 skills 目录：

```bash
# 克隆仓库
git clone https://github.com/win4r/OpenClaw-Skill.git

# 复制到 skills 目录
cp -r OpenClaw-Skill ~/.gemini/antigravity/skills/openclaw
```

安装后，当你提到 OpenClaw 相关任务时，Skill 会自动触发。

### 其他 AI 助手

`SKILL.md` 和 `references/` 中的结构化文档可以适配到任何支持 Skill/知识注入的 AI 助手。

## 使用示例

安装后，自然语言提问即可：

| 你说的话 | AI 的操作 |
|---|---|
| "帮我升级 OpenClaw" | 执行 `npm install -g openclaw@latest`、`openclaw doctor`、重启 Gateway、验证状态 |
| "配置一个 Telegram Bot" | 引导创建 Bot、设置 Token、写入配置、验证连接 |
| "Gateway 没有响应" | 运行诊断命令梯子：status → logs → doctor → channels probe |
| "加固 OpenClaw 安全配置" | 运行安全审计、应用加固基线、修复权限 |
| "添加第二个 Agent 用于工作" | 创建 Agent、设置工作区、配置 Bindings、重启 |
| "EADDRINUSE 错误" | 识别端口冲突，执行 `openclaw gateway --force` 或更换端口 |

## 常用命令速查

```bash
# 状态与健康检查
openclaw status                    # 总体状态
openclaw gateway status            # Gateway 守护进程状态
openclaw doctor                    # 诊断问题
openclaw channels status --probe   # 频道健康检查

# Gateway 管理
openclaw gateway install           # 安装为系统服务
openclaw gateway start/stop/restart

# 配置管理
openclaw config get <路径>          # 读取配置值
openclaw config set <路径> <值>     # 设置配置值
openclaw configure                 # 交互式向导

# 安全
openclaw security audit            # 检查安全状况
openclaw security audit --fix      # 自动修复问题
openclaw secrets reload            # 重新加载密钥引用

# 频道
openclaw channels add              # 添加频道（向导模式）
openclaw channels login            # WhatsApp QR 配对
openclaw channels list             # 显示已配置频道

# 模型
openclaw models set <模型>          # 设置默认模型
openclaw models status --probe     # 检查认证状态
```

## 文档来源

本 Skill 基于 [OpenClaw 官方文档](https://docs.openclaw.ai/) 构建，涵盖：

- [安装](https://docs.openclaw.ai/install)
- [Gateway 架构](https://docs.openclaw.ai/concepts/architecture)
- [Agent 运行时](https://docs.openclaw.ai/concepts/agent)
- [Agent Loop](https://docs.openclaw.ai/concepts/agent-loop)
- [配置](https://docs.openclaw.ai/gateway/configuration)
- [频道](https://docs.openclaw.ai/channels)
- [模型提供商](https://docs.openclaw.ai/providers)
- [模型故障转移与 OAuth](https://docs.openclaw.ai/concepts/model-failover)
- [工具](https://docs.openclaw.ai/tools)
- [思考级别](https://docs.openclaw.ai/tools/thinking)
- [命令队列](https://docs.openclaw.ai/concepts/queue)
- [流式传输与分块](https://docs.openclaw.ai/concepts/streaming)
- [记忆与向量搜索](https://docs.openclaw.ai/concepts/memory)
- [ClawHub 注册中心](https://docs.openclaw.ai/tools/clawhub)
- [多 Agent 路由](https://docs.openclaw.ai/concepts/multi-agent)
- [Talk Mode 与 Voice Wake](https://docs.openclaw.ai/nodes/talk)
- [投票功能](https://docs.openclaw.ai/automation/poll)
- [Presence 与发现机制](https://docs.openclaw.ai/concepts/presence)
- [ACP Agents](https://docs.openclaw.ai/pi)
- [安全](https://docs.openclaw.ai/gateway/security)
- [故障排查](https://docs.openclaw.ai/gateway/troubleshooting)
- [CLI 参考](https://docs.openclaw.ai/cli)

## 许可证

本 Skill 免费提供给 AI 助手使用。OpenClaw 本身采用 [MIT 许可证](https://github.com/openclaw/openclaw/blob/main/LICENSE)。

## 贡献

欢迎 Issue 和 PR！如果 OpenClaw 发布了新功能或变更，请随时更新 references 文件。
