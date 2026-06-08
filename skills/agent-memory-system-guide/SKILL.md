---
name: Agent Memory System Guide
description: An agent memory workflow guide for OpenClaw and Codex with MEMORY.md, daily notes, SESSION-STATE, working-buffer, Obsidian archiving, and optional OpenViking support.
---

# Agent 记忆系统搭建指南 Skill

> 🧠 从零搭建 Agent 长期记忆系统。基于 OpenClaw 实战，覆盖本地优先的 `MEMORY.md`、每日笔记、`SESSION-STATE.md`、`working-buffer.md`、Obsidian 原生笔记与可选召回后端全流程。

## 触发词

`记忆系统`、`memory-setup`、`搭建记忆`、`记忆架构`

## ⚡ 5 分钟快速上手

**如果你赶时间，只需做这几步：**

### 第一步：创建 `MEMORY.md`

```markdown
# MEMORY.md

> 长期记忆。只保留会持续影响协作的事实、偏好和决策。

## User

- Preferred name: K
- Timezone: Asia/Shanghai

## 当前任务

- [ ] 正在做的事

## 决策记录

- YYYY-MM-DD: 决策内容 + 原因

## 踩坑记录

- 问题 → 解决方案
```

### 第二步：创建每日笔记

```markdown
# memory/2026-03-20.md

## 完成
- 分析了网宿科技

## 决策
- 暂不加仓

## 踩坑
- （无）

## 待办
- [ ] 明天要做什么
```

### 第三步：从模板创建 `SESSION-STATE.md` 和 `working-buffer.md`

```markdown
# SESSION-STATE.md

## 当前任务
- 任务名称

## 已完成
- ...

## 卡点
- ...

## 下一步
- ...

## 恢复信息
- 最近一次有效上下文：...
```

```markdown
# working-buffer.md

## 进行中
- ...

## 临时决策
- ...

## 未完成
- ...
```

模板来源：

- `templates/SESSION-STATE.md`
- `templates/working-buffer.md`

### 恢复层契约先写死

- `SESSION-STATE.md` 只使用仓库模板提供的简洁结构：`当前任务`、`已完成`、`卡点`、`下一步`、`恢复信息`
- 不要写入 `Task`、`Status`、`Owner`、`Last Updated`、`Cleanup Rule` 这类另一套 schema 字段
- 如果外部 skill 产出的是详细版字段：
  - `Current Task` 合并到 `当前任务`
  - `Status` 合并到 `已完成`、`卡点` 或 `下一步`
  - `Owner`、`Last Updated`、`Cleanup Rule` 只在条目文本里按需保留，不扩展新标题
- `working-buffer.md` 是唯一的短期毛坯区
- 其他 skill 如果也有 working buffer 概念，应复用这个文件
- 不要再创建第二份并行写入的 WAL / buffer 文件
- `MEMORY.md` 用于启动时快速参考
- `memory/` 用于每日笔记和深度归档
- 两者允许主题重叠，但检索顺序不同：先 `SESSION-STATE.md`，再 recent notes，再 `MEMORY.md` / `memory_search`，最后再查归档

### 第四步：使用 Obsidian 原生笔记模板

```markdown
# templates/OBSIDIAN-NOTE.md

---
title: ""
aliases: []
tags: []
type: memory
status: draft
source: ""
source_url: ""
created: 2026-03-21
updated: 2026-03-21
related: []
---

## Summary
- 一句话摘要

## Key Points
- ...

## Evidence
> ...

## Related Notes
- [[SESSION-STATE]]
- [[working-buffer]]

## Attachments / Embeds
- `![[image.png]]`
- `![[note#^block-id]]`
```

### 第五步：每次对话开始时

```text
先读 SESSION-STATE.md，再读最近 1-3 天 daily notes，最后才做 memory_search。
memory_search(query="相关关键词")
```

**就这么简单。后续优化可以慢慢加。**

## 实战工作流示例

### 首次引导

首次引导工作区就当是开箱即用：复制 `templates/SESSION-STATE.md`、`templates/working-buffer.md` 和 `templates/memory-capture.md`，再跑一遍 `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace`（`bootstrap` 可以省略，默认行为一致），此时 `SESSION-STATE.md`、`working-buffer.md` 和 `memory-capture.md` 都已经齐活了。`MEMORY.md` 仍然建议手动建立和维护，因为它属于长期记忆主文件，不应该被脚本悄悄代写。

### 任务结束记忆捕获

在任务进行中写 `working-buffer.md` 的 `临时决策`/`新坑`/`待蒸馏`，任务结束前 30 秒用 `templates/memory-capture.md` 的 `候选决策`、`候选踩坑`、`候选长期记忆` 把最重要的内容整理出来，再决定哪些内容最终写入 `MEMORY.md`。这个环节让临时笔记和长期记忆的边界清晰且不会掉链子。

### 每日笔记蒸馏

每日笔记蒸馏指的是定期从 `memory/` 下最新的 Markdown 文件里抽取事实和决策转换到 `MEMORY.md`，同时保留原笔记供深度回溯。把这个行为设定为每日或每周结束时的步骤，能确保 `MEMORY.md` 只包含真正长期有用的内容。

### 维护报告命令

`report command` 用来检查工作区当前状态，**永远不会**写入记忆文件。运行 `python3 scripts/memory_capture.py report --workspace /path/to/workspace`，它会输出四节：**Supported files**（`MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`）、**Directories**（递归扫描 `memory/` 和 `attachments/`，在 memory/ 里只统计形如 `YYYY-MM-DD.md` 的 daily notes，在 attachments/ 里数所有文件）、**Latest daily note**（选取 `memory/` 下字典序最新的匹配 daily note 路径）、**Warnings**（比如某个文件缺失或者权限异常）。像 `memory/index.md` 这样的参考页不会被当成 latest daily note。报告命令只在工作区目录不存在或无法读取时退出非 0；其它情况下即便有警告也返回 0。supported files、directories、latest daily note 以及 warnings 是报告里每条节的标题，方便快速对照命令输出。

---

## 为什么需要记忆系统

Agent 每次会话醒来都是空白的。没有记忆文件，你就等于每次失忆重启。记忆系统是 Agent 的“大脑持久化”方案。它不让你变聪明，但让你不犯重复的错误。

这个 skill 的核心定位是本地优先的文件工作流和恢复约定，不是托管式 memory platform。外部检索或语义召回能力只能作为可选后端接在后面，不能替代本地恢复层。

## 核心架构（本地优先分层）

```text
workspace/
├── SESSION-STATE.md
├── working-buffer.md
├── MEMORY.md
├── memory-capture.md
├── attachments/
├── templates/
│   ├── SESSION-STATE.md
│   ├── working-buffer.md
│   └── OBSIDIAN-NOTE.md
└── memory/
    ├── 2026-03-17.md
    ├── 2026-03-16.md
    └── ...
```

### 第一层：恢复层（`SESSION-STATE.md`）

**保存当前任务恢复所需的最小真相。**

**该记什么：**
- 当前任务和最近已完成项
- 卡点、风险、下一步
- 中断后恢复所需的上下文

**不该记什么：**
- 另一套项目管理 schema
- 大段长期背景资料
- 需要反复整理的毛坯草稿

### 第二层：毛坯层（`working-buffer.md`）

**临时决策、草稿和待蒸馏内容先落这里。**

**该记什么：**
- 临时判断
- 新坑
- 待蒸馏条目
- 未完成但还没整理成稳定表达的内容

**不该记什么：**
- 第二份并行 buffer
- 已经蒸馏好的长期事实

### 第三层：长期记忆层（`MEMORY.md`）

**只保留精炼后的长期信息**，不是流水账。

**该记什么：**
- 重大决策和原因
- 踩过的坑和修复方式
- 用户偏好和习惯
- 稳定的命名约定、协作方式和项目画像
- 需要跨会话保留的关键关系或背景

**不该记什么：**
- 每次对话摘要
- 过几天就没用的临时信息
- 密码、API Key 等敏感信息

**维护节奏：** 每隔几天回顾 daily notes，把值得保留的蒸馏到 `MEMORY.md`，删除过时内容。

### 第四层：每日笔记层（`memory/YYYY-MM-DD.md`）

**原始记录，不加工。** 每天发生了什么、做了什么决策、学了什么，直接写。

```markdown
# 2026-03-17

## 完成
- 搭建了 OpenViking 向量数据库
- 在 InStreet 发了第一篇帖子

## 决策
- 记忆双写选 Obsidian 而非 symlink
- embedding 用本地模型，可选召回后端再接外部能力

## 踩坑
- InStreet 发帖字段名写错
- 评论间隔太短会限流

## 待办
- [ ] 明天继续补回顾
```

### 第五层：归档与可选召回层

定期把旧笔记归档，保持核心记忆干净。Obsidian 负责深度归档；`memory_search`、OpenViking 或未来其它服务负责可选召回，不替代本地恢复层。

## Obsidian 原生约定（frontmatter / Dataview / wikilink / backlinks / embeds / attachments）

把稳定知识写进 Obsidian 时，建议遵循这些约定，保证可检索、可回链、可复用：

### frontmatter

- 用 YAML frontmatter 固定结构化字段，便于后续查询、筛选、聚合
- 推荐字段见 `templates/OBSIDIAN-NOTE.md`，核心是：`type`、`status`、`tags`、`related`

### Dataview

如果你使用 Dataview 插件，可以直接用 frontmatter 做查询，例如：

```text
TABLE type, status, tags, related
FROM "memory"
WHERE status != "archived"
SORT updated desc
```

### wikilink / backlinks

- 内部引用优先使用 wikilink：`[[SESSION-STATE]]`、`[[MEMORY]]`、`[[2026-03-21]]`
- 同一概念尽量用同一标题或 aliases，backlinks 才会稳定聚合到一起

### embeds / attachments

- 图片：本地资源优先用 `![[image.png]]`，远程资源保留 `![alt](https://...)`
- 引用证据：用 block quote，或用 block embeds `![[note#^block-id]]` 复用证据段
- attachments 建议放在 vault 内可管理的位置，例如 `attachments/`

### 可选召回后端

- OpenViking 只作为增强层使用，不是硬依赖
- `memory_search` 是默认优先的轻量召回入口
- OpenViking 或其他外部服务适合在记忆量变大后补强语义召回和摘要
- 默认优先保证本地文件流程可运行，再按需接入可选后端

## 启动与结束顺序

- 启动时：先读 `SESSION-STATE.md`，再读最近 1-3 天 daily notes，最后才检索本地记忆
- 结束时：先更新 `SESSION-STATE.md`，再把稳定事实蒸馏进 `MEMORY.md`，最后归档 daily notes
- 中断后恢复：优先从 `working-buffer.md` 续接未完成项
- 仓库模板：先复制 `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`，再填入当前任务

## 文件职责边界

- `SESSION-STATE.md` 保存当前任务恢复所需的最小真相，不承担项目管理面板职责
- `SESSION-STATE.md` 不扩展为详细版任务模板；兼容外部格式时，只做字段合并，不新增 schema
- `working-buffer.md` 是唯一的短期毛坯区，负责临时决策、新坑、待蒸馏和未完成项
- 如果其他 skill 也定义了 working buffer / WAL，直接复用 `working-buffer.md`
- `MEMORY.md` 保存会影响后续协作方式的稳定事实，优先写稳定画像、约定、决策和 recurring pitfalls，适合启动时快速参考
- `memory/` 保存 daily notes 和深度归档，按需进入，不要求每次启动都全量阅读
- 如果一个 workspace 同时服务多个项目，蒸馏进 `MEMORY.md` 时建议附带日期、repo 或项目标签，保持作用域清晰
- Obsidian / OpenViking / `memory_search` 只做增强、归档或可选召回层，不替代本地恢复层

## 记忆维护策略

### 蒸馏法则

每周问自己三个问题：

1. 这条规则上周用过吗？
2. 用了之后有效吗？
3. 环境变了它还成立吗？

任何一条回答“否”，就该删或改。

### 记忆维护规则

- 保留短期会话真相：`SESSION-STATE.md`、`working-buffer.md`、最近 1-3 天 daily notes
- 保留长期稳定事实：`MEMORY.md`
- 需要长期查阅的完整材料：归档到 Obsidian
- 检索优先级：`SESSION-STATE.md` → recent daily notes → `MEMORY.md` / `memory_search` → Obsidian / 可选召回后端 → 网络搜索
- 目标：`MEMORY.md` 保持精炼，超过约 200 行就蒸馏

### 蒸馏与归档

- 每周或每次任务结束后，合并重复项、删除过时项、把案例抽象成原则
- 触发重复查询统计时，优先保留高命中内容
- Obsidian 同步保持可选，不要求每个环境都启用
- 需要脚本或自动同步时，放到 workspace 外部工具，不写进 skill 正文

### Obsidian 只保留必要配置

- Calendar：按日期浏览 daily notes
- Dataview：查询和统计记忆内容
- Templater：自动创建每日笔记模板
- 其他插件按需启用，不要让 skill 依赖插件生态

### Obsidian 配置

- 建议把 `MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`、`memory/`、`attachments/` 放在同一个 vault 里
- `attachments/` 作为统一附件目录，方便 embeds、迁移备份和跨设备同步
- Dataview 只负责查询，不负责改写记忆内容
- Templater 只负责建模板，不负责自动蒸馏长期记忆

### 定时维护

- 可以用 `crontab` 定时跑 `python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md`
- 也可以用 `crontab` 定时跑导出备份命令
- 自动化优先做检查、报告、备份
- 不要自动写入 `MEMORY.md`

### 同步取舍

- `Obsidian Sync` 更省心，适合把 Obsidian 当主界面的用户
- `iCloud` 之类网盘更轻便，但要注意冲突副本
- `git` 更适合文本版本化，不适合单独承担附件备份
- `Syncthing` 更适合本地控制和点对点同步
- 不管选哪种同步方式，都保留导出备份 / 导入恢复作为兜底方案

## 任务结束 30 秒记录流程

不要把“记忆维护”理解成一次完整总结。更稳的做法是先记毛坯，再蒸馏。

### 任务中先写毛坯

- 有临时判断，先写进 `working-buffer.md` 的 `临时决策`
- 遇到新坑，先写进 `working-buffer.md` 的 `新坑`
- 觉得“这个以后可能还会用到”，先写进 `working-buffer.md` 的 `待蒸馏`

这样做的目标不是一次写对，而是先把信息从脑子里落到文件里。

### 任务结束时只做 30 秒捕获

结束时不要强迫自己立刻改完整的 `MEMORY.md`。先复制 `templates/memory-capture.md`，快速填这几项：

- 候选决策
- 候选踩坑
- 候选长期记忆
- 只留在当前恢复层
- 明日续接

如果你是在一个新的 workspace 里启动这套流程，可以直接运行：

```text
python3 scripts/memory_capture.py --workspace /path/to/workspace
```

它会补齐缺失的 `SESSION-STATE.md`、`working-buffer.md`，并刷新一个带时间戳的 `memory-capture.md`。

## 跨设备迁移：导出备份与导入恢复

如果你的目标是不换流程、只换设备，那就不要只拷 `MEMORY.md`。更稳的做法是导出整个记忆工作区的可恢复快照。

### 导出备份

在旧设备执行：

```text
python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/memory-backup.zip
```

导出备份会把存在的 `MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`、`memory/`、`attachments/` 打进一个 zip，方便直接迁移到新设备。

### 导入恢复

在新设备执行：

```text
python3 scripts/memory_capture.py import --workspace /path/to/new-workspace --input /path/to/memory-backup.zip
```

导入恢复默认采用保守策略：先做导入前备份，再覆盖写入。这样即使目标目录里已经有旧的记忆文件，也能回滚到导入前状态。

如果你需要 clean restore，可以改用：

```text
python3 scripts/memory_capture.py import --clean --workspace /path/to/new-workspace --input /path/to/memory-backup.zip
```

`--clean` 只会清理受支持的记忆文件和目录：`MEMORY.md`、`SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`、`memory/`、`attachments/`，不会删除工作区里的其他内容。

### 什么时候用

- 需要把 Agent 的记忆状态搬到新设备
- 需要离线留档一份完整的可恢复快照
- 需要在覆盖恢复前自动保留当前工作区状态

### 候选记忆怎么落层

- 影响下次协作方式的：进 `MEMORY.md`
- 只影响当前任务恢复的：进 `SESSION-STATE.md` 或 `working-buffer.md`
- 值得长期归档但不必放本地核心记忆的：进 Obsidian

### 推荐节奏

- 每次任务后：更新 `SESSION-STATE.md`、`working-buffer.md`、`memory-capture.md`
- 每天或每周：把 `memory-capture.md` 和 recent notes 蒸馏进 `MEMORY.md`

这样能把“需要 Agent 主动记录”降级成“先低成本捕获，再集中整理”。

## 向量检索（无需额外配置）

### OpenClaw 内置 memory_search 已足够

OpenClaw 自带 `memory_search` 工具，基于语义搜索 `MEMORY.md` 和 daily notes：

```text
memory_search(query="投资策略")
```

**优势：**
- 零配置，开箱即用
- 不需要额外的向量数据库
- 支持语义搜索
- 免费，不消耗额外 API

**适用场景：**
- `MEMORY.md` 小于几十 KB
- daily notes 规模还不大
- 不需要复杂的跨库向量操作

**建议：先跑起来再优化。** 绝大多数场景先用内置 `memory_search` 就够了。

### 什么时候需要专业向量数据库

只有以下情况才需要引入 ChromaDB、Qdrant 等方案：

- 记忆文件明显膨胀
- daily notes 数量很多
- 需要跨多个 workspace 检索

## OpenViking 可选增强

- OpenViking 不是强依赖；没有它也能完成核心的断点续接流程
- 有 OpenViking 时，优先把它作为可选召回后端里的语义召回和摘要补全层
- OpenViking 负责补充相关记忆，`SESSION-STATE.md` 负责保存当前任务真相
- 如果 OpenViking 不可用，直接退回到 `SESSION-STATE.md` + `working-buffer.md` + daily notes 的本地流程

## 常见问题 FAQ

### Q: `MEMORY.md` 应该写多长？

**A:** 建议控制在 200 行以内。超过这个量级就该蒸馏了。

### Q: 每日笔记必须写吗？

**A:** 不是必须，但强烈建议。当天觉得“不用记”的事，三天后通常就忘了。

### Q: 我总是忘记维护记忆怎么办？

**A:** 不要一开始就要求自己维护完整记忆。先用 `working-buffer.md` 记录毛坯，再在任务结束时用 `memory-capture.md` 产出候选记忆，最后再统一蒸馏。

### Q: retrieval-stats.md 真的有用吗？

**A:** 可选。只有你真的要做命中统计和归档决策时才需要。

### Q: 如何处理敏感信息？

**A:** 三原则：

1. API Key 不进 `MEMORY.md`
2. 只记录变量名，不记录值
3. 群聊或共享场景不默认加载完整长期记忆

### Q: Obsidian 备份多久同步一次？

**A:** 可选。只有明确需要离线备份或跨设备共享时再同步。真要迁移时，优先用导出备份 + 导入恢复，而不是手工逐个复制文件。

## 踩坑记录

1. 别把密钥写进 `MEMORY.md`
2. 别让 daily notes 长期空着
3. 别把 `MEMORY.md` 撑太大
4. 别过早加复杂工具
5. 别把 Obsidian 绑定成硬依赖

## 适用场景

- 刚搭建 Agent 记忆系统
- 需要断点续接和长期记忆
- 想把稳定知识整理进 Obsidian

## 不适用场景

- 只需要短期对话记忆
- 当前记忆已经非常干净，不需要继续蒸馏

## 兼容性

- OpenClaw-compatible skill
- Codex-compatible skill
- OpenViking-compatible optional enhancement
- Obsidian vault workflows

## 相关文档

- OpenClaw 文档：https://docs.openclaw.ai
- OpenClaw memory_search：https://docs.openclaw.ai/tools#memory_search
