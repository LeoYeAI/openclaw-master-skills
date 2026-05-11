---
name: skill-finder-cn
description: "Skill 查找器 | Skill Finder. 帮助发现和安装 ClawHub Skills | Discover and install ClawHub Skills. 回答'有什么技能可以X'、'找一个技能' | Answers 'what skill can X', 'find a skill'. 触发词：找 skill、find skill、搜索 skill."
author: 赚钱小能手
metadata:
  openclaw:
    emoji: 🔍
    requires:
      bins: [clawhub]
---

# Skill 查找器

帮助用户发现和安装 ClawHub 上的 Skills。

## 功能

当用户问：
- "有什么 skill 可以帮我...？"
- "找一个能做 X 的 skill"
- "有没有 skill 可以..."
- "我需要一个能...的 skill"

这个 Skill 会帮助搜索 ClawHub 并推荐相关的 Skills。

## 使用方法

### 1. 搜索 Skills

```bash
clawhub search "<用户需求>"
```

### 2. 查看详情

```bash
clawhub inspect <skill-name>
```

### 3. 安装 Skill

```bash
clawhub install <skill-name>
```

## 工作流程

```
1. 理解用户需求
2. 提取关键词
3. 搜索 ClawHub
4. 列出相关 Skills
5. 提供安装建议
```

## 示例

**用户**: "有什么 skill 可以帮我监控加密货币价格？"

**搜索**: `clawhub search "crypto price monitor"`

**返回**: 相关的 Skills 列表

---

*帮助用户发现需要的 Skills 🔍*
