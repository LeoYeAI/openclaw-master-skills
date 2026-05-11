/**
 * utils.ts — MCP 工具共享工具函数
 * 从 tools.ts 提取，供 src/tools/ 下所有模块共用
 */
import { type AuthContext } from "./security.js";
import { checkPermission, getRequiredPermission } from "./security.js";
import { logError } from "./logger.js";
import { getErrorMessage } from "./types.js";
import { HubError } from "./errors.js";

// ─── 通用工具：带指数退避的重试 ──────────────────────────
export async function withRetry<T>(
  fn: () => T,
  label: string,
  maxRetries = 3,
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return fn();
    } catch (err: unknown) {
      const isLast = attempt === maxRetries;
      logError("withRetry_failed", err, { label, attempt, maxRetries });
      if (isLast) throw err;
      const delay = Math.pow(2, attempt - 1) * 100;
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error(`unreachable`);
}

/**
 * 创建带权限检查的工具包装器
 */
export function requireAuth(
  authContext: AuthContext | undefined,
  toolName: string
): AuthContext {
  if (!authContext) {
    throw new Error(`Authentication required for tool: ${toolName}`);
  }
  if (!checkPermission(toolName, authContext.role)) {
    const required = getRequiredPermission(toolName) ?? "member";
    throw new Error(
      `Permission denied: ${toolName} requires '${required}' role, current role is '${authContext.role}'`
    );
  }
  return authContext;
}

// ─── MCP 工具错误返回统一格式 ─────────────────────────────

/** MCP 工具 catch 块返回的统一格式（兼容 MCP SDK Tool callback 返回类型） */
export interface McpErrorContent {
  content: [{ type: "text"; text: string }];
  isError?: boolean;
  [x: string]: unknown;
}

/**
 * 构建统一 MCP 错误返回
 * HubError → 结构化 JSON（含 code）
 * 其他 Error → 简单 JSON（含 error + message）
 * unknown   → 简单 JSON（String(err)）
 */
export function mcpError(err: unknown, toolName?: string): McpErrorContent {
  if (HubError.isHubError(err)) {
    return {
      content: [{ type: "text", text: JSON.stringify(err.toJSON()) }],
      isError: true,
    };
  }
  const message = getErrorMessage(err);
  const payload = { error: true, message };
  if (toolName) (payload as Record<string, unknown>).tool = toolName;
  return {
    content: [{ type: "text", text: JSON.stringify(payload) }],
    isError: true,
  };
}

/**
 * 构建统一 MCP 验证失败返回（非异常，用于 result.ok === false）
 * 将 { success: false, error: string } 统一为 McpErrorContent
 */
export function mcpFail(error: string, toolName?: string): McpErrorContent {
  const payload = { error: true, message: error };
  if (toolName) (payload as Record<string, unknown>).tool = toolName;
  return {
    content: [{ type: "text", text: JSON.stringify(payload) }],
    isError: true,
  };
}
