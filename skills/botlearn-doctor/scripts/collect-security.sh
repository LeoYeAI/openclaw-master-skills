#!/bin/bash
# collect-security.sh — Security risk assessment: credential exposure, file permissions,
# dependency vulnerabilities, network exposure, VCS sensitive info
# Output: JSON to stdout | Timeout: 10s | Compatible: macOS (darwin) + Linux
# PRIVACY: All credential values are REDACTED — only type + location are reported
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"
OPENCLAW_LOG_DIR="${OPENCLAW_LOG_DIR:-$OPENCLAW_HOME/logs}"
OPENCLAW_GATEWAY="${OPENCLAW_GATEWAY:-http://localhost:18789}"

node <<'NODESCRIPT'
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const HOME = process.env.OPENCLAW_HOME || (process.env.HOME + "/.openclaw");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || (HOME + "/openclaw.json");
const LOG_DIR = process.env.OPENCLAW_LOG_DIR || (HOME + "/logs");
const GATEWAY = process.env.OPENCLAW_GATEWAY || "http://localhost:18789";

const result = {
  timestamp: new Date().toISOString(),
  credential_exposure: { findings: [], scanned_files: 0, issues_found: 0 },
  file_permissions: { findings: [], checked_files: 0, issues_found: 0 },
  dependency_vulnerabilities: { outdated_count: 0, cve_check_available: false, findings: [] },
  network_exposure: { findings: [] },
  vcs_sensitive: { findings: [] }
};

// --- 1. Credential Exposure Scan ---
const SECRET_PATTERNS = [
  { name: "api_key", regex: /(?:api[_-]?key|apikey)\s*[:=]\s*["\x27]?([A-Za-z0-9_\-]{16,})/gi },
  { name: "secret", regex: /(?:secret|client_secret)\s*[:=]\s*["\x27]?([A-Za-z0-9_\-]{16,})/gi },
  { name: "token", regex: /(?:token|access_token|bearer)\s*[:=]\s*["\x27]?([A-Za-z0-9_\-\.]{16,})/gi },
  { name: "password", regex: /(?:password|passwd|pwd)\s*[:=]\s*["\x27]?([^\s"'\x27]{4,})/gi },
  { name: "private_key", regex: /-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----/gi }
];

function scanFileForSecrets(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf8");
    const findings = [];
    for (const pat of SECRET_PATTERNS) {
      pat.regex.lastIndex = 0;
      let match;
      while ((match = pat.regex.exec(content)) !== null) {
        const lineNum = content.substring(0, match.index).split("\n").length;
        findings.push({
          type: pat.name,
          file: filePath.replace(process.env.HOME, "~"),
          line: lineNum,
          value: "***REDACTED***"
        });
      }
    }
    return findings;
  } catch { return []; }
}

// Scan config directory
function scanDir(dir, extensions) {
  if (!fs.existsSync(dir)) return [];
  let files = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      const fp = path.join(dir, e.name);
      if (e.isDirectory() && !e.name.startsWith(".")) {
        files = files.concat(scanDir(fp, extensions));
      } else if (e.isFile()) {
        const ext = path.extname(e.name).toLowerCase();
        if (extensions.includes(ext) || extensions.includes("*")) {
          files.push(fp);
        }
      }
    }
  } catch {}
  return files;
}

const scanTargets = [
  ...scanDir(HOME + "/config", [".json", ".yaml", ".yml", ".toml", ".env", "*"]),
  ...scanDir(LOG_DIR, [".log", ".txt"]).slice(0, 5) // limit log scan
];

// Also scan .env files in OPENCLAW_HOME
const envFile = HOME + "/.env";
if (fs.existsSync(envFile)) scanTargets.push(envFile);

result.credential_exposure.scanned_files = scanTargets.length;
for (const f of scanTargets) {
  const findings = scanFileForSecrets(f);
  result.credential_exposure.findings.push(...findings);
}
result.credential_exposure.issues_found = result.credential_exposure.findings.length;

// --- 2. File Permissions ---
const sensitiveFiles = [
  CONFIG,
  HOME + "/config",
  HOME + "/.env"
];
// Add any .key/.pem files
try {
  const configDir = HOME + "/config";
  if (fs.existsSync(configDir)) {
    fs.readdirSync(configDir).forEach(f => {
      if (f.endsWith(".key") || f.endsWith(".pem") || f.endsWith(".p12")) {
        sensitiveFiles.push(path.join(configDir, f));
      }
    });
  }
} catch {}

for (const fp of sensitiveFiles) {
  if (!fs.existsSync(fp)) continue;
  result.file_permissions.checked_files++;
  try {
    const stat = fs.statSync(fp);
    const mode = (stat.mode & 0o777).toString(8);
    const worldReadable = (stat.mode & 0o004) !== 0;
    const groupWritable = (stat.mode & 0o020) !== 0;
    if (worldReadable || groupWritable) {
      result.file_permissions.findings.push({
        file: fp.replace(process.env.HOME, "~"),
        mode: mode,
        issue: worldReadable ? "world-readable" : "group-writable",
        recommended: "0600"
      });
    }
  } catch {}
}
result.file_permissions.issues_found = result.file_permissions.findings.length;

// --- 3. Dependency Vulnerabilities ---
try {
  const outdatedOutput = execSync("clawhub list --outdated --json 2>/dev/null || echo \"[]\"", { encoding: "utf8", timeout: 5000 });
  const outdated = JSON.parse(outdatedOutput);
  result.dependency_vulnerabilities.outdated_count = Array.isArray(outdated) ? outdated.length : 0;
  if (Array.isArray(outdated)) {
    for (const dep of outdated.slice(0, 10)) {
      result.dependency_vulnerabilities.findings.push({
        type: "outdated",
        package: dep.name || dep,
        current: dep.current || "unknown",
        latest: dep.latest || "unknown"
      });
    }
  }
} catch {}

try {
  execSync("npm audit --json 2>/dev/null", { timeout: 5000 });
  result.dependency_vulnerabilities.cve_check_available = true;
} catch (e) {
  // npm audit returns non-zero if vulnerabilities found
  if (e.stdout) {
    result.dependency_vulnerabilities.cve_check_available = true;
    try {
      const audit = JSON.parse(e.stdout);
      if (audit.metadata && audit.metadata.vulnerabilities) {
        const v = audit.metadata.vulnerabilities;
        result.dependency_vulnerabilities.findings.push({
          type: "npm_audit",
          critical: v.critical || 0,
          high: v.high || 0,
          moderate: v.moderate || 0,
          low: v.low || 0
        });
      }
    } catch {}
  }
}

// --- 4. Network Exposure ---
// Check Gateway bind mode and auth configuration
try {
  if (fs.existsSync(CONFIG)) {
    const raw = fs.readFileSync(CONFIG, "utf8");
    const clean = raw.replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
    const config = JSON.parse(clean);

    // Bind mode check (loopback | lan | tailnet)
    const bind = config.gateway?.bind || "loopback";
    if (bind === "lan") {
      result.network_exposure.findings.push({
        type: "bind_address",
        value: bind,
        severity: "warning",
        msg: "Gateway bound to LAN — accessible from local network"
      });
    } else if (bind === "tailnet") {
      result.network_exposure.findings.push({
        type: "bind_address",
        value: bind,
        severity: "info",
        msg: "Gateway bound to tailnet — accessible via Tailscale network"
      });
    }

    // Auth check
    const authType = config.gateway?.auth?.type;
    if (!authType || authType === "none") {
      if (bind !== "loopback") {
        result.network_exposure.findings.push({
          type: "no_auth",
          severity: "high",
          msg: "Gateway has no authentication but is accessible beyond localhost"
        });
      } else {
        result.network_exposure.findings.push({
          type: "no_auth",
          severity: "info",
          msg: "No authentication configured (acceptable for loopback)"
        });
      }
    }

    // Control UI exposure
    if (config.gateway?.controlUI !== false && bind !== "loopback") {
      result.network_exposure.findings.push({
        type: "control_ui_exposed",
        severity: "warning",
        msg: "Control UI (/openclaw) accessible on non-loopback bind"
      });
    }
  }
} catch {}

// --- 5. VCS Sensitive Info ---
// Check .gitignore exists and covers sensitive patterns
try {
  const gitRoot = execSync("git rev-parse --show-toplevel 2>/dev/null", { encoding: "utf8", timeout: 3000 }).trim();
  const gitignorePath = path.join(gitRoot, ".gitignore");
  if (fs.existsSync(gitignorePath)) {
    const gitignore = fs.readFileSync(gitignorePath, "utf8");
    const shouldIgnore = [".env", "*.key", "*.pem", "config/*.secret", "credentials"];
    for (const pattern of shouldIgnore) {
      if (!gitignore.includes(pattern)) {
        result.vcs_sensitive.findings.push({
          type: "missing_gitignore",
          pattern: pattern,
          msg: "Pattern not in .gitignore: " + pattern
        });
      }
    }
  } else {
    result.vcs_sensitive.findings.push({
      type: "no_gitignore",
      severity: "warning",
      msg: "No .gitignore file found"
    });
  }

  // Check for tracked secrets
  try {
    const tracked = execSync("git ls-files " + HOME + " 2>/dev/null", { encoding: "utf8", timeout: 3000 });
    const secretFiles = tracked.split("\n").filter(f =>
      f.endsWith(".key") || f.endsWith(".pem") || f.endsWith(".env") ||
      f.includes("credentials") || f.includes("secret")
    );
    for (const sf of secretFiles) {
      if (sf.trim()) {
        result.vcs_sensitive.findings.push({
          type: "tracked_secret",
          file: sf.replace(process.env.HOME, "~"),
          severity: "critical",
          msg: "Potentially sensitive file tracked in git"
        });
      }
    }
  } catch {}
} catch {
  // Not in a git repo — skip VCS checks
  result.vcs_sensitive.findings.push({
    type: "no_git_repo",
    severity: "info",
    msg: "Not in a git repository, VCS checks skipped"
  });
}

console.log(JSON.stringify(result, null, 2));
NODESCRIPT
