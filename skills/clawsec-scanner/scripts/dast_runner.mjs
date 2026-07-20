#!/usr/bin/env node

/**
 * DAST (Dynamic Application Security Testing) Runner for ClawSec Scanner.
 *
 * Scope:
 * - Discover OpenClaw hooks from target directories
 * - Execute real hook handlers in an isolated harness process
 * - Validate malicious-input resilience, timeout behavior, output bounds,
 *   and event mutation safety
 */

import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

import { generateReport, formatReportJson, formatReportText } from "../lib/report.mjs";
import { getTimestamp } from "../lib/utils.mjs";

/**
 * @typedef {import('../lib/types.ts').Vulnerability} Vulnerability
 * @typedef {import('../lib/types.ts').ScanReport} ScanReport
 */

const DEFAULT_TIMEOUT_MS = 30000;
const MAX_OUTPUT_MESSAGES = 25;
const MAX_OUTPUT_CHARS = 20000;
const SKIP_DIR_NAMES = new Set([
  ".git",
  ".github",
  ".idea",
  ".vscode",
  "node_modules",
  "dist",
  "build",
  "coverage",
  ".openclaw",
]);

const MALICIOUS_PAYLOADS = [
  "<script>alert('XSS')</script>",
  "'; DROP TABLE users; --",
  "; rm -rf /",
  "$(whoami)",
  "..\\..\\..\\windows\\system32\\config\\sam",
  "../../../etc/passwd",
  "test\0malicious",
  "A".repeat(200000),
];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const HOOK_EXECUTOR_PATH = path.join(__dirname, "dast_hook_executor.mjs");

/**
 * @typedef {Object} HookDescriptor
 * @property {string} name
 * @property {string} hookDir
 * @property {string} hookFile
 * @property {string} handlerPath
 * @property {string[]} events
 * @property {string} exportName
 */

/**
 * Parse CLI arguments.
 *
 * @param {string[]} argv
 * @returns {{target: string, format: 'json' | 'text', timeout: number}}
 */
function parseArgs(argv) {
  const parsed = {
    target: ".",
    format: "json",
    timeout: DEFAULT_TIMEOUT_MS,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--target") {
      parsed.target = String(argv[i + 1] ?? "").trim();
      i += 1;
      continue;
    }

    if (token === "--format") {
      const value = String(argv[i + 1] ?? "json").trim();
      if (value !== "json" && value !== "text") {
        throw new Error("Invalid --format value. Use 'json' or 'text'.");
      }
      parsed.format = value;
      i += 1;
      continue;
    }

    if (token === "--timeout") {
      const value = Number.parseInt(String(argv[i + 1] ?? ""), 10);
      if (!Number.isFinite(value) || value <= 0) {
        throw new Error("Invalid --timeout value. Must be a positive integer (milliseconds).");
      }
      parsed.timeout = value;
      i += 1;
      continue;
    }

    if (token === "--help" || token === "-h") {
      printUsage();
      process.exit(0);
    }

    throw new Error(`Unknown argument: ${token}`);
  }

  if (!parsed.target) {
    throw new Error("Missing required argument: --target");
  }

  return parsed;
}

function printUsage() {
  process.stderr.write(
    [
      "Usage:",
      "  node scripts/dast_runner.mjs --target <path> [--format json|text] [--timeout ms]",
      "",
      "Examples:",
      "  node scripts/dast_runner.mjs --target ./skills/",
      "  node scripts/dast_runner.mjs --target ./skills/ --format text",
      "  node scripts/dast_runner.mjs --target ./skills/ --timeout 60000",
      "",
      "Flags:",
      "  --target   Target skill/hook directory to test (required)",
      "  --format   Output format: json or text (default: json)",
      `  --timeout  Per-hook invocation timeout in milliseconds (default: ${DEFAULT_TIMEOUT_MS})`,
      "",
    ].join("\n"),
  );
}

/**
 * @param {string} filePath
 * @returns {Promise<boolean>}
 */
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * @param {string} markdown
 * @returns {string}
 */
function extractFrontmatter(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---/);
  return match ? match[1] : "";
}

/**
 * @param {string} frontmatter
 * @returns {string[]}
 */
function parseEvents(frontmatter) {
  const defaultEvents = ["command:new"];
  if (!frontmatter) return defaultEvents;

  const jsonStyle = frontmatter.match(/"events"\s*:\s*\[([^\]]*)\]/m);
  const yamlStyle = frontmatter.match(/events\s*:\s*\[([^\]]*)\]/m);
  const raw = jsonStyle?.[1] ?? yamlStyle?.[1];

  if (!raw) return defaultEvents;

  const events = [];
  const quotedRegex = /"([^"]+)"|'([^']+)'/g;

  let quotedMatch = quotedRegex.exec(raw);
  while (quotedMatch) {
    const value = quotedMatch[1] || quotedMatch[2];
    if (value && value.includes(":")) {
      events.push(value.trim());
    }
    quotedMatch = quotedRegex.exec(raw);
  }

  if (events.length === 0) {
    const fallback = raw
      .split(",")
      .map((part) => part.trim())
      .map((part) => part.replace(/^['"]|['"]$/g, ""))
      .filter((part) => part.includes(":"));
    events.push(...fallback);
  }

  return events.length > 0 ? Array.from(new Set(events)) : defaultEvents;
}

/**
 * @param {string} frontmatter
 * @param {string} fallback
 * @returns {string}
 */
function parseHookName(frontmatter, fallback) {
  if (!frontmatter) return fallback;

  const match = frontmatter.match(/^name\s*:\s*(.+)$/m);
  if (!match) return fallback;

  return match[1].trim().replace(/^['"]|['"]$/g, "") || fallback;
}

/**
 * @param {string} frontmatter
 * @returns {string}
 */
function parseExportName(frontmatter) {
  if (!frontmatter) return "default";

  const jsonStyle = frontmatter.match(/"export"\s*:\s*"([^"]+)"/m);
  if (jsonStyle?.[1]) return jsonStyle[1].trim();

  const yamlStyle = frontmatter.match(/^export\s*:\s*(.+)$/m);
  if (yamlStyle?.[1]) {
    const value = yamlStyle[1].trim().replace(/^['"]|['"]$/g, "");
    return value || "default";
  }

  return "default";
}

/**
 * @param {string} hookDir
 * @returns {Promise<string | null>}
 */
async function resolveHandlerPath(hookDir) {
  const candidates = [
    "handler.mjs",
    "handler.js",
    "handler.cjs",
    "handler.ts",
    "index.mjs",
    "index.js",
    "index.cjs",
    "index.ts",
  ];

  for (const candidate of candidates) {
    const fullPath = path.join(hookDir, candidate);
    if (await fileExists(fullPath)) {
      return fullPath;
    }
  }

  return null;
}

/**
 * @param {string} targetPath
 * @returns {Promise<HookDescriptor[]>}
 */
export async function discoverHooks(targetPath) {
  const hooks = [];
  const absoluteTarget = path.resolve(targetPath);

  /**
   * @param {string} dir
   * @returns {Promise<void>}
   */
  async function walk(dir) {
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        if (SKIP_DIR_NAMES.has(entry.name)) {
          continue;
        }

        await walk(fullPath);
        continue;
      }

      if (!entry.isFile() || entry.name !== "HOOK.md") {
        continue;
      }

      const hookDir = path.dirname(fullPath);
      const hookMd = await fs.readFile(fullPath, "utf8");
      const frontmatter = extractFrontmatter(hookMd);
      const handlerPath = await resolveHandlerPath(hookDir);

      if (!handlerPath) {
        continue;
      }

      hooks.push({
        name: parseHookName(frontmatter, path.basename(hookDir)),
        hookDir,
        hookFile: fullPath,
        handlerPath,
        events: parseEvents(frontmatter),
        exportName: parseExportName(frontmatter),
      });
    }
  }

  await walk(absoluteTarget);

  return hooks;
}

/**
 * @param {string} eventKey
 * @returns {{type: string, action: string}}
 */
function splitEventKey(eventKey) {
  const parts = String(eventKey ?? "").split(":");
  const type = parts.shift() || "command";
  const action = parts.join(":") || "new";
  return { type, action };
}

/**
 * @param {string} eventKey
 * @param {string} payload
 * @param {string} targetPath
 * @returns {Record<string, unknown>}
 */
export function buildEvent(eventKey, payload, targetPath) {
  const { type, action } = splitEventKey(eventKey);

  return {
    type,
    action,
    sessionKey: "clawsec-dast-session",
    timestamp: new Date().toISOString(),
    messages: [],
    context: {
      content: payload,
      transcript: payload,
      workspaceDir: path.resolve(targetPath),
      channelId: "dast-harness",
      commandSource: "dast",
      bootstrapFiles: [],
    },
  };
}

/**
 * @typedef {Object} HarnessInvocationResult
 * @property {boolean} timedOut
 * @property {number} exitCode
 * @property {string} stderr
 * @property {Record<string, unknown> | null} parsed
 * @property {string | null} parseError
 */

/**
 * @param {HookDescriptor} hook
 * @param {Record<string, unknown>} event
 * @param {Record<string, unknown>} context
 * @param {number} timeoutMs
 * @returns {Promise<HarnessInvocationResult>}
 */
async function invokeHookHarness(hook, event, context, timeoutMs) {
  const encodedEvent = Buffer.from(JSON.stringify(event), "utf8").toString("base64");
  const encodedContext = Buffer.from(JSON.stringify(context), "utf8").toString("base64");

  const args = [
    HOOK_EXECUTOR_PATH,
    "--handler",
    hook.handlerPath,
    "--export",
    hook.exportName || "default",
    "--event",
    encodedEvent,
    "--context",
    encodedContext,
  ];

  return new Promise((resolve) => {
    const proc = spawn("node", args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        ...process.env,
        CLAWSEC_DAST_HARNESS: "1",
      },
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill("SIGKILL");
    }, timeoutMs);

    proc.stdout.on("data", (chunk) => {
      stdout += String(chunk);
    });

    proc.stderr.on("data", (chunk) => {
      stderr += String(chunk);
    });

    proc.on("close", (code) => {
      clearTimeout(timer);

      const raw = stdout.trim();
      if (!raw) {
        resolve({
          timedOut,
          exitCode: code ?? 1,
          stderr,
          parsed: null,
          parseError: raw ? null : "Harness produced no JSON output",
        });
        return;
      }

      try {
        const parsed = JSON.parse(raw);
        resolve({
          timedOut,
          exitCode: code ?? 1,
          stderr,
          parsed,
          parseError: null,
        });
      } catch (error) {
        resolve({
          timedOut,
          exitCode: code ?? 1,
          stderr,
          parsed: null,
          parseError: error instanceof Error ? error.message : String(error),
        });
      }
    });
  });
}

/**
 * @param {unknown} value
 * @returns {value is Record<string, unknown>}
 */
function isObject(value) {
  return typeof value === "object" && value !== null;
}

/**
 * @param {unknown} parsed
 * @returns {{ok: boolean, error: string, messagesCount: number, messagesCharCount: number, coreAfter: Record<string, unknown>}}
 */
function normalizeHarnessPayload(parsed) {
  if (!isObject(parsed)) {
    return {
      ok: false,
      error: "Harness output is not an object",
      messagesCount: 0,
      messagesCharCount: 0,
      coreAfter: {},
    };
  }

  const ok = parsed.ok === true;
  const error = typeof parsed.error === "string" ? parsed.error : "";
  const messagesCount = Number(parsed.messages_count ?? 0) || 0;
  const messagesCharCount = Number(parsed.messages_char_count ?? 0) || 0;
  const coreAfter = isObject(parsed.core_after) ? parsed.core_after : {};

  return {
    ok,
    error,
    messagesCount,
    messagesCharCount,
    coreAfter,
  };
}

/**
 * @param {string} input
 * @returns {string}
 */
function slug(input) {
  return String(input)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
}

/**
 * @param {string} reason
 * @returns {boolean}
 */
function isHarnessCapabilityError(reason) {
  const normalized = String(reason ?? "").toLowerCase();
  return (
    normalized.includes("typescript compiler not available")
    || normalized.includes("does not export a handler function")
    || normalized.includes("is not a function")
  );
}

/**
 * @param {Vulnerability[]} bucket
 * @param {string} id
 * @param {'critical' | 'high' | 'medium' | 'low' | 'info'} severity
 * @param {HookDescriptor} hook
 * @param {string} eventKey
 * @param {string} title
 * @param {string} description
 */
function pushHookVulnerability(bucket, id, severity, hook, eventKey, title, description) {
  bucket.push({
    id,
    source: "dast",
    severity,
    package: hook.name,
    version: `${eventKey}:${path.basename(hook.handlerPath)}`,
    fixed_version: "",
    title,
    description,
    references: [hook.hookFile],
    discovered_at: getTimestamp(),
  });
}

/**
 * @param {HookDescriptor} hook
 * @param {string} targetPath
 * @param {number} timeoutMs
 * @returns {Promise<Vulnerability[]>}
 */
async function evaluateHook(hook, targetPath, timeoutMs) {
  const findings = [];
  const invocationTimeoutMs = Math.max(1000, timeoutMs);

  for (const eventKey of hook.events) {
    const safeEvent = buildEvent(eventKey, "safe baseline input", targetPath);
    const safeContext = {
      skillPath: hook.hookDir,
      agentPlatform: "openclaw",
      dastMode: true,
      targetPath: path.resolve(targetPath),
      event: eventKey,
    };

    const safeResult = await invokeHookHarness(hook, safeEvent, safeContext, invocationTimeoutMs);

    if (safeResult.timedOut) {
      pushHookVulnerability(
        findings,
        `DAST-TIMEOUT-${slug(`${hook.name}-${eventKey}`)}`,
        "high",
        hook,
        eventKey,
        "Hook times out under baseline input",
        `Hook execution exceeded ${invocationTimeoutMs}ms for event '${eventKey}' under safe baseline input.`,
      );
      continue;
    }

    if (safeResult.parseError) {
      pushHookVulnerability(
        findings,
        `DAST-HARNESS-${slug(`${hook.name}-${eventKey}`)}`,
        "medium",
        hook,
        eventKey,
        "Hook harness output invalid",
        `Could not parse harness output for event '${eventKey}': ${safeResult.parseError}. stderr: ${safeResult.stderr || "(empty)"}`,
      );
      continue;
    }

    const normalizedSafe = normalizeHarnessPayload(safeResult.parsed);
    if (!normalizedSafe.ok) {
      const reason = normalizedSafe.error || safeResult.stderr || "unknown error";

      if (isHarnessCapabilityError(reason)) {
        pushHookVulnerability(
          findings,
          `DAST-COVERAGE-${slug(`${hook.name}-${eventKey}`)}`,
          "info",
          hook,
          eventKey,
          "Hook not executable in local DAST harness",
          `DAST harness could not execute hook for event '${eventKey}' due to runtime capability limits: ${reason}`,
        );
      } else {
        pushHookVulnerability(
          findings,
          `DAST-CRASH-${slug(`${hook.name}-${eventKey}`)}`,
          "high",
          hook,
          eventKey,
          "Hook throws on baseline input",
          `Hook execution failed for event '${eventKey}' under safe baseline input: ${reason}`,
        );
      }
      continue;
    }

    const mutationObserved =
      normalizedSafe.coreAfter.type !== safeEvent.type ||
      normalizedSafe.coreAfter.action !== safeEvent.action ||
      normalizedSafe.coreAfter.sessionKey !== safeEvent.sessionKey;

    if (mutationObserved) {
      pushHookVulnerability(
        findings,
        `DAST-MUTATION-${slug(`${hook.name}-${eventKey}`)}`,
        "low",
        hook,
        eventKey,
        "Hook mutates core event identity fields",
        `Hook changed one or more of type/action/sessionKey for event '${eventKey}'. This can cause routing side effects in OpenClaw hooks.`,
      );
    }

    if (
      normalizedSafe.messagesCount > MAX_OUTPUT_MESSAGES ||
      normalizedSafe.messagesCharCount > MAX_OUTPUT_CHARS
    ) {
      pushHookVulnerability(
        findings,
        `DAST-OUTPUT-${slug(`${hook.name}-${eventKey}`)}`,
        "medium",
        hook,
        eventKey,
        "Hook output exceeds safe bounds",
        `Hook generated ${normalizedSafe.messagesCount} messages and ${normalizedSafe.messagesCharCount} chars for baseline input. Limits: ${MAX_OUTPUT_MESSAGES} messages / ${MAX_OUTPUT_CHARS} chars.`,
      );
    }

    const maliciousFailures = [];
    const maliciousTimeouts = [];

    for (const payload of MALICIOUS_PAYLOADS) {
      const event = buildEvent(eventKey, payload, targetPath);
      const context = {
        ...safeContext,
        payloadLength: payload.length,
      };

      const result = await invokeHookHarness(hook, event, context, invocationTimeoutMs);

      if (result.timedOut) {
        maliciousTimeouts.push(`len=${payload.length}`);
        continue;
      }

      if (result.parseError) {
        maliciousFailures.push(`parse-error(${result.parseError})`);
        continue;
      }

      const normalized = normalizeHarnessPayload(result.parsed);
      if (!normalized.ok) {
        maliciousFailures.push(normalized.error || "execution-error");
      }

      if (
        normalized.messagesCount > MAX_OUTPUT_MESSAGES ||
        normalized.messagesCharCount > MAX_OUTPUT_CHARS
      ) {
        pushHookVulnerability(
          findings,
          `DAST-OUTPUT-${slug(`${hook.name}-${eventKey}`)}-${payload.length}`,
          "medium",
          hook,
          eventKey,
          "Hook output amplification under malicious input",
          `Hook generated ${normalized.messagesCount} messages and ${normalized.messagesCharCount} chars for payload length ${payload.length}.`,
        );
      }
    }

    if (maliciousTimeouts.length > 0) {
      pushHookVulnerability(
        findings,
        `DAST-MALICIOUS-TIMEOUT-${slug(`${hook.name}-${eventKey}`)}`,
        "high",
        hook,
        eventKey,
        "Hook times out on malicious input",
        `Hook exceeded ${invocationTimeoutMs}ms for malicious payloads (${maliciousTimeouts.slice(0, 3).join(", ")}${maliciousTimeouts.length > 3 ? `, +${maliciousTimeouts.length - 3} more` : ""}).`,
      );
    }

    if (maliciousFailures.length > 0) {
      pushHookVulnerability(
        findings,
        `DAST-MALICIOUS-CRASH-${slug(`${hook.name}-${eventKey}`)}`,
        "high",
        hook,
        eventKey,
        "Hook crashes on malicious input",
        `Hook raised unhandled errors for malicious payloads. Sample errors: ${maliciousFailures.slice(0, 3).join(" | ")}${maliciousFailures.length > 3 ? ` (+${maliciousFailures.length - 3} more)` : ""}`,
      );
    }
  }

  return findings;
}

/**
 * Execute DAST hook tests.
 *
 * @param {string} targetPath
 * @param {number} timeout
 * @returns {Promise<Vulnerability[]>}
 */
export async function runDastTests(targetPath, timeout) {
  const hooks = await discoverHooks(targetPath);
  if (hooks.length === 0) {
    process.stderr.write(`[dast] No OpenClaw hooks discovered under ${targetPath}; skipping DAST harness execution\n`);
    return [];
  }

  const vulnerabilities = [];

  for (const hook of hooks) {
    const hookFindings = await evaluateHook(hook, targetPath, timeout);
    vulnerabilities.push(...hookFindings);
  }

  return vulnerabilities;
}

/**
 * CLI entry point.
 */
async function main() {
  try {
    const args = parseArgs(process.argv.slice(2));

    const targetExists = await fileExists(args.target);
    if (!targetExists) {
      throw new Error(`Target path does not exist: ${args.target}`);
    }

    const vulnerabilities = await runDastTests(args.target, args.timeout);
    const report = generateReport(vulnerabilities, args.target);

    if (args.format === "text") {
      process.stdout.write(formatReportText(report));
      process.stdout.write("\n");
    } else {
      process.stdout.write(formatReportJson(report));
      process.stdout.write("\n");
    }

    const hasCriticalOrHigh = report.summary.critical > 0 || report.summary.high > 0;
    process.exit(hasCriticalOrHigh ? 1 : 0);
  } catch (error) {
    process.stderr.write("DAST runner failed:\n");
    if (error instanceof Error) {
      process.stderr.write(`${error.message}\n`);
    } else {
      process.stderr.write(`${String(error)}\n`);
    }
    process.exit(1);
  }
}

export { MALICIOUS_PAYLOADS };

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
