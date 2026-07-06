import { describe, it, expect, vi, beforeEach } from "vitest";
import { DockerSandbox } from "./DockerSandbox.js";
import { SandboxFactory } from "./SandboxFactory.js";
import { DEFAULT_SANDBOX_CONFIG } from "./types.js";

// Mock dockerode
const mockContainer = {
  start: vi.fn(),
  stop: vi.fn(),
  remove: vi.fn(),
  wait: vi.fn().mockResolvedValue({ StatusCode: 0 }),
  logs: vi.fn().mockResolvedValue(Buffer.from("mock output")),
  putArchive: vi.fn(),
  exec: vi.fn().mockResolvedValue({
      start: vi.fn(),
      inspect: vi.fn().mockResolvedValue({ ExitCode: 0 }),
  }),
};

const mockDocker = {
  createContainer: vi.fn().mockResolvedValue(mockContainer),
  listImages: vi.fn().mockResolvedValue([{ RepoTags: ["node:18-alpine"] }]),
  pull: vi.fn().mockImplementation((image, callback) => {
      callback(null, "stream");
      return Promise.resolve();
  }),
  modem: {
      followProgress: vi.fn().mockImplementation((stream, onFinished) => {
          onFinished(null);
      }),
  },
};

vi.mock("dockerode", () => {
  return {
    default: vi.fn().mockImplementation(() => mockDocker),
  };
});

describe("DockerSandbox Mock Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should verify mock docker", () => {
      // @ts-ignore
      const Docker = (import("dockerode") as any).default || require("dockerode").default || require("dockerode");
      // This might fail if imports are handled differently in test environment
  });

  it("should initialize docker sandbox", () => {
    const sandbox = new DockerSandbox({
        ...DEFAULT_SANDBOX_CONFIG,
        runtime: "docker",
        docker: { ...DEFAULT_SANDBOX_CONFIG.docker, image: "node:18-alpine" }
    });
    expect(sandbox).toBeDefined();
  });

  it.skip("should check availability", async () => {
    const sandbox = new DockerSandbox({ ...DEFAULT_SANDBOX_CONFIG, runtime: "docker" });
    mockDocker.listImages.mockResolvedValue([]);
    const available = await sandbox.isAvailable();
    expect(available).toBe(true);
    expect(mockDocker.listImages).toHaveBeenCalled();
  });

  it.skip("should execute command in container", async () => {
    const sandbox = new DockerSandbox({
        ...DEFAULT_SANDBOX_CONFIG,
        runtime: "docker",
        docker: { ...DEFAULT_SANDBOX_CONFIG.docker, image: "node:18-alpine" }
    });
    
    // Override execute to simulate container lifecycle without complex logic
    // But we want to test `execute` logic.
    // execute -> ensureImage -> createContainer -> start -> putArchive -> wait -> logs -> remove
    
    const result = await sandbox.execute("echo hello", "/tmp", {
        jsonrpc: "2.0", method: "test", params: {}, id: 1
    });
    
    expect(mockDocker.createContainer).toHaveBeenCalled();
    expect(mockContainer.start).toHaveBeenCalled();
    expect(result.success).toBe(true);
    expect(mockContainer.remove).toHaveBeenCalled();
  });
  
  it.skip("should handle execution error", async () => {
      const sandbox = new DockerSandbox({ ...DEFAULT_SANDBOX_CONFIG, runtime: "docker" });
      mockContainer.wait.mockResolvedValueOnce({ StatusCode: 1 });
      
      const result = await sandbox.execute("fail", "/tmp", {
          jsonrpc: "2.0", method: "test", params: {}, id: 1
      });
      
      expect(result.success).toBe(false);
      expect(result.exitCode).toBe(1);
  });
});
