import { SkillFinder, type FindOptions } from "./SkillFinder.js";
import { SkillStore } from "../registry/SkillStore.js";
import type { Skill, AdapterType, BenchmarkResultSummary } from "../types/index.js";

// Helper function to create mock skill
function createMockSkill(overrides: Partial<Skill> = {}): Skill {
  return {
    id: "test-skill",
    name: "Test Skill",
    version: "1.0.0",
    description: "A test skill for unit testing",
    tags: ["test", "mock"],
    inputSchema: { type: "object" },
    outputSchema: { type: "object" },
    adapterType: "http",
    entrypoint: "http://localhost:3000",
    metadata: {},
    ...overrides,
  };
}

// Helper function to create benchmark result summary
function createBenchmarkResult(
  completionRate: number,
  overrides: Partial<BenchmarkResultSummary> = {}
): BenchmarkResultSummary {
  return {
    benchmarkId: "test-benchmark",
    completionRate,
    compositeScore: completionRate * 0.9,
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

describe("SkillFinder", () => {
  let store: SkillStore;
  let finder: SkillFinder;

  beforeEach(() => {
    store = new SkillStore();
    finder = new SkillFinder(store);
  });

  describe("find with no options", () => {
    it("should return all skills when no options provided", () => {
      store.register(createMockSkill({ id: "skill-1" }));
      store.register(createMockSkill({ id: "skill-2" }));
      store.register(createMockSkill({ id: "skill-3" }));

      const result = finder.find();

      expect(result.skills).toHaveLength(3);
      expect(result.total).toBe(3);
    });

    it("should return empty result for empty store", () => {
      const result = finder.find();

      expect(result.skills).toHaveLength(0);
      expect(result.total).toBe(0);
    });

    it("should return same result as find({})", () => {
      store.register(createMockSkill({ id: "skill-1" }));

      const result1 = finder.find();
      const result2 = finder.find({});

      expect(result1.total).toBe(result2.total);
      expect(result1.skills.length).toBe(result2.skills.length);
    });
  });

  describe("find with query filter", () => {
    beforeEach(() => {
      store.register(
        createMockSkill({
          id: "web-search",
          name: "Web Search Tool",
          description: "Search the internet for information",
          tags: ["search", "web"],
        })
      );
      store.register(
        createMockSkill({
          id: "data-parser",
          name: "Data Parser",
          description: "Parse structured data files",
          tags: ["parser", "data"],
        })
      );
      store.register(
        createMockSkill({
          id: "api-caller",
          name: "API Caller",
          description: "Call external REST APIs",
          tags: ["api", "http", "rest"],
        })
      );
    });

    it("should filter by keyword in name", () => {
      const result = finder.find({ query: "Search" });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("web-search");
    });

    it("should filter by keyword in description", () => {
      const result = finder.find({ query: "internet" });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("web-search");
    });

    it("should filter by keyword in tags", () => {
      const result = finder.find({ query: "rest" });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("api-caller");
    });

    it("should be case insensitive", () => {
      const result = finder.find({ query: "WEB" });

      expect(result.skills.length).toBeGreaterThan(0);
    });
  });

  describe("find with tags filter", () => {
    beforeEach(() => {
      store.register(createMockSkill({ id: "skill-1", tags: ["api", "web", "search"] }));
      store.register(createMockSkill({ id: "skill-2", tags: ["api", "data"] }));
      store.register(createMockSkill({ id: "skill-3", tags: ["cli", "data"] }));
    });

    it("should filter by single tag (intersection)", () => {
      const result = finder.find({ tags: ["api"] });

      expect(result.skills).toHaveLength(2);
      expect(result.skills.every((s) => s.tags.includes("api"))).toBe(true);
    });

    it("should filter by multiple tags (intersection - must have all)", () => {
      const result = finder.find({ tags: ["api", "data"] });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("skill-2");
    });

    it("should return empty when no skills have all required tags", () => {
      const result = finder.find({ tags: ["api", "cli"] });

      expect(result.skills).toHaveLength(0);
    });

    it("should handle empty tags array", () => {
      const result = finder.find({ tags: [] });

      expect(result.skills).toHaveLength(3);
    });
  });

  describe("find with adapterType filter", () => {
    beforeEach(() => {
      store.register(createMockSkill({ id: "http-skill", adapterType: "http" }));
      store.register(createMockSkill({ id: "subprocess-skill", adapterType: "subprocess" }));
      store.register(createMockSkill({ id: "mcp-skill", adapterType: "mcp" }));
    });

    it("should filter by adapterType", () => {
      const result = finder.find({ adapterType: "http" });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("http-skill");
    });

    it("should return empty for non-matching adapterType", () => {
      const result = finder.find({ adapterType: "langchain" });

      expect(result.skills).toHaveLength(0);
    });
  });

  describe("find with minCompletion filter", () => {
    beforeEach(() => {
      store.register(
        createMockSkill({
          id: "high-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.95)] },
        })
      );
      store.register(
        createMockSkill({
          id: "mid-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.75)] },
        })
      );
      store.register(
        createMockSkill({
          id: "low-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.5)] },
        })
      );
      store.register(
        createMockSkill({
          id: "no-benchmark",
          metadata: {},
        })
      );
    });

    it("should filter by minimum completion rate", () => {
      const result = finder.find({ minCompletion: 0.7 });

      expect(result.skills).toHaveLength(2);
      expect(result.skills.map((s) => s.id).sort()).toEqual(["high-perf", "mid-perf"]);
    });

    it("should exclude skills without benchmark results", () => {
      const result = finder.find({ minCompletion: 0.1 });

      expect(result.skills.find((s) => s.id === "no-benchmark")).toBeUndefined();
    });

    it("should use max completion rate from multiple benchmarks", () => {
      store.register(
        createMockSkill({
          id: "multi-benchmark",
          metadata: {
            benchmarkResults: [
              createBenchmarkResult(0.6),
              createBenchmarkResult(0.85),
              createBenchmarkResult(0.7),
            ],
          },
        })
      );

      const result = finder.find({ minCompletion: 0.8 });

      expect(result.skills.find((s) => s.id === "multi-benchmark")).toBeDefined();
    });
  });

  describe("find with limit", () => {
    beforeEach(() => {
      for (let i = 0; i < 30; i++) {
        store.register(createMockSkill({ id: `skill-${i}` }));
      }
    });

    it("should limit results to specified count", () => {
      const result = finder.find({ limit: 5 });

      expect(result.skills).toHaveLength(5);
      expect(result.total).toBe(30);
    });

    it("should default to limit of 20", () => {
      const result = finder.find();

      expect(result.skills).toHaveLength(20);
      expect(result.total).toBe(30);
    });

    it("should return all if limit exceeds total", () => {
      const result = finder.find({ limit: 100 });

      expect(result.skills).toHaveLength(30);
    });
  });

  describe("sorting with query", () => {
    beforeEach(() => {
      store.register(
        createMockSkill({
          id: "name-match",
          name: "Search Tool",
          description: "Does other things",
          tags: ["utility"],
        })
      );
      store.register(
        createMockSkill({
          id: "desc-match",
          name: "Utility Tool",
          description: "Search and find",
          tags: ["utility"],
        })
      );
      store.register(
        createMockSkill({
          id: "tag-match",
          name: "Finder Tool",
          description: "Does things",
          tags: ["search"],
        })
      );
      store.register(
        createMockSkill({
          id: "all-match",
          name: "Search Engine",
          description: "Search the web",
          tags: ["search", "web"],
        })
      );
    });

    it("should sort by search score - name has highest weight (3)", () => {
      const result = finder.find({ query: "Search" });

      // Skills with "Search" in name should come first
      const ids = result.skills.map((s) => s.id);
      const nameMatchIndex = ids.indexOf("name-match");
      const descMatchIndex = ids.indexOf("desc-match");
      const tagMatchIndex = ids.indexOf("tag-match");

      // name-match should be before desc-match and tag-match (unless they also have name match)
      expect(nameMatchIndex).toBeLessThan(tagMatchIndex);
    });

    it("should prioritize skills matching in multiple fields", () => {
      const result = finder.find({ query: "Search" });

      // "all-match" has "Search" in name, description, and tags (score = 3+2+1 = 6)
      // "name-match" has "Search" only in name (score = 3)
      const ids = result.skills.map((s) => s.id);
      expect(ids[0]).toBe("all-match");
    });
  });

  describe("sorting without query", () => {
    beforeEach(() => {
      store.register(
        createMockSkill({
          id: "low-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.5)] },
        })
      );
      store.register(
        createMockSkill({
          id: "high-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.95)] },
        })
      );
      store.register(
        createMockSkill({
          id: "mid-perf",
          metadata: { benchmarkResults: [createBenchmarkResult(0.75)] },
        })
      );
      store.register(
        createMockSkill({
          id: "no-benchmark",
          metadata: {},
        })
      );
    });

    it("should sort by completion rate descending when no query", () => {
      const result = finder.find();

      const ids = result.skills.map((s) => s.id);
      expect(ids[0]).toBe("high-perf");
      expect(ids[1]).toBe("mid-perf");
      expect(ids[2]).toBe("low-perf");
      expect(ids[3]).toBe("no-benchmark"); // 0 completion rate
    });
  });

  describe("combined filters", () => {
    beforeEach(() => {
      store.register(
        createMockSkill({
          id: "perfect-match",
          name: "Web Search API",
          tags: ["api", "search"],
          adapterType: "http",
          metadata: { benchmarkResults: [createBenchmarkResult(0.9)] },
        })
      );
      store.register(
        createMockSkill({
          id: "partial-match-tags",
          name: "Web Tool",
          tags: ["cli"],
          adapterType: "http",
          metadata: { benchmarkResults: [createBenchmarkResult(0.9)] },
        })
      );
      store.register(
        createMockSkill({
          id: "partial-match-adapter",
          name: "Web Service",
          tags: ["api", "search"],
          adapterType: "subprocess",
          metadata: { benchmarkResults: [createBenchmarkResult(0.9)] },
        })
      );
      store.register(
        createMockSkill({
          id: "partial-match-completion",
          name: "Web API",
          tags: ["api", "search"],
          adapterType: "http",
          metadata: { benchmarkResults: [createBenchmarkResult(0.5)] },
        })
      );
    });

    it("should apply all filters together", () => {
      const result = finder.find({
        query: "Web",
        tags: ["api", "search"],
        adapterType: "http",
        minCompletion: 0.8,
      });

      expect(result.skills).toHaveLength(1);
      expect(result.skills[0]?.id).toBe("perfect-match");
    });

    it("should return correct total after filtering", () => {
      const result = finder.find({
        tags: ["api"],
        limit: 1,
      });

      expect(result.skills).toHaveLength(1);
      // Total should reflect count after all filters but before limit
      expect(result.total).toBe(3); // perfect-match, partial-match-adapter, partial-match-completion
    });
  });
});
