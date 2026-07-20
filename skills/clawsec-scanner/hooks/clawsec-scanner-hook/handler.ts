import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { execCommand, safeJsonParse } from "../../lib/utils.mjs";
import { formatReportText } from "../../lib/report.mjs";
import type { HookEvent, HookContext, ScanReport } from "../../lib/types.ts";

const DEFAULT_SCAN_INTERVAL_SECONDS = 86400; // 24 hours
const DEFAULT_SCANNER_TIMEOUT = 300; // 5 minutes
const DEFAULT_MIN_SEVERITY = "medium";
let unsignedModeWarningShown = false;

interface ScannerState {
  last_hook_scan: string | null;
  last_full_scan: string | null;
  known_vulnerabilities: string[];
}

function parsePositiveInteger(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }
  return parsed;
}

function toEventName(event: HookEvent): string {
  const eventType = String(event.type ?? "").trim();
  const action = String(event.action ?? "").trim();
  if (!eventType || !action) return "";
  return `${eventType}:${action}`;
}

function shouldHandleEvent(event: HookEvent): boolean {
  const eventName = toEventName(event);
  return eventName === "agent:bootstrap" || eventName === "command:new";
}

function epochMs(isoTimestamp: string | null): number {
  if (!isoTimestamp) return 0;
  const parsed = Date.parse(isoTimestamp);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function scannedRecently(lastScan: string | null, minIntervalSeconds: number): boolean {
  const sinceMs = Date.now() - epochMs(lastScan);
  return sinceMs >= 0 && sinceMs < minIntervalSeconds * 1000;
}

function configuredPath(
  explicit: string | undefined,
  fallback: string,
  label: string,
): string {
  if (!explicit) return fallback;

  const resolved = path.resolve(explicit);
  try {
    // Basic validation - check if path is a string
    if (typeof resolved === "string" && resolved.length > 0) {
      return resolved;
    }
  } catch (error) {
    console.warn(
      `[clawsec-scanner-hook] invalid ${label} path "${explicit}", using default "${fallback}": ${String(error)}`,
    );
  }

  return fallback;
}

async function loadState(stateFile: string): Promise<ScannerState> {
  try {
    const content = await fs.readFile(stateFile, "utf8");
    const parsed = safeJsonParse(content, { fallback: {}, label: "scanner state" });
    const parsedState =
      parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : {};

    return {
      last_hook_scan:
        typeof parsedState.last_hook_scan === "string" ? parsedState.last_hook_scan : null,
      last_full_scan:
        typeof parsedState.last_full_scan === "string" ? parsedState.last_full_scan : null,
      known_vulnerabilities: Array.isArray(parsedState.known_vulnerabilities)
        ? parsedState.known_vulnerabilities.filter((v): v is string => typeof v === "string")
        : [],
    };
  } catch {
    // State file doesn't exist yet - return empty state
    return {
      last_hook_scan: null,
      last_full_scan: null,
      known_vulnerabilities: [],
    };
  }
}

async function persistState(stateFile: string, state: ScannerState): Promise<void> {
  try {
    const dir = path.dirname(stateFile);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(stateFile, JSON.stringify(state, null, 2), "utf8");
  } catch (error) {
    console.warn(`[clawsec-scanner-hook] failed to persist state: ${String(error)}`);
  }
}

async function runScanner(
  targetPath: string,
  options: {
    skipDeps: boolean;
    skipSast: boolean;
    skipDast: boolean;
    skipCve: boolean;
    timeout: number;
  },
): Promise<ScanReport | null> {
  try {
    const scriptPath = path.join(path.dirname(new URL(import.meta.url).pathname), "../../scripts/runner.sh");

    const args = ["--target", targetPath, "--format", "json"];

    if (options.skipDeps) args.push("--skip-deps");
    if (options.skipSast) args.push("--skip-sast");
    if (options.skipDast) args.push("--skip-dast");
    if (options.skipCve) args.push("--skip-cve");

    const { stdout, stderr } = await execCommand("bash", [scriptPath, ...args]);

    if (stderr && !stdout) {
      console.warn(`[clawsec-scanner-hook] scanner warning: ${stderr}`);
    }

    const report = safeJsonParse(stdout, { fallback: null, label: "scanner report" });

    if (!report || typeof report !== "object") {
      console.warn("[clawsec-scanner-hook] scanner produced invalid report");
      return null;
    }

    return report as ScanReport;
  } catch (error) {
    console.warn(`[clawsec-scanner-hook] scanner execution failed: ${String(error)}`);
    return null;
  }
}

function shouldReportSeverity(severity: string, minSeverity: string): boolean {
  const severityOrder = ["info", "low", "medium", "high", "critical"];
  const minIndex = severityOrder.indexOf(minSeverity.toLowerCase());
  const vulnIndex = severityOrder.indexOf(severity.toLowerCase());

  if (minIndex === -1 || vulnIndex === -1) return true;

  return vulnIndex >= minIndex;
}

function deduplicateVulnerabilities(
  report: ScanReport,
  knownVulnIds: string[],
): ScanReport {
  const knownSet = new Set(knownVulnIds);
  const newVulnerabilities = report.vulnerabilities.filter(
    (vuln) => !knownSet.has(vuln.id),
  );

  // Recalculate summary for new vulnerabilities
  const summary = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
  };

  for (const vuln of newVulnerabilities) {
    const severity = vuln.severity;
    if (severity in summary) {
      summary[severity]++;
    }
  }

  return {
    ...report,
    vulnerabilities: newVulnerabilities,
    summary,
  };
}

function buildAlertMessage(report: ScanReport, format: string): string {
  if (format === "json") {
    return JSON.stringify(report, null, 2);
  }

  return formatReportText(report);
}

const handler = async (event: HookEvent, _context: HookContext): Promise<void> => {
  // DAST harness mode executes hook handlers directly; skip recursive scanner runs.
  if (process.env.CLAWSEC_DAST_HARNESS === "1" || _context?.dastMode === true) {
    return;
  }

  if (!shouldHandleEvent(event)) return;

  const installRoot = configuredPath(
    process.env.CLAWSEC_INSTALL_ROOT || process.env.INSTALL_ROOT,
    path.join(os.homedir(), ".openclaw", "skills"),
    "CLAWSEC_INSTALL_ROOT",
  );

  const targetPath = configuredPath(
    process.env.CLAWSEC_SCANNER_TARGET,
    installRoot,
    "CLAWSEC_SCANNER_TARGET",
  );

  const stateFile = configuredPath(
    process.env.CLAWSEC_SCANNER_STATE_FILE,
    path.join(os.homedir(), ".openclaw", "clawsec-scanner-state.json"),
    "CLAWSEC_SCANNER_STATE_FILE",
  );

  const scanIntervalSeconds = parsePositiveInteger(
    process.env.CLAWSEC_SCANNER_INTERVAL,
    DEFAULT_SCAN_INTERVAL_SECONDS,
  );

  const scanTimeout = parsePositiveInteger(
    process.env.CLAWSEC_SCANNER_TIMEOUT,
    DEFAULT_SCANNER_TIMEOUT,
  );

  const minSeverity = process.env.CLAWSEC_SCANNER_MIN_SEVERITY || DEFAULT_MIN_SEVERITY;
  const outputFormat = process.env.CLAWSEC_SCANNER_FORMAT || "text";
  const allowUnsigned = process.env.CLAWSEC_ALLOW_UNSIGNED_FEED === "1";

  const skipDeps = process.env.CLAWSEC_SKIP_DEPENDENCY_SCAN === "1";
  const skipSast = process.env.CLAWSEC_SKIP_SAST === "1";
  const skipDast = process.env.CLAWSEC_SKIP_DAST === "1";
  const skipCve = process.env.CLAWSEC_SKIP_CVE_LOOKUP === "1";

  if (allowUnsigned && !unsignedModeWarningShown) {
    unsignedModeWarningShown = true;
    console.warn(
      "[clawsec-scanner-hook] CLAWSEC_ALLOW_UNSIGNED_FEED=1 is enabled. " +
        "This bypass is for development only.",
    );
  }

  const forceScan = toEventName(event) === "command:new";
  const state = await loadState(stateFile);

  if (!forceScan && scannedRecently(state.last_hook_scan, scanIntervalSeconds)) {
    return;
  }

  const report = await runScanner(targetPath, {
    skipDeps,
    skipSast,
    skipDast,
    skipCve,
    timeout: scanTimeout,
  });

  const nowIso = new Date().toISOString();
  state.last_hook_scan = nowIso;
  state.last_full_scan = nowIso;

  if (!report) {
    await persistState(stateFile, state);
    return;
  }

  // Filter by minimum severity
  const filteredVulns = report.vulnerabilities.filter((vuln) =>
    shouldReportSeverity(vuln.severity, minSeverity),
  );

  // Deduplicate against known vulnerabilities
  const dedupedReport = deduplicateVulnerabilities(
    { ...report, vulnerabilities: filteredVulns },
    state.known_vulnerabilities,
  );

  // Update known vulnerabilities list
  const allVulnIds = report.vulnerabilities.map((v) => v.id).filter((id) => id.trim() !== "");
  state.known_vulnerabilities = Array.from(new Set([...state.known_vulnerabilities, ...allVulnIds]));

  await persistState(stateFile, state);

  // Write optional output file
  const outputFile = process.env.CLAWSEC_SCANNER_OUTPUT_FILE;
  if (outputFile) {
    try {
      await fs.writeFile(outputFile, JSON.stringify(report, null, 2), "utf8");
    } catch (error) {
      console.warn(`[clawsec-scanner-hook] failed to write output file: ${String(error)}`);
    }
  }

  // Post findings to conversation if any new vulnerabilities
  if (dedupedReport.vulnerabilities.length > 0) {
    const alertMessage = buildAlertMessage(dedupedReport, outputFormat);

    event.messages?.push({
      role: "system",
      content: `🔍 ClawSec Scanner detected ${dedupedReport.vulnerabilities.length} new vulnerabilities:\n\n${alertMessage}`,
    });
  }
};

export default handler;
