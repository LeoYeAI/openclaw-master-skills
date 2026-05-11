# 问题 003：没有会话自动保存机制

**创建时间：** 2026-03-04  
**优先级：** 🔴 高  
**预计耗时：** 25 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

当前 `daily/` 目录下的文件依赖手动创建：
- `2026-03-03.md` - 飞书接入项目记录（手动创建）
- `2026-03-04.md` - 今天的教训记录（手动补的）

没有自动保存当天对话历史的机制。

### 问题

1. 如果忘记创建 daily 文件，凌晨整理脚本就没有数据可分析
2. 对话历史散落在各个会话中，没有集中保存
3. 违背了 SKILL.md 中"每日记忆（原始日志）"的设计

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

### 影响 2：丢失日常对话记录

没有自动保存 → 日常对话没有记录 → 无法回顾成长历程

---

## ✅ 修复方案

### 步骤 1：新增 session-saver.js 脚本

创建新文件 `scripts/session-saver.js`：

```javascript
#!/usr/bin/env node

/**
 * Personify Memory - Session Saver
 * 
 * 自动保存当天对话历史到 daily/ 目录
 * 运行时间：每天 23:50 或会话结束时
 */

const fs = require('fs');
const path = require('path');

class SessionSaver {
  constructor(basePath = '/root/openclaw/memory') {
    this.basePath = basePath;
    this.dailyPath = path.join(basePath, 'daily');
    
    // 确保目录存在
    if (!fs.existsSync(this.dailyPath)) {
      fs.mkdirSync(this.dailyPath, { recursive: true });
    }
  }

  /**
   * 保存当天所有会话到 daily 文件
   */
  async saveDailyConversations() {
    console.log('🧠 开始保存当天对话历史...');
    
    const today = new Date().toISOString().split('T')[0];
    const dailyFile = path.join(this.dailyPath, `${today}.md`);
    
    // 1. 获取当天所有会话（需要调用 OpenClaw API）
    const sessions = await this.getTodaySessions();
    console.log(`📂 找到 ${sessions.length} 个会话`);
    
    // 2. 生成每日记忆文件
    let content = `# ${today} - 每日记忆\n\n`;
    content += `## 📝 今日概览\n\n`;
    content += `- 会话数：${sessions.length}\n`;
    content += `- 最后更新：${new Date().toISOString()}\n\n`;
    
    // 3. 保存每个会话的摘要
    for (const session of sessions) {
      const history = await this.getSessionHistory(session.sessionKey);
      
      content += `## 💬 会话 ${session.sessionKey.substring(0, 8)}...\n\n`;
      content += `**通道：** ${session.channel || 'unknown'}\n`;
      content += `**时间：** ${new Date(session.updatedAt).toLocaleString('zh-CN')}\n\n`;
      
      // 提取关键对话
      const highlights = this.extractHighlights(history);
      content += highlights;
      content += `\n---\n\n`;
    }
    
    // 4. 写入文件
    fs.writeFileSync(dailyFile, content, 'utf-8');
    console.log(`✅ 已保存到：${dailyFile}`);
    
    return { success: true, file: dailyFile, sessionCount: sessions.length };
  }

  /**
   * 获取当天所有会话
   * 注意：需要调用 OpenClaw 的 sessions_list API
   */
  async getTodaySessions() {
    // 方法 1：调用 OpenClaw CLI
    // const { exec } = require('child_process');
    // return new Promise((resolve, reject) => {
    //   exec('openclaw sessions list --today', (error, stdout, stderr) => {
    //     if (error) reject(error);
    //     else resolve(JSON.parse(stdout));
    //   });
    // });
    
    // 方法 2：直接读取会话文件（简化版）
    const sessionsDir = '/root/.openclaw/agents/main/sessions/';
    if (!fs.existsSync(sessionsDir)) {
      return [];
    }
    
    const today = new Date().toISOString().split('T')[0];
    const sessions = [];
    
    const files = fs.readdirSync(sessionsDir);
    for (const file of files) {
      if (!file.endsWith('.jsonl')) continue;
      
      const filePath = path.join(sessionsDir, file);
      const stats = fs.statSync(filePath);
      const fileDate = stats.mtime.toISOString().split('T')[0];
      
      if (fileDate === today) {
        sessions.push({
          sessionKey: file.replace('.jsonl', ''),
          updatedAt: stats.mtime.getTime(),
          channel: 'unknown'
        });
      }
    }
    
    return sessions;
  }

  /**
   * 获取会话历史记录
   */
  async getSessionHistory(sessionKey) {
    // 读取会话文件
    const sessionsDir = '/root/.openclaw/agents/main/sessions/';
    const filePath = path.join(sessionsDir, `${sessionKey}.jsonl`);
    
    if (!fs.existsSync(filePath)) {
      return [];
    }
    
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    return lines.map(line => JSON.parse(line));
  }

  /**
   * 提取关键对话
   */
  extractHighlights(messages) {
    if (messages.length === 0) return '*（无消息）*\n';
    
    let content = '';
    
    // 提取最近 20 条消息
    const recentMessages = messages.slice(-20);
    
    for (const msg of recentMessages) {
      const role = msg.role === 'user' ? '👤 Amber' : '🦞 小钳';
      const text = this.extractText(msg.content);
      
      if (text) {
        content += `> ${role}: ${text}\n`;
      }
    }
    
    return content;
  }

  /**
   * 从消息内容中提取文本
   */
  extractText(content) {
    if (!content) return '';
    
    if (Array.isArray(content)) {
      // 查找 text 类型的内容
      const textItem = content.find(item => item.type === 'text');
      return textItem ? textItem.text : '';
    }
    
    return String(content);
  }

  /**
   * 运行定时保存任务（供 cron 调用）
   */
  runSaveTask() {
    console.log('🕐 运行会话保存任务...');
    return this.saveDailyConversations();
  }
}

// CLI usage
if (require.main === module) {
  const saver = new SessionSaver();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'run':
      saver.runSaveTask().catch(console.error);
      break;
    
    case 'save':
      saver.saveDailyConversations().catch(console.error);
      break;
    
    default:
      console.log('Usage: node session-saver.js <command>');
      console.log('Commands:');
      console.log('  run   - Run save task (for cron)');
      console.log('  save  - Save conversations immediately');
  }
}

module.exports = SessionSaver;
```

---

### 步骤 2：添加 cron 任务

在 OpenClaw 中新增 cron 任务，每天 23:50 执行：

```json
{
  "name": "personify-memory 会话保存",
  "schedule": {
    "kind": "cron",
    "expr": "50 23 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "SYSTEM: 执行 node /root/openclaw/work/personify-memory/scripts/session-saver.js run"
  }
}
```

或者更好的方式（真正执行脚本）：

```json
{
  "name": "personify-memory 会话保存",
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "执行会话保存任务：node /root/openclaw/work/personify-memory/scripts/session-saver.js run"
  }
}
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `scripts/session-saver.js` | **新增文件** | ~200 行 |
| cron 配置 | 新增每天 23:50 的保存任务 | ~15 行 |
| **总计** | | **~215 行** |

---

## ✅ 验收标准

- [ ] 脚本能够读取当天会话
- [ ] 能够提取会话历史
- [ ] 能够生成 daily/YYYY-MM-DD.md 文件
- [ ] 文件格式正确，包含今日概览和会话摘要
- [ ] cron 任务配置正确
- [ ] 运行测试：`node scripts/session-saver.js save` 无报错
- [ ] 检查生成的 daily 文件内容正确

---

## 🔗 相关文件

- 新增文件：`/root/openclaw/work/personify-memory/scripts/session-saver.js`
- 输出目录：`/root/openclaw/work/personify-memory/../memory/daily/`
- 会话目录：`/root/.openclaw/agents/main/sessions/`

---

*最后更新：2026-03-04*
