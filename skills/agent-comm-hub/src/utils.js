import { checkPermission, getRequiredPermission } from "./security.js";
import { logError } from "./logger.js";
// ─── 通用工具：带指数退避的重试 ──────────────────────────
export async function withRetry(fn, label, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return fn();
        }
        catch (err) {
            const isLast = attempt === maxRetries;
            logError("withRetry_failed", err, { label, attempt, maxRetries });
            if (isLast)
                throw err;
            const delay = Math.pow(2, attempt - 1) * 100;
            await new Promise(r => setTimeout(r, delay));
        }
    }
    throw new Error(`unreachable`);
}
/**
 * 创建带权限检查的工具包装器
 */
export function requireAuth(authContext, toolName) {
    if (!authContext) {
        throw new Error(`Authentication required for tool: ${toolName}`);
    }
    if (!checkPermission(toolName, authContext.role)) {
        const required = getRequiredPermission(toolName) ?? "member";
        throw new Error(`Permission denied: ${toolName} requires '${required}' role, current role is '${authContext.role}'`);
    }
    return authContext;
}
//# sourceMappingURL=utils.js.map