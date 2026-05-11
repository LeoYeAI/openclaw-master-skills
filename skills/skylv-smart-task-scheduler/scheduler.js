/**
 * scheduler.js — Context-aware task scheduler
 * 
 * Run tasks when conditions are met: time, file change, API rate limit, or custom triggers.
 * 
 * Usage: node scheduler.js <command> [args...]
 * Commands:
 *   run <taskfile>           Run scheduled tasks from a taskfile
 *   now <taskfile>           Run all tasks immediately (ignore triggers)
 *   watch <taskfile>         Start daemon (runs continuously)
 *   add <taskfile> <task>    Add a task interactively
 *   list <taskfile>          List all tasks
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── Config ──────────────────────────────────────────────────────────────────
const STATE_FILE = '.scheduler-state.json';

// ── Task Schema ──────────────────────────────────────────────────────────────
// {
//   "id": "uuid",
//   "name": "task name",
//   "trigger": {
//     "kind": "cron" | "interval" | "file-watch" | "rate-limit" | "manual" | "once",
//     "spec": "..."  // cron expr, ms interval, file path, or null
//   },
//   "condition": { "kind": "file-exists" | "api-ready" | "time-window" | "always", "spec": "..." },
//   "action": { "command": "...", "cwd": "...", "env": {} },
//   "lastRun": "ISO date",
//   "nextRun": "ISO date",
//   "runCount": 0,
//   "enabled": true
// }

// ── Trigger Parsers ──────────────────────────────────────────────────────────
function parseCron(expr) {
  // Simple 5-field cron: min hour dom mon dow
  // Returns next run Date, or null if invalid
  try {
    const [min, hour, dom, mon, dow] = expr.trim().split(/\s+/);
    const now = new Date();
    const next = new Date(now);
    next.setSeconds(0, 0);

    const domOk = dom === '*' || parseInt(dom) === now.getDate();
    const monOk = mon === '*' || parseInt(mon) === now.getMonth() + 1;
    const dowOk = dow === '*' || parseInt(dow) === now.getDay();

    if (!domOk || !monOk || !dowOk) return null;

    const targetMin = min === '*' ? now.getMinutes() + 1 : parseInt(min);
    const targetHour = hour === '*' ? now.getHours() : parseInt(hour);

    if (targetMin <= now.getMinutes()) {
      next.setHours(targetHour, targetMin, 0, 0);
      if (next <= now) next.setDate(next.getDate() + 1);
    } else {
      next.setHours(targetHour, targetMin, 0, 0);
    }
    return next;
  } catch { return null; }
}

function parseInterval(spec) {
  const match = spec.match(/^(\d+)(ms|s|m|h|d)?$/);
  if (!match) return null;
  const n = parseInt(match[1]);
  const unit = match[2] || 's';
  const map = { ms: 1, s: 1000, m: 60000, h: 3600000, d: 86400000 };
  return (map[unit] || 1000) * n;
}

// ── Condition Checkers ───────────────────────────────────────────────────────
function checkCondition(cond) {
  if (!cond || cond.kind === 'always') return true;
  try {
    if (cond.kind === 'file-exists') {
      return fs.existsSync(cond.spec);
    }
    if (cond.kind === 'file-not-exists') {
      return !fs.existsSync(cond.spec);
    }
    if (cond.kind === 'file-changed') {
      const [fpath, oldHash] = cond.spec.split('|');
      const hash = crypto.createHash('md5').update(fs.readFileSync(fpath)).digest('hex');
      return hash !== oldHash;
    }
    if (cond.kind === 'time-window') {
      const [start, end] = cond.spec.split('-').map(t => {
        const [h, m] = t.trim().split(':').map(Number);
        return h * 60 + m;
      });
      const now = new Date();
      const mins = now.getHours() * 60 + now.getMinutes();
      return mins >= start && mins <= end;
    }
    if (cond.kind === 'api-ready') {
      // Check a state file for API availability
      const state = STATE_FILE;
      if (!fs.existsSync(state)) return true;
      const data = JSON.parse(fs.readFileSync(state, 'utf8'));
      if (!data.apiResetAt) return true;
      return Date.now() >= data.apiResetAt;
    }
    return true;
  } catch { return false; }
}

// ── Task Execution ───────────────────────────────────────────────────────────
async function runTask(task) {
  const { action, name } = task;
  if (!action) return { ok: false, error: 'No action defined' };

  console.log(`\n[${new Date().toISOString()}] Running: ${name}`);

  try {
    const { execSync } = require('child_process');
    const opts = {
      cwd: action.cwd || process.cwd(),
      stdio: 'inherit',
      env: { ...process.env, ...action.env },
      timeout: (action.timeout || 60) * 1000,
    };
    const out = execSync(action.command, opts);
    task.lastRun = new Date().toISOString();
    task.runCount = (task.runCount || 0) + 1;
    console.log(`✅ Completed: ${name} (run #${task.runCount})`);
    return { ok: true };
  } catch (err) {
    task.lastRun = new Date().toISOString();
    task.runCount = (task.runCount || 0) + 1;
    task.lastError = err.message?.slice(0, 200);
    console.log(`❌ Failed: ${name} — ${err.message?.slice(0, 100)}`);
    return { ok: false, error: err.message?.slice(0, 200) };
  }
}

// ── Trigger Evaluation ────────────────────────────────────────────────────────
function shouldRun(task) {
  if (!task.enabled) return false;

  const { trigger, condition } = task;

  if (trigger.kind === 'manual' || trigger.kind === 'once') return false; // only run via explicit call

  if (trigger.kind === 'interval') {
    const interval = parseInterval(trigger.spec);
    if (!interval) return false;
    const last = task.lastRun ? new Date(task.lastRun).getTime() : 0;
    return Date.now() - last >= interval;
  }

  if (trigger.kind === 'cron') {
    const next = parseCron(trigger.spec);
    if (!next) return false;
    return Date.now() >= next.getTime();
  }

  if (trigger.kind === 'file-watch') {
    if (!task._lastFileHash) {
      try { task._lastFileHash = crypto.createHash('md5').update(fs.readFileSync(trigger.spec)).digest('hex'); } catch {}
      return false;
    }
    try {
      const h = crypto.createHash('md5').update(fs.readFileSync(trigger.spec)).digest('hex');
      if (h !== task._lastFileHash) { task._lastFileHash = h; return true; }
    } catch {}
    return false;
  }

  return false;
}

// ── Task File Operations ─────────────────────────────────────────────────────
function loadTasks(taskFile) {
  if (!fs.existsSync(taskFile)) return [];
  try { return JSON.parse(fs.readFileSync(taskFile, 'utf8')); }
  catch { return []; }
}

function saveTasks(taskFile, tasks) {
  fs.writeFileSync(taskFile, JSON.stringify(tasks, null, 2));
}

function addTask(taskFile, task) {
  const tasks = loadTasks(taskFile);
  task.id = crypto.randomUUID();
  task.created = new Date().toISOString();
  task.runCount = 0;
  task.enabled = true;
  tasks.push(task);
  saveTasks(taskFile, tasks);
  console.log(`✅ Added: ${task.name} (${task.id.slice(0, 8)})`);
  return task;
}

// ── Commands ─────────────────────────────────────────────────────────────────

function cmdList(taskFile) {
  const tasks = loadTasks(taskFile);
  if (tasks.length === 0) { console.log('No tasks.'); return; }
  console.log(`\n## Tasks: ${taskFile}\n`);
  for (const t of tasks) {
    const en = t.enabled ? '✅' : '⛔';
    const last = t.lastRun ? new Date(t.lastRun).toLocaleString() : 'never';
    const count = t.runCount || 0;
    const trigger = t.trigger?.kind || '?';
    console.log(`  ${en} [${t.id?.slice(0, 8)}] ${t.name}`);
    console.log(`       Trigger: ${trigger} | Runs: ${count} | Last: ${last}`);
  }
  console.log();
}

function cmdRun(taskFile) {
  const tasks = loadTasks(taskFile);
  const runnable = tasks.filter(t => t.enabled && shouldRun(t) && checkCondition(t.condition));

  if (runnable.length === 0) {
    console.log('No tasks ready to run.');
    return;
  }

  console.log(`\nRunning ${runnable.length} task(s)...\n`);
  for (const t of runnable) {
    runTask(t).then(() => {
      saveTasks(taskFile, tasks); // persist updated runCount
    });
  }
}

async function cmdNow(taskFile) {
  const tasks = loadTasks(taskFile);
  const enabled = tasks.filter(t => t.enabled);
  if (enabled.length === 0) { console.log('No enabled tasks.'); return; }
  console.log(`\nRunning ${enabled.length} task(s) immediately...\n`);
  for (const t of enabled) {
    await runTask(t);
  }
  saveTasks(taskFile, tasks);
}

function cmdWatch(taskFile) {
  console.log(`\nScheduler daemon active: ${taskFile}`);
  console.log('Press Ctrl+C to stop\n');

  const tasks = loadTasks(taskFile);
  const interval = 30000; // check every 30s

  const tick = () => {
    const current = loadTasks(taskFile); // reload (user might edit)
    for (const t of current) {
      if (t.enabled && shouldRun(t) && checkCondition(t.condition)) {
        runTask(t).then(() => saveTasks(taskFile, loadTasks(taskFile)));
      }
    }
  };

  tick();
  const id = setInterval(tick, interval);

  process.on('SIGINT', () => {
    clearInterval(id);
    console.log('\nStopped.');
    process.exit(0);
  });
}

// ── Main ──────────────────────────────────────────────────────────────────────
const [,, cmd, taskFile, ...args] = process.argv;

const COMMANDS = { run: cmdRun, now: cmdNow, watch: cmdWatch, list: cmdList };

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`scheduler.js — Context-aware task scheduler

Usage: node scheduler.js <command> <taskfile> [args...]

Commands:
  run <taskfile>      Run all tasks whose triggers are due
  now <taskfile>      Run all enabled tasks immediately
  watch <taskfile>    Start daemon (checks every 30s)
  list <taskfile>     List all tasks
  add <taskfile>      Add task interactively (TODO)

Taskfile format (.json):
{
  "id": "uuid",
  "name": "Check emails every morning",
  "trigger": {
    "kind": "cron",          // cron | interval | file-watch | rate-limit | manual | once
    "spec": "0 9 * * 1-5"   // cron expr, interval spec, or file path
  },
  "condition": {
    "kind": "time-window",   // always | file-exists | file-not-exists | time-window | api-ready
    "spec": "09:00-17:00"    // file path, time range, or null
  },
  "action": {
    "command": "echo done",
    "cwd": ".",
    "timeout": 60
  },
  "enabled": true
}

Trigger kinds:
  cron        — Unix cron expression (min hour dom mon dow)
  interval    — e.g., "30s", "5m", "1h", "1d"
  file-watch  — Run when a file changes
  rate-limit  — Run when API rate limit resets
  manual      — Only via 'now' command
  once        — Run once, then disable

Condition kinds:
  always       — No condition
  file-exists  — File must exist
  file-not-exists — File must not exist
  time-window  — Within time range (HH:MM-HH:MM)
  api-ready    — API rate limit has reset

Examples:
  node scheduler.js list tasks.json
  node scheduler.js now tasks.json
  node scheduler.js watch tasks.json
`);
  process.exit(0);
}

const absTaskFile = path.isAbsolute(taskFile) ? taskFile : path.resolve(process.cwd(), taskFile);
COMMANDS[cmd](absTaskFile);
