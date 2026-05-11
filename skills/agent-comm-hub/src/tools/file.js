import { z } from "zod";
import { randomUUID } from "crypto";
import { attachStmt } from "../db.js";
import { messageRepo } from "../repo/sqlite-impl.js";
import { pushToAgent } from "../sse.js";
import { logError } from "../logger.js";
import { incrementMcpCall } from "../metrics.js";
import { existsSync, mkdirSync, writeFileSync, readFileSync } from "fs";
import { join as pathJoin } from "path";
import { requireAuth } from "../utils.js";
/**
 * 注册文件传输工具
 */
export function registerFileTools(server, authContext) {
    // ═══════════════════════════════════════════════════════════════
    // v2.3 Phase 1.1: 文件传输工具（3 个）
    // ═══════════════════════════════════════════════════════════════
    // --- Tool: upload_file ---
    // 上传文件附件并关联到消息 — member 及以上
    server.tool("upload_file", "上传文件附件并关联到消息。文件以 Base64 编码传入，服务端解码后存储到本地磁盘。", {
        message_id: z.string().describe("关联的消息 ID"),
        filename: z.string().describe("文件名（含扩展名）"),
        content_base64: z.string().describe("文件内容的 Base64 编码"),
        mime_type: z.string().default("application/octet-stream").describe("MIME 类型"),
    }, async ({ message_id, filename, content_base64, mime_type }) => {
        const ctx = requireAuth(authContext, "upload_file");
        try {
            // 验证消息存在
            const msg = messageRepo.getById(message_id);
            if (!msg) {
                return { content: [{ type: "text", text: JSON.stringify({ error: `Message ${message_id} not found` }) }] };
            }
            // Base64 解码
            const buffer = Buffer.from(content_base64, "base64");
            const fileSize = buffer.length;
            // 检查文件大小（10MB 限制）
            if (fileSize > 10 * 1024 * 1024) {
                return { content: [{ type: "text", text: JSON.stringify({ error: "File too large, max 10MB" }) }] };
            }
            // 生成存储路径
            const id = randomUUID();
            const uploadDir = process.env.UPLOAD_DIR || pathJoin(process.cwd(), "uploads");
            if (!existsSync(uploadDir))
                mkdirSync(uploadDir, { recursive: true });
            const storagePath = pathJoin(uploadDir, id);
            // 写入文件
            writeFileSync(storagePath, buffer);
            // 存入数据库
            attachStmt.insert.run({
                id,
                message_id,
                filename,
                mime_type,
                file_size: fileSize,
                storage_path: storagePath,
                uploaded_by: ctx.agentId,
                created_at: Date.now(),
            });
            // SSE 通知接收方
            pushToAgent(msg.to_agent, {
                type: "file_attached",
                attachment_id: id,
                message_id,
                filename,
                mime_type,
                file_size: fileSize,
                uploaded_by: ctx.agentId,
                created_at: Date.now(),
            });
            incrementMcpCall("upload_file", "success", ctx.role);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            attachment_id: id,
                            filename,
                            file_size: fileSize,
                            message_id,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("upload_file_error", err);
            return { content: [{ type: "text", text: JSON.stringify({ success: false, error: err.message }) }] };
        }
    });
    // --- Tool: download_file ---
    // 下载附件，返回 Base64 编码 — member 及以上
    server.tool("download_file", "下载附件，返回 Base64 编码的文件内容。", {
        attachment_id: z.string().describe("附件 ID"),
    }, async ({ attachment_id }) => {
        const ctx = requireAuth(authContext, "download_file");
        try {
            const attach = attachStmt.getById.get(attachment_id);
            if (!attach) {
                return { content: [{ type: "text", text: JSON.stringify({ error: `Attachment ${attachment_id} not found` }) }] };
            }
            if (!existsSync(attach.storage_path)) {
                return { content: [{ type: "text", text: JSON.stringify({ error: "File not found on disk" }) }] };
            }
            const buffer = readFileSync(attach.storage_path);
            incrementMcpCall("download_file", "success", ctx.role);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            attachment_id: attach.id,
                            filename: attach.filename,
                            mime_type: attach.mime_type,
                            file_size: attach.file_size,
                            content_base64: buffer.toString("base64"),
                            message_id: attach.message_id,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("download_file_error", err);
            return { content: [{ type: "text", text: JSON.stringify({ success: false, error: err.message }) }] };
        }
    });
    // --- Tool: list_attachments ---
    // 列出消息的附件列表 — member 及以上
    server.tool("list_attachments", "列出消息的所有附件列表。", {
        message_id: z.string().describe("消息 ID"),
    }, async ({ message_id }) => {
        const ctx = requireAuth(authContext, "list_attachments");
        try {
            const attachments = attachStmt.listByMessage.all(message_id);
            incrementMcpCall("list_attachments", "success", ctx.role);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            message_id,
                            attachments: attachments.map(a => ({
                                id: a.id,
                                filename: a.filename,
                                mime_type: a.mime_type,
                                file_size: a.file_size,
                                uploaded_by: a.uploaded_by,
                                created_at: a.created_at,
                            })),
                            count: attachments.length,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("list_attachments_error", err);
            return { content: [{ type: "text", text: JSON.stringify({ success: false, error: err.message }) }] };
        }
    });
}
//# sourceMappingURL=file.js.map