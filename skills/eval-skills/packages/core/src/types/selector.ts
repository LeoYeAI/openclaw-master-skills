import type { AdapterType } from "./skill.js";

/**
 * Skill 筛选策略
 */
export interface SelectStrategy {
  /** 强过滤条件 */
  filters: {
    /** 最低完成率，默认 0.7 */
    minCompletionRate?: number;
    /** 最高错误率，默认 0.1 */
    maxErrorRate?: number;
    /** 最大 P95 延迟（毫秒） */
    maxLatencyP95Ms?: number;
    /** 允许的 Adapter 类型 */
    adapterTypes?: AdapterType[];
    /** 必须包含的标签 */
    requiredTags?: string[];
  };
  /** 排序依据 */
  sortBy: "completionRate" | "compositeScore" | "latency" | "tokenCost";
  /** 排序方向 */
  order: "desc" | "asc";
  /** 返回前 K 个，0 = 不限制 */
  topK?: number;
}
