import { mkdtempSync, writeFileSync, rmSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { BenchmarkRegistry } from "./BenchmarkRegistry.js";
import { EvalSkillsError } from "../errors.js";
import type { Benchmark } from "../types/index.js";

function createMockBenchmark(overrides: Partial<Benchmark> = {}): Benchmark {
  return {
    id: "test-bench",
    name: "Test Benchmark",
    version: "1.0.0",
    domain: "testing",
    scoringMethod: "mean",
    metadata: {},
    tasks: [
      {
        id: "t1",
        description: "Test task",
        inputData: { x: 1 },
        expectedOutput: { type: "exact", value: "1" },
        evaluator: { type: "exact" },
        timeoutMs: 5000,
      },
    ],
    ...overrides,
  } as Benchmark;
}

describe("BenchmarkRegistry", () => {
  let registry: BenchmarkRegistry;

  beforeEach(() => {
    registry = new BenchmarkRegistry();
  });

  describe("register & get", () => {
    it("registers and retrieves a benchmark", () => {
      const bench = createMockBenchmark();
      registry.register(bench);
      expect(registry.get("test-bench")).toEqual(bench);
    });

    it("returns undefined for missing id", () => {
      expect(registry.get("nope")).toBeUndefined();
    });
  });

  describe("list", () => {
    it("returns metadata without full task details", () => {
      registry.register(createMockBenchmark({ id: "b1", name: "Bench 1" }));
      registry.register(createMockBenchmark({ id: "b2", name: "Bench 2" }));

      const list = registry.list();
      expect(list).toHaveLength(2);
      expect(list[0]).toHaveProperty("id");
      expect(list[0]).toHaveProperty("taskCount");
      expect(list[0]).not.toHaveProperty("tasks");
    });
  });

  describe("loadFromFile", () => {
    let tmpDir: string;

    beforeEach(() => {
      tmpDir = mkdtempSync(path.join(tmpdir(), "eval-bench-test-"));
    });

    afterEach(() => {
      rmSync(tmpDir, { recursive: true, force: true });
    });

    it("loads valid benchmark from file", () => {
      const filePath = path.join(tmpDir, "bench.json");
      writeFileSync(filePath, JSON.stringify(createMockBenchmark({ id: "from-file" })));

      const bench = registry.loadFromFile(filePath);
      expect(bench.id).toBe("from-file");
      expect(registry.get("from-file")).toBeDefined();
    });

    it("throws BENCHMARK_NOT_FOUND for missing file", () => {
      expect(() => registry.loadFromFile("/nonexistent.json")).toThrow(EvalSkillsError);
      try {
        registry.loadFromFile("/nonexistent.json");
      } catch (e) {
        expect((e as EvalSkillsError).code).toBe("E3001");
      }
    });

    it("throws BENCHMARK_SCHEMA_ERR for invalid JSON", () => {
      const filePath = path.join(tmpDir, "bad.json");
      writeFileSync(filePath, "not valid json {{{{");

      expect(() => registry.loadFromFile(filePath)).toThrow(EvalSkillsError);
      try {
        registry.loadFromFile(filePath);
      } catch (e) {
        expect((e as EvalSkillsError).code).toBe("E3002");
      }
    });
  });

  describe("loadBuiltins", () => {
    let tmpDir: string;

    beforeEach(() => {
      tmpDir = mkdtempSync(path.join(tmpdir(), "eval-builtins-"));
    });

    afterEach(() => {
      rmSync(tmpDir, { recursive: true, force: true });
    });

    it("loads from flat JSON files", () => {
      writeFileSync(
        path.join(tmpDir, "bench-a.json"),
        JSON.stringify(createMockBenchmark({ id: "flat-a" })),
      );

      registry.loadBuiltins(tmpDir);
      expect(registry.get("flat-a")).toBeDefined();
    });

    it("loads from subdirectory benchmark.json", () => {
      const subDir = path.join(tmpDir, "my-bench");
      mkdirSync(subDir);
      writeFileSync(
        path.join(subDir, "benchmark.json"),
        JSON.stringify(createMockBenchmark({ id: "sub-bench" })),
      );

      registry.loadBuiltins(tmpDir);
      expect(registry.get("sub-bench")).toBeDefined();
    });

    it("handles non-existent directory gracefully", () => {
      expect(() => registry.loadBuiltins("/nonexistent/path")).not.toThrow();
    });

    it("ignores non-json files", () => {
      writeFileSync(path.join(tmpDir, "readme.md"), "# hello");
      registry.loadBuiltins(tmpDir);
      expect(registry.list()).toHaveLength(0);
    });
  });
});
