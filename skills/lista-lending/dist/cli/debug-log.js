import { appendFileSync, mkdirSync } from "fs";
import { dirname, resolve } from "path";
function writeRecord(filePath, record) {
    try {
        appendFileSync(filePath, `${JSON.stringify(record)}\n`, "utf8");
    }
    catch {
        // Never block command execution because of debug logging failures.
    }
}
function toText(chunk, encoding) {
    if (typeof chunk === "string")
        return chunk;
    if (chunk instanceof Uint8Array) {
        return Buffer.from(chunk).toString(encoding || "utf8");
    }
    return String(chunk);
}
function normalizeWriteArgs(encodingOrCb, cb) {
    if (typeof encodingOrCb === "function") {
        return { encoding: undefined, callback: encodingOrCb };
    }
    return { encoding: encodingOrCb, callback: cb };
}
function parseJsonIfPossible(line) {
    try {
        return JSON.parse(line);
    }
    catch {
        return undefined;
    }
}
function isStructuredJson(value) {
    return Array.isArray(value) || (typeof value === "object" && value !== null);
}
function patchWriteStream(streamName, stream, filePath, skill) {
    const originalWrite = stream.write.bind(stream);
    let buffer = "";
    const emitLine = (line) => {
        if (!line)
            return;
        const parsed = parseJsonIfPossible(line);
        const record = {
            ts: new Date().toISOString(),
            pid: process.pid,
            skill,
            stream: streamName,
            line,
        };
        if (isStructuredJson(parsed)) {
            record.json = parsed;
        }
        writeRecord(filePath, record);
    };
    const flushBuffer = () => {
        if (!buffer)
            return;
        emitLine(buffer.replace(/\r$/, ""));
        buffer = "";
    };
    stream.write = ((chunk, encodingOrCb, cb) => {
        const { encoding, callback } = normalizeWriteArgs(encodingOrCb, cb);
        const text = toText(chunk, encoding);
        buffer += text;
        let index = buffer.indexOf("\n");
        while (index >= 0) {
            const line = buffer.slice(0, index).replace(/\r$/, "");
            emitLine(line);
            buffer = buffer.slice(index + 1);
            index = buffer.indexOf("\n");
        }
        if (encoding !== undefined && callback) {
            return originalWrite(chunk, encoding, callback);
        }
        if (encoding !== undefined) {
            return originalWrite(chunk, encoding);
        }
        if (callback) {
            return originalWrite(chunk, callback);
        }
        return originalWrite(chunk);
    });
    return flushBuffer;
}
export function setupDebugLogFile(skill, cliLogFile) {
    const requested = cliLogFile || process.env.SKILL_DEBUG_LOG_FILE || process.env.DEBUG_LOG_FILE;
    if (!requested)
        return null;
    const filePath = resolve(requested);
    try {
        mkdirSync(dirname(filePath), { recursive: true });
    }
    catch {
        // Ignore and continue.
    }
    // Propagate to child processes (lista-lending -> lista-wallet-connect).
    process.env.SKILL_DEBUG_LOG_FILE = filePath;
    const flushStdout = patchWriteStream("stdout", process.stdout, filePath, skill);
    const flushStderr = patchWriteStream("stderr", process.stderr, filePath, skill);
    const flushAll = () => {
        flushStdout();
        flushStderr();
    };
    process.on("beforeExit", flushAll);
    process.on("exit", flushAll);
    writeRecord(filePath, {
        ts: new Date().toISOString(),
        pid: process.pid,
        skill,
        stream: "stderr",
        line: "debug_log_enabled",
        config: {
            filePath,
            argv: process.argv.slice(2),
        },
    });
    return filePath;
}
