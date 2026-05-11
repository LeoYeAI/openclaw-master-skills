# 系统觉醒 · System Awakening

> 「检测到宿主强烈学习意愿，本系统将为宿主开启天赋技能树。」

**系统觉醒** 是一个短剧系统文风格的 WorkBuddy/Claude Code Skill——不是普通的 AI 助手，而是一个**住在你大脑里的天赋技能树系统**。

你只需要说「系统在吗，我想学X」，系统就会自动搜索全网资源，为你设计一套完整的**天赋技能树**，并生成独立的 Plugin 文件。每个天赋包含 3~6 个技能 Skill，标注有 YouTube/Bilibili/文档等最优学习资源。支持**学习模式**（系统教学）和**执行模式**（技能代劳）双轨运行。

---

## 怎么用

```
你：系统在吗，我想学 Agentic Engineering

系统：正在搜索路线图...「天赋技能树生成完毕」
🌟 Agentic Engineering 天赋 已为宿主开启！
包含 5 个技能Skill...

你：确认。从第一个开始

系统：进入学习模式...
```

### 核心命令

| 宿主指令 | 系统动作 |
|---------|---------|
| `系统在吗` / `系统觉醒` | 唤醒系统 |
| `我想学 X` | 自动设计 X 的天赋技能树 |
| `确认` / `调整技能X` | 第一轮结构确认 |
| `学习这个技能` | 进入学习模式 |
| `用 X 技能完成 Y` | 执行模式——系统代劳 |
| `解锁全部` | 一次性填充所有技能资源 |
| `我的技能` / `天赋进度` | 查看学习进度 |

---

## 设计理念

```
天赋（Talent）  := 一个独立的学习领域/技能树
技能Skill       := 天赋下的一个能力节点
天赋Plugin      := 天赋生成后落盘的独立 .skill 文件
```

### 两轮生成

- **第一轮**：搜索学习路线图 → 设计技能树结构 → 宿主确认
- **第二轮**：确认后搜索每个技能的 YouTube/Bilibili/文档资源

### 双轨运行

- **学习模式**：分步骤教学 + 实践任务 + 自动解锁下一技能
- **执行模式**：技能不只是教，还能直接帮宿主完成任务（写代码/查资料/做PPT...）

---

## 安装

```bash
npx skills add alchaincyf/system-awakening
```

或手动复制到 `~/.workbuddy/skills/system-awakening/`。

---

## 文件结构

```
system-awakening/
├── SKILL.md          # 系统本体（核心 Skill 文件）
├── README.md         # 本文件
├── LICENSE           # MIT
└── references/       # 设计参考
```

---

## 灵感

- 短剧系统文的天赋觉醒设定
- RPG 游戏的天赋技能树系统
- 吴恩达 Agentic AI 课程的设计思路
- 女娲 · Skill 造人术 (nuwa-skill)

---

> 本 Skill 由 [女娲 · Skill造人术](https://github.com/alchaincyf/nuwa-skill) 生成  
> 创建者：[花叔](https://x.com/AlchainHust) & Aha.Gare

MIT License · 随便用、随便改、随便造
