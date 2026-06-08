# agent-memory-system-guide

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GitHub 仓库：[cjke84/agent-memory-system-guide](https://github.com/cjke84/agent-memory-system-guide)

Canonical OpenClaw skill id：`memory-system`

面向 OpenClaw 和 Obsidian 工作流的 Agent 长期记忆搭建指南。

GitHub 发布归档：[v0.1.0](https://github.com/cjke84/agent-memory-system-guide/releases/tag/v0.1.0)

当前已发布 skill 版本：`1.1.5`

## 是什么

这个 skill 说明如何给 Agent 搭建长期记忆：用精简的 `MEMORY.md`、每日笔记、记忆蒸馏和 Obsidian 备份组成一套稳定的本地优先记忆层。
它是本地文件工作流和约定，不是托管式 memory platform。
OpenViking 是可选增强层，用来补充语义召回和摘要。
可以把 OpenViking、`memory_search`，或者未来别的记忆服务都理解成可选召回后端，而不是本地恢复层的替代品。

适合：
- 需要长期记忆的 Agent
- 需要保留每日笔记并蒸馏稳定事实的 Agent
- 想把 Obsidian 作为长期归档的用户

## 怎么用

1. 安装这个 skill。
2. 先复制 `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`，再配合 `MEMORY.md` 和每日笔记使用。
3. 把稳定事实蒸馏进长期记忆，原始记录留在每日笔记里。
4. 将稳定知识归档到 Obsidian。

## 文件边界

- `SESSION-STATE.md` 使用仓库模板的简洁结构：`当前任务`、`已完成`、`卡点`、`下一步`、`恢复信息`
- 不要把它扩展成另一套详细版 schema，例如 `Task`、`Status`、`Owner`、`Last Updated`、`Cleanup Rule`
- 如果外部 workflow 已经产出这些字段，应该合并回简洁版栏目，而不是新增标题
- `working-buffer.md` 是唯一的短期毛坯区；如果别的 skill 也有 working buffer / WAL 概念，应复用这个文件
- `MEMORY.md` 用于启动时快速参考
- `memory/` 用于每日笔记和深度归档
- 两层允许有内容重叠，但职责不同，不视为冲突
- 检索顺序：先 `SESSION-STATE.md`，再 recent daily notes，再 `MEMORY.md` 或 `memory_search`，最后才进入 Obsidian / 深度归档

## 记忆分层

- `SESSION-STATE.md`：当前任务的恢复层，保存中断后续接所需的最小真相
- `working-buffer.md`：毛坯区，放临时判断、草稿和待蒸馏内容
- `MEMORY.md`：蒸馏后的长期记忆，保存稳定偏好、约定、决策和高频踩坑
- `memory/`：每日笔记和按项目沉淀的原始过程记录
- Obsidian、`memory_search`、OpenViking 或其他外部工具：深度归档或可选召回层

实践边界：
- 长期稳定画像写进 `MEMORY.md`
- 高频变化的执行过程留在 `SESSION-STATE.md`、`working-buffer.md` 和 daily notes
- 只有本地恢复层不够时，才进一步查归档或语义召回

## 稳定画像与项目作用域

- `MEMORY.md` 应优先保存稳定画像：偏好、命名约定、架构决策、反复出现的坑，以及会影响后续协作方式的事实。
- 快速变化的执行细节应留在 `SESSION-STATE.md`、`working-buffer.md` 和 recent daily notes。
- 如果一个工作区同时服务多个项目，蒸馏进 `MEMORY.md` 时建议补上日期、仓库名或项目标签，保证后续检索有作用域，但不额外引入强制 schema。

## 记忆捕获

- 用 `templates/memory-capture.md` 作为任务结束时的轻量记录模板。
- 任务进行中，把毛坯先写进 `working-buffer.md` 的 `临时决策`、`新坑`、`待蒸馏`。
- 任务结束后先花 30 秒产出候选记忆，再决定哪些内容真正进入 `MEMORY.md`。
- 真正落到工作区时，可以运行 `python3 scripts/memory_capture.py --workspace /path/to/workspace` 或 `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace` 一键补齐基础文件。

## 实战例子

### 工作流示例

### 首次引导

首次引导阶段只需复制 `templates/SESSION-STATE.md`、`templates/working-buffer.md`、`templates/memory-capture.md`，再运行 `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace`（或者省略 `bootstrap` 使用默认命令）就能补齐 `SESSION-STATE.md`、`working-buffer.md` 并刷新记忆捕获模板。`MEMORY.md` 仍然建议手动创建和维护，这样长期记忆的结构由你自己掌控。

### 任务结束记忆捕获

任务结束记忆捕获的节奏是：先在 `working-buffer.md` 写下临时想法，任务结束前的 30 秒把重点填写到 `templates/memory-capture.md` 的 `候选决策`、`候选踩坑`、`候选长期记忆`，然后再决定哪些内容真正写入 `MEMORY.md`。这样就把临时笔记和长期记忆的边界拉清楚。

### 每日笔记蒸馏

每日笔记蒸馏是让长期记忆保持干净的方式。打开 `memory/` 下最新的 Markdown 文件，挑出重要决策和洞察，放进 `MEMORY.md` 并补上日期或项目标签，保留原始的当日笔记做参考。

### Memory 不等于通用 RAG

这个工作流把 memory 看成分层系统，而不是一个统统丢进去再检索的大桶。`MEMORY.md` 保存稳定画像和长期协作事实，`memory/` 保存原始执行历史，Obsidian 和可选语义工具负责深度召回。这样既保留本地工作流的可审计和可迁移性，也避免把这个仓库讲成一个在线 memory API 产品。

### 报告示例

### 维护报告命令

`python3 scripts/memory_capture.py report --workspace /path/to/workspace` 会记录当前工作区的快照，不会写入任何记忆，只打印状态。它默认能访问工作区就返回 0，只有在目录不存在或无法读取时才退出非 0。报告在 stdout 和可选的 Markdown 输出里都分为四节：**支持的文件**、**目录**、**最新每日笔记**、**警告**。支持的文件固定为 `MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`，扫描目录包括 `memory/` 和 `attachments/`，`memory/` 内部采用递归方式只统计形如 `YYYY-MM-DD.md` 的每日笔记，并选择字典序最大的匹配路径作为最新每日笔记，`attachments/` 递归统计所有文件。像 `index.md` 这样的非每日笔记 Markdown 会被忽略，避免把索引页误当成最新记录。如果某一层出现问题，比如文件缺失或无法访问，会在**警告**中注明。

示例输出：

```text
Memory workspace report for /path/to/workspace

Supported files:
  MEMORY.md: present
  SESSION-STATE.md: present
  working-buffer.md: present
  memory-capture.md: present

Directories:
  memory: 2 daily note(s)
  attachments: 1 attachment(s)

Latest daily note: memory/2026-03-25.md

Warnings: none
```

警告状态示例输出：

```text
Memory workspace report for /path/to/workspace

Supported files:
  MEMORY.md: present
  SESSION-STATE.md: missing
  working-buffer.md: present
  memory-capture.md: present

Directories:
  memory: 0 daily note(s)
  attachments: 0 attachment(s)

Latest daily note: none

Warnings:
  - Missing supported file: SESSION-STATE.md
  - memory directory has no daily notes
  - attachments directory is empty
```

Markdown 报告文件示例：

生成命令：

```text
python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md
```

生成后的 `/path/to/workspace-report.md` 内容示例：

```markdown
# Memory workspace report

- Workspace: /path/to/workspace

## Supported files
- `MEMORY.md`: present
- `SESSION-STATE.md`: present
- `working-buffer.md`: present
- `memory-capture.md`: present

## Directories
- `memory`: 2 daily note(s)
- `attachments`: 1 attachment(s)

## Latest daily note
- memory/2026-03-25.md

## Warnings
- none
```

## 跨设备迁移：导出备份与导入恢复

- 在旧设备导出备份：`python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/memory-backup.zip`
- 把备份包带到新设备后导入恢复：`python3 scripts/memory_capture.py import --workspace /path/to/new-workspace --input /path/to/memory-backup.zip`
- 默认导入是保守模式：会先做导入前备份，再执行覆盖式恢复，不会删除目标工作区里额外存在的受支持记忆文件。
- 如果你要让受支持的记忆面与备份包保持一致，使用 `python3 scripts/memory_capture.py import --clean --workspace /path/to/new-workspace --input /path/to/memory-backup.zip` 做 clean restore。
- 备份包会包含存在的 `MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`、`memory/` 和 `attachments/`。

## Obsidian 配置指南

建议把长期记忆工作区收在同一个 vault 里，目录结构尽量稳定：

```text
vault/
  MEMORY.md
  SESSION-STATE.md
  working-buffer.md
  memory-capture.md
  memory/
  attachments/
```

推荐配置：
- daily notes 放在 `memory/`，这样 CLI 报告和 Obsidian 浏览路径一致。
- 图片、截图、证据附件统一放在 `attachments/`，便于 embeds 和备份迁移。
- 长期笔记优先复用 `templates/OBSIDIAN-NOTE.md`，保持 frontmatter、wikilink、embeds 结构一致。
- 需要按日期浏览时启用 `Calendar`。
- 需要查询记忆属性时启用 `Dataview`。
- 需要自动创建笔记骨架时启用 `Templater`，但不要把核心记忆流程绑死在插件上。

最小 Dataview 查询示例：

```text
TABLE type, status, tags, related
FROM "memory"
WHERE status != "archived"
SORT updated desc
```

同步建议：
- 同步整个 vault，或者至少同步 `MEMORY.md`、`memory/`、`attachments/` 这些核心目录。
- 不要把无关插件的缓存目录混进同步规则。
- Obsidian 同步始终是可选层，本地文件流程应当在不同设备上独立可用。

## 定时维护示例

自动化更适合做检查、报告和备份，不适合直接改写长期记忆。

用 `crontab` 每天生成维护报告：

```text
0 9 * * * cd /path/to/repo && python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md
```

用 `crontab` 每周导出一次备份：

```text
0 18 * * 5 cd /path/to/repo && python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/backups/
```

实践原则：
- 定时运行检查、报告、备份可以自动化。
- 不要自动写入 `MEMORY.md`，蒸馏后的长期记忆仍然保留人工确认这一步。

## 同步方案与取舍

- `Obsidian Sync`：如果你主要在 Obsidian 里工作，这是最省心的多设备同步方式。
- `iCloud` 或其他网盘：适合个人 vault，但要留意冲突副本和大量附件时的延迟。
- `git`：适合文本文件版本化和审阅变更，但对二进制附件和非技术用户不够友好。
- `Syncthing`：适合点对点同步和本地控制，但多设备配置纪律要求更高。

建议：
- 一个 vault 只保留一条主要同步路径，避免重复同步带来的冲突处理。
- 即使开启同步，也保留导出备份 / 导入恢复作为保守恢复手段。
- 如果使用 `git`，把它视为文本版本化工具，不要把它当成附件备份的唯一方案。

## Obsidian 原生笔记

- 稳定知识建议用 `templates/OBSIDIAN-NOTE.md`：包含 YAML frontmatter、wikilink、embeds、attachments 约定。
- 如果使用 Dataview，可以按 `type`、`status`、`tags`、`related` 做查询。

## 包含文件

- `SKILL.md`：技能契约与工作流
- `manifest.toml`：面向 OpenClaw / ClawHub 风格发布流程的元数据
- `INSTALL.md`：可直接发给 Agent 的安装指令
- `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`：恢复模板
- `templates/memory-capture.md`：任务结束时的候选记忆模板
- `scripts/memory_capture.py`：初始化、导出备份、导入恢复、维护报告的辅助脚本

发布说明：后续版本号与虾评更新目标 `skill_id` 以 `manifest.toml` 为准。
