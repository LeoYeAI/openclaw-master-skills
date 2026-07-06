/**
 * @file sandbox/DockerSandbox.ts
 * @description Layer 2 — Docker 容器级强隔离沙箱
 *
 * 防护能力（全面覆盖进程沙箱的短板）：
 *   ✅ 独立内核命名空间（PID / NET / MNT / IPC / UTS）
 *   ✅ cgroup v2 内存/CPU/PID 硬限制（OOM Killer 接管）
 *   ✅ 网络完全隔离（--network none）或精细化白名单
 *   ✅ 只读文件系统挂载（--read-only + tmpfs /tmp）
 *   ✅ seccomp-bpf 系统调用白名单过滤
 *   ✅ Linux Capabilities 全部 drop + 精确 add
 *   ✅ 禁止 root 权限提升（--security-opt no-new-privileges）
 *   ✅ 非 root 用户执行（UID/GID 65534 = nobody）
 *   ✅ 容器生命周期管理（自动清理，防止资源泄漏）
 *
 * 依赖：
 *   npm install dockerode @types/dockerode
 */

import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { Readable } from "node:stream";
import Docker from "dockerode";
import type {
  SandboxConfig,
  SandboxResult,
  ResourceUsageStats,
} from "./types.js";
import {
  SandboxExecutor,
  type JsonRpcRequest,
} from "./SandboxExecutor.js";

// ─── 内部常量 ─────────────────────────────────────────────────────────────────

/** 容器内 Skill 的挂载路径 */
const SKILL_MOUNT_PATH = "/skill" as const;

/** 容器内可写临时目录 */
const TMP_MOUNT_PATH = "/tmp" as const;

/** 非特权用户 UID/GID（nobody） */
const NOBODY_UID = 65534 as const;

/** 容器名前缀（便于识别和清理） */
const CONTAINER_NAME_PREFIX = "eval-skills-sandbox-" as const;

/** 最小允许保留的 Linux Capabilities（Python/Node 脚本通常不需要任何 cap） */
const ALLOWED_CAPABILITIES: string[] = [];

/** 必须 Drop 的高危 Capabilities */
const DROP_CAPABILITIES = ["ALL"] as const;

// ─── 辅助类型 ─────────────────────────────────────────────────────────────────

interface ContainerStats {
  memory_stats: {
    max_usage?: number;
    usage?: number;
    limit?: number;
  };
  cpu_stats: {
    cpu_usage: { total_usage: number };
    system_cpu_usage: number;
    online_cpus?: number;
  };
  precpu_stats: {
    cpu_usage: { total_usage: number };
    system_cpu_usage: number;
  };
}

// ─── DockerSandbox ────────────────────────────────────────────────────────────

export class DockerSandbox extends SandboxExecutor {
  private readonly docker: Docker;

  constructor(config: SandboxConfig) {
    super(config);
    this.docker = new Docker({
      socketPath: config.docker.socketPath ?? "/var/run/docker.sock",
    });
  }

  // ─── 公共接口 ──────────────────────────────────────────────────────────────

  async execute(
    command: string,
    skillDir: string,
    request: JsonRpcRequest,
    signal?: AbortSignal,
  ): Promise<SandboxResult> {
    const startTime = performance.now();

    // ── Step 1: 验证命令 ──────────────────────────────────────────────────
    let parsed;
    try {
      parsed = this.parseAndValidateCommand(command, skillDir);
    } catch (err) {
      return this.makeErrorResult((err as Error).message, "docker", startTime);
    }

    // ── Step 2: 拉取/检查镜像 ────────────────────────────────────────────
    const image = this.config.docker.image;
    try {
      await this.ensureImage(image);
    } catch (err) {
      return this.makeErrorResult(
        `Failed to ensure Docker image "${image}": ${(err as Error).message}`,
        "docker", startTime,
      );
    }

    // ── Step 3: 加载 seccomp profile ─────────────────────────────────────
    const seccompProfile = this.loadSeccompProfile();

    // ── Step 4: 构建容器创建选项 ──────────────────────────────────────────
    const containerName = `${CONTAINER_NAME_PREFIX}${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const safeEnv = this.buildSafeEnv();
    const envArray = Object.entries(safeEnv).map(([k, v]) => `${k}=${v}`);

    const createOptions = this.buildContainerCreateOptions(
      containerName,
      image,
      parsed,
      skillDir,
      envArray,
      seccompProfile,
    );

    // ── Step 5: 创建容器 ──────────────────────────────────────────────────
    let container: Docker.Container | null = null;
    try {
      container = await this.docker.createContainer(createOptions);
    } catch (err) {
      return this.makeErrorResult(
        `Failed to create container: ${(err as Error).message}`,
        "docker", startTime,
      );
    }

    // ── Step 6: 执行（带完整生命周期管理） ──────────────────────────────
    try {
      return await this.runContainer(
        container,
        request,
        startTime,
        signal,
      );
    } finally {
      // 无论成功/失败/超时，都清理容器
      await this.cleanupContainer(container, containerName);
    }
  }

  /**
   * 检查 Docker Daemon 是否可用
   */
  async isAvailable(): Promise<boolean> {
    try {
      await this.docker.ping();
      return true;
    } catch {
      return false;
    }
  }

  // ─── 私有实现 ──────────────────────────────────────────────────────────────

  /**
   * 构建 Docker 容器创建选项（核心安全配置）
   */
  private buildContainerCreateOptions(
    name: string,
    image: string,
    parsed: { executable: string; args: string[]; cwd: string },
    skillDir: string,
    envArray: string[],
    seccompProfile: string,
  ): Docker.ContainerCreateOptions {
    const { resources, filesystem, network } = this.config;

    // 网络模式
    const networkMode = network === "none" ? "none" : "bridge";

    // 绑定挂载：Skill 目录只读 + /tmp 内存盘
    const binds: string[] = [
      `${path.resolve(skillDir)}:${SKILL_MOUNT_PATH}:ro`,  // 只读挂载
    ];
    
    // 额外只读路径
    for (const p of filesystem.additionalReadOnlyPaths ?? []) {
      const resolved = path.resolve(p);
      if (fs.existsSync(resolved)) {
        binds.push(`${resolved}:${resolved}:ro`);
      }
    }

    // tmpfs 配置（容器内唯一可写区域）
    const tmpfsConfig: Record<string, string> = {
      [TMP_MOUNT_PATH]: `rw,noexec,nosuid,size=${resources.tmpDiskMb}m`,
    };

    // seccomp 安全选项
    const securityOpts: string[] = [
      "no-new-privileges",            // 禁止提权
      `seccomp=${seccompProfile}`,    // 系统调用白名单
    ];

    if (this.config.docker.rootless) {
      securityOpts.push("rootless");
    }

    // 屏蔽敏感路径
    const maskedPaths = filesystem.maskSensitivePaths
      ? ["/proc/acpi", "/proc/kcore", "/proc/keys", "/proc/latency_stats",
         "/proc/timer_list", "/proc/timer_stats", "/proc/sched_debug",
         "/proc/scsi", "/sys/firmware", "/sys/devices/virtual/powercap"]
      : [];

    return {
      name,
      Image: image,
      // 直接运行解析后的命令，不经过 shell（防止注入）
      Cmd: [parsed.executable, ...parsed.args],
      WorkingDir: SKILL_MOUNT_PATH,
      Env: envArray,
      // 以非特权用户运行
      User: `${NOBODY_UID}:${NOBODY_UID}`,
      // 关闭 TTY 和 stdin 持久
      Tty: false,
      OpenStdin: true,
      StdinOnce: true,
      AttachStdin: true,
      AttachStdout: true,
      AttachStderr: true,
      // 只读根文件系统
      // ReadonlyRootfs: true, // 移到 HostConfig
      NetworkDisabled: network === "none",
      HostConfig: {
        NetworkMode: networkMode,
        Binds: binds,
        Tmpfs: tmpfsConfig,
        ReadonlyRootfs: true, // 在 HostConfig 中启用
        // ── cgroup 资源硬限制 ─────────────────────────────────────────
        Memory: resources.memoryMb * 1024 * 1024,    // bytes
        MemorySwap: resources.memoryMb * 1024 * 1024, // 禁用 swap（swap = memory 即禁用）
        NanoCpus: Math.floor(resources.cpuCores * 1e9), // 1e9 = 1 CPU
        PidsLimit: resources.maxPids,                 // fork bomb 防护
        // ── 安全配置 ─────────────────────────────────────────────────
        SecurityOpt: securityOpts,
        CapDrop: [...DROP_CAPABILITIES] as string[],
        CapAdd: ALLOWED_CAPABILITIES,
        // ── OOM 配置 ─────────────────────────────────────────────────
        OomKillDisable: false,   // 允许 OOM Killer 杀死进程
        OomScoreAdj: 500,        // 提高 OOM 优先级（更容易被 kill）
        // ── 其他安全选项 ─────────────────────────────────────────────
        AutoRemove: false,       // 手动清理，确保我们能获取退出状态
        MaskedPaths: maskedPaths,
        ReadonlyPaths: ["/proc/asound", "/proc/bus", "/proc/fs", "/proc/irq",
                        "/proc/sys", "/proc/sysrq-trigger"],
      },
    };
  }

  /**
   * 运行容器并收集 I/O
   */
  private async runContainer(
    container: Docker.Container,
    request: JsonRpcRequest,
    startTime: number,
    signal?: AbortSignal,
  ): Promise<SandboxResult> {
    const { resources } = this.config;
    let timedOut = false;
    let oomKilled = false;
    let statsSnapshot: ContainerStats | null = null;

    // Attach stdin/stdout/stderr
    const stream = await container.attach({
      stream: true,
      stdin: true,
      stdout: true,
      stderr: true,
    });

    // 启动容器
    await container.start();

    // 开始后台收集资源统计
    const statsPromise = this.collectStats(container).then((s) => {
      statsSnapshot = s;
    }).catch(() => { /* stats 收集失败不影响主流程 */ });

    // ── 流式读取 stdout/stderr ─────────────────────────────────────────
    const stdoutChunks: Buffer[] = [];
    const stderrChunks: Buffer[] = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let outputTruncated = false;
    const halfMax = Math.floor(resources.maxOutputBytes / 2);

    // Docker attach 返回多路复用流，需要 demux
    const demuxPromise = new Promise<void>((resolve, reject) => {
      container.modem.demuxStream(
        stream,
        // stdout 写入 writable
        new (class extends (require("node:stream").Writable) {
          _write(chunk: Buffer, _enc: string, cb: () => void) {
            if (stdoutBytes < halfMax) {
              const take = Math.min(chunk.length, halfMax - stdoutBytes);
              stdoutChunks.push(chunk.subarray(0, take));
              stdoutBytes += take;
              if (take < chunk.length) {
                outputTruncated = true;
              }
            }
            cb();
          }
        })(),
        // stderr 写入 writable
        new (class extends (require("node:stream").Writable) {
          _write(chunk: Buffer, _enc: string, cb: () => void) {
            if (stderrBytes < halfMax) {
              const take = Math.min(chunk.length, halfMax - stderrBytes);
              stderrChunks.push(chunk.subarray(0, take));
              stderrBytes += take;
            }
            cb();
          }
        })(),
      );

      stream.on("end", () => resolve());
      stream.on("error", (err: Error) => reject(err));
    });

    // ── 写入 JSON-RPC 请求 ─────────────────────────────────────────────
    const requestStr = JSON.stringify(request);
    await new Promise<void>((resolve, reject) => {
      stream.write(requestStr, "utf-8", (err?: Error | null) => {
        if (err) reject(err); else resolve();
      });
    });
    stream.end(); // 关闭 stdin

    // ── 硬超时定时器 ───────────────────────────────────────────────────
    const hardTimeoutPromise = new Promise<"timeout">((resolve) => {
      setTimeout(() => resolve("timeout"), resources.hardTimeoutMs);
    });

    // AbortSignal 转 Promise
    const abortPromise = new Promise<"aborted">((resolve) => {
      if (!signal) return;
      if (signal.aborted) { resolve("aborted"); return; }
      signal.addEventListener("abort", () => resolve("aborted"), { once: true });
    });

    // ── 等待容器结束或超时 ─────────────────────────────────────────────
    const waitResult = await Promise.race([
      container.wait().then((r) => ({ type: "exit" as const, statusCode: r.StatusCode })),
      hardTimeoutPromise,
      abortPromise,
    ]);

    // 处理超时 / abort
    if (waitResult === "timeout" || waitResult === "aborted") {
      timedOut = true;
      try {
        await container.kill({ signal: "SIGKILL" });
      } catch { /* 容器可能已退出 */ }
    }

    // 等待流读取完成
    try {
      await Promise.race([demuxPromise, new Promise((_, r) => setTimeout(() => r(new Error("demux timeout")), 3000))]);
    } catch { /* 流超时，继续 */ }

    // 等待 stats 收集完成（超时 1s）
    await Promise.race([statsPromise, new Promise((r) => setTimeout(r, 1000))]);

    // ── 检查 OOM ──────────────────────────────────────────────────────
    try {
      const inspect = await container.inspect();
      oomKilled = inspect.State?.OOMKilled ?? false;
    } catch { /* 容器已被清理 */ }

    const exitCode = typeof waitResult === "object" ? waitResult.statusCode : null;

    // ── 组装结果 ──────────────────────────────────────────────────────
    const stdout = Buffer.concat(stdoutChunks).toString("utf-8");
    const stderr = Buffer.concat(stderrChunks).toString("utf-8");
    const latencyMs = performance.now() - startTime;
    const success = exitCode === 0 && !timedOut && !oomKilled;

    let errorMsg: string | undefined;
    if (timedOut) {
      errorMsg = `Container timed out after ${resources.hardTimeoutMs}ms`;
    } else if (oomKilled) {
      errorMsg = `Container OOM-killed (memory limit: ${resources.memoryMb}MB)`;
    } else if (exitCode !== 0 && exitCode !== null) {
      errorMsg = `Container exited with code ${exitCode}`;
    }

    // ── 构建资源使用统计 ───────────────────────────────────────────────
    let resourceUsage: ResourceUsageStats | undefined;
    if (statsSnapshot) {
      resourceUsage = this.parseStats(statsSnapshot, latencyMs);
    }

    return {
      success,
      stdout,
      stderr,
      exitCode,
      latencyMs,
      timedOut,
      oomKilled,
      outputTruncated,
      resourceUsage,
      runtimeUsed: "docker",
      error: errorMsg,
    };
  }

  /**
   * 异步收集容器资源统计快照
   */
  private async collectStats(container: Docker.Container): Promise<ContainerStats> {
    return new Promise((resolve, reject) => {
      container.stats({ stream: false }, (err, data) => {
        if (err) reject(err);
        else resolve(data as ContainerStats);
      });
    });
  }

  /**
   * 将 Docker stats 数据解析为统一格式
   */
  private parseStats(stats: ContainerStats, wallTimeMs: number): ResourceUsageStats {
    const memBytes = stats.memory_stats?.max_usage ?? stats.memory_stats?.usage ?? 0;
    
    // CPU 使用率计算（Docker 标准算法）
    const cpuDelta =
      (stats.cpu_stats?.cpu_usage?.total_usage ?? 0) -
      (stats.precpu_stats?.cpu_usage?.total_usage ?? 0);
    const systemDelta =
      (stats.cpu_stats?.system_cpu_usage ?? 0) -
      (stats.precpu_stats?.system_cpu_usage ?? 0);
    const numCpus = stats.cpu_stats?.online_cpus ?? os.cpus().length;
    const cpuPercent =
      systemDelta > 0 ? (cpuDelta / systemDelta) * numCpus : 0;

    return {
      peakMemoryMb: Math.round(memBytes / (1024 * 1024) * 100) / 100,
      avgCpuPercent: Math.round(cpuPercent * 100) / 100,
      wallTimeMs,
    };
  }

  /**
   * 确保镜像存在（按 pullPolicy 决定是否拉取）
   */
  private async ensureImage(imageName: string): Promise<void> {
    const { pullPolicy } = this.config.docker;

    if (pullPolicy === "always") {
      await this.pullImage(imageName);
      return;
    }

    if (pullPolicy === "if-not-present") {
      try {
        await this.docker.getImage(imageName).inspect();
        return; // 镜像已存在，跳过拉取
      } catch {
        // 镜像不存在，执行拉取
        await this.pullImage(imageName);
      }
    }
    // "never": 不拉取，如果镜像不存在则 createContainer 时失败
  }

  /**
   * 拉取 Docker 镜像（带进度事件）
   */
  private pullImage(imageName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.docker.pull(imageName, (err: Error | null, stream: NodeJS.ReadableStream) => {
        if (err) { reject(err); return; }

        this.docker.modem.followProgress(
          stream as Readable,
          (pullErr: Error | null) => {
            if (pullErr) reject(pullErr);
            else {
              this.emit("image-pulled", { image: imageName });
              resolve();
            }
          },
          (event: { status?: string; progress?: string }) => {
            this.emit("image-pull-progress", event);
          },
        );
      });
    });
  }

  /**
   * 加载 seccomp 配置文件（内置 or 自定义）
   */
  private loadSeccompProfile(): string {
    const customPath = this.config.docker.seccompProfilePath;

    if (customPath) {
      if (!fs.existsSync(customPath)) {
        throw new Error(`seccomp profile not found: ${customPath}`);
      }
      return fs.readFileSync(customPath, "utf-8");
    }

    // 使用内置的 eval-skills seccomp profile
    const builtinPath = path.join(
      path.dirname(new URL(import.meta.url).pathname),
      "seccomp-profile.json",
    );

    if (fs.existsSync(builtinPath)) {
      return fs.readFileSync(builtinPath, "utf-8");
    }

    // 降级：返回 "unconfined"（记录警告）
    this.emit("security-warning", {
      message: "seccomp profile not found, running unconfined",
    });
    return "unconfined";
  }

  /**
   * 清理容器（停止 + 删除）
   * 无论执行结果如何都必须调用，防止僵尸容器堆积
   */
  private async cleanupContainer(
    container: Docker.Container,
    name: string,
  ): Promise<void> {
    const timeout = this.config.docker.cleanupTimeoutMs;

    const doCleanup = async () => {
      try {
        // 先 stop（给容器 1s 优雅退出）
        await container.stop({ t: 1 }).catch(() => {});
        // 再 remove（force=true 确保删除）
        await container.remove({ force: true, v: true });
        this.emit("container-cleaned", { name });
      } catch {
        // 清理失败不影响主流程，但记录以便后续排查
        this.emit("cleanup-failed", { name });
      }
    };

    await Promise.race([
      doCleanup(),
      new Promise<void>((resolve) => setTimeout(resolve, timeout)),
    ]);
  }
}
