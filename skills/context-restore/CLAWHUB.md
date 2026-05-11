# Context Restore - ClawHub 市场页面

---

## 🏷️ Skill 信息

| 属性 | 值 |
|------|-----|
| **名称** | context-restore |
| **版本** | 1.0.0 |
| **作者** | OpenClaw Team |
| **许可证** | MIT |
| **兼容平台** | OpenClaw, Claude Code, Claude CLI |
| **依赖** | Python 3.8+ |

---

## 📖 描述

**Context Restore** 是一个智能上下文恢复技能，帮助用户在开启新会话后快速恢复到之前的工作状态。

当用户的对话上下文被压缩保存后，这个技能可以：
- 📊 读取并解析压缩的上下文文件
- 🚀 提取关键项目、任务和操作记录
- 📋 生成结构化的工作状态报告
- 🔄 支持多种恢复级别（极简/标准/完整）
- ⏰ 提供时间线回顾功能
- 🔔 支持自动监控和变化检测

**核心价值**：让用户无需重复解释背景，秒级恢复到之前的工作状态。

---

## ✨ 功能特点

### 🔹 多级别恢复
- **Minimal（极简）**：核心状态一句话概括
- **Normal（标准）**：项目+任务+操作记录（默认）
- **Detailed（完整）**：完整上下文+7天时间线

### 🔹 智能内容提取
- 自动识别项目状态和进度
- 提取待办任务列表
- 解析最近操作记录
- 高亮 MEMORY.md 引用

### 🔹 时间线功能（Phase 2）
- 按天/周/月聚合历史操作
- 过滤特定关键词内容
- 对比两个版本的上下文差异

### 🔹 自动监控（Phase 3）
- 检测上下文变化
- 自动/半自动恢复模式
- Cron 定时任务集成
- 外部通知支持

### 🔹 多平台适配
- Telegram：自动消息分块
- Discord：Embed 格式
- CLI：纯文本树形结构
- WhatsApp：简化格式

---

## 🎯 使用场景

| 场景 | 用户需求 | 恢复内容 |
|------|---------|---------|
| **跨天继续工作** | 昨天做到哪了？ | 项目进度、待办任务 |
| **任务切换后回来** | 之前在做什么？ | 当前任务状态、关键文件 |
| **中断后继续** | 接着刚才的聊 | 对话历史节点 |
| **周期性回顾** | 这周做了哪些事？ | 时间线摘要、成果列表 |
| **状态确认** | 现在什么情况？ | 活跃项目、待办列表 |

---

## 🚀 快速开始

### 安装

```bash
# 方式一：通过 ClawdHub 安装（推荐）
clawdhub install context-restore

# 方式二：手动安装
git clone https://github.com/openclaw/context-restore.git ~/.openclaw/skills/context-restore
```

### 使用

```bash
# 基础使用 - 恢复上下文
/context-restore

# 指定恢复级别
/context-restore --level detailed
/context-restore -l minimal

# 命令行工具
python scripts/restore_context.py --level normal

# 获取结构化摘要
python scripts/restore_context.py --summary

# 用户确认流程
python scripts/restore_context.py --confirm

# Telegram 消息分块
python scripts/restore_context.py --telegram
```

---

## 📖 使用示例

### 示例 1：日常继续工作

**用户输入**：
```
继续之前的工作
```

**技能输出**：
```
✅ 上下文已恢复

📊 压缩信息:
- 原始消息: 45
- 压缩后: 12
- 压缩率: 26.7%

🔄 最近操作:
- 完成数据管道测试
- 部署新功能到生产环境
- 添加 3 个新 cron 任务

🚀 当前项目:
1. Hermes Plan - 数据分析助手（进度：80%）
2. Akasha Plan - 自主新闻系统（进度：45%）

📋 待办任务:
- [高] 编写数据管道测试用例
- [中] 设计 Akasha UI 组件
```

### 示例 2：时间线回顾

**命令**：
```bash
/context-restore --level detailed --timeline --period weekly
```

**输出**：
```
📅 Week 6 (Feb 2-8)
├── ✅ 完成数据管道测试
├── ✅ 部署新功能到生产环境
└── 🚀 项目: Hermes Plan, Akasha Plan

📅 Week 5 (Jan 26 - Feb 1)
├── ✅ 启动 Akasha UI 改进
└── 🚀 项目: Hermes Plan
```

### 示例 3：上下文对比

**命令**：
```bash
/context-restore --diff old.json new.json
```

**输出**：
```
📊 上下文对比报告

时间差: 24.0 小时

➕ 新增项目:
- Akasha Plan

➖ 移除项目:
- Morning Brief

🔄 修改项目:
- Hermes Plan: 进度 70% → 80%

📝 操作变化:
- 新增 5 个操作
- 移除 1 个操作
```

---

## 🖥️ 屏幕截图

### 截图 1：Normal 级别恢复

```
┌─────────────────────────────────────────────┐
│ ✅ 上下文已恢复                              │
├─────────────────────────────────────────────┤
│ 📊 压缩信息:                                │
│    原始消息: 45 → 压缩后: 12 (26.7%)        │
│                                             │
│ 🔄 最近操作:                                │
│    • 完成数据管道测试                       │
│    • 部署新功能到生产环境                    │
│    • 添加 3 个 cron 任务                   │
│                                             │
│ 🚀 项目:                                    │
│    1. Hermes Plan (80%)                    │
│    2. Akasha Plan (45%)                    │
│                                             │
│ 📋 待办:                                    │
│    • [高] 编写测试用例                      │
│    • [中] 设计 UI 组件                      │
└─────────────────────────────────────────────┘
```

### 截图 2：Detailed 级别 + 时间线

```
┌─────────────────────────────────────────────┐
│ ✅ 上下文已恢复（详细模式）                  │
├─────────────────────────────────────────────┤
│ 📊 会话概览:                                │
│    当前会话: #2026-02-06-main               │
│    活跃会话: 3个                            │
│    最后活动: 2小时前                        │
├─────────────────────────────────────────────┤
│ 📅 Week 6 (Feb 2-8)                        │
│    ├── ✅ 完成数据管道测试                  │
│    ├── ✅ 部署新功能                        │
│    └── 🚀 Hermes, Akasha                   │
│                                             │
│ 📅 Week 5 (Jan 26 - Feb 1)                 │
│    ├── ✅ 启动 UI 改进                      │
│    └── 🚀 Hermes Plan                      │
└─────────────────────────────────────────────┘
```

### 截图 3：自动监控通知

```
┌─────────────────────────────────────────────┐
│ 🔔 上下文变化检测                            │
├─────────────────────────────────────────────┤
│ 📁 文件: latest_compressed.json             │
│ ⏰ 检测时间: 2026-02-07 10:30               │
│                                             │
│ 🔄 检测到变化!                              │
│    • 新增项目: Akasha Plan                 │
│    • 进度更新: Hermes 70%→80%              │
│                                             │
│ 💡 自动恢复已启用，输入 /context-restore    │
│    查看详情...                              │
└─────────────────────────────────────────────┘
```

---

## 🔧 API 参考

### Python API

```python
from restore_context import (
    restore_context,
    get_context_summary,
    extract_timeline,
    compare_contexts,
    filter_context
)

# 基础恢复
report = restore_context(filepath, level="normal")

# 获取结构化摘要
summary = get_context_summary(filepath)
# 返回: {success, metadata, operations, projects, tasks, timeline}

# 提取时间线
timeline = extract_timeline(content, period="weekly", days=30)

# 对比两个版本
diff = compare_contexts(old_file, new_file)

# 过滤内容
filtered = filter_context(content, "Hermes")
```

### 命令行参数

```bash
python restore_context.py [选项]

基础选项：
  --file, -f      上下文文件路径（默认）
  --level, -l     恢复级别（minimal/normal/detailed）
  --output, -o    输出文件路径
  --summary, -s   输出结构化摘要（JSON）
  --confirm       添加用户确认流程
  --telegram      Telegram 消息分块

Phase 2 选项：
  --timeline      启用时间线视图
  --period        聚合周期（daily/weekly/monthly）
  --filter        过滤关键词
  --diff          对比两个版本

Phase 3 选项：
  --auto          自动模式检测变化
  --quiet         静默模式
  --check-only   仅检查变化
  --install-cron  安装 cron 自动监控
```

---

## 📦 安装依赖

- Python 3.8+
- 无外部依赖（纯标准库）

---

## 🔗 相关技能

| 技能 | 关系 | 说明 |
|------|------|------|
| context-save | 依赖 | 保存上下文到文件 |
| context-monitor | 补充 | 自动监控上下文变化 |
| memory_get | 依赖 | 读取 MEMORY.md |
| memory_search | 依赖 | 搜索历史记录 |

---

## 📄 许可证

MIT License - 详见项目仓库

---

## 🐛 问题反馈

如有问题或建议，请提交 Issue：
- GitHub: https://github.com/openclaw/context-restore/issues
- Email: support@openclaw.ai

---

## 📖 完整文档

- [README.md](README.md) - 完整使用指南
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速上手
- [SKILL.md](SKILL.md) - 技能详细文档

---

*最后更新：2026-02-07*
