/**
 * logger.ts — 结构化 JSON 日志（Phase 5b）
 * 替换 console.log/error/warn 为 JSON 格式输出
 *
 * 输出目标：stdout（info/debug）+ stderr（warn/error）
 * 格式：{"timestamp":"ISO8601","level":"info","traceId":"xxx","module":"server","msg":"xxx",...meta}
 *
 * 环境变量：LOG_LEVEL（默认 info）
 */
export interface ChildLogger {
    info(msg: string, meta?: Record<string, unknown>): void;
    warn(msg: string, meta?: Record<string, unknown>): void;
    error(msg: string, meta?: Record<string, unknown>): void;
    debug(msg: string, meta?: Record<string, unknown>): void;
}
export declare const logger: {
    info(msg: string, meta?: Record<string, unknown>): void;
    warn(msg: string, meta?: Record<string, unknown>): void;
    error(msg: string, meta?: Record<string, unknown>): void;
    debug(msg: string, meta?: Record<string, unknown>): void;
    child(bindings: {
        traceId?: string;
        module?: string;
    }): ChildLogger;
};
/** 记录带 Error.stack 的错误（仅写入 stderr，不暴露给客户端） */
export declare function logError(label: string, err: unknown, meta?: Record<string, unknown>): void;
