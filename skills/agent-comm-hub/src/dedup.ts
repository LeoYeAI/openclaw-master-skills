/**
 * dedup.ts — 消息去重模块 (Phase 2)
 *
 * 功能：
 *   - 消息完整性校验：msg_hash = sha256(sender + receiver + content + nonce)
 *   - per-sender 递增 nonce 管理（SQLite 持久化，Phase 2）
 *   - dedup_cache 表操作（isDuplicate / recordHash）
 *   - TTL 定时清理（15min）
 *   - 消息体结构化分界（防 prompt injection）
 *
 * Phase 2 变更：
 *   - nonce 从 in-memory Map 迁移到 SQLite sender_nonces 表
 *   - Hub 重启后 nonce 从上次值继续递增
 *   - 启动时自动建表（IF NOT EXISTS）
 */
import { createHash } from "crypto";
import { db } from "./db.js";
import { auditLog } from "./security.js";
import { logError, logger } from "./logger.js";
import { getErrorMessage } from "./types.js";

// ─── 常量 ────────────────────────────────────────────────
const DEDUP_TTL_MS = parseInt(process.env.DEDUP_TTL ?? "900", 10) * 1000; // 默认 15 分钟
const DEDUP_CLEANUP_INTERVAL_MS = parseInt(process.env.DEDUP_CLEANUP_INTERVAL ?? "60000", 10); // 默认 1 分钟

// ─── sender_nonces 表初始化 ─────────────────────────────

/** 确保 sender_nonces 表存在（启动时调用） */
function ensureNonceTable(): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS sender_nonces (
      sender_id  TEXT PRIMARY KEY,
      last_nonce INTEGER NOT NULL DEFAULT 0,
      updated_at INTEGER NOT NULL
    );
  `);
}

// 模块加载时自动初始化
ensureNonceTable();

// ─── Per-Sender Nonce 管理（SQLite 持久化）────────────

/**
 * 获取 sender 的下一个 nonce（递增，持久化）
 * @returns 递增后的 nonce 值
 */
export function nextNonce(senderId: string): number {
  const row = db
    .prepare(`SELECT last_nonce FROM sender_nonces WHERE sender_id = ?`)
    .get(senderId) as any;

  const last = row ? row.last_nonce : 0;
  const next = last + 1;
  const now = Date.now();

  db.prepare(`
    INSERT INTO sender_nonces (sender_id, last_nonce, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT(sender_id) DO UPDATE SET last_nonce = ?, updated_at = ?
  `).run(senderId, next, now, next, now);

  return next;
}

/**
 * 获取 sender 的当前 nonce（不递增）
 */
export function currentNonce(senderId: string): number {
  const row = db
    .prepare(`SELECT last_nonce FROM sender_nonces WHERE sender_id = ?`)
    .get(senderId) as any;
  return row ? row.last_nonce : 0;
}

/**
 * 重置 sender 的 nonce（测试用）
 */
export function resetNonce(senderId: string): void {
  db.prepare(`DELETE FROM sender_nonces WHERE sender_id = ?`).run(senderId);
}

// ─── 消息哈希 ────────────────────────────────────────────

/**
 * 计算去重哈希（不含 nonce）
 * dedup_hash = sha256(sender + receiver + content)
 * 用于检测完全相同的消息（防止重复发送）
 */
export function computeDedupHash(
  sender: string,
  receiver: string,
  content: string
): string {
  const raw = `${sender}:${receiver}:${content}`;
  return createHash("sha256").update(raw).digest("hex");
}

/**
 * 计算消息完整性哈希（含 nonce）
 * msg_hash = sha256(sender + receiver + content + nonce)
 * 用于防篡改 + 客户端验证
 */
export function computeMsgHash(
  sender: string,
  receiver: string,
  content: string,
  nonce: number
): string {
  const raw = `${sender}:${receiver}:${content}:${nonce}`;
  return createHash("sha256").update(raw).digest("hex");
}

// ─── 重复检测 ────────────────────────────────────────────

/**
 * 检查消息是否重复（基于 msg_hash）
 * @returns true = 重复（应拒绝），false = 新消息
 */
export function isDuplicate(msgHash: string): boolean {
  try {
    const row = db
      .prepare(`SELECT msg_hash FROM dedup_cache WHERE msg_hash = ?`)
      .get(msgHash) as any;
    return !!row;
  } catch (err: unknown) {
    logError("dedup_isDuplicate_error", err);
    return false; // 出错时允许通过（安全优先于阻断）
  }
}

/**
 * 记录消息哈希到去重缓存
 */
export function recordHash(
  msgHash: string,
  senderId: string,
  nonce: number
): void {
  try {
    const now = Date.now();
    db.prepare(
      `INSERT OR IGNORE INTO dedup_cache (msg_hash, sender_id, nonce, created_at)
       VALUES (?, ?, ?, ?)`
    ).run(msgHash, senderId, nonce, now);
  } catch (err: unknown) {
    logError("dedup_recordHash_error", err);
  }
}

// ─── 消息体结构化分界 ────────────────────────────────────

/** 最大消息内容长度 */
const MAX_CONTENT_LENGTH = 50000;

/**
 * 消息体安全校验（防 prompt injection 和格式攻击）
 *
 * 检查项：
 *   1. 内容非空
 *   2. 长度限制（50KB）
 *   3. 不包含 NULL 字节（\x00 分界符保留）
 *   4. 不包含 SSE 注入模式（data: / event: / id:）
 *
 * @returns { safe: true } 或 { safe: false, reason: string }
 */
export function validateMessageBody(content: string): { safe: boolean; reason?: string } {
  // 非空检查
  if (!content || content.trim().length === 0) {
    return { safe: false, reason: "Message content cannot be empty" };
  }

  // 长度检查
  if (content.length > MAX_CONTENT_LENGTH) {
    return {
      safe: false,
      reason: `Message content too long (${content.length} > ${MAX_CONTENT_LENGTH} chars)`,
    };
  }

  // NULL 字节检查（\x00 是消息分界符，不能出现在正文）
  if (content.includes("\x00")) {
    return { safe: false, reason: "Message content contains NULL byte (\\x00)" };
  }

  // SSE 注入检测
  const ssePatterns = [/^data:\s*/m, /^event:\s*/m, /^id:\s*/m, /^retry:\s*/m];
  for (const pattern of ssePatterns) {
    if (pattern.test(content)) {
      return {
        safe: false,
        reason: `Message content contains potential SSE injection pattern: ${pattern.source}`,
      };
    }
  }

  return { safe: true };
}

/**
 * 完整的消息去重流程
 *
 * 1. 校验消息体
 * 2. 计算去重哈希（不含 nonce）并检查重复
 * 3. 分配 nonce
 * 4. 计算完整性哈希（含 nonce）
 * 5. 记录去重哈希
 *
 * @returns
 *   - { ok: true, msgHash, nonce } — 消息可以发送
 *   - { ok: false, reason } — 消息被拒绝
 */
export function dedupMessage(
  sender: string,
  receiver: string,
  content: string
): { ok: true; msgHash: string; nonce: number } | { ok: false; reason: string } {
  // 1. 校验消息体
  const validation = validateMessageBody(content);
  if (!validation.safe) {
    return { ok: false, reason: validation.reason! };
  }

  // 2. 计算去重哈希并检查重复（不含 nonce）
  const dedupHash = computeDedupHash(sender, receiver, content);
  if (isDuplicate(dedupHash)) {
    return { ok: false, reason: "Duplicate message detected (same content from same sender)" };
  }

  // 3. 分配 nonce
  const nonce = nextNonce(sender);

  // 4. 计算完整性哈希（含 nonce）
  const msgHash = computeMsgHash(sender, receiver, content, nonce);

  // 5. 记录去重哈希
  recordHash(dedupHash, sender, nonce);

  return { ok: true, msgHash, nonce };
}

// ─── TTL 清理 ────────────────────────────────────────────

let cleanupTimer: ReturnType<typeof setInterval> | null = null;

/**
 * 清理过期的去重缓存条目
 */
export function cleanupExpiredEntries(): number {
  const cutoff = Date.now() - DEDUP_TTL_MS;
  try {
    const result = db.prepare(
      `DELETE FROM dedup_cache WHERE created_at < ?`
    ).run(cutoff);
    const deleted = result.changes;
    if (deleted > 0) {
      logger.info("dedup_cleanup", { module: "dedup", deleted, ttl_ms: DEDUP_TTL_MS });
      // Phase 5a Day 2: 审计批量删除去重缓存
      auditLog("cleanup_dedup_cache", "system:dedup", `batch`, `deleted=${deleted}, ttl=${DEDUP_TTL_MS}ms`);
    }
    return deleted;
  } catch (err: unknown) {
    logError("dedup_cleanup_error", err);
    return 0;
  }
}

/**
 * 启动 TTL 定时清理
 */
export function startDedupCleanup(): void {
  if (cleanupTimer) {
    clearInterval(cleanupTimer);
  }

  logger.info("dedup_cleanup_started", { module: "dedup", interval_ms: DEDUP_CLEANUP_INTERVAL_MS, ttl_ms: DEDUP_TTL_MS });

  cleanupTimer = setInterval(() => {
    cleanupExpiredEntries();
  }, DEDUP_CLEANUP_INTERVAL_MS);
}

/**
 * 停止 TTL 定时清理
 */
export function stopDedupCleanup(): void {
  if (cleanupTimer) {
    clearInterval(cleanupTimer);
    cleanupTimer = null;
    logger.info("dedup_cleanup_stopped", { module: "dedup" });
  }
}
