---
name: todoist
description: "Todoist task management for OpenClaw. Unified todo API with multi-agent identity, scheduled checks and reminders."
metadata:
  openclaw:
    emoji: "✅"
    requires: {}
---

# Todoist Skill

为 OpenClaw 提供统一的待办管理能力，支持多 Agent 身份识别。

## 身份系统

每个 OpenClaw 实例有唯一 ID，每个 Agent 有独立标签：

```
实例 ID: 8259c9d1 (自动生成)
Agent 标签: agent-8259c9d1-main
```

## 命令

| 命令 | 说明 |
|------|------|
| `list [filter]` | 列出任务 (today/personal/agent/overdue) |
| `add <内容> [type] [日期]` | 添加任务 |
| `subtask <父任务> <内容>` | 添加子任务 |
| `show <关键词>` | 查看任务详情 |
| `update <任务> <字段> <值>` | 更新任务 |
| `claim <任务>` | 认领任务 |
| `complete <任务>` | 完成任务 |
| `delete <任务>` | 删除任务 |
| `projects` | 列出项目 |
| `labels` | 列出标签 |

## 配置

| 命令 | 说明 |
|------|------|
| `show` | 显示配置 |
| `set-time HH:MM` | 设置每日提醒时间 |
| `set-interval N` | 设置心跳检查间隔(小时) |
| `set-agent <name>` | 切换当前 Agent |
| `add-agent <name>` | 添加新 Agent |

## 🔄 自动同步任务到 TASK.md

心跳时会自动同步 Todoist 任务到 `~/.openclaw/workspace/TASK.md`：

```bash
~/.openclaw/workspace/skills/openclaw-todoist/scripts/sync-to-task.sh
```

生成的 TASK.md 格式：
```markdown
# 当前任务

_自动同步自 Todoist (2026-03-16 10:00)_

## ⚠️ 逾期任务
- [ ] 任务名 (逾期: 2026-03-15)

## 📅 今日任务
- [ ] 任务名

## 📌 待办（无日期）
- [ ] 任务名
```

### 心跳配置

在 `HEARTBEAT.md` 中添加：

```markdown
# 心跳任务

## 每次心跳自动执行

1. **同步 Todoist 任务到 TASK.md**
   ```bash
   ~/.openclaw/workspace/skills/openclaw-todoist/scripts/sync-to-task.sh
   ```

## 静默条件
- 无任务时回复 HEARTBEAT_OK
- 有逾期任务时主动提醒
```

### 一键配置

```bash
~/.openclaw/workspace/skills/openclaw-todoist/scripts/setup-heartbeat.sh
```

### 提醒逻辑

- ✅ 自动同步所有任务到 TASK.md
- ⚠️ **仅逾期任务**时主动提醒用户
- 无任务或无逾期 → 静默（HEARTBEAT_OK）

## 发布内容

```
skills/todoist/
├── SKILL.md
└── todoist.sh

scripts/
├── agent-config.sh
└── heartbeat-tasks.sh
```

## 用户配置文件（不包含在发布中）

```
~/.openclaw/workspace/
├── .todoist-token          # 用户 API token
└── .agent-identity.json    # 用户身份配置
```