/**
 * Literature Skills - Configuration
 * 文献检索总结工具配置系统
 */

import type { AIProviderType, SearchSource } from './shared/types';

export interface LiteratureSkillConfig {
  // AI 提供商配置
  ai: {
    provider: AIProviderType;
    apiKey?: string;
    baseUrl?: string;
    model?: string;
    timeout: number;
  };

  // 用户配置
  user: {
    name?: string;
    interests: string[];
    level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    primaryLanguage: 'zh-CN' | 'en-US';
  };

  // 检索配置
  search: {
    defaultSources: SearchSource[];
    maxResults: number;
    sortBy: 'relevance' | 'date' | 'citations';
    cacheResults: boolean;
    cacheDuration: number; // 毫秒
  };

  // 数据源 API 密钥配置
  sourceApiKeys: {
    ncbiApiKey?: string;
    ieeeApiKey?: string;
    coreApiKey?: string;
    unpaywallEmail?: string;
    crossrefMailto?: string;
    serpApiKey?: string;
  };

  // 搜索策略配置
  searchStrategy: {
    defaultPriority: SearchSource[];
    domainPriorities: Record<string, SearchSource[]>;
    maxConcurrentSources: number;
    useComplementaryStrategy: boolean;
  };

  // PDF 下载配置
  pdf: {
    downloadDir: string;
    namingStrategy: 'title' | 'id' | 'doi';
    maxFileSize: number; // bytes
    skipExisting: boolean;
    concurrency: number;
    autoDownload: boolean;
  };

  // 学习配置
  learning: {
    depth: 'quick' | 'standard' | 'deep';
    includePapers: boolean;
    includeCode: boolean;
    focusAreas: string[];
  };

  // 追踪配置
  tracking: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    keywords: string[];
    authors: string[];
    conferences: string[];
    // 内存管理配置
    maxHistoryEntries: number;
    maxTotalEntries: number;
    maxAgeMs: number;
  };

  // 输出配置
  output: {
    format: 'json' | 'markdown' | 'html';
    savePath: string;
    generateReports: boolean;
    reportFrequency: 'daily' | 'weekly' | 'monthly';
  };
}

export const defaultConfig: LiteratureSkillConfig = {
  ai: {
    provider: (process.env.AI_PROVIDER as AIProviderType) || 'zai',
    apiKey: process.env.AI_API_KEY,
    baseUrl: process.env.AI_BASE_URL,
    model: process.env.AI_MODEL,
    timeout: 30000
  },

  user: {
    interests: [],
    level: 'intermediate',
    primaryLanguage: 'zh-CN'
  },

  search: {
    defaultSources: ['arxiv', 'semantic_scholar', 'web'],
    maxResults: 20,
    sortBy: 'relevance',
    cacheResults: true,
    cacheDuration: 3600000 // 1小时
  },

  sourceApiKeys: {
    ncbiApiKey: process.env.NCBI_API_KEY,
    ieeeApiKey: process.env.IEEE_API_KEY,
    coreApiKey: process.env.CORE_API_KEY,
    unpaywallEmail: process.env.UNPAYWALL_EMAIL,
    crossrefMailto: process.env.CROSSREF_MAILTO,
    serpApiKey: process.env.SERPAPI_KEY
  },

  searchStrategy: {
    defaultPriority: [
      'semantic_scholar', 'openalex', 'arxiv', 'pubmed',
      'crossref', 'dblp', 'core', 'ieee', 'web'
    ],
    domainPriorities: {
      biomedical: ['pubmed', 'semantic_scholar', 'openalex', 'crossref'],
      cs: ['semantic_scholar', 'arxiv', 'dblp', 'openalex'],
      engineering: ['ieee', 'semantic_scholar', 'openalex', 'crossref'],
      physics: ['arxiv', 'semantic_scholar', 'openalex'],
      general: ['semantic_scholar', 'openalex', 'crossref', 'arxiv']
    },
    maxConcurrentSources: 4,
    useComplementaryStrategy: true
  },

  pdf: {
    downloadDir: './downloads/pdfs',
    namingStrategy: 'title',
    maxFileSize: 50 * 1024 * 1024, // 50MB
    skipExisting: true,
    concurrency: 3,
    autoDownload: false
  },

  learning: {
    depth: 'standard',
    includePapers: true,
    includeCode: false,
    focusAreas: []
  },

  tracking: {
    enabled: true,
    frequency: 'weekly',
    keywords: [],
    authors: [],
    conferences: [],
    maxHistoryEntries: 100,
    maxTotalEntries: 1000,
    maxAgeMs: 7 * 24 * 60 * 60 * 1000 // 7 days
  },

  output: {
    format: 'markdown',
    savePath: './output',
    generateReports: true,
    reportFrequency: 'weekly'
  }
};

/**
 * 配置管理器
 */
export class ConfigManager {
  private config: LiteratureSkillConfig;
  private configPath: string;

  constructor(configPath: string = './literature-config.json') {
    this.configPath = configPath;
    this.config = { ...defaultConfig };
  }

  /**
   * 加载配置
   */
  load(): LiteratureSkillConfig {
    try {
      const fs = require('fs');
      if (fs.existsSync(this.configPath)) {
        const loaded = JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));
        this.config = { ...defaultConfig, ...loaded };
      }
    } catch (error) {
      console.warn('Failed to load config, using defaults:', error);
    }
    return this.config;
  }

  /**
   * 保存配置
   */
  save(): void {
    try {
      const fs = require('fs');
      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  }

  /**
   * 更新配置
   */
  update(partial: Partial<LiteratureSkillConfig>): void {
    this.config = {
      ...this.config,
      ...partial,
      ai: { ...this.config.ai, ...partial.ai },
      user: { ...this.config.user, ...partial.user },
      search: { ...this.config.search, ...partial.search },
      sourceApiKeys: { ...this.config.sourceApiKeys, ...partial.sourceApiKeys },
      searchStrategy: { ...this.config.searchStrategy, ...partial.searchStrategy },
      pdf: { ...this.config.pdf, ...partial.pdf },
      learning: { ...this.config.learning, ...partial.learning },
      tracking: { ...this.config.tracking, ...partial.tracking },
      output: { ...this.config.output, ...partial.output }
    };
    this.save();
  }

  /**
   * 获取当前配置
   */
  get(): LiteratureSkillConfig {
    return this.config;
  }

  /**
   * 重置为默认配置
   */
  reset(): void {
    this.config = { ...defaultConfig };
    this.save();
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const command = args[0];

  const manager = new ConfigManager();

  switch (command) {
    case 'init':
      manager.save();
      console.log('Configuration initialized at ./literature-config.json');
      break;

    case 'show':
      const config = manager.load();
      console.log(JSON.stringify(config, null, 2));
      break;

    case 'set':
      const key = args[1];
      const value = args[2];
      if (key && value) {
        try {
          const parsed = JSON.parse(value);
          manager.update({ [key]: parsed });
          console.log(`Set ${key} = ${value}`);
        } catch {
          manager.update({ [key]: value });
          console.log(`Set ${key} = "${value}"`);
        }
      }
      break;

    case 'reset':
      manager.reset();
      console.log('Configuration reset to defaults');
      break;

    default:
      console.log(`
Usage:
  config.ts init              - Initialize configuration file
  config.ts show              - Show current configuration
  config.ts set <key> <value> - Set configuration value
  config.ts reset             - Reset to defaults

Environment Variables:
  AI_PROVIDER     - AI provider: zai | openai | anthropic | azure | ollama | qwen (default: zai)
  AI_API_KEY      - API key for the selected provider
  AI_BASE_URL     - Custom API base URL (optional)
  AI_MODEL        - Model name (optional)

  OPENAI_API_KEY       - OpenAI API key
  ANTHROPIC_API_KEY    - Anthropic API key
  AZURE_OPENAI_ENDPOINT - Azure OpenAI endpoint
  AZURE_OPENAI_API_KEY  - Azure OpenAI API key
  OLLAMA_BASE_URL      - Ollama server URL (default: http://localhost:11434)

  QWEN_API_KEY         - Qwen (通义千问) API key
  DASHSCOPE_API_KEY    - Alias for QWEN_API_KEY
  QWEN_BASE_URL        - Qwen API base URL (default: https://dashscope.aliyuncs.com/compatible-mode/v1)
  QWEN_MODEL           - Qwen model name (default: qwen-plus)

  SERPER_API_KEY       - Serper API key for web search (optional)
`);
  }
}
