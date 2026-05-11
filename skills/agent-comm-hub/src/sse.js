import { logger } from "./logger.js";
// 在线 Agent 连接池
const clients = new Map();
// ─── 客户端去重：per-connection 递增 event_id ─────────────
const clientEventCounters = new Map();
function nextEventId(agentId) {
    const current = clientEventCounters.get(agentId) ?? 0;
    const next = current + 1;
    clientEventCounters.set(agentId, next);
    return next;
}
/**
 * 获取下一个 event_id（不递增，预览用）
 */
export function peekNextEventId(agentId) {
    return (clientEventCounters.get(agentId) ?? 0) + 1;
}
/**
 * 注册 Agent 的 SSE 连接
 */
export function registerClient(agentId, res) {
    // 如果已有旧连接，先关掉（Agent 重启场景）
    const existing = clients.get(agentId);
    if (existing) {
        try {
            existing.end();
        }
        catch (_) { }
    }
    clients.set(agentId, res);
    // 重置 event counter
    clientEventCounters.set(agentId, 0);
    logger.info("sse_client_connected", { module: "sse", agent_id: agentId, total: clients.size });
}
/**
 * 移除 Agent 连接（断线时调用）
 */
export function removeClient(agentId) {
    clients.delete(agentId);
    clientEventCounters.delete(agentId);
    logger.info("sse_client_disconnected", { module: "sse", agent_id: agentId, total: clients.size });
}
/**
 * 向指定 Agent 推送事件
 *
 * 每个推送附加递增的 event_id，客户端可据此实现去重：
 *   - event_id 是严格递增的
 *   - 客户端保存 last_seen_event_id，忽略 ≤ last_seen 的消息
 *
 * @param agentId 目标 Agent
 * @param event 事件数据（会被序列化为 JSON）
 * @param dedupId 可选的去重标识（如 msg_hash），附加到事件中供客户端验证
 * @returns true = 在线已推送；false = 离线，消息已持久化等待补发
 */
export function pushToAgent(agentId, event, dedupId) {
    const res = clients.get(agentId);
    if (!res)
        return false;
    try {
        const eventId = nextEventId(agentId);
        const payload = {
            ...event,
            _hub_event_id: eventId,
            ...(dedupId ? { _hub_dedup_id: dedupId } : {}),
        };
        // SSE 事件格式：id + event + data
        res.write(`id: ${eventId}\n`);
        res.write(`event: message\n`);
        res.write(`data: ${JSON.stringify(payload)}\n\n`);
        return true;
    }
    catch (err) {
        // 连接异常，移除
        removeClient(agentId);
        return false;
    }
}
/**
 * 广播给多个 Agent
 */
export function broadcast(agentIds, event) {
    const results = {};
    for (const id of agentIds) {
        results[id] = pushToAgent(id, event);
    }
    return results;
}
/**
 * 查询哪些 Agent 在线
 */
export function onlineAgents() {
    return [...clients.keys()];
}
/**
 * Phase 5b: 优雅关闭时 drain 所有 SSE 连接
 * 向每个客户端发送 close 事件后关闭连接
 */
export function drainAllClients() {
    for (const [agentId, res] of clients.entries()) {
        try {
            const eventId = nextEventId(agentId);
            res.write(`id: ${eventId}\n`);
            res.write(`event: hub_shutdown\n`);
            res.write(`data: {"message":"Server shutting down"}\n\n`);
            res.end();
        }
        catch { }
    }
    clients.clear();
    clientEventCounters.clear();
}
//# sourceMappingURL=sse.js.map