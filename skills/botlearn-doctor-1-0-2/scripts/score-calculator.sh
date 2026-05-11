#!/bin/bash
# score-calculator.sh — 10-dimension traffic-light health analysis, output JSON
# v4.0: Replaces weighted percentage scoring with ✅ pass / ⚠️ warning / ❌ error model
# Input: Reads JSON from stdin with 8 data sources
# Output: analysis.json with 10 dimensions, each independently judged
# Timeout: 5s | Compatible: macOS (darwin) + Linux
set -euo pipefail

# Input format:
# { "env": {...}, "config": {...}, "logs": {...}, "skills": {...},
#   "health": {...}, "precheck": {...}, "channels": {...}, "tools": {...} }
#
# Usage: cat combined-data.json | ./score-calculator.sh

node -e '
const data = JSON.parse(require("fs").readFileSync("/dev/stdin", "utf8"));

const env = data.env || {};
const config = data.config || {};
const logs = data.logs || {};
const skills = data.skills || {};
const health = data.health || {};
const precheck = data.precheck || {};
const channels = data.channels || {};
const tools = data.tools || {};

// --- Dimension 1: 基础平台 (Platform) ---
function judgePlatform(env) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  // Node.js version
  if (env.node_version && env.node_version !== "NOT_FOUND") {
    const major = parseInt(env.node_version.replace("v", ""));
    if (major >= 20) { /* pass */ }
    else if (major >= 18) { hasWarning = true; issues.push({ msg: "Node.js " + env.node_version + " — v20+ recommended", severity: "warning" }); }
    else { hasError = true; issues.push({ msg: "Node.js " + env.node_version + " unsupported, v18+ required", severity: "error" }); }
  } else {
    hasError = true; issues.push({ msg: "Node.js not found", severity: "error" });
  }

  // Memory
  if (env.memory) {
    const pct = env.memory.available_mb / env.memory.total_mb;
    if (pct > 0.3) { /* pass */ }
    else if (pct > 0.15) { hasWarning = true; issues.push({ msg: "Memory available " + Math.round(pct * 100) + "% (recommend >30%)", severity: "warning" }); }
    else { hasError = true; issues.push({ msg: "Memory critically low: " + Math.round(pct * 100) + "%", severity: "error" }); }
  }

  // Disk
  if (env.disk) {
    const pct = env.disk.available_gb / env.disk.total_gb;
    if (pct > 0.2) { /* pass */ }
    else if (pct > 0.1) { hasWarning = true; issues.push({ msg: "Disk space low: " + Math.round(pct * 100) + "% available", severity: "warning" }); }
    else { hasError = true; issues.push({ msg: "Disk critically low: " + Math.round(pct * 100) + "%", severity: "error" }); }
  }

  // CPU
  if (env.cpu && env.cpu.cores > 0) {
    const loadPerCore = env.cpu.load_avg_1m / env.cpu.cores;
    if (loadPerCore < 0.7) { /* pass */ }
    else if (loadPerCore < 0.9) { hasWarning = true; issues.push({ msg: "CPU load elevated: " + env.cpu.load_avg_1m + " on " + env.cpu.cores + " cores", severity: "warning" }); }
    else { hasError = true; issues.push({ msg: "CPU load critical: " + env.cpu.load_avg_1m + " on " + env.cpu.cores + " cores", severity: "error" }); }
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "Platform meets recommended specs"
            : status === "warning" ? "Platform meets minimum specs but has concerns"
            : "Platform below minimum requirements";
  return { id: 1, label: "基础平台", label_en: "Platform", status, message: msg, issues };
}

// --- Dimension 2: OpenClaw 版本 (Version) ---
function judgeVersion(env) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  // OpenClaw CLI
  const oc = env.openclaw_version || "NOT_FOUND";
  const ch = env.clawhub_version || "NOT_FOUND";
  if (oc === "NOT_FOUND" && ch === "NOT_FOUND") {
    hasError = true; issues.push({ msg: "Neither openclaw nor clawhub CLI found", severity: "error" });
  } else {
    // Check if versions seem outdated (heuristic: if version string available)
    if (oc !== "NOT_FOUND" && oc !== "unknown") {
      issues.push({ msg: "openclaw CLI: " + oc, severity: "info" });
    }
    if (ch !== "NOT_FOUND" && ch !== "unknown") {
      issues.push({ msg: "clawhub CLI: " + ch, severity: "info" });
    }
  }

  // Node.js version (also relevant here)
  if (env.node_version && env.node_version !== "NOT_FOUND") {
    const major = parseInt(env.node_version.replace("v", ""));
    if (major >= 20) { /* latest LTS */ }
    else if (major >= 18) { hasWarning = true; issues.push({ msg: "Node.js " + env.node_version + " — not latest LTS", severity: "warning" }); }
    else { hasError = true; issues.push({ msg: "Node.js " + env.node_version + " too old", severity: "error" }); }
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "All versions up to date"
            : status === "warning" ? "Versions usable but not latest"
            : "Critical version issues";
  return { id: 2, label: "OpenClaw 版本", label_en: "Version", status, message: msg, issues };
}

// --- Dimension 3: 配置正确性 (Config) ---
function judgeConfig(config) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  if (!config.config_exists) {
    hasError = true; issues.push({ msg: "Config file not found", severity: "error", fix_ref: "PB-002" });
    return { id: 3, label: "配置正确性", label_en: "Config", status: "error", message: "Config file missing", issues };
  }

  if (!config.config_valid_json) {
    hasError = true; issues.push({ msg: "Config file has invalid JSON", severity: "error", fix_ref: "PB-002" });
    return { id: 3, label: "配置正确性", label_en: "Config", status: "error", message: "Config parse failure", issues };
  }

  // Check required sections
  const sections = config.sections || {};
  const missing = ["gateway", "agents", "messages", "session", "tools"].filter(s => !sections[s]);
  if (missing.length > 0) {
    if (missing.includes("gateway") || missing.includes("agents")) {
      hasError = true; issues.push({ msg: "Critical config sections missing: " + missing.join(", "), severity: "error" });
    } else {
      hasWarning = true; issues.push({ msg: "Optional config sections missing: " + missing.join(", "), severity: "warning" });
    }
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "Config valid and complete"
            : status === "warning" ? "Config has minor omissions"
            : "Config has critical issues";
  return { id: 3, label: "配置正确性", label_en: "Config", status, message: msg, issues };
}

// --- Dimension 4: 日志告警 (Logs) ---
function judgeLogs(logs) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  if (!logs.log_dir_exists) {
    hasWarning = true; issues.push({ msg: "Log directory not found", severity: "warning" });
    return { id: 4, label: "日志告警", label_en: "Logs", status: "warning", message: "No logs to analyze", issues };
  }

  // Error rate
  const rate = logs.main_log?.error_rate_pct || 0;
  if (rate > 10) { hasError = true; issues.push({ msg: "Error rate " + rate + "% (>10%)", severity: "error", fix_ref: "PB-009" }); }
  else if (rate > 1) { hasWarning = true; issues.push({ msg: "Error rate " + rate + "% (1-10%)", severity: "warning" }); }

  // Critical events (OOM, segfault)
  const critEvents = logs.critical_events || [];
  const oomEvents = critEvents.filter(e => e.type === "oom" || e.type === "segfault");
  if (oomEvents.length > 0) {
    hasError = true; issues.push({ msg: oomEvents.length + " OOM/segfault event(s) detected", severity: "error", fix_ref: "PB-007" });
  }

  // Error spikes
  const spikes = logs.error_spikes || [];
  if (spikes.length > 0) {
    hasWarning = true; issues.push({ msg: spikes.length + " error spike(s) detected", severity: "warning", fix_ref: "PB-009" });
  }

  // Log growth
  if (logs.growth_rate?.excessive) {
    hasWarning = true; issues.push({ msg: "Total logs exceed 500MB — rotation needed", severity: "warning", fix_ref: "PB-005" });
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "Logs clean, error rate <1%"
            : status === "warning" ? "Some log concerns detected"
            : "Critical log issues found";
  return { id: 4, label: "日志告警", label_en: "Logs", status, message: msg, issues };
}

// --- Dimension 5: 预检 (Precheck) ---
function judgePrecheck(precheck) {
  const issues = [];

  if (!precheck.cli_available || !precheck.precheck_ran) {
    return { id: 5, label: "预检", label_en: "Precheck", status: "warning", message: "Precheck could not run (CLI unavailable)", issues: [{ msg: precheck.message || "CLI not available", severity: "warning" }] };
  }

  const summary = precheck.summary || {};
  if (summary.error > 0) {
    issues.push({ msg: summary.error + " precheck error(s)", severity: "error" });
    for (const c of (precheck.checks || []).filter(c => c.status === "error" || c.status === "fail")) {
      issues.push({ msg: "FAIL: " + (c.name || c.raw || "unknown check"), severity: "error" });
    }
    return { id: 5, label: "预检", label_en: "Precheck", status: "error", message: summary.error + " precheck error(s)", issues };
  }
  if (summary.warn > 0) {
    issues.push({ msg: summary.warn + " precheck warning(s)", severity: "warning" });
    return { id: 5, label: "预检", label_en: "Precheck", status: "warning", message: summary.warn + " precheck warning(s)", issues };
  }

  return { id: 5, label: "预检", label_en: "Precheck", status: "pass", message: "All precheck items passed", issues };
}

// --- Dimension 6: Skills 安装 ---
function judgeSkills(skills) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  if (!skills.skills_dir_exists) {
    hasError = true; issues.push({ msg: "Skills directory not found", severity: "error" });
    return { id: 6, label: "Skills 安装", label_en: "Skills", status: "error", message: "Skills directory missing", issues };
  }

  const count = skills.installed_count || 0;
  if (count >= 3) { /* pass */ }
  else if (count >= 1) { hasWarning = true; issues.push({ msg: "Only " + count + " skill(s) installed (recommend ≥3)", severity: "warning" }); }
  else { hasWarning = true; issues.push({ msg: "No skills installed", severity: "warning" }); }

  // Broken dependencies
  const broken = Array.isArray(skills.broken_dependencies) ? skills.broken_dependencies.length : 0;
  if (broken > 0) {
    hasError = true; issues.push({ msg: broken + " skill(s) have broken dependencies", severity: "error", fix_ref: "PB-004" });
  }

  // Outdated
  const outdated = Array.isArray(skills.outdated) ? skills.outdated.length : 0;
  if (outdated > 0) {
    hasWarning = true; issues.push({ msg: outdated + " skill(s) outdated", severity: "warning" });
  }

  // Integrity
  if (Array.isArray(skills.skills)) {
    const incomplete = skills.skills.filter(s => !s.has_skill_md || !s.has_knowledge || !s.has_strategies);
    if (incomplete.length > 0) {
      hasWarning = true; issues.push({ msg: incomplete.length + " skill(s) missing required files", severity: "warning" });
    }
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? count + " skills installed, all healthy"
            : status === "warning" ? "Skills have minor issues"
            : "Skills have critical issues";
  return { id: 6, label: "Skills 安装", label_en: "Skills", status, message: msg, issues };
}

// --- Dimension 7: Channels 安装 ---
function judgeChannels(channels) {
  const issues = [];

  if (!channels.channel_config_exists) {
    return { id: 7, label: "Channels 安装", label_en: "Channels", status: "warning", message: "Channel config not found", issues: [{ msg: "doctor-channels.json not found — run setup", severity: "warning" }] };
  }

  if (!channels.channel_config_valid) {
    return { id: 7, label: "Channels 安装", label_en: "Channels", status: "error", message: "Channel config invalid", issues: (channels.issues || []).map(i => ({ msg: i.issue || i.msg, severity: "error" })) };
  }

  const enabled = channels.enabled_count || 0;
  if (enabled > 0) {
    // Check for misconfigured channels
    const configIssues = (channels.issues || []).filter(i => i.issue);
    if (configIssues.length > 0) {
      for (const ci of configIssues) {
        issues.push({ msg: ci.issue, severity: "warning" });
      }
      return { id: 7, label: "Channels 安装", label_en: "Channels", status: "warning", message: enabled + " channel(s) enabled, " + configIssues.length + " issue(s)", issues };
    }
    return { id: 7, label: "Channels 安装", label_en: "Channels", status: "pass", message: enabled + " channel(s) enabled and configured", issues };
  }

  issues.push({ msg: "All channels disabled", severity: "warning" });
  return { id: 7, label: "Channels 安装", label_en: "Channels", status: "warning", message: "All channels disabled", issues };
}

// --- Dimension 8: Agent 配置 ---
function judgeAgent(config) {
  const issues = [];
  let hasError = false;
  let hasWarning = false;

  if (!config.config_exists || !config.config_valid_json) {
    return { id: 8, label: "Agent 配置", label_en: "Agent", status: "warning", message: "Cannot check agent config (config unavailable)", issues: [{ msg: "Config not available for agent parameter check", severity: "warning" }] };
  }

  const v = config.values || {};

  // maxConcurrent
  const mc = v.max_concurrent || 0;
  if (mc >= 1 && mc <= 10) { /* recommended */ }
  else if (mc > 0 && mc <= 20) { hasWarning = true; issues.push({ msg: "maxConcurrent=" + mc + " outside recommended range (1-10)", severity: "warning" }); }
  else if (mc > 20) { hasError = true; issues.push({ msg: "maxConcurrent=" + mc + " exceeds safe range (max 20)", severity: "error" }); }
  else { hasWarning = true; issues.push({ msg: "maxConcurrent not configured", severity: "warning" }); }

  // timeoutSeconds
  const ts = v.timeout_seconds || 0;
  if (ts >= 30 && ts <= 1800) { /* recommended */ }
  else if (ts > 0 && ts <= 3600) { hasWarning = true; issues.push({ msg: "timeoutSeconds=" + ts + "s outside recommended range (30-1800s)", severity: "warning" }); }
  else if (ts > 3600) { hasError = true; issues.push({ msg: "timeoutSeconds=" + ts + "s exceeds safe range", severity: "error" }); }

  // heartbeat
  const hb = v.heartbeat_interval || 0;
  if (hb > 0 && (hb < 5 || hb > 120)) {
    hasWarning = true; issues.push({ msg: "heartbeat interval " + hb + "min outside recommended range (5-120)", severity: "warning" });
  }

  const status = hasError ? "error" : hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "Agent parameters in recommended range"
            : status === "warning" ? "Agent parameters acceptable but not optimal"
            : "Agent parameters exceed safe limits";
  return { id: 8, label: "Agent 配置", label_en: "Agent", status, message: msg, issues };
}

// --- Dimension 9: Gateway 健康 ---
function judgeGateway(health) {
  const issues = [];

  if (!health.gateway_reachable) {
    issues.push({ msg: "Gateway unreachable at " + (health.gateway_url || "localhost:18789"), severity: "error", fix_ref: "PB-003" });
    return { id: 9, label: "Gateway 健康", label_en: "Gateway", status: "error", message: "Gateway unreachable", issues };
  }

  let hasWarning = false;

  if (!health.gateway_operational) {
    issues.push({ msg: "/openclaw endpoint not responsive", severity: "error", fix_ref: "PB-003" });
    return { id: 9, label: "Gateway 健康", label_en: "Gateway", status: "error", message: "Gateway not operational", issues };
  }

  // Check individual endpoints
  if (Array.isArray(health.endpoints)) {
    const unhealthy = health.endpoints.filter(e => e.status !== "healthy" && e.status !== "redirect" && e.status !== "auth_required");
    if (unhealthy.length > 0) {
      hasWarning = true;
      for (const ep of unhealthy) {
        issues.push({ msg: ep.endpoint + " returned " + ep.status_code + " (" + ep.status + ")", severity: "warning" });
      }
    }

    // Latency check
    const avgLatency = health.endpoints.reduce((sum, e) => sum + (e.latency_ms || 0), 0) / health.endpoints.length;
    if (avgLatency > 500) {
      hasWarning = true; issues.push({ msg: "High average latency: " + Math.round(avgLatency) + "ms", severity: "warning" });
    }
  }

  const status = hasWarning ? "warning" : "pass";
  const msg = status === "pass" ? "All Gateway endpoints healthy"
            : "Some Gateway endpoints have issues";
  return { id: 9, label: "Gateway 健康", label_en: "Gateway", status, message: msg, issues };
}

// --- Dimension 10: 内置工具 (Tools) ---
function judgeTools(tools) {
  const issues = [];

  const coreMissing = tools.summary?.core_missing || [];
  if (coreMissing.length > 0) {
    for (const t of coreMissing) {
      issues.push({ msg: "Core tool missing: " + t, severity: "error" });
    }
    return { id: 10, label: "内置工具", label_en: "Tools", status: "error", message: coreMissing.length + " core tool(s) missing", issues };
  }

  // Check optional tools
  const toolIssues = (tools.issues || []).filter(i => i.severity === "warning");
  if (toolIssues.length > 0) {
    for (const ti of toolIssues) {
      issues.push({ msg: ti.msg, severity: "warning" });
    }
    return { id: 10, label: "内置工具", label_en: "Tools", status: "warning", message: toolIssues.length + " optional tool(s) missing", issues };
  }

  return { id: 10, label: "内置工具", label_en: "Tools", status: "pass", message: "All core tools available", issues };
}

// === Run all 10 dimensions ===
const dimensions = [
  judgePlatform(env),
  judgeVersion(env),
  judgeConfig(config),
  judgeLogs(logs),
  judgePrecheck(precheck),
  judgeSkills(skills),
  judgeChannels(channels),
  judgeAgent(config),
  judgeGateway(health),
  judgeTools(tools)
];

// === Overall status ===
const hasError = dimensions.some(d => d.status === "error");
const hasWarning = dimensions.some(d => d.status === "warning");
const overallStatus = hasError ? "error" : hasWarning ? "warning" : "pass";

// === Summary counts ===
const summary = {
  pass_count: dimensions.filter(d => d.status === "pass").length,
  warning_count: dimensions.filter(d => d.status === "warning").length,
  error_count: dimensions.filter(d => d.status === "error").length,
  total: 10
};

// === Build output ===
const output = {
  timestamp: new Date().toISOString(),
  version: "4.0.0",
  model: "traffic-light",
  overall_status: overallStatus,
  summary,
  dimensions,
  // Collect all issues across dimensions for quick reference
  all_issues: dimensions.flatMap(d => (d.issues || []).map(i => ({
    dimension: d.label_en,
    dimension_id: d.id,
    ...i
  }))).filter(i => i.severity !== "info")
};

console.log(JSON.stringify(output, null, 2));
'
