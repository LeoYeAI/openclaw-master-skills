#!/usr/bin/env node

/**
 * Personify Memory - Core Memory Manager
 * 
 * 核心记忆管理器，提供记忆更新、搜索、归档、索引构建功能
 */

const fs = require('fs');
const path = require('path');
const synonyms = require('./synonyms.js');

class MemoryManager {
  constructor(basePath = '/root/openclaw/memory') {
    this.basePath = basePath;
    this.dailyPath = path.join(basePath, 'daily');
    this.archivePath = path.join(basePath, 'archive');
    this.indexFile = path.join(basePath, 'memory-index.json');
    
    // 语义搜索配置
    this.synonymsEnabled = true;  // 是否启用同义词扩展
    this.minMatchCount = 1;       // 最少匹配关键词数
    
    // 确保目录存在
    this.ensureDirectories();
  }

  /**
   * 确保所有必要目录存在
   */
  ensureDirectories() {
    [this.basePath, this.dailyPath, this.archivePath].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`✅ Created directory: ${dir}`);
      }
    });
  }

  /**
   * 更新记忆
   * @param {Object} options - 记忆选项
   * @param {string} options.content - 记忆内容
   * @param {string} options.type - 记忆类型 (core/emotion/knowledge/daily)
   * @param {string} options.category - 分类标签
   * @param {string} options.importance - 重要程度 (critical/high/medium/low)
   * @param {Array} options.tags - 关键词标签
   * @param {string} options.title - 记忆标题
   * @param {string} options.date - 日期 (YYYY-MM-DD)
   * @returns {Object} 更新结果
   */
  async updateMemory(options) {
    const {
      content,
      type = 'daily',
      category = '日常记录',
      importance = 'medium',
      tags = [],
      title,
      date = new Date().toISOString().split('T')[0]
    } = options;

    console.log(`📝 Updating memory: ${type} - ${title || 'Untitled'}`);

    let filePath;
    let entry;

    switch (type) {
      case 'core':
        filePath = path.join(this.basePath, '..', 'MEMORY.md');
        entry = await this.updateCoreMemory(content, title, category, tags);
        break;

      case 'emotion':
        filePath = path.join(this.basePath, 'emotion-memory.json');
        entry = await this.updateEmotionMemory(content, category, tags);
        break;

      case 'knowledge':
        filePath = path.join(this.basePath, 'knowledge-base.md');
        entry = await this.updateKnowledgeBase(content, title, category, tags);
        break;

      case 'daily':
      default:
        filePath = path.join(this.dailyPath, `${date}.md`);
        entry = await this.updateDailyMemory(content, title, date, category, tags);
        break;
    }

    // 更新索引
    if (entry) {
      await this.addToIndex({
        id: entry.id,
        title: entry.title || title || 'Untitled',
        date,
        category,
        importance,
        keywords: tags,
        location: {
          type,
          file: path.relative(this.basePath, filePath)
        },
        archived: false,
        summary: content.substring(0, 200) + '...'
      });
    }

    return {
      success: true,
      file: filePath,
      entry
    };
  }

  /**
   * 更新核心记忆 (MEMORY.md)
   */
  async updateCoreMemory(content, title, category, tags) {
    const filePath = path.join(this.basePath, '..', 'MEMORY.md');
    const entry = {
      id: `mem_${Date.now()}`,
      title: title || '核心记忆',
      content,
      category,
      tags,
      timestamp: new Date().toISOString()
    };

    // 如果文件不存在，创建基础模板
    if (!fs.existsSync(filePath)) {
      const template = this.getMemoryTemplate();
      fs.writeFileSync(filePath, template, 'utf-8');
    }

    // 读取现有内容
    let existingContent = '';
    if (fs.existsSync(filePath)) {
      existingContent = fs.readFileSync(filePath, 'utf-8');
    }

    // 查找合适的位置插入（在"身份与成长"章节后，或在文件末尾）
    const insertMarker = '## 🦞 身份与成长';
    const insertIndex = existingContent.indexOf(insertMarker);
    
    let newContent;
    if (insertIndex !== -1) {
      // 找到插入点，在该章节后插入
      const sectionEnd = existingContent.indexOf('\n\n---', insertIndex);
      if (sectionEnd !== -1) {
        // 在章节结束前插入
        const insertPos = existingContent.indexOf('\n', sectionEnd);
        newContent = existingContent.substring(0, insertPos) + 
          `\n\n### 📌 ${title || '新记忆'}\n\n${content}\n` + 
          existingContent.substring(insertPos);
      } else {
        newContent = existingContent + `\n\n### 📌 ${title || '新记忆'}\n\n${content}\n`;
      }
    } else {
      // 找不到标记，追加到文件末尾
      newContent = existingContent + `\n\n---\n\n### 📌 ${title || '新记忆'}\n\n${content}\n`;
    }

    fs.writeFileSync(filePath, newContent, 'utf-8');

    console.log(`✅ Core memory updated: ${filePath}`);
    return entry;
  }

  /**
   * 更新情感记忆 (emotion-memory.json)
   */
  async updateEmotionMemory(content, category, tags) {
    const filePath = path.join(this.basePath, 'emotion-memory.json');
    const entry = {
      id: `emotion_${Date.now()}`,
      content,
      category,
      tags,
      timestamp: new Date().toISOString()
    };

    let data = { Amber: {}, Grace: {} };
    
    if (fs.existsSync(filePath)) {
      data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    }

    // 根据分类添加到对应位置
    if (!data.warmMoments) {
      data.warmMoments = [];
    }
    data.warmMoments.push(entry);

    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    console.log(`✅ Emotion memory updated: ${filePath}`);
    return entry;
  }

  /**
   * 更新知识库 (knowledge-base.md)
   */
  async updateKnowledgeBase(content, title, category, tags) {
    const filePath = path.join(this.basePath, 'knowledge-base.md');
    const entry = {
      id: `kb_${Date.now()}`,
      title: title || '知识条目',
      content,
      category,
      tags,
      timestamp: new Date().toISOString()
    };

    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, '# 📚 知识库\n\n', 'utf-8');
    }

    const appendContent = `\n## ${title || '新条目'}\n\n${content}\n`;
    fs.appendFileSync(filePath, appendContent, 'utf-8');

    console.log(`✅ Knowledge base updated: ${filePath}`);
    return entry;
  }

  /**
   * 更新每日记忆
   */
  async updateDailyMemory(content, title, date, category, tags) {
    const filePath = path.join(this.dailyPath, `${date}.md`);
    const entry = {
      id: `daily_${date}_${Date.now()}`,
      title: title || '每日记录',
      content,
      category,
      tags,
      timestamp: new Date().toISOString()
    };

    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, `# ${date} - 每日记忆\n\n`, 'utf-8');
    }

    const appendContent = `\n## ${title || '新记录'}\n\n${content}\n`;
    fs.appendFileSync(filePath, appendContent, 'utf-8');

    console.log(`✅ Daily memory updated: ${filePath}`);
    return entry;
  }

  /**
   * 添加到索引
   */
  async addToIndex(entry) {
    let index = {
      version: '1.0',
      lastUpdated: new Date().toISOString(),
      entries: [],
      categories: [],
      importanceLevels: ['critical', 'high', 'medium', 'low'],
      stats: {
        totalEntries: 0,
        coreMemories: 0,
        dailyMemories: 0,
        archivedMemories: 0
      }
    };

    if (fs.existsSync(this.indexFile)) {
      index = JSON.parse(fs.readFileSync(this.indexFile, 'utf-8'));
    }

    index.entries.push(entry);
    index.lastUpdated = new Date().toISOString();
    index.stats.totalEntries = index.entries.length;

    // 更新分类统计
    const categories = new Set(index.entries.map(e => e.category));
    index.categories = Array.from(categories);

    fs.writeFileSync(this.indexFile, JSON.stringify(index, null, 2), 'utf-8');
    console.log(`✅ Index updated: ${this.indexFile}`);
  }

  /**
   * 搜索记忆（支持同义词扩展）
   */
  async searchMemory(query, options = {}) {
    const {
      includeArchived = false,
      category = null,
      importance = null,
      limit = 10,
      synonymsEnabled = this.synonymsEnabled,
      minMatchCount = this.minMatchCount
    } = options;

    console.log(`🔍 Searching memory: "${query}"`);

    // 读取索引
    if (!fs.existsSync(this.indexFile)) {
      return { results: [], message: 'No index found' };
    }

    const index = JSON.parse(fs.readFileSync(this.indexFile, 'utf-8'));
    let results = index.entries;

    // 过滤
    if (query) {
      // 1. 扩展关键词（同义词）
      const expandedQuery = synonymsEnabled ? this.expandQuery(query) : [query];
      
      // 2. 多关键词匹配
      results = results.filter(entry => {
        const matchCount = expandedQuery.filter(k =>
          entry.title.toLowerCase().includes(k.toLowerCase()) ||
          entry.summary.toLowerCase().includes(k.toLowerCase()) ||
          entry.keywords.some(kw => kw.toLowerCase().includes(k.toLowerCase()))
        ).length;
        
        return matchCount >= minMatchCount;
      });
      
      // 3. 按匹配度排序（匹配关键词越多，排名越靠前）
      results = results.map(entry => ({
        ...entry,
        matchCount: expandedQuery.filter(k =>
          entry.title.toLowerCase().includes(k.toLowerCase()) ||
          entry.summary.toLowerCase().includes(k.toLowerCase()) ||
          entry.keywords.some(kw => kw.toLowerCase().includes(k.toLowerCase()))
        ).length
      }));
      
      results.sort((a, b) => b.matchCount - a.matchCount);
    }

    if (category) {
      results = results.filter(e => e.category === category);
    }

    if (importance) {
      results = results.filter(e => e.importance === importance);
    }

    if (!includeArchived) {
      results = results.filter(e => !e.archived);
    }

    // 限制数量
    results = results.slice(0, limit);

    console.log(`✅ Found ${results.length} results (expanded from ${query})`);
    return { results, total: results.length };
  }

  /**
   * 扩展查询关键词（同义词）
   * @param {string} query - 原始查询
   * @returns {Array<string>} 扩展后的关键词列表
   */
  expandQuery(query) {
    const expanded = [query];
    const queryLower = query.toLowerCase();
    
    // 查找同义词
    for (const [key, values] of Object.entries(synonyms)) {
      if (queryLower.includes(key.toLowerCase())) {
        expanded.push(...values);
      }
      if (values.some(v => queryLower.includes(v.toLowerCase()))) {
        expanded.push(key);
      }
    }
    
    // 去重
    return [...new Set(expanded)];
  }

  /**
   * 归档记忆
   */
  async archiveMemory(date) {
    const dailyFile = path.join(this.dailyPath, `${date}.md`);
    const monthDir = path.join(this.archivePath, date.substring(0, 7)); // YYYY-MM

    if (!fs.existsSync(dailyFile)) {
      console.log(`⚠️  Daily file not found: ${dailyFile}`);
      return { success: false, message: 'File not found' };
    }

    // 创建月份目录
    if (!fs.existsSync(monthDir)) {
      fs.mkdirSync(monthDir, { recursive: true });
    }

    // 移动文件
    const archiveFile = path.join(monthDir, `${date}.md`);
    fs.renameSync(dailyFile, archiveFile);

    // 更新索引
    await this.markAsArchived(date);

    console.log(`✅ Archived: ${date} → ${monthDir}/`);
    return { success: true, file: archiveFile };
  }

  /**
   * 标记为已归档
   */
  async markAsArchived(date) {
    if (!fs.existsSync(this.indexFile)) return;

    const index = JSON.parse(fs.readFileSync(this.indexFile, 'utf-8'));
    
    index.entries.forEach(entry => {
      if (entry.date === date) {
        entry.archived = true;
      }
    });

    index.stats.archivedMemories = index.entries.filter(e => e.archived).length;
    index.lastUpdated = new Date().toISOString();

    fs.writeFileSync(this.indexFile, JSON.stringify(index, null, 2), 'utf-8');
  }

  /**
   * 获取记忆模板
   */
  getMemoryTemplate() {
    return `# 🦞💰 小钳的长期记忆 | Long-term Memory

> 最后更新：${new Date().toISOString().split('T')[0]}  
> 这是 curated memory —— 从每日记录中提炼的长期知识

---

## 👤 主人信息

**名字：** Amber  
**时区：** Asia/Shanghai (GMT+8)

---

## 💬 重要对话记录

（重要对话的详细内容将记录在这里）

---

## 🦞 小钳的身份

**名字含义：**
- 🦞 OpenClaw 的"钳子"
- 💰 谐音"小钱"

**性格定位：**
- 温和严谨，活泼开朗
- 像朋友一样真诚

---

## 📦 已安装技能清单

（技能列表）

---

## 🖥️ 重要基础设施

（服务器、配置等信息）

---

## 🧠 知识管理策略

（记忆管理规则）

---

## 📚 重要经验总结

（经验教训）

---

## 🎯 当前项目状态

（进行中的项目）

---

## 💡 偏好和习惯

（用户偏好）

---

*此文件由每日记忆整理提炼而成，定期更新保持最新。*
`;
  }
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MemoryManager;
}

// CLI usage
if (require.main === module) {
  const manager = new MemoryManager();
  
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case 'add':
      manager.updateMemory({
        content: args.join(' '),
        type: 'daily',
        title: 'Manual entry'
      });
      break;

    case 'search':
      manager.searchMemory(args.join(' ')).then(result => {
        console.log(JSON.stringify(result, null, 2));
      });
      break;

    case 'archive':
      manager.archiveMemory(args[0]);
      break;

    default:
      console.log('Usage: node memory-manager.js <command> [args]');
      console.log('Commands: add, search, archive');
  }
}
