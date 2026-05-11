#!/bin/bash
# collect-workspace-audit.sh — Workspace audit: critical md files, storage usage,
# config cross-validation, environment variable audit
# Output: JSON to stdout | Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"

node <<'NODESCRIPT'
const fs = require("fs");
const path = require("path");

const HOME = process.env.OPENCLAW_HOME || (process.env.HOME + "/.openclaw");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || (HOME + "/openclaw.json");

const result = {
  timestamp: new Date().toISOString(),
  critical_files: { present: [], missing: [], total_checked: 0 },
  storage: { directories: {}, total_size_mb: 0 },
  config_cross_validation: { issues: [] },
  env_audit: { defined: [], missing: [], conflicts: [] },
  summary: { issues_found: 0, severity_breakdown: { critical: 0, warning: 0, info: 0 } }
};

// --- 1. Critical File Presence ---
const criticalFiles = [
  { path: CONFIG, name: "openclaw.json", required: true },
  { path: HOME + "/config", name: "config/", required: false, isDir: true },
  { path: HOME + "/logs", name: "logs/", required: true, isDir: true },
  { path: HOME + "/skills", name: "skills/", required: true, isDir: true },
  { path: HOME + "/data", name: "data/", required: true, isDir: true },
  { path: HOME + "/reports", name: "reports/", required: false, isDir: true },
  { path: HOME + "/plugins", name: "plugins/", required: false, isDir: true },
  { path: HOME + "/workspace", name: "workspace/", required: false, isDir: true }
];

for (const cf of criticalFiles) {
  result.critical_files.total_checked++;
  const exists = fs.existsSync(cf.path);
  if (exists) {
    result.critical_files.present.push({ name: cf.name, path: cf.path.replace(process.env.HOME, "~"), required: cf.required });
  } else {
    result.critical_files.missing.push({ name: cf.name, path: cf.path.replace(process.env.HOME, "~"), required: cf.required });
    if (cf.required) {
      result.summary.severity_breakdown.warning++;
    }
  }
}

// --- 2. Storage Usage ---
function getDirSize(dirPath) {
  let totalSize = 0;
  let fileCount = 0;
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      const fp = path.join(dirPath, entry.name);
      try {
        if (entry.isFile()) {
          totalSize += fs.statSync(fp).size;
          fileCount++;
        } else if (entry.isDirectory() && !entry.name.startsWith(".")) {
          const sub = getDirSize(fp);
          totalSize += sub.size;
          fileCount += sub.files;
        }
      } catch {}
    }
  } catch {}
  return { size: totalSize, files: fileCount };
}

const storageDirs = ["config", "skills", "logs", "data", "plugins", "memory", "workspace", "reports"];
let totalBytes = 0;

for (const dir of storageDirs) {
  const dirPath = path.join(HOME, dir);
  if (fs.existsSync(dirPath)) {
    const info = getDirSize(dirPath);
    result.storage.directories[dir] = {
      size_mb: Math.round(info.size / 1024 / 1024 * 100) / 100,
      file_count: info.files,
      exists: true
    };
    totalBytes += info.size;
  } else {
    result.storage.directories[dir] = { size_mb: 0, file_count: 0, exists: false };
  }
}
result.storage.total_size_mb = Math.round(totalBytes / 1024 / 1024 * 100) / 100;

// Flag large directories
for (const [dir, info] of Object.entries(result.storage.directories)) {
  if (info.size_mb > 500) {
    result.config_cross_validation.issues.push({
      type: "large_directory",
      severity: "warning",
      directory: dir,
      size_mb: info.size_mb,
      msg: dir + "/ is " + info.size_mb + " MB — consider cleanup"
    });
  }
}

// --- 3. Config Cross-Validation ---
try {
  if (fs.existsSync(CONFIG)) {
    const raw = fs.readFileSync(CONFIG, "utf8");
    const clean = raw.replace(/\/\/.*$/gm, "").replace(/\/\*[\s\S]*?\*\//g, "");
    const config = JSON.parse(clean);

    // Check agent workspace dir exists
    const workspace = config.agents?.defaults?.workspace;
    if (workspace && !fs.existsSync(workspace.replace("$HOME", process.env.HOME))) {
      result.config_cross_validation.issues.push({
        type: "config_path_mismatch",
        severity: "warning",
        msg: "Configured agent workspace does not exist: " + workspace
      });
    }

    // Check gateway bind mode (security)
    const bind = config.gateway?.bind || "loopback";
    if (bind === "lan" || bind === "tailnet") {
      result.config_cross_validation.issues.push({
        type: "gateway_exposed",
        severity: "info",
        msg: "Gateway bind set to '" + bind + "' — accessible beyond localhost"
      });
    }

    // Check heartbeat config
    if (config.agents?.heartbeat) {
      if (!config.agents.heartbeat.autoRecovery) {
        result.config_cross_validation.issues.push({
          type: "no_auto_recovery",
          severity: "warning",
          msg: "Agent heartbeat autoRecovery is disabled"
        });
      }
    }

    // maxConcurrent vs available skills
    const skillsDir = HOME + "/skills/@botlearn";
    let skillCount = 0;
    try {
      skillCount = fs.readdirSync(skillsDir).filter(d => !d.startsWith(".")).length;
    } catch {}
    const maxConc = config.agents?.defaults?.maxConcurrent || 3;
    if (skillCount > 0 && maxConc > skillCount * 3) {
      result.config_cross_validation.issues.push({
        type: "over_provisioned_concurrency",
        severity: "info",
        msg: "maxConcurrent (" + maxConc + ") seems high for " + skillCount + " installed skills"
      });
    }

    // Timeout sanity — agents.defaults.timeoutSeconds
    const timeout = config.agents?.defaults?.timeoutSeconds || 600;
    if (timeout > 3600) {
      result.config_cross_validation.issues.push({
        type: "excessive_timeout",
        severity: "warning",
        msg: "Agent timeout " + timeout + "s (>1h) is very high"
      });
    }
  }
} catch {}

// --- 4. Environment Variable Audit ---
const envVars = [
  { name: "OPENCLAW_HOME", required: false, default: "~/.openclaw" },
  { name: "OPENCLAW_CONFIG_PATH", required: false, default: "$OPENCLAW_HOME/openclaw.json" },
  { name: "OPENCLAW_STATE_DIR", required: false, default: "$OPENCLAW_HOME/state" },
  { name: "OPENCLAW_LOG_DIR", required: false, default: "$OPENCLAW_HOME/logs" },
  { name: "OPENCLAW_SKILLS_DIR", required: false, default: "$OPENCLAW_HOME/skills" }
];

for (const ev of envVars) {
  const value = process.env[ev.name];
  if (value) {
    result.env_audit.defined.push({ name: ev.name, set: true, value_redacted: value.replace(process.env.HOME, "~") });
    // Check if defined path exists
    if (!fs.existsSync(value)) {
      result.env_audit.conflicts.push({
        name: ev.name,
        severity: "warning",
        msg: ev.name + " points to non-existent path: " + value.replace(process.env.HOME, "~")
      });
    }
  } else {
    result.env_audit.missing.push({ name: ev.name, default: ev.default, required: ev.required });
  }
}

// Check for conflicting env vars
if (process.env.OPENCLAW_HOME && process.env.OPENCLAW_CONFIG_PATH) {
  const expectedPrefix = process.env.OPENCLAW_HOME;
  if (!process.env.OPENCLAW_CONFIG_PATH.startsWith(expectedPrefix)) {
    result.env_audit.conflicts.push({
      name: "OPENCLAW_CONFIG_PATH",
      severity: "warning",
      msg: "OPENCLAW_CONFIG_PATH is outside OPENCLAW_HOME directory"
    });
  }
}

// --- Aggregate issues ---
result.summary.issues_found =
  result.critical_files.missing.filter(f => f.required).length +
  result.config_cross_validation.issues.length +
  result.env_audit.conflicts.length;

for (const issue of result.config_cross_validation.issues) {
  result.summary.severity_breakdown[issue.severity] = (result.summary.severity_breakdown[issue.severity] || 0) + 1;
}
for (const conflict of result.env_audit.conflicts) {
  result.summary.severity_breakdown[conflict.severity] = (result.summary.severity_breakdown[conflict.severity] || 0) + 1;
}

console.log(JSON.stringify(result, null, 2));
NODESCRIPT
