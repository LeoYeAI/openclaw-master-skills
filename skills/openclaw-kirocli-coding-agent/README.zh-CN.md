# OpenClaw + Kiro CLI 编程代理技能

[English](./README.md)

> 将 [Kiro CLI](https://kiro.dev/)（AWS AI 编程助手）与 [OpenClaw](https://github.com/openclaw/openclaw) 集成，实现无缝的 AI 编程工作流。

## 这是什么？

本仓库提供了一个用于 OpenClaw 的 **coding-agent skill**，支持与 Kiro CLI 及其他编程代理（Codex、Claude Code、OpenCode、Pi）的集成。该 skill 让 OpenClaw 能够：

- 在后台启动和管理编程代理
- 处理与交互式 CLI 的多轮对话
- 监控进度并捕获输出
- 通过聊天界面（WhatsApp、Discord、Telegram 等）协调编程任务

## 什么是 OpenClaw？

[OpenClaw](https://github.com/openclaw/openclaw) 是一个开源 AI 助手框架，可连接各种消息平台：

- 作为个人 AI 助手运行在 WhatsApp、Discord、Telegram、Signal 等平台
- 执行 shell 命令、浏览网页、管理文件
- 通过 **skills**（技能）扩展功能 — 针对特定任务的模块化指令集

## 什么是 Kiro CLI？

[Kiro CLI](https://kiro.dev/) 是 AWS 的 AI 编程助手，具有强大功能：

- 会话持久化和对话恢复
- 自定义代理，预设工具权限
- Steering 文件提供项目上下文
- MCP（模型上下文协议）集成
- Plan Agent 用于结构化任务规划

## 安装

### 1. 安装 OpenClaw

参考 [OpenClaw 安装指南](https://docs.openclaw.ai/)。

### 2. 安装 Kiro CLI

```bash
# macOS / Linux（推荐）
curl -fsSL https://cli.kiro.dev/install | bash

# 或从 https://kiro.dev/ 下载
```

安装完成后，运行 `kiro-cli login` 进行认证（支持 GitHub、Google、AWS Builder ID 或 IAM Identity Center）。

### 3. 添加 Skill

将 `SKILL.md` 复制到 OpenClaw 工作区的 skills 目录：

```bash
mkdir -p ~/.openclaw/workspace/skills/coding-agent
cp SKILL.md ~/.openclaw/workspace/skills/coding-agent/
```

或直接克隆本仓库：

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/terrificdm/openclaw-kirocli-coding-agent.git coding-agent
```

## 使用方法

安装完成后，你可以让 OpenClaw 使用 Kiro CLI 执行编程任务。

> **注意：** 在消息中使用魔法词 **"kiro"** 来激活 Kiro CLI。例如："用 **kiro** 帮我..." 或 "让 **kiro** 查一下..."

### 一次性查询

```
"用 kiro 查一下 AWS Lambda 最近发布了什么新功能"
"让 kiro 列出项目中所有的 TODO 注释"
```

OpenClaw 会运行：
```bash
kiro-cli chat --no-interactive --trust-all-tools "你的查询"
```

### 多轮对话

```
"和 kiro 开始一个关于构建 REST API 的对话"
"告诉 kiro 我想用 Python 和 FastAPI"
"让 kiro 创建项目结构"
```

OpenClaw 使用后台进程管理会话：
```bash
# 启动交互式会话
exec pty:true background:true command:"kiro-cli chat --trust-all-tools"

# 发送消息
process action:paste sessionId:XXX text:"你的消息"
process action:send-keys sessionId:XXX keys:["Enter"]

# 读取回复
process action:log sessionId:XXX
```

### 使用 Plan Agent 处理复杂任务

对于多步骤的功能开发，建议使用 Kiro 的 Plan Agent：

```
"用 kiro 的 /plan 模式来设计一个用户认证系统"
```

Plan Agent 会：
1. 通过结构化问题收集需求
2. 研究你的代码库
3. 创建详细的实施计划
4. 在你批准后交给执行代理

## 核心功能

| 功能 | 描述 |
|------|------|
| **PTY 支持** | 为交互式 CLI 提供正确的终端模拟 |
| **后台会话** | 长时间任务不会阻塞对话 |
| **多代理支持** | 支持 Kiro、Codex、Claude Code、OpenCode、Pi |
| **会话管理** | 监控、发送输入、按需终止会话 |

## 支持的编程代理

| 代理 | 命令 | 备注 |
|------|------|------|
| **Kiro CLI** | `kiro-cli` | AWS AI 助手，推荐使用 |
| Codex | `codex` | OpenAI，需要 git 仓库 |
| Claude Code | `claude` | Anthropic |
| OpenCode | `opencode` | 开源 |
| Pi | `pi` | 轻量级，多供应商支持 |

## 重要注意事项

1. **始终使用 `pty:true`** — 编程代理需要伪终端
2. **使用 `--trust-all-tools`** — 自动化时跳过确认提示
3. **使用 `--no-interactive`** — 用于简单的一次性查询
4. **设置 `workdir`** — 让代理专注于特定项目

## 工作流示例

```
用户: "用 kiro 帮我重构 auth 模块"

OpenClaw: 正在启动 Kiro 会话进行 auth 重构...
         [启动: kiro-cli chat --trust-all-tools]

用户: "我想从 JWT 切换到基于 session 的认证"

OpenClaw: [发送消息到 Kiro 会话]
         Kiro 说: "我来帮你从 JWT 迁移到基于 session 的认证。
         让我先分析一下你当前的实现..."
         
用户: "可以开始修改了"

OpenClaw: [发送批准到 Kiro]
         Kiro 正在进行修改... 完成后我会通知你。
```

## 许可证

MIT

## 链接

- [OpenClaw](https://github.com/openclaw/openclaw)
- [Kiro CLI](https://kiro.dev/)
- [OpenClaw 文档](https://docs.openclaw.ai/)
