/**
 * utils.ts — MCP 工具共享工具函数
 * 从 tools.ts 提取，供 src/tools/ 下所有模块共用
 */
import { type AuthContext } from "./security.js";
export declare function withRetry<T>(fn: () => T, label: string, maxRetries?: number): Promise<T>;
/**
 * 创建带权限检查的工具包装器
 */
export declare function requireAuth(authContext: AuthContext | undefined, toolName: string): AuthContext;
