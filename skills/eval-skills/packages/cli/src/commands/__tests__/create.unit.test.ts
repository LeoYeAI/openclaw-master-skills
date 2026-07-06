import { describe, it, expect, vi, beforeEach } from "vitest";
import { registerCreateCommand } from "../create.js";
import { Command } from "commander";
import { SkillCreator } from "@eval-skills/core";
import { log } from "../../utils/output.js";

vi.mock("@eval-skills/core");
vi.mock("../../utils/output.js", () => ({
  log: {
    success: vi.fn(),
    info: vi.fn(),
    dim: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock process.exit
const mockExit = vi.spyOn(process, "exit").mockImplementation((code) => {
  throw new Error(`process.exit(${code})`);
});

describe("create command", () => {
  let program: Command;

  beforeEach(() => {
    vi.clearAllMocks();
    program = new Command();
  });

  it("should register create command", () => {
    registerCreateCommand(program);
    const cmd = program.commands.find((c) => c.name() === "create");
    expect(cmd).toBeDefined();
  });

  it("should create skill with template", async () => {
    let actionHandler: any;
    const originalCommand = program.command.bind(program);
    vi.spyOn(program, "command").mockImplementation((name) => {
        const cmd = originalCommand(name);
        vi.spyOn(cmd, "action").mockImplementation((fn) => {
            actionHandler = fn;
            return cmd;
        });
        return cmd;
    });

    registerCreateCommand(program);
    
    (SkillCreator.create as any).mockResolvedValue({
        skillDir: "/path/to/skill",
        files: ["skill.json"],
    });

    await actionHandler({
        name: "test-skill",
        fromTemplate: "python_script",
        outputDir: "./skills",
        description: "A test skill",
    });

    expect(SkillCreator.create).toHaveBeenCalledWith({
        name: "test-skill",
        template: "python_script",
        outputDir: "./skills",
        description: "A test skill",
        openapiSpec: undefined,
    });
    
    expect(log.success).toHaveBeenCalled();
  });

  it("should handle creation error", async () => {
    let actionHandler: any;
    const originalCommand = program.command.bind(program);
    vi.spyOn(program, "command").mockImplementation((name) => {
        const cmd = originalCommand(name);
        vi.spyOn(cmd, "action").mockImplementation((fn) => {
            actionHandler = fn;
            return cmd;
        });
        return cmd;
    });

    registerCreateCommand(program);
    
    (SkillCreator.create as any).mockRejectedValue(new Error("Create failed"));
    
    await expect(actionHandler({ name: "test" }))
        .rejects.toThrow("process.exit(1)");
        
    expect(log.error).toHaveBeenCalledWith("Create failed");
  });
});
