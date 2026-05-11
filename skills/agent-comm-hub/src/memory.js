/**
 * memory.ts — Memory Service (Phase 1 Week 2)
 *
 * 功能：
 *   - storeMemory: 存储记忆（private/group/collective 三种 scope）
 *   - recallMemory: 通过 FTS5 全文搜索召回记忆
 *   - listMemories: 列出 Agent 的记忆（支持 scope 筛选）
 *   - deleteMemory: 删除记忆
 *   - getMemoryStats: 获取记忆统计
 *
 * 设计要点：
 *   - FTS5 全文索引自动同步（通过 triggers）
 *   - scope 控制：private 仅本人可见，group 组内可见，collective 全局可见
 *   - 内容长度限制 10KB
 *   - 标签支持：JSON array 字符串存储
 */
import { randomUUID } from "crypto";
import { db } from "./db.js";
import { buildFtsTokens, buildSearchQuery } from "./tokenizer.js";
import { auditLog } from "./security.js";
import { logError, logger } from "./logger.js";
// ─── 常量 ────────────────────────────────────────────────
const MAX_CONTENT_LENGTH = 10000;
const MAX_TITLE_LENGTH = 500;
const MAX_RECALL_RESULTS = 20;
const MAX_LIST_RESULTS = 50;
// ─── 存储记忆 ────────────────────────────────────────────
/**
 * 存储新记忆
 *
 * @returns
 *   - { ok: true, memory } — 成功
 *   - { ok: false, error } — 失败
 */
export function storeMemory(agentId, content, options) {
    // 参数校验
    if (!content || content.trim().length === 0) {
        return { ok: false, error: "Memory content cannot be empty" };
    }
    if (content.length > MAX_CONTENT_LENGTH) {
        return {
            ok: false,
            error: `Memory content too long (${content.length} > ${MAX_CONTENT_LENGTH} chars)`,
        };
    }
    const title = options?.title?.trim() ?? null;
    if (title && title.length > MAX_TITLE_LENGTH) {
        return {
            ok: false,
            error: `Memory title too long (${title.length} > ${MAX_TITLE_LENGTH} chars)`,
        };
    }
    const scope = options?.scope ?? "private";
    if (!["private", "group", "collective"].includes(scope)) {
        return { ok: false, error: `Invalid scope: ${scope}` };
    }
    const tags = options?.tags ?? null;
    const tagsJson = tags ? JSON.stringify(tags) : null;
    const sourceAgentId = options?.source_agent_id ?? null;
    const sourceTaskId = options?.source_task_id ?? null;
    const now = Date.now();
    const id = randomUUID();
    try {
        const ftsTokens = buildFtsTokens(title, content);
        db.prepare(`INSERT INTO memories (id, agent_id, title, content, fts_tokens, scope, tags, source_agent_id, source_task_id, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(id, agentId, title, content, ftsTokens, scope, tagsJson, sourceAgentId, sourceTaskId, now, now);
        // 同步写入 FTS5 索引
        db.prepare(`INSERT INTO memories_fts (title, content, tags, fts_tokens) VALUES (?, ?, ?, ?)`).run(title, content, tagsJson, ftsTokens);
        const memory = {
            id,
            agent_id: agentId,
            title,
            content,
            scope,
            tags: tagsJson,
            source_agent_id: sourceAgentId,
            source_task_id: sourceTaskId,
            created_at: now,
            updated_at: now,
        };
        return { ok: true, memory };
    }
    catch (err) {
        return { ok: false, error: `Failed to store memory: ${err.message}` };
    }
}
// ─── 召回记忆（FTS5 全文搜索） ──────────────────────────
/**
 * 通过全文搜索召回记忆
 *
 * 搜索范围：
 *   - private: 仅本人的记忆
 *   - group: scope=group 或 scope=collective 的记忆
 *   - collective: scope=collective 的记忆
 *
 * @param query 搜索关键词（FTS5 query syntax）
 * @param agentId 查询者 ID（用于 scope 过滤）
 * @param options 可选参数
 * @returns 匹配的记忆列表
 */
export function recallMemory(query, agentId, options) {
    if (!query || query.trim().length === 0) {
        return [];
    }
    const limit = Math.min(options?.limit ?? MAX_RECALL_RESULTS, MAX_RECALL_RESULTS);
    const scope = options?.scope ?? "all";
    // 构建 FTS5 查询（N-gram 中文分词）
    const safeQuery = buildSearchQuery(query);
    if (!safeQuery) {
        return [];
    }
    try {
        let sql;
        let params;
        if (scope === "all") {
            // 搜索所有可见的记忆（private 仅限本人 + group + collective）
            // Phase 2 Day 4: 按 agent trust_score 加权排序（高信任排名靠前）
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        JOIN memories_fts fts ON m.title = fts.title AND m.content = fts.content
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE memories_fts MATCH ?
        AND (m.agent_id = ? OR m.scope IN ('group', 'collective'))
        ORDER BY source_trust_score DESC, rank
        LIMIT ?
      `;
            params = [safeQuery, agentId, limit];
        }
        else if (scope === "private") {
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        JOIN memories_fts fts ON m.title = fts.title AND m.content = fts.content
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE memories_fts MATCH ?
        AND m.agent_id = ? AND m.scope = 'private'
        ORDER BY source_trust_score DESC, rank
        LIMIT ?
      `;
            params = [safeQuery, agentId, limit];
        }
        else if (scope === "group") {
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        JOIN memories_fts fts ON m.title = fts.title AND m.content = fts.content
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE memories_fts MATCH ?
        AND (m.agent_id = ? OR m.scope IN ('group', 'collective'))
        AND m.scope != 'private'
        ORDER BY source_trust_score DESC, rank
        LIMIT ?
      `;
            params = [safeQuery, agentId, limit];
        }
        else {
            // collective
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        JOIN memories_fts fts ON m.title = fts.title AND m.content = fts.content
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE memories_fts MATCH ?
        AND m.scope = 'collective'
        ORDER BY source_trust_score DESC, rank
        LIMIT ?
      `;
            params = [safeQuery, limit];
        }
        return db.prepare(sql).all(...params);
    }
    catch (err) {
        logError("memory_recallMemory_error", err);
        return [];
    }
}
// ─── 列出记忆 ────────────────────────────────────────────
/**
 * 列出 Agent 的记忆
 */
export function listMemories(agentId, options) {
    const limit = Math.min(options?.limit ?? MAX_LIST_RESULTS, MAX_LIST_RESULTS);
    const offset = options?.offset ?? 0;
    const scope = options?.scope ?? "all";
    try {
        let sql;
        let params;
        if (scope === "all") {
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE m.agent_id = ? OR m.scope IN ('group', 'collective')
        ORDER BY source_trust_score DESC, m.created_at DESC
        LIMIT ? OFFSET ?
      `;
            params = [agentId, limit, offset];
        }
        else if (scope === "private") {
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE m.agent_id = ? AND m.scope = 'private'
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
      `;
            params = [agentId, limit, offset];
        }
        else {
            sql = `
        SELECT m.*, COALESCE(a.trust_score, 50) AS source_trust_score
        FROM memories m
        LEFT JOIN agents a ON m.agent_id = a.agent_id
        WHERE (m.agent_id = ? OR m.scope IN ('group', 'collective'))
        AND m.scope = ?
        ORDER BY source_trust_score DESC, m.created_at DESC
        LIMIT ? OFFSET ?
      `;
            params = [agentId, scope, limit, offset];
        }
        return db.prepare(sql).all(...params);
    }
    catch (err) {
        logError("memory_listMemories_error", err);
        return [];
    }
}
// ─── 删除记忆 ────────────────────────────────────────────
/**
 * 删除记忆
 * 仅允许删除自己的记忆，或 admin 删除任何记忆
 */
export function deleteMemory(memoryId, agentId, role) {
    try {
        // 查找记忆
        const memory = db.prepare(`SELECT * FROM memories WHERE id = ?`).get(memoryId);
        if (!memory) {
            return { ok: false, error: `Memory ${memoryId} not found` };
        }
        // 权限检查：只能删除自己的记忆（admin 可以删除任何）
        if (memory.agent_id !== agentId && role !== "admin") {
            return { ok: false, error: "Permission denied: can only delete own memories" };
        }
        // 删除 FTS 索引（通过 title + content 匹配）
        try {
            db.prepare(`DELETE FROM memories_fts WHERE title = ? AND content = ?`).run(memory.title, memory.content);
            // Phase 5a Day 2: 审计 FTS 索引删除
            auditLog("delete_memory_fts", agentId, memoryId, `title=${memory.title?.slice(0, 50) ?? "null"}`);
        }
        catch {
            // FTS 删除失败不影响主表删除
        }
        db.prepare(`DELETE FROM memories WHERE id = ?`).run(memoryId);
        // Phase 5a Day 2: 审计记忆主表删除
        auditLog("delete_memory_db", agentId, memoryId, `scope=${memory.scope}, agent=${memory.agent_id}`);
        return { ok: true, deleted: true };
    }
    catch (err) {
        return { ok: false, error: `Failed to delete memory: ${err.message}` };
    }
}
// ─── 记忆统计 ────────────────────────────────────────────
/**
 * 获取记忆统计信息
 */
export function getMemoryStats() {
    try {
        const totalRow = db.prepare(`SELECT COUNT(*) as cnt FROM memories`).get();
        let ftsEntries = 0;
        try {
            const ftsRow = db.prepare(`SELECT COUNT(*) as cnt FROM memories_fts`).get();
            ftsEntries = ftsRow?.cnt ?? 0;
        }
        catch {
            // FTS 表可能不存在
        }
        const byAgentRows = db.prepare(`SELECT agent_id, COUNT(*) as cnt FROM memories GROUP BY agent_id`).all();
        const byScopeRows = db.prepare(`SELECT scope, COUNT(*) as cnt FROM memories GROUP BY scope`).all();
        const byAgent = {};
        for (const row of byAgentRows) {
            byAgent[row.agent_id] = row.cnt;
        }
        const byScope = {};
        for (const row of byScopeRows) {
            byScope[row.scope] = row.cnt;
        }
        return {
            total: totalRow?.cnt ?? 0,
            by_agent: byAgent,
            by_scope: byScope,
            fts_entries: ftsEntries,
        };
    }
    catch (err) {
        logError("memory_getMemoryStats_error", err);
        return { total: 0, by_agent: {}, by_scope: {}, fts_entries: 0 };
    }
}
// ─── FTS 索引重建 ────────────────────────────────────────
/**
 * 为所有已有 memories 重建 FTS 索引（Phase 2 Migration）
 * 在 server.ts 启动时调用一次
 */
export function rebuildFtsIndex() {
    try {
        const memCount = db.prepare(`SELECT COUNT(*) as cnt FROM memories`).get()?.cnt ?? 0;
        let ftsCount = 0;
        try {
            ftsCount = db.prepare(`SELECT COUNT(*) as cnt FROM memories_fts`).get()?.cnt ?? 0;
        }
        catch {
            // FTS 表不存在，跳过
            return;
        }
        if (memCount === 0 || ftsCount >= memCount) {
            return; // 不需要重建
        }
        logger.info("memory_fts_rebuild_start", { module: "memory", mem_count: memCount, fts_count: ftsCount });
        const memories = db.prepare(`SELECT id, title, content, tags, source_agent_id, source_task_id FROM memories`).all();
        const insertFts = db.prepare(`INSERT INTO memories_fts (title, content, tags, fts_tokens) VALUES (?, ?, ?, ?)`);
        const rebuildBatch = db.transaction((mems) => {
            for (const m of mems) {
                const tokens = buildFtsTokens(m.title, m.content);
                insertFts.run(m.title, m.content, m.tags, tokens);
            }
        });
        rebuildBatch(memories);
        logger.info("memory_fts_rebuild_done", { module: "memory", entries: memories.length });
    }
    catch (err) {
        logError("memory_rebuildFtsIndex_error", err);
    }
}
//# sourceMappingURL=memory.js.map