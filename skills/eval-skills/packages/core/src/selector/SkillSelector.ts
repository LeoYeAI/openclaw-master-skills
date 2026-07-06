import type { SelectStrategy, Skill, SkillCompletionReport } from "../types/index.js";

/**
 * 选中的 Skill 条目
 */
export interface SelectedSkill {
  skill: Skill;
  report: SkillCompletionReport;
  rank: number;
}

/**
 * 筛选结果
 */
export interface SelectResult {
  selected: SelectedSkill[];
  total: number;
  filtered: number;
}

/**
 * Skill 多维筛选器
 * 流水线：Filter → Score → Rank → TopK
 */
export class SkillSelector {
  /**
   * 按策略筛选 Skill
   */
  static select(
    skills: Skill[],
    reports: SkillCompletionReport[],
    strategy: SelectStrategy,
  ): SelectResult {
    const total = skills.length;

    // 构建 skillId → report 映射
    const reportMap = new Map<string, SkillCompletionReport>();
    for (const report of reports) {
      reportMap.set(report.skillId, report);
    }

    // 构建候选列表
    let candidates = skills
      .filter((s) => reportMap.has(s.id))
      .map((skill) => ({
        skill,
        report: reportMap.get(skill.id)!,
      }));

    // === Filter 阶段 ===
    const { filters } = strategy;

    if (filters.minCompletionRate !== undefined) {
      candidates = candidates.filter(
        (c) => c.report.summary.completionRate >= filters.minCompletionRate!,
      );
    }

    if (filters.maxErrorRate !== undefined) {
      candidates = candidates.filter(
        (c) => c.report.summary.errorRate <= filters.maxErrorRate!,
      );
    }

    if (filters.maxLatencyP95Ms !== undefined) {
      candidates = candidates.filter(
        (c) => c.report.latency.p95Ms <= filters.maxLatencyP95Ms!,
      );
    }

    if (filters.adapterTypes && filters.adapterTypes.length > 0) {
      candidates = candidates.filter((c) =>
        filters.adapterTypes!.includes(c.skill.adapterType),
      );
    }

    if (filters.requiredTags && filters.requiredTags.length > 0) {
      candidates = candidates.filter((c) =>
        filters.requiredTags!.every((tag) => c.skill.tags.includes(tag)),
      );
    }

    const filtered = candidates.length;

    // === Score + Rank 阶段 ===
    const sortKey = strategy.sortBy;
    const ascending = strategy.order === "asc";

    candidates.sort((a, b) => {
      let valA: number;
      let valB: number;

      switch (sortKey) {
        case "completionRate":
          valA = a.report.summary.completionRate;
          valB = b.report.summary.completionRate;
          break;
        case "compositeScore":
          valA = a.report.summary.compositeScore;
          valB = b.report.summary.compositeScore;
          break;
        case "latency":
          valA = a.report.latency.p95Ms;
          valB = b.report.latency.p95Ms;
          break;
        case "tokenCost":
          valA = a.report.tokenCost?.estimatedUSD ?? 0;
          valB = b.report.tokenCost?.estimatedUSD ?? 0;
          break;
        default:
          valA = a.report.summary.compositeScore;
          valB = b.report.summary.compositeScore;
      }

      return ascending ? valA - valB : valB - valA;
    });

    // === TopK 阶段 ===
    if (strategy.topK && strategy.topK > 0) {
      candidates = candidates.slice(0, strategy.topK);
    }

    // 分配 rank
    const selected: SelectedSkill[] = candidates.map((c, idx) => ({
      skill: c.skill,
      report: c.report,
      rank: idx + 1,
    }));

    return { selected, total, filtered };
  }
}
