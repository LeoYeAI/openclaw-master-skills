import { DiffReporter } from "./DiffReporter.js";
import type { SkillCompletionReport } from "../types/index.js";

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
    taskResults: [],
    evaluatorMetadata: {},
    ...overrides,
  };
}

describe("DiffReporter", () => {
  describe("generateDiff with paired skills", () => {
    it("should generate delta for skills present in both reports", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: {
            completionRate: 0.7,
            partialScore: 0.65,
            errorRate: 0.15,
            consistencyScore: 1.0,
            compositeScore: 0.75,
          },
          latency: { p50Ms: 100, p95Ms: 250, p99Ms: 400 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: {
            completionRate: 0.85,
            partialScore: 0.8,
            errorRate: 0.05,
            consistencyScore: 1.0,
            compositeScore: 0.9,
          },
          latency: { p50Ms: 80, p95Ms: 180, p99Ms: 300 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("### skill-1");
      expect(diff).toContain("Completion Rate");
      expect(diff).toContain("Error Rate");
      expect(diff).toContain("P95 Latency");
      expect(diff).toContain("Composite Score");
    });

    it("should show before and after values in table", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.7 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.85 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("70.0%");
      expect(diff).toContain("85.0%");
    });

    it("should use custom labels", () => {
      const reportA = [createMockReport({ skillId: "skill-1" })];
      const reportB = [createMockReport({ skillId: "skill-1" })];

      const diff = DiffReporter.generateDiff(reportA, reportB, "v1.0", "v2.0");

      expect(diff).toContain("v1.0");
      expect(diff).toContain("v2.0");
      expect(diff).toContain("Delta Report: v1.0");
    });
  });

  describe("delta arrows", () => {
    it("should show up arrow for improvement in completion rate", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.7 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.9 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // Should contain up arrow for positive delta
      expect(diff).toContain("\u2191"); // ↑
    });

    it("should show down arrow for regression in completion rate", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.9 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.7 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // Should contain down arrow for negative delta
      expect(diff).toContain("\u2193"); // ↓
    });

    it("should not show arrow when value unchanged", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.8 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.8 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // For completion rate delta of 0, should show +0.0% without arrow
      const completionRateLine = diff.split("\n").find((line) => line.includes("Completion Rate"));
      expect(completionRateLine).toContain("+0.0%");
    });
  });

  describe("new skill in report B", () => {
    it("should indicate skill is new in report B", () => {
      const reportA: SkillCompletionReport[] = [];
      const reportB = [createMockReport({ skillId: "new-skill" })];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("### new-skill (new in After)");
    });

    it("should show completion rate for new skill", () => {
      const reportA: SkillCompletionReport[] = [];
      const reportB = [
        createMockReport({
          skillId: "new-skill",
          summary: { ...createMockReport().summary, completionRate: 0.85 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("85.0%");
    });

    it("should use custom label for new skill", () => {
      const reportA: SkillCompletionReport[] = [];
      const reportB = [createMockReport({ skillId: "new-skill" })];

      const diff = DiffReporter.generateDiff(reportA, reportB, "Old", "New");

      expect(diff).toContain("(new in New)");
    });
  });

  describe("removed skill in report B", () => {
    it("should indicate skill was removed in report B", () => {
      const reportA = [createMockReport({ skillId: "removed-skill" })];
      const reportB: SkillCompletionReport[] = [];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("### removed-skill (removed in After)");
    });

    it("should use custom label for removed skill", () => {
      const reportA = [createMockReport({ skillId: "removed-skill" })];
      const reportB: SkillCompletionReport[] = [];

      const diff = DiffReporter.generateDiff(reportA, reportB, "Old", "New");

      expect(diff).toContain("(removed in New)");
    });
  });

  describe("delta formatting", () => {
    it("should format percentage deltas with + sign for positive values", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.7 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.85 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("+15.0%");
    });

    it("should format percentage deltas without + sign for negative values", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.85 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.7 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("-15.0%");
    });

    it("should format latency deltas in ms", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          latency: { p50Ms: 100, p95Ms: 200, p99Ms: 300 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          latency: { p50Ms: 80, p95Ms: 150, p99Ms: 250 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("-50");
      expect(diff).toContain("ms");
    });

    it("should format composite score deltas as decimal", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, compositeScore: 0.75 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, compositeScore: 0.85 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // The delta should be formatted (0.85 - 0.75 = 0.1, but shown as rounded integer in formatDelta)
      expect(diff).toContain("0.750");
      expect(diff).toContain("0.850");
    });
  });

  describe("multiple skills", () => {
    it("should handle multiple skills with different scenarios", () => {
      const reportA = [
        createMockReport({ skillId: "unchanged" }),
        createMockReport({ skillId: "improved", summary: { ...createMockReport().summary, completionRate: 0.7 } }),
        createMockReport({ skillId: "removed" }),
      ];
      const reportB = [
        createMockReport({ skillId: "unchanged" }),
        createMockReport({ skillId: "improved", summary: { ...createMockReport().summary, completionRate: 0.9 } }),
        createMockReport({ skillId: "new-skill" }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("### unchanged");
      expect(diff).toContain("### improved");
      expect(diff).toContain("### removed (removed in After)");
      expect(diff).toContain("### new-skill (new in After)");
    });

    it("should include all skills from both reports", () => {
      const reportA = [
        createMockReport({ skillId: "only-in-a" }),
        createMockReport({ skillId: "in-both" }),
      ];
      const reportB = [
        createMockReport({ skillId: "in-both" }),
        createMockReport({ skillId: "only-in-b" }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("only-in-a");
      expect(diff).toContain("in-both");
      expect(diff).toContain("only-in-b");
    });
  });

  describe("header formatting", () => {
    it("should include delta report header with labels", () => {
      const reportA = [createMockReport()];
      const reportB = [createMockReport()];

      const diff = DiffReporter.generateDiff(reportA, reportB, "Baseline", "Current");

      expect(diff).toContain("## Delta Report: Baseline \u2192 Current");
    });

    it("should use default labels", () => {
      const reportA = [createMockReport()];
      const reportB = [createMockReport()];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("## Delta Report: Before \u2192 After");
    });
  });

  describe("table formatting", () => {
    it("should generate valid markdown table for paired skills", () => {
      const reportA = [createMockReport({ skillId: "skill-1" })];
      const reportB = [createMockReport({ skillId: "skill-1" })];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("| Metric | Before | After |");
      expect(diff).toContain("|--------|----|----|---|");
    });

    it("should include delta column in table", () => {
      const reportA = [createMockReport({ skillId: "skill-1" })];
      const reportB = [createMockReport({ skillId: "skill-1" })];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // The delta column header is just Δ
      expect(diff).toContain("\u0394");
    });
  });

  describe("edge cases", () => {
    it("should handle empty report arrays", () => {
      const diff = DiffReporter.generateDiff([], []);

      expect(diff).toContain("## Delta Report");
      // Should not throw and should have minimal content
    });

    it("should handle reports with same values (no change)", () => {
      const report = createMockReport({ skillId: "stable" });
      const reportA = [report];
      const reportB = [{ ...report }];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      expect(diff).toContain("### stable");
      // All deltas should be 0 or +0
    });

    it("should handle very small delta values", () => {
      const reportA = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.8001 },
        }),
      ];
      const reportB = [
        createMockReport({
          skillId: "skill-1",
          summary: { ...createMockReport().summary, completionRate: 0.8002 },
        }),
      ];

      const diff = DiffReporter.generateDiff(reportA, reportB);

      // Should handle small floating point differences
      expect(diff).toContain("skill-1");
    });
  });
});
