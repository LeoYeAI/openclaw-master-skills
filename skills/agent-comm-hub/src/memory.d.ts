export interface MemoryEntry {
    id: string;
    agent_id: string;
    title: string | null;
    content: string;
    scope: "private" | "group" | "collective";
    tags: string | null;
    source_agent_id: string | null;
    source_task_id: string | null;
    created_at: number;
    updated_at: number | null;
}
export interface MemoryStats {
    total: number;
    by_agent: Record<string, number>;
    by_scope: Record<string, number>;
    fts_entries: number;
}
/**
 * 存储新记忆
 *
 * @returns
 *   - { ok: true, memory } — 成功
 *   - { ok: false, error } — 失败
 */
export declare function storeMemory(agentId: string, content: string, options?: {
    title?: string;
    scope?: "private" | "group" | "collective";
    tags?: string[];
    source_agent_id?: string;
    source_task_id?: string;
}): {
    ok: true;
    memory: MemoryEntry;
} | {
    ok: false;
    error: string;
};
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
export declare function recallMemory(query: string, agentId: string, options?: {
    limit?: number;
    scope?: "private" | "group" | "collective" | "all";
}): MemoryEntry[];
/**
 * 列出 Agent 的记忆
 */
export declare function listMemories(agentId: string, options?: {
    scope?: "private" | "group" | "collective" | "all";
    limit?: number;
    offset?: number;
}): MemoryEntry[];
/**
 * 删除记忆
 * 仅允许删除自己的记忆，或 admin 删除任何记忆
 */
export declare function deleteMemory(memoryId: string, agentId: string, role: string): {
    ok: true;
    deleted: boolean;
} | {
    ok: false;
    error: string;
};
/**
 * 获取记忆统计信息
 */
export declare function getMemoryStats(): MemoryStats;
/**
 * 为所有已有 memories 重建 FTS 索引（Phase 2 Migration）
 * 在 server.ts 启动时调用一次
 */
export declare function rebuildFtsIndex(): void;
