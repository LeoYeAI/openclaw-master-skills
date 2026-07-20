import { spawn } from "node:child_process";

/**
 * @param {unknown} value
 * @returns {value is Record<string, unknown>}
 */
export function isObject(value) {
  return typeof value === "object" && value !== null;
}

/**
 * Execute a command as a subprocess and return its output.
 *
 * NOTE: npm audit exits non-zero when vulnerabilities are found.
 * Check stderr for actual errors vs. normal vulnerability reports.
 *
 * @param {string} cmd - Command to execute
 * @param {string[]} args - Command arguments
 * @param {{env?: Record<string, string>, cwd?: string}} [options] - Execution options
 * @returns {Promise<{code: number, stdout: string, stderr: string}>}
 */
export function execCommand(cmd, args, options = {}) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, ...options.env },
      cwd: options.cwd,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (d) => {
      stdout += d;
    });
    proc.stderr.on("data", (d) => {
      stderr += d;
    });

    proc.on("close", (code) => {
      // npm audit and other security tools exit non-zero when vulnerabilities found
      // Check stderr for actual errors (ERR! pattern) vs. normal findings
      if (code !== 0 && stderr.includes("ERR!")) {
        reject(new Error(stderr));
      } else {
        resolve({ code, stdout, stderr });
      }
    });

    proc.on("error", (error) => {
      reject(error);
    });
  });
}

/**
 * Safely parse JSON string with error handling.
 *
 * @param {string} jsonString - JSON string to parse
 * @param {{fallback?: unknown, label?: string}} [options] - Parse options
 * @returns {unknown}
 */
export function safeJsonParse(jsonString, { fallback = null, label = "JSON" } = {}) {
  const raw = String(jsonString ?? "").trim();
  if (!raw) return fallback;

  try {
    return JSON.parse(raw);
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`Failed to parse ${label}: ${error.message}`);
    }
    return fallback;
  }
}

/**
 * Normalize severity levels from different security tools to standard levels.
 *
 * @param {string} severity - Severity string from security tool
 * @returns {'critical' | 'high' | 'medium' | 'low' | 'info'}
 */
export function normalizeSeverity(severity) {
  const normalized = String(severity ?? "")
    .trim()
    .toLowerCase();

  if (normalized.includes("critical")) return "critical";
  if (normalized.includes("high")) return "high";
  if (normalized.includes("moderate") || normalized.includes("medium")) return "medium";
  if (normalized.includes("low")) return "low";

  return "info";
}

/**
 * @param {string[]} values
 * @returns {string[]}
 */
export function uniqueStrings(values) {
  return Array.from(new Set(values));
}

/**
 * Generate a simple UUID v4.
 *
 * @returns {string}
 */
export function generateUuid() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get current ISO 8601 timestamp.
 *
 * @returns {string}
 */
export function getTimestamp() {
  return new Date().toISOString();
}

/**
 * Check if a command exists in PATH.
 *
 * @param {string} command - Command name to check
 * @returns {Promise<boolean>}
 */
export async function commandExists(command) {
  try {
    const { code } = await execCommand("which", [command]);
    return code === 0;
  } catch {
    return false;
  }
}
