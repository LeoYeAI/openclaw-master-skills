import type { ReportFormat } from "./report.js";

/**
 * 评测运行配置
 */
export interface EvalRunConfig {
  /** Skill 路径列表（文件或目录） */
  skillPaths: string[];
  /** Benchmark ID 或本地路径 */
  benchmark: string;
  /** 自定义任务文件路径（替代 benchmark） */
  tasksFile?: string;
  /** 并发数，默认 4 */
  concurrency: number;
  /** 单任务超时（毫秒），默认 30000 */
  timeoutMs: number;
  /** 失败重试次数，默认 0 */
  retries: number;
  /** 评分器类型 */
  evaluator: string;
  /** LLM Judge 配置 */
  llmJudge?: {
    model: string;
    temperature: number;
    apiKey?: string;
  };
  /** 输出配置 */
  output: {
    dir: string;
    formats: ReportFormat[];
  };
  /** 失败退出配置 */
  exitOnFail?: {
    enabled: boolean;
    minCompletionRate: number;
  };
  /** 是否从上次中断位置继续 */
  resume?: boolean;
  /** 是否只验证配置不实际执行 */
  dryRun?: boolean;
  /** 执行轮次 (用于 consistencyScore 计算)，默认 1 */
  runs?: number;
}

/**
 * 全局配置
 */
export interface GlobalConfig {
  /** 默认并发数 */
  concurrency: number;
  /** 默认超时 */
  timeoutMs: number;
  /** LLM 配置 */
  llm?: {
    model: string;
    temperature: number;
  };
  /** 报告输出目录 */
  outputDir: string;
  /** 默认报告格式 */
  defaultFormats: ReportFormat[];
}

/**
 * 默认全局配置
 */
export const DEFAULT_GLOBAL_CONFIG: GlobalConfig = {
  concurrency: 4,
  timeoutMs: 30000,
  outputDir: "./reports",
  defaultFormats: ["json", "markdown"],
};
