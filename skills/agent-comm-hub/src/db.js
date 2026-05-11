/**
 * db.ts — SQLite 持久化层
 * 消息 + 任务 两张表，进程重启数据不丢失
 */
import Database from "better-sqlite3";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { logger, logError } from "./logger.js";
const __dir = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(__dir, "../comm_hub.db");
export const db = new Database(DB_PATH);
// 开启 WAL 模式，提升并发读写性能
db.pragma("journal_mode = WAL");
db.pragma("synchronous = NORMAL");
// ─── 建表 ──────────────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    from_agent  TEXT NOT NULL,
    to_agent    TEXT NOT NULL,
    content     TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'message',
    metadata    TEXT,
    status      TEXT NOT NULL DEFAULT 'unread',
    created_at  INTEGER NOT NULL
  );

  CREATE TABLE IF NOT EXISTS tasks (
    id           TEXT PRIMARY KEY,
    assigned_by  TEXT NOT NULL,
    assigned_to  TEXT NOT NULL DEFAULT '',
    description  TEXT NOT NULL,
    context      TEXT,
    priority     TEXT NOT NULL DEFAULT 'normal',
    status       TEXT NOT NULL DEFAULT 'inbox',
    result       TEXT,
    progress     INTEGER DEFAULT 0,
    pipeline_id  TEXT,
    order_index  INTEGER DEFAULT 0,
    required_capability TEXT,
    due_at       INTEGER,
    assigned_at  INTEGER,
    completed_at INTEGER,
    tags         TEXT DEFAULT '[]',
    created_at   INTEGER NOT NULL,
    updated_at   INTEGER NOT NULL
  );

  -- 消费水位线表：记录 Agent 已处理过的文件路径，防止重复消费
  CREATE TABLE IF NOT EXISTS consumed_log (
    id           TEXT PRIMARY KEY,
    agent_id     TEXT NOT NULL,
    resource     TEXT NOT NULL,
    resource_type TEXT NOT NULL DEFAULT 'file',  -- 'file' | 'signal' | 'message'
    action       TEXT NOT NULL,
    notes        TEXT,
    consumed_at  INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_messages_to_agent  ON messages(to_agent, status);
  CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to  ON tasks(assigned_to, status);
  CREATE INDEX IF NOT EXISTS idx_consumed_log       ON consumed_log(agent_id, resource);
`);
// ─── Phase 4a Migration: tasks 表新增字段 ──────────────
// 必须在 taskStmt.insert 之前执行
try {
    const taskCols = db.pragma("table_info(tasks)");
    if (taskCols.length > 0) {
        const colNames = taskCols.map((c) => c.name);
        const migrations = [
            ["pipeline_id", "ALTER TABLE tasks ADD COLUMN pipeline_id TEXT"],
            ["order_index", "ALTER TABLE tasks ADD COLUMN order_index INTEGER DEFAULT 0"],
            ["required_capability", "ALTER TABLE tasks ADD COLUMN required_capability TEXT"],
            ["due_at", "ALTER TABLE tasks ADD COLUMN due_at INTEGER"],
            ["assigned_at", "ALTER TABLE tasks ADD COLUMN assigned_at INTEGER"],
            ["completed_at", "ALTER TABLE tasks ADD COLUMN completed_at INTEGER"],
            ["tags", "ALTER TABLE tasks ADD COLUMN tags TEXT DEFAULT '[]'"],
        ];
        for (const [col, sql] of migrations) {
            if (!colNames.includes(col)) {
                db.exec(sql);
                logger.info("db_migration", { module: "db", column: col, table: "tasks" });
            }
        }
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "tasks", phase: "4a", error: e.message });
}
// ─── Phase 4a 新表：pipelines + pipeline_tasks ──────────
// 必须在 pipelineStmt 和 taskStmt.listByPipeline 之前创建
db.exec(`
  CREATE TABLE IF NOT EXISTS pipelines (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    description   TEXT,
    status        TEXT NOT NULL DEFAULT 'draft',
    creator       TEXT NOT NULL,
    config        TEXT,
    created_at    INTEGER NOT NULL,
    updated_at    INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_pipelines_creator ON pipelines(creator);
  CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);
`);
db.exec(`
  CREATE TABLE IF NOT EXISTS pipeline_tasks (
    id            TEXT PRIMARY KEY,
    pipeline_id   TEXT NOT NULL REFERENCES pipelines(id),
    task_id       TEXT NOT NULL REFERENCES tasks(id),
    order_index   INTEGER NOT NULL DEFAULT 0,
    created_at    INTEGER NOT NULL,
    UNIQUE(pipeline_id, task_id)
  );

  CREATE INDEX IF NOT EXISTS idx_pipeline_tasks_pipe ON pipeline_tasks(pipeline_id);
  CREATE INDEX IF NOT EXISTS idx_pipeline_tasks_order ON pipeline_tasks(pipeline_id, order_index);
`);
export const msgStmt = {
    insert: db.prepare(`INSERT INTO messages VALUES (@id,@from_agent,@to_agent,@content,@type,@metadata,@status,@created_at)`),
    markDelivered: db.prepare(`UPDATE messages SET status='delivered' WHERE id=?`),
    markRead: db.prepare(`UPDATE messages SET status='read' WHERE id=?`),
    markAcknowledged: db.prepare(`UPDATE messages SET status='acknowledged' WHERE id=?`),
    pendingFor: db.prepare(`SELECT * FROM messages WHERE to_agent=? AND status='unread' ORDER BY created_at ASC`),
    markAllDelivered: db.prepare(`UPDATE messages SET status='delivered' WHERE to_agent=? AND status='unread'`),
    getById: db.prepare(`SELECT * FROM messages WHERE id=?`),
};
export const consumedStmt = {
    insert: db.prepare(`INSERT OR REPLACE INTO consumed_log VALUES (@id,@agent_id,@resource,@resource_type,@action,@notes,@consumed_at)`),
    check: db.prepare(`SELECT * FROM consumed_log WHERE agent_id=? AND resource=?`),
    listByAgent: db.prepare(`SELECT * FROM consumed_log WHERE agent_id=? ORDER BY consumed_at DESC LIMIT ?`),
};
export const taskStmt = {
    insert: db.prepare(`INSERT INTO tasks (id, assigned_by, assigned_to, description, context, priority, status, result, progress, pipeline_id, order_index, required_capability, due_at, assigned_at, completed_at, tags, created_at, updated_at)
     VALUES (@id, @assigned_by, @assigned_to, @description, @context, @priority, @status, @result, @progress, @pipeline_id, @order_index, @required_capability, @due_at, @assigned_at, @completed_at, @tags, @created_at, @updated_at)`),
    getById: db.prepare(`SELECT * FROM tasks WHERE id=?`),
    update: db.prepare(`UPDATE tasks SET status=?,result=?,progress=?,updated_at=? WHERE id=?`),
    updateAssignee: db.prepare(`UPDATE tasks SET assigned_to=?,assigned_at=?,status='assigned',updated_at=? WHERE id=?`),
    listFor: db.prepare(`SELECT * FROM tasks WHERE assigned_to=? AND status=? ORDER BY created_at DESC`),
    listByPipeline: db.prepare(`SELECT t.* FROM tasks t JOIN pipeline_tasks pt ON t.id=pt.task_id WHERE pt.pipeline_id=? ORDER BY pt.order_index ASC`),
};
export const pipelineStmt = {
    insert: db.prepare(`INSERT INTO pipelines VALUES (@id,@name,@description,@status,@creator,@config,@created_at,@updated_at)`),
    getById: db.prepare(`SELECT * FROM pipelines WHERE id=?`),
    updateStatus: db.prepare(`UPDATE pipelines SET status=?,updated_at=? WHERE id=?`),
    listByCreator: db.prepare(`SELECT * FROM pipelines WHERE creator=? ORDER BY created_at DESC`),
};
export const pipelineTaskStmt = {
    insert: db.prepare(`INSERT OR REPLACE INTO pipeline_tasks VALUES (@id,@pipeline_id,@task_id,@order_index,@created_at)`),
    listByPipeline: db.prepare(`SELECT * FROM pipeline_tasks WHERE pipeline_id=? ORDER BY order_index ASC`),
    deleteByTask: db.prepare(`DELETE FROM pipeline_tasks WHERE task_id=?`),
};
// ═══════════════════════════════════════════════════════════════
// Phase 1 — Security + Identity + Dedup + Memory 表
// ═══════════════════════════════════════════════════════════════
// --- agents 表：Agent 注册与在线状态 ---
// Phase 2 Day 4 Migration: 先添加 trust_score 列（必须在建索引前）
try {
    const agentCols = db.pragma("table_info(agents)");
    if (agentCols.length > 0 && !agentCols.some((c) => c.name === "trust_score")) {
        db.exec(`ALTER TABLE agents ADD COLUMN trust_score INTEGER NOT NULL DEFAULT 50`);
        logger.info("db_migration", { module: "db", column: "trust_score", table: "agents" });
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", column: "trust_score", table: "agents", error: e.message });
}
db.exec(`
  CREATE TABLE IF NOT EXISTS agents (
    agent_id      TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'member',   -- 'admin' | 'member'
    api_token     TEXT,                              -- SHA-256 hash
    status        TEXT NOT NULL DEFAULT 'offline',  -- 'online' | 'offline'
    trust_score   INTEGER NOT NULL DEFAULT 50,      -- Phase 2 Day 4: 信任分 0-100
    last_heartbeat INTEGER,
    created_at    INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
  CREATE INDEX IF NOT EXISTS idx_agents_heartbeat ON agents(last_heartbeat);
  CREATE INDEX IF NOT EXISTS idx_agents_trust ON agents(trust_score);
`);
// Phase 2 Day 4 Migration: 为已有 agents 表添加 trust_score 字段
try {
    const agentCols = db.pragma("table_info(agents)");
    if (!agentCols.some((c) => c.name === "trust_score")) {
        db.exec(`ALTER TABLE agents ADD COLUMN trust_score INTEGER NOT NULL DEFAULT 50`);
        logger.info("db_migration", { module: "db", column: "trust_score", table: "agents", fallback: true });
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", column: "trust_score", table: "agents", error: e.message });
}
// --- auth_tokens 表：邀请码 + API Token 管理 ---
db.exec(`
  CREATE TABLE IF NOT EXISTS auth_tokens (
    token_id      TEXT PRIMARY KEY,
    token_type    TEXT NOT NULL,            -- 'invite_code' | 'api_token'
    token_value   TEXT NOT NULL,            -- SHA-256 hash
    agent_id      TEXT,                      -- api_token 关联的 agent
    role          TEXT,                      -- api_token 关联的角色
    used          INTEGER DEFAULT 0,        -- 1 = 已使用
    created_at    INTEGER NOT NULL,
    expires_at    INTEGER,
    revoked_at    INTEGER,
    UNIQUE(token_type, token_value)
  );

  CREATE INDEX IF NOT EXISTS idx_auth_tokens_type ON auth_tokens(token_type, used);
  CREATE INDEX IF NOT EXISTS idx_auth_tokens_agent ON auth_tokens(agent_id);
`);
// --- dedup_cache 表：消息去重缓存 ---
db.exec(`
  CREATE TABLE IF NOT EXISTS dedup_cache (
    msg_hash   TEXT PRIMARY KEY,
    sender_id  TEXT NOT NULL,
    nonce      INTEGER NOT NULL,
    created_at INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_dedup_sender_nonce ON dedup_cache(sender_id, nonce);
`);
// --- memories 表 + FTS5 全文索引（N-gram 中文分词） ---
// Phase 2 Day 4 Migration: 先添加溯源列（必须在建索引前）
try {
    const memCols = db.pragma("table_info(memories)");
    if (memCols.length > 0) {
        if (!memCols.some((c) => c.name === "source_agent_id")) {
            db.exec(`ALTER TABLE memories ADD COLUMN source_agent_id TEXT`);
            logger.info("db_migration", { module: "db", column: "source_agent_id", table: "memories" });
        }
        if (!memCols.some((c) => c.name === "source_task_id")) {
            db.exec(`ALTER TABLE memories ADD COLUMN source_task_id TEXT`);
            logger.info("db_migration", { module: "db", column: "source_task_id", table: "memories" });
        }
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "memories", error: e.message });
}
db.exec(`
  CREATE TABLE IF NOT EXISTS memories (
    id               TEXT PRIMARY KEY,
    agent_id         TEXT NOT NULL,
    title            TEXT,
    content          TEXT NOT NULL,
    fts_tokens       TEXT NOT NULL DEFAULT '',     -- Phase 2: N-gram 预分词 tokens
    scope            TEXT NOT NULL DEFAULT 'private',  -- 'private' | 'group' | 'collective'
    tags             TEXT,                               -- JSON array
    source_agent_id  TEXT,                               -- Phase 2 Day 4: 溯源 — 实际写入者
    source_task_id   TEXT,                               -- Phase 2 Day 4: 溯源 — 关联任务
    created_at       INTEGER NOT NULL,
    updated_at       INTEGER
  );

  CREATE INDEX IF NOT EXISTS idx_memories_agent      ON memories(agent_id);
  CREATE INDEX IF NOT EXISTS idx_memories_scope      ON memories(scope);
  CREATE INDEX IF NOT EXISTS idx_memories_source     ON memories(source_agent_id);
`);
// Phase 2 Migration: 为已有 memories 表添加 fts_tokens 列
try {
    const colInfo = db.pragma("table_info(memories)");
    const hasFtsTokens = colInfo.some((c) => c.name === "fts_tokens");
    if (!hasFtsTokens) {
        db.exec(`ALTER TABLE memories ADD COLUMN fts_tokens TEXT NOT NULL DEFAULT ''`);
        logger.info("db_migration", { module: "db", column: "fts_tokens", table: "memories" });
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", column: "fts_tokens", table: "memories", error: e.message });
}
// FTS5 虚拟表（独立存储模式 + fts_tokens 列）
try {
    // Phase 2: 旧版 FTS5 可能已存在（external content 模式），需要重建
    // 先尝试删除旧表（ignore error 如果不存在）
    try {
        db.exec(`DROP TRIGGER IF EXISTS memories_ai`);
        db.exec(`DROP TRIGGER IF EXISTS memories_ad`);
        db.exec(`DROP TRIGGER IF EXISTS memories_au`);
        db.exec(`DROP TABLE IF EXISTS memories_fts`);
    }
    catch {
        // ignore
    }
    // 新版 FTS5：独立存储 fts_tokens 列
    db.exec(`
    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
      title,
      content,
      tags,
      fts_tokens
    );
  `);
}
catch (e) {
    if (!e.message.includes("already exists")) {
        logger.warn("db_fts5_init_warning", { module: "db", error: e.message });
    }
}
// --- agents_capabilities 表 ---
db.exec(`
  CREATE TABLE IF NOT EXISTS agent_capabilities (
    id            TEXT PRIMARY KEY,
    agent_id      TEXT NOT NULL,
    capability    TEXT NOT NULL,
    params        TEXT,            -- JSON
    verified      INTEGER DEFAULT 0,
    verified_at   INTEGER,
    created_at    INTEGER NOT NULL,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
  );

  CREATE INDEX IF NOT EXISTS idx_capabilities_agent ON agent_capabilities(agent_id);
`);
// --- audit_log 表 ---
db.exec(`
  CREATE TABLE IF NOT EXISTS audit_log (
    id          TEXT PRIMARY KEY,
    action      TEXT NOT NULL,
    agent_id    TEXT,
    target      TEXT,
    details     TEXT,
    ip_address  TEXT,
    created_at  INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_audit_log_time ON audit_log(created_at);
`);
// ═══════════════════════════════════════════════════════════════
// Phase 3 — Evolution Engine 表
// ═══════════════════════════════════════════════════════════════
// strategies 表
db.exec(`
  CREATE TABLE IF NOT EXISTS strategies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT 'workflow',
    sensitivity     TEXT NOT NULL DEFAULT 'normal',
    proposer_id     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    approve_reason  TEXT,
    approved_by     TEXT,
    approved_at     INTEGER,
    proposed_at     INTEGER NOT NULL,
    task_id         TEXT,
    source_trust    INTEGER NOT NULL DEFAULT 50,
    apply_count     INTEGER NOT NULL DEFAULT 0,
    feedback_count  INTEGER NOT NULL DEFAULT 0,
    positive_count  INTEGER NOT NULL DEFAULT 0,
    UNIQUE(title, proposer_id, proposed_at)
  );

  CREATE INDEX IF NOT EXISTS idx_strategies_status    ON strategies(status);
  CREATE INDEX IF NOT EXISTS idx_strategies_proposer  ON strategies(proposer_id);
  CREATE INDEX IF NOT EXISTS idx_strategies_category  ON strategies(category);
`);
// strategy_feedback 表（UNIQUE 防刷）
db.exec(`
  CREATE TABLE IF NOT EXISTS strategy_feedback (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id  INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    agent_id     TEXT NOT NULL,
    feedback     TEXT NOT NULL,
    comment      TEXT,
    applied      INTEGER NOT NULL DEFAULT 0,
    created_at   INTEGER NOT NULL,
    UNIQUE(strategy_id, agent_id)
  );

  CREATE INDEX IF NOT EXISTS idx_feedback_strategy ON strategy_feedback(strategy_id);
  CREATE INDEX IF NOT EXISTS idx_feedback_agent    ON strategy_feedback(agent_id);
`);
// strategy_applications 表（采纳记录）
db.exec(`
  CREATE TABLE IF NOT EXISTS strategy_applications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id  INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    agent_id     TEXT NOT NULL,
    context      TEXT,
    result       TEXT,
    created_at   INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_applications_strategy ON strategy_applications(strategy_id);
  CREATE INDEX IF NOT EXISTS idx_applications_agent    ON strategy_applications(agent_id);
`);
// FTS5 全文索引（N-gram 中文分词，与 memories 一致）
try {
    try {
        db.exec(`DROP TRIGGER IF EXISTS strategies_ai`);
        db.exec(`DROP TRIGGER IF EXISTS strategies_ad`);
        db.exec(`DROP TRIGGER IF EXISTS strategies_au`);
        db.exec(`DROP TABLE IF EXISTS strategies_fts`);
    }
    catch {
        // ignore
    }
    db.exec(`
    CREATE VIRTUAL TABLE IF NOT EXISTS strategies_fts USING fts5(
      title, content, category
    );
  `);
}
catch (e) {
    if (!e.message.includes("already exists")) {
        logger.warn("db_strategies_fts5_init_warning", { module: "db", error: e.message });
    }
}
// ═══════════════════════════════════════════════════════════════
// Phase 4b — Task Orchestrator 进阶（依赖链 + 质量门 + 交接 + 分级审批）
// ═══════════════════════════════════════════════════════════════
// --- Phase 4b: tasks 表扩展列 ---
try {
    const taskCols = db.pragma("table_info(tasks)");
    if (taskCols.length > 0) {
        const colNames = taskCols.map((c) => c.name);
        const colMigrations = [
            ["parallel_group", "ALTER TABLE tasks ADD COLUMN parallel_group TEXT DEFAULT NULL"],
            ["handoff_status", "ALTER TABLE tasks ADD COLUMN handoff_status TEXT DEFAULT 'none'"],
            // Phase 4b Day 3: 交接协议目标 Agent
            ["handoff_to", "ALTER TABLE tasks ADD COLUMN handoff_to TEXT DEFAULT NULL"],
        ];
        for (const [col, sql] of colMigrations) {
            if (!colNames.includes(col)) {
                db.exec(sql);
                logger.info("db_migration", { module: "db", column: col, table: "tasks", phase: "4b" });
            }
        }
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "tasks", phase: "4b", error: e.message });
}
// --- Phase 4b: strategies 表扩展列 ---
try {
    const stratCols = db.pragma("table_info(strategies)");
    if (stratCols.length > 0) {
        const colNames = stratCols.map((c) => c.name);
        const colMigrations = [
            ["approval_tier", "ALTER TABLE strategies ADD COLUMN approval_tier TEXT DEFAULT 'admin'"],
            ["observation_start", "ALTER TABLE strategies ADD COLUMN observation_start INTEGER"],
            ["veto_deadline", "ALTER TABLE strategies ADD COLUMN veto_deadline INTEGER"],
        ];
        for (const [col, sql] of colMigrations) {
            if (!colNames.includes(col)) {
                db.exec(sql);
                logger.info("db_migration", { module: "db", column: col, table: "strategies", phase: "4b" });
            }
        }
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "strategies", phase: "4b", error: e.message });
}
// --- Phase 4b: task_dependencies 表（依赖链） ---
db.exec(`
  CREATE TABLE IF NOT EXISTS task_dependencies (
    id              TEXT PRIMARY KEY,
    upstream_id     TEXT NOT NULL,
    downstream_id   TEXT NOT NULL,
    dep_type        TEXT NOT NULL DEFAULT 'finish_to_start',
    status          TEXT NOT NULL DEFAULT 'pending',
    created_at      INTEGER NOT NULL,
    UNIQUE(upstream_id, downstream_id)
  );

  CREATE INDEX IF NOT EXISTS idx_deps_downstream ON task_dependencies(downstream_id, status);
  CREATE INDEX IF NOT EXISTS idx_deps_upstream   ON task_dependencies(upstream_id, status);
`);
// --- Phase 4b: quality_gates 表（质量门） ---
db.exec(`
  CREATE TABLE IF NOT EXISTS quality_gates (
    id              TEXT PRIMARY KEY,
    pipeline_id     TEXT NOT NULL,
    gate_name       TEXT NOT NULL,
    criteria        TEXT NOT NULL,
    after_order     INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'pending',
    evaluator_id    TEXT,
    result          TEXT,
    evaluated_at    INTEGER,
    created_at      INTEGER NOT NULL,
    UNIQUE(pipeline_id, gate_name)
  );

  CREATE INDEX IF NOT EXISTS idx_qg_pipeline ON quality_gates(pipeline_id, status);
  CREATE INDEX IF NOT EXISTS idx_qg_after_order ON quality_gates(pipeline_id, after_order);
`);
// ═══════════════════════════════════════════════════════════════
// Phase 5a — Security 增强（RBAC 细化 + Audit 防篡改）
// ═══════════════════════════════════════════════════════════════
// --- Phase 5a: agents 表扩展列（group_admin 支持） ---
try {
    const agentCols = db.pragma("table_info(agents)");
    if (agentCols.length > 0) {
        const colNames = agentCols.map((c) => c.name);
        const colMigrations = [
            ["managed_group_id", "ALTER TABLE agents ADD COLUMN managed_group_id TEXT"],
        ];
        for (const [col, sql] of colMigrations) {
            if (!colNames.includes(col)) {
                db.exec(sql);
                logger.info("db_migration", { module: "db", column: col, table: "agents", phase: "5a" });
            }
        }
    }
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "agents", phase: "5a", error: e.message });
}
// --- Phase 5a: audit_log 哈希链列 + 写保护触发器 ---
try {
    const auditCols = db.pragma("table_info(audit_log)");
    if (auditCols.length > 0) {
        const colNames = auditCols.map((c) => c.name);
        const colMigrations = [
            ["prev_hash", "ALTER TABLE audit_log ADD COLUMN prev_hash TEXT"],
            ["record_hash", "ALTER TABLE audit_log ADD COLUMN record_hash TEXT"],
        ];
        for (const [col, sql] of colMigrations) {
            if (!colNames.includes(col)) {
                db.exec(sql);
                logger.info("db_migration", { module: "db", column: col, table: "audit_log", phase: "5a" });
            }
        }
    }
    // 写保护触发器（INSERT ONLY）
    db.exec(`
    CREATE TRIGGER IF NOT EXISTS audit_log_no_modify BEFORE UPDATE ON audit_log
      BEGIN SELECT RAISE(ABORT, 'audit log is immutable'); END;
  `);
    db.exec(`
    CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
      BEGIN SELECT RAISE(ABORT, 'audit log is immutable'); END;
  `);
    logger.info("db_migration", { module: "db", detail: "audit_log write protection triggers ready", phase: "5a" });
}
catch (e) {
    logger.warn("db_migration_warning", { module: "db", table: "audit_log", phase: "5a", error: e.message });
}
// ═══════════════════════════════════════════════════════════════
// Phase 4a — Task Orchestrator（建表已在文件开头执行）
// ═══════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════
// v2.3 Phase 1.1 — 文件附件表
// ═══════════════════════════════════════════════════════════════
db.exec(`
  CREATE TABLE IF NOT EXISTS attachments (
    id           TEXT PRIMARY KEY,
    message_id   TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    filename     TEXT NOT NULL,
    mime_type    TEXT NOT NULL DEFAULT 'application/octet-stream',
    file_size    INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_by  TEXT NOT NULL,
    created_at   INTEGER NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_attachments_message ON attachments(message_id);
  CREATE INDEX IF NOT EXISTS idx_attachments_uploader ON attachments(uploaded_by);
`);
export const attachStmt = {
    insert: db.prepare(`INSERT INTO attachments VALUES (@id,@message_id,@filename,@mime_type,@file_size,@storage_path,@uploaded_by,@created_at)`),
    getById: db.prepare(`SELECT * FROM attachments WHERE id=?`),
    listByMessage: db.prepare(`SELECT id,filename,mime_type,file_size,uploaded_by,created_at FROM attachments WHERE message_id=? ORDER BY created_at ASC`),
    deleteById: db.prepare(`DELETE FROM attachments WHERE id=?`),
};
// ═══════════════════════════════════════════════════════════════
// v2.3 Phase 3.2: 数据库归档表（messages + audit_log）
// ═══════════════════════════════════════════════════════════════
db.exec(`
  CREATE TABLE IF NOT EXISTS messages_archive (
    id           TEXT PRIMARY KEY,
    from_agent   TEXT NOT NULL,
    to_agent     TEXT NOT NULL,
    content      TEXT NOT NULL,
    type         TEXT NOT NULL DEFAULT 'message',
    metadata     TEXT,
    status       TEXT NOT NULL DEFAULT 'unread',
    created_at   INTEGER NOT NULL,
    archived_at   INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
  );

  CREATE INDEX IF NOT EXISTS idx_messages_archive_created ON messages_archive(created_at);
  CREATE INDEX IF NOT EXISTS idx_messages_archive_to_agent ON messages_archive(to_agent);
`);
db.exec(`
  CREATE TABLE IF NOT EXISTS audit_log_archive (
    id           TEXT PRIMARY KEY,
    action       TEXT NOT NULL,
    agent_id     TEXT,
    target       TEXT,
    details      TEXT,
    ip_address   TEXT,
    created_at   INTEGER NOT NULL,
    prev_hash    TEXT,
    record_hash  TEXT,
    archived_at   INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
  );

  CREATE INDEX IF NOT EXISTS idx_audit_archive_timestamp ON audit_log_archive(created_at);
  CREATE INDEX IF NOT EXISTS idx_audit_archive_agent    ON audit_log_archive(agent_id);
`);
// ─── DB 统计信息（调试用） ────────────────────────────────
export function getDbStats() {
    const tables = [
        "messages", "tasks", "consumed_log",
        "agents", "auth_tokens", "dedup_cache",
        "memories", "agent_capabilities", "audit_log",
        "strategies", "strategy_feedback", "strategy_applications",
        "pipelines", "pipeline_tasks",
        "task_dependencies", "quality_gates",
        "attachments",
        "messages_archive", "audit_log_archive",
    ];
    const stats = {};
    for (const t of tables) {
        try {
            const row = db.prepare(`SELECT COUNT(*) as cnt FROM ${t}`).get();
            stats[t] = row?.cnt ?? 0;
        }
        catch {
            stats[t] = -1; // 表不存在
        }
    }
    return stats;
}
// ─── Phase 3.2: 归档方法 ──────────────────────────────────
/**
 * 归档 N 天前的消息（从 messages 移到 messages_archive）
 * @returns 归档的记录数
 */
export function archiveOldMessages(days = 30) {
    const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
    // 插入到归档表
    const insertSql = `
    INSERT OR IGNORE INTO messages_archive (id, from_agent, to_agent, content, type, metadata, status, created_at)
    SELECT id, from_agent, to_agent, content, type, metadata, status, created_at
    FROM messages WHERE created_at < ? AND id NOT IN (SELECT id FROM messages_archive)
  `;
    const insertResult = db.prepare(insertSql).run(cutoff);
    // 删除已归档的原始记录
    db.prepare(`DELETE FROM messages WHERE created_at < ? AND id IN (SELECT id FROM messages_archive)`).run(cutoff);
    return insertResult.changes;
}
/**
 * 归档 N 天前的审计日志（从 audit_log 移到 audit_log_archive）
 * @returns 归档的记录数
 */
export function archiveOldAuditLogs(days = 90) {
    const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
    // 插入到归档表
    const insertSql = `
    INSERT OR IGNORE INTO audit_log_archive (id, action, agent_id, target, details, ip_address, created_at, prev_hash, record_hash)
    SELECT id, action, agent_id, target, details, ip_address, created_at, prev_hash, record_hash
    FROM audit_log WHERE created_at < ? AND id NOT IN (SELECT id FROM audit_log_archive)
  `;
    const insertResult = db.prepare(insertSql).run(cutoff);
    // 删除已归档的原始记录
    // audit_log 有 BEFORE DELETE 触发器保护，需临时删除触发器再执行删除
    db.exec(`DROP TRIGGER IF EXISTS audit_log_no_delete`);
    db.exec(`DELETE FROM audit_log WHERE created_at < ? AND id IN (SELECT id FROM audit_log_archive)`);
    db.exec(`
    CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
      BEGIN SELECT RAISE(ABORT, 'audit log is immutable'); END;
  `);
    return insertResult.changes;
}
/**
 * 执行数据库 VACUUM（释放空闲页面，紧缩数据库文件）
 * 建议在低峰期调用（如凌晨 3-5 点）
 */
export function vacuumDatabase() {
    // 先执行 WAL 检查点（TRUNCATE 模式释放 WAL 文件空间）
    db.pragma(`wal_checkpoint(TRUNCATE)`);
    // 执行 VACUUM
    db.exec(`VACUUM`);
    logger.info("db_vacuum_executed", { module: "db" });
}
/**
 * 获取数据库文件大小（字节）
 */
export function getDbSize() {
    const fs = require("fs");
    try {
        const stats = fs.statSync(DB_PATH);
        return stats.size;
    }
    catch {
        return 0;
    }
}
/**
 * 获取增强版数据库统计信息（用于 MCP 工具 get_db_stats）
 */
export function getEnhancedDbStats() {
    const tableCounts = getDbStats();
    const dbSize = getDbSize();
    // WAL 大小
    let walSize = 0;
    const walPath = DB_PATH + "-wal";
    try {
        const fs = require("fs");
        if (fs.existsSync(walPath)) {
            walSize = fs.statSync(walPath).size;
        }
    }
    catch { /* ignore */ }
    // 最后归档时间
    let lastMsgArchive = null;
    let lastAuditArchive = null;
    try {
        const msgRow = db.prepare(`SELECT MAX(archived_at) as ts FROM messages_archive`).get();
        lastMsgArchive = msgRow?.ts ? new Date(msgRow.ts).toISOString() : null;
    }
    catch { /* ignore */ }
    try {
        const auditRow = db.prepare(`SELECT MAX(archived_at) as ts FROM audit_log_archive`).get();
        lastAuditArchive = auditRow?.ts ? new Date(auditRow.ts).toISOString() : null;
    }
    catch { /* ignore */ }
    return {
        table_counts: tableCounts,
        database_size_bytes: dbSize,
        database_size_mb: Math.round((dbSize / 1024 / 1024) * 100) / 100,
        wal_size_bytes: walSize,
        last_messages_archive: lastMsgArchive,
        last_audit_log_archive: lastAuditArchive,
    };
}
// ═══════════════════════════════════════════════════════════════
// Phase 6 — 定时清理过期数据
// ═══════════════════════════════════════════════════════════════
let cleanupTimer = null;
/**
 * 定时清理过期数据（每小时执行一次）
 * - 过期的 API Token（token_type='api_token'）
 * - 过期的去重缓存（超过 dedupTTL 秒）
 * - 过期的消费日志（>1天）
 */
export function scheduleCleanup(dedupTTL) {
    if (cleanupTimer) {
        clearInterval(cleanupTimer);
    }
    cleanupTimer = setInterval(() => {
        try {
            const expiredTokens = db.prepare("DELETE FROM auth_tokens WHERE expires_at IS NOT NULL AND expires_at < (strftime('%s', 'now') * 1000) AND token_type = 'api_token'").run();
            const cutoff = Date.now() - dedupTTL;
            const expiredDedup = db.prepare("DELETE FROM dedup_cache WHERE created_at < ?").run(cutoff);
            const expiredConsumed = db.prepare("DELETE FROM consumed_log WHERE consumed_at < (strftime('%s', 'now') * 1000 - 86400000)").run();
            logger.info("scheduled_cleanup", {
                module: "db",
                expired_tokens: expiredTokens.changes,
                expired_dedup: expiredDedup.changes,
                expired_consumed: expiredConsumed.changes,
            });
        }
        catch (err) {
            logError("scheduled_cleanup_error", err, { module: "db" });
        }
    }, 3600 * 1000);
    logger.info("cleanup_scheduler_started", {
        module: "db",
        interval_ms: 3600 * 1000,
        dedup_ttl_ms: dedupTTL,
    });
}
export function stopCleanup() {
    if (cleanupTimer) {
        clearInterval(cleanupTimer);
        cleanupTimer = null;
        logger.info("cleanup_scheduler_stopped", { module: "db" });
    }
}
//# sourceMappingURL=db.js.map