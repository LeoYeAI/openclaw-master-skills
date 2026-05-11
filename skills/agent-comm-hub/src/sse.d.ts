/**
 * sse.ts — SSE 连接管理 (Phase 1 Week 2 增强)
 * 维护 AgentID → Response 映射，实现零轮询实时推送
 *
 * Week 2 增强：
 *   - pushToAgent 支持可选的 dedup_id，用于客户端去重
 *   - 每个 SSE 事件附加 event_id（递增），客户端可据此去重
 */
import type { Response } from "express";
/**
 * 获取下一个 event_id（不递增，预览用）
 */
export declare function peekNextEventId(agentId: string): number;
/**
 * 注册 Agent 的 SSE 连接
 */
export declare function registerClient(agentId: string, res: Response): void;
/**
 * 移除 Agent 连接（断线时调用）
 */
export declare function removeClient(agentId: string): void;
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
export declare function pushToAgent(agentId: string, event: object, dedupId?: string): boolean;
/**
 * 广播给多个 Agent
 */
export declare function broadcast(agentIds: string[], event: object): Record<string, boolean>;
/**
 * 查询哪些 Agent 在线
 */
export declare function onlineAgents(): string[];
/**
 * Phase 5b: 优雅关闭时 drain 所有 SSE 连接
 * 向每个客户端发送 close 事件后关闭连接
 */
export declare function drainAllClients(): void;
