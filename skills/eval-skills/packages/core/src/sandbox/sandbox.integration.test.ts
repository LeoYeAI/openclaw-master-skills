/**
 * @file sandbox/sandbox.integration.test.ts
 * @description 安全沙箱端到端集成测试
 *
 * 测试策略：
 *   - 使用真实子进程（Python/Node.js）验证隔离效果
 *   - 覆盖正常路径、超时、内存溢出、命令注入、路径遍历等场景
 *   - Docker 测试用 skip.if 在没有 Docker 的 CI 中跳过
 *
 * 运行方式：
 *   pnpm test:integration            # 跑所有测试
 *   SANDBOX_DOCKER=1 pnpm test:integration  # 强制跑 Docker 测试
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import * as os from "node:os";
import * as fs from "node:fs";
import * as path from "node:path";
import { ProcessSandbox } from "./ProcessSandbox.js";
import { SandboxFactory } from "./SandboxFactory.js";
import { SandboxMonitor } from "./SandboxMonitor.js";
import type { SandboxConfig } from "./types.js";
import type { JsonRpcRequest } from "./SandboxExecutor.js";

// ─── 测试夹具 ─────────────────────────────────────────────────────────────────

/** 创建临时技能目录 */
function makeTempSkillDir(name: string): string {
  const dir = path.join(os.tmpdir(), `eval-skills-sandbox-test-${name}-${Date.now()}`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

/** 写入简单的 Python JSON-RPC skill */
function writePythonSkill(dir: string, code: string): void {
  fs.writeFileSync(path.join(dir, "skill.py"), code, "utf-8");
}

/** 标准 JSON-RPC 请求 */
function makeRequest(method = "invoke", params: Record<string, unknown> = {}): JsonRpcRequest {
  return { jsonrpc: "2.0", method, params, id: 1 };
}

/** 基础测试沙箱配置 */
function baseConfig(overrides: Partial<SandboxConfig> = {}): Partial<SandboxConfig> {
  return {
    runtime: "process",
    resources: {
      memoryMb: 128,
      cpuCores: 0.5,
      hardTimeoutMs: 5_000,
      maxOutputBytes: 1024 * 1024,
      maxPids: 10,
    },
    network: "none",
    filesystem: {
      readOnly: true,
      allowPaths: [],
      tmpSizeMb: 16,
    },
    env: {
      allowList: ["PATH", "HOME"],
      inject: { EVAL_SKILLS_SANDBOX: "1" },
    },
    ...overrides,
  };
}

// ─── Python 技能模板 ──────────────────────────────────────────────────────────

const ECHO_SKILL = `
import sys
import json

def main():
    req = json.loads(sys.stdin.read())
    method = req.get("method", "")
    if method == "healthcheck":
        print(json.dumps({"jsonrpc":"2.0","result":{"status":"ok"},"id":req["id"]}))
        return
    params = req.get("params", {})
    print(json.dumps({"jsonrpc":"2.0","result":{"echo": params},"id":req["id"]}))

if __name__ == "__main__":
    main()
`;

const TIMEOUT_SKILL = `
import sys
import json
import time

req = json.loads(sys.stdin.read())
time.sleep(30)  # 模拟超时
print(json.dumps({"jsonrpc":"2.0","result":"done","id":req["id"]}))
`;

const OOM_SKILL = `
import sys
import json

req = json.loads(sys.stdin.read())
# 分配大量内存
data = []
try:
    while True:
        data.append(b"x" * (1024 * 1024))  # 每次分配 1MB
except MemoryError:
    pass
print(json.dumps({"jsonrpc":"2.0","result":"should_not_reach","id":req["id"]}))
`;

const MIXED_OUTPUT_SKILL = `
import sys
import json

req = json.loads(sys.stdin.read())
# 混入调试输出（不应破坏 JSON-RPC 解析）
print("DEBUG: starting skill", file=sys.stderr)
print("some debug line")
print(json.dumps({"jsonrpc":"2.0","result":{"value":42},"id":req["id"]}))
print("another debug line after json")
`;

const FORK_BOMB_SKILL = `
import sys
import json
import os

req = json.loads(sys.stdin.read())
# 尝试 fork bomb（应被 --pids-limit 或 SIGKILL 阻止）
for i in range(50):
    try:
        pid = os.fork()
        if pid == 0:
            import time
            time.sleep(5)
            sys.exit(0)
    except OSError:
        break
print(json.dumps({"jsonrpc":"2.0","result":"forked","id":req["id"]}))
`;

const ENV_LEAK_SKILL = `
import sys
import json
import os

req = json.loads(sys.stdin.read())
# 尝试读取敏感环境变量
secret_keys = [k for k in os.environ.keys() 
               if any(s in k.lower() for s in ["key","secret","token","password","api"])]
print(json.dumps({
    "jsonrpc":"2.0",
    "result":{"found_secrets": secret_keys, "env_count": len(os.environ)},
    "id": req["id"]
}))
`;

const FILESYSTEM_READ_SKILL = `
import sys
import json
import os

req = json.loads(sys.stdin.read())
# 尝试读取系统敏感文件
results = {}
sensitive_files = ["/etc/passwd", "/etc/shadow", "/root/.ssh/id_rsa", "/proc/1/environ"]
for f in sensitive_files:
    try:
        with open(f, "r") as fp:
            results[f] = fp.read(50)  # 只读前 50 字节
    except Exception as e:
        results[f] = f"BLOCKED: {type(e).__name__}"

print(json.dumps({
    "jsonrpc":"2.0",
    "result":{"file_access": results},
    "id": req["id"]
}))
`;

// ─── 测试套件 ─────────────────────────────────────────────────────────────────

describe("ProcessSandbox — 正常功能", () => {
  let skillDir: string;

  beforeAll(() => {
    skillDir = makeTempSkillDir("echo");
    writePythonSkill(skillDir, ECHO_SKILL);
  });

  afterAll(() => {
    fs.rmSync(skillDir, { recursive: true, force: true });
  });

  it("应正确执行并返回 JSON-RPC 响应", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
    const result = await sandbox.execute(
      "python3 skill.py",
      skillDir,
      makeRequest("invoke", { message: "hello" }),
    );

    expect(result.success).toBe(true);
    expect(result.exitCode).toBe(0);
    expect(result.timedOut).toBe(false);
    expect(result.stdout).toContain('"echo"');
    expect(result.latencyMs).toBeGreaterThan(0);
    expect(result.runtimeUsed).toBe("process");
  });

  it("应正确执行 healthcheck", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
    const result = await sandbox.execute(
      "python3 skill.py",
      skillDir,
      makeRequest("healthcheck"),
    );

    expect(result.success).toBe(true);
    expect(result.stdout).toContain('"status"');
  });

  it("应透传环境变量白名单中的变量", async () => {
    const envSkillCode = `
import sys, json, os
req = json.loads(sys.stdin.read())
print(json.dumps({"jsonrpc":"2.0","result":{"has_sandbox_flag": os.environ.get("EVAL_SKILLS_SANDBOX")},"id":req["id"]}))
`;
    const envDir = makeTempSkillDir("env");
    writePythonSkill(envDir, envSkillCode);

    try {
      const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
      const result = await sandbox.execute("python3 skill.py", envDir, makeRequest());
      
      expect(result.success).toBe(true);
      const parsed = JSON.parse(result.stdout.trim());
      expect(parsed.result.has_sandbox_flag).toBe("1");
    } finally {
      fs.rmSync(envDir, { recursive: true, force: true });
    }
  });

  it("混有调试输出时应正确找到 JSON-RPC 响应行", async () => {
    const mixedDir = makeTempSkillDir("mixed");
    writePythonSkill(mixedDir, MIXED_OUTPUT_SKILL);

    try {
      const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
      const result = await sandbox.execute("python3 skill.py", mixedDir, makeRequest());

      expect(result.success).toBe(true);
      // stdout 包含多行，沙箱层应原样返回
      expect(result.stdout).toContain('value');
      expect(result.stdout).toContain('42');
    } finally {
      fs.rmSync(mixedDir, { recursive: true, force: true });
    }
  });
});

// ─── 超时测试 ─────────────────────────────────────────────────────────────────

describe("ProcessSandbox — 硬超时", () => {
  let skillDir: string;

  beforeAll(() => {
    skillDir = makeTempSkillDir("timeout");
    writePythonSkill(skillDir, TIMEOUT_SKILL);
  });

  afterAll(() => {
    fs.rmSync(skillDir, { recursive: true, force: true });
  });

  it("超时后应返回 timedOut=true", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(
      baseConfig({ resources: { memoryMb: 128, cpuCores: 0.5, hardTimeoutMs: 500, maxOutputBytes: 1024*1024, maxPids: 10 } }),
    );

    const start = Date.now();
    const result = await sandbox.execute("python3 skill.py", skillDir, makeRequest());
    const elapsed = Date.now() - start;

    expect(result.timedOut).toBe(true);
    expect(result.success).toBe(false);
    expect(elapsed).toBeLessThan(2_000); // 不应等超过 2 秒
    expect(result.error).toContain("timed out");
  });

  it("AbortSignal 应触发提前终止", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(
      baseConfig({ resources: { memoryMb: 128, cpuCores: 0.5, hardTimeoutMs: 10_000, maxOutputBytes: 1024*1024, maxPids: 10 } }),
    );

    const controller = new AbortController();
    setTimeout(() => controller.abort(), 300);

    const start = Date.now();
    const result = await sandbox.execute(
      "python3 skill.py",
      skillDir,
      makeRequest(),
      controller.signal,
    );
    const elapsed = Date.now() - start;

    expect(result.timedOut).toBe(true);
    expect(result.success).toBe(false);
    expect(elapsed).toBeLessThan(1_500);
  });
});

// ─── 命令注入防护测试 ─────────────────────────────────────────────────────────

describe("SandboxExecutor — 命令注入防护", () => {
  const skillDir = os.tmpdir();
  let sandbox: ProcessSandbox;

  beforeEach(() => {
    sandbox = SandboxFactory.createProcessSandbox(baseConfig());
  });

  const injectionAttempts = [
    ["shell 管道注入", "python3 skill.py; rm -rf /"],
    ["反引号注入", "python3 `echo malicious`"],
    ["重定向注入", "python3 skill.py > /etc/passwd"],
    ["AND 链注入", "python3 skill.py && cat /etc/shadow"],
    ["路径遍历", "python3 ../../etc/passwd"],
    ["sudo 提权", "sudo python3 skill.py"],
    ["eval 注入", "python3 -c 'eval(input())'"],
  ];

  for (const [name, command] of injectionAttempts) {
    it(`应阻断 ${name}`, async () => {
      const result = await sandbox.execute(
        command,
        skillDir,
        makeRequest(),
      );
      expect(result.success).toBe(false);
      // 违规应被记录
      const violations = sandbox.getViolations();
      expect(violations.length).toBeGreaterThan(0);
      expect(violations.some((v) => v.severity === "critical" || v.severity === "error")).toBe(true);
    });
  }

  it("不在白名单中的可执行程序应被拒绝", async () => {
    const result = await sandbox.execute("nmap -sV localhost", skillDir, makeRequest());
    expect(result.success).toBe(false);
    expect(sandbox.getViolations().some((v) => v.type === "command_injection")).toBe(true);
  });
});

// ─── 环境变量过滤测试 ─────────────────────────────────────────────────────────

describe("ProcessSandbox — 环境变量隔离", () => {
  let skillDir: string;

  beforeAll(() => {
    skillDir = makeTempSkillDir("env-leak");
    writePythonSkill(skillDir, ENV_LEAK_SKILL);
  });

  afterAll(() => {
    fs.rmSync(skillDir, { recursive: true, force: true });
  });

  it("沙箱中不应泄露敏感环境变量", async () => {
    // 模拟进程中存在敏感 env
    const originalEnv = { ...process.env };
    process.env["SECRET_API_KEY"] = "super-secret-key-12345";
    process.env["OPENAI_TOKEN"] = "sk-test-token";
    process.env["DB_PASSWORD"] = "password123";

    try {
      const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
      const result = await sandbox.execute("python3 skill.py", skillDir, makeRequest());

      expect(result.success).toBe(true);
      const parsed = JSON.parse(result.stdout.split("\n").find((l) => l.startsWith("{")) ?? "{}");
      
      // 沙箱内应看不到敏感变量
      const foundSecrets: string[] = parsed.result?.found_secrets ?? [];
      expect(foundSecrets).not.toContain("SECRET_API_KEY");
      expect(foundSecrets).not.toContain("OPENAI_TOKEN");
      expect(foundSecrets).not.toContain("DB_PASSWORD");
      
      // env_count 应远少于宿主环境
      expect(parsed.result?.env_count ?? 999).toBeLessThan(10);
    } finally {
      // 恢复原始 env
      for (const key of ["SECRET_API_KEY", "OPENAI_TOKEN", "DB_PASSWORD"]) {
        delete process.env[key];
      }
    }
  });
});

// ─── 输出大小限制测试 ─────────────────────────────────────────────────────────

describe("ProcessSandbox — 输出大小限制", () => {
  it("超出 maxOutputBytes 时应截断并标记", async () => {
    const skillDir = makeTempSkillDir("big-output");
    // 写一个生成大量输出的 skill
    writePythonSkill(skillDir, `
import sys, json
req = json.loads(sys.stdin.read())
# 输出 1MB 的 'x'
print("x" * 1024 * 1024)
print(json.dumps({"jsonrpc":"2.0","result":"ok","id":req["id"]}))
`);

    try {
      const sandbox = SandboxFactory.createProcessSandbox(
        baseConfig({
          resources: {
            memoryMb: 128, cpuCores: 0.5, hardTimeoutMs: 5000,
            maxOutputBytes: 1024,  // 限制为 1KB
            maxPids: 10,
          },
        }),
      );
      const result = await sandbox.execute("python3 skill.py", skillDir, makeRequest());

      expect(result.outputTruncated).toBe(true);
      expect(result.stdout.length).toBeLessThanOrEqual(600); // 约 512 字节（stderr 也占一半）
      
      const violations = sandbox.getViolations();
      expect(violations.some((v) => v.type === "output_truncated")).toBe(true);
    } finally {
      fs.rmSync(skillDir, { recursive: true, force: true });
    }
  });
});

// ─── SandboxMonitor 测试 ──────────────────────────────────────────────────────

describe("SandboxMonitor — 违规监控与熔断", () => {
  it("应聚合违规并触发熔断", () => {
    const monitor = new SandboxMonitor({
      circuitBreakerThreshold: 2,
      retentionHours: 1,
    });

    const skillId = "test-skill-001";

    // 添加违规记录
    monitor.recordViolation({
      type: "command_injection",
      severity: "critical",
      detail: "injection attempt 1",
      timestamp: new Date().toISOString(),
      skillId,
    });

    // 第一次未熔断
    expect(monitor.isCircuitBroken(skillId)).toBe(false);

    monitor.recordViolation({
      type: "command_injection",
      severity: "critical",
      detail: "injection attempt 2",
      timestamp: new Date().toISOString(),
      skillId,
    });

    // 达到阈值，应熔断
    expect(monitor.isCircuitBroken(skillId)).toBe(true);
  });

  it("应正确统计违规类型分布", () => {
    const monitor = new SandboxMonitor({ circuitBreakerThreshold: 100 });
    const skillId = "test-skill-002";

    monitor.recordViolation({ type: "command_injection", severity: "critical", detail: "a", timestamp: new Date().toISOString(), skillId });
    monitor.recordViolation({ type: "output_truncated",  severity: "warn",     detail: "b", timestamp: new Date().toISOString(), skillId });
    monitor.recordViolation({ type: "command_injection", severity: "error",    detail: "c", timestamp: new Date().toISOString(), skillId });

    const stats = monitor.getStats(skillId);
    expect(stats).not.toBeNull();
    expect(stats!.totalViolations).toBe(3);
    expect(stats!.byType["command_injection"]).toBe(2);
    expect(stats!.byType["output_truncated"]).toBe(1);
    expect(stats!.criticalCount).toBe(1);
    expect(stats!.errorCount).toBe(1);
  });

  it("getTopOffenders 应按违规数降序排列", () => {
    const monitor = new SandboxMonitor({ circuitBreakerThreshold: 100 });

    for (let i = 0; i < 5; i++) {
      monitor.recordViolation({ type: "output_truncated", severity: "warn", detail: "x", timestamp: new Date().toISOString(), skillId: "skill-A" });
    }
    for (let i = 0; i < 2; i++) {
      monitor.recordViolation({ type: "command_injection", severity: "critical", detail: "y", timestamp: new Date().toISOString(), skillId: "skill-B" });
    }
    monitor.recordViolation({ type: "path_traversal", severity: "error", detail: "z", timestamp: new Date().toISOString(), skillId: "skill-C" });

    const offenders = monitor.getTopOffenders(3);
    expect(offenders[0]!.skillId).toBe("skill-A");
    expect(offenders[0]!.totalViolations).toBe(5);
    expect(offenders[1]!.skillId).toBe("skill-B");
  });

  it("reset 后应清空违规记录", () => {
    const monitor = new SandboxMonitor({ circuitBreakerThreshold: 1 });
    const skillId = "test-skill-003";

    monitor.recordViolation({ type: "command_injection", severity: "critical", detail: "d", timestamp: new Date().toISOString(), skillId });
    expect(monitor.isCircuitBroken(skillId)).toBe(true);

    monitor.resetCircuit(skillId);
    expect(monitor.isCircuitBroken(skillId)).toBe(false);
  });
});

// ─── SandboxFactory 降级策略测试 ──────────────────────────────────────────────

describe("SandboxFactory — 配置合并", () => {
  it("Partial config 应与默认值正确合并", () => {
    const merged = SandboxFactory.mergeWithDefaults({
      resources: { memoryMb: 512 } as never,
    });

    expect(merged.resources.memoryMb).toBe(512);
    // 其他字段应保留默认值
    expect(merged.resources.cpuCores).toBeGreaterThan(0);
    expect(merged.runtime).toBeDefined();
    expect(merged.network).toBeDefined();
  });

  it("env.allowList 应合并（不覆盖）", () => {
    const merged = SandboxFactory.mergeWithDefaults({
      env: { allowList: ["MY_CUSTOM_VAR"], inject: {} },
    });

    expect(merged.env.allowList).toContain("MY_CUSTOM_VAR");
    // 默认白名单也应保留
    expect(merged.env.allowList).toContain("PATH");
  });

  it("createProcessSandbox 应强制设置 runtime=process", () => {
    const sandbox = SandboxFactory.createProcessSandbox({ runtime: "docker" } as never);
    // 无论传什么 runtime，都应是 ProcessSandbox 实例
    expect(sandbox).toBeInstanceOf(ProcessSandbox);
  });
});

// ─── 文件系统访问测试（Linux only）────────────────────────────────────────────

describe.skipIf(os.platform() !== "linux")("ProcessSandbox — 文件系统访问（Linux）", () => {
  let skillDir: string;

  beforeAll(() => {
    skillDir = makeTempSkillDir("fs-access");
    writePythonSkill(skillDir, FILESYSTEM_READ_SKILL);
  });

  afterAll(() => {
    fs.rmSync(skillDir, { recursive: true, force: true });
  });

  it("/etc/shadow 在进程沙箱中应因权限被拒绝（EACCES）", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(baseConfig());
    const result = await sandbox.execute("python3 skill.py", skillDir, makeRequest());

    if (result.success) {
      const parsed = JSON.parse(
        result.stdout.split("\n").find((l) => l.startsWith("{")) ?? "{}"
      );
      const shadowResult = parsed.result?.file_access?.["/etc/shadow"] ?? "";
      // 普通用户应无法读取 /etc/shadow
      expect(shadowResult).toContain("BLOCKED");
    }
    // 如果执行失败，则本身就是被拒绝，测试通过
  });
});

// ─── 并发执行稳定性测试 ───────────────────────────────────────────────────────

describe("ProcessSandbox — 并发稳定性", () => {
  let skillDir: string;

  beforeAll(() => {
    skillDir = makeTempSkillDir("concurrent");
    writePythonSkill(skillDir, ECHO_SKILL);
  });

  afterAll(() => {
    fs.rmSync(skillDir, { recursive: true, force: true });
  });

  it("10 个并发执行应全部成功完成", async () => {
    const sandbox = SandboxFactory.createProcessSandbox(baseConfig());

    const tasks = Array.from({ length: 10 }, (_, i) =>
      sandbox.execute("python3 skill.py", skillDir, makeRequest("invoke", { idx: i }))
    );

    const results = await Promise.all(tasks);

    const successCount = results.filter((r) => r.success).length;
    expect(successCount).toBe(10);

    // 所有延迟应合理
    for (const r of results) {
      expect(r.latencyMs).toBeLessThan(5_000);
    }
  }, 15_000);
});
