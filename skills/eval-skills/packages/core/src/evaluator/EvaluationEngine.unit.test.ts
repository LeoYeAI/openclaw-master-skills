import { describe, it, expect, vi, beforeEach } from "vitest";
import { EvaluationEngine } from "./EvaluationEngine.js";
import { SkillStore } from "../registry/SkillStore.js";
import { BenchmarkRegistry } from "../benchmarks/BenchmarkRegistry.js";
import { AdapterRegistry } from "../adapters/AdapterRegistry.js";
import { TaskExecutor } from "./TaskExecutor.js";
import * as fs from "node:fs";
import type { Benchmark, Skill, Task } from "../types/index.js";

// Mock dependencies
vi.mock("../registry/SkillStore.js");
vi.mock("../benchmarks/BenchmarkRegistry.js");
vi.mock("../adapters/AdapterRegistry.js");
vi.mock("./TaskExecutor.js");
vi.mock("node:fs");

describe("EvaluationEngine Unit Tests", () => {
  let engine: EvaluationEngine;
  let mockSkillStore: any;
  let mockBenchmarkRegistry: any;
  let mockAdapterRegistry: any;
  let mockTaskExecutor: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockSkillStore = new SkillStore();
    mockBenchmarkRegistry = new BenchmarkRegistry();
    mockAdapterRegistry = new AdapterRegistry();
    
    mockTaskExecutor = {
        on: vi.fn(),
        execute: vi.fn().mockResolvedValue([]),
    };
    (TaskExecutor as any).mockImplementation(() => mockTaskExecutor);

    // Mock fs
    (fs.existsSync as any).mockReturnValue(true);
    (fs.statSync as any).mockReturnValue({ isDirectory: () => true });
    
    engine = new EvaluationEngine({
        skillStore: mockSkillStore,
        benchmarkRegistry: mockBenchmarkRegistry,
        adapterRegistry: mockAdapterRegistry,
    });
  });

  it("should throw error if no skills found", async () => {
    // Mock loadSkills returning empty
    mockSkillStore.loadDir.mockReturnValue([]);
    
    await expect(engine.evaluate({
        skillPaths: ["/path/to/skills"],
        benchmark: "bench-1",
    } as any)).rejects.toThrow("No skills found");
  });

  it("should throw error if benchmark not found", async () => {
    mockSkillStore.loadDir.mockReturnValue([{ id: "s1" }]);
    mockBenchmarkRegistry.get.mockReturnValue(undefined);
    
    // Mock fs to allow skill path but deny benchmark path
     (fs.existsSync as any).mockImplementation((p: string) => {
         return p.includes("/path/to/skills");
     });

    await expect(engine.evaluate({
        skillPaths: ["/path/to/skills"],
        benchmark: "unknown-bench",
    } as any)).rejects.toThrow("Benchmark not found");
  });

  it("should throw error if no tasks in benchmark", async () => {
    mockSkillStore.loadDir.mockReturnValue([{ id: "s1" }]);
    mockBenchmarkRegistry.get.mockReturnValue({ id: "bench", tasks: [] });

    await expect(engine.evaluate({
        skillPaths: ["/path/to/skills"],
        benchmark: "bench",
    } as any)).rejects.toThrow("No tasks found");
  });

  it("should handle dry run", async () => {
    mockSkillStore.loadDir.mockReturnValue([{ id: "s1" }]);
    mockBenchmarkRegistry.get.mockReturnValue({ id: "bench", tasks: [{ id: "t1" }] });
    
    const result = await engine.evaluate({
        skillPaths: ["/path/to/skills"],
        benchmark: "bench",
        dryRun: true,
    } as any);
    
    expect(result).toEqual([]);
    expect(mockTaskExecutor.execute).not.toHaveBeenCalled();
  });

  it("should execute tasks and resolve adapters/scorers", async () => {
    const skill = { id: "s1", adapterType: "http" };
    const task = { id: "t1", expectedOutput: { type: "exact_match", value: "foo" } };
    
    mockSkillStore.loadDir.mockReturnValue([skill]);
    mockBenchmarkRegistry.get.mockReturnValue({ id: "bench", tasks: [task] });
    
    await engine.evaluate({
        skillPaths: ["/path/to/skills"],
        benchmark: "bench",
    } as any);
    
    expect(mockTaskExecutor.execute).toHaveBeenCalled();
    
    // Test callbacks
    const [items, adapterResolver, scorerResolver] = mockTaskExecutor.execute.mock.calls[0];
    expect(items.length).toBe(1);
    
    // Test adapter resolution
    adapterResolver(skill);
    expect(mockAdapterRegistry.resolveForSkill).toHaveBeenCalledWith(skill);
    
    // Test scorer resolution
    const scorer = scorerResolver(task);
    expect(scorer.type).toBe("exact_match");
  });
});
