import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

export interface ContainsOptions {
  /** 是否区分大小写，默认 false */
  caseSensitive?: boolean;
}

/**
 * 关键词包含评分器
 *
 * 检查 expected.keywords 中的每个关键词是否包含在 output 字符串中。
 * score = 匹配关键词数 / 总关键词数（partial scoring）
 * passed = score === 1.0（全部匹配才通过）
 */
export class ContainsScorer implements Scorer {
  readonly type = "contains";
  private readonly caseSensitive: boolean;

  constructor(options?: ContainsOptions) {
    this.caseSensitive = options?.caseSensitive ?? false;
  }

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    const keywords = expected.keywords ?? [];

    if (keywords.length === 0) {
      return {
        score: 1.0,
        passed: true,
        reason: "No keywords to check",
      };
    }

    // 将对象输出转为 JSON 字符串以便搜索
    const rawStr = typeof output === "object" ? JSON.stringify(output) : String(output);
    const outputStr = this.caseSensitive ? rawStr : rawStr.toLowerCase();

    const results = keywords.map((keyword) => {
      const kw = this.caseSensitive ? keyword : keyword.toLowerCase();
      return outputStr.includes(kw);
    });

    const matchedCount = results.filter(Boolean).length;
    const score = matchedCount / keywords.length;
    const passed = score === 1.0;

    if (passed) {
      return { score, passed };
    }

    const missing = keywords.filter((_, i) => !results[i]);
    return {
      score,
      passed,
      reason: `Missing keywords: ${missing.map((k) => `"${k}"`).join(", ")} (${matchedCount}/${keywords.length} matched)`,
    };
  }
}
