import { bootstrapCI, ConfidenceInterval } from "./BootstrapCI.js";
import type {
  TaskResult,
  SkillCompletionReport,
  ReportSummary,
  LatencyStats,
  Skill,
} from "../types/index.js";

/**
 * 计算数组的指定百分位数
 */
function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  const idx = Math.ceil(p * sorted.length) - 1;
  return sorted[Math.max(0, Math.min(idx, sorted.length - 1))]!;
}

/**
 * 将值限制在 [min, max] 范围内
 */
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * 报告构建器
 * 从 TaskResult[] 聚合生成 SkillCompletionReport
 */
export class ReportBuilder {
  /**
   * Calculate combinations C(n, k)
   */
  private static combinations(n: number, k: number): number {
    if (k < 0 || k > n) {
      return 0;
    }
    if (k === 0 || k === n) {
      return 1;
    }
    if (k > n / 2) {
      k = n - k;
    }
    let res = 1;
    for (let i = 1; i <= k; i++) {
      res = (res * (n - i + 1)) / i;
    }
    return res;
  }

  /**
   * Calculate Pass@k
   * Formula: 1 - C(n-c, k) / C(n, k)
   * where n = total samples per task, c = correct samples per task, k = k
   */
  private static calculatePassAtK(taskResults: TaskResult[], k: number = 1): number {
    // Group by taskId
    const taskGroups = new Map<string, TaskResult[]>();
    for (const r of taskResults) {
        if (!taskGroups.has(r.taskId)) taskGroups.set(r.taskId, []);
        taskGroups.get(r.taskId)!.push(r);
    }
    
    let totalPassProb = 0;
    for (const [_, results] of taskGroups) {
        const n = results.length;
        const c = results.filter(r => r.status === "pass").length;
        
        if (n === 0) continue;

        if (c >= n) {
            totalPassProb += 1.0;
        } else if (c === 0) {
            totalPassProb += 0.0;
        } else {
             // 1 - C(n-c, k) / C(n, k)
             // If k > n, we can't really calculate pass@k from n samples strictly, 
             // but typically k <= n is required. If k > n, we clamp k to n?
             // Or we just assume k=1 if not specified.
             // Let's assume k=1 for "pass at least one" if k is not provided or k=1.
             // If k is provided via some config, we should use it. 
             // Currently scoringMethod doesn't carry k. 
             // We default k=1 here which effectively means "did any sample pass?"
             
             // For k=1: 1 - C(n-c, 1)/C(n, 1) = 1 - (n-c)/n = c/n (Wait, this is pass rate, not pass@1)
             // Wait. Pass@1 means "if we take 1 sample, what's the prob it passes?" -> c/n.
             // Pass@k means "if we take k samples, what's the prob AT LEAST ONE passes?"
             // = 1 - Prob(all k fail)
             // = 1 - C(n-c, k) / C(n, k)
             
             // If we ran n=10 times, and c=5 passed.
             // Pass@1 = 1 - C(5, 1)/C(10, 1) = 1 - 5/10 = 0.5. Correct.
             // Pass@10 = 1 - C(0, 10)/C(10, 10) = 1 - 1/1 = 0. Correct (since c>0, at least one passed in 10 samples).
             
             const probAllFail = ReportBuilder.combinations(n - c, k) / ReportBuilder.combinations(n, k);
             totalPassProb += (1 - probAllFail);
        }
    }
    
    return taskGroups.size > 0 ? totalPassProb / taskGroups.size : 0;
  }

  /**
   * 为单个 Skill 构建评测报告
   */
  static build(
    skill: Skill,
    benchmarkId: string,
    taskResults: TaskResult[],
    maxLatencyMs: number = 30000,
    scoringMethod: "mean" | "weighted_mean" | "pass_at_k" = "mean",
  ): SkillCompletionReport {
    const total = taskResults.length;
    if (total === 0) {
      return {
        skillId: skill.id,
        skillVersion: skill.version,
        benchmarkId,
        timestamp: new Date().toISOString(),
        summary: {
          completionRate: 0,
          partialScore: 0,
          errorRate: 0,
          consistencyScore: 1.0,
          compositeScore: 0,
        },
        latency: { p50Ms: 0, p95Ms: 0, p99Ms: 0 },
        taskResults,
        evaluatorMetadata: {},
      };
    }

    // 统计
    const passCount = taskResults.filter((r) => r.status === "pass").length;
    const errorCount = taskResults.filter(
      (r) => r.status === "error" || r.status === "timeout",
    ).length;

    const completionRate = passCount / total;
    let partialScore = 0;
    
    // Calculate partialScore based on scoringMethod
    if (scoringMethod === "pass_at_k") {
        // Assume k=1 for score calculation if not specified (standard Pass@1)
        partialScore = ReportBuilder.calculatePassAtK(taskResults, 1);
    } else {
        // mean or weighted_mean (weighted not fully supported in Task structure yet, treating as mean)
        if (scoringMethod === "weighted_mean") {
            const totalWeight = taskResults.reduce((sum, r) => sum + (r.weight ?? 1), 0);
            if (totalWeight > 0) {
                partialScore = taskResults.reduce((sum, r) => sum + r.score * (r.weight ?? 1), 0) / totalWeight;
            } else {
                partialScore = 0;
            }
        } else {
            partialScore = taskResults.reduce((sum, r) => sum + r.score, 0) / total;
        }
    }

    const errorRate = errorCount / total;

    // Consistency Score
    let consistencyScore = 1.0;
    const runGroups = new Map<number, TaskResult[]>();

    // Group results by runId
    for (const r of taskResults) {
      const runId = r.runId ?? 1;
      if (!runGroups.has(runId)) runGroups.set(runId, []);
      runGroups.get(runId)!.push(r);
    }

    if (runGroups.size > 1) {
      const runRates: number[] = [];
      for (const [_, results] of runGroups) {
        const runPass = results.filter((r) => r.status === "pass").length;
        runRates.push(runPass / results.length);
      }

      const mean = runRates.reduce((a, b) => a + b, 0) / runRates.length;
      const variance =
        runRates.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / runRates.length;
      const stdDev = Math.sqrt(variance);
      consistencyScore = Math.max(0, 1.0 - stdDev);
    }

    // 延迟统计
    const latencies = taskResults
      .map((r) => r.latencyMs)
      .filter((l) => l > 0)
      .sort((a, b) => a - b);

    const latency: LatencyStats = {
      p50Ms: Math.round(percentile(latencies, 0.5)),
      p95Ms: Math.round(percentile(latencies, 0.95)),
      p99Ms: Math.round(percentile(latencies, 0.99)),
    };

    // Composite Score
    const latencyP95Normalized = clamp(latency.p95Ms / maxLatencyMs, 0, 1);
    const compositeScore =
      0.5 * completionRate + 0.2 * (1 - latencyP95Normalized) + 0.3 * (1 - errorRate);

    // Token Usage
    let tokenCost: { promptTokens: number; completionTokens: number; totalTokens: number } | undefined;
    const totalPrompt = taskResults.reduce((sum, r) => sum + (r.usage?.promptTokens ?? 0), 0);
    const totalCompletion = taskResults.reduce((sum, r) => sum + (r.usage?.completionTokens ?? 0), 0);
    
    if (totalPrompt > 0 || totalCompletion > 0) {
        tokenCost = {
            promptTokens: totalPrompt,
            completionTokens: totalCompletion,
            totalTokens: totalPrompt + totalCompletion
        };
    }

    let confidenceInterval: ConfidenceInterval | undefined;
    // Calculate bootstrap CI if we have enough samples (e.g. >= 10)
    if (taskResults.length >= 10) {
        const scores = taskResults.map(r => r.score);
        confidenceInterval = bootstrapCI(scores);
    }

    const summary: ReportSummary = {
      completionRate: Math.round(completionRate * 10000) / 10000,
      partialScore: Math.round(partialScore * 10000) / 10000,
      errorRate: Math.round(errorRate * 10000) / 10000,
      consistencyScore,
      compositeScore: Math.round(compositeScore * 10000) / 10000,
      confidenceInterval,
    };

    return {
      skillId: skill.id,
      skillVersion: skill.version,
      benchmarkId,
      timestamp: new Date().toISOString(),
      summary,
      latency,
      tokenCost,
      taskResults,
      evaluatorMetadata: {},
    };
  }

  /**
   * 为多个 Skill 构建评测报告
   */
  static buildMultiple(
    skills: Skill[],
    benchmarkId: string,
    allResults: TaskResult[],
    maxLatencyMs: number = 30000,
    scoringMethod: "mean" | "weighted_mean" | "pass_at_k" = "mean",
  ): SkillCompletionReport[] {
    return skills.map((skill) => {
      const skillResults = allResults.filter((r) => r.skillId === skill.id);
      return ReportBuilder.build(skill, benchmarkId, skillResults, maxLatencyMs, scoringMethod);
    });
  }
}
