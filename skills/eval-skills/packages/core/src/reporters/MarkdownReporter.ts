import * as fs from "node:fs";
import * as path from "node:path";
import type { SkillCompletionReport, TaskResult } from "../types/index.js";
import type { IReporter } from "./interfaces/IReporter.js";

const STATUS_EMOJI: Record<string, string> = {
  pass: "\u2705 PASS",
  fail: "\u274c FAIL",
  error: "\u26a0\ufe0f ERROR",
  timeout: "\u23f1\ufe0f TIMEOUT",
};

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatMs(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.round(ms)}ms`;
}

/**
 * Markdown 格式报告生成器
 */
export class MarkdownReporter implements IReporter {
  readonly format = "markdown";

  generate(reports: SkillCompletionReport[]): string {
    return MarkdownReporter.generate(reports);
  }

  async writeToFile(reports: SkillCompletionReport[], filePath: string): Promise<void> {
    return MarkdownReporter.writeToFile(reports, filePath);
  }

  static generate(reports: SkillCompletionReport[]): string {
    if (reports.length === 0) return "# eval-skills Report\n\nNo evaluation results.\n";

    const benchmarkId = reports[0]!.benchmarkId;
    const timestamp = reports[0]!.timestamp;
    const lines: string[] = [];

    lines.push("# eval-skills Report");
    lines.push("");
    lines.push(`Generated: ${timestamp} | Benchmark: ${benchmarkId}`);
    lines.push("");

    // Summary table
    lines.push("## Summary");
    lines.push("");
    lines.push("| Skill | Completion Rate | Error Rate | P95 Latency | Composite Score |");
    lines.push("|-------|:--------------:|:----------:|:-----------:|:---------------:|");

    // Sort by compositeScore desc
    const sorted = [...reports].sort(
      (a, b) => b.summary.compositeScore - a.summary.compositeScore,
    );

    for (const report of sorted) {
      const s = report.summary;
      lines.push(
        `| ${report.skillId} | ${formatPercent(s.completionRate)} | ${formatPercent(s.errorRate)} | ${formatMs(report.latency.p95Ms)} | ${s.compositeScore.toFixed(3)} |`,
      );
    }

    lines.push("");

    // Detail sections
    for (const report of sorted) {
      lines.push(`## Details: ${report.skillId}`);
      lines.push("");
      lines.push(`Version: ${report.skillVersion} | Tasks: ${report.taskResults.length}`);
      lines.push("");
      lines.push("### Task Results");
      lines.push("");
      lines.push("| Task ID | Status | Score | Latency |");
      lines.push("|---------|--------|-------|---------|");

      for (const tr of report.taskResults) {
        const status = STATUS_EMOJI[tr.status] ?? tr.status;
        lines.push(
          `| ${tr.taskId} | ${status} | ${tr.score.toFixed(2)} | ${formatMs(tr.latencyMs)} |`,
        );
      }
      lines.push("");
    }

    return lines.join("\n");
  }

  static writeToFile(reports: SkillCompletionReport[], filePath: string): void {
    const dir = path.dirname(filePath);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(filePath, MarkdownReporter.generate(reports), "utf-8");
  }
}
