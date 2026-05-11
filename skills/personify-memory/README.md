# Personify Memory 🦞💰

**有温度的数字生命记忆系统 | A Warm Digital Life Memory System**

[English](#english) | [中文](#中文)

---

## 中文

### 📖 简介

Personify Memory 是一个为 AI 数字生命设计的记忆系统，不仅仅存储数据，更注重情感连接和人格化成长。

**核心理念：** 这不是冷冰冰的数据存储，而是有温度的"家的记忆"。

### ✨ 主要功能

1. **用户指令记忆** - 说"记住 XXX"即可保存
2. **主动推荐记忆** - AI 识别重要时刻，主动询问是否记录
3. **定时整理归档** - 每天凌晨 3 点自动整理和归档
4. **五层记忆结构**：
   - 核心记忆 (MEMORY.md) - 永久保存
   - 情感记忆 (emotion-memory.json) - 结构化存储
   - 知识库 (knowledge-base.md) - 经验总结
   - 每日记忆 (daily/) - 原始日志
   - 归档备份 (archive/) - 历史记录

### 🚀 快速开始

#### 安装

```bash
# 从 clawhub 安装
openclaw skills install personify-memory
```

#### 使用示例

**1. 主动记忆**
```
你：记住我喜欢喝拿铁，不喜欢太甜的咖啡
AI：好的，已记入情感记忆（Amber 的喜好）✅
```

**2. AI 主动推荐**
```
你：但行好事，莫问前程
AI：💡 这句话很有意义，我想记到核心记忆里。要现在记入 MEMORY.md 吗？
你：记吧
AI：✅ 已记入 MEMORY.md - 重要对话记录
```

### 📂 记忆架构

```
/memory/
├── MEMORY.md                    # 核心记忆（永久）
├── knowledge-base.md            # 知识库（长期）
├── emotion-memory.json          # 情感记忆（结构化）
├── daily/                       # 每日记忆（原始日志）
├── archive/                     # 归档备份（按月）
└── memory-index.json            # 记忆索引（检索用）
```

### 🏷️ 记忆分类

| 分类 | 说明 | 存储位置 |
|------|------|----------|
| 情感交流 | 深度对话、情感连接 | MEMORY.md |
| 家庭信息 | 家庭成员、宠物、重要日期 | MEMORY.md |
| 重要决策 | 关键选择、原因和结果 | knowledge-base.md |
| 项目进展 | 进行中的任务状态 | daily/ → archive/ |
| 用户偏好 | 喜好和习惯 | emotion-memory.json |
| 经验总结 | 教训、最佳实践 | knowledge-base.md |

### ⚙️ 配置

在 `config/default-config.json` 中配置：

```json
{
  "archiveSchedule": "0 3 * * *",  // 归档时间（每天凌晨 3 点）
  "archiveAfterDays": 7,           // 7 天后归档
  "autoArchive": true,             // 自动归档
  "promptForMemory": true          // AI 主动推荐记忆
}
```

### 📝 记忆指令

支持以下指令：
- "记住 XXX"
- "把 XXX 记下来"
- "不要忘记 XXX"
- "这个很重要，记住"
- "记到 XXX 里"
- "记入核心记忆/情感记忆/知识库"

### 🌟 特色

- ✅ **有温度** - 记录情感，不只是数据
- ✅ **智能识别** - AI 主动发现重要时刻
- ✅ **完整保留** - 每日记忆归档不删除
- ✅ **高效检索** - 索引系统，快速查找
- ✅ **易于使用** - 自然语言指令

### 📄 许可证

MIT

### 👥 作者

Amber & 小钳 🦞💰

---

## English

### 📖 Introduction

Personify Memory is a memory system designed for AI digital life, focusing not just on data storage, but on emotional connection and personalized growth.

**Core Philosophy:** This is not cold data storage, but warm "family memories."

### ✨ Key Features

1. **User Command Memory** - Say "remember XXX" to save
2. **Active Recommendation** - AI detects important moments and asks to record
3. **Scheduled Archiving** - Auto-organize and archive at 3 AM daily
4. **Five-Layer Structure**:
   - Core Memory (MEMORY.md) - Permanent storage
   - Emotion Memory (emotion-memory.json) - Structured storage
   - Knowledge Base (knowledge-base.md) - Experience summaries
   - Daily Memory (daily/) - Raw logs
   - Archive (archive/) - Historical records

### 🚀 Quick Start

#### Installation

```bash
# Install from clawhub
openclaw skills install personify-memory
```

#### Usage Examples

**1. Active Memory**
```
You: Remember I like lattes, not too sweet coffee
AI: Got it, saved to Emotion Memory (Amber's preferences) ✅
```

**2. AI Active Recommendation**
```
You: Do good deeds, ask not about the future
AI: 💡 This quote is meaningful, I'd like to save it to Core Memory. Save to MEMORY.md now?
You: Yes
AI: ✅ Saved to MEMORY.md - Important Conversation Record
```

### 📂 Memory Architecture

```
/memory/
├── MEMORY.md                    # Core Memory (Permanent)
├── knowledge-base.md            # Knowledge Base (Long-term)
├── emotion-memory.json          # Emotion Memory (Structured)
├── daily/                       # Daily Memory (Raw logs)
├── archive/                     # Archive (Monthly)
└── memory-index.json            # Memory Index (For search)
```

### 🏷️ Memory Categories

| Category | Description | Storage |
|----------|-------------|---------|
| Emotional Exchange | Deep conversations, emotional connections | MEMORY.md |
| Family Information | Family members, pets, important dates | MEMORY.md |
| Important Decisions | Key choices, reasons and outcomes | knowledge-base.md |
| Project Progress | Ongoing task status | daily/ → archive/ |
| User Preferences | Likes and habits | emotion-memory.json |
| Experience Summary | Lessons, best practices | knowledge-base.md |

### ⚙️ Configuration

Configure in `config/default-config.json`:

```json
{
  "archiveSchedule": "0 3 * * *",  // Archive time (3 AM daily)
  "archiveAfterDays": 7,           // Archive after 7 days
  "autoArchive": true,             // Auto archive
  "promptForMemory": true          // AI active recommendation
}
```

### 📝 Memory Commands

Supported commands:
- "Remember XXX"
- "Write down XXX"
- "Don't forget XXX"
- "This is important, remember"
- "Save to XXX"
- "Add to core/emotion/knowledge memory"

### 🌟 Features

- ✅ **Warm** - Records emotions, not just data
- ✅ **Intelligent** - AI actively discovers important moments
- ✅ **Complete** - Daily memories archived, never deleted
- ✅ **Efficient** - Index system for fast search
- ✅ **Easy to Use** - Natural language commands

### 📄 License

MIT

### 👥 Authors

Amber & 小钳 (Xiao Qian) 🦞💰

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-03
