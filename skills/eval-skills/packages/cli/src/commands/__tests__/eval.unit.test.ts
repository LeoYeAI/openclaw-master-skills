import { describe, it, expect, vi, beforeEach } from "vitest";
import { registerEvalCommand } from "../eval.js";
import { Command } from "commander";
import { EvaluationEngine, SkillStore, SqliteStore, BenchmarkRegistry } from "@eval-skills/core";

vi.mock("ora", () => ({
    default: vi.fn().mockReturnValue({
        start: vi.fn().mockReturnThis(),
        succeed: vi.fn(),
        fail: vi.fn(),
        text: "",
    }),
}));

vi.mock("@eval-skills/core");
vi.mock("../../utils/config.js", () => ({
    loadGlobalConfig: vi.fn().mockReturnValue({}),
    buildEvalConfig: vi.fn().mockReturnValue({ 
        output: { dir: "out", formats: [] },
        dryRun: true,
        skillPaths: ["s1"],
        benchmark: "b1",
        concurrency: 1,
        timeoutMs: 1000
    }),
}));
vi.mock("../../utils/output.js", () => ({
    log: { info: vi.fn(), error: vi.fn() },
    spinner: { start: vi.fn(), succeed: vi.fn(), fail: vi.fn() },
}));
vi.mock("../../utils/reportWriter.js", () => ({
    writeReports: vi.fn().mockResolvedValue([]),
}));

// Mock process.exit
const mockExit = vi.spyOn(process, "exit").mockImplementation((code) => {
  throw new Error(`process.exit(${code})`);
});

describe("eval command", () => {
  let program: Command;
  let mockEngine: any;

  beforeEach(() => {
    vi.clearAllMocks();
    program = new Command();
    mockEngine = {
        evaluate: vi.fn().mockResolvedValue([]),
        on: vi.fn(),
    };
    (EvaluationEngine as any).mockImplementation(() => mockEngine);
    (SkillStore as any).mockImplementation(() => ({
        loadSkills: vi.fn().mockResolvedValue([{ id: "s1" }]),
    }));
    (SqliteStore as any).mockImplementation(() => ({
        close: vi.fn(),
    }));
    (BenchmarkRegistry as any).mockImplementation(() => ({
        loadBuiltins: vi.fn(),
    }));
    
    // Mock SqliteStore
    // It is imported from @eval-skills/core, which is already mocked.
    // But we need to ensure constructor works.
  });

  it("should register eval command", () => {
    registerEvalCommand(program);
    const cmd = program.commands.find((c) => c.name() === "eval");
    expect(cmd).toBeDefined();
  });

  it.skip("should run evaluation when action is triggered", async () => {
    let actionHandler: any;
    
    // Spy on command definition to capture action
    const originalCommand = program.command.bind(program);
    vi.spyOn(program, "command").mockImplementation((name) => {
        const cmd = originalCommand(name);
        vi.spyOn(cmd, "action").mockImplementation((fn) => {
            actionHandler = fn;
            return cmd;
        });
        return cmd;
    });

    registerEvalCommand(program);
    
    expect(actionHandler).toBeDefined();
    
    // Simulate action
    await actionHandler({ skills: ["s1"], benchmark: "b1" });
    
    expect(EvaluationEngine).toHaveBeenCalled();
    expect(mockEngine.evaluate).toHaveBeenCalled();
  });
});
