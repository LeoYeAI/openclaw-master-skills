import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../../errors.js";
import OpenAI from "openai";
import pLimit from "p-limit";

// Define a type for the limit function if not exported
type LimitFunction = ReturnType<typeof pLimit>;

export interface LlmJudgeOptions {
  /** OpenAI 模型名称，默认 "gpt-4o" */
  model?: string;
  /** OpenAI API base URL，默认 "https://api.openai.com/v1" */
  baseUrl?: string;
  /** 通过阈值 (0-1)，默认 0.5 */
  passThreshold?: number;
  /** Max retries, default 3 */
  maxRetries?: number;
  /** Concurrency limit, default 4. Set to <= 0 to disable (use global shared limit if applicable) */
  concurrency?: number;
  /** System prompt override */
  systemPrompt?: string;
  /** Temperature, default 0 */
  temperature?: number;
}

/**
 * LLM 评分器
 *
 * 使用 OpenAI API 对 output 进行评分。
 * 需要设置 EVAL_SKILLS_LLM_KEY 环境变量。
 */
export class LlmJudgeScorer implements Scorer {
  readonly type = "llm_judge";
  private readonly model: string;
  private readonly baseUrl: string;
  private readonly passThreshold: number;
  private readonly maxRetries: number;
  private readonly limit: LimitFunction;
  private readonly systemPrompt: string;
  private readonly temperature: number;

  constructor(options?: LlmJudgeOptions) {
    this.model = options?.model ?? "gpt-4o";
    this.baseUrl = options?.baseUrl ?? "https://api.openai.com/v1";
    this.passThreshold = options?.passThreshold ?? 0.5;
    this.maxRetries = options?.maxRetries ?? 3;
    this.systemPrompt = options?.systemPrompt ?? "You are an evaluator. Rate the output quality from 0 to 10. Respond with ONLY a number.";
    this.temperature = options?.temperature ?? 0;
    
    const concurrency = options?.concurrency ?? 4;
    this.limit = LlmJudgeScorer.getLimiter(concurrency);
  }

  private static limiters: Map<number, LimitFunction> = new Map();

  private static getLimiter(concurrency: number): LimitFunction {
      if (!this.limiters.has(concurrency)) {
          this.limiters.set(concurrency, pLimit(concurrency));
      }
      return this.limiters.get(concurrency)!;
  }

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    const apiKey = process.env.EVAL_SKILLS_LLM_KEY ?? process.env.OPENAI_API_KEY ?? process.env.OPENAI_KEY;

    if (!apiKey) {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.CONFIG_LLM_MISSING,
        "EVAL_SKILLS_LLM_KEY (or OPENAI_API_KEY) environment variable is not set",
      );
    }

    const openai = new OpenAI({
        apiKey,
        baseURL: this.baseUrl,
        maxRetries: this.maxRetries,
    });

    const judgePrompt = expected.judgePrompt ?? "Evaluate the quality of the output.";
    const outputStr = typeof output === "string" ? output : JSON.stringify(output);
    const expectedStr = expected.value ? (typeof expected.value === "string" ? expected.value : JSON.stringify(expected.value)) : null;

    const userContent = expectedStr
      ? `Judge Criteria: ${judgePrompt}\nReference Answer: ${expectedStr}\nActual Output: ${outputStr}\n\nScore the actual output from 0 to 10 based on the criteria and reference.\nRespond with ONLY a number.`
      : `Judge Criteria: ${judgePrompt}\nActual Output: ${outputStr}\n\nScore the actual output from 0 to 10 based on the criteria.\nRespond with ONLY a number.`;

    try {
        const response = await this.limit(() => openai.chat.completions.create({
            model: this.model,
            temperature: this.temperature,
            messages: [
                {
                    role: "system",
                    content: this.systemPrompt,
                },
                {
                    role: "user",
                    content: userContent,
                },
            ],
        }));

        const content = response.choices[0]?.message?.content?.trim() ?? "";
        const rawScore = parseFloat(content);

        if (isNaN(rawScore)) {
            return {
                score: 0.0,
                passed: false,
                reason: `LLM returned non-numeric response: "${content}"`,
            };
        }

        // Clamp to [0, 10] then normalize to [0, 1]
        const clamped = Math.max(0, Math.min(10, rawScore));
        const normalized = clamped / 10;

        return {
            score: normalized,
            passed: normalized >= this.passThreshold,
            reason: `LLM judge score: ${rawScore}/10 (threshold: ${this.passThreshold})`,
        };
    } catch (err) {
        return {
            score: 0.0,
            passed: false,
            reason: `LLM API request failed: ${(err as Error).message}`,
        };
    }
  }
}
