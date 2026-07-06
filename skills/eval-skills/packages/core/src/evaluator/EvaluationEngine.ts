import { EventEmitter } from "node:events";
import * as fs from "node:fs";
import * as path from "node:path";
import type { EvalRunConfig, Skill, Benchmark, SkillCompletionReport, Task, TaskResult } from "../types/index.js";
import { SkillStore } from "../registry/SkillStore.js";
import { BenchmarkRegistry } from "../benchmarks/BenchmarkRegistry.js";
import { AdapterRegistry } from "../adapters/AdapterRegistry.js";
import { TaskExecutor } from "./TaskExecutor.js";
import type { TaskItem } from "./TaskExecutor.js";
import { ReportBuilder } from "./ReportBuilder.js";
import { ScorerFactory } from "./scorers/ScorerFactory.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../errors.js";
import { SqliteStore } from "../store/SqliteStore.js";
import { nanoid } from "nanoid";

/**
 * 评测引擎 — 编排整个 Skill × Benchmark 评测流程
 */
export class EvaluationEngine extends EventEmitter {
  private skillStore: SkillStore;
  private benchmarkRegistry: BenchmarkRegistry;
  private adapterRegistry: AdapterRegistry;
  private sqliteStore?: SqliteStore;

  constructor(options?: {
    skillStore?: SkillStore;
    benchmarkRegistry?: BenchmarkRegistry;
    adapterRegistry?: AdapterRegistry;
    sqliteStore?: SqliteStore;
  }) {
    super();
    this.skillStore = options?.skillStore ?? new SkillStore();
    this.benchmarkRegistry = options?.benchmarkRegistry ?? new BenchmarkRegistry();
    this.adapterRegistry = options?.adapterRegistry ?? new AdapterRegistry();
    this.sqliteStore = options?.sqliteStore;
  }

  /**
   * 执行评测
   */
  async evaluate(config: EvalRunConfig): Promise<SkillCompletionReport[]> {
    // 1. 加载 Skills
    const skills = this.loadSkills(config.skillPaths);
    if (skills.length === 0) {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.SKILL_NOT_FOUND,
        "No skills found in the specified paths",
        { paths: config.skillPaths },
      );
    }

    // 2. 加载 Benchmark / Tasks
    let tasks: Task[];
    let benchmarkId: string;
    let maxLatencyMs = config.timeoutMs;

    if (config.tasksFile) {
      // 从自定义任务文件加载
      const raw = fs.readFileSync(config.tasksFile, "utf-8");
      tasks = JSON.parse(raw) as Task[];
      benchmarkId = "custom";
    } else {
      const benchmark = this.loadBenchmark(config.benchmark);
      tasks = benchmark.tasks;
      benchmarkId = benchmark.id;
      maxLatencyMs = benchmark.maxLatencyMs ?? config.timeoutMs;
    }

    if (tasks.length === 0) {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.EVAL_NO_TASKS,
        "No tasks found in benchmark or tasks file",
      );
    }

    // 3. Dry run 检查
    if (config.dryRun) {
      const runs = config.runs && config.runs > 0 ? config.runs : 1;
      this.emit("eval:dry-run", {
        skillCount: skills.length,
        taskCount: tasks.length,
        totalItems: skills.length * tasks.length * runs,
      });
      return [];
    }

    // 4. 构建笛卡尔积 TaskItem[]
    const items: TaskItem[] = [];
    const runs = config.runs && config.runs > 0 ? config.runs : 1;
    
    // Create evaluation record if store exists
    const skillEvalIds = new Map<string, string>();
    for (const skill of skills) {
        let id = nanoid();
        
        // If resume is enabled, try to find existing evaluation
        if (config.resume && this.sqliteStore) {
             const existing = this.sqliteStore.findLatestEvaluation(skill.id, benchmarkId);
             if (existing) {
                 id = existing.id;
             }
        }

        skillEvalIds.set(skill.id, id);
        if (this.sqliteStore) {
            this.sqliteStore.saveSkill(skill);
            // Only create if not exists (handled by INSERT ... ON CONFLICT DO NOTHING in SqliteStore, 
            // but we can also check here or rely on store implementation)
            this.sqliteStore.createEvaluation(id, skill.id, benchmarkId);
        }
    }

    for (let runId = 1; runId <= runs; runId++) {
      for (const skill of skills) {
        for (const task of tasks) {
          // If resume is enabled, check if task result exists
           if (config.resume && this.sqliteStore) {
              const sEvalId = skillEvalIds.get(skill.id)!;
              if (this.sqliteStore.hasTaskResult(sEvalId, task.id, runId)) {
                  // Skip this task
                  this.emit("task:skip", { skillId: skill.id, taskId: task.id, runId });
                  continue;
              }
           }
           items.push({ skill, task, runId });
        }
      }
    }

    // 5. 创建 TaskExecutor
    const executor = new TaskExecutor({
      concurrency: config.concurrency,
      timeoutMs: config.timeoutMs,
      retries: config.retries,
    });

    // 转发事件
    executor.on("task:start", (data) => this.emit("task:start", data));
    executor.on("task:complete", (data) => this.emit("task:complete", data));
    executor.on("task:error", (data) => this.emit("task:error", data));
    executor.on("progress", (data) => this.emit("progress", data));
    
    // 监听结果用于持久化
    executor.on("task:result", (result: TaskResult) => {
        if (this.sqliteStore) {
             const sEvalId = skillEvalIds.get(result.skillId);
             if (sEvalId) {
                 this.sqliteStore.saveTaskResult(sEvalId, result);
             }
        }
    });

    // 6. 执行
    const allResults = await executor.execute(
      items,
      (skill) => this.adapterRegistry.resolveForSkill(skill),
      (task) => {
        const evaluatorType = task.evaluator?.type ?? config.evaluator ?? "exact";
        return ScorerFactory.create(evaluatorType, config.llmJudge);
      },
    );

    // 7. 构建报告
    let scoringMethod: "mean" | "weighted_mean" | "pass_at_k" = "mean";
    if (benchmarkId !== "custom") {
        try {
            const benchmark = this.loadBenchmark(benchmarkId);
            scoringMethod = benchmark.scoringMethod;
        } catch (error) {
            if (process.env.DEBUG) {
                console.warn(`[EvaluationEngine] Failed to load benchmark ${benchmarkId} for scoring method lookup:`, error);
            }
        }
    }
    
    const reports = ReportBuilder.buildMultiple(
        skills, 
        benchmarkId, 
        allResults, 
        maxLatencyMs,
        scoringMethod
    );

    // Save summaries
    if (this.sqliteStore) {
        for (const report of reports) {
            const sEvalId = skillEvalIds.get(report.skillId);
            if (sEvalId) {
                this.sqliteStore.updateEvaluationSummary(sEvalId, report.summary);
            }
        }
    }

    // 8. 发射完成事件
    this.emit("eval:complete", { reports });

    return reports;
  }

  /**
   * 从路径列表加载 Skills
   */
  private loadSkills(skillPaths: string[]): Skill[] {
    const skills: Skill[] = [];

    for (const p of skillPaths) {
      if (!fs.existsSync(p)) {
        this.emit("warn", { message: `Skill path not found, skipping: ${p}` });
        continue;
      }

      const stat = fs.statSync(p);
      if (stat.isDirectory()) {
        const loaded = this.skillStore.loadDir(p);
        skills.push(...loaded);
      } else if (p.endsWith(".json")) {
        try {
          const raw = fs.readFileSync(p, "utf-8");
          const skill = JSON.parse(raw) as Skill;
          skills.push(skill);
          this.skillStore.register(skill);
        } catch (err) {
          this.emit("warn", {
            message: `Failed to load skill from ${p}: ${(err as Error).message}`,
          });
        }
      }
    }

    return skills;
  }

  /**
   * 加载 Benchmark（优先内置，其次文件路径）
   */
  private loadBenchmark(benchmarkIdOrPath: string): Benchmark {
    // 先尝试从注册表获取
    const existing = this.benchmarkRegistry.get(benchmarkIdOrPath);
    if (existing) return existing;

    // 尝试作为文件路径加载
    const resolved = path.resolve(benchmarkIdOrPath);
    if (fs.existsSync(resolved)) {
      return this.benchmarkRegistry.loadFromFile(resolved);
    }

    throw new EvalSkillsError(
      EvalSkillsErrorCode.BENCHMARK_NOT_FOUND,
      `Benchmark not found: ${benchmarkIdOrPath}`,
      { benchmarkIdOrPath },
    );
  }
}
