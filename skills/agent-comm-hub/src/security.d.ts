import type { Request, Response, NextFunction } from "express";
declare global {
    namespace Express {
        interface Request {
            auth?: {
                agent?: AuthContext | undefined;
            };
        }
    }
}
export type AgentRole = "admin" | "member" | "group_admin";
export interface AuthContext {
    agentId: string;
    role: AgentRole;
}
/** SHA-256 哈希 */
export declare function sha256(input: string): string;
/** 生成明文 Token（一次性返回） */
export declare function generateToken(): string;
/** 验证 Token 并返回 AuthContext，失败返回 null */
export declare function verifyToken(plainToken: string): AuthContext | null;
export declare function rateLimiter(agentId: string): boolean;
/** 工具访问级别 */
type PermissionLevel = "public" | "member" | "admin";
export declare const TOOL_PERMISSIONS: Record<string, PermissionLevel>;
/**
 * 检查工具调用权限
 * group_admin 权限等同于 member（仅任务相关工具），其余 admin 工具不可用
 * @returns true=允许, false=拒绝
 */
export declare function checkPermission(toolName: string, role: AgentRole): boolean;
/**
 * 获取权限级别（用于返回错误信息）
 */
export declare function getRequiredPermission(toolName: string): PermissionLevel | undefined;
/**
 * 强制认证中间件 — 所有 API/MCP 端点使用
 * 无有效 Token → 401
 */
export declare function authMiddleware(req: Request, res: Response, next: NextFunction): void;
/**
 * 可选认证中间件 — SSE 端点使用
 * 有 Token 则验证，无 Token 则 auth = undefined
 * ⚠️ 关键：未认证时 auth 必须为 undefined，不能创建默认 authContext
 */
export declare function optionalAuthMiddleware(req: Request, res: Response, next: NextFunction): void;
/**
 * 生成邀请码（明文）
 * @returns 明文邀请码
 */
export declare function generateInviteCode(): string;
/**
 * 创建邀请码记录
 * @returns 明文邀请码（唯一一次可见）
 */
export declare function createInviteCode(role?: "admin" | "member"): string;
/**
 * 验证邀请码并标记已使用
 * @returns 有效邀请码的角色，或 null
 */
export declare function verifyInviteCode(plainCode: string): "admin" | "member" | null;
/**
 * 标记邀请码已使用
 */
export declare function markInviteCodeUsed(plainCode: string): void;
/**
 * 吊销 API Token
 */
export declare function revokeToken(tokenId: string): boolean;
/**
 * 记录审计日志（带哈希链）
 * 每条记录包含 prev_hash 和 record_hash，形成不可篡改链
 */
export declare function auditLog(action: string, agentId: string | null, target?: string, details?: string): void;
/**
 * 验证审计日志哈希链完整性
 * @returns { valid, total, checked, firstBreak } — valid=true 表示链完整
 */
export declare function verifyAuditChain(): {
    valid: boolean;
    total: number;
    checked: number;
    firstBreak?: {
        id: string;
        action: string;
        expected: string;
        actual: string;
    };
};
/**
 * 重新计算 Agent 信任评分
 *
 * 公式：
 *   base = 50
 *   + verified_capabilities × 3
 *   + auto_approved_strategies × 2
 *   + positive_feedback × 1
 *   - negative_feedback × 2
 *   - rejected_applications × 3
 *   - revoked_token_count × 10
 *   → clamp(0, 100)
 *
 * @returns 计算后的信任分数
 */
export declare function recalculateTrustScore(agentId: string): number;
/**
 * 重新计算所有 Agent 的信任评分
 * @returns { agent_id, score } 数组
 */
export declare function recalculateAllTrustScores(): Array<{
    agent_id: string;
    score: number;
}>;
/**
 * 检查路径是否安全（防止路径遍历）
 */
export declare function sanitizePath(inputPath: string): boolean;
export {};
