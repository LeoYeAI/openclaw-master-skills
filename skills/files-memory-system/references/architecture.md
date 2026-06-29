# 记忆系统架构

## 概述

本记忆系统实现了按群组隔离的记忆存储方案，支持多平台（飞书、Discord 等）群聊的独立记忆管理，同时保留跨群组共享的全局记忆能力。此外，系统还支持**群组专属技能隔离**，确保不同群组的技能不会互相污染。

## 目录结构

### 记忆目录

```
memory/
├── global/                          # 通用记忆（跨群组共享）
│   ├── GLOBAL.md                    # 全局关键信息汇总
│   └── YYYY-MM-DD.md                # 按日期的记录
├── group_feishu_<id>/              # 飞书群专属记忆
│   ├── GLOBAL.md                    # 群组全局关键信息
│   ├── YYYY-MM-DD.md                # 按日期的记录
│   ├── skills/                      # ⭐ 群组专属技能（隔离）
│   │   ├── skill-a/
│   │   └── skill-b/
│   └── repos/                       # ⭐ 群组专属项目
│       ├── my-project/              # 本群组创建的代码
│       └── cloned-repo/             # 为本群组克隆的项目
├── group_discord_<id>/             # Discord 群专属记忆
│   ├── GLOBAL.md                    # 群组全局关键信息
│   ├── YYYY-MM-DD.md                # 按日期的记录
│   ├── skills/                      # ⭐ 群组专属技能（隔离）
│   │   └── group-only-skill/
│   └── repos/                       # ⭐ 群组专属项目
├── private/                         # 1对1私聊记忆
│   ├── GLOBAL.md                    # 私聊全局关键信息
│   └── YYYY-MM-DD.md                # 按日期的记录
└── MEMORY.md                        # 长期精华记忆（仅私聊加载）
```

### 工作区目录

```
/workspace/
├── memory/                          # 记忆系统根目录
├── skills/                          # 全局共享技能
│   ├── inkos/
│   └── files-memory-system/
├── projects/                        # 自己编写的程序
│   └── <project-name>/
├── repos/                           # 开源项目 / 克隆的项目
│   └── <repo-name>/
└── MEMORY.md                        # 长期精华记忆
```

## 文件类型说明

| 文件 | 用途 |
|------|------|
| `GLOBAL.md` | 该目录的全局关键信息汇总（快速查阅） |
| `YYYY-MM-DD.md` | 按日期的详细对话记录 |
| `MEMORY.md` | 跨所有群组的长期精华记忆（仅私聊加载） |

## 记录规则

| 场景 | 写入位置 |
|------|----------|
| 群聊中的对话 | `memory/group_<channel>_<id>/YYYY-MM-DD.md` |
| 私聊中的对话 | `memory/private/YYYY-MM-DD.md` |
| 主动说"记住这个" | `memory/global/YYYY-MM-DD.md` |
| 跨群组通用的知识 | `memory/global/GLOBAL.md` |
| 当前群组的关键信息 | `memory/group_<channel>_<id>/GLOBAL.md` |
| 提炼的长期记忆 | `MEMORY.md` |

## 技能隔离系统

### 技能类型

| 类型 | 位置 | 访问范围 | 优先级 |
|------|------|----------|--------|
| 群组专属技能 | `memory/group_<id>/skills/` | 仅当前群组 | 高（覆盖全局） |
| 全局技能 | `/workspace/skills/` | 所有群组 | 低 |

### 技能加载优先级

当在某个群组上下文中时，技能加载顺序：
1. **首先搜索** `memory/group_<id>/skills/` - 群组专属技能
2. **然后搜索** `/workspace/skills/` - 全局共享技能
3. **同名冲突** - 群组版本优先于全局版本

### 技能安装方法

#### 方法1：使用 clawhub CLI
```bash
# 安装到特定群组
clawhub install <skill-name> --dir memory/group_feishu_<id>/skills
```

#### 方法2：手动安装
```bash
# 创建技能目录
mkdir -p memory/group_feishu_<id>/skills/my-skill

# 复制技能文件
cp -r my-skill/* memory/group_feishu_<id>/skills/my-skill/
```

### 记录已安装技能

安装后应在群组的 `GLOBAL.md` 中记录：

```markdown
## 已安装的群组专属 Skills

| Skill | 版本 | 来源 | 描述 |
|-------|------|------|------|
| inkos | 1.0.0 | clawhub | 小说写作工具 |
| custom-skill | 0.5.0 | manual | 本群组定制功能 |
```

### 技能隔离的好处

1. **防止污染**：小说写作技能不会影响编程群组
2. **定制化**：每个群组可以有专属的技能版本
3. **安全性**：群组技能无法访问其他群组的记忆
4. **灵活性**：全局技能提供基础，群组技能提供定制

## 项目隔离系统

每个群组可以有自己独立的 `repos/` 目录，用于存放：
- 在群组讨论中创建的代码项目
- 为群组特定需求克隆的开源项目

### 项目类型

| 类型 | 位置 | 说明 |
|------|------|------|
| **群组专属项目** | `memory/group_<id>/repos/` | 仅在本群组上下文使用 |
| **全局项目** | `/workspace/projects/` 或 `/workspace/repos/` | 跨群组共享 |

### 项目存储规则

| 场景 | 存储位置 |
|------|----------|
| 在群组中编写的代码 | `memory/group_<id>/repos/<project>/` |
| 为群组克隆的仓库 | `memory/group_<id>/repos/<repo>/` |
| 跨群组共享的项目 | `/workspace/projects/` 或 `/workspace/repos/` |

### 记录群组项目

在群组的 `GLOBAL.md` 中记录项目信息：

```markdown
## 群组项目 (repos/)

| 项目名称 | 类型 | 描述 | 位置 |
|---------|------|------|------|
| my-tool | own | 本群组创建的工具 | repos/my-tool/ |
| inkos | cloned | 克隆的小说写作工具 | repos/inkos/ |
```

### 项目隔离的好处

1. **上下文保持**：项目与创建它的群组上下文绑定
2. **减少混乱**：全局工作区保持整洁
3. **易于交接**：新成员通过 GLOBAL.md 了解群组项目
4. **高效搜索**：在群组中工作时，相关项目立即可用

## 搜索优先级

### 记忆搜索
搜索记忆时，按以下优先级顺序：
1. 当前群组目录（如 `group_feishu_xxx/`）
2. `memory/global/` 目录
3. 其他群组目录（仅在必要时）

### 技能搜索
搜索技能时，按以下优先级顺序：
1. 当前群组的 `skills/` 目录
2. 全局的 `/workspace/skills/` 目录
3. 系统默认 skills 目录

### 项目搜索
搜索代码项目时，按以下优先级顺序：
1. 当前群组的 `repos/` 目录（如果在群组上下文中）
2. `/workspace/projects/` - 全局自有项目
3. `/workspace/repos/` - 全局克隆项目

## 工作区目录规范

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

## 初始化步骤

### 1. 初始化全局记忆
```bash
mkdir -p memory/{global,private}
touch memory/global/GLOBAL.md
```

### 2. 初始化群组记忆
```bash
mkdir -p memory/group_<channel>_<id>
touch memory/group_<channel>_<id>/GLOBAL.md
touch memory/group_<channel>_<id>/YYYY-MM-DD.md
```

### 3. 初始化群组技能目录和项目目录
```bash
mkdir -p memory/group_<channel>_<id>/skills
mkdir -p memory/group_<channel>_<id>/repos
```

### 4. 初始化工作区
```bash
mkdir -p projects repos
touch MEMORY.md
```

## 安全注意事项

- `MEMORY.md` 仅在私聊时加载，避免群聊中泄露个人敏感信息
- 群聊记忆仅对应当前群组成员可见
- **群组技能完全隔离**，无法被其他群组访问
- **群组解散时保留记忆** - 当群组解散时，不删除 `memory/group_<channel>_<id>/` 目录下的所有记忆文件。这些文件保留用于：
  - 历史回顾和审计
  - 重新激活群组时恢复上下文
  - 数据分析和知识提取
- 定期审查 `MEMORY.md` 中的内容，移除过时或敏感信息
- 群组专属 skills 不应随意共享到其他群组
