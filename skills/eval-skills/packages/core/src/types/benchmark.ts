import type { Task } from "./task.js";

/**
 * 评分方式
 */
export type ScoringMethod = "mean" | "weighted_mean" | "pass_at_k";

/**
 * Benchmark 领域
 */
export type BenchmarkDomain = "general" | "coding" | "web" | "reasoning" | "tool-use";

/**
 * Benchmark — 标准化评测任务集
 */
export interface Benchmark {
  /** Benchmark 唯一 ID，如 "gaia-v1" */
  id: string;
  /** 人类可读名称 */
  name: string;
  /** 版本号 */
  version: string;
  /** 领域分类 */
  domain: BenchmarkDomain;
  /** 评测任务列表 */
  tasks: Task[];
  /** 评分方式 */
  scoringMethod: ScoringMethod;
  /** 最大允许延迟（用于延迟归一化），默认 30000ms */
  maxLatencyMs?: number;
  /** 元数据 */
  metadata: {
    source?: string;
    paper?: string;
    lastUpdated?: string;
  };
}

/**
 * Benchmark 列表元信息（不含 tasks 详情）
 */
export interface BenchmarkMeta {
  id: string;
  name: string;
  version: string;
  domain: BenchmarkDomain;
  taskCount: number;
  scoringMethod: ScoringMethod;
}
