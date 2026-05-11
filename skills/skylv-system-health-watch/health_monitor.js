/**
 * health_monitor.js — AI Agent Self-Health Monitoring Engine
 * 
 * Monitors agent health: memory, API calls, errors, performance.
 * Calculates health score and suggests optimizations.
 * 
 * Usage: node health_monitor.js <command> [args...]
 * Commands:
 *   status                Show current health status
 *   check                 Run full health check
 *   api-stats             Show API call statistics
 *   memory                Show memory usage
 *   errors [limit]        Show recent errors
 *   alert [threshold]     Set alert thresholds
 *   report [format]       Generate health report (text/json)
 *   watch [interval]      Continuous monitoring mode
 *   optimize              Get optimization suggestions
 */

const os = require('os');
const fs = require('fs');
const path = require('path');

// ── Config ──────────────────────────────────────────────────────────────────
const HISTORY_FILE = '.health-history.json';
const ALERTS_FILE = '.health-alerts.json';
const MAX_HISTORY = 1000;
const DEFAULT_THRESHOLDS = {
  memoryWarning: 0.75,      // 75% of heap used
  memoryCritical: 0.90,     // 90% of heap used
  errorRateWarning: 0.10,   // 10% error rate
  errorRateCritical: 0.25,  // 25% error rate
  apiLatencyWarning: 2000,  // 2 seconds
  apiLatencyCritical: 5000, // 5 seconds
};

// ── History Storage ──────────────────────────────────────────────────────────
function loadHistory() {
  if (!fs.existsSync(HISTORY_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8')); }
  catch { return []; }
}

function saveHistory(history) {
  const trimmed = history.slice(-MAX_HISTORY);
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(trimmed, null, 2));
}

function loadAlerts() {
  if (!fs.existsSync(ALERTS_FILE)) return { thresholds: DEFAULT_THRESHOLDS, events: [] };
  try { return JSON.parse(fs.readFileSync(ALERTS_FILE, 'utf8')); }
  catch { return { thresholds: DEFAULT_THRESHOLDS, events: [] }; }
}

function saveAlerts(alerts) {
  fs.writeFileSync(ALERTS_FILE, JSON.stringify(alerts, null, 2));
}

// ── Memory Metrics ───────────────────────────────────────────────────────────
function getMemoryMetrics() {
  const mem = process.memoryUsage();
  const system = {
    total: os.totalmem(),
    free: os.freemem(),
    used: os.totalmem() - os.freemem(),
  };
  
  return {
    process: {
      heapUsed: mem.heapUsed,
      heapTotal: mem.heapTotal,
      heapPercent: mem.heapUsed / mem.heapTotal,
      external: mem.external,
      rss: mem.rss,
      arrayBuffers: mem.arrayBuffers || 0,
    },
    system: {
      total: system.total,
      free: system.free,
      used: system.used,
      usedPercent: system.used / system.total,
    },
    uptime: process.uptime(),
    pid: process.pid,
  };
}

// ── API Statistics ───────────────────────────────────────────────────────────
let apiCalls = { total: 0, success: 0, failed: 0, totalLatency: 0, endpoints: {} };

// Hook for tracking API calls (can be imported by other modules)
function trackApiCall(endpoint, success, latency) {
  apiCalls.total++;
  if (success) apiCalls.success++;
  else apiCalls.failed++;
  apiCalls.totalLatency += latency;
  
  if (!apiCalls.endpoints[endpoint]) {
    apiCalls.endpoints[endpoint] = { calls: 0, success: 0, failed: 0, totalLatency: 0 };
  }
  apiCalls.endpoints[endpoint].calls++;
  if (success) apiCalls.endpoints[endpoint].success++;
  else apiCalls.endpoints[endpoint].failed++;
  apiCalls.endpoints[endpoint].totalLatency += latency;
}

function getApiStats() {
  return {
    ...apiCalls,
    successRate: apiCalls.total > 0 ? apiCalls.success / apiCalls.total : 1,
    avgLatency: apiCalls.total > 0 ? apiCalls.totalLatency / apiCalls.total : 0,
  };
}

// ── Error Tracking ───────────────────────────────────────────────────────────
let errors = [];

function trackError(error, context = {}) {
  const entry = {
    timestamp: new Date().toISOString(),
    message: error.message || String(error),
    stack: error.stack?.slice(0, 500),
    context,
  };
  errors.push(entry);
  if (errors.length > 100) errors.shift();
}

function getErrors(limit = 10) {
  return errors.slice(-limit);
}

function getErrorRate() {
  const recent = errors.slice(-10);
  const history = loadHistory();
  const recentChecks = history.slice(-10);
  
  // Error rate based on recent API calls
  if (apiCalls.total > 0) {
    return apiCalls.failed / apiCalls.total;
  }
  return 0;
}

// ── Health Score Calculation ────────────────────────────────────────────────
function calculateHealthScore(metrics, apiStats, thresholds) {
  let score = 100;
  const issues = [];
  
  // Memory health (max -30 points)
  const heapPercent = metrics.process.heapPercent;
  if (heapPercent > thresholds.memoryCritical) {
    score -= 30;
    issues.push({ severity: 'critical', area: 'memory', message: `Heap usage critical: ${(heapPercent * 100).toFixed(1)}%` });
  } else if (heapPercent > thresholds.memoryWarning) {
    score -= 15;
    issues.push({ severity: 'warning', area: 'memory', message: `Heap usage high: ${(heapPercent * 100).toFixed(1)}%` });
  }
  
  // API health (max -25 points)
  const errorRate = apiStats.total > 0 ? apiStats.failed / apiStats.total : 0;
  if (errorRate > thresholds.errorRateCritical) {
    score -= 25;
    issues.push({ severity: 'critical', area: 'api', message: `Error rate critical: ${(errorRate * 100).toFixed(1)}%` });
  } else if (errorRate > thresholds.errorRateWarning) {
    score -= 10;
    issues.push({ severity: 'warning', area: 'api', message: `Error rate elevated: ${(errorRate * 100).toFixed(1)}%` });
  }
  
  // Latency health (max -20 points)
  const avgLatency = apiStats.avgLatency;
  if (avgLatency > thresholds.apiLatencyCritical) {
    score -= 20;
    issues.push({ severity: 'critical', area: 'latency', message: `API latency critical: ${avgLatency.toFixed(0)}ms` });
  } else if (avgLatency > thresholds.apiLatencyWarning) {
    score -= 10;
    issues.push({ severity: 'warning', area: 'latency', message: `API latency high: ${avgLatency.toFixed(0)}ms` });
  }
  
  // System memory (max -15 points)
  if (metrics.system.usedPercent > 0.90) {
    score -= 15;
    issues.push({ severity: 'critical', area: 'system', message: `System memory critical: ${(metrics.system.usedPercent * 100).toFixed(1)}%` });
  } else if (metrics.system.usedPercent > 0.80) {
    score -= 8;
    issues.push({ severity: 'warning', area: 'system', message: `System memory high: ${(metrics.system.usedPercent * 100).toFixed(1)}%` });
  }
  
  // Uptime bonus (max +5 points for long-running stable agents)
  if (metrics.uptime > 3600) score += 5; // Running > 1 hour
  if (metrics.uptime > 86400) score += 5; // Running > 24 hours
  
  score = Math.max(0, Math.min(100, score));
  
  return {
    score,
    grade: score >= 90 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : score >= 40 ? 'D' : 'F',
    issues,
  };
}

// ── Optimization Suggestions ────────────────────────────────────────────────
function getOptimizations(metrics, apiStats, healthScore) {
  const suggestions = [];
  
  if (metrics.process.heapPercent > 0.7) {
    suggestions.push({
      priority: 'high',
      area: 'memory',
      action: 'Consider running garbage collection or restarting the agent',
      impact: 'Could free 20-40% of heap memory',
    });
  }
  
  if (apiStats.failed > apiStats.success * 0.1) {
    suggestions.push({
      priority: 'high',
      area: 'api',
      action: 'Review failing endpoints and implement retry logic with exponential backoff',
      impact: 'Could improve success rate by 15-30%',
    });
  }
  
  if (apiStats.avgLatency > 1500) {
    suggestions.push({
      priority: 'medium',
      area: 'latency',
      action: 'Consider caching frequent API responses or batching requests',
      impact: 'Could reduce latency by 30-50%',
    });
  }
  
  if (metrics.system.usedPercent > 0.85) {
    suggestions.push({
      priority: 'high',
      area: 'system',
      action: 'Free system memory by closing unused processes or reducing cache size',
      impact: 'Could improve overall system stability',
    });
  }
  
  if (healthScore.score >= 90) {
    suggestions.push({
      priority: 'low',
      area: 'general',
      action: 'Agent is healthy. Continue monitoring and consider setting up automated alerts.',
      impact: 'Proactive monitoring prevents issues',
    });
  }
  
  return suggestions;
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdStatus() {
  const mem = getMemoryMetrics();
  const api = getApiStats();
  const alerts = loadAlerts();
  const health = calculateHealthScore(mem, api, alerts.thresholds);
  
  console.log(`\n## Agent Health Status\n`);
  console.log(`Health Score: ${health.score} (${health.grade})`);
  console.log(`Uptime: ${formatUptime(mem.uptime)}`);
  console.log(`\nMemory:`);
  console.log(`  Heap: ${(mem.process.heapUsed / 1024 / 1024).toFixed(1)} / ${(mem.process.heapTotal / 1024 / 1024).toFixed(1)} MB (${(mem.process.heapPercent * 100).toFixed(1)}%)`);
  console.log(`  RSS: ${(mem.process.rss / 1024 / 1024).toFixed(1)} MB`);
  console.log(`  System: ${(mem.system.usedPercent * 100).toFixed(1)}% used`);
  
  console.log(`\nAPI Calls:`);
  console.log(`  Total: ${api.total} | Success: ${api.success} | Failed: ${api.failed}`);
  console.log(`  Success Rate: ${(api.successRate * 100).toFixed(1)}%`);
  console.log(`  Avg Latency: ${api.avgLatency.toFixed(0)}ms`);
  
  if (health.issues.length > 0) {
    console.log(`\n⚠️  Issues:`);
    for (const issue of health.issues) {
      console.log(`  [${issue.severity.toUpperCase()}] ${issue.area}: ${issue.message}`);
    }
  }
  console.log();
}

function cmdCheck() {
  cmdStatus();
  
  const mem = getMemoryMetrics();
  const api = getApiStats();
  const alerts = loadAlerts();
  const health = calculateHealthScore(mem, api, alerts.thresholds);
  const opts = getOptimizations(mem, api, health);
  
  if (opts.length > 0) {
    console.log(`\n## Optimization Suggestions\n`);
    for (const opt of opts) {
      console.log(`[${opt.priority.toUpperCase()}] ${opt.area}: ${opt.action}`);
      console.log(`  Impact: ${opt.impact}\n`);
    }
  }
  
  // Save to history
  const history = loadHistory();
  history.push({
    timestamp: new Date().toISOString(),
    health: health.score,
    memory: mem.process.heapPercent,
    errorRate: api.total > 0 ? api.failed / api.total : 0,
    latency: api.avgLatency,
  });
  saveHistory(history);
}

function cmdMemory() {
  const mem = getMemoryMetrics();
  console.log(`\n## Memory Details\n`);
  console.log(`Process:`);
  console.log(`  heapUsed: ${(mem.process.heapUsed / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  heapTotal: ${(mem.process.heapTotal / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  heapPercent: ${(mem.process.heapPercent * 100).toFixed(2)}%`);
  console.log(`  external: ${(mem.process.external / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  rss: ${(mem.process.rss / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  arrayBuffers: ${(mem.process.arrayBuffers / 1024 / 1024).toFixed(2)} MB`);
  console.log(`\nSystem:`);
  console.log(`  total: ${(mem.system.total / 1024 / 1024 / 1024).toFixed(2)} GB`);
  console.log(`  free: ${(mem.system.free / 1024 / 1024 / 1024).toFixed(2)} GB`);
  console.log(`  used: ${((mem.system.total - mem.system.free) / 1024 / 1024 / 1024).toFixed(2)} GB`);
  console.log(`  usedPercent: ${(mem.system.usedPercent * 100).toFixed(2)}%`);
  console.log(`\nUptime: ${formatUptime(mem.uptime)}`);
  console.log(`PID: ${mem.pid}`);
  console.log();
}

function cmdApiStats() {
  const api = getApiStats();
  console.log(`\n## API Statistics\n`);
  console.log(`Total calls: ${api.total}`);
  console.log(`Success: ${api.success} | Failed: ${api.failed}`);
  console.log(`Success rate: ${(api.successRate * 100).toFixed(2)}%`);
  console.log(`Avg latency: ${api.avgLatency.toFixed(0)}ms`);
  
  if (Object.keys(api.endpoints).length > 0) {
    console.log(`\nPer-endpoint:`);
    for (const [ep, stats] of Object.entries(api.endpoints)) {
      const rate = stats.calls > 0 ? (stats.success / stats.calls * 100).toFixed(1) : '100';
      const lat = stats.calls > 0 ? (stats.totalLatency / stats.calls).toFixed(0) : '0';
      console.log(`  ${ep}: ${stats.calls} calls, ${rate}% success, ${lat}ms avg`);
    }
  }
  console.log();
}

function cmdErrors(limit) {
  const errs = getErrors(parseInt(limit) || 10);
  console.log(`\n## Recent Errors (${errs.length})\n`);
  for (const e of errs) {
    console.log(`[${e.timestamp}] ${e.message}`);
    if (e.context && Object.keys(e.context).length > 0) {
      console.log(`  Context: ${JSON.stringify(e.context)}`);
    }
  }
  console.log();
}

function cmdReport(format) {
  const mem = getMemoryMetrics();
  const api = getApiStats();
  const alerts = loadAlerts();
  const health = calculateHealthScore(mem, api, alerts.thresholds);
  const opts = getOptimizations(mem, api, health);
  
  const report = {
    timestamp: new Date().toISOString(),
    health: health,
    memory: mem,
    api: api,
    optimizations: opts,
  };
  
  if (format === 'json') {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`\n# Health Report - ${report.timestamp}\n`);
    console.log(`## Health Score: ${health.score} (${health.grade})\n`);
    console.log(`### Memory`);
    console.log(`- Heap: ${(mem.process.heapPercent * 100).toFixed(1)}%`);
    console.log(`- RSS: ${(mem.process.rss / 1024 / 1024).toFixed(1)} MB`);
    console.log(`- System: ${(mem.system.usedPercent * 100).toFixed(1)}%`);
    console.log(`\n### API`);
    console.log(`- Calls: ${api.total}`);
    console.log(`- Success Rate: ${(api.successRate * 100).toFixed(1)}%`);
    console.log(`- Avg Latency: ${api.avgLatency.toFixed(0)}ms`);
    if (health.issues.length > 0) {
      console.log(`\n### Issues`);
      for (const issue of health.issues) {
        console.log(`- [${issue.severity}] ${issue.message}`);
      }
    }
    console.log();
  }
}

function cmdWatch(interval) {
  const ms = parseInt(interval) || 5000;
  console.log(`\n## Health Watch Mode`);
  console.log(`Interval: ${ms}ms | Press Ctrl+C to stop\n`);
  
  const intervalId = setInterval(() => {
    const now = new Date().toISOString().slice(11, 19);
    const mem = getMemoryMetrics();
    const api = getApiStats();
    const alerts = loadAlerts();
    const health = calculateHealthScore(mem, api, alerts.thresholds);
    
    const score = String(health.score).padStart(3);
    const heap = (mem.process.heapPercent * 100).toFixed(1).padStart(5);
    const rate = (api.successRate * 100).toFixed(1).padStart(5);
    
    console.log(`[${now}] Score: ${score} | Heap: ${heap}% | API: ${rate}% | Issues: ${health.issues.length}`);
    
    // Alert on critical issues
    for (const issue of health.issues) {
      if (issue.severity === 'critical') {
        console.log(`  ⚠️  ALERT: ${issue.message}`);
      }
    }
  }, ms);
  
  process.on('SIGINT', () => {
    clearInterval(intervalId);
    console.log('\n\nStopped.');
    process.exit(0);
  });
}

function cmdOptimize() {
  const mem = getMemoryMetrics();
  const api = getApiStats();
  const alerts = loadAlerts();
  const health = calculateHealthScore(mem, api, alerts.thresholds);
  const opts = getOptimizations(mem, api, health);
  
  console.log(`\n## Optimization Suggestions\n`);
  if (opts.length === 0) {
    console.log(`No optimizations needed. Agent is healthy.`);
  } else {
    for (const opt of opts) {
      const badge = opt.priority === 'high' ? '🔴' : opt.priority === 'medium' ? '🟡' : '🟢';
      console.log(`${badge} [${opt.priority.toUpperCase()}] ${opt.area}`);
      console.log(`  Action: ${opt.action}`);
      console.log(`  Impact: ${opt.impact}\n`);
    }
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatUptime(seconds) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  status: cmdStatus,
  check: cmdCheck,
  memory: cmdMemory,
  'api-stats': cmdApiStats,
  errors: cmdErrors,
  report: cmdReport,
  watch: cmdWatch,
  optimize: cmdOptimize,
};

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`health_monitor.js — AI Agent Self-Health Monitoring Engine

Usage: node health_monitor.js <command> [args...]

Commands:
  status              Show current health status
  check               Run full health check with suggestions
  memory              Show detailed memory usage
  api-stats           Show API call statistics
  errors [limit]      Show recent errors (default: 10)
  report [format]     Generate health report (text/json)
  watch [interval]    Continuous monitoring mode (default: 5000ms)
  optimize            Get optimization suggestions

Health Score:
  90-100: A (Excellent)
  75-89:  B (Good)
  60-74:  C (Fair)
  40-59:  D (Poor)
  0-39:   F (Critical)

Examples:
  node health_monitor.js status
  node health_monitor.js check
  node health_monitor.js report json
  node health_monitor.js watch 3000
`);
  process.exit(0);
}

COMMANDS[cmd](...args);
