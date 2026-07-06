import { describe, it, expect, vi, beforeEach } from "vitest";
import { SubprocessAdapter } from "./SubprocessAdapter.js";
import { SandboxFactory } from "../sandbox/SandboxFactory.js";
import type { SandboxExecutor, SandboxResult } from "../sandbox/types.js";

// Mock SandboxFactory
vi.mock("../sandbox/SandboxFactory.js");

const mockSkill = {
  id: "test-skill",
  name: "Test Skill",
  adapterType: "subprocess",
  entrypoint: "python skill.py",
  inputSchema: {},
  outputSchema: {},
  metadata: {},
};

describe("SubprocessAdapter with Mock Sandbox", () => {
  let adapter: SubprocessAdapter;
  let mockExecutor: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Create a mock executor
    mockExecutor = {
      execute: vi.fn(),
    };

    // Mock factory to return our mock executor
    (SandboxFactory as any).prototype.createExecutor = vi.fn().mockResolvedValue(mockExecutor);

    adapter = new SubprocessAdapter();
  });

  it("should create sandbox and execute request", async () => {
    // Setup successful execution
    mockExecutor.execute.mockResolvedValue({
      success: true,
      stdout: JSON.stringify({ jsonrpc: "2.0", result: "success", id: 1 }),
      stderr: "",
      exitCode: 0,
    } as SandboxResult);

    const result = await adapter.invoke(mockSkill, { key: "value" });

    expect(SandboxFactory.prototype.createExecutor).toHaveBeenCalled();
    expect(mockExecutor.execute).toHaveBeenCalledWith(
      "python skill.py",
      expect.any(String), // CWD
      expect.objectContaining({
        jsonrpc: "2.0",
        method: "invoke",
        params: { key: "value" },
      }),
      expect.any(AbortSignal)
    );

    expect(result.success).toBe(true);
    expect(result.output).toBe("success");
  });

  it("should handle sandbox execution failure", async () => {
    mockExecutor.execute.mockResolvedValue({
      success: false,
      stdout: "",
      stderr: "Process failed",
      exitCode: 1,
      error: "Command failed",
    } as SandboxResult);

    const result = await adapter.invoke(mockSkill, {});
    expect(result.success).toBe(false);
    expect(result.error).toContain("Sandbox execution failed");
    expect(result.error).toContain("Process failed");
  });

  it("should handle JSON-RPC error response", async () => {
    mockExecutor.execute.mockResolvedValue({
      success: true,
      stdout: JSON.stringify({
        jsonrpc: "2.0",
        error: { code: -32600, message: "Invalid Request" },
        id: 1,
      }),
      stderr: "",
      exitCode: 0,
    } as SandboxResult);

    const result = await adapter.invoke(mockSkill, {});

    expect(result.success).toBe(false);
    expect(result.error).toContain("JSON-RPC error -32600");
  });

  it("should parse JSON-RPC from mixed output", async () => {
    const mixedOutput = `
      Some logs
      Debug info
      {"jsonrpc": "2.0", "result": "found it", "id": 1}
      More logs
    `;

    mockExecutor.execute.mockResolvedValue({
      success: true,
      stdout: mixedOutput,
      stderr: "",
      exitCode: 0,
    } as SandboxResult);

    const result = await adapter.invoke(mockSkill, {});

    expect(result.success).toBe(true);
    expect(result.output).toBe("found it");
  });

  it("should fail if no valid JSON-RPC found", async () => {
    mockExecutor.execute.mockResolvedValue({
      success: true,
      stdout: "Just logs, no json",
      stderr: "",
      exitCode: 0,
    } as SandboxResult);

    const result = await adapter.invoke(mockSkill, {});
    expect(result.success).toBe(false);
    expect(result.error).toContain("Failed to find valid JSON-RPC response");
  });

  it("should perform health check", async () => {
    mockExecutor.execute.mockResolvedValue({
      success: true,
      stdout: JSON.stringify({ jsonrpc: "2.0", result: "ok", id: 0 }),
      stderr: "",
      exitCode: 0,
    } as SandboxResult);

    const result = await adapter.healthCheck(mockSkill);

    expect(mockExecutor.execute).toHaveBeenCalledWith(
      expect.any(String),
      expect.any(String),
      expect.objectContaining({ method: "healthcheck" }),
      expect.any(AbortSignal)
    );
    expect(result.healthy).toBe(true);
  });

  it("should handle health check failure", async () => {
    mockExecutor.execute.mockResolvedValue({
      success: false,
      stdout: "",
      stderr: "Crash",
      exitCode: 1,
    } as SandboxResult);

    const result = await adapter.healthCheck(mockSkill);
    expect(result.healthy).toBe(false);
  });
});
