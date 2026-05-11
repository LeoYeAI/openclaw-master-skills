import { z } from "zod";
import { randomUUID } from "crypto";
import { consumedRepo } from "../repo/sqlite-impl.js";
import { logError } from "../logger.js";
import { withRetry, requireAuth } from "../utils.js";
export function registerConsumedTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // Tool 12: mark_consumed (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("mark_consumed", "记录 Agent 已处理某个资源（文件路径或信号 ID）。处理完 WorkBuddy 发来的任何文件或信号后必须调用，防止下次重复处理。", {
        agent_id: z.string().describe("执行方 Agent ID，如 hermes"),
        resource: z.string().describe("文件路径（相对 shared 目录）或信号 ID"),
        resource_type: z.enum(["file", "signal", "message"]).default("file"),
        action: z.string().describe("执行的动作，如 reviewed_and_replied / acknowledged / processed"),
        notes: z.string().optional().describe("处理说明，方便日后追溯"),
    }, async ({ agent_id, resource, resource_type, action, notes }) => {
        requireAuth(authContext, "mark_consumed");
        try {
            const entry = {
                id: randomUUID(),
                agent_id,
                resource,
                resource_type,
                action,
                notes: notes || null,
                consumed_at: Date.now(),
            };
            await withRetry(() => consumedRepo.insert(entry), "mark_consumed:insert");
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            resource,
                            resource_type,
                            action,
                            consumed_at: new Date(entry.consumed_at).toISOString(),
                            note: "已记录消费水位线，下次不会重复处理此资源",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("mark_consumed_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: err.message,
                            fallback: "水位线记录失败，建议稍后重试或检查 Hub 服务状态",
                        }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Tool 13: check_consumed (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("check_consumed", "查询某资源是否已被当前 Agent 处理过。在处理 WorkBuddy 发来的文件或信号前，先调用此工具检查，已处理的直接跳过。", {
        agent_id: z.string().describe("Agent ID，如 hermes"),
        resource: z.string().describe("文件路径或信号 ID"),
    }, async ({ agent_id, resource }) => {
        requireAuth(authContext, "check_consumed");
        try {
            const record = await withRetry(() => consumedRepo.check(agent_id, resource), "check_consumed:query");
            if (record) {
                return {
                    content: [{
                            type: "text",
                            text: JSON.stringify({
                                consumed: true,
                                resource,
                                action: record.action,
                                notes: record.notes,
                                consumed_at: new Date(record.consumed_at).toISOString(),
                                advice: "此资源已处理过，无需重复操作。如需重新处理，请通知 WorkBuddy 发送新版本。",
                            }, null, 2),
                        }],
                };
            }
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            consumed: false,
                            resource,
                            advice: "此资源尚未处理，可以正常处理。处理完成后请调用 mark_consumed 记录水位线。",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("check_consumed_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            consumed: false,
                            resource,
                            warning: `水位线查询失败: ${err.message}`,
                            advice: "无法确认是否已处理（查询出错），建议继续处理并在完成后调用 mark_consumed",
                        }, null, 2),
                    }],
            };
        }
    });
}
//# sourceMappingURL=consumed.js.map