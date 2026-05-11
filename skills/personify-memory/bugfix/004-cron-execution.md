# 问题 004：cron 任务不会真正执行脚本

**创建时间：** 2026-03-04  
**更新时间：** 2026-03-04 23:49  
**优先级：** 🟡 中  
**预计耗时：** 10 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

当前 cron 任务的 payload 是 `systemEvent`，只注入文本到会话，不会真正执行脚本。

**当前配置：**
```json
{
  "name": "personify-memory 自动归档",
  "payload": {
    "kind": "systemEvent",
    "text": "🦞💰 运行 personify-memory 每日复盘任务...\n**运行命令：**\nnode scripts/daily-review.js"
  }
}
```

### 问题

- `systemEvent` 只是注入文本到会话
- 不会真正执行 `node daily-review.js`
- 依赖 AI 看到消息后手动执行
- 如果 AI 不在线或不响应，任务就失败了

---

## 📊 影响分析

### 实际表现

```
凌晨 3 点 cron 触发
   ↓
注入 systemEvent 文本到会话
   ↓
❌ 不会自动执行脚本
   ↓
AI 看到消息（如果在线）
   ↓
AI 手动执行脚本
   ↓
❌ 如果 AI 不在线或不响应，任务就失败了
```

### 影响

1. **任务执行不可靠** - 依赖 AI 是否在线
2. **没有独立日志** - 执行结果不记录
3. **错误无法捕获** - 脚本报错没人知道
4. **违背自动化设计** - cron 任务应该自动执行

---

## ✅ 修复方案

### 方案：改为 isolated + agentTurn（推荐）

**修改后的配置：**
```json
[
  {
    "name": "personify-memory 月度归档",
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "执行月度归档任务：node /root/openclaw/work/personify-memory/scripts/monthly-session-archive.js run"
    }
  },
  {
    "name": "personify-memory 每日备份",
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "执行每日备份任务：node /root/openclaw/work/personify-memory/scripts/daily-session-backup.js run"
    }
  }
]
```

### 为什么选择 isolated + agentTurn？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **isolated + agentTurn** | ✅ 独立会话执行<br>✅ 不依赖主会话<br>✅ 有执行日志<br>✅ 错误可捕获 | - |
| systemEvent + hooks | ⚠️ 需要 hooks 支持<br>⚠️ 配置复杂 | ❌ 可能不支持 |
| 保持 systemEvent | - | ❌ 依赖 AI 响应<br>❌ 不可靠 |

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| cron 配置 | 修改 2 个任务的 sessionTarget 和 payload | ~30 行 |

---

## ✅ 验收标准

- [ ] cron 任务能够真正执行脚本
- [ ] 执行结果有独立日志记录
- [ ] 错误能够被捕获和报告
- [ ] 不依赖主会话 AI 是否在线
- [ ] 每月 1 号 02:50 自动执行月度归档
- [ ] 每天 03:00 自动执行每日备份

---

## 🔗 相关文件

- cron 配置文件：`~/.openclaw/cron.json` 或通过 `openclaw cron` 命令管理

---

*最后更新：2026-03-04 23:49*
