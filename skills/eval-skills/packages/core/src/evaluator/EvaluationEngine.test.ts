import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { EvaluationEngine } from "./EvaluationEngine.js";
import { SkillStore } from "../registry/SkillStore.js";
import { BenchmarkRegistry } from "../benchmarks/BenchmarkRegistry.js";
import { AdapterRegistry } from "../adapters/AdapterRegistry.js";
import { TaskExecutor } from "./TaskExecutor.js";
import * as fs from "node:fs";

// Mock dependencies
vi.mock("node:fs");
vi.mock("../registry/SkillStore.js");
vi.mock("../benchmarks/BenchmarkRegistry.js");
vi.mock("../adapters/AdapterRegistry.js");
vi.mock("./TaskExecutor.js");

describe("EvaluationEngine", () => {
    let engine: EvaluationEngine;
    let mockSkillStore: any;
    let mockBenchmarkRegistry: any;
    let mockAdapterRegistry: any;
    let mockTaskExecutor: any;

    const mockSkill = { id: "skill-1", name: "Skill 1" };
    const mockBenchmark = { 
        id: "bench-1", 
        tasks: [{ id: "task-1", evaluator: { type: "exact" } }],
        scoringMethod: "mean"
    };

    beforeEach(() => {
        mockSkillStore = {
            loadDir: vi.fn().mockReturnValue([mockSkill]),
            register: vi.fn(),
        };
        mockBenchmarkRegistry = {
            get: vi.fn().mockReturnValue(mockBenchmark),
            loadFromFile: vi.fn().mockReturnValue(mockBenchmark),
        };
        mockAdapterRegistry = {
            resolveForSkill: vi.fn(),
        };
        mockTaskExecutor = {
            execute: vi.fn().mockResolvedValue([]),
            on: vi.fn(),
        };

        (SkillStore as any).mockImplementation(() => mockSkillStore);
        (BenchmarkRegistry as any).mockImplementation(() => mockBenchmarkRegistry);
        (AdapterRegistry as any).mockImplementation(() => mockAdapterRegistry);
        (TaskExecutor as any).mockImplementation(() => mockTaskExecutor);

        engine = new EvaluationEngine();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it("should load skills and execute evaluation", async () => {
        (fs.existsSync as any).mockReturnValue(true);
        (fs.statSync as any).mockReturnValue({ isDirectory: () => true });
        
        mockTaskExecutor.execute.mockResolvedValue([
            { skillId: "skill-1", taskId: "task-1", status: "pass", score: 1.0, latencyMs: 10 }
        ]);

        const reports = await engine.evaluate({
            skillPaths: ["./skills"],
            benchmark: "bench-1"
        });

        expect(reports).toHaveLength(1);
        expect(reports[0].skillId).toBe("skill-1");
        expect(reports[0].summary.completionRate).toBe(1.0);
        expect(mockTaskExecutor.execute).toHaveBeenCalled();
    });

    it("should throw if no skills found", async () => {
        mockSkillStore.loadDir.mockReturnValue([]);
        (fs.existsSync as any).mockReturnValue(true);
        (fs.statSync as any).mockReturnValue({ isDirectory: () => true });

        await expect(engine.evaluate({
            skillPaths: ["./empty"],
            benchmark: "bench-1"
        })).rejects.toThrow("No skills found");
    });

    it("should aggregate task scores correctly", async () => {
        (fs.existsSync as any).mockReturnValue(true);
        (fs.statSync as any).mockReturnValue({ isDirectory: () => true });
        
        mockTaskExecutor.execute.mockResolvedValue([
            { skillId: "skill-1", taskId: "task-1", status: "pass", score: 1.0, latencyMs: 10 },
            { skillId: "skill-1", taskId: "task-2", status: "fail", score: 0.0, latencyMs: 10 }
        ]);
        
        // Update mock benchmark to have 2 tasks
        mockBenchmarkRegistry.get.mockReturnValue({
            ...mockBenchmark,
            tasks: [
                { id: "task-1", evaluator: { type: "exact" } },
                { id: "task-2", evaluator: { type: "exact" } }
            ]
        });

        const reports = await engine.evaluate({
            skillPaths: ["./skills"],
            benchmark: "bench-1"
        });

        expect(reports[0].summary.completionRate).toBe(0.5);
        expect(reports[0].summary.partialScore).toBe(0.5);
    });

    it("should respect concurrency limit config", async () => {
        (fs.existsSync as any).mockReturnValue(true);
        (fs.statSync as any).mockReturnValue({ isDirectory: () => true });

        await engine.evaluate({
            skillPaths: ["./skills"],
            benchmark: "bench-1",
            concurrency: 5
        });

        expect(TaskExecutor).toHaveBeenCalledWith(expect.objectContaining({
            concurrency: 5
        }));
    });
});
