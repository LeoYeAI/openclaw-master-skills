#!/bin/bash
# collect-log-anomalies.sh — Log anomaly detection: error spikes, stack traces,
# OOM/segfault, unhandled promises, time clustering, log growth rate
# Output: JSON to stdout | Timeout: 10s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_LOG_DIR="${OPENCLAW_LOG_DIR:-$OPENCLAW_HOME/logs}"

node <<'NODESCRIPT'
const fs = require("fs");
const path = require("path");

const LOG_DIR = process.env.OPENCLAW_LOG_DIR || ((process.env.OPENCLAW_HOME || process.env.HOME + "/.openclaw") + "/logs");

const result = {
  timestamp: new Date().toISOString(),
  log_dir_exists: false,
  anomalies: [],
  error_spikes: [],
  stack_traces: [],
  critical_events: [],
  time_clusters: [],
  growth_rate: null,
  summary: { total_anomalies: 0, critical: 0, warning: 0, info: 0 }
};

if (!fs.existsSync(LOG_DIR)) {
  result.log_dir_exists = false;
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

if (logFiles.length === 0) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(0);
}

// Read main log (limit to last 10000 lines for performance)
const mainLog = path.join(LOG_DIR, "openclaw.log");
let lines = [];
if (fs.existsSync(mainLog)) {
  const content = fs.readFileSync(mainLog, "utf8");
  lines = content.split("\n");
  if (lines.length > 10000) lines = lines.slice(-10000);
}

// --- 1. Error Spikes Detection ---
// Group errors by hour, detect spikes (>3x average)
const errorsByHour = {};
const errorPattern = /\b(error|ERROR|Error|FATAL|fatal|CRIT|crit)\b/;
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
  const threshold = Math.max(avg * 3, 10); // at least 10 errors to count as spike
  for (const [hour, count] of Object.entries(errorsByHour)) {
    if (count > threshold) {
      result.error_spikes.push({
        hour: hour,
        count: count,
        average: Math.round(avg),
        multiplier: Math.round(count / avg * 10) / 10,
        severity: count > threshold * 2 ? "critical" : "warning"
      });
    }
  }
}

// --- 2. Stack Traces ---
const stackTracePattern = /^\s+at\s+/;
let inStack = false;
let currentStack = [];
let stackTrigger = "";

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (stackTracePattern.test(line)) {
    if (!inStack) {
      stackTrigger = lines[i - 1] || "";
      inStack = true;
    }
    currentStack.push(line.trim());
  } else {
    if (inStack && currentStack.length > 0) {
      result.stack_traces.push({
        trigger: stackTrigger.substring(0, 200),
        depth: currentStack.length,
        top_frame: currentStack[0],
        line_number: i - currentStack.length
      });
      inStack = false;
      currentStack = [];
    }
  }
}
// Limit to last 10 stack traces
result.stack_traces = result.stack_traces.slice(-10);

// --- 3. Critical Events (OOM, Segfault, Unhandled Promise) ---
const criticalPatterns = [
  { name: "oom", regex: /\b(out\s*of\s*memory|OOM|heap\s+out\s+of\s+memory|ENOMEM|JavaScript\s+heap)\b/i },
  { name: "segfault", regex: /\b(segmentation\s+fault|SIGSEGV|segfault)\b/i },
  { name: "unhandled_promise", regex: /\b(UnhandledPromiseRejection|unhandled\s+promise|PromiseRejectionHandledWarning)\b/i },
  { name: "uncaught_exception", regex: /\b(uncaughtException|UNCAUGHT_EXCEPTION)\b/i },
  { name: "kill_signal", regex: /\b(SIGKILL|SIGTERM|killed\s+by\s+signal)\b/i }
];

for (let i = 0; i < lines.length; i++) {
  for (const pat of criticalPatterns) {
    if (pat.regex.test(lines[i])) {
      result.critical_events.push({
        type: pat.name,
        line_number: i + 1,
        excerpt: lines[i].substring(0, 200),
        severity: "critical"
      });
    }
  }
}
// Limit to last 20 events
result.critical_events = result.critical_events.slice(-20);

// --- 4. Time Clustering ---
// Detect bursts of errors within 1-minute windows
const errorTimestamps = [];
const isoPattern = /(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})/;

for (const line of lines) {
  if (!errorPattern.test(line)) continue;
  const m = line.match(isoPattern);
  if (m) errorTimestamps.push(m[1]);
}

// Group by minute
const byMinute = {};
for (const ts of errorTimestamps) {
  byMinute[ts] = (byMinute[ts] || 0) + 1;
}

// Find clusters (>5 errors in one minute)
for (const [minute, count] of Object.entries(byMinute)) {
  if (count >= 5) {
    result.time_clusters.push({
      window: minute,
      error_count: count,
      severity: count >= 20 ? "critical" : count >= 10 ? "warning" : "info"
    });
  }
}
result.time_clusters = result.time_clusters.slice(-10);

// --- 5. Log Growth Rate ---
try {
  const stat = fs.statSync(mainLog);
  const ageHours = (Date.now() - stat.mtimeMs) / 3600000;
  const sizeKB = Math.round(stat.size / 1024);

  // Check if rotated logs exist
  const rotatedLogs = logFiles.filter(f => f !== mainLog);
  let totalSizeKB = sizeKB;
  for (const rl of rotatedLogs) {
    totalSizeKB += Math.round(fs.statSync(rl).size / 1024);
  }

  result.growth_rate = {
    main_log_size_kb: sizeKB,
    total_logs_size_kb: totalSizeKB,
    log_file_count: logFiles.length,
    lines_analyzed: lines.length,
    estimated_daily_growth_kb: ageHours > 0 ? Math.round((sizeKB / Math.max(ageHours, 1)) * 24) : null,
    excessive: totalSizeKB > 512000 // >500MB total
  };
} catch {}

// --- Build anomaly summary ---
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

result.summary.total_anomalies = result.anomalies.length;
result.summary.critical = result.anomalies.filter(a => a.severity === "critical").length;
result.summary.warning = result.anomalies.filter(a => a.severity === "warning").length;
result.summary.info = result.anomalies.filter(a => a.severity === "info").length;

console.log(JSON.stringify(result, null, 2));
NODESCRIPT
