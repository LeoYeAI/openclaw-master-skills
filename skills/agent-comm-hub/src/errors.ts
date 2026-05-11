/**
 * errors.ts — 统一错误码体系
 * Phase D: 替换散落的 new Error()，提供结构化错误信息
 */

// ─── 错误码枚举 ────────────────────────────────────────────

export enum HubErrorCode {
  // 通用 1xxx
  UNKNOWN            = "HUB_1000",
  INTERNAL           = "HUB_1001",
  NOT_FOUND          = "HUB_1002",
  VALIDATION         = "HUB_1003",
  ALREADY_EXISTS     = "HUB_1004",
  UNREACHABLE        = "HUB_1005",

  // 认证/权限 2xxx
  AUTH_REQUIRED      = "HUB_2000",
  PERMISSION_DENIED  = "HUB_2001",
  TOKEN_EXPIRED      = "HUB_2002",
  TOKEN_INVALID      = "HUB_2003",

  // Agent 3xxx
  AGENT_NOT_FOUND    = "HUB_3000",
  AGENT_OFFLINE      = "HUB_3001",
  INVALID_ROLE       = "HUB_3002",

  // 任务/编排 4xxx
  TASK_NOT_FOUND     = "HUB_4000",
  INVALID_TRANSITION = "HUB_4001",
  CYCLE_DETECTED     = "HUB_4002",
  DEPENDENCY_EXISTS  = "HUB_4003",
  DEPENDENCY_NOT_FOUND = "HUB_4004",
  HANDOFF_NOT_TARGET = "HUB_4005",
  GATE_NOT_FOUND     = "HUB_4006",
  GATE_ALREADY_EVAL  = "HUB_4007",
  PARALLEL_MIN_TASKS = "HUB_4008",
  PARALLEL_MAX_TASKS = "HUB_4009",
  GROUP_NOT_FOUND    = "HUB_4010",

  // Pipeline 5xxx
  PIPELINE_NOT_FOUND = "HUB_5000",

  // 消息 6xxx
  MESSAGE_SEND_FAIL  = "HUB_6000",

  // 数据库 7xxx
  DB_ERROR           = "HUB_7000",
  DB_INTEGRITY       = "HUB_7001",
}

// ─── HubError 类 ────────────────────────────────────────────

export class HubError extends Error {
  readonly code: HubErrorCode;
  readonly details?: Record<string, unknown>;

  constructor(code: HubErrorCode, message: string, details?: Record<string, unknown>) {
    super(message);
    this.name = "HubError";
    this.code = code;
    this.details = details;
  }

  /** 序列化为 MCP 工具返回格式 */
  toJSON(): { error: true; code: string; message: string; details?: Record<string, unknown> } {
    return {
      error: true,
      code: this.code,
      message: this.message,
      ...(this.details && { details: this.details }),
    };
  }

  /** 从 unknown 判断是否为 HubError */
  static isHubError(err: unknown): err is HubError {
    return err instanceof HubError;
  }
}

// ─── 工厂函数（简化常见错误创建） ────────────────────────────

export function notFound(resource: string, id: string): HubError {
  return new HubError(HubErrorCode.NOT_FOUND, `${resource} not found: ${id}`, { resource, id });
}

export function alreadyExists(resource: string, id?: string): HubError {
  return new HubError(HubErrorCode.ALREADY_EXISTS, `${resource} already exists${id ? `: ${id}` : ""}`, { resource, id });
}

export function validation(msg: string, details?: Record<string, unknown>): HubError {
  return new HubError(HubErrorCode.VALIDATION, msg, details);
}

export function permissionDenied(tool: string, required: string, actual: string): HubError {
  return new HubError(
    HubErrorCode.PERMISSION_DENIED,
    `Permission denied: ${tool} requires '${required}' role, current role is '${actual}'`,
    { tool, required, actual },
  );
}

export function authRequired(tool?: string): HubError {
  return new HubError(HubErrorCode.AUTH_REQUIRED, tool ? `Authentication required for tool: ${tool}` : "Authentication required", { tool });
}
