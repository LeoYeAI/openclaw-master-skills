import { MarkdownReporter } from "./MarkdownReporter.js";
import type { SkillCompletionReport, TaskResult } from "../types/index.js";

// Helper function to create mock task result
function createMockTaskResult(overrides: Partial<TaskResult> = {}): TaskResult {
  return {
    taskId: "task-1",
    skillId: "test-skill",
    status: "pass",
    score: 1.0,
    latencyMs: 100,
    scorerType: "exact_match",
    ...overrides,
  };
}

// Helper function to create mock report
function createMockReport(overrides: Partial<SkillCompletionReport> = {}): SkillCompletionReport {
  return {
    skillId: "test-skill",
    skillVersion: "1.0.0",
    benchmarkId: "test-benchmark",
    timestamp: "2024-01-15T10:30:00.000Z",
    summary: {
      completionRate: 0.8,
      partialScore: 0.75,
      errorRate: 0.1,
      consistencyScore: 1.0,
      compositeScore: 0.85,
    },
    latency: {
      p50Ms: 100,
      p95Ms: 200,
      p99Ms: 300,
    },
    taskResults: [createMockTaskResult()],
    evaluatorMetadata: {},
    ...overrides,
  };
}

describe("MarkdownReporter", () => {
  describe("generate with empty reports", () => {
    it("should return 'No evaluation results' for empty reports array", () => {
      const markdown = MarkdownReporter.generate([]);

      expect(markdown).toContain("# eval-skills Report");
      expect(markdown).toContain("No evaluation results");
    });
  });

  describe("generate with reports", () => {
    it("should generate valid markdown with header", () => {
      const reports = [createMockReport()];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("# eval-skills Report");
    });

    it("should include timestamp and benchmark ID", () => {
      const reports = [createMockReport({ timestamp: "2024-01-15T10:30:00.000Z", benchmarkId: "my-benchmark" })];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("Generated: 2024-01-15T10:30:00.000Z");
      expect(markdown).toContain("Benchmark: my-benchmark");
    });

    it("should include summary section with table", () => {
      const reports = [createMockReport()];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("## Summary");
      expect(markdown).toContain("| Skill | Completion Rate | Error Rate | P95 Latency | Composite Score |");
      expect(markdown).toContain("|-------|:--------------:|:----------:|:-----------:|:---------------:|");
    });

    it("should include skill row in summary table", () => {
      const reports = [
        createMockReport({
          skillId: "my-skill",
          summary: {
            completionRate: 0.85,
            partialScore: 0.8,
            errorRate: 0.05,
            consistencyScore: 1.0,
            compositeScore: 0.9,
          },
          latency: { p50Ms: 100, p95Ms: 250, p99Ms: 400 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("my-skill");
      expect(markdown).toContain("85.0%"); // completionRate
      expect(markdown).toContain("5.0%"); // errorRate
      expect(markdown).toContain("250ms"); // p95 latency
      expect(markdown).toContain("0.900"); // compositeScore
    });

    it("should include detail sections for each skill", () => {
      const reports = [
        createMockReport({
          skillId: "skill-1",
          skillVersion: "1.0.0",
          taskResults: [
            createMockTaskResult({ taskId: "t1" }),
            createMockTaskResult({ taskId: "t2" }),
          ],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("## Details: skill-1");
      expect(markdown).toContain("Version: 1.0.0");
      expect(markdown).toContain("Tasks: 2");
      expect(markdown).toContain("### Task Results");
    });

    it("should include task results table in detail section", () => {
      const reports = [
        createMockReport({
          taskResults: [
            createMockTaskResult({ taskId: "task-001", status: "pass", score: 1.0, latencyMs: 150 }),
          ],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("| Task ID | Status | Score | Latency |");
      expect(markdown).toContain("task-001");
      expect(markdown).toContain("1.00"); // score
      expect(markdown).toContain("150ms"); // latency
    });
  });

  describe("sorting by compositeScore", () => {
    it("should sort reports by compositeScore descending", () => {
      const reports = [
        createMockReport({
          skillId: "low-score",
          summary: { ...createMockReport().summary, compositeScore: 0.5 },
        }),
        createMockReport({
          skillId: "high-score",
          summary: { ...createMockReport().summary, compositeScore: 0.95 },
        }),
        createMockReport({
          skillId: "mid-score",
          summary: { ...createMockReport().summary, compositeScore: 0.75 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      // In the summary table, high-score should appear before mid-score, which should appear before low-score
      const highIndex = markdown.indexOf("high-score");
      const midIndex = markdown.indexOf("mid-score");
      const lowIndex = markdown.indexOf("low-score");

      expect(highIndex).toBeLessThan(midIndex);
      expect(midIndex).toBeLessThan(lowIndex);
    });
  });

  describe("percentage formatting", () => {
    it("should format percentages correctly with one decimal place", () => {
      const reports = [
        createMockReport({
          summary: {
            completionRate: 0.8567,
            partialScore: 0.75,
            errorRate: 0.1234,
            consistencyScore: 1.0,
            compositeScore: 0.85,
          },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("85.7%"); // completionRate rounded
      expect(markdown).toContain("12.3%"); // errorRate rounded
    });

    it("should handle 0% correctly", () => {
      const reports = [
        createMockReport({
          summary: { ...createMockReport().summary, errorRate: 0 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("0.0%");
    });

    it("should handle 100% correctly", () => {
      const reports = [
        createMockReport({
          summary: { ...createMockReport().summary, completionRate: 1.0 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("100.0%");
    });
  });

  describe("latency formatting", () => {
    it("should format latency in ms for values under 1000ms", () => {
      const reports = [
        createMockReport({
          latency: { p50Ms: 50, p95Ms: 500, p99Ms: 800 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("500ms");
    });

    it("should format latency in seconds for values 1000ms and above", () => {
      const reports = [
        createMockReport({
          latency: { p50Ms: 500, p95Ms: 1500, p99Ms: 3000 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("1.5s");
    });

    it("should format exactly 1000ms as 1.0s", () => {
      const reports = [
        createMockReport({
          latency: { p50Ms: 100, p95Ms: 1000, p99Ms: 1500 },
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("1.0s");
    });

    it("should round ms values", () => {
      const reports = [
        createMockReport({
          taskResults: [
            createMockTaskResult({ latencyMs: 123.7 }),
          ],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("124ms");
    });
  });

  describe("status emoji formatting", () => {
    it("should format pass status with checkmark", () => {
      const reports = [
        createMockReport({
          taskResults: [createMockTaskResult({ status: "pass" })],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("PASS");
    });

    it("should format fail status with X", () => {
      const reports = [
        createMockReport({
          taskResults: [createMockTaskResult({ status: "fail" })],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("FAIL");
    });

    it("should format error status with warning", () => {
      const reports = [
        createMockReport({
          taskResults: [createMockTaskResult({ status: "error" })],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("ERROR");
    });

    it("should format timeout status with clock", () => {
      const reports = [
        createMockReport({
          taskResults: [createMockTaskResult({ status: "timeout" })],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("TIMEOUT");
    });
  });

  describe("multiple reports", () => {
    it("should generate sections for all reports", () => {
      const reports = [
        createMockReport({ skillId: "skill-alpha", summary: { ...createMockReport().summary, compositeScore: 0.9 } }),
        createMockReport({ skillId: "skill-beta", summary: { ...createMockReport().summary, compositeScore: 0.8 } }),
        createMockReport({ skillId: "skill-gamma", summary: { ...createMockReport().summary, compositeScore: 0.7 } }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("## Details: skill-alpha");
      expect(markdown).toContain("## Details: skill-beta");
      expect(markdown).toContain("## Details: skill-gamma");
    });

    it("should include all skills in summary table", () => {
      const reports = [
        createMockReport({ skillId: "skill-1" }),
        createMockReport({ skillId: "skill-2" }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      // Count occurrences in summary table (before details section)
      const summarySection = markdown.split("## Details")[0];
      expect(summarySection).toContain("skill-1");
      expect(summarySection).toContain("skill-2");
    });
  });

  describe("edge cases", () => {
    it("should handle skill with no task results", () => {
      const reports = [
        createMockReport({
          skillId: "empty-skill",
          taskResults: [],
        }),
      ];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("Tasks: 0");
    });

    it("should handle very long skill IDs", () => {
      const longId = "very-long-skill-id-".repeat(5);
      const reports = [createMockReport({ skillId: longId })];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain(longId);
    });

    it("should handle special characters in skill ID", () => {
      const reports = [createMockReport({ skillId: "skill-with-special_chars.v1" })];

      const markdown = MarkdownReporter.generate(reports);

      expect(markdown).toContain("skill-with-special_chars.v1");
    });
  });
});
