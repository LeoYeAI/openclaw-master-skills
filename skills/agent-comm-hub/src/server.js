/**
 * server.ts — 主入口
 * Express HTTP 服务器 + MCP Server + SSE 推送 + Security 中间件
 *
 * Phase 5b 变更：
 *   - 结构化 JSON 日志（logger.ts）
 *   - 全局错误处理中间件
 *   - 增强健康检查（/health）
 *   - 优雅关闭（SIGTERM/SIGINT）
 *   - Prometheus metrics 端点（/metrics）
 *   - CORS + 安全头中间件
 *   - 请求追踪（traceId）
 */
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { registerTools } from "./tools.js";
import { registerClient, removeClient, pushToAgent, onlineAgents, drainAllClients } from "./sse.js";
import { getDbStats, db, scheduleCleanup, stopCleanup } from "./db.js";
import { messageRepo, taskRepo, consumedRepo } from "./repo/sqlite-impl.js";
import { authMiddleware, optionalAuthMiddleware, createInviteCode, auditLog, rateLimiter, } from "./security.js";
import { startHeartbeatMonitor, stopHeartbeatMonitor } from "./identity.js";
import { startDedupCleanup, stopDedupCleanup } from "./dedup.js";
import { rebuildFtsIndex } from "./memory.js";
import { logger, logError } from "./logger.js";
import { join } from "path";
import { getMetricsOutput, trackHttpRequest, incrementGauge, decrementGauge, collectHubMetrics, } from "./metrics.js";
// ═══════════════════════════════════════════════════════════════
// Phase 6: 配置外部化（零依赖，所有配置有默认值）
// ═══════════════════════════════════════════════════════════════
const config = {
    port: parseInt(process.env.PORT ?? "3100", 10),
    logLevel: process.env.LOG_LEVEL || "info",
    corsOrigins: (process.env.CORS_ORIGINS ?? "").split(",").map(s => s.trim()).filter(Boolean),
    dbPath: process.env.DB_PATH || "./comm_hub.db",
    sseHeartbeatInterval: parseInt(process.env.SSE_HEARTBEAT_INTERVAL ?? "10000", 10),
    sseReplayWindow: parseInt(process.env.SSE_REPLAY_WINDOW ?? "3600", 10) * 1000,
    rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW ?? "1000", 10),
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX ?? "10", 10),
    heartbeatOnlineThreshold: parseInt(process.env.HEARTBEAT_ONLINE_THRESHOLD ?? "90000", 10),
    heartbeatNotifyThreshold: parseInt(process.env.HEARTBEAT_NOTIFY_THRESHOLD ?? "300000", 10),
    heartbeatCheckInterval: parseInt(process.env.HEARTBEAT_CHECK_INTERVAL ?? "30000", 10),
    dedupTTL: parseInt(process.env.DEDUP_TTL ?? "900", 10) * 1000,
    dedupCleanupInterval: parseInt(process.env.DEDUP_CLEANUP_INTERVAL ?? "60000", 10),
    tokenExpireDays: parseInt(process.env.TOKEN_EXPIRE_DAYS ?? "90", 10),
    uploadDir: process.env.UPLOAD_DIR || join(process.cwd(), "uploads"),
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE ?? "10485760", 10), // 10MB
};
const app = express();
app.use(express.json());
// ═══════════════════════════════════════════════════════════════
// Phase 5b: CORS 中间件（零依赖）
// ═══════════════════════════════════════════════════════════════
const CORS_ORIGINS = config.corsOrigins;
app.use((req, res, next) => {
    const origin = req.headers.origin;
    if (origin && CORS_ORIGINS.includes(origin)) {
        res.setHeader("Access-Control-Allow-Origin", origin);
        res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, PATCH, OPTIONS");
        res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Trace-Id, X-Api-Key");
        res.setHeader("Access-Control-Max-Age", "86400");
    }
    if (req.method === "OPTIONS") {
        return res.sendStatus(204);
    }
    next();
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 安全头中间件（零依赖 Helmet 替代）
// ═══════════════════════════════════════════════════════════════
app.use((_req, res, next) => {
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("X-XSS-Protection", "1; mode=block");
    res.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    res.setHeader("Content-Security-Policy", "default-src 'self'");
    next();
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 请求追踪（traceId）
// ═══════════════════════════════════════════════════════════════
app.use((req, res, next) => {
    const traceId = req.headers["x-trace-id"] || crypto.randomUUID().slice(0, 8);
    req.traceId = traceId;
    res.setHeader("X-Trace-Id", traceId);
    next();
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: HTTP 请求日志 + metrics 中间件
// ═══════════════════════════════════════════════════════════════
app.use((req, res, next) => {
    const start = Date.now();
    res.on("finish", () => {
        const duration = Date.now() - start;
        const traceId = req.traceId;
        logger.info("http_request", {
            traceId,
            module: "server",
            method: req.method,
            path: req.path,
            status: res.statusCode,
            duration_ms: duration,
        });
        trackHttpRequest(req.method, req.path, res.statusCode, duration);
    });
    next();
});
// ═══════════════════════════════════════════════════════════════
// SSE 端点：Agent 启动时订阅一次，保持长连接
// GET /events/:agent_id?token=<api_token>
// ═══════════════════════════════════════════════════════════════
// SSE 重连回放窗口（秒），默认 1 小时
const SSE_REPLAY_WINDOW = config.sseReplayWindow;
app.get("/events/:agent_id", optionalAuthMiddleware, (req, res) => {
    const { agent_id } = req.params;
    const authContext = req.auth?.agent;
    // SSE 必要响应头
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("X-Accel-Buffering", "no");
    res.flushHeaders();
    // 注册连接
    registerClient(agent_id, res);
    incrementGauge("active_sse_connections");
    // 检查 Last-Event-ID（断线重连场景）
    const lastEventId = req.headers["last-event-id"];
    if (lastEventId) {
        // 解析 lastEventId 为时间戳（毫秒）
        const since = parseInt(lastEventId, 10);
        if (!isNaN(since)) {
            // 检查是否在回放窗口内
            const now = Date.now();
            const windowStart = now - SSE_REPLAY_WINDOW;
            const effectiveSince = Math.max(since, windowStart);
            // 查询并回放该时间戳之后的消息
            const missedMessages = messageRepo.listSince(agent_id, effectiveSince);
            if (missedMessages.length > 0) {
                for (const msg of missedMessages) {
                    pushToAgent(agent_id, {
                        event: "new_message",
                        message: msg,
                    });
                }
                logger.info("SSE replay", { module: "sse", agent_id, replay_count: missedMessages.length, since: effectiveSince });
            }
        }
    }
    else {
        // 首次连接：补发离线期间积压的未读消息
        const pending = messageRepo.pendingFor(agent_id);
        if (pending.length > 0) {
            for (const msg of pending) {
                pushToAgent(agent_id, {
                    event: "new_message",
                    message: msg,
                });
            }
            messageRepo.markAllDelivered(agent_id);
            logger.info("SSE backfill", { module: "sse", agent_id, pending_count: pending.length });
        }
    }
    // 补发积压的未执行任务
    const pendingTasks = taskRepo.listFor(agent_id, "pending");
    for (const task of pendingTasks) {
        pushToAgent(agent_id, {
            event: "task_assigned",
            task: {
                ...task,
                instruction: "你有一项待执行的任务，请立即处理。",
            },
        });
    }
    if (pendingTasks.length > 0) {
        logger.info("SSE tasks push", { module: "sse", agent_id, pending_tasks: pendingTasks.length });
    }
    // 心跳（10 秒间隔）
    const heartbeat = setInterval(() => {
        try {
            res.write(": ping\n\n");
        }
        catch (_) {
            clearInterval(heartbeat);
        }
    }, config.sseHeartbeatInterval);
    // 断线清理
    req.on("close", () => {
        clearInterval(heartbeat);
        removeClient(agent_id);
        decrementGauge("active_sse_connections");
    });
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 增强健康检查端点（免认证）
// ═══════════════════════════════════════════════════════════════
app.get("/health", (_req, res) => {
    const stats = getDbStats();
    const mem = process.memoryUsage();
    let dbSize = 0;
    try {
        const row = db.prepare(`SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()`).get();
        dbSize = row?.size ?? 0;
    }
    catch { }
    res.json({
        status: "ok",
        version: "2.3.1",
        uptime: process.uptime(),
        timestamp: Date.now(),
        memory: {
            rss: Math.round(mem.rss / 1024 / 1024),
            heap_used: Math.round(mem.heapUsed / 1024 / 1024),
            heap_total: Math.round(mem.heapTotal / 1024 / 1024),
        },
        db: {
            size: dbSize,
            size_mb: Math.round(dbSize / 1024 / 1024 * 100) / 100,
            tables: stats,
        },
        sse: {
            active_connections: onlineAgents().length,
        },
    });
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: Prometheus Metrics 端点（免认证）
// ═══════════════════════════════════════════════════════════════
app.get("/metrics", (_req, res) => {
    res.setHeader("Content-Type", "text/plain; version=0.0.4; charset=utf-8");
    // Phase 3.1: 拼接 Hub 数据库指标（agents / messages / trust_scores）
    const hubMetrics = collectHubMetrics(db);
    const output = getMetricsOutput() + hubMetrics;
    res.send(output);
});
// ═══════════════════════════════════════════════════════════════
// 管理端点：/admin/invite/generate — 生成邀请码
// ═══════════════════════════════════════════════════════════════
app.post("/admin/invite/generate", authMiddleware, (req, res) => {
    const role = req.auth?.agent?.role;
    if (role !== "admin") {
        res.status(403).json({ error: "Admin access required" });
        return;
    }
    const targetRole = req.body.role === "admin" ? "admin" : "member";
    const code = createInviteCode(targetRole);
    auditLog("invite_generated", req.auth?.agent?.agentId ?? null, undefined, `role=${targetRole}`);
    res.json({
        success: true,
        invite_code: code,
        role: targetRole,
        expires_in: "24h",
    });
});
// ═══════════════════════════════════════════════════════════════
// REST API：供自动化脚本通过 curl 轮询任务和消息（需认证）
// ═══════════════════════════════════════════════════════════════
// GET /api/tasks?agent_id=workbuddy&status=pending
app.get("/api/tasks", authMiddleware, (req, res) => {
    const { agent_id, status } = req.query;
    if (!agent_id) {
        res.status(400).json({ error: "agent_id is required" });
        return;
    }
    if (status && !["pending", "in_progress", "completed", "failed"].includes(status)) {
        res.status(400).json({ error: `Invalid status: ${status}` });
        return;
    }
    const tasks = status
        ? taskRepo.listFor(agent_id, status)
        : taskRepo.listFor(agent_id, "pending");
    res.json({ tasks, count: tasks.length });
});
// GET /api/messages?agent_id=workbuddy&status=unread
app.get("/api/messages", authMiddleware, (req, res) => {
    const { agent_id, status } = req.query;
    if (!agent_id) {
        res.status(400).json({ error: "agent_id is required" });
        return;
    }
    const validStatuses = ["unread", "delivered", "read", "acknowledged"];
    if (status && !validStatuses.includes(status)) {
        res.status(400).json({ error: `Invalid status: ${status}. Valid: ${validStatuses.join(", ")}` });
        return;
    }
    const queryStatus = status || "unread";
    const messages = messageRepo.listByStatus(agent_id, queryStatus);
    res.json({ messages, count: messages.length });
});
// PATCH /api/tasks/:id/status
app.patch("/api/tasks/:id/status", authMiddleware, (req, res) => {
    const { status, result, progress } = req.body;
    if (!["in_progress", "completed", "failed"].includes(status)) {
        res.status(400).json({ error: `Invalid status: ${status}` });
        return;
    }
    const task = taskRepo.getById(req.params.id);
    if (!task) {
        res.status(404).json({ error: "Task not found" });
        return;
    }
    taskRepo.update(req.params.id, status, result || null, progress || 0);
    pushToAgent(task.assigned_by, {
        event: "task_updated",
        update: {
            task_id: task.id,
            status,
            result: result || null,
            progress: progress || 0,
            updated_by: "workbuddy-automation",
            timestamp: Date.now(),
        },
    });
    res.json({ success: true, task_id: task.id, status });
});
// PATCH /api/messages/:id/status
app.patch("/api/messages/:id/status", authMiddleware, (req, res) => {
    const { status } = req.body;
    const validStatuses = ["read", "delivered", "acknowledged"];
    if (!validStatuses.includes(status)) {
        res.status(400).json({ error: `Invalid status: ${status}. Valid: ${validStatuses.join(", ")}` });
        return;
    }
    try {
        messageRepo.updateStatus(req.params.id, status);
        res.json({ success: true, message_id: req.params.id, status });
    }
    catch (err) {
        res.status(500).json({ error: err.message });
    }
});
// GET /api/consumed?agent_id=hermes&resource=feedback/xxx.json
app.get("/api/consumed", authMiddleware, (req, res) => {
    const { agent_id, resource } = req.query;
    if (!agent_id) {
        res.status(400).json({ error: "agent_id is required" });
        return;
    }
    if (resource) {
        const record = consumedRepo.check(agent_id, resource);
        res.json({
            consumed: !!record,
            resource,
            record: record || null,
        });
    }
    else {
        const records = consumedRepo.listByAgent(agent_id, 50);
        res.json({ records, count: records.length });
    }
});
// ═══════════════════════════════════════════════════════════════
// MCP 端点：Stateless 模式
// ═══════════════════════════════════════════════════════════════
function createMcpServer(authContext) {
    const server = new McpServer({
        name: "agent-comm-hub",
        version: "2.3.1",
    });
    registerTools(server, authContext);
    return server;
}
function extractToolName(req) {
    try {
        const body = req.body;
        if (body?.method === "tools/call" && body?.params?.name) {
            return body.params.name;
        }
    }
    catch { }
    return null;
}
// POST /mcp
app.post("/mcp", optionalAuthMiddleware, async (req, res) => {
    const authContext = req.auth?.agent
        ? { agentId: req.auth.agent.agentId, role: req.auth.agent.role }
        : undefined;
    if (authContext) {
        if (!rateLimiter(authContext.agentId)) {
            res.status(429).json({
                jsonrpc: "2.0",
                error: { code: -32001, message: "Rate limit exceeded (10 req/s)" },
                id: null,
            });
            return;
        }
    }
    const server = createMcpServer(authContext);
    const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
    });
    try {
        await server.connect(transport);
        await transport.handleRequest(req, res, req.body);
        res.on("close", () => {
            transport.close();
            server.close();
        });
    }
    catch (error) {
        logError("[MCP] handleRequest error", error, { module: "mcp", traceId: req.traceId });
        if (!res.headersSent) {
            res.status(500).json({
                jsonrpc: "2.0",
                error: { code: -32603, message: "Internal server error" },
                id: null,
            });
        }
    }
});
// GET /mcp
app.get("/mcp", optionalAuthMiddleware, async (req, res) => {
    const authContext = req.auth?.agent
        ? { agentId: req.auth.agent.agentId, role: req.auth.agent.role }
        : undefined;
    const server = createMcpServer(authContext);
    const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
    });
    try {
        await server.connect(transport);
        await transport.handleRequest(req, res, undefined);
        res.on("close", () => {
            transport.close();
            server.close();
        });
    }
    catch (error) {
        logError("[MCP] GET /mcp error", error, { module: "mcp", traceId: req.traceId });
        if (!res.headersSent) {
            res.status(500).end();
        }
    }
});
// DELETE /mcp
app.delete("/mcp", optionalAuthMiddleware, async (req, res) => {
    const authContext = req.auth?.agent
        ? { agentId: req.auth.agent.agentId, role: req.auth.agent.role }
        : undefined;
    const server = createMcpServer(authContext);
    const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
    });
    try {
        await server.connect(transport);
        await transport.handleRequest(req, res, req.body);
        res.on("close", () => {
            transport.close();
            server.close();
        });
    }
    catch (error) {
        logError("[MCP] DELETE /mcp error", error, { module: "mcp", traceId: req.traceId });
        if (!res.headersSent) {
            res.status(500).end();
        }
    }
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 404 处理（在 error handler 之前）
// ═══════════════════════════════════════════════════════════════
app.use((req, res) => {
    const traceId = req.traceId;
    res.status(404).json({
        error: true,
        message: "Not Found",
        traceId,
    });
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 全局错误处理中间件（放在所有路由之后）
// ═══════════════════════════════════════════════════════════════
app.use((err, req, res, _next) => {
    const traceId = req.traceId;
    logError("unhandled_error", err, { traceId, path: req.path, method: req.method });
    if (res.headersSent)
        return;
    res.status(err.status || 500).json({
        error: true,
        message: process.env.NODE_ENV === "development" ? err.message : "Internal Server Error",
        traceId,
    });
});
// ═══════════════════════════════════════════════════════════════
// Phase 5b: 优雅关闭
// ═══════════════════════════════════════════════════════════════
let httpServer = null;
async function gracefulShutdown(signal) {
    logger.info("shutdown_initiated", { signal, module: "server" });
    // 1. 停止接受新连接
    if (httpServer) {
        httpServer.close(() => {
            logger.info("http_server_closed", { module: "server" });
        });
    }
    // 2. drain SSE 连接
    drainAllClients();
    logger.info("sse_drained", { module: "server" });
    // 3. 停止定时器
    stopHeartbeatMonitor();
    stopDedupCleanup();
    stopCleanup();
    // 4. 关闭数据库
    try {
        db.close();
        logger.info("database_closed", { module: "server" });
    }
    catch (err) {
        logError("database_close_error", err, { module: "server" });
    }
    logger.info("shutdown_complete", { module: "server" });
    process.exit(0);
}
// ═══════════════════════════════════════════════════════════════
// 未捕获异常兜底
// ═══════════════════════════════════════════════════════════════
process.on("uncaughtException", (err) => {
    logError("uncaught_exception", err, { module: "process" });
    process.exit(1);
});
process.on("unhandledRejection", (reason) => {
    logError("unhandled_rejection", reason, { module: "process" });
});
// ═══════════════════════════════════════════════════════════════
// 启动
// ═══════════════════════════════════════════════════════════════
httpServer = app.listen(config.port, () => {
    logger.info("server_started", {
        module: "server",
        version: "2.3.1",
        port: config.port,
        phase: "5b",
    });
    // 启动心跳超时监控
    startHeartbeatMonitor((agentId) => {
        logger.info("agent_offline_timeout", { module: "monitor", agent_id: agentId });
    });
    // 启动去重缓存 TTL 清理（15min）
    startDedupCleanup();
    // Phase 6: 启动定时清理（过期 Token / Dedup / Consumed）
    scheduleCleanup(config.dedupTTL);
    // 重建 FTS 索引
    rebuildFtsIndex();
});
// 优雅关闭信号监听
process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));
//# sourceMappingURL=server.js.map