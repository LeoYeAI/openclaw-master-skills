import type { SkillCompletionReport } from "../types/index.js";

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatDelta(a: number, b: number, isPercent = false): string {
  const diff = b - a;
  const sign = diff >= 0 ? "+" : "";
  const formatted = isPercent
    ? `${sign}${(diff * 100).toFixed(1)}%`
    : `${sign}${Math.round(diff)}`;
  const arrow = diff > 0 ? " \u2191" : diff < 0 ? " \u2193" : "";
  return `**${formatted}**${arrow}`;
}

/**
 * 差异对比报告生成器
 */
export class DiffReporter {
  static generateDiff(
    reportA: SkillCompletionReport[],
    reportB: SkillCompletionReport[],
    labelA = "Before",
    labelB = "After",
  ): string {
    const lines: string[] = [];
    lines.push(`## Delta Report: ${labelA} \u2192 ${labelB}`);
    lines.push("");

    // 按 skillId 配对
    const mapA = new Map(reportA.map((r) => [r.skillId, r]));
    const mapB = new Map(reportB.map((r) => [r.skillId, r]));
    const allSkillIds = new Set([...mapA.keys(), ...mapB.keys()]);

    for (const skillId of allSkillIds) {
      const a = mapA.get(skillId);
      const b = mapB.get(skillId);

      if (!a && b) {
        lines.push(`### ${skillId} (new in ${labelB})`);
        lines.push("");
        lines.push(`Completion Rate: ${formatPercent(b.summary.completionRate)}`);
        lines.push("");
        continue;
      }
      if (a && !b) {
        lines.push(`### ${skillId} (removed in ${labelB})`);
        lines.push("");
        continue;
      }
      if (!a || !b) continue;

      lines.push(`### ${skillId}`);
      lines.push("");
      lines.push(`| Metric | ${labelA} | ${labelB} | \u0394 |`);
      lines.push("|--------|----|----|---|");
      lines.push(
        `| Completion Rate | ${formatPercent(a.summary.completionRate)} | ${formatPercent(b.summary.completionRate)} | ${formatDelta(a.summary.completionRate, b.summary.completionRate, true)} |`,
      );
      lines.push(
        `| Error Rate | ${formatPercent(a.summary.errorRate)} | ${formatPercent(b.summary.errorRate)} | ${formatDelta(a.summary.errorRate, b.summary.errorRate, true)} |`,
      );
      lines.push(
        `| P95 Latency | ${Math.round(a.latency.p95Ms)}ms | ${Math.round(b.latency.p95Ms)}ms | ${formatDelta(a.latency.p95Ms, b.latency.p95Ms)}ms |`,
      );
      lines.push(
        `| Composite Score | ${a.summary.compositeScore.toFixed(3)} | ${b.summary.compositeScore.toFixed(3)} | ${formatDelta(a.summary.compositeScore, b.summary.compositeScore)} |`,
      );
      lines.push("");
    }

    return lines.join("\n");
  }
}
