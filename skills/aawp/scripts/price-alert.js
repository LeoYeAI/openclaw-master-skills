#!/usr/bin/env node
/**
 * AAWP Price Alert — monitor token prices and notify/auto-swap
 *
 * Usage:
 *   price-alert.js add --chain base --from ETH --to USDC --above 2600 [--notify] [--auto-swap 0.01]
 *   price-alert.js add --chain base --from ETH --to USDC --below 2200 [--notify] [--auto-swap 0.01]
 *   price-alert.js list
 *   price-alert.js remove <id>
 *   price-alert.js check   -- manually check all alerts (called by cron)
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');
const { execSync } = require('child_process');

const S = process.env.AAWP_SKILL || require('path').resolve(__dirname, '..');
const ALERTS_FILE = path.join(S, '.price-alerts.json');
const CHAINS = JSON.parse(fs.readFileSync(path.join(S, 'config/chains.json'), 'utf8'));

const NATIVE = '0x0000000000000000000000000000000000000000';
const RELAY_API = 'https://api.relay.link';

// ── Helpers ──────────────────────────────────────────────────────────────────
function loadAlerts() {
  try { return JSON.parse(fs.readFileSync(ALERTS_FILE, 'utf8')); }
  catch { return []; }
}
function saveAlerts(a) { fs.writeFileSync(ALERTS_FILE, JSON.stringify(a, null, 2)); }

function resolveToken(chainKey, sym) {
  if (sym === 'ETH' || sym === 'BNB' || sym === 'MATIC' || sym.toLowerCase() === 'native') return NATIVE;
  if (sym.startsWith('0x') && sym.length === 42) return sym;
  const cfg = CHAINS[chainKey];
  const upper = sym.toUpperCase();
  if (cfg?.tokens?.[upper]) return cfg.tokens[upper];
  throw new Error(`Unknown token "${sym}" on ${chainKey}`);
}

function relayFetch(method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const url = new URL(RELAY_API + urlPath);
    const opts = {
      hostname: url.hostname, path: url.pathname + url.search, method,
      headers: { 'Content-Type': 'application/json', 'User-Agent': 'AAWP/1.0', ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}) },
      timeout: 15000,
    };
    const req = https.request(opts, (res) => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => { try { resolve(JSON.parse(raw)); } catch (e) { reject(new Error(`Parse error: ${raw.slice(0, 200)}`)); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (data) req.write(data);
    req.end();
  });
}

/** Get price of 1 unit of fromToken denominated in toToken via Relay quote */
async function getPrice(chainKey, fromToken, toToken) {
  const { ethers } = require('ethers');
  const chain = CHAINS[chainKey];
  if (!chain) throw new Error(`Unknown chain: ${chainKey}`);

  const fromAddr = resolveToken(chainKey, fromToken);
  const toAddr = resolveToken(chainKey, toToken);

  // Use 1 unit of fromToken (18 decimals for native, query for ERC20)
  let decimals = 18;
  if (fromAddr !== NATIVE) {
    try {
      const p = new ethers.JsonRpcProvider(chain.rpcOverride || chain.rpc);
      const tok = new ethers.Contract(fromAddr, ['function decimals() view returns (uint8)'], p);
      decimals = Number(await tok.decimals());
    } catch {}
  }
  const amount = ethers.parseUnits('1', decimals).toString();

  // We need a user address for the quote — use zero address for quote-only
  const quote = await relayFetch('POST', '/quote/v2', {
    user: '0x0000000000000000000000000000000000000001',
    originChainId: chain.chainId,
    destinationChainId: chain.chainId,
    originCurrency: fromAddr,
    destinationCurrency: toAddr,
    amount,
    tradeType: 'EXACT_INPUT',
  });

  if (quote.message && !quote.details) {
    throw new Error(`Relay quote: ${quote.message}`);
  }

  const cout = quote.details?.currencyOut;
  if (!cout) throw new Error('No output in quote');
  const outDecimals = cout.currency?.decimals || 6;
  const outAmount = cout.amount?.amount || cout.amount || '0';
  return parseFloat(ethers.formatUnits(BigInt(outAmount), outDecimals));
}

// ── Parse args ───────────────────────────────────────────────────────────────
function parseArgs(args) {
  const opts = { notify: false, autoSwap: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--chain'      && args[i+1]) { opts.chain     = args[++i]; continue; }
    if (args[i] === '--from'       && args[i+1]) { opts.from      = args[++i]; continue; }
    if (args[i] === '--to'         && args[i+1]) { opts.to        = args[++i]; continue; }
    if (args[i] === '--above'      && args[i+1]) { opts.above     = parseFloat(args[++i]); continue; }
    if (args[i] === '--below'      && args[i+1]) { opts.below     = parseFloat(args[++i]); continue; }
    if (args[i] === '--notify')                   { opts.notify    = true; continue; }
    if (args[i] === '--auto-swap'  && args[i+1]) { opts.autoSwap  = args[++i]; continue; }
    if (!args[i].startsWith('--')) opts._pos = opts._pos || [], opts._pos.push(args[i]);
  }
  return opts;
}

// ── Register cron (every 5 min check) ────────────────────────────────────────
let _cronRegistered = false;
function ensureCronRegistered() {
  if (_cronRegistered) return;
  const checkCmd = `node ${path.join(S, 'scripts/price-alert.js')} check`;
  // Try OpenClaw cron
  try {
    execSync(`command -v openclaw`, { stdio: 'pipe' });
    const payload = JSON.stringify({
      name: 'aawp-price-alert-check',
      trigger: { kind: 'cron', expr: '*/5 * * * *', tz: 'Asia/Hong_Kong' },
      action: { kind: 'agentTurn', message: `Run Price Alert check: ${checkCmd}` },
    });
    execSync(`openclaw cron add '${payload.replace(/'/g, "'\\''")}'`, { stdio: 'pipe', timeout: 10000 });
    _cronRegistered = true;
    return;
  } catch {}
  // Fallback: system crontab
  try {
    const cronLine = `*/5 * * * * ${checkCmd} >> /tmp/aawp-price-alert.log 2>&1`;
    const existing = execSync('crontab -l 2>/dev/null || true', { encoding: 'utf8' });
    if (!existing.includes('aawp-price-alert')) {
      execSync(`(crontab -l 2>/dev/null; echo '${cronLine}') | crontab -`, { stdio: 'pipe' });
    }
    _cronRegistered = true;
    return;
  } catch {}
  console.log(`  ⚠️  No scheduler available. Run manually: ${checkCmd}`);
}

// ── Commands ─────────────────────────────────────────────────────────────────

function addAlert(opts) {
  if (!opts.chain || !opts.from || !opts.to || (opts.above == null && opts.below == null)) {
    console.log('Usage: price-alert.js add --chain <chain> --from <token> --to <token> --above <price> | --below <price> [--notify] [--auto-swap <amount>]');
    process.exit(1);
  }

  const alerts = loadAlerts();
  const alert = {
    id:        crypto.randomBytes(4).toString('hex'),
    chain:     opts.chain.toLowerCase(),
    fromToken: opts.from.toUpperCase(),
    toToken:   opts.to.toUpperCase(),
    condition: opts.above != null ? 'above' : 'below',
    threshold: opts.above != null ? opts.above : opts.below,
    notify:    opts.notify,
    autoSwap:  opts.autoSwap,
    triggered: false,
    createdAt: new Date().toISOString(),
    triggeredAt: null,
  };

  alerts.push(alert);
  saveAlerts(alerts);
  ensureCronRegistered();

  console.log(`\n✅ Price alert created: ${alert.id}`);
  console.log(`   ${alert.fromToken}/${alert.toToken} ${alert.condition} ${alert.threshold} on ${alert.chain.toUpperCase()}`);
  if (alert.notify) console.log('   📱 Telegram notification enabled');
  if (alert.autoSwap) console.log(`   🔄 Auto-swap: ${alert.autoSwap} ${alert.fromToken}`);
}

function listAlerts() {
  const alerts = loadAlerts();
  if (alerts.length === 0) { console.log('No price alerts configured.'); return; }

  console.log('=== AAWP Price Alerts ===\n');
  for (const a of alerts) {
    const status = a.triggered ? '🔔 TRIGGERED' : '👀 watching';
    console.log(`  [${a.id}] ${a.fromToken}/${a.toToken} ${a.condition} ${a.threshold} (${a.chain.toUpperCase()}) — ${status}`);
    if (a.notify) process.stdout.write('    📱 notify');
    if (a.autoSwap) process.stdout.write(`    🔄 auto-swap ${a.autoSwap}`);
    if (a.triggeredAt) process.stdout.write(`    triggered: ${a.triggeredAt}`);
    console.log('');
  }
}

function removeAlert(id) {
  if (!id) { console.log('Usage: price-alert.js remove <id>'); process.exit(1); }
  const alerts = loadAlerts();
  const idx = alerts.findIndex(a => a.id === id);
  if (idx === -1) { console.log(`❌ Alert not found: ${id}`); process.exit(1); }
  alerts.splice(idx, 1);
  saveAlerts(alerts);
  console.log(`✅ Removed alert: ${id}`);
}

async function checkAlerts() {
  const alerts = loadAlerts();
  const active = alerts.filter(a => !a.triggered);
  if (active.length === 0) { console.log('No active alerts.'); return; }

  console.log(`Checking ${active.length} active alert(s)...\n`);
  let changed = false;

  for (const alert of active) {
    try {
      const price = await getPrice(alert.chain, alert.fromToken, alert.toToken);
      const met = (alert.condition === 'above' && price >= alert.threshold) ||
                  (alert.condition === 'below' && price <= alert.threshold);

      console.log(`  ${alert.fromToken}/${alert.toToken} = ${price.toFixed(4)} | threshold ${alert.condition} ${alert.threshold} → ${met ? '🔔 TRIGGERED' : 'not met'}`);

      if (met) {
        alert.triggered = true;
        alert.triggeredAt = new Date().toISOString();
        changed = true;

        const now = new Date().toLocaleString('en-US', { timeZone: 'Asia/Hong_Kong', hour12: false });

        // Notify via Telegram (best effort — output message for agent to pick up)
        if (alert.notify) {
          const msg = `⚡ Price Alert Triggered\n${alert.fromToken}/${alert.toToken} = ${price.toFixed(4)} (${alert.condition} ${alert.threshold})\nChain: ${alert.chain.toUpperCase()} | Time: ${now}`;
          console.log(`\n📱 NOTIFY:\n${msg}\n`);
          // Try openclaw message
          try {
            execSync(`echo '${msg.replace(/'/g, "'\\''")}' | openclaw message send --channel telegram`, { stdio: 'pipe', timeout: 10000 });
          } catch { /* agent will see console output */ }
        }

        // Auto-swap
        if (alert.autoSwap) {
          console.log(`\n🔄 Auto-swap: ${alert.autoSwap} ${alert.fromToken} → ${alert.toToken}`);
          try {
            const swapModule = require(path.join(S, 'scripts/swap.js'));
            await swapModule.swap(alert.chain, alert.fromToken, alert.toToken, alert.autoSwap);
            console.log('✅ Auto-swap complete');
          } catch (e) {
            console.error(`❌ Auto-swap failed: ${e.message}`);
          }
        }
      }
    } catch (e) {
      console.log(`  ❌ ${alert.fromToken}/${alert.toToken} on ${alert.chain}: ${e.message}`);
    }
  }

  if (changed) saveAlerts(alerts);
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const opts = parseArgs(args.slice(1));

  switch (cmd) {
    case 'add':    addAlert(opts); break;
    case 'list':   listAlerts(); break;
    case 'remove': removeAlert(opts._pos?.[0] || args[1]); break;
    case 'check':  await checkAlerts(); break;
    default:
      console.log(`AAWP Price Alert — Monitor & Auto-Swap

Usage:
  price-alert.js add --chain <chain> --from <token> --to <token> --above <price> [--notify] [--auto-swap <amt>]
  price-alert.js add --chain <chain> --from <token> --to <token> --below <price> [--notify] [--auto-swap <amt>]
  price-alert.js list
  price-alert.js remove <id>
  price-alert.js check
`);
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
