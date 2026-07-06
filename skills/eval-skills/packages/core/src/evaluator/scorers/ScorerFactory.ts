import type { Scorer } from "./BaseScorer.js";
import { ExactMatchScorer } from "./ExactMatchScorer.js";
import { ContainsScorer } from "./ContainsScorer.js";
import { JsonSchemaScorer } from "./JsonSchemaScorer.js";
import { RegexScorer } from "./RegexScorer.js";
import { LlmJudgeScorer } from "./LlmJudgeScorer.js";
import { CustomScorer } from "./CustomScorer.js";

/**
 * 评分器工厂
 *
 * 按 type 字符串创建对应的 Scorer 实例。
 */
export class ScorerFactory {
  static create(type: string, options?: Record<string, unknown>): Scorer {
    switch (type) {
      case "exact":
      case "exact_match":
        return new ExactMatchScorer({
          caseSensitive: (options?.caseSensitive as boolean) ?? true,
        });

      case "contains":
        return new ContainsScorer({
          caseSensitive: (options?.caseSensitive as boolean) ?? false,
        });

      case "schema":
      case "json_schema":
        return new JsonSchemaScorer();

      case "regex":
        return new RegexScorer();

      case "llm_judge":
        return new LlmJudgeScorer({
          model: (options?.model as string) ?? undefined,
          baseUrl: (options?.baseUrl as string) ?? undefined,
        });

      case "custom":
        return new CustomScorer();

      default:
        throw new Error(`Unknown scorer type: "${type}"`);
    }
  }
}
