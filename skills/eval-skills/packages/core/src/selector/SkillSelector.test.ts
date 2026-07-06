import { SkillSelector, type SelectResult } from "./SkillSelector.js";
import type { Skill, SkillCompletionReport, SelectStrategy, AdapterType } from "../types/index.js";

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

// Helper function to create mock report
function createMockReport(overrides: Partial<SkillCompletionReport> = {}): SkillCompletionReport {
  return {
    skillId: "test-skill",
    skillVersion: "1.0.0",
    benchmarkId: "test-benchmark",
    timestamp: new Date().toISOString(),
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

// Helper function to create strategy
function createStrategy(overrides: Partial<SelectStrategy> = {}): SelectStrategy {
  return {
    filters: {},
    sortBy: "compositeScore",
    order: "desc",
    ...overrides,
  };
}

describe("SkillSelector", () => {
  describe("minCompletionRate filter", () => {
    it("should filter by minimum completion rate", () => {
      const skills = [
        createMockSkill({ id: "high" }),
        createMockSkill({ id: "mid" }),
        createMockSkill({ id: "low" }),
      ];
      const reports = [
        createMockReport({ skillId: "high", summary: { ...createMockReport().summary, completionRate: 0.9 } }),
        createMockReport({ skillId: "mid", summary: { ...createMockReport().summary, completionRate: 0.7 } }),
        createMockReport({ skillId: "low", summary: { ...createMockReport().summary, completionRate: 0.5 } }),
      ];
      const strategy = createStrategy({ filters: { minCompletionRate: 0.7 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
      expect(result.selected.map((s) => s.skill.id)).toEqual(expect.arrayContaining(["high", "mid"]));
    });

    it("should include skills exactly at threshold", () => {
      const skills = [createMockSkill({ id: "exact" })];
      const reports = [
        createMockReport({ skillId: "exact", summary: { ...createMockReport().summary, completionRate: 0.7 } }),
      ];
      const strategy = createStrategy({ filters: { minCompletionRate: 0.7 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
    });
  });

  describe("maxErrorRate filter", () => {
    it("should filter by maximum error rate", () => {
      const skills = [
        createMockSkill({ id: "low-error" }),
        createMockSkill({ id: "high-error" }),
      ];
      const reports = [
        createMockReport({ skillId: "low-error", summary: { ...createMockReport().summary, errorRate: 0.05 } }),
        createMockReport({ skillId: "high-error", summary: { ...createMockReport().summary, errorRate: 0.2 } }),
      ];
      const strategy = createStrategy({ filters: { maxErrorRate: 0.1 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
      expect(result.selected[0]?.skill.id).toBe("low-error");
    });

    it("should include skills exactly at threshold", () => {
      const skills = [createMockSkill({ id: "exact" })];
      const reports = [
        createMockReport({ skillId: "exact", summary: { ...createMockReport().summary, errorRate: 0.1 } }),
      ];
      const strategy = createStrategy({ filters: { maxErrorRate: 0.1 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
    });
  });

  describe("maxLatencyP95Ms filter", () => {
    it("should filter by maximum P95 latency", () => {
      const skills = [
        createMockSkill({ id: "fast" }),
        createMockSkill({ id: "slow" }),
      ];
      const reports = [
        createMockReport({ skillId: "fast", latency: { p50Ms: 50, p95Ms: 100, p99Ms: 150 } }),
        createMockReport({ skillId: "slow", latency: { p50Ms: 500, p95Ms: 1000, p99Ms: 1500 } }),
      ];
      const strategy = createStrategy({ filters: { maxLatencyP95Ms: 500 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
      expect(result.selected[0]?.skill.id).toBe("fast");
    });

    it("should include skills exactly at threshold", () => {
      const skills = [createMockSkill({ id: "exact" })];
      const reports = [
        createMockReport({ skillId: "exact", latency: { p50Ms: 100, p95Ms: 500, p99Ms: 600 } }),
      ];
      const strategy = createStrategy({ filters: { maxLatencyP95Ms: 500 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
    });
  });

  describe("adapterTypes filter", () => {
    it("should filter by allowed adapter types", () => {
      const skills = [
        createMockSkill({ id: "http", adapterType: "http" }),
        createMockSkill({ id: "subprocess", adapterType: "subprocess" }),
        createMockSkill({ id: "mcp", adapterType: "mcp" }),
      ];
      const reports = [
        createMockReport({ skillId: "http" }),
        createMockReport({ skillId: "subprocess" }),
        createMockReport({ skillId: "mcp" }),
      ];
      const strategy = createStrategy({ filters: { adapterTypes: ["http", "mcp"] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
      expect(result.selected.map((s) => s.skill.id).sort()).toEqual(["http", "mcp"]);
    });

    it("should return empty when no adapter types match", () => {
      const skills = [createMockSkill({ id: "http", adapterType: "http" })];
      const reports = [createMockReport({ skillId: "http" })];
      const strategy = createStrategy({ filters: { adapterTypes: ["subprocess"] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(0);
    });

    it("should handle empty adapterTypes array as no filter", () => {
      const skills = [
        createMockSkill({ id: "http", adapterType: "http" }),
        createMockSkill({ id: "subprocess", adapterType: "subprocess" }),
      ];
      const reports = [
        createMockReport({ skillId: "http" }),
        createMockReport({ skillId: "subprocess" }),
      ];
      const strategy = createStrategy({ filters: { adapterTypes: [] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
    });
  });

  describe("requiredTags filter", () => {
    it("should filter by required tags (must have all)", () => {
      const skills = [
        createMockSkill({ id: "all-tags", tags: ["api", "search", "web"] }),
        createMockSkill({ id: "some-tags", tags: ["api", "cli"] }),
        createMockSkill({ id: "no-tags", tags: ["other"] }),
      ];
      const reports = [
        createMockReport({ skillId: "all-tags" }),
        createMockReport({ skillId: "some-tags" }),
        createMockReport({ skillId: "no-tags" }),
      ];
      const strategy = createStrategy({ filters: { requiredTags: ["api", "search"] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
      expect(result.selected[0]?.skill.id).toBe("all-tags");
    });

    it("should handle single required tag", () => {
      const skills = [
        createMockSkill({ id: "has-tag", tags: ["api"] }),
        createMockSkill({ id: "no-tag", tags: ["cli"] }),
      ];
      const reports = [
        createMockReport({ skillId: "has-tag" }),
        createMockReport({ skillId: "no-tag" }),
      ];
      const strategy = createStrategy({ filters: { requiredTags: ["api"] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(1);
    });

    it("should handle empty requiredTags array as no filter", () => {
      const skills = [
        createMockSkill({ id: "skill-1" }),
        createMockSkill({ id: "skill-2" }),
      ];
      const reports = [
        createMockReport({ skillId: "skill-1" }),
        createMockReport({ skillId: "skill-2" }),
      ];
      const strategy = createStrategy({ filters: { requiredTags: [] } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
    });
  });

  describe("sorting by compositeScore", () => {
    it("should sort by compositeScore descending (default)", () => {
      const skills = [
        createMockSkill({ id: "low" }),
        createMockSkill({ id: "high" }),
        createMockSkill({ id: "mid" }),
      ];
      const reports = [
        createMockReport({ skillId: "low", summary: { ...createMockReport().summary, compositeScore: 0.5 } }),
        createMockReport({ skillId: "high", summary: { ...createMockReport().summary, compositeScore: 0.9 } }),
        createMockReport({ skillId: "mid", summary: { ...createMockReport().summary, compositeScore: 0.7 } }),
      ];
      const strategy = createStrategy({ sortBy: "compositeScore", order: "desc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected.map((s) => s.skill.id)).toEqual(["high", "mid", "low"]);
    });

    it("should sort by compositeScore ascending", () => {
      const skills = [
        createMockSkill({ id: "low" }),
        createMockSkill({ id: "high" }),
        createMockSkill({ id: "mid" }),
      ];
      const reports = [
        createMockReport({ skillId: "low", summary: { ...createMockReport().summary, compositeScore: 0.5 } }),
        createMockReport({ skillId: "high", summary: { ...createMockReport().summary, compositeScore: 0.9 } }),
        createMockReport({ skillId: "mid", summary: { ...createMockReport().summary, compositeScore: 0.7 } }),
      ];
      const strategy = createStrategy({ sortBy: "compositeScore", order: "asc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected.map((s) => s.skill.id)).toEqual(["low", "mid", "high"]);
    });
  });

  describe("sorting by latency", () => {
    it("should sort by latency (P95) ascending", () => {
      const skills = [
        createMockSkill({ id: "slow" }),
        createMockSkill({ id: "fast" }),
        createMockSkill({ id: "medium" }),
      ];
      const reports = [
        createMockReport({ skillId: "slow", latency: { p50Ms: 500, p95Ms: 1000, p99Ms: 1500 } }),
        createMockReport({ skillId: "fast", latency: { p50Ms: 50, p95Ms: 100, p99Ms: 150 } }),
        createMockReport({ skillId: "medium", latency: { p50Ms: 200, p95Ms: 400, p99Ms: 600 } }),
      ];
      const strategy = createStrategy({ sortBy: "latency", order: "asc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected.map((s) => s.skill.id)).toEqual(["fast", "medium", "slow"]);
    });

    it("should sort by latency descending", () => {
      const skills = [
        createMockSkill({ id: "slow" }),
        createMockSkill({ id: "fast" }),
      ];
      const reports = [
        createMockReport({ skillId: "slow", latency: { p50Ms: 500, p95Ms: 1000, p99Ms: 1500 } }),
        createMockReport({ skillId: "fast", latency: { p50Ms: 50, p95Ms: 100, p99Ms: 150 } }),
      ];
      const strategy = createStrategy({ sortBy: "latency", order: "desc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected.map((s) => s.skill.id)).toEqual(["slow", "fast"]);
    });
  });

  describe("sorting by completionRate", () => {
    it("should sort by completionRate", () => {
      const skills = [
        createMockSkill({ id: "mid" }),
        createMockSkill({ id: "high" }),
        createMockSkill({ id: "low" }),
      ];
      const reports = [
        createMockReport({ skillId: "mid", summary: { ...createMockReport().summary, completionRate: 0.7 } }),
        createMockReport({ skillId: "high", summary: { ...createMockReport().summary, completionRate: 0.95 } }),
        createMockReport({ skillId: "low", summary: { ...createMockReport().summary, completionRate: 0.5 } }),
      ];
      const strategy = createStrategy({ sortBy: "completionRate", order: "desc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected.map((s) => s.skill.id)).toEqual(["high", "mid", "low"]);
    });
  });

  describe("topK limit", () => {
    it("should limit results to topK", () => {
      const skills = [
        createMockSkill({ id: "skill-1" }),
        createMockSkill({ id: "skill-2" }),
        createMockSkill({ id: "skill-3" }),
        createMockSkill({ id: "skill-4" }),
        createMockSkill({ id: "skill-5" }),
      ];
      const reports = skills.map((s) => createMockReport({ skillId: s.id }));
      const strategy = createStrategy({ topK: 3 });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(3);
    });

    it("should return all if topK exceeds count", () => {
      const skills = [
        createMockSkill({ id: "skill-1" }),
        createMockSkill({ id: "skill-2" }),
      ];
      const reports = skills.map((s) => createMockReport({ skillId: s.id }));
      const strategy = createStrategy({ topK: 10 });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
    });

    it("should handle topK of 0 as no limit", () => {
      const skills = [
        createMockSkill({ id: "skill-1" }),
        createMockSkill({ id: "skill-2" }),
        createMockSkill({ id: "skill-3" }),
      ];
      const reports = skills.map((s) => createMockReport({ skillId: s.id }));
      const strategy = createStrategy({ topK: 0 });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(3);
    });
  });

  describe("rank assignment", () => {
    it("should assign rank starting from 1", () => {
      const skills = [
        createMockSkill({ id: "first" }),
        createMockSkill({ id: "second" }),
        createMockSkill({ id: "third" }),
      ];
      const reports = [
        createMockReport({ skillId: "first", summary: { ...createMockReport().summary, compositeScore: 0.9 } }),
        createMockReport({ skillId: "second", summary: { ...createMockReport().summary, compositeScore: 0.8 } }),
        createMockReport({ skillId: "third", summary: { ...createMockReport().summary, compositeScore: 0.7 } }),
      ];
      const strategy = createStrategy({ sortBy: "compositeScore", order: "desc" });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected[0]?.rank).toBe(1);
      expect(result.selected[1]?.rank).toBe(2);
      expect(result.selected[2]?.rank).toBe(3);
    });

    it("should assign consecutive ranks after filtering", () => {
      const skills = [
        createMockSkill({ id: "high" }),
        createMockSkill({ id: "mid" }),
        createMockSkill({ id: "low" }),
      ];
      const reports = [
        createMockReport({ skillId: "high", summary: { ...createMockReport().summary, completionRate: 0.9, compositeScore: 0.9 } }),
        createMockReport({ skillId: "mid", summary: { ...createMockReport().summary, completionRate: 0.7, compositeScore: 0.7 } }),
        createMockReport({ skillId: "low", summary: { ...createMockReport().summary, completionRate: 0.5, compositeScore: 0.5 } }),
      ];
      const strategy = createStrategy({ filters: { minCompletionRate: 0.6 } });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected).toHaveLength(2);
      expect(result.selected[0]?.rank).toBe(1);
      expect(result.selected[1]?.rank).toBe(2);
    });
  });

  describe("result counts", () => {
    it("should return correct total and filtered counts", () => {
      const skills = [
        createMockSkill({ id: "skill-1" }),
        createMockSkill({ id: "skill-2" }),
        createMockSkill({ id: "skill-3" }),
        createMockSkill({ id: "skill-4" }),
      ];
      const reports = [
        createMockReport({ skillId: "skill-1", summary: { ...createMockReport().summary, completionRate: 0.9 } }),
        createMockReport({ skillId: "skill-2", summary: { ...createMockReport().summary, completionRate: 0.8 } }),
        createMockReport({ skillId: "skill-3", summary: { ...createMockReport().summary, completionRate: 0.5 } }),
        createMockReport({ skillId: "skill-4", summary: { ...createMockReport().summary, completionRate: 0.4 } }),
      ];
      const strategy = createStrategy({ filters: { minCompletionRate: 0.7 }, topK: 1 });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.total).toBe(4); // Total skills
      expect(result.filtered).toBe(2); // After filter, before topK
      expect(result.selected).toHaveLength(1); // After topK
    });

    it("should exclude skills without reports", () => {
      const skills = [
        createMockSkill({ id: "with-report" }),
        createMockSkill({ id: "without-report" }),
      ];
      const reports = [createMockReport({ skillId: "with-report" })];
      const strategy = createStrategy();

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.total).toBe(2);
      expect(result.selected).toHaveLength(1);
      expect(result.selected[0]?.skill.id).toBe("with-report");
    });
  });

  describe("combined filters and sorting", () => {
    it("should apply filters before sorting", () => {
      const skills = [
        createMockSkill({ id: "best-filtered-out", tags: ["excluded"] }),
        createMockSkill({ id: "second-best", tags: ["included"] }),
        createMockSkill({ id: "third-best", tags: ["included"] }),
      ];
      const reports = [
        createMockReport({ skillId: "best-filtered-out", summary: { ...createMockReport().summary, compositeScore: 0.99 } }),
        createMockReport({ skillId: "second-best", summary: { ...createMockReport().summary, compositeScore: 0.9 } }),
        createMockReport({ skillId: "third-best", summary: { ...createMockReport().summary, compositeScore: 0.8 } }),
      ];
      const strategy = createStrategy({
        filters: { requiredTags: ["included"] },
        sortBy: "compositeScore",
        order: "desc",
      });

      const result = SkillSelector.select(skills, reports, strategy);

      expect(result.selected[0]?.skill.id).toBe("second-best");
      expect(result.selected[0]?.rank).toBe(1);
    });
  });
});
