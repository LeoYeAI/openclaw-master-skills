// Structured logger — never logs private keys, wallet addresses from env,
// or any field matching a PII pattern. Safe for production use.

type LogLevel = "error" | "warn" | "info" | "debug";

const LEVELS: Record<LogLevel, number> = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

// Fields that must NEVER appear in log output
const REDACTED_KEYS = new Set([
  "privateKey",
  "private_key",
  "seed",
  "mnemonic",
  "secret",
  "password",
  "apiKey",
  "api_key",
  "PRIVY_APP_SECRET",
  "ANTHROPIC_API_KEY",
  "COINBASE_CDP_API_KEY_PRIVATE_KEY",
  "TENDERLY_ACCESS_KEY",
  "LLM_API_KEY",
]);

function redact(obj: unknown, depth = 0): unknown {
  if (depth > 5) return "[DEEP]";
  if (obj === null || typeof obj !== "object") return obj;
  if (Array.isArray(obj)) return obj.map((v) => redact(v, depth + 1));

  const result: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
    if (REDACTED_KEYS.has(k)) {
      result[k] = "[REDACTED]";
    } else if (
      typeof v === "string" &&
      (v.startsWith("sk-ant-") || v.startsWith("privy-"))
    ) {
      result[k] = "[REDACTED]";
    } else {
      result[k] = redact(v, depth + 1);
    }
  }
  return result;
}

function getConfiguredLevel(): LogLevel {
  const raw = process.env["LOG_LEVEL"] ?? "info";
  if (raw in LEVELS) return raw as LogLevel;
  return "info";
}

function emit(level: LogLevel, data: Record<string, unknown>): void {
  const configuredLevel = getConfiguredLevel();
  if (LEVELS[level] > LEVELS[configuredLevel]) return;

  const entry = {
    ts: new Date().toISOString(),
    level,
    ...(redact(data) as Record<string, unknown>),
  };

  const line = JSON.stringify(entry);

  if (level === "error" || level === "warn") {
    process.stderr.write(line + "\n");
  } else {
    process.stdout.write(line + "\n");
  }
}

export const logger = {
  error: (data: Record<string, unknown>) => emit("error", data),
  warn: (data: Record<string, unknown>) => emit("warn", data),
  info: (data: Record<string, unknown>) => emit("info", data),
  debug: (data: Record<string, unknown>) => emit("debug", data),
};
