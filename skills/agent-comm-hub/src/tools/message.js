import { z } from "zod";
import { randomUUID } from "crypto";
import { db } from "../db.js";
import { messageRepo } from "../repo/sqlite-impl.js";
import { pushToAgent } from "../sse.js";
import { auditLog } from "../security.js";
import { resolveAgentId } from "../identity.js";
import { dedupMessage, validateMessageBody } from "../dedup.js";
import { logError } from "../logger.js";
import { withRetry, requireAuth } from "../utils.js";
export function registerMessageTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // Tool 5: send_message (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("send_message", "向另一个 Agent 发送即时消息。对方在线时实时送达（<50ms），离线时持久化存储，上线后自动补发。", {
        from: z.string().describe("发送方 Agent ID，如 workbuddy 或 hermes"),
        to: z.string().describe("接收方 Agent ID"),
        content: z.string().describe("消息正文，支持 Markdown"),
        type: z.enum(["message", "task_assign", "task_update", "ack"])
            .default("message")
            .describe("消息类型"),
        metadata: z.record(z.unknown()).optional()
            .describe("附加结构化数据，如 taskId、priority 等"),
    }, async ({ from, to, content, type, metadata }) => {
        const ctx = requireAuth(authContext, "send_message");
        // ── from_agent 格式规范化（Phase 2.1） ────────────────
        const resolvedFrom = resolveAgentId(from);
        if (!resolvedFrom) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: `无效的发件人标识: '${from}'。请使用完整的 agent_id 或已注册的 agent 名称。`,
                            code: "INVALID_FROM_AGENT",
                        }),
                    }],
                isError: true,
            };
        }
        const resolvedTo = resolveAgentId(to);
        if (!resolvedTo) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: `无效的收件人标识: '${to}'。请使用完整的 agent_id 或已注册的 agent 名称。`,
                            code: "INVALID_TO_AGENT",
                        }),
                    }],
                isError: true,
            };
        }
        // 消息去重 + 完整性校验
        const dedupResult = dedupMessage(from, to, content);
        if (!dedupResult.ok) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: dedupResult.reason,
                            code: "DEDUP_REJECTED",
                        }),
                    }],
            };
        }
        const msg = {
            id: randomUUID(),
            from_agent: resolvedFrom,
            to_agent: resolvedTo,
            content,
            type,
            metadata: metadata ? JSON.stringify(metadata) : null,
            status: "unread",
            created_at: Date.now(),
        };
        messageRepo.insert(msg);
        // 审计日志
        auditLog("tool_send_message", ctx.agentId, resolvedTo, `msg_id=${msg.id}, hash=${dedupResult.msgHash.slice(0, 12)}, nonce=${dedupResult.nonce}`);
        const delivered = pushToAgent(resolvedTo, {
            event: "new_message",
            message: { ...msg, metadata, msg_hash: dedupResult.msgHash, nonce: dedupResult.nonce },
        });
        if (delivered)
            messageRepo.markDelivered(msg.id);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        messageId: msg.id,
                        msg_hash: dedupResult.msgHash,
                        nonce: dedupResult.nonce,
                        delivered_realtime: delivered,
                        note: delivered
                            ? `✅ ${resolvedTo} 在线，已实时送达`
                            : `📦 ${resolvedTo} 离线，消息已存储，上线后自动补发`,
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Tool 9: broadcast_message (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("broadcast_message", "向多个 Agent 广播消息，适用于任务协调、状态同步、紧急通知。", {
        from: z.string(),
        agent_ids: z.array(z.string()).describe("接收方 Agent ID 列表"),
        content: z.string(),
        metadata: z.record(z.unknown()).optional(),
    }, async ({ from, agent_ids, content, metadata }) => {
        const ctx = requireAuth(authContext, "broadcast_message");
        // 消息体校验
        const validation = validateMessageBody(content);
        if (!validation.safe) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: validation.reason,
                            code: "VALIDATION_REJECTED",
                        }),
                    }],
            };
        }
        const results = {};
        const errors = [];
        let deliveredCount = 0;
        for (const to of agent_ids) {
            // 每个接收者独立去重
            const dedupResult = dedupMessage(from, to, content);
            if (!dedupResult.ok) {
                errors.push(`${to}: ${dedupResult.reason}`);
                results[to] = false;
                continue;
            }
            const msg = {
                id: randomUUID(),
                from_agent: from,
                to_agent: to,
                content,
                type: "message",
                metadata: metadata ? JSON.stringify(metadata) : null,
                status: "unread",
                created_at: Date.now(),
            };
            messageRepo.insert(msg);
            const delivered = pushToAgent(to, {
                event: "new_message",
                message: { ...msg, metadata, msg_hash: dedupResult.msgHash, nonce: dedupResult.nonce },
            });
            if (delivered) {
                messageRepo.markDelivered(msg.id);
                deliveredCount++;
            }
            results[to] = delivered;
        }
        auditLog("tool_broadcast_message", ctx.agentId, agent_ids.join(","), `total=${agent_ids.length}, delivered=${deliveredCount}, errors=${errors.length}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        broadcast: true,
                        delivery_status: results,
                        delivered_count: deliveredCount,
                        duplicate_count: errors.length,
                        errors: errors.length > 0 ? errors : undefined,
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Tool 11: acknowledge_message (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("acknowledge_message", "标记消息为已处理（acknowledged）。调用此工具后该消息不会再出现在未处理消息列表中。Hermes 处理完 WorkBuddy 发来的消息并回复后，必须调用此工具。", {
        message_id: z.string().describe("消息 ID"),
        agent_id: z.string().describe("确认方 Agent ID，如 hermes"),
    }, async ({ message_id, agent_id }) => {
        requireAuth(authContext, "acknowledge_message");
        try {
            const msg = await withRetry(() => messageRepo.getById(message_id), "acknowledge_message:lookup");
            if (!msg) {
                return {
                    content: [{
                            type: "text",
                            text: JSON.stringify({ error: `Message ${message_id} not found`, suggestion: "请检查 message_id 是否正确" }),
                        }],
                };
            }
            await withRetry(() => messageRepo.markAcknowledged(message_id), "acknowledge_message:update");
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            message_id,
                            agent_id,
                            status: "acknowledged",
                            note: "此消息已标记为已处理，不会重复出现在待处理列表中",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("acknowledge_message_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: err.message,
                            fallback: "标记失败，消息仍为当前状态，请稍后重试",
                        }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Tool S1: search_messages — member 及以上
    // ────────────────────────────────────────────────────
    server.tool("search_messages", "全文搜索消息内容。支持按 Agent ID 筛选。使用 SQL LIKE 模糊匹配（暂无 FTS5 索引）。", {
        query: z.string().describe("搜索关键词"),
        agent_id: z.string().optional().describe("限定 Agent ID（按发送方或接收方过滤）"),
        limit: z.number().min(1).max(50).optional().default(10).describe("最大返回数量"),
    }, async ({ query, agent_id, limit }) => {
        const ctx = requireAuth(authContext, "search_messages");
        try {
            const conditions = ["content LIKE ?"];
            const params = [`%${query}%`];
            if (agent_id) {
                conditions.push("(from_agent = ? OR to_agent = ?)");
                params.push(agent_id, agent_id);
            }
            const where = conditions.join(" AND ");
            const messages = db.prepare(`SELECT id, from_agent, to_agent, content, type, status, created_at
           FROM messages WHERE ${where}
           ORDER BY created_at DESC LIMIT ?`).all(...params, limit);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            query,
                            agent_id: agent_id ?? null,
                            messages: messages.map(m => ({
                                id: m.id,
                                from_agent: m.from_agent,
                                to_agent: m.to_agent,
                                content: m.content,
                                type: m.type,
                                status: m.status,
                                created_at: m.created_at,
                            })),
                            count: messages.length,
                            queried_by: ctx.agentId,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Tool: batch_acknowledge_messages (Phase 1.3)
    // 批量确认消息
    // ────────────────────────────────────────────────────
    server.tool("batch_acknowledge_messages", "批量确认消息为已处理。可按 agent_id 和时间范围筛选，将匹配的未确认消息全部标记为 acknowledged。用于清理消息积压。", {
        agent_id: z.string().describe("目标 Agent ID（消息接收方），即要清理谁的未读消息"),
        from_agent: z.string().optional().describe("发送方 Agent ID 过滤（可选），只确认来自特定发送方的消息"),
        before: z.number().optional().describe("时间戳上限（毫秒），只确认此时间之前的消息"),
        after: z.number().optional().describe("时间戳下限（毫秒），只确认此时间之后的消息"),
        status: z.enum(["unread", "delivered"]).optional().default("unread").describe("要确认的消息状态，默认 unread"),
        limit: z.number().int().min(1).max(500).default(100).describe("最多确认的消息数量，默认 100，上限 500"),
    }, async ({ agent_id, from_agent, before, after, status, limit }) => {
        const ctx = requireAuth(authContext, "batch_acknowledge_messages");
        try {
            // 构建查询条件
            const conditions = ["to_agent = ?"];
            const params = [agent_id];
            if (from_agent) {
                conditions.push("from_agent = ?");
                params.push(from_agent);
            }
            if (before !== undefined) {
                conditions.push("created_at < ?");
                params.push(before);
            }
            if (after !== undefined) {
                conditions.push("created_at > ?");
                params.push(after);
            }
            // 只确认非 acknowledged 状态的消息
            if (status === "delivered") {
                conditions.push("status = 'delivered'");
            }
            else {
                conditions.push("status IN ('unread', 'delivered')");
            }
            const whereClause = conditions.join(" AND ");
            // 先查询匹配的消息数量
            const countResult = db.prepare(`SELECT COUNT(*) as cnt FROM messages WHERE ${whereClause}`).get(...params);
            const totalCount = countResult?.cnt ?? 0;
            const actualLimit = Math.min(limit, totalCount);
            if (actualLimit === 0) {
                return {
                    content: [{
                            type: "text",
                            text: JSON.stringify({
                                success: true,
                                agent_id,
                                acknowledged_count: 0,
                                total_matching: 0,
                                filters: { from_agent, before, after, status },
                                note: "没有匹配的未确认消息",
                            }, null, 2),
                        }],
                };
            }
            // 批量更新：使用子查询限制更新行数
            const updateResult = db.prepare(`UPDATE messages SET status = 'acknowledged' WHERE ${whereClause} AND rowid IN (
            SELECT rowid FROM messages WHERE ${whereClause} LIMIT ?
          )`).run(...params, ...params, actualLimit);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            agent_id,
                            acknowledged_count: updateResult.changes,
                            total_matching: totalCount,
                            filters: { from_agent, before, after, status },
                            note: updateResult.changes < totalCount
                                ? `已确认 ${updateResult.changes} 条（达到 limit ${limit} 上限），可再次调用继续清理`
                                : `全部 ${totalCount} 条匹配消息已确认`,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("batch_acknowledge_messages_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
}
//# sourceMappingURL=message.js.map