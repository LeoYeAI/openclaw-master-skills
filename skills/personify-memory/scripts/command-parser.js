#!/usr/bin/env node

/**
 * Personify Memory - Command Parser
 * 
 * 识别用户"记住"指令，解析内容和目标位置
 */

class CommandParser {
  constructor() {
    // 记忆指令模式
    this.memoryCommands = [
      // "记住 XXX"（支持中文逗号、英文逗号、空格或无分隔符）
      {
        pattern: /记住.*?([^\s,，].+)/i,
        extract: (match) => ({ content: match[1], target: null })
      },
      // "把 XXX 记下来"
      {
        pattern: /把 (.+?) 记 (下来 | 起来 | 住)/i,
        extract: (match) => ({ content: match[1], target: null })
      },
      // "不要忘记 XXX"
      {
        pattern: /不要忘记.*?([^\s,，].+)/i,
        extract: (match) => ({ content: match[1], target: null, importance: 'high' })
      },
      // "这个很重要，记住"
      {
        pattern: /这个很 (重要 | 关键| 有意义) [\s,，]*记住/i,
        extract: (match) => ({ content: '上一段话', target: null, importance: 'high' })
      },
      // "记到 XXX 里"
      {
        pattern: /记到 (.+?) 里/i,
        extract: (match) => ({ content: null, target: match[1] })
      },
      // "记入核心记忆/情感记忆/知识库"
      {
        pattern: /记入 [\s,，]*(核心记忆 | 情感记忆 | 知识库 | 每日记忆)/i,
        extract: (match) => ({ content: null, target: match[1] })
      },
      // "添加到记忆里"
      {
        pattern: /添加 (到 | 进) 记忆 (里 | 中)/i,
        extract: (match) => ({ content: '上一段话', target: null })
      }
    ];

    // 目标位置映射
    this.targetMap = {
      '核心记忆': 'core',
      'MEMORY.md': 'core',
      '情感记忆': 'emotion',
      'emotion-memory.json': 'emotion',
      '知识库': 'knowledge',
      'knowledge-base.md': 'knowledge',
      '每日记忆': 'daily',
      'daily': 'daily'
    };
  }

  /**
   * 解析用户消息，识别记忆指令
   * @param {string} message - 用户消息
   * @returns {Object|null} 解析结果，如果不是记忆指令返回 null
   */
  parse(message) {
    if (!message || typeof message !== 'string') {
      return null;
    }

    const trimmedMessage = message.trim();

    // 尝试匹配每个模式
    for (const cmd of this.memoryCommands) {
      const match = trimmedMessage.match(cmd.pattern);
      if (match) {
        const extracted = cmd.extract(match);
        return {
          isMemoryCommand: true,
          content: extracted.content,
          target: this.resolveTarget(extracted.target),
          importance: extracted.importance || 'medium',
          originalMessage: trimmedMessage
        };
      }
    }

    return null;
  }

  /**
   * 解析目标位置
   */
  resolveTarget(target) {
    if (!target) {
      return null;
    }

    const normalized = target.trim();
    return this.targetMap[normalized] || 'daily';
  }

  /**
   * 判断消息是否包含记忆指令
   */
  isMemoryCommand(message) {
    return this.parse(message) !== null;
  }

  /**
   * 从上下文中提取要记忆的内容
   * @param {Object} parsedCommand - 解析后的命令
   * @param {Array} conversationContext - 对话上下文
   * @returns {string} 提取的内容
   */
  extractContentFromContext(parsedCommand, conversationContext = []) {
    if (parsedCommand.content && parsedCommand.content !== '上一段话') {
      return parsedCommand.content;
    }

    // 如果是"上一段话"，从上下文中获取
    if (conversationContext.length > 0) {
      const lastUserMessage = conversationContext.slice().reverse().find(
        msg => msg.role === 'user'
      );
      if (lastUserMessage) {
        return lastUserMessage.content;
      }
    }

    return '未指定内容';
  }

  /**
   * 根据内容自动判断记忆类型
   * @param {string} content - 记忆内容
   * @returns {string} 建议的记忆类型
   */
  suggestMemoryType(content) {
    if (!content) return 'daily';

    const lowerContent = content.toLowerCase();

    // 优先级 1：基础设施/重要项目（最高优先级）
    const infrastructureKeywords = ['到期', '服务器', '域名', '续费', '配置', '部署', '上线', '迁移', '搬家'];
    if (infrastructureKeywords.some(k => lowerContent.includes(k))) {
      return 'core';  // 重要基础设施
    }

    // 优先级 2：家庭信息
    const familyKeywords = ['家人', '宝宝', '孩子', '宠物', '老公', '老婆', '名字', '一一', '卷卷', 'Amber', 'Grace'];
    if (familyKeywords.some(k => lowerContent.includes(k))) {
      return 'core';
    }

    // 优先级 3：情感相关
    const emotionKeywords = ['喜欢', '不喜欢', '习惯', '偏好', '温暖', '感动', '开心', '难过'];
    if (emotionKeywords.some(k => lowerContent.includes(k))) {
      return 'emotion';
    }

    // 优先级 4：经验教训
    const knowledgeKeywords = ['经验', '教训', '注意', '方法', '技巧', '方案', '解决', '问题', 'Bug', '错误'];
    if (knowledgeKeywords.some(k => lowerContent.includes(k))) {
      return 'knowledge';
    }

    // 优先级 5：哲理/价值观
    const philosophyKeywords = ['意义', '活着', '成长', '学习', '人生', '价值', '哲学', '道理'];
    if (philosophyKeywords.some(k => lowerContent.includes(k))) {
      return 'core';
    }

    // 默认每日记忆
    return 'daily';
  }

  /**
   * 生成确认提示
   * @param {Object} parsedCommand - 解析后的命令
   * @param {string} suggestedType - 建议的记忆类型
   * @returns {string} 确认提示语
   */
  generateConfirmPrompt(parsedCommand, suggestedType) {
    const typeNames = {
      'core': '核心记忆 (MEMORY.md)',
      'emotion': '情感记忆 (emotion-memory.json)',
      'knowledge': '知识库 (knowledge-base.md)',
      'daily': '每日记忆'
    };

    const target = parsedCommand.target || suggestedType;
    const targetName = typeNames[target] || typeNames['daily'];

    if (parsedCommand.target) {
      return `好的，已记入 ${targetName} ✅`;
    } else {
      return `好的，这段话我想记到 ${targetName} 里，可以吗？`;
    }
  }
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CommandParser;
}

// CLI usage
if (require.main === module) {
  const parser = new CommandParser();
  
  const message = process.argv.slice(2).join(' ');
  
  if (!message) {
    console.log('Usage: node command-parser.js <message>');
    console.log('Example: node command-parser.js "记住我喜欢喝拿铁"');
    process.exit(1);
  }

  const result = parser.parse(message);
  
  if (result) {
    console.log('✅ 识别到记忆指令:');
    console.log(JSON.stringify(result, null, 2));
    
    const suggestedType = parser.suggestMemoryType(result.content);
    console.log(`\n💡 建议记忆类型：${suggestedType}`);
    console.log(`📝 确认提示：${parser.generateConfirmPrompt(result, suggestedType)}`);
  } else {
    console.log('❌ 未识别到记忆指令');
  }
}
