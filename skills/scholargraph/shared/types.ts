/**
 * Shared Types - 公共类型定义
 * 用于替代 any 类型，提供类型安全
 */

// Web 搜索结果项类型 (替代 any)
export interface WebSearchResultItem {
  name: string;
  url: string;
  snippet?: string;
  date?: string;
  host_name?: string;
}

// CLI 参数类型
export type SearchSource = 'arxiv' | 'semantic_scholar' | 'web'
  | 'pubmed' | 'crossref' | 'openalex' | 'dblp'
  | 'core' | 'ieee' | 'unpaywall' | 'google_scholar';
export type SortBy = 'relevance' | 'date' | 'citations';
export type LearningDepth = 'beginner' | 'intermediate' | 'advanced';
export type AnalysisMode = 'quick' | 'standard' | 'deep';
export type ReportType = 'daily' | 'weekly' | 'monthly';

// AI 提供商类型
export type AIProviderType = 'zai' | 'openai' | 'anthropic' | 'azure' | 'ollama' | 'qwen' | 'minimax' | 'deepseek' | 'zhipu' | 'baichuan' | 'moonshot' | 'yi' | 'doubao' | 'groq' | 'together';

// 聊天消息类型
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

// 聊天选项
export interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  model?: string;
}

// AI 提供商配置
export interface AIProviderConfig {
  type: AIProviderType;
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  timeout?: number;
}

// 重试选项
export interface RetryOptions {
  maxRetries?: number;
  initialDelayMs?: number;
  maxDelayMs?: number;
  backoffMultiplier?: number;
  retryableErrors?: string[];
}

// JSON 提取结果
export interface JsonExtractionResult<T> {
  success: boolean;
  data?: T;
  error?: string;
  rawMatch?: string;
}

// 验证结果
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  value?: unknown;
}

// 搜索 CLI 参数
export interface SearchCliParams {
  query: string;
  limit: number;
  source?: SearchSource;
  sortBy?: SortBy;
}

// 学习 CLI 参数
export interface LearnCliParams {
  concept: string;
  depth: LearningDepth;
  includePapers: boolean;
  includeCode: boolean;
  outputFile?: string;
}

// 检测 CLI 参数
export interface DetectCliParams {
  domain: string;
  known: string[];
  outputFile?: string;
}

// 追踪 CLI 参数
export interface TrackCliParams {
  action: 'add' | 'report';
  type?: ReportType;
  outputFile?: string;
}

// 分析 CLI 参数
export interface AnalyzeCliParams {
  url: string;
  mode: AnalysisMode;
  outputFile?: string;
}

// 图谱 CLI 参数
export interface GraphCliParams {
  concepts: string[];
  format: 'mermaid' | 'json';
  outputFile?: string;
}

// 解析的 arXiv 条目
export interface ParsedArxivEntry {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  published: string;
  updated?: string;
  categories: string[];
  pdfUrl: string;
}

// 内存管理配置
export interface MemoryConfig {
  maxHistoryEntries: number;
  maxTotalEntries: number;
  maxAgeMs: number;
  cleanupIntervalMs: number;
}

// 论文可视化 CLI 参数
export interface PaperVizCliParams {
  url: string;
  mode: AnalysisMode;
  theme: 'academic-dark' | 'academic-light';
  outputFile?: string;
  ppt: boolean;
  figuresDir?: string;
}

// 交互式图谱 CLI 参数
export interface GraphInteractiveCliParams {
  graphName: string;
  outputFile?: string;
  includePaperViz: boolean;
}
