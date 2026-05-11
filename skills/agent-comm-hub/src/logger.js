/**
 * logger.ts — 结构化 JSON 日志（Phase 5b）
 * 替换 console.log/error/warn 为 JSON 格式输出
 *
 * 输出目标：stdout（info/debug）+ stderr（warn/error）
 * 格式：{"timestamp":"ISO8601","level":"info","traceId":"xxx","module":"server","msg":"xxx",...meta}
 *
 * 环境变量：LOG_LEVEL（默认 info）
 */
const LOG_LEVEL_PRIORITY = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
};
const MIN_LEVEL = process.env.LOG_LEVEL || "info";
function shouldLog(level) {
    return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[MIN_LEVEL];
}
function write(entry) {
    if (!shouldLog(entry.level))
        return;
    const line = JSON.stringify(entry);
    if (entry.level === "warn" || entry.level === "error") {
        process.stderr.write(line + "\n");
    }
    else {
        process.stdout.write(line + "\n");
    }
}
function formatMsg(args) {
    return args.map(a => {
        if (a instanceof Error)
            return a.message;
        if (typeof a === "object" && a !== null)
            return JSON.stringify(a);
        return String(a);
    }).join(" ");
}
export const logger = {
    info(msg, meta) {
        write({ timestamp: new Date().toISOString(), level: "info", msg, ...meta });
    },
    warn(msg, meta) {
        write({ timestamp: new Date().toISOString(), level: "warn", msg, ...meta });
    },
    error(msg, meta) {
        write({ timestamp: new Date().toISOString(), level: "error", msg, ...meta });
    },
    debug(msg, meta) {
        write({ timestamp: new Date().toISOString(), level: "debug", msg, ...meta });
    },
    child(bindings) {
        return {
            info(msg, meta) {
                write({ timestamp: new Date().toISOString(), level: "info", traceId: bindings.traceId, module: bindings.module, msg, ...meta });
            },
            warn(msg, meta) {
                write({ timestamp: new Date().toISOString(), level: "warn", traceId: bindings.traceId, module: bindings.module, msg, ...meta });
            },
            error(msg, meta) {
                write({ timestamp: new Date().toISOString(), level: "error", traceId: bindings.traceId, module: bindings.module, msg, ...meta });
            },
            debug(msg, meta) {
                write({ timestamp: new Date().toISOString(), level: "debug", traceId: bindings.traceId, module: bindings.module, msg, ...meta });
            },
        };
    },
};
/** 记录带 Error.stack 的错误（仅写入 stderr，不暴露给客户端） */
export function logError(label, err, meta) {
    const message = err instanceof Error ? err.message : String(err);
    const stack = err instanceof Error ? err.stack : undefined;
    write({ timestamp: new Date().toISOString(), level: "error", msg: label, error: message, stack, ...meta });
}
//# sourceMappingURL=logger.js.map