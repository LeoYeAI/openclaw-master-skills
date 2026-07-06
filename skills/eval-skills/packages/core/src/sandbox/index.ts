/**
 * @file sandbox/index.ts
 * @description 沙箱模块公共导出
 *
 * @example
 * // 最简使用
 * import { SandboxFactory } from "@eval-skills/core/sandbox";
 * const sandbox = await SandboxFactory.create({ runtime: "auto" });
 * const result = await sandbox.execute("python3 skill.py", "/path/to/skill", request);
 *
 * // 带监控
 * import { SandboxFactory, SandboxMonitor } from "@eval-skills/core/sandbox";
 * const monitor = new SandboxMonitor({ circuitBreakerThreshold: 3 });
 * const sandbox = await SandboxFactory.create();
 * monitor.attach(sandbox, skillId);
 */

export { SandboxFactory } from "./SandboxFactory.js";
export { ProcessSandbox } from "./ProcessSandbox.js";
export { DockerSandbox } from "./DockerSandbox.js";
export { SandboxExecutor } from "./SandboxExecutor.js";
export { SandboxMonitor } from "./SandboxMonitor.js";

export type {
  // 主配置
  SandboxConfig,
  // 子配置
  ResourceLimits,
  FilesystemPolicy,
  EnvPolicy,
  DockerSandboxConfig,
  NetworkPolicy,
  NetworkAllowEntry,
  // 结果
  SandboxResult,
  ResourceUsageStats,
  // 违规
  SandboxViolation,
  ViolationType,
} from "./types.js";

export {
  DEFAULT_SANDBOX_CONFIG,
  DEV_SANDBOX_CONFIG,
} from "./types.js";

export type {
  JsonRpcRequest,
  ParsedCommand,
} from "./SandboxExecutor.js";

export type {
  SkillViolationStats,
  MonitorConfig,
} from "./SandboxMonitor.js";
