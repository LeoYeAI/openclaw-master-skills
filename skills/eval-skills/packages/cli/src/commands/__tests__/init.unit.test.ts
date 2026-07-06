import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { registerInitCommand } from "../init.js";
import { Command } from "commander";
import * as fs from "node:fs";
import { log } from "../../utils/output.js";

vi.mock("node:fs");
vi.mock("../../utils/output.js", () => ({
  log: {
    success: vi.fn(),
    dim: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock process.exit
const mockExit = vi.spyOn(process, "exit").mockImplementation((code) => {
  throw new Error(`process.exit(${code})`);
});

describe("init command", () => {
  let program: Command;

  beforeEach(() => {
    vi.clearAllMocks();
    program = new Command();
  });

  it("should register init command", () => {
    registerInitCommand(program);
    const cmd = program.commands.find((c) => c.name() === "init");
    expect(cmd).toBeDefined();
  });

  it("should create config and directories if not exist", () => {
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

    registerInitCommand(program);
    
    // Simulate fs
    (fs.existsSync as any).mockReturnValue(false);
    
    // Trigger action
    actionHandler({ dir: "." });
    
    expect(fs.writeFileSync).toHaveBeenCalledWith(expect.stringContaining("eval-skills.config.yaml"), expect.any(String), "utf-8");
    expect(fs.mkdirSync).toHaveBeenCalledTimes(3); // skills, benchmarks, reports
    expect(log.success).toHaveBeenCalled();
  });

  it("should skip existing config and directories", () => {
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

    registerInitCommand(program);
    
    (fs.existsSync as any).mockReturnValue(true);
    
    actionHandler({ dir: "." });
    
    expect(fs.writeFileSync).not.toHaveBeenCalled();
    expect(fs.mkdirSync).not.toHaveBeenCalled();
    expect(log.dim).toHaveBeenCalled();
  });

  it("should handle errors", () => {
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

    registerInitCommand(program);
    
    (fs.existsSync as any).mockImplementation(() => {
        throw new Error("FS Error");
    });
    
    expect(() => actionHandler({ dir: "." })).toThrow("process.exit(1)");
    expect(log.error).toHaveBeenCalledWith("FS Error");
  });
});
