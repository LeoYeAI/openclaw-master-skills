import type { TaskResult } from "./task.js";

/**
 * 延迟统计
 */
export interface LatencyStats {
  p50Ms: number;
  p95Ms: number;
  p99Ms: number;
}

/**
 * Token 消耗统计
 */
export interface TokenCost {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  estimatedUSD?: number;
}

/**
 * 报告摘要指标
 */
export interface ReportSummary {
  /** 完成率 0.0 ~ 1.0 */
  completionRate: number;
  /** 加权得分 */
  partialScore: number;
  /** 错误率 */
  errorRate: number;
  /** 多次运行稳定性 */
  consistencyScore: number;
  /**
   * 综合评分
   * = 0.5 * completionRate + 0.2 * (1 - latencyP95_normalized) + 0.3 * (1 - errorRate)
   */
  compositeScore: number;
  /**
   * 置信区间 (Bootstrap)
   */
  confidenceInterval?: {
    lower: number;
    upper: number;
    mean: number;
    level: number;
  };
}

/**
 * 单个 Skill 的完整评测报告
 */
export interface SkillCompletionReport {
  skillId: string;
  skillVersion: string;
  benchmarkId: string;
  /** ISO 8601 时间戳 */
  timestamp: string;
  /** 摘要指标 */
  summary: ReportSummary;
  /** 延迟分位数 */
  latency: LatencyStats;
  /** Token 消耗（可选） */
  tokenCost?: TokenCost;
  /** 每个任务的详细结果 */
  taskResults: TaskResult[];
  /** 评测器元数据 */
  evaluatorMetadata: Record<string, unknown>;
}

/**
 * 报告输出格式
 */
export type ReportFormat = "json" | "markdown" | "html" | "csv";
