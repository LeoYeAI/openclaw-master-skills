import { describe, it, expect, vi, beforeEach } from "vitest";
import { OnDemandEvaluator, OnDemandConfig } from "./OnDemandEvaluator.js";
import { TaskExecutor } from "./TaskExecutor.js";
import * as fs from "node:fs";

// Mock dependencies
vi.mock("node:fs");
vi.mock("./TaskExecutor.js");

describe("OnDemandEvaluator", () => {
    let evaluator: OnDemandEvaluator;
    const mockTaskExecutor = {
        execute: vi.fn(),
        on: vi.fn(),
    };

    beforeEach(() => {
        evaluator = new OnDemandEvaluator();
        (TaskExecutor as any).mockImplementation(() => mockTaskExecutor);
        vi.clearAllMocks();
    });

    it("should evaluate with regex strategy", async () => {
        const skillJson = JSON.stringify({
            id: "test-skill",
            adapterType: "http",
            entrypoint: "http://localhost",
        });
        (fs.existsSync as any).mockReturnValue(true);
        (fs.statSync as any).mockReturnValue({ isDirectory: () => false });
        (fs.readFileSync as any).mockReturnValue(skillJson);
        // path.resolve mock is tricky, let's assume it returns input for simple cases or mock it if needed
        // But we are mocking fs.existsSync so it should be fine if we mock it to return true for whatever path

        mockTaskExecutor.execute.mockResolvedValue([{
            taskId: "task-1",
            skillId: "test-skill",
            status: "pass",
            score: 1.0,
            latencyMs: 100,
            scorerType: "regex",
        }]);

        const config: OnDemandConfig = {
            skillPath: "skill.json",
            input: { msg: "hello" },
            scoringStrategy: {
                type: "regex",
                patterns: ["hello"]
            }
        };

        const result = await evaluator.evaluate(config);

        expect(result.score).toBe(1.0);
        expect(result.status).toBe("pass");
        expect(mockTaskExecutor.execute).toHaveBeenCalled();
        
        // Verify task construction
        const callArgs = mockTaskExecutor.execute.mock.calls[0];
        const items = callArgs[0];
        expect(items[0].task.evaluator.type).toBe("regex");
        expect(items[0].task.expectedOutput.patterns).toEqual(["hello"]);
    });
});
