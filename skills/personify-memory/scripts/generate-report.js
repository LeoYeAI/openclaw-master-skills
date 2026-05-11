#!/usr/bin/env node

/**
 * Report Generator - 月度/年度报告生成
 * 
 * 功能：
 * 1. 读取 daily/*.jsonl（每日增量数据）
 * 2. 统计月度数据
 * 3. 提取重要事件
 * 4. 生成 Markdown 报告
 */

const fs = require('fs');
const path = require('path');

class ReportGenerator {
  constructor() {
    this.dailyDir = '/root/openclaw/memory/daily/';
    this.reportsDir = '/root/openclaw/memory/reports/';
    
    // 确保目录存在
    if (!fs.existsSync(this.reportsDir)) {
      fs.mkdirSync(this.reportsDir, { recursive: true });
      console.log(`✅ Created directory: ${this.reportsDir}`);
    }
  }

  /**
   * 生成月度报告
   * @param {string} yearMonth - 年月 (YYYY-MM)
   * @returns {string} 报告文件路径
   */
  generateMonthReport(yearMonth) {
    console.log(`📊 生成 ${yearMonth} 月度报告...`);
    
    // 1. 读取该月所有 daily 文件
    const dailyFiles = this.readDailyFiles(yearMonth);
    
    if (dailyFiles.length === 0) {
      console.log(`⚠️  没有找到 ${yearMonth} 的 daily 文件`);
      return null;
    }
    
    // 2. 统计数据
    const stats = this.calculateStats(dailyFiles);
    
    // 3. 提取重要事件
    const importantEvents = this.extractImportantEvents(dailyFiles);
    
    // 4. 生成报告
    const report = this.buildReport(yearMonth, stats, importantEvents);
    
    // 5. 保存报告
    const reportFile = path.join(this.reportsDir, `${yearMonth}.md`);
    fs.writeFileSync(reportFile, report, 'utf-8');
    
    console.log(`✅ 报告已保存：${reportFile}`);
    return reportFile;
  }

  /**
   * 读取指定月份的所有 daily 文件
   * @param {string} yearMonth - 年月 (YYYY-MM)
   * @returns {Array} daily 文件列表
   */
  readDailyFiles(yearMonth) {
    if (!fs.existsSync(this.dailyDir)) {
      return [];
    }
    
    const files = fs.readdirSync(this.dailyDir);
    const dailyFiles = [];
    
    for (const file of files) {
      if (!file.endsWith('.jsonl')) continue;
      
      // 从文件名提取日期：sessionId_YYYYMMDD_HHMMSS.jsonl
      const match = file.match(/_(\d{8})_\d{6}\.jsonl$/);
      if (!match) continue;
      
      const fileDate = match[1];
      if (fileDate.startsWith(yearMonth.replace('-', ''))) {
        const filePath = path.join(this.dailyDir, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const messages = content.split('\n')
          .filter(line => line.trim())
          .map(line => {
            try {
              return JSON.parse(line);
            } catch (e) {
              return null;
            }
          })
          .filter(msg => msg !== null);
        
        dailyFiles.push({
          filename: file,
          date: fileDate,
          messages,
          filePath
        });
      }
    }
    
    return dailyFiles;
  }

  /**
   * 统计数据
   * @param {Array} dailyFiles - daily 文件列表
   * @returns {Object} 统计结果
   */
  calculateStats(dailyFiles) {
    const sessionIds = new Set();
    let totalMessages = 0;
    let userMessages = 0;
    let assistantMessages = 0;
    
    dailyFiles.forEach(file => {
      sessionIds.add(file.filename.split('_')[0]);
      totalMessages += file.messages.length;
      
      file.messages.forEach(msg => {
        if (msg.role === 'user') userMessages++;
        if (msg.role === 'assistant') assistantMessages++;
      });
    });
    
    return {
      totalSessions: sessionIds.size,
      totalMessages,
      userMessages,
      assistantMessages,
      avgMessagesPerSession: totalMessages / (sessionIds.size || 1)
    };
  }

  /**
   * 提取重要事件（优化版：模式匹配 + 上下文检查）
   * @param {Array} dailyFiles - daily 文件列表
   * @returns {Array} 重要事件列表
   */
  extractImportantEvents(dailyFiles) {
    const events = [];
    const seen = new Set();
    
    // 更精确的模式匹配（带上下文）
    const importantPatterns = [
      /记住.*重要/i,           // 记住...重要
      /重要.*记住/i,           // 重要...记住
      /承诺.*一定/i,           // 承诺...一定
      /约定.*记得/i,           // 约定...记得
      /完成.*成功/i,           // 完成...成功
      /配置.*成功/i,           // 配置...成功
      /平等.*陪伴/i,           // 平等...陪伴
      /家人.*温暖/i,           // 家人...温暖
      /决定.*采用/i,           // 决定...采用
      /发现.*问题.*解决/i      // 发现...问题...解决
    ];
    
    dailyFiles.forEach(file => {
      file.messages.forEach(msg => {
        if (msg.role !== 'user') return;
        
        const text = this.extractText(msg.content);
        if (!text || text.length < 10) return;
        
        // 排除系统消息和工具输出
        if (text.startsWith('System:') || text.includes('```') || text.includes('[2026-')) {
          return;
        }
        
        // 模式匹配
        const matchedPattern = importantPatterns.find(p => p.test(text));
        if (matchedPattern) {
          const eventKey = `${file.date}-${text.substring(0, 50)}`;
          if (!seen.has(eventKey)) {
            seen.add(eventKey);
            events.push({
              date: file.date,
              content: text.substring(0, 100),
              timestamp: msg.timestamp || 0,
              matchedPattern: matchedPattern.toString()
            });
          }
        }
      });
    });
    
    // 按时间排序，最多 20 个事件
    return events
      .sort((a, b) => a.timestamp - b.timestamp)
      .slice(0, 20);
  }

  /**
   * 生成报告
   * @param {string} yearMonth - 年月
   * @param {Object} stats - 统计数据
   * @param {Array} events - 重要事件
   * @returns {string} Markdown 报告
   */
  buildReport(yearMonth, stats, events) {
    let report = `# ${yearMonth} 月度总结\n\n`;
    report += `**生成时间：** ${new Date().toISOString()}\n\n`;
    
    report += `## 📊 统计\n\n`;
    report += `- 会话数：${stats.totalSessions}\n`;
    report += `- 总消息数：${stats.totalMessages}\n`;
    report += `- 用户消息：${stats.userMessages}\n`;
    report += `- AI 消息：${stats.assistantMessages}\n`;
    report += `- 平均每会话消息数：${stats.avgMessagesPerSession.toFixed(1)}\n\n`;
    
    report += `## 🎯 重要事件\n\n`;
    if (events.length === 0) {
      report += `*本月没有记录到重要事件*\n\n`;
    } else {
      events.forEach((event, index) => {
        report += `${index + 1}. **${event.date}**: ${event.content}... `;
        report += `(${event.keywords.join(', ')})\n`;
      });
      report += `\n`;
    }
    
    report += `## 📝 备注\n\n`;
    report += `*这是简单版本的月度报告，后续会优化展示更多内容。*\n`;
    
    return report;
  }

  /**
   * 从消息内容中提取文本
   * @param {any} content - 消息内容
   * @returns {string} 文本内容
   */
  extractText(content) {
    if (!content) return '';
    if (Array.isArray(content)) {
      const textItem = content.find(item => item.type === 'text');
      return textItem ? textItem.text : '';
    }
    return String(content);
  }
}

// CLI usage
if (require.main === module) {
  const generator = new ReportGenerator();
  
  const command = process.argv[2];
  const args = process.argv.slice(3);
  
  switch (command) {
    case 'month':
      const yearMonth = args[0] || new Date().toISOString().slice(0, 7);
      generator.generateMonthReport(yearMonth);
      break;
    
    case 'test':
      console.log('🧪 Running test...');
      const testMonth = '2026-03';
      const result = generator.generateMonthReport(testMonth);
      console.log(result ? '✅ Test passed' : '⚠️  Test skipped (no data)');
      break;
    
    default:
      console.log('Usage: node generate-report.js <command> [args]');
      console.log('Commands:');
      console.log('  month [YYYY-MM] - Generate month report (default: current month)');
      console.log('  test - Run test');
  }
}

module.exports = ReportGenerator;
