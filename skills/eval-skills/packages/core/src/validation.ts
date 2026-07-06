import { z } from "zod";

/**
 * Skill 元数据的运行时 Zod Schema
 * 用于在注册/加载时校验 skill.json 的合法性
 */
export const SkillSchema = z.object({
  id: z
    .string()
    .min(1, "Skill id must not be empty")
    .regex(/^[a-z0-9_-]+$/, "Skill id must be lowercase alphanumeric with _ or -"),
  name: z.string().min(1, "Skill name must not be empty"),
  version: z
    .string()
    .regex(/^\d+\.\d+\.\d+$/, "Skill version must follow semver (e.g., 1.0.0)"),
  description: z.string(),
  tags: z.array(z.string()).default([]),
  inputSchema: z.record(z.unknown()).default({}),
  outputSchema: z.record(z.unknown()).default({}),
  adapterType: z.enum(["http", "subprocess", "mcp"]),
  entrypoint: z.string().min(1, "Skill entrypoint must not be empty"),
  metadata: z
    .object({
      author: z.string().optional(),
      license: z.string().optional(),
      homepage: z.string().optional(),
      benchmarkResults: z
        .array(
          z.object({
            benchmarkId: z.string(),
            completionRate: z.number(),
            compositeScore: z.number(),
            timestamp: z.string(),
          }),
        )
        .optional(),
    })
    .default({}),
});

/**
 * Benchmark 的运行时 Zod Schema
 */
export const BenchmarkSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  version: z.string(),
  domain: z.string(),
  scoringMethod: z.enum(["mean", "weighted_mean", "pass_at_k"]),
  maxLatencyMs: z.number().positive().optional(),
  metadata: z
    .object({
      source: z.string().optional(),
      paper: z.string().optional(),
      lastUpdated: z.string().optional(),
    })
    .default({}),
  tasks: z.array(
    z.object({
      id: z.string().min(1),
      description: z.string(),
      inputData: z.record(z.unknown()),
      expectedOutput: z.object({
        type: z.enum(["exact", "contains", "schema", "llm_judge", "regex", "custom"]),
        value: z.unknown().optional(),
        schema: z.record(z.unknown()).optional(),
        keywords: z.array(z.string()).optional(),
        patterns: z.array(z.string()).optional(),
        judgePrompt: z.string().optional(),
        customScorerPath: z.string().optional(),
      }),
      evaluator: z.object({
        type: z.enum(["exact", "contains", "schema", "llm_judge", "regex", "custom"]),
        caseSensitive: z.boolean().optional(),
        customScorerPath: z.string().optional(),
      }),
      timeoutMs: z.number().positive().optional(),
      tags: z.array(z.string()).optional(),
    }),
  ),
});

/**
 * 校验 Skill 数据，返回标准化后的对象或抛出异常
 */
export function validateSkill(data: unknown) {
  return SkillSchema.parse(data);
}

/**
 * 校验 Benchmark 数据，返回标准化后的对象或抛出异常
 */
export function validateBenchmark(data: unknown) {
  return BenchmarkSchema.parse(data);
}
