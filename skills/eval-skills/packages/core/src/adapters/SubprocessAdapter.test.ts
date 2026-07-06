import { SubprocessAdapter } from "./SubprocessAdapter.js";
import type { Skill } from "../types/index.js";
import { describe, it, expect, vi, afterEach } from "vitest";
import { spawn } from "node:child_process";
import { EventEmitter } from "node:events";

// Mock spawn
vi.mock("node:child_process", () => ({
  spawn: vi.fn(),
}));

const mockSkill: Skill = {
  id: "cli-skill",
  name: "CLI Skill",
  version: "1.0",
  description: "desc",
  tags: [],
  adapterType: "subprocess",
  entrypoint: "node script.js",
  inputSchema: {},
  outputSchema: {},
  metadata: {},
};

describe("SubprocessAdapter", () => {
  const adapter = new SubprocessAdapter();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it.skip("should spawn process and handle JSON-RPC response", async () => {
    const mockChild = new EventEmitter() as any;
    mockChild.stdin = { write: vi.fn(), end: vi.fn() };
    mockChild.stdout = new EventEmitter();
    mockChild.stderr = new EventEmitter();
    mockChild.kill = vi.fn();

    (spawn as any).mockReturnValue(mockChild);

    const promise = adapter.invoke(mockSkill, { input: "test" });

    // Simulate stdout data
    const response = { jsonrpc: "2.0", result: { out: "ok" }, id: 1 };
    mockChild.stdout.emit("data", Buffer.from(JSON.stringify(response)));
    mockChild.emit("close", 0);

    const result = await promise;

    expect(spawn).toHaveBeenCalledWith("node", ["script.js"], expect.any(Object));
    expect(result.success).toBe(true);
    expect(result.output).toEqual({ out: "ok" });
  });

  it.skip("should handle process error exit", async () => {
    const mockChild = new EventEmitter() as any;
    mockChild.stdin = { write: vi.fn(), end: vi.fn() };
    mockChild.stdout = new EventEmitter();
    mockChild.stderr = new EventEmitter();
    
    (spawn as any).mockReturnValue(mockChild);

    const promise = adapter.invoke(mockSkill, {});

    mockChild.stderr.emit("data", Buffer.from("Syntax Error"));
    mockChild.emit("close", 1);

    const result = await promise;
    expect(result.success).toBe(false);
    expect(result.error).toContain("exited with code 1");
    expect(result.error).toContain("Syntax Error");
  });
});
