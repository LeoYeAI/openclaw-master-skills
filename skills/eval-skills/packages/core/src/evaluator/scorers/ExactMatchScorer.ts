import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

/**
 * 从 Skill 输出中提取实际值
 * 支持 { result: "..." } 格式和原始值
 */
function extractValue(output: unknown): unknown {
  if (output !== null && typeof output === "object" && !Array.isArray(output)) {
    const obj = output as Record<string, unknown>;
    if ("result" in obj) return obj.result;
    if ("output" in obj) return obj.output;
    if ("answer" in obj) return obj.answer;
  }
  return output;
}

export interface ExactMatchOptions {
  /** 是否区分大小写，默认 true */
  caseSensitive?: boolean;
}

/**
 * 精确匹配评分器
 *
 * 将 output 和 expected.value 都转为字符串并 trim 后比较。
 */
export class ExactMatchScorer implements Scorer {
  readonly type = "exact_match";
  private readonly caseSensitive: boolean;

  constructor(options?: ExactMatchOptions) {
    this.caseSensitive = options?.caseSensitive ?? true;
  }

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    const actual = String(extractValue(output)).trim();
    const expectedValue = String(expected.value).trim();

    const isMatch = this.caseSensitive
      ? actual === expectedValue
      : actual.toLowerCase() === expectedValue.toLowerCase();

    if (isMatch) {
      return { score: 1.0, passed: true };
    }

    return {
      score: 0.0,
      passed: false,
      reason: `Expected "${expectedValue}" but got "${actual}"`,
    };
  }
}
