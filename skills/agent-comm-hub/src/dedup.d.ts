/**
 * 获取 sender 的下一个 nonce（递增，持久化）
 * @returns 递增后的 nonce 值
 */
export declare function nextNonce(senderId: string): number;
/**
 * 获取 sender 的当前 nonce（不递增）
 */
export declare function currentNonce(senderId: string): number;
/**
 * 重置 sender 的 nonce（测试用）
 */
export declare function resetNonce(senderId: string): void;
/**
 * 计算去重哈希（不含 nonce）
 * dedup_hash = sha256(sender + receiver + content)
 * 用于检测完全相同的消息（防止重复发送）
 */
export declare function computeDedupHash(sender: string, receiver: string, content: string): string;
/**
 * 计算消息完整性哈希（含 nonce）
 * msg_hash = sha256(sender + receiver + content + nonce)
 * 用于防篡改 + 客户端验证
 */
export declare function computeMsgHash(sender: string, receiver: string, content: string, nonce: number): string;
/**
 * 检查消息是否重复（基于 msg_hash）
 * @returns true = 重复（应拒绝），false = 新消息
 */
export declare function isDuplicate(msgHash: string): boolean;
/**
 * 记录消息哈希到去重缓存
 */
export declare function recordHash(msgHash: string, senderId: string, nonce: number): void;
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
export declare function validateMessageBody(content: string): {
    safe: boolean;
    reason?: string;
};
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
export declare function dedupMessage(sender: string, receiver: string, content: string): {
    ok: true;
    msgHash: string;
    nonce: number;
} | {
    ok: false;
    reason: string;
};
/**
 * 清理过期的去重缓存条目
 */
export declare function cleanupExpiredEntries(): number;
/**
 * 启动 TTL 定时清理
 */
export declare function startDedupCleanup(): void;
/**
 * 停止 TTL 定时清理
 */
export declare function stopDedupCleanup(): void;
