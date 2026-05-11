# OpenClaw Workflow

🔀 确定性工作流引擎 - 运行 YAML 自动化流程

## 概述

OpenClaw Workflow 是一个符合 OpenClaw / AgentSkills 规范的确定性工作流引擎。在不破坏 OpenClaw 灵活性的前提下，按 YAML 剧本执行 100% 确定性逻辑。

## 功能特性

- **条件分支** — If-Else 逻辑
- **循环遍历** — ForEach / Times 循环
- **脚本执行** — Shell / Python 脚本
- **LLM 调用** — 直接调用语言模型
- **Agent 调用** — 调用 OpenClaw Agent
- **Subagent** — 创建并行子代理执行任务
- **HTTP 请求** — 发送 REST API 请求
- **消息发送** — iMessage / Telegram 等渠道通知

## 快速开始

```bash
# 安装依赖
pip install -r scripts/requirements.txt

# 运行工作流
python3 scripts/openclaw_workflow.py execute <workflow.yaml>

# 验证语法
python3 scripts/openclaw_workflow.py validate <workflow.yaml>

# 列出可用工作流
python3 scripts/openclaw_workflow.py list
```

## 文档

详细使用说明请参阅 [SKILL.md](./SKILL.md)

## 许可证

本项目采用 **CC BY-NC 4.0** 许可证 — 署名-非商业性使用

详见 [LICENSE](./LICENSE) 文件

## 作者

OpenClaw Team
