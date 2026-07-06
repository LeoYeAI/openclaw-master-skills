import type { ExpectedOutput } from "../../types/index.js";

/**
 * 评分结果
 */
export interface ScorerResult {
  /** 得分 0.0 ~ 1.0 */
  score: number;
  /** 是否通过 */
  passed: boolean;
  /** 评分原因说明 */
  reason?: string;
}

/**
 * 评分器抽象接口
 */
export interface Scorer {
  readonly type: string;
  score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult>;
}
