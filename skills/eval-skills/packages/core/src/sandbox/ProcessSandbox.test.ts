import { describe, it, expect } from "vitest";
import { ProcessSandbox } from "./ProcessSandbox.js";
import { DEFAULT_SANDBOX_CONFIG, SandboxConfig } from "./types.js";
import * as path from "node:path";
import * as os from "node:os";
import * as fs from "node:fs";

describe("ProcessSandbox", () => {
  const tmpDir = os.tmpdir();
  const testConfig: SandboxConfig = {
    ...DEFAULT_SANDBOX_CONFIG,
    runtime: "process",
    filesystem: {
        ...DEFAULT_SANDBOX_CONFIG.filesystem,
        allowPaths: [tmpDir] // Allow access to tmp dir for testing if needed
    }
  };

  // Track created files for cleanup
  const createdFiles: string[] = [];
  
  function createScript(name: string, content: string): string {
      const p = path.join(tmpDir, name);
      fs.writeFileSync(p, content);
      createdFiles.push(p);
      return p;
  }

  afterEach(() => {
      for (const p of createdFiles) {
          try {
              if (fs.existsSync(p)) fs.unlinkSync(p);
          } catch {}
      }
      createdFiles.length = 0;
  });

  it("should execute a simple command successfully", async () => {
    const scriptPath = createScript("test-success.js", "console.log('hello sandbox')");

    const sandbox = new ProcessSandbox(testConfig);
    const result = await sandbox.execute(
      `node ${scriptPath}`,
      tmpDir,
      { jsonrpc: "2.0", method: "test", params: {}, id: 1 }
    );
    if (!result.success) {
        console.error("Execution failed:", result.error);
        console.error("Stdout:", result.stdout);
        console.error("Stderr:", result.stderr);
    }

    expect(result.success).toBe(true);
    expect(result.stdout).toContain("hello sandbox");
    expect(result.exitCode).toBe(0);
  });

  it("should handle timeout", async () => {
    const scriptPath = createScript("test-timeout.js", "setTimeout(() => {}, 2000);");

    const configWithTimeout = {
        ...testConfig,
        resources: {
            ...testConfig.resources,
            hardTimeoutMs: 100 // Short timeout
        }
    };
    const sandbox = new ProcessSandbox(configWithTimeout);
    const result = await sandbox.execute(
      `node ${scriptPath}`,
      tmpDir,
      { jsonrpc: "2.0", method: "test", params: {}, id: 1 }
    );

    expect(result.success).toBe(false);
    expect(result.timedOut).toBe(true);
    expect(result.error).toContain("timed out");
  });

  it("should block disallowed executables", async () => {
    // perl is not in the allowed list
    const scriptPath = createScript("test.pl", "print 1;");

    const sandbox = new ProcessSandbox(testConfig);
    const result = await sandbox.execute(
      `perl ${scriptPath}`,
      tmpDir,
      { jsonrpc: "2.0", method: "test", params: {}, id: 1 }
    );

    expect(result.success).toBe(false);
    expect(result.error).toContain("not allowed");
  });

  it("should truncate output", async () => {
      const scriptPath = createScript("test-truncate.js", "console.log('123456789012345')");

      const configWithLimit = {
          ...testConfig,
          resources: {
              ...testConfig.resources,
              maxOutputBytes: 10 // Very small limit
          }
      };
      const sandbox = new ProcessSandbox(configWithLimit);
      const result = await sandbox.execute(
        `node ${scriptPath}`,
        tmpDir,
        { jsonrpc: "2.0", method: "test", params: {}, id: 1 }
      );
  
      expect(result.outputTruncated).toBe(true);
  });
});
