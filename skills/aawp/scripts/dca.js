#!/usr/bin/env node
/**
 * AAWP DCA — Dollar Cost Averaging
 * Scheduling: OpenClaw cron (preferred) → system crontab (fallback) → manual
 *
 * Usage:
 *   dca.js add --chain base --from ETH --to USDC --amount 0.01 --cron "0 9 * * *" [--name myDCA] [--slippage 0.5]
 *   dca.js list
 *   dca.js remove <id>
 *   dca.js run <id>     -- manually execute once
 *   dca.js history <id> -- execution history for this DCA job
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const S = process.env.AAWP_SKILL || require('path').resolve(__dirname, '..');
const JOBS_FILE    = path.join(S, '.dca-jobs.json');
const HISTORY_FILE = path.join(S, '.dca-history.json');

// ── Storage ──────────────────────────────────────────────────────────────────
function loadJobs() {
  try { return JSON.parse(fs.readFileSync(JOBS_FILE, 'utf8')); }
  catch { return []; }
}
function saveJobs(jobs) { fs.writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2)); }

function loadHistory() {
  try { return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8')); }
  catch { return []; }
}
function saveHistory(h) { fs.writeFileSync(HISTORY_FILE, JSON.stringify(h, null, 2)); }

// ── Parse args ───────────────────────────────────────────────────────────────
function parseArgs(args) {
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--chain'    && args[i+1]) { opts.chain    = args[++i]; continue; }
    if (args[i] === '--from'     && args[i+1]) { opts.from     = args[++i]; continue; }
    if (args[i] === '--to'       && args[i+1]) { opts.to       = args[++i]; continue; }
    if (args[i] === '--amount'   && args[i+1]) { opts.amount   = args[++i]; continue; }
    if (args[i] === '--cron'     && args[i+1]) { opts.cron     = args[++i]; continue; }
    if (args[i] === '--name'     && args[i+1]) { opts.name     = args[++i]; continue; }
    if (args[i] === '--slippage' && args[i+1]) { opts.slippage = args[++i]; continue; }
    if (!args[i].startsWith('--')) opts._pos = opts._pos || [], opts._pos.push(args[i]);
  }
  return opts;
}

// ── Register OpenClaw cron ───────────────────────────────────────────────────
function registerCron(job) {
  const cronPayload = JSON.stringify({
    name: `aawp-dca-${job.id}`,
    trigger: { kind: 'cron', expr: job.cron, tz: 'Asia/Hong_Kong' },
    action: { kind: 'agentTurn', message: `Run AAWP DCA: node ${path.join(S, 'scripts/dca.js')} run ${job.id}` },
  });
  const runCmd = `node ${path.join(S, 'scripts/dca.js')} run ${job.id}`;
  // Try OpenClaw cron first
  try {
    execSync(`command -v openclaw`, { stdio: 'pipe' });
    execSync(`openclaw cron add '${cronPayload.replace(/'/g, "'\\''")}'`, { stdio: 'pipe', timeout: 10000 });
    console.log(`  ✅ Scheduled via OpenClaw cron`);
    return true;
  } catch { /* OpenClaw not available */ }
  // Fallback: system crontab
  try {
    const cronLine = `${job.cron} ${runCmd} >> /tmp/aawp-dca.log 2>&1`;
    const existing = execSync('crontab -l 2>/dev/null || true', { encoding: 'utf8' });
    if (!existing.includes(job.id)) {
      execSync(`(crontab -l 2>/dev/null; echo '${cronLine}') | crontab -`, { stdio: 'pipe' });
      console.log(`  ✅ Scheduled via system crontab`);
      return true;
    }
    return true;
  } catch { /* crontab not available */ }
  // Manual fallback
  console.log(`  ⚠️  No scheduler available. Run manually or add to crontab:`);
  console.log(`  Cron: ${job.cron}`);
  console.log(`  Command: ${runCmd}`);
  return false;
}

function removeCron(jobId) {
  // Try OpenClaw
  try { execSync(`openclaw cron remove aawp-dca-${jobId}`, { stdio: 'pipe', timeout: 10000 }); return; } catch {}
  // Try system crontab
  try {
    const existing = execSync('crontab -l 2>/dev/null', { encoding: 'utf8' });
    const filtered = existing.split('\n').filter(l => !l.includes(jobId)).join('\n');
    execSync(`echo '${filtered}' | crontab -`, { stdio: 'pipe' });
  } catch { /* best effort */ }
}

// ── Commands ─────────────────────────────────────────────────────────────────

function addJob(opts) {
  if (!opts.chain || !opts.from || !opts.to || !opts.amount || !opts.cron) {
    console.log('Usage: dca.js add --chain <chain> --from <token> --to <token> --amount <amt> --cron "<expr>" [--name <name>] [--slippage <pct>]');
    process.exit(1);
  }

  const jobs = loadJobs();
  const job = {
    id:         crypto.randomBytes(4).toString('hex'),
    name:       opts.name || `${opts.from}→${opts.to}`,
    chain:      opts.chain.toLowerCase(),
    fromToken:  opts.from.toUpperCase(),
    toToken:    opts.to.toUpperCase(),
    amount:     opts.amount,
    slippage:   opts.slippage || '0.5',
    cron:       opts.cron,
    createdAt:  new Date().toISOString(),
    lastRun:    null,
    totalRuns:  0,
    totalSpent: '0',
    cronRegistered: false,
  };

  job.cronRegistered = registerCron(job);
  jobs.push(job);
  saveJobs(jobs);

  console.log(`\n✅ DCA job created: ${job.id}`);
  console.log(`   ${job.amount} ${job.fromToken} → ${job.toToken} on ${job.chain.toUpperCase()}`);
  console.log(`   Schedule: ${job.cron} (Asia/Hong_Kong)`);
}

function listJobs() {
  const jobs = loadJobs();
  if (jobs.length === 0) { console.log('No DCA jobs configured.'); return; }

  console.log('=== AAWP DCA Jobs ===\n');
  for (const j of jobs) {
    console.log(`  [${j.id}] ${j.name}`);
    console.log(`    ${j.amount} ${j.fromToken} → ${j.toToken} on ${j.chain.toUpperCase()}`);
    console.log(`    Cron: ${j.cron} | Runs: ${j.totalRuns} | Last: ${j.lastRun || 'never'}`);
    console.log(`    Total spent: ${j.totalSpent} ${j.fromToken} | Cron registered: ${j.cronRegistered ? '✅' : '❌'}`);
    console.log('');
  }
}

function removeJob(id) {
  if (!id) { console.log('Usage: dca.js remove <id>'); process.exit(1); }
  const jobs = loadJobs();
  const idx = jobs.findIndex(j => j.id === id);
  if (idx === -1) { console.log(`❌ Job not found: ${id}`); process.exit(1); }
  removeCron(id);
  const removed = jobs.splice(idx, 1)[0];
  saveJobs(jobs);
  console.log(`✅ Removed DCA job: ${removed.name} (${id})`);
}

async function runJob(id) {
  if (!id) { console.log('Usage: dca.js run <id>'); process.exit(1); }
  const jobs = loadJobs();
  const job = jobs.find(j => j.id === id);
  if (!job) { console.log(`❌ Job not found: ${id}`); process.exit(1); }

  console.log(`\n🔄 Executing DCA: ${job.amount} ${job.fromToken} → ${job.toToken} on ${job.chain.toUpperCase()}`);

  const swapModule = require(path.join(S, 'scripts/swap.js'));
  const history = loadHistory();
  const entry = {
    jobId: id,
    timestamp: new Date().toISOString(),
    amount: job.amount,
    fromToken: job.fromToken,
    toToken: job.toToken,
    chain: job.chain,
    status: 'pending',
    error: null,
  };

  try {
    await swapModule.swap(job.chain, job.fromToken, job.toToken, job.amount);
    entry.status = 'success';
    job.totalRuns++;
    job.totalSpent = String(parseFloat(job.totalSpent) + parseFloat(job.amount));
    job.lastRun = entry.timestamp;
    console.log(`\n✅ DCA execution successful`);
  } catch (e) {
    entry.status = 'failed';
    entry.error = e.message;
    job.totalRuns++;
    job.lastRun = entry.timestamp;
    console.error(`\n❌ DCA execution failed: ${e.message}`);
  }

  history.push(entry);
  saveHistory(history);
  saveJobs(jobs);
}

function showHistory(id) {
  if (!id) { console.log('Usage: dca.js history <id>'); process.exit(1); }
  const history = loadHistory().filter(h => h.jobId === id);
  if (history.length === 0) { console.log(`No history for job ${id}`); return; }

  console.log(`=== DCA History: ${id} ===\n`);
  for (const h of history.slice(-20)) {
    const icon = h.status === 'success' ? '✅' : '❌';
    console.log(`  ${icon} ${h.timestamp} | ${h.amount} ${h.fromToken} → ${h.toToken} | ${h.status}${h.error ? ' | ' + h.error : ''}`);
  }
  console.log(`\nTotal entries: ${history.length}`);
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const opts = parseArgs(args.slice(1));

  switch (cmd) {
    case 'add':     addJob(opts); break;
    case 'list':    listJobs(); break;
    case 'remove':  removeJob(opts._pos?.[0] || args[1]); break;
    case 'run':     await runJob(opts._pos?.[0] || args[1]); break;
    case 'history': showHistory(opts._pos?.[0] || args[1]); break;
    default:
      console.log(`AAWP DCA — Dollar Cost Averaging

Usage:
  dca.js add --chain <chain> --from <token> --to <token> --amount <amt> --cron "<expr>" [--name <name>]
  dca.js list
  dca.js remove <id>
  dca.js run <id>
  dca.js history <id>

Examples:
  dca.js add --chain base --from ETH --to USDC --amount 0.01 --cron "0 9 * * *" --name "Daily ETH→USDC"
  dca.js run abc123
`);
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
