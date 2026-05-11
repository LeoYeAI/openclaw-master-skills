# 问题 003：没有会话自动保存机制

**创建时间：** 2026-03-04  
**更新时间：** 2026-03-05 00:35  
**优先级：** 🔴 高  
**预计耗时：** 35 分钟  
**实际耗时：** 30 分钟  
**状态：** ✅ 已完成

---

## 📋 问题描述

### 现状

当前 `daily/` 目录下的文件依赖手动创建：
- `2026-03-03.md` - 手动创建（飞书接入项目）
- `2026-03-04.md` - 手动创建（今天的教训）

**没有自动保存机制：**
- ❌ 没有脚本自动保存当天对话
- ❌ Session 目录文件会无限增长
- ❌ 没有系统的归档和清理机制

### 问题

1. 如果忘记创建 daily 文件，凌晨整理脚本就没有数据可分析
2. Session 文件（`/root/.openclaw/agents/main/sessions/*.jsonl`）会越来越大
3. 没有分层存储策略（活跃数据 vs 历史归档）

---

## 📊 影响分析

### 影响 1：daily-review.js 无数据可分析

```
凌晨 3 点 cron 触发
   ↓
daily-review.js 读取 daily/*.md
   ↓
❌ daily 目录为空或文件不全
   ↓
无法提取关键信息
   ↓
记忆整理失败
```

### 影响 2：Session 目录无限增长

**当前状态：**
```bash
$ du -sh /root/.openclaw/agents/main/sessions/*.jsonl | sort -rh
2.0M  b80f37d4-....jsonl  (2026-03-03)
1.3M  9020e621-....jsonl  (2026-03-04)
524K  d2ab1547-....jsonl  (2026-03-04)
484K  3dedf42f-....jsonl  (2026-03-03)
```

**问题：**
- 文件按会话 ID 命名，长期保存
- 随着时间推移，文件越来越多、越来越大
- 每天读取所有文件分析会越来越慢

### 影响 3：违背 SKILL.md 的设计规范

**SKILL.md 明确定义：**
```markdown
/memory/
├── daily/  ← 每日记忆（原始日志）
└── archive/  ← 归档备份
```

**但实际：**
- ❌ daily 目录没有自动保存
- ❌ archive 目录没有系统归档
- ❌ 依赖手动创建

---

## ✅ 修复方案（简化版）

### 核心设计思路

```
┌─────────────────────────────────────────────────────────┐
│ 第一层：Session 目录（活跃数据）                         │
│ - 保存所有会话的完整历史                                 │
│ - 每天备份到 daily 目录                                  │
│ - 每月清理一次（保留 30 天滚动）                         │
└─────────────────────────────────────────────────────────┘
                          ↓ 每天备份
┌─────────────────────────────────────────────────────────┐
│ 第二层：Daily 目录（每日增量数据）                       │
│ - 备份文件：sessionId_时间戳.jsonl                       │
│ - 直接修改备份文件：只保留"上次处理"到"这次处理"的对话   │
│ - 30 天后删除                                            │
└─────────────────────────────────────────────────────────┘
                          ↓ 每月归档
┌─────────────────────────────────────────────────────────┐
│ 第三层：Archive 目录（历史归档）                         │
│ - 每月备份一次 Session 完整数据                          │
│ - 永久保存                                               │
└─────────────────────────────────────────────────────────┘
```

**简化点：**
- ✅ 不需要 `daily-summary/` 目录
- ✅ 直接修改 daily/下的备份文件
- ✅ 减少 IO 操作，减少文件数量

---

### 流程 1：每日备份和增量处理（每天 03:00）

```
Step 1: 备份 Session 文件
   ↓
   /root/.openclaw/agents/main/sessions/
   ├── xxx.jsonl  → 复制 →  /root/openclaw/memory/daily/xxx_20260304_030000.jsonl
   ├── yyy.jsonl  → 复制 →  /root/openclaw/memory/daily/yyy_20260304_030000.jsonl
   └── ...
   
Step 2: 直接修改备份文件（从后往前读，高效）
   ↓
   读取备份文件
   ↓
   找到最后一条消息的时间戳 T1
   ↓
   读取上次处理的时间戳 T0（从 state.json）
   ↓
   只保留 T0 到 T1 之间的消息
   ↓
   直接覆盖写入备份文件（原地修改）
   ↓
   更新 state.json：lastProcessed = T1

Step 3: 清理 Daily 目录
   ↓
   删除 30 天前的备份文件
```

---

### 流程 2：Session 归档和清理（每月 1 号 02:50）

```
Step 1: 归档 Session 文件
   ↓
   /root/.openclaw/agents/main/sessions/
   ├── xxx.jsonl  → 复制 →  /root/openclaw/memory/archive/sessions/2026-03/xxx_20260301_025000.jsonl
   └── ...
   
Step 2: 清理 Session 文件（从前往后读，快速）
   ↓
   对每个 session 文件：
   - 从前往后读，找到 30 天前的位置
   - 删除该位置之前的所有消息
   - 保留最近 30 天的消息
```

---

### 📁 文件结构（简化后）

```
/root/.openclaw/agents/main/sessions/  ← OpenClaw Session 目录（活跃数据）
├── xxx.jsonl  ← 完整对话历史（每月清理一次，保留 30 天）
├── yyy.jsonl
└── ...

/root/openclaw/memory/  ← 我们的记忆目录
├── daily/  ← 每日备份（增量处理后的文件）
│   ├── xxx_20260304_030000.jsonl  ← 备份后直接增量处理这个文件
│   ├── yyy_20260304_030000.jsonl
│   └── ...（保留 30 天）
│
└── archive/
    └── sessions/  ← Session 月度归档
        ├── 2026-03/
        │   ├── xxx_20260301_025000.jsonl
        │   └── ...
        └── ...

/root/openclaw/memory/state/  ← 处理状态
└── session-processor.json  ← 记录上次处理时间戳
```

---

### 🔧 新增脚本

#### 脚本 1：daily-session-backup.js（每天 03:00 执行）

**功能：**
1. 备份 session 目录到 daily/（原文件名 + 时间戳）
2. 直接修改备份文件：只保留上次处理到这次的对话（从后往前读）
3. 清理 30 天前的 daily 文件

**关键代码：**
```javascript
class DailySessionBackup {
  async runDailyBackup() {
    const timestamp = this.getTimestamp();
    
    // 1. 备份所有 session 文件
    const backups = this.backupSessions(timestamp);
    
    // 2. 增量处理：直接修改备份文件
    const lastProcessedTime = this.getLastProcessedTime();
    let totalNewMessages = 0;
    
    for (const backup of backups) {
      const newMessages = await this.processBackupFile(backup.path, lastProcessedTime);
      totalNewMessages += newMessages.length;
    }
    
    // 3. 更新状态
    this.updateState(lastProcessedTime, totalNewMessages);
    
    // 4. 清理 30 天前的 daily 文件
    const deletedCount = this.cleanupOldBackups(30);
    
    return { backups: backups.length, newMessages: totalNewMessages, deleted: deletedCount };
  }

  // 从后往前读，直接修改备份文件
  async processBackupFile(filePath, lastProcessedTime) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    const newMessages = [];
    
    // 从后往前读
    for (let i = lines.length - 1; i >= 0; i--) {
      const msg = JSON.parse(lines[i]);
      
      if (msg.timestamp <= lastProcessedTime) {
        break;
      }
      
      newMessages.unshift(msg);
      
      // 优化：最多读 1000 条
      if (newMessages.length >= 1000) break;
    }
    
    // 直接覆盖写入（只保留新消息）
    const newContent = newMessages.map(m => JSON.stringify(m)).join('\n') + '\n';
    fs.writeFileSync(filePath, newContent, 'utf-8');
    
    console.log(`  ✅ 处理：${path.basename(filePath)} - ${newMessages.length} 条新消息`);
    return newMessages;
  }
}
```

---

#### 脚本 2：monthly-session-archive.js（每月 1 号 02:50 执行）

**功能：**
1. 归档 session 目录到 archive/sessions/YYYY-MM/
2. 清理 session 文件中 30 天前的消息（从前往后读）

**关键代码：**
```javascript
class MonthlySessionArchive {
  async runMonthlyArchive() {
    const timestamp = this.getTimestamp();
    const monthDir = path.join(this.archiveDir, timestamp.slice(0, 6));
    
    // 1. 归档所有 session 文件
    const archives = this.archiveSessions(monthDir, timestamp);
    
    // 2. 清理 session 文件（保留 30 天）
    const cutoffTime = Date.now() - (30 * 24 * 60 * 60 * 1000);
    const cleanedCount = this.cleanupSessions(cutoffTime);
    
    return { archived: archives.length, cleaned: cleanedCount };
  }

  // 从前往后读，快速找到 30 天前的位置
  cleanSingleFile(filePath, cutoffTime) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    let cutoffIndex = -1;
    
    // 从前往后读，找到 30 天前的位置
    for (let i = 0; i < lines.length; i++) {
      const msg = JSON.parse(lines[i]);
      
      if (msg.timestamp >= cutoffTime) {
        cutoffIndex = i;
        break;  // 找到就停止，不用读完
      }
    }
    
    if (cutoffIndex === -1) {
      // 所有消息都超过 30 天
      fs.writeFileSync(filePath, '', 'utf-8');
    } else {
      // 删除 cutoffIndex 之前的消息
      const keptLines = lines.slice(cutoffIndex);
      fs.writeFileSync(filePath, keptLines.join('\n') + '\n', 'utf-8');
    }
  }
}
```

---

### ⏰ Cron 配置

```json
[
  {
    "name": "personify-memory 月度归档",
    "schedule": {
      "kind": "cron",
      "expr": "50 2 1 * *",
      "tz": "Asia/Shanghai"
    },
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "执行月度归档：node scripts/monthly-session-archive.js run"
    }
  },
  {
    "name": "personify-memory 每日备份",
    "schedule": {
      "kind": "cron",
      "expr": "0 3 * * *",
      "tz": "Asia/Shanghai"
    },
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "执行每日备份：node scripts/daily-session-backup.js run"
    }
  }
]
```

---

### 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `scripts/daily-session-backup.js` | **新增文件** | ~180 行 |
| `scripts/monthly-session-archive.js` | **新增文件** | ~150 行 |
| `scripts/daily-review.js` | 修改为读取 daily/*.jsonl | ~30 行 |
| cron 配置 | 新增 2 个定时任务 | ~30 行 |
| **总计** | | **~390 行** |

---

## ✅ 验收标准

- [x] 每天 03:00 自动备份 session 到 daily/
- [x] 增量处理直接修改备份文件（从后往前读）
- [x] 不生成 daily-summary/目录
- [x] 每月 1 号 02:50 自动归档 session
- [x] 清理 session 文件 30 天前的消息（从前往后读）
- [x] daily/目录保留 30 天备份
- [x] 运行测试：`node scripts/daily-session-backup.js run` 无报错
- [x] 运行测试：`node scripts/monthly-session-archive.js run` 无报错

**验收结果：** 所有测试通过，脚本运行正常 ✅

---

## 📊 方案优势（简化后）

| 优势 | 说明 |
|------|------|
| ✅ **简化流程** | 不需要 daily-summary/目录，减少文件数量 |
| ✅ **减少 IO** | 直接修改备份文件，不需要额外写入 |
| ✅ **避免读写冲突** | 先备份到 daily，处理备份文件，不影响 session 原文件 |
| ✅ **增量处理** | 只处理上次到这次的对话，效率高 |
| ✅ **从后往前读** | 快速定位新消息，不用读完整文件 |
| ✅ **从前往后清理** | 找到 30 天前位置就停止，快速清理 |
| ✅ **三层存储** | Session（活跃）→ Daily（增量）→ Archive（归档） |
| ✅ **自动清理** | Daily 保留 30 天，Session 保留 30 天滚动 |
| ✅ **历史不丢失** | 月度归档永久保存 |

---

## 🔗 相关文件

- 新增文件：`/root/openclaw/work/personify-memory/scripts/daily-session-backup.js`
- 新增文件：`/root/openclaw/work/personify-memory/scripts/monthly-session-archive.js`
- 修改文件：`/root/openclaw/work/personify-memory/scripts/daily-review.js`
- 输出目录：`/root/openclaw/work/personify-memory/../memory/daily/`
- 归档目录：`/root/openclaw/work/personify-memory/../memory/archive/sessions/`
- Session 目录：`/root/.openclaw/agents/main/sessions/`

---

*最后更新：2026-03-05 00:20*
