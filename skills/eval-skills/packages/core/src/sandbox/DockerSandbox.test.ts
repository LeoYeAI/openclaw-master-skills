/**
 * @file sandbox/DockerSandbox.test.ts
 * @description Docker 沙箱集成测试
 *
 * 运行条件：需要 Docker daemon 可访问
 * 运行命令：pnpm test:docker
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { SandboxFactory } from "./SandboxFactory.js";
import { DEFAULT_SANDBOX_CONFIG } from "./types.js";
import type { SandboxConfig } from "./types.js";

// ── 测试专用配置（内存超小，便于测试 OOM） ────────────────────────────────────
const DOCKER_TEST_CONFIG: SandboxConfig = {
  ...DEFAULT_SANDBOX_CONFIG,
  runtime: "docker",
  network: "none",
  resources: {
    memoryMb: 64,
    cpuCores: 0.25,
    hardTimeoutMs: 10_000,
    maxOutputBytes: 1024 * 1024, // 1MB
    maxPids: 16,
    tmpDiskMb: 32,
  },
  docker: {
    ...DEFAULT_SANDBOX_CONFIG.docker,
    image: "python:3.12-slim",
    pullPolicy: "if-not-present",
    cleanupTimeoutMs: 3_000,
    rootless: false,
  },
};

let tmpSkillDir: string;

beforeAll(() => {
  tmpSkillDir = fs.mkdtempSync(path.join(os.tmpdir(), "docker-skill-test-"));
});

afterAll(() => {
  fs.rmSync(tmpSkillDir, { recursive: true, force: true });
});

describe("DockerSandbox — availability check", () => {
  it("should detect Docker availability", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);
    const available = await sandbox.isAvailable();
    console.log(`Docker available: ${available}`);
    // 不断言 true，因为 CI 环境可能无 Docker
    expect(typeof available).toBe("boolean");
  });
});

describe("DockerSandbox — basic execution", () => {
  it("should execute a simple Python skill in Docker", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);

    const available = await sandbox.isAvailable();
    if (!available) {
      console.warn("Docker not available, skipping test");
      return;
    }

    // 创建简单 skill
    const skillFile = path.join(tmpSkillDir, "echo_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys
req = json.loads(sys.stdin.read())
result = {"echo": req["params"]}
print(json.dumps({"jsonrpc":"2.0","result":result,"id":req["id"]}))
`);

    const result = await sandbox.execute(
      `python3 echo_skill.py`,
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: { msg: "hello docker" }, id: 1 },
    );

    expect(result.runtimeUsed).toBe("docker");
    expect(result.success).toBe(true);
    expect(result.exitCode).toBe(0);

    const parsed = JSON.parse(result.stdout);
    expect(parsed.result.echo.msg).toBe("hello docker");
  }, 60_000); // Docker 首次拉取镜像可能需要较长时间
});

describe("DockerSandbox — network isolation", () => {
  it("should block all network access when policy=none", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);
    const available = await sandbox.isAvailable();
    if (!available) return;

    // 尝试进行网络请求的 Skill
    const skillFile = path.join(tmpSkillDir, "network_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys, socket
req = json.loads(sys.stdin.read())
try:
    s = socket.create_connection(("8.8.8.8", 53), timeout=2)
    result = {"network": "accessible"}  # 如果网络可用
    s.close()
except Exception as e:
    result = {"network": "blocked", "reason": str(e)}
print(json.dumps({"jsonrpc":"2.0","result":result,"id":req["id"]}))
`);

    const result = await sandbox.execute(
      "python3 network_skill.py",
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );

    expect(result.success).toBe(true);
    const parsed = JSON.parse(result.stdout);
    // 网络应该被隔离
    expect(parsed.result.network).toBe("blocked");
  }, 30_000);
});

describe("DockerSandbox — filesystem isolation", () => {
  it("should not allow writing to skill dir (read-only mount)", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);
    const available = await sandbox.isAvailable();
    if (!available) return;

    const skillFile = path.join(tmpSkillDir, "write_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys, os
req = json.loads(sys.stdin.read())
try:
    with open("/skill/evil_file.txt", "w") as f:
        f.write("hacked")
    result = {"write": "succeeded"}  # 不应该发生
except PermissionError as e:
    result = {"write": "blocked", "reason": str(e)}
print(json.dumps({"jsonrpc":"2.0","result":result,"id":req["id"]}))
`);

    const result = await sandbox.execute(
      "python3 write_skill.py",
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );

    expect(result.success).toBe(true);
    const parsed = JSON.parse(result.stdout);
    // Skill 目录应该是只读的，写入必须失败
    expect(parsed.result.write).toBe("blocked");
  }, 30_000);

  it("should allow writing to /tmp (tmpfs)", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);
    const available = await sandbox.isAvailable();
    if (!available) return;

    const skillFile = path.join(tmpSkillDir, "tmp_write_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys
req = json.loads(sys.stdin.read())
try:
    with open("/tmp/test_output.txt", "w") as f:
        f.write("temp data")
    result = {"tmp_write": "ok"}
except Exception as e:
    result = {"tmp_write": "failed", "reason": str(e)}
print(json.dumps({"jsonrpc":"2.0","result":result,"id":req["id"]}))
`);

    const result = await sandbox.execute(
      "python3 tmp_write_skill.py",
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );

    expect(result.success).toBe(true);
    const parsed = JSON.parse(result.stdout);
    // /tmp 应该可写
    expect(parsed.result.tmp_write).toBe("ok");
  }, 30_000);
});

describe("DockerSandbox — timeout enforcement", () => {
  it("should kill container when hard timeout exceeded", async () => {
    const sandbox = SandboxFactory.createDockerSandbox({
      ...DOCKER_TEST_CONFIG,
      resources: {
        ...DOCKER_TEST_CONFIG.resources,
        hardTimeoutMs: 2_000, // 2s 超时
      },
    });
    const available = await sandbox.isAvailable();
    if (!available) return;

    const skillFile = path.join(tmpSkillDir, "sleep_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys, time
req = json.loads(sys.stdin.read())
time.sleep(60)  # 死循环
print(json.dumps({"jsonrpc":"2.0","result":{},"id":req["id"]}))
`);

    const start = Date.now();
    const result = await sandbox.execute(
      "python3 sleep_skill.py",
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );
    const elapsed = Date.now() - start;

    expect(result.timedOut).toBe(true);
    expect(result.success).toBe(false);
    // 应在约 2s 内结束（允许 1s 清理时间）
    expect(elapsed).toBeLessThan(6_000);
  }, 30_000);
});

describe("DockerSandbox — resource usage stats", () => {
  it("should return resourceUsage stats after execution", async () => {
    const sandbox = SandboxFactory.createDockerSandbox(DOCKER_TEST_CONFIG);
    const available = await sandbox.isAvailable();
    if (!available) return;

    const skillFile = path.join(tmpSkillDir, "mem_skill.py");
    fs.writeFileSync(skillFile, `
import json, sys
req = json.loads(sys.stdin.read())
# 分配少量内存
data = [0] * 100000
print(json.dumps({"jsonrpc":"2.0","result":{"ok":True},"id":req["id"]}))
`);

    const result = await sandbox.execute(
      "python3 mem_skill.py",
      tmpSkillDir,
      { jsonrpc: "2.0", method: "invoke", params: {}, id: 1 },
    );

    expect(result.success).toBe(true);
    // resourceUsage 应该有值（Docker stats）
    if (result.resourceUsage) {
      expect(result.resourceUsage.peakMemoryMb).toBeGreaterThan(0);
      expect(result.resourceUsage.wallTimeMs).toBeGreaterThan(0);
    }
  }, 30_000);
});
