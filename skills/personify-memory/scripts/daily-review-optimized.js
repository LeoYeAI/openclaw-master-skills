#!/usr/bin/env node

/**
 * Personify Memory - 优化版每日复盘
 * 添加详细日志，找出性能瓶颈
 */

const fs = require('fs');
const path = require('path');

class DailyReview {
  constructor(basePath = '/root/openclaw/memory') {
    this.basePath = basePath;
    this.dailyPath = path.join(basePath, 'daily');
    this.archivePath = path.join(basePath, 'archive');
    this.emotionFile = path.join(basePath, 'emotion-memory.json');
    this.knowledgeFile = path.join(basePath, 'knowledge-base.md');
    this.memoryFile = path.join(basePath, '..', 'MEMORY.md');
    this.indexFile = path.join(basePath, 'memory-index.json');
  }

  async runDailyReview() {
    console.log('🧠 开始每日记忆整理复盘...\n');
    let startTime = Date.now();

    // 1. 读取文件
    console.log('[1/7] 读取每日记忆文件...');
    const dailyFiles = this.readDailyFiles();
    console.log(`✅ 找到 ${dailyFiles.length} 个文件 (${Date.now() - startTime}ms)\n`);
    startTime = Date.now();

    // 2. 分析文件
    console.log('[2/7] 分析内容，提取关键信息...');
    const extractedData = this.analyzeFiles(dailyFiles);
    console.log(`✅ 提取完成 (${Date.now() - startTime}ms)`);
    console.log(`   - 项目进展：${extractedData.projects.length} 条`);
    console.log(`   - 经验教训：${extractedData.lessons.length} 条`);
    console.log(`   - 温暖瞬间：${extractedData.moments.length} 条\n`);
    startTime = Date.now();

    // 3. 更新情感记忆
    console.log('[3/7] 更新情感记忆...');
    this.updateEmotionMemory(extractedData);
    console.log(`✅ 完成 (${Date.now() - startTime}ms)\n`);
    startTime = Date.now();

    // 4. 更新知识库
    console.log('[4/7] 更新知识库...');
    this.updateKnowledgeBase(extractedData);
    console.log(`✅ 完成 (${Date.now() - startTime}ms)\n`);
    startTime = Date.now();

    // 5. 更新核心记忆
    console.log('[5/7] 更新核心记忆...');
    this.updateCoreMemory(extractedData);
    console.log(`✅ 完成 (${Date.now() - startTime}ms)\n`);
    startTime = Date.now();

    // 6. 更新记忆索引
    console.log('[6/7] 更新记忆索引...');
    this.updateIndex(extractedData);
    console.log(`✅ 完成 (${Date.now() - startTime}ms)\n`);
    startTime = Date.now();

    // 7. 归档旧文件
    console.log('[7/7] 归档旧文件...');
    this.archiveOldFiles();
    console.log(`✅ 完成 (${Date.now() - startTime}ms)\n`);

    console.log('🎉 每日记忆整理复盘完成！');
  }

  readDailyFiles() {
    if (!fs.existsSync(this.dailyPath)) return [];

    const files = fs.readdirSync(this.dailyPath)
      .filter(f => f.endsWith('.jsonl'))
      .map(filename => {
        const filepath = path.join(this.dailyPath, filename);
        const content = fs.readFileSync(filepath, 'utf-8');
        const messages = content.split('\n')
          .filter(line => line.trim())
          .map(line => {
            try { return JSON.parse(line); } catch (e) { return null; }
          })
          .filter(msg => msg !== null);
        const match = filename.match(/_(\d{8})_\d{6}\.jsonl$/);
        const date = match ? match[1] : filename.replace('.jsonl', '');
        return { filename, filepath, content, date, messages };
      });

    return files;
  }

  analyzeFiles(files) {
    const data = { projects: [], lessons: [], moments: [], decisions: [], preferences: [] };
    const patterns = {
      project: [/✅.*完成/gi, /已完成/gi, /上线/gi, /发布/gi],
      lesson: [
        /问题[：:].{10,}解决[：:]/gi,      // 问题：xxx 解决：xxx（结构化格式）
        /解决[方法|方案][：:].{20,}/gi,    // 解决方案：xxx
        /经验总结[：:].{20,}/gi,           // 经验总结：xxx
        /教训[：:].{15,}/gi,               // 教训：xxx
        /注意事项[：:].{15,}/gi,           // 注意事项：xxx
        /Bug.*修复/gi,                     // Bug 修复
        /报错.*解决/gi,                    // 报错...解决
      ],
      moment: [/温暖/gi, /感动/gi, /谢谢/gi, /承诺/gi, /答应/gi, /信任/gi],
      decision: [/我决定/gi, /我们决定/gi, /最终决定/gi, /确定使用/gi, /采用.*方案/gi, /选择.*策略/gi],
      preference: [/我喜欢/gi, /我不喜欢/gi, /习惯了/gi, /偏好/gi, /习惯用/gi]
    };

    // 排除模式（这些内容不应该被提取）
    const EXCLUDE_PATTERNS = [
      /^\d+\./,  // 列表项
      /^\[/,     // JSON 数组
      /^\{/,     // JSON 对象
      /```/,     // 代码块
      /'type':/gi,
      /"type":/gi,
      /^\*\*/,   // Markdown 粗体
      /^好的/gi,
      /^让我/gi,
      /^我这就/gi,
      /需要我/gi,
      /请告诉/gi,
    ];

    const MIN_DECISION_LEN = 30;
    const MAX_LEN = 3000;

    files.forEach(file => {
      file.messages.forEach((msg) => {
        const text = this.extractTextFromMessage(msg);
        if (!text) return;

        const trimmedText = text.trim();
        if (trimmedText.length > MAX_LEN) return;

        // 检查是否应该排除
        const shouldExclude = EXCLUDE_PATTERNS.some(pattern => pattern.test(trimmedText));
        if (shouldExclude) return;

        if (patterns.project.some(p => p.test(trimmedText))) {
          data.projects.push({ date: file.date, content: trimmedText.substring(0, 500), source: file.filename });
        }
        if (patterns.lesson.some(p => p.test(trimmedText))) {
          data.lessons.push({ date: file.date, content: trimmedText.substring(0, 500), source: file.filename });
        }
        if (patterns.moment.some(p => p.test(trimmedText))) {
          data.moments.push({ date: file.date, content: trimmedText.substring(0, 500), source: file.filename });
        }
        if (patterns.decision.some(p => p.test(trimmedText)) && trimmedText.length >= MIN_DECISION_LEN) {
          data.decisions.push({ date: file.date, content: trimmedText.substring(0, 500), source: file.filename });
        }
        if (patterns.preference.some(p => p.test(trimmedText))) {
          data.preferences.push({ date: file.date, content: trimmedText.substring(0, 500), source: file.filename });
        }
      });
    });

    return data;
  }

  extractTextFromMessage(event) {
    if (!event.message) return '';
    const msg = event.message;
    if (!msg.content) return '';
    if (Array.isArray(msg.content)) {
      return msg.content.filter(item => item.type === 'text').map(item => item.text || '').join(' ');
    }
    return String(msg.content);
  }

  updateEmotionMemory(data) {
    let emotion = { Amber: { warmMoments: [] } };
    if (fs.existsSync(this.emotionFile)) {
      emotion = JSON.parse(fs.readFileSync(this.emotionFile, 'utf-8'));
    }

    // 更新项目进展
    data.projects.forEach(project => {
      if (!emotion.Amber.projects) emotion.Amber.projects = {};
      const match = project.content.match(/([^\s:：]+).*完成/);
      if (match) {
        emotion.Amber.projects[match[1]] = `✅ 已完成（${project.date}）`;
      }
    });

    // 更新温暖瞬间（去重优化：使用 Set）
    const existingKeys = new Set(
      (emotion.Amber.warmMoments || []).map(m => m.content?.substring(0, 30) || '')
    );

    let newCount = 0;
    data.moments.forEach(moment => {
      const key = moment.content.substring(0, 30);
      if (!existingKeys.has(key)) {
        if (!emotion.Amber.warmMoments) emotion.Amber.warmMoments = [];
        emotion.Amber.warmMoments.push({
          date: moment.date || new Date().toISOString().split('T')[0],
          content: moment.content,
          feeling: '被信任'
        });
        existingKeys.add(key);
        newCount++;
      }
    });

    emotion.lastUpdated = new Date().toISOString();
    fs.writeFileSync(this.emotionFile, JSON.stringify(emotion, null, 2), 'utf-8');
    console.log(`   新增 ${newCount} 条温暖瞬间`);
  }

  updateKnowledgeBase(data) {
    if (data.lessons.length === 0) {
      console.log('   无新经验教训');
      return;
    }

    const today = new Date().toISOString().split('T')[0];
    let newSection = `\n\n## ${today} 自动整理 - 新增经验\n\n`;

    data.lessons.slice(0, 10).forEach((lesson, index) => {
      newSection += `### ${index + 1}. ${lesson.content}\n\n`;
    });

    fs.appendFileSync(this.knowledgeFile, newSection, 'utf-8');
    console.log(`   新增 ${Math.min(data.lessons.length, 10)} 条经验`);
  }

  updateCoreMemory(data) {
    // 只处理高重要性的决策
    const importantDecisions = data.decisions.filter(d => 
      d.content.length > 20 && d.content.length < 500
    );
    
    if (importantDecisions.length === 0) {
      console.log('   无新决策需要记录');
      return;
    }

    const today = new Date().toISOString().split('T')[0];
    let newContent = `\n\n### 📌 ${today} 自动整理 - 重要决策\n\n`;
    
    importantDecisions.slice(0, 5).forEach((decision, index) => {
      newContent += `${index + 1}. ${decision.content}\n\n`;
    });

    // 追加到 MEMORY.md 的"身份与成长"章节后
    try {
      fs.appendFileSync(this.memoryFile, newContent, 'utf-8');
      console.log(`   新增 ${Math.min(importantDecisions.length, 5)} 条决策记录`);
    } catch (err) {
      console.error(`   ❌ 写入 MEMORY.md 失败：${err.message}`);
    }
  }

  updateIndex(data) {
    let index = { entries: [], stats: { totalEntries: 0 } };
    if (fs.existsSync(this.indexFile)) {
      index = JSON.parse(fs.readFileSync(this.indexFile, 'utf-8'));
    }

    // 批量添加条目
    const newEntries = [];
    const today = new Date().toISOString().split('T')[0];

    data.projects.forEach(p => {
      newEntries.push({
        id: 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        title: p.content.substring(0, 50),
        date: today,
        category: '项目进展',
        importance: 'high',
        keywords: ['项目', '完成'],
        location: { type: 'daily', file: p.source },
        archived: false,
        summary: p.content
      });
    });

    data.lessons.forEach(l => {
      newEntries.push({
        id: 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        title: '经验教训：' + l.content.substring(0, 30),
        date: today,
        category: '经验总结',
        importance: 'high',
        keywords: ['经验', '教训'],
        location: { type: 'knowledge', file: 'knowledge-base.md' },
        archived: false,
        summary: l.content
      });
    });

    index.entries.push(...newEntries);
    index.stats.totalEntries = index.entries.length;
    index.lastUpdated = new Date().toISOString();

    fs.writeFileSync(this.indexFile, JSON.stringify(index, null, 2), 'utf-8');
    console.log(`   总计 ${index.stats.totalEntries} 条记录`);
  }

  archiveOldFiles() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30);
    const cutoffStr = cutoffDate.toISOString().split('T')[0].replace(/-/g, '');

    console.log(`   归档阈值：${cutoffStr} (30 天前)`);

    if (!fs.existsSync(this.dailyPath)) {
      console.log('   daily 目录不存在');
      return;
    }

    const files = fs.readdirSync(this.dailyPath);
    let archived = 0;

    files.forEach(file => {
      if (!file.endsWith('.jsonl')) return;

      const match = file.match(/_(\d{8})_\d{6}\.jsonl$/);
      if (!match) return;

      const fileDate = match[1];
      if (fileDate < cutoffStr) {
        this.archiveFile(file, fileDate);
        archived++;
      }
    });

    console.log(`   归档了 ${archived} 个文件`);
  }

  archiveFile(filename, fileDate) {
    const dailyFile = path.join(this.dailyPath, filename);
    const monthDir = path.join(this.archivePath, fileDate.substring(0, 6));

    if (!fs.existsSync(dailyFile)) return;

    if (!fs.existsSync(monthDir)) {
      fs.mkdirSync(monthDir, { recursive: true });
    }

    const archiveFile = path.join(monthDir, filename);
    fs.renameSync(dailyFile, archiveFile);

    console.log(`     📦 ${filename} → archive/${fileDate.substring(0, 6)}/`);
  }
}

// CLI usage
if (require.main === module) {
  const review = new DailyReview();
  review.runDailyReview().catch(err => {
    console.error('❌ 错误:', err.message);
    console.error(err.stack);
    process.exit(1);
  });
}

module.exports = DailyReview;
