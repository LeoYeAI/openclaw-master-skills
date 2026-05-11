#!/bin/bash
# collect-logs.sh — Collect log statistics, error patterns, and anomaly detection, output JSON
# Merged: v3.0 collect-logs.sh + collect-log-anomalies.sh anomaly detection logic
# Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
LOG_DIR="${OPENCLAW_LOG_DIR:-$OPENCLAW_HOME/logs}"

node <<'NODESCRIPT'
const fs = require("fs");
const path = require("path");

const LOG_DIR = process.env.OPENCLAW_LOG_DIR || ((process.env.OPENCLAW_HOME || process.env.HOME + "/.openclaw") + "/logs");

const result = {
  timestamp: new Date().toISOString(),
  log_dir: LOG_DIR,
  log_dir_exists: false,
  main_log: {
    exists: false,
    size_kb: 0,
    total_lines: 0,
    error_count: 0,
    warn_count: 0,
    error_rate_pct: 0
  },
  error_log: { exists: false, size_kb: 0 },
  recent_errors: [],
  error_patterns: {},
  log_rotation_enabled: false,
  // Anomaly detection (merged from collect-log-anomalies.sh)
  anomalies: [],
  error_spikes: [],
  stack_traces: [],
  critical_events: [],
  time_clusters: [],
  growth_rate: null,
  anomaly_summary: { total: 0, critical: 0, warning: 0, info: 0 }
};

if (!fs.existsSync(LOG_DIR)) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(0);
}
result.log_dir_exists = true;

// Find log files
const logFiles = [];
try {
  fs.readdirSync(LOG_DIR).forEach(f => {
    const fp = path.join(LOG_DIR, f);
    if (fs.statSync(fp).isFile() && (f.endsWith(".log") || f.endsWith(".txt"))) {
      logFiles.push(fp);
    }
  });
} catch {}

// Check log rotation
result.log_rotation_enabled = logFiles.some(f => /openclaw\.log\.\d/.test(path.basename(f)));

const mainLog = path.join(LOG_DIR, "openclaw.log");
let lines = [];

if (fs.existsSync(mainLog)) {
  result.main_log.exists = true;
  const stat = fs.statSync(mainLog);
  result.main_log.size_kb = Math.round(stat.size / 1024);

  const content = fs.readFileSync(mainLog, "utf8");
  const allLines = content.split("\n");
  result.main_log.total_lines = allLines.length;

  // Limit to last 10000 lines for performance
  lines = allLines.length > 10000 ? allLines.slice(-10000) : allLines;

  // Count errors and warnings
  const errorPattern = /\b(error|ERROR|Error|FATAL|fatal|CRIT|crit)\b/;
  const warnPattern = /\b(warn|WARN|Warning)\b/;

  for (const line of allLines) {
    if (errorPattern.test(line)) result.main_log.error_count++;
    if (warnPattern.test(line)) result.main_log.warn_count++;
  }

  // Error rate
  if (result.main_log.total_lines > 0) {
    result.main_log.error_rate_pct = Math.round((result.main_log.error_count / result.main_log.total_lines) * 10000) / 100;
  }

  // Recent errors (last 5)
  const recentErrorLines = lines.filter(l => errorPattern.test(l)).slice(-5);
  result.recent_errors = recentErrorLines.map(l => {
    try { return JSON.parse(l).message || l.substring(0, 200); }
    catch { return l.substring(0, 200); }
  });

  // Error pattern frequency
  const patternCounts = {};
  const codePattern = /"code":"([A-Z_]+)"/g;
  for (const line of lines.slice(-1000)) {
    let m;
    while ((m = codePattern.exec(line)) !== null) {
      patternCounts[m[1]] = (patternCounts[m[1]] || 0) + 1;
    }
  }
  // Top 5 patterns
  const sortedPatterns = Object.entries(patternCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  result.error_patterns = Object.fromEntries(sortedPatterns);

  // === Anomaly Detection (merged from collect-log-anomalies.sh) ===

  // 1. Error Spikes Detection — group errors by hour, detect >3x average
  const errorsByHour = {};
  const timestampPattern = /(\d{4}-\d{2}-\d{2}[T ]\d{2})/;

  for (const line of lines) {
    if (!errorPattern.test(line)) continue;
    const tsMatch = line.match(timestampPattern);
    if (tsMatch) {
      const hourKey = tsMatch[1];
      errorsByHour[hourKey] = (errorsByHour[hourKey] || 0) + 1;
    }
  }

  const hourCounts = Object.values(errorsByHour);
  if (hourCounts.length > 2) {
    const avg = hourCounts.reduce((s, v) => s + v, 0) / hourCounts.length;
    const threshold = Math.max(avg * 3, 10);
    for (const [hour, count] of Object.entries(errorsByHour)) {
      if (count > threshold) {
        result.error_spikes.push({
          hour, count, average: Math.round(avg),
          multiplier: Math.round(count / avg * 10) / 10,
          severity: count > threshold * 2 ? "critical" : "warning"
        });
      }
    }
  }

  // 2. Stack Traces
  const stackTracePattern = /^\s+at\s+/;
  let inStack = false;
  let currentStack = [];
  let stackTrigger = "";

  for (let i = 0; i < lines.length; i++) {
    if (stackTracePattern.test(lines[i])) {
      if (!inStack) { stackTrigger = lines[i - 1] || ""; inStack = true; }
      currentStack.push(lines[i].trim());
    } else if (inStack && currentStack.length > 0) {
      result.stack_traces.push({
        trigger: stackTrigger.substring(0, 200),
        depth: currentStack.length,
        top_frame: currentStack[0],
        line_number: i - currentStack.length
      });
      inStack = false; currentStack = [];
    }
  }
  result.stack_traces = result.stack_traces.slice(-10);

  // 3. Critical Events (OOM, Segfault, Unhandled Promise)
  const criticalPatterns = [
    { name: "oom", regex: /\b(out\s*of\s*memory|OOM|heap\s+out\s+of\s+memory|ENOMEM|JavaScript\s+heap)\b/i },
    { name: "segfault", regex: /\b(segmentation\s+fault|SIGSEGV|segfault)\b/i },
    { name: "unhandled_promise", regex: /\b(UnhandledPromiseRejection|unhandled\s+promise)\b/i },
    { name: "uncaught_exception", regex: /\b(uncaughtException|UNCAUGHT_EXCEPTION)\b/i },
    { name: "kill_signal", regex: /\b(SIGKILL|SIGTERM|killed\s+by\s+signal)\b/i }
  ];

  for (let i = 0; i < lines.length; i++) {
    for (const pat of criticalPatterns) {
      if (pat.regex.test(lines[i])) {
        result.critical_events.push({
          type: pat.name, line_number: i + 1,
          excerpt: lines[i].substring(0, 200), severity: "critical"
        });
      }
    }
  }
  result.critical_events = result.critical_events.slice(-20);

  // 4. Time Clustering — bursts of errors within 1-minute windows
  const errorTimestamps = [];
  const isoPattern = /(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})/;
  for (const line of lines) {
    if (!errorPattern.test(line)) continue;
    const m = line.match(isoPattern);
    if (m) errorTimestamps.push(m[1]);
  }
  const byMinute = {};
  for (const ts of errorTimestamps) { byMinute[ts] = (byMinute[ts] || 0) + 1; }
  for (const [minute, count] of Object.entries(byMinute)) {
    if (count >= 5) {
      result.time_clusters.push({
        window: minute, error_count: count,
        severity: count >= 20 ? "critical" : count >= 10 ? "warning" : "info"
      });
    }
  }
  result.time_clusters = result.time_clusters.slice(-10);

  // 5. Log Growth Rate
  try {
    const ageHours = (Date.now() - stat.mtimeMs) / 3600000;
    const sizeKB = result.main_log.size_kb;
    let totalSizeKB = sizeKB;
    for (const rl of logFiles.filter(f => f !== mainLog)) {
      totalSizeKB += Math.round(fs.statSync(rl).size / 1024);
    }
    result.growth_rate = {
      main_log_size_kb: sizeKB,
      total_logs_size_kb: totalSizeKB,
      log_file_count: logFiles.length,
      lines_analyzed: lines.length,
      estimated_daily_growth_kb: ageHours > 0 ? Math.round((sizeKB / Math.max(ageHours, 1)) * 24) : null,
      excessive: totalSizeKB > 512000
    };
  } catch {}

  // Build anomaly summary
  for (const spike of result.error_spikes) {
    result.anomalies.push({ type: "error_spike", severity: spike.severity, detail: spike.hour + ": " + spike.count + " errors" });
  }
  for (const evt of result.critical_events) {
    result.anomalies.push({ type: evt.type, severity: "critical", detail: evt.excerpt.substring(0, 100) });
  }
  for (const cluster of result.time_clusters) {
    result.anomalies.push({ type: "time_cluster", severity: cluster.severity, detail: cluster.window + ": " + cluster.error_count + " errors" });
  }
  if (result.growth_rate && result.growth_rate.excessive) {
    result.anomalies.push({ type: "log_growth", severity: "warning", detail: "Total logs exceed 500MB" });
  }
  if (result.stack_traces.length > 5) {
    result.anomalies.push({ type: "frequent_stack_traces", severity: "warning", detail: result.stack_traces.length + " stack traces found" });
  }

  result.anomaly_summary.total = result.anomalies.length;
  result.anomaly_summary.critical = result.anomalies.filter(a => a.severity === "critical").length;
  result.anomaly_summary.warning = result.anomalies.filter(a => a.severity === "warning").length;
  result.anomaly_summary.info = result.anomalies.filter(a => a.severity === "info").length;
}

// Error log
const errorLog = path.join(LOG_DIR, "error.log");
if (fs.existsSync(errorLog)) {
  result.error_log.exists = true;
  result.error_log.size_kb = Math.round(fs.statSync(errorLog).size / 1024);
}

console.log(JSON.stringify(result, null, 2));
NODESCRIPT
