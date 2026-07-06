import { TaskExecutor } from "./TaskExecutor.js";
import type { TaskItem, Task, Skill } from "../types/index.js";
import type { SkillAdapter, AdapterResponse } from "../types/index.js";
import type { Scorer, ScorerResult } from "./scorers/BaseScorer.js";
import { describe, it, expect, vi } from "vitest";

// Mock Adapter
const mockAdapter: SkillAdapter = {
  type: "http",
  invoke: vi.fn().mockResolvedValue({
    success: true,
    output: "result",
    latencyMs: 10,
  } as AdapterResponse),
  healthCheck: vi.fn(),
};

// Mock Scorer
const mockScorer: Scorer = {
  type: "exact",
  score: vi.fn().mockResolvedValue({
    passed: true,
    score: 1.0,
  } as ScorerResult),
};

const mockSkill: Skill = {
  id: "s1",
  name: "Skill 1",
  version: "1.0",
  description: "desc",
  tags: [],
  adapterType: "http",
  entrypoint: "url",
  inputSchema: {},
  outputSchema: {},
  metadata: {},
};

const mockTask: Task = {
  id: "t1",
  description: "task",
  inputData: {},
  expectedOutput: { type: "exact", value: "result" },
  evaluator: { type: "exact" },
};

describe("TaskExecutor", () => {
  it("should execute tasks and return results", async () => {
    const executor = new TaskExecutor({ concurrency: 2 });
    const items: TaskItem[] = [{ skill: mockSkill, task: mockTask }];

    const results = await executor.execute(
      items,
      () => mockAdapter,
      () => mockScorer,
    );

    expect(results).toHaveLength(1);
    expect(results[0].status).toBe("pass");
    expect(results[0].score).toBe(1.0);
    expect(mockAdapter.invoke).toHaveBeenCalled();
    expect(mockScorer.score).toHaveBeenCalled();
  });

  it("should handle adapter failure", async () => {
    const executor = new TaskExecutor();
    const failureAdapter = {
      ...mockAdapter,
      invoke: vi.fn().mockResolvedValue({
        success: false,
        error: "Failed",
        latencyMs: 5,
      } as AdapterResponse),
    };

    const items: TaskItem[] = [{ skill: mockSkill, task: mockTask }];
    const results = await executor.execute(
      items,
      () => failureAdapter,
      () => mockScorer,
    );

    expect(results[0].status).toBe("error");
    expect(results[0].error).toBe("Failed");
  });

  it("should emit progress events", async () => {
    const executor = new TaskExecutor();
    const items: TaskItem[] = [
      { skill: mockSkill, task: mockTask },
      { skill: mockSkill, task: { ...mockTask, id: "t2" } },
    ];

    const progressSpy = vi.fn();
    executor.on("progress", progressSpy);

    await executor.execute(items, () => mockAdapter, () => mockScorer);

    expect(progressSpy).toHaveBeenCalledTimes(2);
    expect(progressSpy).toHaveBeenLastCalledWith(expect.objectContaining({
        completed: 2,
        total: 2,
        percent: 100
    }));
  });
});
