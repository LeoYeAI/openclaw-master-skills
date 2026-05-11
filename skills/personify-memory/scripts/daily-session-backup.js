#!/usr/bin/env node

/**
 * Personify Memory - Daily Session Backup
 * 
 * 每日 Session 备份和增量处理脚本
 * 运行时间：每天凌晨 03:00
 * 
 * 核心功能：
 * 1. 备份 session 目录到 daily/（原文件名 + 时间戳）
 * 2. 增量处理：直接修改备份文件，只保留上次处理到这次的对话
 * 3. 清理 30 天前的 daily 文件
 */

const fs = require('fs');
const path = require('path');

class DailySessionBackup {
  constructor(options = {}) {
    // Session 目录（OpenClaw 活跃数据）
    this.sessionDir = options.sessionDir || '/root/.openclaw/agents/main/sessions';
    
    // 记忆目录
    this.memoryBase = options.memoryBase || '/root/openclaw/memory';
    this.dailyDir = path.join(this.memoryBase, 'daily');
    this.stateDir = path.join(this.memoryBase, 'state');
    this.stateFile = path.join(this.stateDir, 'session-processor.json');
    
    // 保留天数
    this.retentionDays = options.retentionDays || 30;
    
    // 单次最多处理的消息数
    this.maxMessagesPerSession = options.maxMessagesPerSession || 1000;
  }

  /**
   * 运行每日备份
   */
  async runDailyBackup() {
    console.log('🧠 开始每日 Session 备份...\n');

    // 确保目录存在
    this.ensureDirectories();

    // 1. 备份所有 session 文件
    console.log('📦 Step 1: 备份 Session 文件');
    const backups = this.backupSessions();
    console.log(`   ✅ 备份了 ${backups.length} 个 session 文件\n`);

    // 2. 增量处理：直接修改备份文件
    console.log('📝 Step 2: 增量处理备份文件');
    const lastProcessedTime = this.getLastProcessedTime();
    console.log(`   上次处理时间：${new Date(lastProcessedTime).toISOString()}`);
    
    let totalNewMessages = 0;
    for (const backup of backups) {
      const newMessages = await this.processBackupFile(backup.path, lastProcessedTime);
      totalNewMessages += newMessages.length;
    }
    console.log(`   ✅ 共提取 ${totalNewMessages} 条新消息\n`);

    // 3. 更新状态
    const now = Date.now();
    this.updateState(now, totalNewMessages);
    console.log(`📊 Step 3: 更新处理状态`);
    console.log(`   新处理时间：${new Date(now).toISOString()}\n`);

    // 4. 清理 30 天前的 daily 文件
    console.log(`🗑️  Step 4: 清理 ${this.retentionDays} 天前的备份`);
    const deletedCount = this.cleanupOldBackups(this.retentionDays);
    console.log(`   ✅ 删除了 ${deletedCount} 个旧文件\n`);

    console.log('🎉 每日 Session 备份完成！');
    
    return {
      backups: backups.length,
      newMessages: totalNewMessages,
      deleted: deletedCount
    };
  }

  /**
   * 确保目录存在
   */
  ensureDirectories() {
    if (!fs.existsSync(this.dailyDir)) {
      fs.mkdirSync(this.dailyDir, { recursive: true });
      console.log(`   创建目录：${this.dailyDir}`);
    }
    if (!fs.existsSync(this.stateDir)) {
      fs.mkdirSync(this.stateDir, { recursive: true });
      console.log(`   创建目录：${this.stateDir}`);
    }
  }

  /**
   * 获取当前时间戳字符串
   */
  getTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
  }

  /**
   * 备份所有 session 文件
   */
  backupSessions() {
    const backups = [];
    const timestamp = this.getTimestamp();

    if (!fs.existsSync(this.sessionDir)) {
      console.log(`   ⚠️  Session 目录不存在：${this.sessionDir}`);
      return backups;
    }

    const files = fs.readdirSync(this.sessionDir);
    
    files.forEach(file => {
      if (!file.endsWith('.jsonl')) return;

      const sourcePath = path.join(this.sessionDir, file);
      const sessionId = file.replace('.jsonl', '');
      const backupName = `${sessionId}_${timestamp}.jsonl`;
      const backupPath = path.join(this.dailyDir, backupName);

      // 复制文件
      fs.copyFileSync(sourcePath, backupPath);
      
      backups.push({
        sessionId,
        source: sourcePath,
        path: backupPath,
        backupName
      });

      console.log(`   📄 ${file} → ${backupName}`);
    });

    return backups;
  }

  /**
   * 获取上次处理时间
   */
  getLastProcessedTime() {
    if (!fs.existsSync(this.stateFile)) {
      // 首次运行，返回 7 天前的时间
      const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
      console.log(`   ⚠️  首次运行，使用 7 天前作为起始时间`);
      return sevenDaysAgo;
    }

    const state = JSON.parse(fs.readFileSync(this.stateFile, 'utf-8'));
    return state.lastProcessedTime || 0;
  }

  /**
   * 处理备份文件（从后往前读，提取新消息）
   */
  async processBackupFile(filePath, lastProcessedTime) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    const newMessages = [];
    
    // 从后往前读，快速定位新消息
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        const msg = JSON.parse(lines[i]);
        
        // 如果消息时间早于上次处理时间，停止
        if (msg.timestamp <= lastProcessedTime) {
          break;
        }
        
        newMessages.unshift(msg);
        
        // 优化：最多读 maxMessagesPerSession 条
        if (newMessages.length >= this.maxMessagesPerSession) {
          console.log(`   ⚠️  达到最大消息数限制 (${this.maxMessagesPerSession})`);
          break;
        }
      } catch (e) {
        console.log(`   ⚠️  解析失败：${lines[i].substring(0, 50)}...`);
      }
    }
    
    // 直接覆盖写入（只保留新消息）
    if (newMessages.length > 0) {
      const newContent = newMessages.map(m => JSON.stringify(m)).join('\n') + '\n';
      fs.writeFileSync(filePath, newContent, 'utf-8');
      
      const basename = path.basename(filePath);
      console.log(`   ✅ 处理：${basename} - ${newMessages.length} 条新消息`);
    } else {
      const basename = path.basename(filePath);
      console.log(`   ⏭️  跳过：${basename} - 无新消息`);
    }
    
    return newMessages;
  }

  /**
   * 更新处理状态
   */
  updateState(lastProcessedTime, totalNewMessages) {
    const state = {
      lastProcessedTime,
      lastRun: new Date().toISOString(),
      totalMessagesProcessed: totalNewMessages,
      version: '1.2.0'
    };
    
    fs.writeFileSync(this.stateFile, JSON.stringify(state, null, 2), 'utf-8');
  }

  /**
   * 清理旧备份文件
   */
  cleanupOldBackups(retentionDays) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
    const cutoffStr = cutoffDate.toISOString().split('T')[0].replace(/-/g, '');
    
    let deletedCount = 0;

    if (!fs.existsSync(this.dailyDir)) {
      return deletedCount;
    }

    const files = fs.readdirSync(this.dailyDir);
    
    files.forEach(file => {
      if (!file.endsWith('.jsonl')) return;

      // 从文件名提取日期（格式：sessionId_YYYYMMDD_HHMMSS.jsonl）
      const match = file.match(/_(\d{8})_\d{6}\.jsonl$/);
      if (!match) return;

      const fileDate = match[1];
      
      if (fileDate < cutoffStr) {
        const filePath = path.join(this.dailyDir, file);
        fs.unlinkSync(filePath);
        console.log(`   🗑️  删除：${file}`);
        deletedCount++;
      }
    });

    return deletedCount;
  }
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const backup = new DailySessionBackup();
  
  if (args[0] === 'run') {
    backup.runDailyBackup().catch(console.error);
  } else if (args[0] === 'test') {
    // 测试模式：不实际删除文件
    console.log('🧪 测试模式运行...\n');
    backup.runDailyBackup().catch(console.error);
  } else {
    console.log('用法：node daily-session-backup.js [run|test]');
    console.log('  run   - 运行完整备份流程');
    console.log('  test  - 测试模式（不删除文件）');
  }
}

module.exports = DailySessionBackup;
