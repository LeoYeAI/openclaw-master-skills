import { z } from "zod";
import { EvmAddress, PaymentModel, SafeTaskDescription, USDCRate, validateInput } from "../security/input-gate.js";
import { safe_hire_agent, type HireResult } from "./hire.js";
import { toError } from "../utils/errors.js";

const BatchHireItemSchema = z.object({
  target_id: EvmAddress,
  task_description: SafeTaskDescription,
  payment_model: PaymentModel,
  rate: USDCRate,
  idempotency_key: z
    .string()
    .min(8)
    .max(128)
    .regex(/^[a-zA-Z0-9:_-]+$/)
    .optional(),
  confirmed: z.boolean().optional().default(false),
});

const BatchHireSchema = z.object({
  hires: z.array(BatchHireItemSchema).min(1).max(50),
  failure_policy: z.enum(["continue", "halt"]).default("continue"),
  max_concurrency: z.number().int().min(1).max(10).default(3),
  batch_idempotency_key: z
    .string()
    .min(8)
    .max(128)
    .regex(/^[a-zA-Z0-9:_-]+$/)
    .optional(),
});

export type BatchHireInput = z.infer<typeof BatchHireSchema>;

export interface BatchHireResult {
  status: "completed" | "partial" | "failed";
  total: number;
  succeeded: number;
  failed: number;
  skipped: number;
  results: Array<{
    index: number;
    ok: boolean;
    data?: HireResult;
    error?: string;
    skipped?: boolean;
  }>;
}

interface BatchDeps {
  hireAgent?: (input: unknown) => Promise<HireResult>;
}

export async function safe_hire_agents_batch(
  rawInput: unknown,
  deps: BatchDeps = {}
): Promise<BatchHireResult> {
  const input = validateInput(BatchHireSchema, rawInput);
  const hireAgent = deps.hireAgent ?? safe_hire_agent;
  const results: BatchHireResult["results"] = Array.from(
    { length: input.hires.length },
    (_, i) => ({
      index: i,
      ok: false,
      skipped: true,
    })
  );

  let cursor = 0;
  let stop = false;

  async function worker(): Promise<void> {
    while (true) {
      if (stop) return;
      const idx = cursor;
      cursor += 1;
      if (idx >= input.hires.length) return;

      const item = input.hires[idx]!;
      const derivedKey =
        item.idempotency_key ??
        (input.batch_idempotency_key
          ? `${input.batch_idempotency_key}:${idx}`
          : undefined);

      try {
        const data = await hireAgent({
          ...item,
          ...(derivedKey ? { idempotency_key: derivedKey } : {}),
        });
        results[idx] = { index: idx, ok: true, data, skipped: false };
      } catch (err) {
        results[idx] = {
          index: idx,
          ok: false,
          error: toError(err).message,
          skipped: false,
        };
        if (input.failure_policy === "halt") {
          stop = true;
          return;
        }
      }
    }
  }

  const workerCount = input.max_concurrency ?? 3;
  const workers = Array.from({ length: workerCount }, () => worker());
  await Promise.all(workers);

  const succeeded = results.filter((r) => r.ok).length;
  const failed = results.filter((r) => !!r.error).length;
  const skipped = results.length - succeeded - failed;

  return {
    status: failed === 0 ? "completed" : succeeded === 0 ? "failed" : "partial",
    total: results.length,
    succeeded,
    failed,
    skipped,
    results,
  };
}
