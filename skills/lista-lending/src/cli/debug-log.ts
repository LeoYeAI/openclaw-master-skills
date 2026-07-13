import { appendFileSync, mkdirSync } from "fs";
import { dirname, resolve } from "path";

type StreamName = "stdout" | "stderr";
type WriteCallback = (err?: Error | null) => void;

function writeRecord(filePath: string, record: Record<string, unknown>): void {
  try {
    appendFileSync(filePath, `${JSON.stringify(record)}\n`, "utf8");
  } catch {
    // Never block command execution because of debug logging failures.
  }
}

function toText(chunk: unknown, encoding?: BufferEncoding): string {
  if (typeof chunk === "string") return chunk;
  if (chunk instanceof Uint8Array) {
    return Buffer.from(chunk).toString(encoding || "utf8");
  }
  return String(chunk);
}

function normalizeWriteArgs(
  encodingOrCb?: BufferEncoding | WriteCallback,
  cb?: WriteCallback
): { encoding?: BufferEncoding; callback?: WriteCallback } {
  if (typeof encodingOrCb === "function") {
    return { encoding: undefined, callback: encodingOrCb };
  }
  return { encoding: encodingOrCb, callback: cb };
}

function parseJsonIfPossible(line: string): unknown | undefined {
  try {
    return JSON.parse(line);
  } catch {
    return undefined;
  }
}

function isStructuredJson(value: unknown): value is Record<string, unknown> | unknown[] {
  return Array.isArray(value) || (typeof value === "object" && value !== null);
}

function patchWriteStream(
  streamName: StreamName,
  stream: NodeJS.WriteStream,
  filePath: string,
  skill: string
): () => void {
  const originalWrite = stream.write.bind(stream) as typeof stream.write;
  let buffer = "";

  const emitLine = (line: string): void => {
    if (!line) return;
    const parsed = parseJsonIfPossible(line);
    const record: Record<string, unknown> = {
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

  const flushBuffer = (): void => {
    if (!buffer) return;
    emitLine(buffer.replace(/\r$/, ""));
    buffer = "";
  };

  stream.write = ((
    chunk: unknown,
    encodingOrCb?: BufferEncoding | WriteCallback,
    cb?: WriteCallback
  ): boolean => {
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
      return originalWrite(chunk as never, encoding as never, callback as never);
    }
    if (encoding !== undefined) {
      return originalWrite(chunk as never, encoding as never);
    }
    if (callback) {
      return originalWrite(chunk as never, callback as never);
    }
    return originalWrite(chunk as never);
  }) as typeof stream.write;

  return flushBuffer;
}

export function setupDebugLogFile(skill: string, cliLogFile?: string): string | null {
  const requested = cliLogFile || process.env.SKILL_DEBUG_LOG_FILE || process.env.DEBUG_LOG_FILE;
  if (!requested) return null;

  const filePath = resolve(requested);
  try {
    mkdirSync(dirname(filePath), { recursive: true });
  } catch {
    // Ignore and continue.
  }

  // Propagate to child processes (lista-lending -> lista-wallet-connect).
  process.env.SKILL_DEBUG_LOG_FILE = filePath;

  const flushStdout = patchWriteStream("stdout", process.stdout, filePath, skill);
  const flushStderr = patchWriteStream("stderr", process.stderr, filePath, skill);
  const flushAll = (): void => {
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
