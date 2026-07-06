/**
 * @file sandbox/SandboxExecutor.ts
 * @description 沙箱执行器抽象基类
 *
 * 定义沙箱执行器的统一接口，ProcessSandbox 和 DockerSandbox 均继承此类。
 * 提供：
 *   - 输入验证（命令注入防护、路径遍历检测）
 *   - 环境变量过滤
 *   - 输出大小限制
 *   - 违规事件收集
 */

import { EventEmitter } from "node:events";
import * as path from "node:path";
import type {
  SandboxConfig,
  SandboxResult,
  SandboxViolation,
  ViolationType,
} from "./types.js";

/** JSON-RPC 请求结构 */
export interface JsonRpcRequest {
  jsonrpc: "2.0";
  method: string;
  params: Record<string, unknown>;
  id: number;
}

/** 解析后的命令结构 */
export interface ParsedCommand {
  /** 可执行程序（如 "python3", "node"） */
  executable: string;
  /** 参数列表（如 ["skill.py"]） */
  args: string[];
  /** 工作目录 */
  cwd: string;
}

// ─── 安全规则常量 ─────────────────────────────────────────────────────────────

/** 允许运行的可执行程序白名单（不在列表中的将被拒绝） */
const ALLOWED_EXECUTABLES = new Set([
  "python3", "python", "python3.10", "python3.11", "python3.12",
  "node", "node20", "node18",
  "ruby", "ruby3",
  "php", "php8",
  "java",
  "bun",
  "deno",
  "bash", "sh",   // 谨慎：shell 需要额外检查脚本路径
]);

/** 高风险 shell 命令模式（用于检测注入） */
const SHELL_INJECTION_PATTERNS = [
  /[;&|`$(){}[\]<>]/,         // shell 特殊字符
  /\.\./,                      // 路径遍历
  /\/etc\//,                   // 系统配置目录
  /\/proc\//,                  // 进程信息
  /\/sys\//,                   // 内核接口
  /\bsudo\b/,                  // 提权命令
  /\bchmod\b|\bchown\b/,       // 权限变更
  /\bkill\b|\bpkill\b/,        // 进程终止
  /\bcurl\b|\bwget\b/,         // 网络下载（subprocess 模式下需额外审查）
  /\brm\b.*-rf/,               // 危险删除
  // /\beval\b/,               // eval 注入 (移除：路径中常见 eval 单词，且 shell: false 下无风险)
  // /\bexec\b/,               // exec 替换进程 (移除：同上)
];

/** 敏感环境变量名模式（不得泄露进沙箱） */
const SENSITIVE_ENV_PATTERNS = [
  /key/i, /secret/i, /token/i, /password/i, /passwd/i,
  /credential/i, /private/i, /auth/i, /api_key/i,
  /aws_/i, /gcp_/i, /azure_/i,
  /openai/i, /anthropic/i,
];

// ─── 抽象基类 ─────────────────────────────────────────────────────────────────

export abstract class SandboxExecutor extends EventEmitter {
  protected readonly config: SandboxConfig;
  protected readonly violations: SandboxViolation[] = [];

  constructor(config: SandboxConfig) {
    super();
    this.config = config;
  }

  // ─── 公共接口 ──────────────────────────────────────────────────────────────

  /**
   * 在沙箱中执行 JSON-RPC 调用
   * @param command   Skill 的 entrypoint 命令字符串（如 "python3 skill.py"）
   * @param skillDir  Skill 所在目录（绝对路径）
   * @param request   JSON-RPC 请求
   * @param signal    AbortSignal（来自 TaskExecutor 的软超时）
   */
  abstract execute(
    command: string,
    skillDir: string,
    request: JsonRpcRequest,
    signal?: AbortSignal,
  ): Promise<SandboxResult>;

  /** 获取本次执行中收集到的所有安全违规事件 */
  getViolations(): readonly SandboxViolation[] {
    return this.violations;
  }

  // ─── 输入验证（子类复用） ──────────────────────────────────────────────────

  /**
   * 解析并验证命令字符串
   * @throws Error 当命令不合法时（命令注入 / 不在白名单）
   */
  protected parseAndValidateCommand(command: string, skillDir: string): ParsedCommand {
    // Step 1: 清理命令字符串
    const trimmed = command.trim();

    // Step 2: 检测 shell 注入模式
    for (const pattern of SHELL_INJECTION_PATTERNS) {
      if (pattern.test(trimmed)) {
        this.recordViolation("command_injection", "critical",
          `Suspicious pattern "${pattern.source}" detected in command: "${trimmed}"`);
        throw new Error(
          `[Sandbox] Command blocked due to potential injection: "${trimmed}". ` +
          `Pattern: ${pattern.source}`
        );
      }
    }

    // Step 3: 解析命令（支持 "python3 skill.py" 或 "node /abs/path/index.js"）
    const parts = trimmed.split(/\s+/).filter(Boolean);
    if (parts.length === 0) {
      throw new Error("[Sandbox] Empty command is not allowed");
    }

    const executable = parts[0]!;
    const rawArgs = parts.slice(1);

    // Step 4: 可执行程序白名单检查
    const execBasename = path.basename(executable);
    if (!ALLOWED_EXECUTABLES.has(execBasename) && !ALLOWED_EXECUTABLES.has(executable)) {
      this.recordViolation("command_injection", "error",
        `Executable "${executable}" is not in the allowlist`);
      throw new Error(
        `[Sandbox] Executable "${executable}" is not allowed. ` +
        `Allowed: ${[...ALLOWED_EXECUTABLES].join(", ")}`
      );
    }

    // Step 5: 解析脚本参数路径（防止路径遍历）
    const resolvedArgs = rawArgs.map((arg) => {
      // 如果参数看起来像文件路径（不以 - 开头），则解析为绝对路径
      if (!arg.startsWith("-") && !arg.startsWith("--") && /[./\\]/.test(arg)) {
        const resolved = path.resolve(skillDir, arg);
        // 确保解析后的路径在 skillDir 内
        if (!resolved.startsWith(path.resolve(skillDir))) {
          this.recordViolation("path_traversal", "critical",
            `Path traversal attempt: "${arg}" resolves to "${resolved}" outside skillDir`);
          throw new Error(
            `[Sandbox] Path traversal blocked: "${arg}" is outside skill directory`
          );
        }
        return resolved;
      }
      return arg;
    });

    return {
      executable,
      args: resolvedArgs,
      cwd: skillDir,
    };
  }

  /**
   * 构建过滤后的环境变量
   * 只透传白名单中的变量，并注入配置的强制变量
   */
  protected buildSafeEnv(): Record<string, string> {
    const { allowList, inject } = this.config.env;
    const safeEnv: Record<string, string> = {};

    for (const key of allowList) {
      const value = process.env[key];
      if (value !== undefined) {
        // 双重检查：即使在白名单中，也不允许名字带敏感词
        const isSensitive = SENSITIVE_ENV_PATTERNS.some((p) => p.test(key));
        if (isSensitive) {
          this.recordViolation("env_leak", "warn",
            `Env var "${key}" is in allowList but matches sensitive pattern, skipped`);
          continue;
        }
        safeEnv[key] = value;
      }
    }

    // 注入强制变量（覆盖）
    if (inject) {
      for (const [key, value] of Object.entries(inject)) {
        safeEnv[key] = value;
      }
    }

    return safeEnv;
  }

  /**
   * 从输出 Buffer 中收集数据，超出限制时截断
   * @returns [截断后的字符串, 是否被截断]
   */
  protected collectOutput(chunks: Buffer[], maxBytes: number): [string, boolean] {
    let totalSize = 0;
    const finalChunks: Buffer[] = [];

    for (const chunk of chunks) {
      const remaining = maxBytes - totalSize;
      if (remaining <= 0) {
        this.recordViolation("output_truncated", "warn",
          `Output exceeded ${maxBytes} bytes and was truncated`);
        return [Buffer.concat(finalChunks).toString("utf-8"), true];
      }
      if (chunk.length <= remaining) {
        finalChunks.push(chunk);
        totalSize += chunk.length;
      } else {
        finalChunks.push(chunk.subarray(0, remaining));
        totalSize += remaining;
        this.recordViolation("output_truncated", "warn",
          `Output exceeded ${maxBytes} bytes and was truncated`);
        return [Buffer.concat(finalChunks).toString("utf-8"), true];
      }
    }

    return [Buffer.concat(finalChunks).toString("utf-8"), false];
  }

  /**
   * 记录安全违规事件并触发 "violation" 事件
   */
  protected recordViolation(
    type: ViolationType,
    severity: SandboxViolation["severity"],
    detail: string,
  ): void {
    const violation: SandboxViolation = {
      type,
      severity,
      detail,
      timestamp: new Date().toISOString(),
      skillId: "(unknown)",
    };
    this.violations.push(violation);
    this.emit("violation", violation);
  }

  /**
   * 构建空结果（用于错误提前返回）
   */
  protected makeErrorResult(
    error: string,
    runtimeUsed: "process" | "docker",
    startTime: number,
    extras: Partial<SandboxResult> = {},
  ): SandboxResult {
    return {
      success: false,
      stdout: "",
      stderr: "",
      exitCode: null,
      latencyMs: performance.now() - startTime,
      timedOut: false,
      oomKilled: false,
      outputTruncated: false,
      runtimeUsed,
      error,
      ...extras,
    };
  }
}
