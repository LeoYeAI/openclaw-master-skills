/**
 * metrics.ts — Prometheus 兼容指标（Phase 5b / Phase 3.1）
 * 零依赖实现，内存存储
 *
 * 指标：
 *   - mcp_calls_total{tool_name, status, role} : Counter
 *   - active_sse_connections : Gauge
 *   - message_delivery_total{status} : Counter
 *   - http_requests_total{method, path, status} : Counter
 *   - http_request_duration_ms{method, path} : Histogram (简易)
 *   - db_query_duration_ms{operation} : Histogram (简易)
 *   ──────────────────────────────── Phase 3.1 新增 ────────────────────────────────
 *   - hub_agents_online : Gauge
 *   - hub_messages_total{status} : Gauge
 *   - hub_trust_scores{agent_id} : Gauge
 */
import type { Database as DatabaseType } from "better-sqlite3";
export declare function incrementCounter(name: string, labels?: Record<string, string>, value?: number): void;
export declare function setGauge(name: string, value: number): void;
export declare function incrementGauge(name: string, value?: number): void;
export declare function decrementGauge(name: string, value?: number): void;
export declare function observeHistogram(name: string, valueMs: number, labels?: Record<string, string>): void;
export declare function getMetricsOutput(): string;
export declare function incrementMcpCall(toolName: string, status: "success" | "error" | "denied", role: string): void;
export declare function trackHttpRequest(method: string, path: string, statusCode: number, durationMs: number): void;
export declare function trackDbQuery(operation: string, durationMs: number): void;
/**
 * 从 SQLite 数据库采集 Hub 层指标，返回 Prometheus 文本格式字符串。
 * 由 server.ts 在 /metrics 路由中调用。
 */
export declare function collectHubMetrics(db: DatabaseType): string;
