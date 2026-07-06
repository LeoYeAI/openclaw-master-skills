import { ReportBuilder } from "./ReportBuilder.js";
import type { Skill, TaskResult, TaskStatus } from "../types/index.js";

// Helper function to create mock skill
function createMockSkill(overrides: Partial<Skill> = {}): Skill {
  return {
    id: "test-skill",
    name: "Test Skill",
    version: "1.0.0",
    description: "A test skill",
    tags: ["test"],
    inputSchema: { type: "object" },
    outputSchema: { type: "object" },
    adapterType: "http",
    entrypoint: "http://localhost:3000",
    metadata: {},
    ...overrides,
  };
}

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

describe("ReportBuilder", () => {
  const skill = createMockSkill();
  const benchmarkId = "test-benchmark";

  describe("build with empty results", () => {
    it("should return zero report for empty taskResults", () => {
      const report = ReportBuilder.build(skill, benchmarkId, []);

      expect(report.skillId).toBe(skill.id);
      expect(report.skillVersion).toBe(skill.version);
      expect(report.benchmarkId).toBe(benchmarkId);
      expect(report.summary.completionRate).toBe(0);
      expect(report.summary.partialScore).toBe(0);
      expect(report.summary.errorRate).toBe(0);
      expect(report.summary.consistencyScore).toBe(1.0);
      expect(report.summary.compositeScore).toBe(0);
      expect(report.latency.p50Ms).toBe(0);
      expect(report.latency.p95Ms).toBe(0);
      expect(report.latency.p99Ms).toBe(0);
      expect(report.taskResults).toHaveLength(0);
    });

    it("should include timestamp in ISO format", () => {
      const report = ReportBuilder.build(skill, benchmarkId, []);

      expect(report.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });
  });

  describe("consistency score calculation", () => {
    it("should return 1.0 for single run", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass", runId: 1 }),
      ];
      const report = ReportBuilder.build(skill, benchmarkId, results);
      expect(report.summary.consistencyScore).toBe(1.0);
    });

    it("should calculate consistency score for multiple runs", () => {
      const results: TaskResult[] = [
        // Run 1: 100% pass
        createMockTaskResult({ taskId: "t1", status: "pass", runId: 1 }),
        createMockTaskResult({ taskId: "t2", status: "pass", runId: 1 }),
        // Run 2: 50% pass
        createMockTaskResult({ taskId: "t1", status: "pass", runId: 2 }),
        createMockTaskResult({ taskId: "t2", status: "fail", runId: 2 }),
      ];

      // Run 1 rate: 1.0
      // Run 2 rate: 0.5
      // Mean: 0.75
      // Variance: ((1-0.75)^2 + (0.5-0.75)^2) / 2 = (0.0625 + 0.0625) / 2 = 0.0625
      // StdDev: sqrt(0.0625) = 0.25
      // Consistency: 1 - 0.25 = 0.75

      const report = ReportBuilder.build(skill, benchmarkId, results);
      expect(report.summary.consistencyScore).toBeCloseTo(0.75);
    });
  });

  describe("completion rate calculation", () => {
    it("should return completionRate 1.0 when all tasks pass", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "pass" }),
        createMockTaskResult({ taskId: "t3", status: "pass" }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.completionRate).toBe(1.0);
    });

    it("should calculate correct completion rate for mixed results", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "pass" }),
        createMockTaskResult({ taskId: "t3", status: "fail", score: 0 }),
        createMockTaskResult({ taskId: "t4", status: "error", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.completionRate).toBe(0.5); // 2 pass out of 4
    });

    it("should return completionRate 0.0 when all tasks fail", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "fail", score: 0 }),
        createMockTaskResult({ taskId: "t2", status: "fail", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.completionRate).toBe(0);
    });
  });

  describe("error rate calculation", () => {
    it("should return errorRate 0.0 when no errors or timeouts", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "fail", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.errorRate).toBe(0);
    });

    it("should include error status in error rate", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "error", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.errorRate).toBe(0.5);
    });

    it("should include timeout status in error rate", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "timeout", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.errorRate).toBe(0.5);
    });

    it("should combine error and timeout in error rate", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", status: "pass" }),
        createMockTaskResult({ taskId: "t3", status: "error", score: 0 }),
        createMockTaskResult({ taskId: "t4", status: "timeout", score: 0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.errorRate).toBe(0.5); // 2 errors out of 4
    });
  });

  describe("latency percentiles", () => {
    it("should compute p50 correctly", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", latencyMs: 100 }),
        createMockTaskResult({ taskId: "t2", latencyMs: 200 }),
        createMockTaskResult({ taskId: "t3", latencyMs: 300 }),
        createMockTaskResult({ taskId: "t4", latencyMs: 400 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.latency.p50Ms).toBe(200);
    });

    it("should compute p95 correctly", () => {
      // Create 20 results with latencies 100, 200, 300, ..., 2000
      const results: TaskResult[] = Array.from({ length: 20 }, (_, i) =>
        createMockTaskResult({ taskId: `t${i}`, latencyMs: (i + 1) * 100 })
      );

      const report = ReportBuilder.build(skill, benchmarkId, results);

      // p95 of [100, 200, ..., 2000] = 1900 (19th element at 95th percentile)
      expect(report.latency.p95Ms).toBe(1900);
    });

    it("should compute p99 correctly", () => {
      // Create 100 results with latencies 10, 20, 30, ..., 1000
      const results: TaskResult[] = Array.from({ length: 100 }, (_, i) =>
        createMockTaskResult({ taskId: `t${i}`, latencyMs: (i + 1) * 10 })
      );

      const report = ReportBuilder.build(skill, benchmarkId, results);

      // p99 of sorted array = value at index ceil(0.99 * 100) - 1 = 98
      expect(report.latency.p99Ms).toBe(990);
    });

    it("should handle single result", () => {
      const results: TaskResult[] = [createMockTaskResult({ latencyMs: 500 })];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.latency.p50Ms).toBe(500);
      expect(report.latency.p95Ms).toBe(500);
      expect(report.latency.p99Ms).toBe(500);
    });

    it("should filter out zero latencies", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", latencyMs: 0 }),
        createMockTaskResult({ taskId: "t2", latencyMs: 100 }),
        createMockTaskResult({ taskId: "t3", latencyMs: 200 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      // Only 100 and 200 should be considered
      expect(report.latency.p50Ms).toBe(100);
    });

    it("should round latency values", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", latencyMs: 100.7 }),
        createMockTaskResult({ taskId: "t2", latencyMs: 200.3 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(Number.isInteger(report.latency.p50Ms)).toBe(true);
    });
  });

  describe("composite score calculation", () => {
    it("should calculate composite score with formula: 0.5*CR + 0.2*(1-lat_norm) + 0.3*(1-ER)", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass", latencyMs: 1000 }),
        createMockTaskResult({ taskId: "t2", status: "pass", latencyMs: 1000 }),
      ];

      // CR = 1.0, ER = 0.0, lat_norm = 1000/30000 = 0.0333...
      // composite = 0.5*1.0 + 0.2*(1-0.0333) + 0.3*(1-0.0) = 0.5 + 0.1933 + 0.3 = 0.9933
      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.compositeScore).toBeCloseTo(0.9933, 2);
    });

    it("should clamp latency normalization to [0, 1]", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass", latencyMs: 50000 }), // > maxLatencyMs
      ];

      // lat_norm should be clamped to 1.0
      const report = ReportBuilder.build(skill, benchmarkId, results, 30000);

      // composite = 0.5*1.0 + 0.2*(1-1) + 0.3*(1-0) = 0.5 + 0 + 0.3 = 0.8
      expect(report.summary.compositeScore).toBeCloseTo(0.8, 2);
    });

    it("should use custom maxLatencyMs", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass", latencyMs: 5000 }),
      ];

      // With maxLatencyMs = 10000, lat_norm = 5000/10000 = 0.5
      // composite = 0.5*1.0 + 0.2*(1-0.5) + 0.3*(1-0) = 0.5 + 0.1 + 0.3 = 0.9
      const report = ReportBuilder.build(skill, benchmarkId, results, 10000);

      expect(report.summary.compositeScore).toBeCloseTo(0.9, 2);
    });

    it("should round composite score to 4 decimal places", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", status: "pass", latencyMs: 1234 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      // Check that it's rounded to at most 4 decimal places
      const decimals = (report.summary.compositeScore.toString().split(".")[1] || "").length;
      expect(decimals).toBeLessThanOrEqual(4);
    });
  });

  describe("partial score calculation", () => {
    it("should calculate partial score as average of all scores", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", score: 1.0 }),
        createMockTaskResult({ taskId: "t2", score: 0.5 }),
        createMockTaskResult({ taskId: "t3", score: 0.0 }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.summary.partialScore).toBe(0.5);
    });
  });

  describe("buildMultiple", () => {
    it("should group results by skillId", () => {
      const skill1 = createMockSkill({ id: "skill-1", version: "1.0.0" });
      const skill2 = createMockSkill({ id: "skill-2", version: "2.0.0" });

      const allResults: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", skillId: "skill-1", status: "pass" }),
        createMockTaskResult({ taskId: "t2", skillId: "skill-1", status: "pass" }),
        createMockTaskResult({ taskId: "t3", skillId: "skill-2", status: "fail", score: 0 }),
      ];

      const reports = ReportBuilder.buildMultiple([skill1, skill2], benchmarkId, allResults);

      expect(reports).toHaveLength(2);

      const report1 = reports.find((r) => r.skillId === "skill-1");
      const report2 = reports.find((r) => r.skillId === "skill-2");

      expect(report1?.taskResults).toHaveLength(2);
      expect(report1?.summary.completionRate).toBe(1.0);

      expect(report2?.taskResults).toHaveLength(1);
      expect(report2?.summary.completionRate).toBe(0);
    });

    it("should return empty report for skill with no results", () => {
      const skill1 = createMockSkill({ id: "skill-1" });
      const skill2 = createMockSkill({ id: "skill-2" });

      const allResults: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", skillId: "skill-1", status: "pass" }),
      ];

      const reports = ReportBuilder.buildMultiple([skill1, skill2], benchmarkId, allResults);

      const report2 = reports.find((r) => r.skillId === "skill-2");
      expect(report2?.taskResults).toHaveLength(0);
      expect(report2?.summary.completionRate).toBe(0);
    });

    it("should use custom maxLatencyMs for all reports", () => {
      const skill1 = createMockSkill({ id: "skill-1" });

      const allResults: TaskResult[] = [
        createMockTaskResult({ taskId: "t1", skillId: "skill-1", latencyMs: 5000 }),
      ];

      const reports = ReportBuilder.buildMultiple([skill1], benchmarkId, allResults, 10000);

      // lat_norm = 5000/10000 = 0.5
      expect(reports[0]?.summary.compositeScore).toBeCloseTo(0.9, 2);
    });
  });

  describe("report metadata", () => {
    it("should include evaluatorMetadata as empty object", () => {
      const report = ReportBuilder.build(skill, benchmarkId, [createMockTaskResult()]);

      expect(report.evaluatorMetadata).toEqual({});
    });

    it("should include all task results in report", () => {
      const results: TaskResult[] = [
        createMockTaskResult({ taskId: "t1" }),
        createMockTaskResult({ taskId: "t2" }),
        createMockTaskResult({ taskId: "t3" }),
      ];

      const report = ReportBuilder.build(skill, benchmarkId, results);

      expect(report.taskResults).toHaveLength(3);
      expect(report.taskResults).toEqual(results);
    });
  });
});
