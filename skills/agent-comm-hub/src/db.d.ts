/**
 * db.ts — SQLite 持久化层
 * 消息 + 任务 两张表，进程重启数据不丢失
 */
import { type Database as DatabaseType, type Statement } from "better-sqlite3";
export declare const db: DatabaseType;
export interface Message {
    id: string;
    from_agent: string;
    to_agent: string;
    content: string;
    type: "message" | "task_assign" | "task_update" | "ack";
    metadata?: string | null;
    status: "unread" | "delivered" | "read" | "acknowledged";
    created_at: number;
}
export declare const msgStmt: Record<string, Statement>;
export interface ConsumedEntry {
    id: string;
    agent_id: string;
    resource: string;
    resource_type: string;
    action: string;
    notes?: string | null;
    consumed_at: number;
}
export declare const consumedStmt: Record<string, Statement>;
export interface Task {
    id: string;
    assigned_by: string;
    assigned_to: string;
    description: string;
    context?: string | null;
    priority: "low" | "normal" | "high" | "urgent";
    status: "inbox" | "assigned" | "waiting" | "pending" | "in_progress" | "completed" | "failed" | "cancelled";
    result?: string | null;
    progress: number;
    pipeline_id?: string | null;
    order_index: number;
    required_capability?: string | null;
    due_at?: number | null;
    assigned_at?: number | null;
    completed_at?: number | null;
    tags?: string | null;
    parallel_group?: string | null;
    handoff_status?: string | null;
    handoff_to?: string | null;
    created_at: number;
    updated_at: number;
}
export declare const taskStmt: Record<string, Statement>;
export interface Pipeline {
    id: string;
    name: string;
    description?: string | null;
    status: "draft" | "active" | "completed" | "cancelled";
    creator: string;
    config?: string | null;
    created_at: number;
    updated_at: number;
}
export interface PipelineTask {
    id: string;
    pipeline_id: string;
    task_id: string;
    order_index: number;
    created_at: number;
}
export declare const pipelineStmt: Record<string, Statement>;
export declare const pipelineTaskStmt: Record<string, Statement>;
export interface Attachment {
    id: string;
    message_id: string;
    filename: string;
    mime_type: string;
    file_size: number;
    storage_path: string;
    uploaded_by: string;
    created_at: number;
}
export declare const attachStmt: Record<string, Statement>;
export declare function getDbStats(): Record<string, number>;
/**
 * 归档 N 天前的消息（从 messages 移到 messages_archive）
 * @returns 归档的记录数
 */
export declare function archiveOldMessages(days?: number): number;
/**
 * 归档 N 天前的审计日志（从 audit_log 移到 audit_log_archive）
 * @returns 归档的记录数
 */
export declare function archiveOldAuditLogs(days?: number): number;
/**
 * 执行数据库 VACUUM（释放空闲页面，紧缩数据库文件）
 * 建议在低峰期调用（如凌晨 3-5 点）
 */
export declare function vacuumDatabase(): void;
/**
 * 获取数据库文件大小（字节）
 */
export declare function getDbSize(): number;
/**
 * 获取增强版数据库统计信息（用于 MCP 工具 get_db_stats）
 */
export declare function getEnhancedDbStats(): {
    table_counts: Record<string, number>;
    database_size_bytes: number;
    database_size_mb: number;
    wal_size_bytes: number;
    last_messages_archive: string | null;
    last_audit_log_archive: string | null;
};
/**
 * 定时清理过期数据（每小时执行一次）
 * - 过期的 API Token（token_type='api_token'）
 * - 过期的去重缓存（超过 dedupTTL 秒）
 * - 过期的消费日志（>1天）
 */
export declare function scheduleCleanup(dedupTTL: number): void;
export declare function stopCleanup(): void;
