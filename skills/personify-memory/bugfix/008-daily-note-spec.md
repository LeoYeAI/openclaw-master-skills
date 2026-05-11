# 问题 008：没有定义每日记忆生成规范

**创建时间：** 2026-03-04  
**更新时间：** 2026-03-05 00:35  
**优先级：** 🟢 低  
**预计耗时：** 15 分钟  
**实际耗时：** 10 分钟  
**状态：** ✅ 已完成

---

## 📋 问题描述

### 现状

**SKILL.md 没有定义：**
- ❌ daily 文件应该如何生成？
- ❌ 来源是什么？
- ❌ 格式是什么？
- ❌ 什么时候生成？

### 问题

- daily 文件来源不明确
- 依赖手动创建
- 格式不统一
- 与问题 003 的三层存储架构不一致

---

## 📊 影响分析

### 影响 1：daily 文件来源不明确

**没有明确来源的结果：**
- 依赖手动创建
- 没有自动化流程
- 容易遗漏

### 影响 2：与问题 003 的架构不一致

**问题 003 定义了三层存储：**
```
Session 目录（活跃数据）→ Daily 目录（每日备份）→ Archive 目录（月度归档）
```

**但 SKILL.md 没有体现这个架构：**
- ❌ 没有说明 daily/ 目录的文件来源
- ❌ 没有说明 daily-summary/ 的作用
- ❌ 没有说明与 session 目录的关系

### 影响 3：格式不统一

**没有统一格式的结果：**
- 不同时间创建的 daily 文件格式可能不同
- 难以批量处理和分析
- 不利于长期维护

---

## ✅ 修复方案（与问题 003 完全一致）

### 核心设计

**文件结构（与问题 003 一致）：**
```
/memory/
├── daily/              ← Session 备份文件（原始格式，JSONL）
│   ├── xxx_20260304_030000.jsonl
│   ├── yyy_20260304_030000.jsonl
│   └── ...（保留 30 天）
│
├── daily-summary/      ← 每日增量数据（原始格式，JSONL）
│   ├── 2026-03-04.jsonl
│   └── ...（保留 30 天）
│
└── archive/
    └── sessions/       ← 月度归档（原始格式，JSONL）
        ├── 2026-03/
        │   ├── xxx_20260301_025000.jsonl
        │   └── ...
        └── ...
```

**关键点：**
- ✅ daily/ 和 daily-summary/ 都是 JSONL 格式（原始格式）
- ✅ daily-summary/ 存的是增量聊天的**完整记录**，不是摘要
- ✅ 不修改文件格式，保持与 session 目录一致

---

### 步骤 1：在 SKILL.md 中明确文件结构

```markdown
### 每日记忆文件结构

**目录结构：**
```
/memory/
├── daily/              ← Session 备份文件（原始格式）
│   └── sessionId_时间戳.jsonl
│
├── daily-summary/      ← 每日增量数据（原始格式）
│   └── YYYY-MM-DD.jsonl
│
└── archive/sessions/   ← 月度归档（原始格式）
```

**文件说明：**

| 目录 | 文件命名 | 内容 | 格式 | 保留时间 |
|------|---------|------|------|---------|
| `daily/` | `sessionId_YYYYMMDD_HHMMSS.jsonl` | Session 完整备份 | JSONL（原始） | 30 天 |
| `daily-summary/` | `YYYY-MM-DD.jsonl` | 当日增量消息（完整记录） | JSONL（原始） | 30 天 |
| `archive/sessions/` | `sessionId_YYYYMMDD_HHMMSS.jsonl` | 月度归档 | JSONL（原始） | 永久 |
```

---

### 步骤 2：明确生成流程

```markdown
### 每日记忆生成流程

**自动备份（每天 03:00）：**
```
03:00 → daily-session-backup.js 运行
   ↓
1. 备份 session 目录到 daily/
   - 文件名：sessionId_时间戳.jsonl
   - 内容：完整的 session 对话历史（JSONL 原始格式）
   ↓
2. 增量处理：提取新消息
   - 从后往前读备份文件
   - 只保留"上次处理"到"这次处理"的新消息
   - 写入 daily-summary/YYYY-MM-DD.jsonl
   - 格式：保持 JSONL 原始格式
   ↓
3. 更新状态
   - 文件：state/session-processor.json
   - 记录：lastProcessedTime（最后处理时间戳）
   ↓
4. 清理旧文件
   - 删除 daily/目录 30 天前的备份
   - 删除 daily-summary/目录 30 天前的增量数据
```

**月度归档（每月 1 号 02:50）：**
```
02:50 → monthly-session-archive.js 运行
   ↓
1. 归档 session 目录到 archive/sessions/YYYY-MM/
   ↓
2. 清理 session 文件
   - 从前往后读
   - 保留最近 30 天的消息
   - 删除 30 天前的消息
```
```

---

### 步骤 3：明确文件格式（保持原始格式）

```markdown
### 文件格式规范

**所有文件都保持 JSONL 原始格式：**

```jsonl
{"role":"user","content":[{"type":"text","text":"帮我查一下 DeepSeek"}],"timestamp":1772582779784}
{"role":"assistant","content":[{"type":"text","text":"好的，我查一下..."}],"timestamp":1772582785000}
{"role":"user","content":[{"type":"text","text":"研究结果呢"}],"timestamp":1772582800000}
```

**1. daily/*.jsonl - Session 原始备份**
- 格式：JSONL（与 session 目录完全一致）
- 内容：完整的 session 对话历史
- 命名：`sessionId_YYYYMMDD_HHMMSS.jsonl`

**2. daily-summary/YYYY-MM-DD.jsonl - 每日增量数据**
- 格式：JSONL（与 session 目录完全一致）
- 内容：当日所有 session 的新消息（完整记录，不是摘要）
- 命名：`YYYY-MM-DD.jsonl`

**3. state/session-processor.json - 处理状态**
- 格式：JSON
- 内容：记录最后处理时间戳
```

---

### 步骤 4：明确清理策略

```markdown
### 清理策略

| 目录 | 清理规则 | 说明 |
|------|---------|------|
| `daily/` | 保留 30 天 | 每天 03:00 删除 30 天前的备份文件 |
| `daily-summary/` | 保留 30 天 | 每天 03:00 删除 30 天前的增量数据 |
| `archive/sessions/` | 永久保存 | 月度归档，不删除 |
| `session 目录` | 滚动保留 30 天 | 每月 1 号清理 30 天前的消息 |
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `SKILL.md` | 更新"每日记忆生成规范"章节 | +80 行 |
| `SKILL.md` | 与问题 003 的三层架构保持一致 | - |

---

## ✅ 验收标准

- [x] SKILL.md 中有明确的文件结构说明
- [x] 文件结构与问题 003 的三层架构完全一致
- [x] 所有文件都保持 JSONL 原始格式
- [x] daily-summary/ 存的是增量聊天的完整记录，不是摘要
- [x] 有明确的生成流程说明
- [x] 有明确的清理策略
- [x] 测试：运行 daily-session-backup.js → 生成正确的文件
- [x] 测试：文件格式与 session 目录一致

**验收结果：** SKILL.md 已更新，所有测试通过 ✅

**修复记录：**
- ✅ 在 SKILL.md 中增加"详细对话记录格式"章节
- ✅ 定义格式规范（7 个必填字段）
- ✅ 提供 3 个实际示例
- ✅ 定义使用规范
- 修改文件：`SKILL.md` +190 行

---

## 🔗 相关文件

- 修改文件：`/root/openclaw/work/personify-memory/SKILL.md`
- 关联问题：问题 003（Session 归档和清理）
- 相关脚本：`scripts/daily-session-backup.js`
- 相关脚本：`scripts/monthly-session-archive.js`

---

*最后更新：2026-03-05 00:11*
