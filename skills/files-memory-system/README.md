# Files Memory System

> 多上下文记忆管理系统，让 OpenClaw Agent 在多群组场景下井井有条

[![Version](https://img.shields.io/badge/version-1.14.0-blue.svg)](https://clawhub.com/skills/files-memory-system)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 项目简介

**Files Memory System** 是一个为 OpenClaw Agent 设计的**多上下文记忆管理系统**，解决 AI 助手在多个群组中缺乏**记忆持久化**的问题。

> OpenClaw 本身已有**会话隔离**（不同群组之间不会互相干扰），但每次新会话都是"一张白纸"，没有历史记忆。

### 核心能力

- 🏠 **群组隔离记忆** - 每个群组有独立的记忆空间
- 🌍 **全局共享记忆** - 跨群组的通用知识
- 🔒 **技能隔离** - 每个群组可以有专属的技能
- 📁 **项目隔离** - 每个群组可以有专属的项目目录
- 🤖 **自动加载** - 进入群聊自动加载该群的记忆

## 🚀 快速开始

### 安装

```bash
# 从 ClawHub 安装
clawhub install files-memory-system

# 运行安装脚本
cd /workspace/skills/files-memory-system
./scripts/install.sh
```

安装完成后，系统会自动：
- 创建私聊记忆目录
- 创建全局共享记忆目录
- 注册到 AGENTS.md（Agent 启动时自动识别）

### 使用

**无需手动操作！** 当 Agent 进入群聊时，会自动：
1. 加载该群组的 GLOBAL.md
2. 加载今日和昨日的对话记录
3. 加载跨群组全局记忆

你只需要正常使用 AI，其他的交给系统自动处理。

## 📂 目录结构

```
/workspace/
├── memory/
│   ├── global/                    # 全局共享记忆
│   │   ├── GLOBAL.md
│   │   └── YYYY-MM-DD.md
│   ├── group_feishu_<id>/         # 群组专属记忆
│   │   ├── GLOBAL.md
│   │   ├── YYYY-MM-DD.md
│   │   ├── skills/
│   │   └── repos/
│   └── private/                   # 私聊记忆
│       ├── GLOBAL.md
│       └── YYYY-MM-DD.md
├── MEMORY.md                      # 长期核心记忆（仅私聊）
└── skills/                        # 全局共享技能
```

## 💡 使用场景

### 场景1：群聊中克隆项目

**用户说**："克隆 https://github.com/user/project"

**系统自动**：
- 识别当前群组
- 克隆到该群组的 repos/ 目录
- 更新 GLOBAL.md 记录
- 其他群组完全不可见

### 场景2：安装群组专属技能

```bash
clawhub install inkos --dir memory/group_feishu_<id>/skills
```

该技能仅当前群组可用，完美隔离。

### 场景3：跨群组共享信息

将信息从群组移动到 `memory/global/GLOBAL.md`，所有群组都能访问。

## 🔧 可用脚本

| 脚本 | 用途 |
|------|------|
| `install.sh` | 安装 skill，初始化基础目录 |
| `post-install.sh` | 自注册到 AGENTS.md |
| `init-group-memory.sh` | 初始化群组记忆结构 |
| `ensure-group-memory.sh` | 确保群组目录存在（按需创建） |
| `ensure-private-memory.sh` | 确保私聊目录存在 |
| `ensure-global-memory.sh` | 确保全局目录存在 |
| `auto-clone.sh` | 自动克隆仓库到正确位置 |

## 🛠️ 开发

### 环境要求

- OpenClaw >= 2026.3.0
- Bash >= 4.0
- Git

### 开发流程

```bash
# 1. 克隆源码
git clone https://gitee.com/wxwzl-ai/files-memory-system.git
cd files-memory-system

# 2. 修改代码
# ...

# 3. 提交并推送
git add .
git commit -m "feat: your changes"
git push origin master

# 4. 发布到 ClawHub
clawhub publish . --version x.x.x
```

### 目录规范

- **原始源码**：`~/.openclaw/skills/files-memory-system/`
- **工作区**：`/workspace/skills/files-memory-system/`（通过 clawhub 安装）
- **发布**：ClawHub Registry

## 📝 记录规则

| 场景 | 写入位置 |
|------|----------|
| 群聊对话 | `memory/group_<channel>_<id>/YYYY-MM-DD.md` |
| 私聊对话 | `memory/private/YYYY-MM-DD.md` |
| 跨群组通用信息 | `memory/global/GLOBAL.md` |
| 长期精华记忆 | `MEMORY.md` |

## 🔍 记忆加载优先级

1. **当前群组目录**（最高优先级）
2. **全局目录**
3. **其他群组**（仅在必要时）

## 🔒 安全特性

- `MEMORY.md` **仅在私聊中加载**
- 群组技能完全隔离
- 群组解散后记忆保留（历史审计）
- 敏感信息过滤（自动）

## 📚 文档

- [用户使用指南](references/USER_GUIDE.md) - 面向最终用户
- [架构设计说明](references/architecture.md) - 面向开发者
- [SKILL.md](SKILL.md) - Skill 完整技术文档

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

[MIT](LICENSE) © wxwzl

## 🔗 链接

- **GitHub**: https://gitee.com/wxwzl-ai/files-memory-system
- **ClawHub**: https://clawhub.com/skills/files-memory-system
- **问题反馈**: https://gitee.com/wxwzl-ai/files-memory-system/issues

---

> **记忆口诀**：群聊产出归群管，私聊产出归私管，全局共享放 global
