#!/usr/bin/env node

/**
 * Personify Memory - Archive Script
 * 
 * 归档每日记忆到 archive/ 目录
 * 运行时间：每天凌晨 3:00
 */

const fs = require('fs');
const path = require('path');

class ArchiveManager {
  constructor(basePath = '/root/openclaw/memory') {
    this.basePath = basePath;
    this.dailyPath = path.join(basePath, 'daily');
    this.archivePath = path.join(basePath, 'archive');
    this.indexFile = path.join(basePath, 'memory-index.json');
  }

  /**
   * 归档指定日期的记忆
   */
  archiveDate(dateStr) {
    const dailyFile = path.join(this.dailyPath, `${dateStr}.md`);
    const monthDir = path.join(this.archivePath, dateStr.substring(0, 7)); // YYYY-MM

    if (!fs.existsSync(dailyFile)) {
      console.log(`⚠️  Daily file not found: ${dailyFile}`);
      return { success: false, message: 'File not found' };
    }

    // 创建月份目录
    if (!fs.existsSync(monthDir)) {
      fs.mkdirSync(monthDir, { recursive: true });
      console.log(`✅ Created month directory: ${monthDir}`);
    }

    // 移动文件
    const archiveFile = path.join(monthDir, `${dateStr}.md`);
    fs.renameSync(dailyFile, archiveFile);
    console.log(`✅ Archived: ${dateStr} → ${archiveFile}`);

    // 更新索引
    this.markAsArchived(dateStr);

    return { success: true, file: archiveFile };
  }

  /**
   * 归档 N 天前的所有记忆
   */
  archiveOldFiles(daysAgo = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysAgo);
    const cutoffStr = cutoffDate.toISOString().split('T')[0];

    console.log(`📅 Archiving files before ${cutoffStr}...`);

    if (!fs.existsSync(this.dailyPath)) {
      console.log('ℹ️  Daily directory not found');
      return [];
    }

    const files = fs.readdirSync(this.dailyPath);
    const archived = [];

    for (const file of files) {
      if (!file.endsWith('.md')) continue;

      const dateStr = file.replace('.md', '');
      if (dateStr < cutoffStr) {
        const result = this.archiveDate(dateStr);
        if (result.success) {
          archived.push(dateStr);
        }
      }
    }

    console.log(`✅ Archived ${archived.length} files`);
    return archived;
  }

  /**
   * 标记为已归档
   */
  markAsArchived(dateStr) {
    if (!fs.existsSync(this.indexFile)) return;

    const index = JSON.parse(fs.readFileSync(this.indexFile, 'utf-8'));
    
    index.entries.forEach(entry => {
      if (entry.date === dateStr) {
        entry.archived = true;
        // 更新位置信息
        const monthDir = dateStr.substring(0, 7);
        entry.location.type = 'archive';
        entry.location.file = `archive/${monthDir}/${dateStr}.md`;
      }
    });

    index.stats.archivedMemories = index.entries.filter(e => e.archived).length;
    index.lastUpdated = new Date().toISOString();

    fs.writeFileSync(this.indexFile, JSON.stringify(index, null, 2), 'utf-8');
  }

  /**
   * 生成月度总结
   */
  generateMonthSummary(yearMonth) {
    const monthDir = path.join(this.archivePath, yearMonth);
    
    if (!fs.existsSync(monthDir)) {
      console.log(`⚠️  Month directory not found: ${monthDir}`);
      return null;
    }

    const files = fs.readdirSync(monthDir).filter(f => f.endsWith('.md'));
    const summary = {
      month: yearMonth,
      totalDays: files.length,
      dates: files.map(f => f.replace('.md', '')),
      generatedAt: new Date().toISOString()
    };

    // 写入总结文件
    const summaryFile = path.join(monthDir, 'month-summary.json');
    fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2), 'utf-8');
    console.log(`✅ Generated month summary: ${summaryFile}`);

    return summary;
  }

  /**
   * 运行归档任务（定时调用）
   */
  runArchiveTask() {
    console.log('🕐 Running archive task...');
    
    // 归档 7 天前的文件
    const archived = this.archiveOldFiles(7);
    
    // 如果是月末，生成本月总结
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    const isMonthEnd = nextMonth.getDate() === 1 && today.getDate() >= 28;
    
    if (isMonthEnd) {
      const currentMonth = today.toISOString().substring(0, 7);
      this.generateMonthSummary(currentMonth);
    }

    console.log('✅ Archive task completed');
    return { archived, isMonthEnd };
  }
}

// CLI usage
if (require.main === module) {
  const manager = new ArchiveManager();
  
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case 'run':
      manager.runArchiveTask();
      break;

    case 'archive':
      if (args[0]) {
        manager.archiveDate(args[0]);
      } else {
        console.log('Usage: node archive.js archive <date>');
        console.log('Example: node archive.js archive 2026-03-01');
      }
      break;

    case 'archive-old':
      const days = parseInt(args[0]) || 7;
      manager.archiveOldFiles(days);
      break;

    case 'summary':
      if (args[0]) {
        manager.generateMonthSummary(args[0]);
      } else {
        console.log('Usage: node archive.js summary <YYYY-MM>');
        console.log('Example: node archive.js summary 2026-03');
      }
      break;

    default:
      console.log('Usage: node archive.js <command> [args]');
      console.log('Commands:');
      console.log('  run           - Run archive task (for cron)');
      console.log('  archive <date>- Archive specific date');
      console.log('  archive-old [days] - Archive files older than N days');
      console.log('  summary <YYYY-MM> - Generate month summary');
  }
}
