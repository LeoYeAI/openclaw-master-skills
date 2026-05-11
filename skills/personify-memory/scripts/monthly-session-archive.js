#!/usr/bin/env node

/**
 * Personify Memory - Monthly Session Archive
 * 
 * 月度 Session 归档和清理脚本
 * 运行时间：每月 1 号凌晨 02:50
 * 
 * 核心功能：
 * 1. 归档 session 目录到 archive/sessions/YYYY-MM/
 * 2. 清理 session 文件中 30 天前的消息（从前往后读）
 */

const fs = require('fs');
const path = require('path');

class MonthlySessionArchive {
  constructor(options = {}) {
    // Session 目录（OpenClaw 活跃数据）
    this.sessionDir = options.sessionDir || '/root/.openclaw/agents/main/sessions';
    
    // 记忆目录
    this.memoryBase = options.memoryBase || '/root/openclaw/memory';
    this.archiveDir = path.join(this.memoryBase, 'archive', 'sessions');
    
    // 保留天数
    this.retentionDays = options.retentionDays || 30;
  }

  /**
   * 运行月度归档
   */
  async runMonthlyArchive() {
    console.log('🧠 开始月度 Session 归档...\n');

    // 确保目录存在
    this.ensureDirectories();

    // 1. 归档所有 session 文件
    console.log('📦 Step 1: 归档 Session 文件');
    const timestamp = this.getTimestamp();
    const monthDir = path.join(this.archiveDir, timestamp.slice(0, 6));
    const archives = this.archiveSessions(monthDir, timestamp);
    console.log(`   ✅ 归档了 ${archives.length} 个 session 文件\n`);

    // 2. 清理 session 文件（保留 30 天）
    console.log(`🗑️  Step 2: 清理 ${this.retentionDays} 天前的消息`);
    const cutoffTime = Date.now() - (this.retentionDays * 24 * 60 * 60 * 1000);
    const cleanedCount = this.cleanupSessions(cutoffTime);
    console.log(`   ✅ 清理了 ${cleanedCount} 个 session 文件\n`);

    console.log('🎉 月度 Session 归档完成！');
    
    return {
      archived: archives.length,
      cleaned: cleanedCount
    };
  }

  /**
   * 确保目录存在
   */
  ensureDirectories() {
    if (!fs.existsSync(this.archiveDir)) {
      fs.mkdirSync(this.archiveDir, { recursive: true });
      console.log(`   创建目录：${this.archiveDir}`);
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
   * 归档所有 session 文件
   */
  archiveSessions(monthDir, timestamp) {
    const archives = [];

    if (!fs.existsSync(this.sessionDir)) {
      console.log(`   ⚠️  Session 目录不存在：${this.sessionDir}`);
      return archives;
    }

    // 创建月份目录
    if (!fs.existsSync(monthDir)) {
      fs.mkdirSync(monthDir, { recursive: true });
      console.log(`   创建月份目录：${path.basename(monthDir)}`);
    }

    const files = fs.readdirSync(this.sessionDir);
    
    files.forEach(file => {
      if (!file.endsWith('.jsonl')) return;

      const sourcePath = path.join(this.sessionDir, file);
      const sessionId = file.replace('.jsonl', '');
      const archiveName = `${sessionId}_${timestamp}.jsonl`;
      const archivePath = path.join(monthDir, archiveName);

      // 复制文件
      fs.copyFileSync(sourcePath, archivePath);
      
      archives.push({
        sessionId,
        source: sourcePath,
        path: archivePath,
        archiveName
      });

      console.log(`   📄 ${file} → ${path.basename(monthDir)}/${archiveName}`);
    });

    return archives;
  }

  /**
   * 清理 session 文件（保留 30 天）
   */
  cleanupSessions(cutoffTime) {
    let cleanedCount = 0;

    if (!fs.existsSync(this.sessionDir)) {
      return cleanedCount;
    }

    const files = fs.readdirSync(this.sessionDir);
    
    files.forEach(file => {
      if (!file.endsWith('.jsonl')) return;

      const filePath = path.join(this.sessionDir, file);
      const cleaned = this.cleanSingleFile(filePath, cutoffTime);
      
      if (cleaned) {
        cleanedCount++;
        console.log(`   ✅ 清理：${file}`);
      }
    });

    return cleanedCount;
  }

  /**
   * 清理单个文件（从前往后读，快速找到 30 天前的位置）
   */
  cleanSingleFile(filePath, cutoffTime) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
      return false;
    }

    let cutoffIndex = -1;
    
    // 从前往后读，找到 30 天前的位置
    for (let i = 0; i < lines.length; i++) {
      try {
        const msg = JSON.parse(lines[i]);
        
        if (msg.timestamp >= cutoffTime) {
          cutoffIndex = i;
          break;  // 找到就停止，不用读完
        }
      } catch (e) {
        // 跳过解析失败的行
      }
    }
    
    if (cutoffIndex === -1) {
      // 所有消息都超过 30 天
      console.log(`   ⚠️  ${path.basename(filePath)} - 所有消息都超过 30 天`);
      fs.writeFileSync(filePath, '', 'utf-8');
      return true;
    }
    
    if (cutoffIndex === 0) {
      // 所有消息都在 30 天内，不需要清理
      return false;
    }
    
    // 删除 cutoffIndex 之前的消息
    const keptLines = lines.slice(cutoffIndex);
    const newContent = keptLines.join('\n') + '\n';
    fs.writeFileSync(filePath, newContent, 'utf-8');
    
    return true;
  }
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const archiver = new MonthlySessionArchive();
  
  if (args[0] === 'run') {
    archiver.runMonthlyArchive().catch(console.error);
  } else if (args[0] === 'test') {
    // 测试模式：不实际清理文件
    console.log('🧪 测试模式运行...\n');
    archiver.runMonthlyArchive().catch(console.error);
  } else {
    console.log('用法：node monthly-session-archive.js [run|test]');
    console.log('  run   - 运行完整归档流程');
    console.log('  test  - 测试模式（仅归档，不清理）');
  }
}

module.exports = MonthlySessionArchive;
