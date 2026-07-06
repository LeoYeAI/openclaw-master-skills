import type { JSONSchema } from "./common.js";

/**
 * 评分器配置
 */
export interface EvaluatorConfig {
  type: "exact" | "contains" | "schema" | "llm_judge" | "regex" | "custom";
  caseSensitive?: boolean;
  customScorerPath?: string;
}

/**
 * 预期输出定义
 */
export interface ExpectedOutput {
  /** 匹配类型 */
  type: "exact" | "contains" | "schema" | "llm_judge" | "regex" | "custom";
  /** 精确匹配值 */
  value?: unknown;
  /** JSON Schema（type=schema 时使用） */
  schema?: JSONSchema;
  /** 关键词列表（type=contains 时使用） */
  keywords?: string[];
  /** 正则表达式列表（type=regex 时使用） */
  patterns?: string[];
  /** LLM Judge 提示词（type=llm_judge 时使用） */
  judgePrompt?: string;
  /** 自定义评分器路径（type=custom 时使用） */
  customScorerPath?: string;
}

/**
 * 单个评测任务
 */
export interface Task {
  /** 任务唯一 ID */
  id: string;
  /** 任务描述 */
  description: string;
  /** 输入数据 */
  inputData: Record<string, unknown>;
  /** 预期输出 */
  expectedOutput: ExpectedOutput;
  /** 评分器配置 */
  evaluator: EvaluatorConfig;
  /** 单任务超时（毫秒），默认 30000 */
  timeoutMs?: number;
  /** 任务标签 */
  tags?: string[];
  /** 任务权重，默认 1.0 */
  weight?: number;
}

/**
 * 任务执行结果状态
 */
export type TaskStatus = "pass" | "fail" | "error" | "timeout";

/**
 * 单个任务的评测结果
 */
export interface TaskResult {
  /** 任务 ID */
  taskId: string;
  /** Skill ID */
  skillId: string;
  /** 执行状态 */
  status: TaskStatus;
  /** 得分 0.0 ~ 1.0 */
  score: number;
  /** 响应延迟（毫秒） */
  latencyMs: number;
  /** Skill 实际输出 */
  output?: unknown;
  /** 错误信息 */
  error?: string;
  /** 使用的评分器类型 */
  scorerType: string;
  /** 评分原因说明 */
  reason?: string;
  /** 执行轮次 ID (用于 consistencyScore 计算) */
  runId?: number;
  /** Token usage */
  usage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
  };
  /** 任务权重 */
  weight?: number;
}
