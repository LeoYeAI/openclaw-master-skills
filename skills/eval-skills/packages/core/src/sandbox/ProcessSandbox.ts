/**
 * @file sandbox/ProcessSandbox.ts
 * @description Layer 1 — 进程级沙箱（跨平台，零额外依赖）
 *
 * 防护能力：
 *   ✅ 命令注入防护（可执行程序白名单 + 特殊字符过滤）
 *   ✅ 路径遍历防护（路径归一化 + 边界检查）
 *   ✅ 环境变量过滤（白名单透传）
 *   ✅ 输出大小限制（按字节截断）
 *   ✅ 硬超时 + 进程树强制销毁（防止僵尸进程）
 *   ✅ 内存限制（Linux: ulimit -v；macOS: 仅记录）
 *   ⚠️  网络隔离：仅记录警告，无法强制阻断（需升级 DockerSandbox）
 *   ⚠️  文件系统隔离：基于路径校验，非内核级别隔离
 *
 * 原理：
 *   1. 在独立进程组（detached: true）中启动 Skill 进程
 *   2. Linux 通过 ulimit -v 设置虚拟内存上限
 *   3. 通过 process.kill(-pgid, SIGKILL) 销毁整个进程树
 *   4. 流式读取 stdout/stderr，达到 maxOutputBytes 即截断
 */

import { spawn } from "node:child_process";
import * as os from "node:os";
import type { SandboxConfig, SandboxResult } from "./types.js";
import {
  SandboxExecutor,
  type JsonRpcRequest,
} from "./SandboxExecutor.js";

export class ProcessSandbox extends SandboxExecutor {
  constructor(config: SandboxConfig) {
    super(config);
  }

  async execute(
    command: string,
    skillDir: string,
    request: JsonRpcRequest,
    signal?: AbortSignal,
  ): Promise<SandboxResult> {
    const startTime = performance.now();

    // ── Step 1: 验证并解析命令 ─────────────────────────────────────────────
    let parsed;
    try {
      parsed = this.parseAndValidateCommand(command, skillDir);
    } catch (err) {
      return this.makeErrorResult(
        (err as Error).message, "process", startTime,
      );
    }

    // ── Step 2: 检查网络策略（ProcessSandbox 无法强制，仅警告） ─────────────
    if (this.config.network === "none") {
      // 我们无法在进程级别阻断网络，记录一条安全警告
      this.emit("security-warning", {
        message: "ProcessSandbox cannot enforce network isolation. " +
          "Use DockerSandbox for strict network control.",
        skillDir,
      });
    }

    // ── Step 3: 构建安全环境变量 ───────────────────────────────────────────
    const safeEnv = this.buildSafeEnv();

    // ── Step 4: 构建 Linux 资源限制包装命令 ──────────────────────────────────
    const { executable, args, cwd } = parsed;
    const { resources } = this.config;

    let finalExec = executable;
    let finalArgs = [...args];

    if (os.platform() === "linux") {
      // 使用 bash -c 包装，通过 ulimit 设置内存限制
      // ulimit -v: 虚拟内存上限（KB）
      const memLimitKb = resources.memoryMb * 1024;
      const shellCmd =
        `ulimit -v ${memLimitKb}; ` +
        `exec ${[executable, ...args].map((a) => JSON.stringify(a)).join(" ")}`;
      finalExec = "bash";
      finalArgs = ["-c", shellCmd];
    }

    // ── Step 5: 启动子进程（独立进程组，用于后续整树 kill） ─────────────────
    const child = spawn(finalExec, finalArgs, {
      cwd,
      env: safeEnv,
      stdio: ["pipe", "pipe", "pipe"],
      // detached=true: 在新进程组中启动，便于通过 -pgid 杀死整个进程树
      detached: true,
    });

    // ── Step 6: 并发读取 stdout/stderr（流式，内存安全） ─────────────────────
    const stdoutChunks: Buffer[] = [];
    const stderrChunks: Buffer[] = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let stdoutTruncated = false;
    const maxBytes = resources.maxOutputBytes;
    const halfMax = Math.floor(maxBytes / 2); // stdout/stderr 各占一半

    child.stdout.on("data", (chunk: Buffer) => {
      if (stdoutBytes < halfMax) {
        const take = Math.min(chunk.length, halfMax - stdoutBytes);
        stdoutChunks.push(chunk.subarray(0, take));
        stdoutBytes += take;
        if (take < chunk.length) {
          stdoutTruncated = true;
          this.recordViolation("output_truncated", "warn",
            `stdout exceeded ${halfMax} bytes, truncated`);
        }
      }
    });

    child.stderr.on("data", (chunk: Buffer) => {
      if (stderrBytes < halfMax) {
        const take = Math.min(chunk.length, halfMax - stderrBytes);
        stderrChunks.push(chunk.subarray(0, take));
        stderrBytes += take;
      }
    });

    // ── Step 7: 写入 JSON-RPC 请求到 stdin ────────────────────────────────
    const requestStr = JSON.stringify(request);
    child.stdin.write(requestStr, "utf-8");
    child.stdin.end();

    // ── Step 8: 设置硬超时 + AbortSignal 监听 ────────────────────────────
    let timedOut = false;
    let oomKilled = false;

    /**
     * 强制销毁整个进程树
     * 先发 SIGTERM（优雅关闭，300ms 宽限期），再发 SIGKILL
     */
    const forceKill = async (reason: string) => {
      try {
        if (child.pid !== undefined) {
          // 发送给整个进程组（负号 = 进程组 ID）
          process.kill(-child.pid, "SIGTERM");
        }
      } catch { /* 进程可能已经退出 */ }

      // 等待 300ms 后强制 SIGKILL
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          try {
            if (child.pid !== undefined) {
              process.kill(-child.pid, "SIGKILL");
            }
          } catch { /* 忽略 "process not found" 错误 */ }
          resolve();
        }, 300);
      });

      this.emit("process-killed", { pid: child.pid, reason });
    };

    // 硬超时定时器
    const hardTimeout = setTimeout(async () => {
      timedOut = true;
      await forceKill(`hard timeout (${resources.hardTimeoutMs}ms)`);
    }, resources.hardTimeoutMs);

    // AbortSignal 监听（来自 TaskExecutor 的软超时）
    const onAbort = async () => {
      timedOut = true;
      await forceKill("aborted by signal");
    };
    signal?.addEventListener("abort", onAbort, { once: true });

    // ── Step 9: 等待进程结束 ──────────────────────────────────────────────
    const exitCode = await new Promise<number | null>((resolve) => {
      child.on("close", (code, killSignal) => {
        clearTimeout(hardTimeout);
        signal?.removeEventListener("abort", onAbort);

        // 检测 OOM kill（Linux 中 SIGKILL 后退出码为 -9 或 null）
        if (killSignal === "SIGKILL" && !timedOut) {
          oomKilled = true;
        }
        resolve(code);
      });

      child.on("error", (err) => {
        clearTimeout(hardTimeout);
        signal?.removeEventListener("abort", onAbort);
        this.emit("spawn-error", { error: err.message });
        resolve(null);
      });
    });

    // ── Step 10: 组装结果 ─────────────────────────────────────────────────
    const stdout = Buffer.concat(stdoutChunks).toString("utf-8");
    const stderr = Buffer.concat(stderrChunks).toString("utf-8");
    const latencyMs = performance.now() - startTime;

    const success = exitCode === 0 && !timedOut && !oomKilled;

    let errorMsg: string | undefined;
    if (timedOut) {
      errorMsg = `Process timed out after ${resources.hardTimeoutMs}ms`;
    } else if (oomKilled) {
      errorMsg = `Process killed due to memory limit (${resources.memoryMb}MB)`;
    } else if (exitCode !== 0 && exitCode !== null) {
      errorMsg = `Process exited with code ${exitCode}${stderr ? `: ${stderr.trim().slice(0, 200)}` : ""}`;
    }

    return {
      success,
      stdout,
      stderr,
      exitCode,
      latencyMs,
      timedOut,
      oomKilled,
      outputTruncated: stdoutTruncated,
      runtimeUsed: "process",
      error: errorMsg,
    };
  }
}
