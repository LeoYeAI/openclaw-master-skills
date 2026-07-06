/**
 * @file sandbox/types.ts (完整版)
 * @description 沙箱执行环境完整类型定义
 *
 * 三层防御架构：
 *   Layer 1 (ProcessSandbox)  — 进程级隔离，跨平台，零额外依赖
 *   Layer 2 (DockerSandbox)   — 容器级强隔离，需要 Docker daemon
 *   Layer 3 (SeccompProfile)  — 系统调用级白名单过滤（Docker 内嵌）
 */

// ─── 网络权限 ──────────────────────────────────────────────────────────────────

/** 允许访问的域名/IP 白名单条目 */
export interface NetworkAllowEntry {
  /** 目标主机（域名或 IP，支持 CIDR，如 "10.0.0.0/8"） */
  host: string;
  /** 允许的端口列表，空数组 = 该主机所有端口 */
  ports: number[];
  /** 协议 */
  protocol: "tcp" | "udp" | "any";
}

/** 网络访问策略 */
export type NetworkPolicy =
  | "none"            // 完全禁止所有网络访问（推荐用于纯计算类 Skill）
  | "allow_all"       // 允许所有网络访问（不建议，仅开发调试用）
  | NetworkAllowEntry[]; // 白名单模式（生产环境推荐）

// ─── 资源限制 ──────────────────────────────────────────────────────────────────

/** 沙箱资源硬限制（超出即强制终止） */
export interface ResourceLimits {
  /**
   * 内存上限（MB）
   * - ProcessSandbox: Linux 通过 `ulimit -v` 实现，macOS 仅警告
   * - DockerSandbox:  --memory 强制限制
   * @default 256
   */
  memoryMb: number;

  /**
   * 临时磁盘空间上限（MB）
   * @deprecated 推荐配置在 filesystem.tmpSizeMb
   */
  tmpDiskMb?: number;

  /**
   * CPU 使用率上限（核心数，如 0.5 = 50% 一核心）
   * - ProcessSandbox: 不强制（Linux 可结合 cpulimit）
   * - DockerSandbox:  --cpus 参数
   * @default 0.5
   */
  cpuCores: number;

  /**
   * 硬超时（毫秒）。独立于 TaskExecutor 的软超时，
   * 确保即使 AbortController 失效也能强制回收资源
   * @default 30000
   */
  hardTimeoutMs: number;

  /**
   * stdout + stderr 合计大小上限（bytes）
   * 超出后截断并标记 outputTruncated = true
   * @default 10 * 1024 * 1024  (10 MB)
   */
  maxOutputBytes: number;

  /**
   * 最大进程数（防止 fork bomb）
   * - ProcessSandbox: 不强制
   * - DockerSandbox:  --pids-limit 参数
   * @default 32
   */
  maxPids: number;
}

// ─── 文件系统权限 ─────────────────────────────────────────────────────────────

/** 文件系统访问策略 */
export interface FilesystemPolicy {
  /**
   * 是否以只读模式挂载 Skill 目录
   * - ProcessSandbox: 不强制（仅路径校验）
   * - DockerSandbox:  :ro bind mount 强制
   * @default true
   */
  readOnly: boolean;

  /**
   * 额外允许读写的路径列表（绝对路径）
   * 通常用于允许访问数据集或缓存目录
   * @default []
   */
  allowPaths: string[];

  /**
   * 额外允许只读访问的路径列表
   * @default []
   */
  additionalReadOnlyPaths?: string[];

  /**
   * 是否屏蔽敏感路径（如 /proc, /sys 等）
   * @default true
   */
  maskSensitivePaths?: boolean;

  /**
   * /tmp 临时目录大小限制（MB）
   * DockerSandbox 通过 tmpfs 挂载实现
   * @default 64
   */
  tmpSizeMb: number;
}

// ─── 环境变量策略 ─────────────────────────────────────────────────────────────

/** 环境变量传递策略 */
export interface EnvPolicy {
  /**
   * 允许透传到沙箱的环境变量名白名单
   * 即使在白名单中，名字包含敏感词（key/secret/token等）的也会被过滤
   * @default ["PATH", "HOME", "LANG", "TZ"]
   */
  allowList: string[];

  /**
   * 强制注入到沙箱的环境变量（覆盖白名单透传值）
   * 常用于注入 EVAL_SKILLS_SANDBOX=1 等标识
   * @default { EVAL_SKILLS_SANDBOX: "1" }
   */
  inject?: Record<string, string>;
}

// ─── Docker 特定配置 ──────────────────────────────────────────────────────────

/** Docker 沙箱专属配置 */
export interface DockerSandboxConfig {
  /**
   * Docker Socket 路径（覆盖默认）
   */
  socketPath?: string;

  /**
   * 是否使用 Rootless 模式（如 Podman 或 Rootless Docker）
   * @default false
   */
  rootless?: boolean;

  /**
   * 用于运行 Skill 的 Docker 镜像
   * 建议使用预加固的最小化镜像
   * @default "python:3.12-slim"
   */
  image: string;

  /**
   * 镜像拉取策略
   * - "always":        每次运行前都 pull（确保最新，但慢）
   * - "if-not-present": 本地不存在时才 pull（推荐生产）
   * - "never":         从不 pull（必须手动准备镜像）
   * @default "if-not-present"
   */
  pullPolicy: "always" | "if-not-present" | "never";

  /**
   * Seccomp 安全配置文件路径（JSON 格式，OCI 规范）
   * 不指定时使用 Docker 默认配置
   * 指定 "unconfined" 可禁用 seccomp（不推荐）
   */
  seccompProfile?: string;

  /**
   * @deprecated 使用 seccompProfile 代替
   */
  seccompProfilePath?: string;

  /**
   * 容器清理超时（毫秒）
   * @default 5000
   */
  cleanupTimeoutMs?: number;

  /**
   * 要额外丢弃的 Linux capabilities（在 Docker 已 drop-all 基础上）
   * 默认行为：drop ALL capabilities
   * @default []
   */
  dropCapabilities?: string[];

  /**
   * 要添加的 Linux capabilities（谨慎使用）
   * @default []
   */
  addCapabilities?: string[];

  /**
   * 是否禁用容器内 setuid/setgid（防止权限提升）
   * @default true
   */
  noNewPrivileges?: boolean;

  /**
   * 容器内运行用户（UID:GID 或用户名）
   * @default "65534:65534"  (nobody:nogroup)
   */
  user?: string;

  /**
   * 自定义 Docker 标签（用于过滤/审计）
   * @default { "eval-skills.sandbox": "true" }
   */
  labels?: Record<string, string>;
}

// ─── 主配置结构 ───────────────────────────────────────────────────────────────

/** 沙箱执行环境主配置 */
export interface SandboxConfig {
  /**
   * 是否启用沙箱
   * false 时 SubprocessAdapter 退回原始实现（仅限开发调试）
   * @default true
   */
  enabled: boolean;

  /**
   * 沙箱运行时选择
   * - "auto":    自动检测 Docker，可用则 Docker，否则 Process
   * - "docker":  强制使用 Docker（若 Docker 不可用则报错）
   * - "process": 强制使用进程级沙箱（跨平台，但隔离较弱）
   * @default "auto"
   */
  runtime: "auto" | "docker" | "process";

  /** 资源限制 */
  resources: ResourceLimits;

  /** 网络访问策略 */
  network: NetworkPolicy;

  /** 文件系统访问策略 */
  filesystem: FilesystemPolicy;

  /** 环境变量策略 */
  env: EnvPolicy;

  /** Docker 特定配置（仅 runtime=docker/auto 时生效） */
  docker: DockerSandboxConfig;
}

// ─── 执行结果 ─────────────────────────────────────────────────────────────────

/** 沙箱执行结果 */
export interface SandboxResult {
  /** 执行是否成功（exit code 0 且无超时/OOM） */
  success: boolean;

  /** 标准输出（可能被截断，见 outputTruncated） */
  stdout: string;

  /** 标准错误输出 */
  stderr: string;

  /** 进程退出码（超时强杀时可能为 null） */
  exitCode: number | null;

  /** 执行耗时（毫秒） */
  latencyMs: number;

  /** 是否超时被强制终止 */
  timedOut: boolean;

  /** 是否因内存超限被 OOM Kill */
  oomKilled: boolean;

  /** stdout 是否因大小限制被截断 */
  outputTruncated: boolean;

  /** 实际使用的运行时（auto 模式下确认用了哪个） */
  runtimeUsed: "process" | "docker";

  /** 错误消息（success=false 时填充） */
  error?: string;

  /** 资源使用统计（DockerSandbox 提供，ProcessSandbox 为 null） */
  resourceUsage?: ResourceUsageStats | null;
}

/** 容器资源使用统计（来自 Docker Stats API） */
export interface ResourceUsageStats {
  /** 峰值内存使用（字节） */
  peakMemoryBytes?: number;
  /** 峰值内存使用（MB） */
  peakMemoryMb?: number;

  /** CPU 使用时间（纳秒） */
  cpuUsageNs?: number;
  /** 平均 CPU 使用率（%） */
  avgCpuPercent?: number;

  /** 墙钟时间（毫秒） */
  wallTimeMs?: number;

  /** 网络接收字节数 */
  netRxBytes?: number;
  /** 网络发送字节数 */
  netTxBytes?: number;
  /** 进程数峰值 */
  pidsMax?: number;
}

// ─── 违规事件 ─────────────────────────────────────────────────────────────────

/** 安全违规类型 */
export type ViolationType =
  | "command_injection"    // 命令注入尝试
  | "path_traversal"       // 路径遍历尝试
  | "env_leak"             // 环境变量泄露风险
  | "output_truncated"     // 输出超过大小限制
  | "timeout"              // 超时（疑似死循环/慢速攻击）
  | "oom"                  // 内存溢出（疑似内存耗尽攻击）
  | "network_blocked"      // 网络访问被阻断
  | "syscall_blocked"      // 系统调用被 seccomp 阻断
  | "privilege_escalation" // 权限提升尝试
  | "process_limit"        // 进程数超限（疑似 fork bomb）
  | "unknown";             // 未知违规

/** 安全违规事件 */
export interface SandboxViolation {
  type: ViolationType;
  severity: "critical" | "error" | "warn" | "info";
  detail: string;
  timestamp: string;   // ISO 8601
  skillId: string;
  /** 额外上下文数据 */
  context?: Record<string, unknown>;
}

// ─── 预设配置 ─────────────────────────────────────────────────────────────────

/** 生产环境推荐默认配置 */
export const DEFAULT_SANDBOX_CONFIG: SandboxConfig = {
  enabled: true,
  runtime: "auto",
  resources: {
    memoryMb: 256,
    cpuCores: 0.5,
    hardTimeoutMs: 30_000,
    maxOutputBytes: 10 * 1024 * 1024,  // 10 MB
    maxPids: 32,
  },
  network: "none",
  filesystem: {
    readOnly: true,
    allowPaths: [],
    tmpSizeMb: 64,
  },
  env: {
    allowList: ["PATH", "HOME", "LANG", "LC_ALL", "TZ"],
    inject: {
      EVAL_SKILLS_SANDBOX: "1",
      PYTHONDONTWRITEBYTECODE: "1",
      PYTHONUNBUFFERED: "1",
    },
  },
  docker: {
    image: "python:3.12-slim",
    pullPolicy: "if-not-present",
    noNewPrivileges: true,
    user: "65534:65534",
    labels: { "eval-skills.sandbox": "true" },
  },
};

/** 开发/调试模式配置（宽松限制，不建议生产使用） */
export const DEV_SANDBOX_CONFIG: SandboxConfig = {
  enabled: true,
  runtime: "process",  // 开发环境不强求 Docker
  resources: {
    memoryMb: 512,
    cpuCores: 1.0,
    hardTimeoutMs: 60_000,
    maxOutputBytes: 50 * 1024 * 1024,
    maxPids: 64,
  },
  network: "allow_all",  // 开发时允许网络
  filesystem: {
    readOnly: false,
    allowPaths: [],
    tmpSizeMb: 256,
  },
  env: {
    allowList: ["PATH", "HOME", "LANG", "LC_ALL", "TZ", "PYTHONPATH", "NODE_PATH"],
    inject: { EVAL_SKILLS_SANDBOX: "dev" },
  },
  docker: {
    image: "python:3.12-slim",
    pullPolicy: "if-not-present",
    noNewPrivileges: false,
    user: "root",  // 开发镜像允许 root
  },
};
