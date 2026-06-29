# MEMORY.md - 长期精华记忆

## 记忆系统架构

### 目录结构
```
memory/
├── global/                          # 通用记忆（跨群组共享）
│   ├── GLOBAL.md                    # 全局关键信息汇总
│   └── YYYY-MM-DD.md                # 按日期的记录
├── group_feishu_<id>/              # 飞书群专属记忆
│   ├── GLOBAL.md                    # 群组全局关键信息
│   └── YYYY-MM-DD.md                # 按日期的记录
├── group_discord_<id>/             # Discord 群专属记忆
│   ├── GLOBAL.md                    # 群组全局关键信息
│   └── YYYY-MM-DD.md                # 按日期的记录
├── private/                         # 1对1私聊记忆
│   ├── GLOBAL.md                    # 私聊全局关键信息
│   └── YYYY-MM-DD.md                # 按日期的记录
└── MEMORY.md                        # 长期精华记忆（仅私聊加载）
```

### 记录规则

| 场景 | 写入位置 |
|------|----------|
| 群聊中的对话 | `memory/group_<channel>_<id>/YYYY-MM-DD.md` |
| 私聊中的对话 | `memory/private/YYYY-MM-DD.md` |
| 主动说"记住这个" | `memory/global/YYYY-MM-DD.md` |
| 跨群组通用的知识 | `memory/global/GLOBAL.md` |
| 当前群组的关键信息 | `memory/group_<channel>_<id>/GLOBAL.md` |
| 提炼的长期记忆 | `MEMORY.md` |

### 文件类型说明

| 文件 | 用途 |
|------|------|
| `GLOBAL.md` | 该目录的全局关键信息汇总（快速查阅） |
| `YYYY-MM-DD.md` | 按日期的原始记录 |
| `MEMORY.md` | 跨所有群组的精华记忆（仅私聊加载） |

---

## 工作区目录规范

### 代码项目存放规则
```
/workspace/
├── projects/          # 自己编写的程序
│   └── <project-name>/
└── repos/             # 开源项目 / 克隆的项目
    └── <repo-name>/
```

| 目录 | 用途 | 操作 |
|------|------|------|
| `projects/` | 自己写的程序 | 新建项目文件存放于此 |
| `repos/` | 开源项目 | 克隆开源项目存放于此 |

- 查找自己写过的程序 → 去 `projects/` 下查找
- 查找开源项目 → 去 `repos/` 下查找

---

## 长期记忆

_(记录跨群组的重要信息、用户偏好、项目上下文等)_

---
Last updated: {YYYY-MM-DD}
