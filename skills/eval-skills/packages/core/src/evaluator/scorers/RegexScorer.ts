import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

/**
 * 正则表达式评分器
 *
 * 验证输出是否匹配指定的正则表达式列表。
 */
export class RegexScorer implements Scorer {
  readonly type = "regex";

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    const patterns = expected.patterns;

    if (!patterns || patterns.length === 0) {
      return {
        score: 0.0,
        passed: false,
        reason: "No regex patterns provided in expected output",
      };
    }

    const outputStr = typeof output === "string" ? output : JSON.stringify(output);
    const matchedCount = patterns.reduce((count, pattern) => {
      try {
        const regex = new RegExp(pattern);
        return count + (regex.test(outputStr) ? 1 : 0);
      } catch (err) {
        // Invalid regex pattern, treat as no match
        return count;
      }
    }, 0);

    const score = matchedCount / patterns.length;
    const passed = score === 1.0; // All patterns must match for pass? Or should it be configurable? 
    // Usually regex matching implies all required patterns are present.
    // Let's assume strict matching for now (all must match).
    
    return {
      score,
      passed,
      reason: passed 
        ? "All regex patterns matched" 
        : `Matched ${matchedCount}/${patterns.length} patterns`,
    };
  }
}
