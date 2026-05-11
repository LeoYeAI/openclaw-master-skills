#!/bin/bash
# collect-config.sh — Validate and analyze OpenClaw configuration, output JSON
# Primary check: openclaw config validate
# Content analysis: direct file parsing via Node.js
# Timeout: 15s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"

# ─── Step 1: Run openclaw config validate ────────────────────────────────────
# Success output format: "🦞 OpenClaw 2026.3.2 (85377a2) — The lobster in your shell. 🦞"
# Exit code 0 = valid, non-zero = invalid
validate_output=""
validate_exit=0
validate_ran=false

if command -v openclaw &>/dev/null; then
  validate_ran=true
  validate_output=$(openclaw config validate 2>&1) || validate_exit=$?
fi

# Parse version and commit from validation output
oc_version=$(echo "$validate_output" | grep -oE 'OpenClaw [0-9]+\.[0-9]+[^ ]*' | awk '{print $2}' | head -1)
oc_commit=$(echo "$validate_output"  | grep -oE '\([0-9a-f]{6,}\)' | tr -d '()' | head -1)
oc_version="${oc_version:-}"
oc_commit="${oc_commit:-}"

validate_success="false"
[[ "$validate_ran" == "true" && "$validate_exit" -eq 0 ]] && validate_success="true"

# Escape validate output for JSON
validate_output_escaped=$(echo "$validate_output" | head -5 | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' '|' | sed 's/|$//')

# ─── Step 2: Content analysis via Node.js ────────────────────────────────────
node_output=$(OPENCLAW_HOME="$OPENCLAW_HOME" OPENCLAW_CONFIG_PATH="$OPENCLAW_CONFIG_PATH" \
  node <<'NODESCRIPT'
const fs   = require("fs");
const path = require("path");

const HOME   = process.env.OPENCLAW_HOME   || (process.env.HOME + "/.openclaw");
const CONFIG = process.env.OPENCLAW_CONFIG_PATH || (HOME + "/openclaw.json");

const out = {
  config_exists:    false,
  config_file:      CONFIG.replace(process.env.HOME, "~"),
  json_valid:       false,
  sections_present: [],
  sections_missing: [],
  gateway:  null,
  agents:   null,
  tools:    null,
  messages: null,
  session:  null,
  extra_keys: [],
  consistency_issues: [],
  issues: []
};

if (!fs.existsSync(CONFIG)) {
  out.issues.push("Config file not found: " + out.config_file);
  console.log(JSON.stringify(out));
  process.exit(0);
}

out.config_exists = true;
let config = {};
try {
  const raw   = fs.readFileSync(CONFIG, "utf8");
  // Strip JSON5-style comments before parsing
  const clean = raw
    .replace(/\/\/[^\n]*/g, "")
    .replace(/\/\*[\s\S]*?\*\//g, "");
  config = JSON.parse(clean);
  out.json_valid = true;
} catch (e) {
  out.issues.push("JSON parse error: " + e.message);
  console.log(JSON.stringify(out));
  process.exit(0);
}

// ── Section presence ──────────────────────────────────────────────────────
const REQUIRED = ["gateway", "agents", "messages", "session", "tools"];
for (const s of REQUIRED) {
  if (config[s]) out.sections_present.push(s);
  else           out.sections_missing.push(s);
}

// Extra top-level keys (potential deprecated / unknown config)
const KNOWN = new Set([...REQUIRED, "version", "name", "description"]);
out.extra_keys = Object.keys(config).filter(k => !KNOWN.has(k));

// ── Gateway analysis ──────────────────────────────────────────────────────
if (config.gateway) {
  const gw = config.gateway;
  out.gateway = {
    port:        gw.port        || 18789,
    bind:        gw.bind        || "loopback",
    mode:        gw.mode        || "ws+http",
    reload:      gw.reload      || "hybrid",
    control_ui:  !!(gw.controlUI),
    auth: {
      type:       gw.auth?.type       || "none",
      configured: gw.auth?.type && gw.auth.type !== "none"
    },
    ssl: {
      enabled: !!(gw.ssl?.enabled),
      cert:    !!(gw.ssl?.cert)
    },
    allowed_origins: Array.isArray(gw.allowedOrigins) ? gw.allowedOrigins.length : 0
  };
}

// ── Agents analysis ───────────────────────────────────────────────────────
if (config.agents) {
  const ag = config.agents;
  const def = ag.defaults || {};
  out.agents = {
    max_concurrent:   def.maxConcurrent   || ag.maxConcurrent   || 3,
    timeout_seconds:  def.timeoutSeconds  || ag.timeoutSeconds  || 600,
    default_model:    def.model           || ag.defaultModel    || "unknown",
    heartbeat: {
      interval_minutes: ag.heartbeat?.intervalMinutes || 30,
      auto_recovery:    !!(ag.heartbeat?.autoRecovery),
      enabled:          ag.heartbeat?.enabled !== false
    },
    memory: {
      max_items:     ag.memory?.maxItems    || null,
      ttl_days:      ag.memory?.ttlDays     || null,
      auto_compact:  !!(ag.memory?.autoCompact)
    }
  };
}

// ── Tools analysis ────────────────────────────────────────────────────────
if (config.tools) {
  const tl = config.tools;
  const mcp = tl.mcp || {};
  out.tools = {
    profile:      tl.profile  || "default",
    enabled:      Array.isArray(tl.enabled)  ? tl.enabled  : [],
    disabled:     Array.isArray(tl.disabled) ? tl.disabled : [],
    mcp_servers:  Object.keys(mcp).length,
    mcp_list:     Object.keys(mcp)
  };
}

// ── Messages analysis ─────────────────────────────────────────────────────
if (config.messages) {
  const ms = config.messages;
  out.messages = {
    history_limit:   ms.historyLimit   || null,
    max_tokens:      ms.maxTokens      || null,
    retention_days:  ms.retentionDays  || null
  };
}

// ── Session analysis ──────────────────────────────────────────────────────
if (config.session) {
  const ss = config.session;
  out.session = {
    timeout_minutes: ss.timeoutMinutes || null,
    persist:         !!(ss.persist),
    auto_save:       !!(ss.autoSave)
  };
}

// ── Consistency checks (cross-field validation) ───────────────────────────
const gw = out.gateway;
const ag = out.agents;

if (gw) {
  // LAN/tailnet without auth
  if (gw.bind !== "loopback" && !gw.auth.configured) {
    out.consistency_issues.push({
      severity: "critical",
      field:    "gateway.bind + gateway.auth",
      message:  `Gateway bind="${gw.bind}" but auth.type="${gw.auth.type}" — unauthenticated exposure`
    });
  }
  // Control UI on non-loopback
  if (gw.control_ui && gw.bind !== "loopback") {
    out.consistency_issues.push({
      severity: "critical",
      field:    "gateway.controlUI + gateway.bind",
      message:  `controlUI=true with bind="${gw.bind}" exposes admin interface to network`
    });
  }
  // LAN without SSL
  if (gw.bind === "lan" && gw.auth.configured && !gw.ssl.enabled) {
    out.consistency_issues.push({
      severity: "warning",
      field:    "gateway.bind + gateway.ssl",
      message:  `Gateway on LAN with auth but no SSL — credentials transmitted in plaintext`
    });
  }
}

if (ag) {
  // Concurrent vs timeout mismatch
  if (ag.max_concurrent > 5 && ag.timeout_seconds > 1800) {
    out.consistency_issues.push({
      severity: "warning",
      field:    "agents.maxConcurrent + agents.timeoutSeconds",
      message:  `High concurrency (${ag.max_concurrent}) with long timeout (${ag.timeout_seconds}s) may exhaust resources`
    });
  }
  // Heartbeat configured but autoRecovery off
  if (ag.heartbeat.enabled && !ag.heartbeat.auto_recovery) {
    out.consistency_issues.push({
      severity: "warning",
      field:    "agents.heartbeat.autoRecovery",
      message:  "Heartbeat enabled but autoRecovery=false — agent won't restart after crash"
    });
  }
}

console.log(JSON.stringify(out, null, 2));
NODESCRIPT
)

# ─── Step 3: Merge and output final JSON ─────────────────────────────────────
node - <<MERGESCRIPT
const analysis = ${node_output};
const result = {
  timestamp: new Date().toISOString(),
  cli_validation: {
    ran:     ${validate_ran},
    success: ${validate_success},
    exit_code: ${validate_exit},
    openclaw_version: "${oc_version}",
    openclaw_commit:  "${oc_commit}",
    output_preview:   "${validate_output_escaped}"
  },
  ...analysis
};
console.log(JSON.stringify(result, null, 2));
MERGESCRIPT
