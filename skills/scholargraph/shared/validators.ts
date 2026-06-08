/**
 * Shared Validators - 输入验证函数
 * 提供 CLI 参数和数据验证
 */

import type {
  ValidationResult,
  ValidationError,
  SearchSource,
  SortBy,
  LearningDepth,
  AnalysisMode,
  ReportType,
  SearchCliParams
} from './types';

// 有效值常量
const VALID_PAPER_VIZ_THEMES = ['academic-dark', 'academic-light'] as const;
const VALID_SEARCH_SOURCES: SearchSource[] = [
  'arxiv', 'semantic_scholar', 'web',
  'pubmed', 'crossref', 'openalex', 'dblp',
  'core', 'ieee', 'unpaywall', 'google_scholar'
];
const VALID_SORT_BY: SortBy[] = ['relevance', 'date', 'citations'];
const VALID_LEARNING_DEPTHS: LearningDepth[] = ['beginner', 'intermediate', 'advanced'];
const VALID_ANALYSIS_MODES: AnalysisMode[] = ['quick', 'standard', 'deep'];
const VALID_REPORT_TYPES: ReportType[] = ['daily', 'weekly', 'monthly'];

/**
 * 创建验证结果
 */
function createResult(errors: ValidationError[] = []): ValidationResult {
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * 创建验证错误
 */
function createError(field: string, message: string, value?: unknown): ValidationError {
  return { field, message, value };
}

/**
 * 验证数值范围
 */
export function validateNumberRange(
  value: number,
  min: number,
  max: number,
  fieldName: string
): ValidationResult {
  const errors: ValidationError[] = [];

  if (typeof value !== 'number' || isNaN(value)) {
    errors.push(createError(fieldName, `${fieldName} must be a valid number`, value));
  } else if (value < min) {
    errors.push(createError(fieldName, `${fieldName} must be at least ${min}`, value));
  } else if (value > max) {
    errors.push(createError(fieldName, `${fieldName} must be at most ${max}`, value));
  }

  return createResult(errors);
}

/**
 * 验证搜索源
 */
export function validateSearchSource(value: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!VALID_SEARCH_SOURCES.includes(value as SearchSource)) {
    errors.push(createError(
      'source',
      `Invalid source. Must be one of: ${VALID_SEARCH_SOURCES.join(', ')}`,
      value
    ));
  }

  return createResult(errors);
}

/**
 * 验证排序方式
 */
export function validateSortBy(value: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!VALID_SORT_BY.includes(value as SortBy)) {
    errors.push(createError(
      'sortBy',
      `Invalid sortBy. Must be one of: ${VALID_SORT_BY.join(', ')}`,
      value
    ));
  }

  return createResult(errors);
}

/**
 * 验证学习深度
 */
export function validateLearningDepth(value: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!VALID_LEARNING_DEPTHS.includes(value as LearningDepth)) {
    errors.push(createError(
      'depth',
      `Invalid depth. Must be one of: ${VALID_LEARNING_DEPTHS.join(', ')}`,
      value
    ));
  }

  return createResult(errors);
}

/**
 * 验证分析模式
 */
export function validateAnalysisMode(value: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!VALID_ANALYSIS_MODES.includes(value as AnalysisMode)) {
    errors.push(createError(
      'mode',
      `Invalid mode. Must be one of: ${VALID_ANALYSIS_MODES.join(', ')}`,
      value
    ));
  }

  return createResult(errors);
}

/**
 * 验证报告类型
 */
export function validateReportType(value: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!VALID_REPORT_TYPES.includes(value as ReportType)) {
    errors.push(createError(
      'type',
      `Invalid type. Must be one of: ${VALID_REPORT_TYPES.join(', ')}`,
      value
    ));
  }

  return createResult(errors);
}

/**
 * 验证非空字符串
 */
export function validateNonEmptyString(value: string, fieldName: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (typeof value !== 'string' || value.trim().length === 0) {
    errors.push(createError(fieldName, `${fieldName} is required and cannot be empty`, value));
  }

  return createResult(errors);
}

/**
 * 验证 URL
 */
export function validateUrl(value: string, fieldName: string = 'url'): ValidationResult {
  const errors: ValidationError[] = [];

  try {
    new URL(value);
  } catch {
    errors.push(createError(fieldName, `${fieldName} must be a valid URL`, value));
  }

  return createResult(errors);
}

/**
 * 验证搜索参数
 */
export function validateSearchParams(params: Partial<SearchCliParams>): ValidationResult {
  const errors: ValidationError[] = [];

  // 验证查询
  if (!params.query || params.query.trim().length === 0) {
    errors.push(createError('query', 'Search query is required'));
  }

  // 验证限制数量
  if (params.limit !== undefined) {
    const limitResult = validateNumberRange(params.limit, 1, 100, 'limit');
    errors.push(...limitResult.errors);
  }

  // 验证搜索源
  if (params.source !== undefined) {
    const sourceResult = validateSearchSource(params.source);
    errors.push(...sourceResult.errors);
  }

  // 验证排序方式
  if (params.sortBy !== undefined) {
    const sortResult = validateSortBy(params.sortBy);
    errors.push(...sortResult.errors);
  }

  return createResult(errors);
}

/**
 * 验证学习参数
 */
export function validateLearnParams(params: {
  concept?: string;
  depth?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  // 验证概念
  if (!params.concept || params.concept.trim().length === 0) {
    errors.push(createError('concept', 'Concept is required'));
  }

  // 验证深度
  if (params.depth !== undefined) {
    const depthResult = validateLearningDepth(params.depth);
    errors.push(...depthResult.errors);
  }

  return createResult(errors);
}

/**
 * 验证检测参数
 */
export function validateDetectParams(params: {
  domain?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  // 验证领域
  if (!params.domain || params.domain.trim().length === 0) {
    errors.push(createError('domain', 'Domain is required'));
  }

  return createResult(errors);
}

/**
 * 验证分析参数
 */
export function validateAnalyzeParams(params: {
  url?: string;
  mode?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  // 验证 URL
  if (!params.url) {
    errors.push(createError('url', 'Paper URL is required'));
  } else {
    const urlResult = validateUrl(params.url);
    errors.push(...urlResult.errors);
  }

  // 验证模式
  if (params.mode !== undefined) {
    const modeResult = validateAnalysisMode(params.mode);
    errors.push(...modeResult.errors);
  }

  return createResult(errors);
}

/**
 * 验证图谱参数
 */
export function validateGraphParams(params: {
  concepts?: string[];
}): ValidationResult {
  const errors: ValidationError[] = [];

  // 验证概念列表
  if (!params.concepts || params.concepts.length < 2) {
    errors.push(createError('concepts', 'At least 2 concepts are required'));
  }

  return createResult(errors);
}

/**
 * 格式化验证错误为可读字符串
 */
export function formatValidationErrors(errors: ValidationError[]): string {
  if (errors.length === 0) {
    return '';
  }

  return errors
    .map(e => `  - ${e.field}: ${e.message}${e.value !== undefined ? ` (got: ${JSON.stringify(e.value)})` : ''}`)
    .join('\n');
}

/**
 * 合并多个验证结果
 */
export function mergeValidationResults(...results: ValidationResult[]): ValidationResult {
  const allErrors: ValidationError[] = [];

  for (const result of results) {
    allErrors.push(...result.errors);
  }

  return createResult(allErrors);
}

/**
 * 类型守卫：检查是否为有效的搜索源
 */
export function isValidSearchSource(value: unknown): value is SearchSource {
  return typeof value === 'string' && VALID_SEARCH_SOURCES.includes(value as SearchSource);
}

/**
 * 类型守卫：检查是否为有效的排序方式
 */
export function isValidSortBy(value: unknown): value is SortBy {
  return typeof value === 'string' && VALID_SORT_BY.includes(value as SortBy);
}

/**
 * 类型守卫：检查是否为有效的学习深度
 */
export function isValidLearningDepth(value: unknown): value is LearningDepth {
  return typeof value === 'string' && VALID_LEARNING_DEPTHS.includes(value as LearningDepth);
}

/**
 * 类型守卫：检查是否为有效的分析模式
 */
export function isValidAnalysisMode(value: unknown): value is AnalysisMode {
  return typeof value === 'string' && VALID_ANALYSIS_MODES.includes(value as AnalysisMode);
}

/**
 * 类型守卫：检查是否为有效的报告类型
 */
export function isValidReportType(value: unknown): value is ReportType {
  return typeof value === 'string' && VALID_REPORT_TYPES.includes(value as ReportType);
}

/**
 * 验证 PDF 下载参数
 */
export function validatePdfDownloadParams(params: {
  query?: string;
  limit?: number;
  outputDir?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  if (!params.query || params.query.trim().length === 0) {
    errors.push(createError('query', 'Search query is required for PDF download'));
  }

  if (params.limit !== undefined) {
    const limitResult = validateNumberRange(params.limit, 1, 50, 'limit');
    errors.push(...limitResult.errors);
  }

  return createResult(errors);
}

/**
 * 验证论文可视化参数
 */
export function validatePaperVizParams(params: {
  url?: string;
  mode?: string;
  theme?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  if (!params.url) {
    errors.push(createError('url', 'Paper URL is required'));
  } else {
    const urlResult = validateUrl(params.url);
    errors.push(...urlResult.errors);
  }

  if (params.mode !== undefined) {
    const modeResult = validateAnalysisMode(params.mode);
    errors.push(...modeResult.errors);
  }

  if (params.theme !== undefined && !VALID_PAPER_VIZ_THEMES.includes(params.theme as typeof VALID_PAPER_VIZ_THEMES[number])) {
    errors.push(createError('theme', `Invalid theme. Must be one of: ${VALID_PAPER_VIZ_THEMES.join(', ')}`, params.theme));
  }

  return createResult(errors);
}

/**
 * 验证交互式图谱参数
 */
export function validateGraphInteractiveParams(params: {
  graphName?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  if (!params.graphName || params.graphName.trim().length === 0) {
    errors.push(createError('graphName', 'Graph name is required'));
  }

  return createResult(errors);
}
