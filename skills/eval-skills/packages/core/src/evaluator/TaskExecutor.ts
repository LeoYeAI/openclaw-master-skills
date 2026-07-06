import { EventEmitter } from "node:events";
import pLimit from "p-limit";
import type { Skill, Task, TaskResult, TaskStatus } from "../types/index.js";
import type { SkillAdapter } from "../types/index.js";
import type { Scorer } from "./scorers/BaseScorer.js";
import { withSpan } from "../telemetry/OTelTracer.js";

/**
 * TaskExecutor 配置选项
 */
export interface TaskExecutorOptions {
  /** 并发数，默认 4 */
  concurrency: number;
  /** 单任务超时（毫秒），默认 30000 */
  timeoutMs: number;
  /** 失败重试次数，默认 0 */
  retries: number;
}

/**
 * 单个执行项：Skill × Task
 */
export interface TaskItem {
  skill: Skill;
  task: Task;
  runId?: number;
  usage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
  };
}

/**
 * 并发任务执行器
 * 使用 p-limit 控制并发，支持超时和重试
 */
export class TaskExecutor extends EventEmitter {
  private options: TaskExecutorOptions;

  constructor(options: Partial<TaskExecutorOptions> = {}) {
    super();
    this.options = {
      concurrency: options.concurrency ?? 4,
      timeoutMs: options.timeoutMs ?? 30000,
      retries: options.retries ?? 0,
    };
  }

  /**
   * 并发执行所有任务
   */
  async execute(
    items: TaskItem[],
    adapterResolver: (skill: Skill) => SkillAdapter,
    scorerResolver: (task: Task) => Scorer,
  ): Promise<TaskResult[]> {
    const limit = pLimit(this.options.concurrency);
    let completed = 0;
    const total = items.length;

    const promises = items.map((item) =>
      limit(async () => {
        const result = await this.executeOne(item, adapterResolver, scorerResolver);
        completed++;
        this.emit("progress", {
          completed,
          total,
          percent: Math.round((completed / total) * 100),
        });
        return result;
      }),
    );

    return Promise.all(promises);
  }

  /**
   * 执行单个任务
   */
  private async executeOne(
    item: TaskItem,
    adapterResolver: (skill: Skill) => SkillAdapter,
    scorerResolver: (task: Task) => Scorer,
  ): Promise<TaskResult> {
    const { skill, task, runId } = item;
    const timeoutMs = task.timeoutMs ?? this.options.timeoutMs;

    this.emit("task:start", { skillId: skill.id, taskId: task.id });

    return withSpan("task.execute", {
        "skill.id": skill.id,
        "task.id": task.id,
        "run.id": runId ?? 1,
        "task.timeout_ms": timeoutMs
    }, async (span) => {
        try {
          const adapter = adapterResolver(skill);
          const scorer = scorerResolver(task);

          // 调用 Adapter
          const response = await adapter.invoke(skill, task.inputData, {
            timeoutMs,
            retries: this.options.retries,
          });

          if (!response.success) {
            span.setAttribute("error", true);
            span.setAttribute("error.message", response.error || "Unknown error");
            
            const status: TaskStatus = response.error?.includes("timeout") ? "timeout" : "error";
            const result: TaskResult = {
              taskId: task.id,
              skillId: skill.id,
              status,
              score: 0,
              latencyMs: response.latencyMs,
              error: response.error,
              scorerType: scorer.type,
              runId,
              usage: response.usage,
              weight: task.weight,
            };
            this.emit("task:error", { skillId: skill.id, taskId: task.id, error: response.error });
            this.emit("task:result", result);
            return result;
          }

          // 评分
          const scorerResult = await scorer.score(response.output, task.expectedOutput);
          
          span.setAttribute("score", scorerResult.score);
          span.setAttribute("passed", scorerResult.passed);

          const result: TaskResult = {
            taskId: task.id,
            skillId: skill.id,
            status: scorerResult.passed ? "pass" : "fail",
            score: scorerResult.score,
            latencyMs: response.latencyMs,
            output: response.output,
            scorerType: scorer.type,
            reason: scorerResult.reason,
            runId,
            usage: response.usage,
            weight: task.weight,
          };

          this.emit("task:complete", result);
          this.emit("task:result", result);

          return result;
        } catch (err) {
          const error = err instanceof Error ? err.message : String(err);
          const result: TaskResult = {
            taskId: task.id,
            skillId: skill.id,
            status: "error",
            score: 0,
            latencyMs: 0,
            error,
            scorerType: "unknown",
            runId,
          };
          this.emit("task:error", { skillId: skill.id, taskId: task.id, error });
          this.emit("task:result", result);
          return result;
        }
    });
  }
}
