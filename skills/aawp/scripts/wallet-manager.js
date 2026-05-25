#!/usr/bin/env node
/**
 * AAWP Wallet Manager — Multi-chain ERC-20 Edition
 * Chains: base, eth, arb, op, polygon, bsc
 *
 * Usage:
 *   wallet-manager [--chain <chain>] <command> [args]
 *
 * Commands:
 *   status                          Show wallet status on active chain
 *   status --all                    Show wallet status on all 6 chains
 *   send <to> <amount>              Send native ETH/BNB/MATIC
 *   send-token <token> <to> <amt>   Send ERC-20 (token = symbol or address)
 *   balance                         Show native + ERC-20 balances
 *   compute-address                 Predict stable wallet address
 *   upgrade-signer                  Upgrade aiSigner after binary update
 *   backup [path]                   Backup wallet seed/config
 *   restore <path>                  Restore wallet from backup
 *
 * Examples:
 *   wallet-manager status
 *   wallet-manager --chain arb balance
 *   wallet-manager --chain bsc send-token USDT 0xABC... 100
 *   wallet-manager status --all
 */
'use strict';

const net = require('net');
const { ethers } = require('ethers');
const { execSync, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ENSURE_SCRIPT = path.join(__dirname, 'ensure-daemon.sh');

// ── Infrastructure libs ──────────────────────────────────────────────────────
const nonceManager = require(path.join(__dirname, '../lib/nonce-manager'));
const { getGasPrice, estimateGasCost } = require(path.join(__dirname, '../lib/gas-estimator'));
const txHistory = require(path.join(__dirname, '../lib/tx-history'));
const { batchExecute } = require(path.join(__dirname, '../lib/multicall'));

// ── Parse flags ──────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
let chainArg = null;
let showAll = false;
let rpcFlag = null;  // --rpc <url> : one-shot override, not persisted
let slippageBps = 50; // default 0.5%
let bridgeRecipient = null; // --to <address> for bridge recipient
const filteredArgv = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chain' && argv[i + 1]) { chainArg = argv[++i]; }
  else if (argv[i] === '--all') { showAll = true; }
  else if (argv[i] === '--rpc' && argv[i + 1]) { rpcFlag = argv[++i]; }
  else if (argv[i] === '--slippage' && argv[i + 1]) { slippageBps = parseInt(argv[++i], 10); }
  else if (argv[i] === '--to' && argv[i + 1]) { bridgeRecipient = argv[++i]; }
  else filteredArgv.push(argv[i]);
}
process.argv = [process.argv[0], process.argv[1], ...filteredArgv];

// ── Paths & Config ───────────────────────────────────────────────────────────
const C = process.env.AAWP_CONFIG || require('path').join(__dirname, '..', '.agent-config');
const S = process.env.AAWP_SKILL || require('path').resolve(__dirname, '..');
// Detect restore early — skip native addon entirely (shard may be missing)
const _earlyCmd = process.argv.slice(2).filter(a => !a.startsWith('--'))[0] || '';
if (_earlyCmd === 'restore') { require('./restore-impl.js'); process.exit(0); }
const addon = require(process.env.AAWP_CORE || require('path').join(__dirname, '..', 'core', 'aawp-core.node'));

// ── Chain Registry ───────────────────────────────────────────────────────────
const CHAINS_FILE = path.join(S, 'config/chains.json');
let CHAINS = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));
const DEFAULT_CHAIN = process.env.AAWP_CHAIN || 'base';

function saveChains() {
  fs.writeFileSync(CHAINS_FILE, JSON.stringify(CHAINS, null, 2));
}

function getChain(name) {
  const key = (name || chainArg || DEFAULT_CHAIN).toLowerCase();
  if (!CHAINS[key]) {
    console.error(`❌ Unknown chain: ${key}. Valid: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }
  const cfg = CHAINS[key];
  // RPC priority: --rpc flag > env AAWP_RPC > rpcOverride > default rpc
  const rpc = rpcFlag
    || (key === (chainArg || DEFAULT_CHAIN) && process.env.AAWP_RPC)
    || cfg.rpcOverride
    || cfg.rpc;
  return { key, ...cfg, rpc };
}

// ── Bootstrap: download missing binaries on first run ────────────────────────
try {
  require('child_process').execSync(`bash "${S}/scripts/bootstrap.sh"`, { stdio: 'inherit' });
} catch (_) { /* bootstrap is best-effort; ensure-daemon will also try */ }

// ── Socket Daemon ────────────────────────────────────────────────────────────
// ── Daemon Connection (AI Gate Architecture) ────────────────────────────────
// wallet-manager.js no longer starts its own daemon.
// It MUST connect to a persistent daemon started by OpenClaw via start-daemon.js.
// If no daemon is running, all signing operations fail.
// This ensures every signing request flows through the AI-gated daemon.
const _cmd0 = process.argv.slice(2).filter(a => !a.startsWith('--'))[0] || '';
const DAEMON_LOCK = '/tmp/.aawp-daemon.lock';
let sock;
let _aiGateToken = null;

// ── Auto-provision on first run ──
if (_cmd0 === 'create' && !fs.existsSync(`${S}/.agent-config/seed.enc`)) {
  console.log('🔧 First-time setup — provisioning signer key...\n');
  require('child_process').execSync(`bash ${S}/scripts/provision.sh`, { stdio: 'inherit' });
  console.log('\n✅ Provision complete. Run the create command again to deploy your wallet.');
  // Binary was replaced on disk — native addon in memory is stale.
  // process.exit() triggers V8 cleanup → segfault. SIGKILL skips it.
  process.kill(process.pid, 'SIGKILL');
}

if (_cmd0 !== 'restore') {
  // Read lock file written by start-daemon.js (OpenClaw)
  let lockData;
  try {
    lockData = JSON.parse(require('fs').readFileSync(DAEMON_LOCK, 'utf8'));
  } catch (e) {
    lockData = null;
  }

  // Security: NO auto-start. Daemon must be started by OpenClaw only.
  // This prevents root attackers from spawning a fresh daemon to obtain a new AI gate token.
  if (!lockData || !lockData.sock || !require('fs').existsSync(lockData.sock)) {
    console.error('❌ AAWP daemon not running. It must be started by OpenClaw (not manually).');
    console.error('   Run via OpenClaw: the daemon is started automatically with AI gate token.');
    process.exit(1);
  }

  sock = lockData.sock;
  // AI Gate token: ONLY from env var injected by OpenClaw — never from disk.
  // This ensures only AI-initiated calls can sign transactions.
  // Token priority: persisted rotated token > env var > none
  // Persisted token is more recent (rotated after last successful sign)
  try {
    const persisted = fs.readFileSync('/tmp/.aawp-ai-token', 'utf8').trim();
    if (persisted && persisted.length === 64) _aiGateToken = persisted;
  } catch (_) {}
  if (!_aiGateToken) _aiGateToken = process.env.AAWP_AI_TOKEN || null;
  if (!_aiGateToken) {
    console.error('⚠️  No AAWP_AI_TOKEN — signing operations will be rejected (read-only mode).');
  }
  // Init addon state (HMAC key etc) WITHOUT starting a competing daemon
  addon._i0(C, S);
}

function ensureDaemon() {
  try {
    execFileSync(ENSURE_SCRIPT, { stdio: 'ignore', timeout: 30000 });
  } catch (e) {
    throw new Error('AAWP daemon unavailable; auto-restart failed');
  }
}

function socketQuery(obj) {
  const signCmds = new Set(['sign', 'sign_hash', 'create_proof', 'send', 'execute', 'atomic_sign_submit']);
  const ensureCmds = new Set(['sign', 'sign_hash', 'create_proof', 'send', 'execute', 'atomic_sign_submit', 'guardian', 'address', 'logichash']);
  const cmdName = typeof obj === 'string' ? obj : obj && obj.cmd;
  if (cmdName && ensureCmds.has(cmdName)) ensureDaemon();
  const ts = Math.floor(Date.now() / 1000);
  const hmac = addon._h0(ts);
  const isSign = typeof obj !== 'string' && (!obj.cmd || signCmds.has(obj.cmd));
  // For sign requests, include ai_token if available; rotate locally after use
  const aiFields = (isSign && _aiGateToken) ? { ai_token: _aiGateToken } : {};
  if (isSign && _aiGateToken) {
    // Persist current token for this request; rotate only after a successful response.
  }
  const payload = typeof obj === 'string'
    ? { cmd: obj, ts, hmac }
    : { ...obj, ts, hmac, ...aiFields };
  return new Promise((res, rej) => {
    const c = net.createConnection(sock, () => c.end(JSON.stringify(payload)));
    let d = '';
    c.on('data', x => d += x);
    c.on('end', () => {
      try {
        const parsed = JSON.parse(d);
        if (isSign && _aiGateToken && parsed && !parsed.error) {
          try {
            const rotated = fs.readFileSync('/tmp/.aawp-ai-token', 'utf8').trim();
            if (rotated && rotated.length === 64 && rotated !== _aiGateToken) {
              _aiGateToken = rotated;
            }
          } catch (_) {}
        }
        res(parsed);
      } catch (e) { rej(d); }
    });
    c.on('error', rej);
    setTimeout(() => { c.destroy(); rej(new Error('socket timeout')); }, 30000);
  });
}

// ── ABIs ─────────────────────────────────────────────────────────────────────
const FACTORY_ABI = [
  'function computeAddress(address,bytes32,address) view returns (address)',
  'function commit(bytes32 blindHash) external',
  'function reveal(address,bytes32,address,bytes32,bytes32,bytes) payable returns (address,uint256)',
  'function commitStatus(bytes32) view returns (bool exists, address committer, uint256 committedAt, bool revealable, bool expired)',
  'function REVEAL_DELAY() view returns (uint256)',
  'function approvedBinary(bytes32) view returns (bool)',
  'function usedNonces(bytes32) view returns (bool)',
];

const WALLET_ABI = (() => {
  try { return require('/root/aawp-contracts/out/AAWPWallet.sol/AAWPWallet.json').abi; }
  catch { return [
    'function nonce() view returns (uint256)',
    'function aiSigner() view returns (address)',
    'function logicHash() view returns (bytes32)',
    'function frozen() view returns (bool)',
    'function execute(address,uint256,bytes,uint256,bytes) returns (bytes)',
    'function upgradeAiSigner(address,bytes32)',
    'function freeze()',
    'function unfreeze()',
    'function emergencyWithdraw(address,address,uint256)',
  ]; }
})();

const ERC20_ABI = [
  'function name() view returns (string)',
  'function symbol() view returns (string)',
  'function decimals() view returns (uint8)',
  'function balanceOf(address) view returns (uint256)',
  'function transfer(address,uint256) returns (bool)',
  'function allowance(address,address) view returns (uint256)',
  'function approve(address,uint256) returns (bool)',
];

// ── Relay swap module ─────────────────────────────────────────────────────────
const swapModule = require(path.join(S, 'scripts/swap.js'));

// ── Address book ──────────────────────────────────────────────────────────────
const addressBook = require(path.join(S, 'lib/address-book.js'));

// ── Constants ─────────────────────────────────────────────────────────────────
const MIN_WALLET_BAL = ethers.parseEther('0.0001');
const MIN_GUARDIAN_BAL  = ethers.parseEther('0.00005');

// ── Helpers ───────────────────────────────────────────────────────────────────
function loadGuardianRecord() {
  const p = path.join(S, 'config/guardian.json');
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (_) {
    return null;
  }
}

function saveGuardianRecord(rec) {
  const p = path.join(S, 'config/guardian.json');
  fs.writeFileSync(p, JSON.stringify(rec, null, 2));
}

function ensureLocalGuardian() {
  let rec = loadGuardianRecord();
  if (rec && rec.address && rec.privateKey) return rec;
  const w = ethers.Wallet.createRandom();
  rec = { address: w.address, privateKey: w.privateKey, createdAt: new Date().toISOString() };
  saveGuardianRecord(rec);
  return rec;
}

async function getAddresses() {
  const [a, l] = await Promise.all([
    socketQuery('address'),
    socketQuery('logichash'),
  ]);
  const guardianRec = ensureLocalGuardian();
  return { signer: a.address, guardian: guardianRec.address, logicHash: l.logicHash };
}

function resolveToken(chain, tokenArg) {
  if (ethers.isAddress(tokenArg)) return tokenArg;
  const sym = tokenArg.toUpperCase();
  if (chain.tokens && chain.tokens[sym]) return chain.tokens[sym];
  console.error(`❌ Unknown token "${tokenArg}" on ${chain.name}. Known: ${Object.keys(chain.tokens || {}).join(', ')} or use contract address.`);
  process.exit(1);
}

async function getWalletAddress(chain, signer, logicHash, guardian) {
  if (process.env.AAWP_WALLET) return process.env.AAWP_WALLET;
  if (!chain.deployed || chain.factory === ethers.ZeroAddress) return null;
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  return factory.computeAddress(signer, logicHash, guardian);
}

async function signAndSend(chain, walletAddr, to, value, data, nonce, deadline, gasLimit) {
  const payload = {
    cmd: 'sign',
    wallet: walletAddr,
    to,
    value: '0x' + value.toString(16),
    nonce: Number(nonce),
    deadline,
    chain_id: chain.chainId,
    rpc: chain.rpc,
    data: data || '0x',
    ...(gasLimit ? { gas_limit: Number(gasLimit) } : {}),
  };

  const worker = path.join(__dirname, 'sign-worker.js');
  let raw;
  try {
    raw = execFileSync(process.execPath, [worker, JSON.stringify(payload)], {
      env: process.env,
      encoding: 'utf8',
      timeout: 45000,
      maxBuffer: 1024 * 1024,
    });
  } catch (err) {
    const out = (err.stdout || err.stderr || err.message || '').toString().trim();
    console.log('❌ Sign error:', out || 'sign worker failed');
    process.exit(1);
  }

  let result;
  try {
    result = JSON.parse(String(raw).trim());
  } catch (_) {
    console.log('❌ Sign error: invalid worker response');
    process.exit(1);
  }

  if (result.error) {
    console.log('❌ Sign error:', result.error);
    process.exit(1);
  }
  return result.result;
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════════════════

// ── status ────────────────────────────────────────────────────────────────────
async function statusChain(chain, addrs) {
  const { signer, guardian, logicHash } = addrs;
  const tag = `[${chain.key.toUpperCase()}]`;

  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`${tag} ${chain.name} — Factory not deployed (placeholder)`);
    console.log(`${tag}   Factory:  ${chain.factory}`);
    console.log(`${tag}   To deploy: forge script script/Deploy.s.sol --rpc-url ${chain.rpc} --broadcast`);
    return;
  }

  const p = new ethers.JsonRpcProvider(chain.rpc);
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const code = await p.getCode(walletAddr);
  const isDeployed = code.length > 2;

  console.log(`${tag} ${chain.name}`);
  console.log(`${tag}   Wallet:   ${walletAddr} ${isDeployed ? '✅ deployed' : '⚠️  not deployed'}`);
  console.log(`${tag}   Factory:  ${chain.factory}`);

  if (isDeployed) {
    const [wBal, gBal] = await Promise.all([p.getBalance(walletAddr), p.getBalance(guardian)]);
    const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
    const nonce = await w.nonce();
    const frozen = await w.frozen();
    console.log(`${tag}   Balance:  ${ethers.formatEther(wBal)} ${chain.nativeCurrency}`);
    console.log(`${tag}   Guardian: ${ethers.formatEther(gBal)} ${chain.nativeCurrency}`);
    console.log(`${tag}   Nonce:    ${nonce} | Frozen: ${frozen ? '🔒 yes' : 'no'}`);
    if (wBal < MIN_WALLET_BAL) console.log(`${tag}   ⚠️  Wallet balance low! Top up: ${walletAddr}`);
    if (gBal < MIN_GUARDIAN_BAL)  console.log(`${tag}   ⚠️  Guardian balance low!  Top up: ${guardian}`);
  } else {
    console.log(`${tag}   Use: wallet-manager --chain ${chain.key} create`);
  }
}

async function status() {
  const addrs = await getAddresses();
  console.log('=== AAWP Wallet Status ===');
  console.log('Signer   :', addrs.signer);
  console.log('Guardian :', addrs.guardian);
  console.log('');

  if (showAll) {
    for (const key of Object.keys(CHAINS)) {
      await statusChain({ key, ...CHAINS[key] }, addrs);
      console.log('');
    }
  } else {
    const chain = getChain();
    await statusChain(chain, addrs);
  }
}

// ── balance ───────────────────────────────────────────────────────────────────
async function balance() {
  const chain = getChain();
  const { signer, guardian, logicHash } = await getAddresses();

  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`⚠️  ${chain.name} factory not deployed.`);
    return;
  }

  const p = new ethers.JsonRpcProvider(chain.rpc);
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const code = await p.getCode(walletAddr);
  if (code.length <= 2) {
    console.log(`⚠️  Wallet not deployed on ${chain.name}: ${walletAddr}`);
    return;
  }

  console.log(`=== ${chain.name} Balances ===`);
  console.log(`Wallet: ${walletAddr}`);

  const nativeBal = await p.getBalance(walletAddr);
  console.log(`\n  ${chain.nativeCurrency.padEnd(8)} ${ethers.formatEther(nativeBal)}`);

  // ERC-20 tokens via Multicall3 (single RPC call → no rate limit)
  const tokens = chain.tokens || {};
  const MC3 = chain.multicall3 || '0xcA11bde05977b3631167028862bE2a173976CA11';
  const MC3_ABI = ['function aggregate3(tuple(address target,bool allowFailure,bytes callData)[] calls) view returns (tuple(bool success,bytes returnData)[] returnData)'];
  const iface = new ethers.Interface(['function balanceOf(address) view returns (uint256)', 'function decimals() view returns (uint8)']);

  if (Object.keys(tokens).length > 0) {
    const entries = Object.entries(tokens);
    const calls = entries.flatMap(([, addr]) => [
      { target: addr, allowFailure: true, callData: iface.encodeFunctionData('decimals') },
      { target: addr, allowFailure: true, callData: iface.encodeFunctionData('balanceOf', [walletAddr]) },
    ]);

    try {
      const mc3 = new ethers.Contract(MC3, MC3_ABI, p);
      const results = await mc3.aggregate3(calls);
      for (let i = 0; i < entries.length; i++) {
        const [sym, addr] = entries[i];
        const decRes = results[i * 2];
        const balRes = results[i * 2 + 1];
        try {
          if (!decRes.success || !balRes.success) throw new Error('call failed');
          const dec = iface.decodeFunctionResult('decimals', decRes.returnData)[0];
          const bal = iface.decodeFunctionResult('balanceOf', balRes.returnData)[0];
          console.log(`  ${sym.padEnd(8)} ${ethers.formatUnits(bal, Number(dec)).padStart(20)}  (${addr})`);
        } catch {
          console.log(`  ${sym.padEnd(8)} ${'(error)'.padStart(20)}  (${addr})`);
        }
      }
    } catch (e) {
      // Multicall not available on this chain — fall back to sequential
      for (const [sym, addr] of entries) {
        try {
          const tok = new ethers.Contract(addr, ERC20_ABI, p);
          const dec = await tok.decimals();
          const bal = await tok.balanceOf(walletAddr);
          console.log(`  ${sym.padEnd(8)} ${ethers.formatUnits(bal, Number(dec)).padStart(20)}  (${addr})`);
        } catch {
          console.log(`  ${sym.padEnd(8)} ${'(error)'.padStart(20)}  (${addr})`);
        }
      }
    }
  }
}

// ── send (native) ─────────────────────────────────────────────────────────────
async function send() {
  const toRaw = process.argv[3], amount = process.argv[4];
  const to = toRaw ? addressBook.resolve(toRaw) : toRaw;
  if (!to || !amount) {
    console.log('Usage: wallet-manager [--chain <chain>] send <to> <amount>');
    process.exit(1);
  }

  const chain = getChain();
  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`❌ ${chain.name} factory not deployed.`); process.exit(1);
  }

  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);

  const [wBal, gBal] = await Promise.all([p.getBalance(walletAddr), p.getBalance(guardian)]);
  const sendAmt = ethers.parseEther(amount);

  if (wBal < sendAmt + MIN_WALLET_BAL) {
    console.log(`❌ Insufficient wallet balance on ${chain.name}.`);
    console.log(`   Have: ${ethers.formatEther(wBal)} ${chain.nativeCurrency}`);
    console.log(`   Need: ${ethers.formatEther(sendAmt + MIN_WALLET_BAL)} (incl. reserve)`);
    process.exit(1);
  }
  if (gBal < MIN_GUARDIAN_BAL) {
    console.log(`⚠️  Guardian (guardian.json) balance low: ${ethers.formatEther(gBal)} ETH — relay key may differ`);
  }

  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
  const nonce = await nonceManager.getNonce(p, walletAddr, chain.chainId, w);
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  console.log(`Sending ${amount} ${chain.nativeCurrency} on ${chain.name}`);
  console.log(`  From: ${walletAddr} → ${to}`);

  let txHash, receipt;
  try {
    txHash = await signAndSend(chain, walletAddr, to, sendAmt, '0x', nonce, deadline);
    console.log(`✅ TX: ${chain.explorer}/tx/${txHash}`);
    receipt = await p.waitForTransaction(txHash, 1, 120000);
    console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'} | Gas: ${receipt.gasUsed}`);
    txHistory.append({ chain: chain.key, type: 'send', from: walletAddr, to, amount, token: chain.nativeCurrency, txHash, status: receipt.status === 1 ? 'confirmed' : 'reverted', gasUsed: receipt.gasUsed.toString() });
  } catch (err) {
    txHistory.append({ chain: chain.key, type: 'send', from: walletAddr, to, amount, token: chain.nativeCurrency, txHash: txHash || 'n/a', status: 'failed' });
    throw err;
  } finally {
    nonceManager.confirm(walletAddr, chain.chainId);
  }
}

// ── send-token (ERC-20) ───────────────────────────────────────────────────────
async function sendToken() {
  const tokenArg = process.argv[3], toRaw = process.argv[4], amount = process.argv[5];
  const to = toRaw ? addressBook.resolve(toRaw) : toRaw;
  if (!tokenArg || !to || !amount) {
    console.log('Usage: wallet-manager [--chain <chain>] send-token <TOKEN|0xAddr> <to> <amount>');
    process.exit(1);
  }

  const chain = getChain();
  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`❌ ${chain.name} factory not deployed.`); process.exit(1);
  }

  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);

  const tokenAddr = resolveToken(chain, tokenArg);
  const tok = new ethers.Contract(tokenAddr, ERC20_ABI, p);
  const [sym, dec, bal] = await Promise.all([tok.symbol(), tok.decimals(), tok.balanceOf(walletAddr)]);
  const sendAmt = ethers.parseUnits(amount, dec);

  if (bal < sendAmt) {
    console.log(`❌ Insufficient ${sym} balance.`);
    console.log(`   Have: ${ethers.formatUnits(bal, dec)} ${sym}`);
    console.log(`   Need: ${amount} ${sym}`);
    process.exit(1);
  }

  const gBal = await p.getBalance(guardian);
  if (gBal < MIN_GUARDIAN_BAL) {
    console.log(`❌ Guardian balance too low. Top up: ${guardian}`); process.exit(1);
  }

  // Encode ERC-20 transfer(to, amount)
  const iface = new ethers.Interface(ERC20_ABI);
  const data = iface.encodeFunctionData('transfer', [to, sendAmt]);

  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
  const nonce = await nonceManager.getNonce(p, walletAddr, chain.chainId, w);
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  console.log(`Sending ${amount} ${sym} on ${chain.name}`);
  console.log(`  Token:  ${tokenAddr}`);
  console.log(`  From:   ${walletAddr} → ${to}`);

  let txHash, receipt;
  try {
    txHash = await signAndSend(chain, walletAddr, tokenAddr, 0n, data, nonce, deadline);
    console.log(`✅ TX: ${chain.explorer}/tx/${txHash}`);
    receipt = await p.waitForTransaction(txHash, 1, 120000);
    console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'} | Gas: ${receipt.gasUsed}`);
    txHistory.append({ chain: chain.key, type: 'send-token', from: walletAddr, to, amount, token: sym, txHash, status: receipt.status === 1 ? 'confirmed' : 'reverted', gasUsed: receipt.gasUsed.toString() });
  } catch (err) {
    txHistory.append({ chain: chain.key, type: 'send-token', from: walletAddr, to, amount, token: sym, txHash: txHash || 'n/a', status: 'failed' });
    throw err;
  } finally {
    nonceManager.confirm(walletAddr, chain.chainId);
  }
}

// ── compute-address ───────────────────────────────────────────────────────────
async function createWallet() {
  const { execSync } = require('child_process');
  const readline = require('readline');
  const ROOT = require('path').resolve(__dirname, '..');

  const chain = getChain();
  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`❌ Factory not deployed on ${chain.name}`); process.exit(1);
  }
  const { signer, guardian, logicHash } = await getAddresses();

  // ── Check for existing wallet on-chain ──
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const existingAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const existingCode = await p.getCode(existingAddr);
  if (existingCode.length > 2) {
    console.log(`⚠️  Wallet already exists on ${chain.name}: ${existingAddr}`);
    console.log('');
    console.log('Options:');
    console.log('  1) Keep existing wallet (exit)');
    console.log('  2) Reset signer & create new wallet (DESTROYS access to current wallet!)');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const answer = await new Promise(resolve => rl.question('\nChoice [1]: ', resolve));
    rl.close();
    if (answer.trim() === '2') {
      console.log('\n⚠️  Resetting signer key...\n');
      execSync(`bash ${ROOT}/scripts/provision.sh --reset <<< "yes"`, { stdio: 'inherit', shell: '/bin/bash' });
      console.log('\n🔄 Re-run create to deploy with new signer.\n');
      process.exit(0);
    } else {
      console.log(`\n✅ Keeping existing wallet: ${existingAddr}`);
      process.exit(0);
    }
  }
  const walletAddr = existingAddr;

  const guardianRec = ensureLocalGuardian();
  const gBal = await p.getBalance(guardian);
  if (gBal < MIN_GUARDIAN_BAL) {
    console.log(`❌ Guardian gas balance too low to deploy wallet.`);
    console.log('');
    console.log('┌─────────────────────────────────────────────────────────┐');
    console.log('│  💰 Please fund gas to the Guardian wallet:            │');
    console.log(`│  Address: ${guardian}  │`);
    console.log(`│  Current: ${ethers.formatEther(gBal)} ${chain.nativeCurrency}`.padEnd(58) + '│');
    console.log(`│  Need:    ~0.005 ${chain.nativeCurrency} (for deployment gas)`.padEnd(58) + '│');
    console.log('├─────────────────────────────────────────────────────────┤');
    console.log('│  🔑 Guardian Private Key (for import to external       │');
    console.log('│     wallet if needed):                                  │');
    console.log(`│  ${guardianRec.privateKey}  │`);
    console.log('├─────────────────────────────────────────────────────────┤');
    console.log('│  ℹ️  What is the Guardian?                              │');
    console.log('│  The Guardian is a gas relay wallet that pays for       │');
    console.log('│  on-chain transactions (deployment, swaps, sends).     │');
    console.log('│  It does NOT hold your assets — only gas fees.         │');
    console.log('│  Your AI wallet is a separate smart contract address.  │');
    console.log('└─────────────────────────────────────────────────────────┘');
    process.exit(1);
  }

  const nonce = ethers.hexlify(ethers.randomBytes(32));
  const entropy = ethers.hexlify(ethers.randomBytes(32));

  console.log(`Deploying wallet on ${chain.name} via V3 factory...`);
  console.log(`  Predicted wallet: ${walletAddr}`);
  console.log(`  Guardian (gas relay): ${guardian}`);
  console.log(`  Requesting blind commit + reveal proof from daemon...`);

  const binaryHash = logicHash;
  const innerHash = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(
    ['address', 'bytes32', 'address', 'bytes32'],
    [signer, binaryHash, guardian, nonce]
  ));
  const BLIND_TYPEHASH = ethers.keccak256(ethers.toUtf8Bytes('BlindCommit(bytes32 innerHash,bytes32 entropy)'));
  const blindHash = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(
    ['bytes32', 'bytes32', 'bytes32'],
    [BLIND_TYPEHASH, innerHash, entropy]
  ));

  // Pre-check: is this binary hash approved on the factory?
  const isApproved = await factory.approvedBinary(binaryHash);
  if (!isApproved) {
    console.log(`❌ Daemon binary not approved on ${chain.name} factory.`);
    console.log(`   Contact the factory owner to approve the current daemon build.`);
    process.exit(1);
  }

  const guardianKey = process.env.AAWP_GUARDIAN_KEY || process.env.AAWP_GAS_KEY || guardianRec.privateKey;
  if (!guardianKey) {
    console.log(`❌ Guardian signing key not set.`);
    process.exit(1);
  }

  const wallet = new ethers.Wallet(guardianKey, p);
  if (wallet.address.toLowerCase() !== guardian.toLowerCase()) {
    console.log(`❌ Guardian key/address mismatch.`);
    console.log(`   Expected guardian: ${guardian}`);
    console.log(`   Key resolves to   : ${wallet.address}`);
    process.exit(1);
  }
  const factoryWithSigner = factory.connect(wallet);

  const commitTx = await factoryWithSigner.commit(blindHash);
  console.log(`  Commit TX: ${chain.explorer}/tx/${commitTx.hash}`);
  const commitReceipt = await commitTx.wait(1);
  const commitBlock = commitReceipt.blockNumber;

  const delay = Number(await factory.REVEAL_DELAY());

  // NOTE: On Arbitrum, Solidity block.number = L1 block (~13s each), but
  // provider.getBlockNumber() = L2 block (~0.25s). Waiting by L2 count causes
  // commitStatus.revealable=false. Use wall-clock wait based on L1 time instead.
  const isArbitrum = chain.chainId === 42161;
  if (isArbitrum) {
    const waitMs = delay * 13000 + 5000; // L1 block ~12-13s each + 5s buffer
    process.stdout.write(`  Waiting ${delay} L1 blocks (~${Math.round(waitMs/1000)}s on Arbitrum)`);
    await new Promise(r => setTimeout(r, waitMs));
    process.stdout.write('\n');
  } else {
    process.stdout.write(`  Waiting ${delay} blocks`);
    while (true) {
      const current = await p.getBlockNumber();
      if (current >= commitBlock + delay) break;
      process.stdout.write('.');
      await new Promise(r => setTimeout(r, 2000));
    }
    process.stdout.write('\n');
  }
  process.stdout.write('\n');

  let committedAt = commitBlock;
  try {
    const status = await factory.commitStatus(blindHash);
    const committer = status[1];
    committedAt = Number(status[2]);
    const revealable = status[3];
    const expired = status[4];
    console.log(`  Commit owner: ${committer}`);
    console.log(`  Commit block: ${committedAt}`);
    if (committer.toLowerCase() !== wallet.address.toLowerCase()) {
      console.log(`❌ Commit owner mismatch.`);
      process.exit(1);
    }
    if (!revealable || expired) {
      console.log(`❌ Commit not revealable yet or expired.`);
      process.exit(1);
    }
  } catch (_) {
    console.log('  commitStatus decode mismatch — fallback to commit receipt block');
  }

  console.log('  Waiting signer cooldown...');
  await new Promise(r => setTimeout(r, 31000));

  const DOMAIN_TYPEHASH = ethers.keccak256(ethers.toUtf8Bytes('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)'));
  const CREATE_TYPEHASH = ethers.keccak256(ethers.toUtf8Bytes('CreateWallet(address aiSigner,bytes32 binaryHash,address guardian,bytes32 nonce,bytes32 entropy,uint256 commitBlock)'));
  const domainSeparator = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(
    ['bytes32', 'bytes32', 'bytes32', 'uint256', 'address'],
    [
      DOMAIN_TYPEHASH,
      ethers.keccak256(ethers.toUtf8Bytes('AAWPFactory')),
      ethers.keccak256(ethers.toUtf8Bytes('3')),
      chain.chainId,
      chain.factory,
    ]
  ));
  const structHash = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(
    ['bytes32', 'address', 'bytes32', 'address', 'bytes32', 'bytes32', 'uint256'],
    [CREATE_TYPEHASH, signer, binaryHash, guardian, nonce, entropy, committedAt]
  ));
  const digest = ethers.keccak256(ethers.solidityPacked(['bytes2', 'bytes32', 'bytes32'], ['0x1901', domainSeparator, structHash]));
  const proofResult = await socketQuery({ cmd: 'sign_hash', hash: digest.replace(/^0x/, '') });
  if (proofResult.error || !proofResult.signature) {
    console.log(`❌ Proof generation failed: ${proofResult.error || 'missing signature'}`);
    process.exit(1);
  }
  const proof = proofResult.signature;

  const revealTx = await factoryWithSigner.reveal(signer, binaryHash, guardian, nonce, entropy, proof);
  console.log(`  Reveal TX: ${chain.explorer}/tx/${revealTx.hash}`);
  const receipt = await revealTx.wait(1);
  console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'}`);

  for (const log of receipt.logs) {
    try {
      const parsed = factory.interface.parseLog(log);
      if (parsed && parsed.name === 'WalletCreated') {
        console.log(`  🆔 SBT Token ID: ${parsed.args.tokenId}`);
      }
    } catch (_) {}
  }
  await status();

  // ── Auto-backup on wallet creation ────────────────────────────────────────
  console.log('\n');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  🔐 AUTO-BACKUP — CRITICAL SECURITY NOTICE                  ║');
  console.log('╠══════════════════════════════════════════════════════════════╣');
  console.log('║  Your wallet was just created. An automatic backup is       ║');
  console.log('║  being generated now.                                        ║');
  console.log('║                                                              ║');
  console.log('║  ⚠️  THE BACKUP FILE = YOUR WALLET.                         ║');
  console.log('║  Anyone with this file can restore and control your         ║');
  console.log('║  on-chain wallet. Treat it like a private key.              ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('');

  let backupResult;
  try {
    const ROOT = require('path').resolve(__dirname, '..');
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    // Save backup temporarily in /tmp to make it explicit it must be moved
    process.argv[3] = `/tmp/aawp-backup-${today}-${Date.now()}.tar.gz`;
    backupResult = await backup();
  } catch (e) {
    console.log(`\n❌ Auto-backup FAILED: ${e.message}`);
    console.log('   ⚠️  Please run backup manually IMMEDIATELY:');
    console.log('   node scripts/wallet-manager.js backup ./my-backup.tar.gz');
    return;
  }

  console.log('');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║  📦 BACKUP CREATED — ACTION REQUIRED                        ║');
  console.log('╠══════════════════════════════════════════════════════════════╣');
  console.log(`║  File   : ${backupResult.outPath.padEnd(51)}║`);
  console.log(`║  SHA256 : ${backupResult.sha.padEnd(51)}║`);
  console.log('╠══════════════════════════════════════════════════════════════╣');
  console.log('║  NEXT STEPS (do this NOW):                                  ║');
  console.log('║  1. Download this file to your local machine (SCP/SFTP)     ║');
  console.log('║  2. Verify the SHA256 matches after download                ║');
  console.log('║  3. Store it in a safe place (encrypted drive, cold storage)║');
  console.log('║  4. The server copy will now be DELETED for your security   ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`  SCP command:  scp root@<server>:${backupResult.outPath} ./aawp-wallet-backup.tar.gz`);
  console.log('');

  // Wait for user confirmation before deleting server backup
  const rl2 = require('readline').createInterface({ input: process.stdin, output: process.stdout });
  const confirm = await new Promise(resolve =>
    rl2.question('  ✅ Type YES to confirm you have downloaded the backup and delete the server copy: ', resolve)
  );
  rl2.close();

  if (confirm.trim().toUpperCase() === 'YES') {
    try {
      fs.unlinkSync(backupResult.outPath);
      console.log('🗑️  Server copy deleted. The backup only exists on YOUR local machine now.');
    } catch (e) {
      console.log(`⚠️  Could not delete server copy: ${e.message}`);
      console.log(`   Please delete manually: rm "${backupResult.outPath}"`);
    }
  } else {
    console.log(`⚠️  Skipped deletion. Backup still on server at: ${backupResult.outPath}`);
    console.log('   Delete it manually once you have a local copy:');
    console.log(`   rm "${backupResult.outPath}"`);
  }
  console.log('');
}

async function computeAddr() {
  const { signer, guardian, logicHash } = await getAddresses();
  console.log('=== Stable Wallet Address Prediction ===');
  console.log('Guardian:', guardian);
  console.log('');
  for (const [key, cfg] of Object.entries(CHAINS)) {
    if (!cfg.deployed || cfg.factory === ethers.ZeroAddress) {
      console.log(`  [${key.toUpperCase().padEnd(8)}] Factory not deployed — address: TBD`);
      continue;
    }
    try {
      const p = new ethers.JsonRpcProvider(cfg.rpc);
      const factory = new ethers.Contract(cfg.factory, FACTORY_ABI, p);
      const addr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
      const code = await p.getCode(addr);
      const live = code.length > 2;
      console.log(`  [${key.toUpperCase().padEnd(8)}] ${addr} ${live ? '✅' : '⬜'}`);
    } catch (e) {
      console.log(`  [${key.toUpperCase().padEnd(8)}] Error: ${e.message}`);
    }
  }
}

// ── upgrade-signer ────────────────────────────────────────────────────────────
async function upgradeSigner() {
  const chain = getChain();
  if (!chain.deployed || chain.factory === ethers.ZeroAddress) {
    console.log(`❌ ${chain.name} factory not deployed.`); process.exit(1);
  }

  const { signer, guardian, logicHash } = await getAddresses();
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const code = await p.getCode(walletAddr);
  if (code.length <= 2) {
    console.log(`❌ Wallet not deployed at ${walletAddr}`); process.exit(1);
  }

  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
  const [currentSigner, currentLogic] = await Promise.all([w.aiSigner(), w.logicHash()]);

  console.log('Current signer:', currentSigner);
  console.log('New signer    :', signer);
  console.log('New logicHash :', logicHash);

  if (currentSigner.toLowerCase() === signer.toLowerCase() && currentLogic === logicHash) {
    console.log('✅ Already up to date.'); return;
  }

  const iface = new ethers.Interface(WALLET_ABI);
  const data = iface.encodeFunctionData('upgradeAiSigner', [signer, logicHash]);
  const nonce = await w.nonce();
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  console.log(`Upgrading signer on ${chain.name}...`);
  const txHash = await signAndSend(chain, walletAddr, walletAddr, 0n, data, nonce, deadline);
  console.log(`✅ TX: ${chain.explorer}/tx/${txHash}`);
  const receipt = await p.waitForTransaction(txHash, 1, 120000);
  console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'}`);
}

// ── swap (same-chain) ─────────────────────────────────────────────────────────
async function swapCmd() {
  const fromToken = process.argv[3], toToken = process.argv[4], amount = process.argv[5];
  if (!fromToken || !toToken || !amount) {
    console.log('Usage: wallet-manager [--chain <chain>] swap <fromToken> <toToken> <amount>');
    console.log('  e.g. wallet-manager --chain base swap ETH USDC 0.01');
    process.exit(1);
  }
  const chain = getChain();
  await swapModule.swap(chain.key, fromToken, toToken, amount, null, slippageBps);
}

// ── bridge (cross-chain) ──────────────────────────────────────────────────────
async function bridgeCmd() {
  const fromChain = process.argv[3], toChain = process.argv[4];
  const fromToken = process.argv[5], toToken = process.argv[6], amount = process.argv[7];
  const recipient = bridgeRecipient;
  if (!fromChain || !toChain || !fromToken || !toToken || !amount) {
    console.log('Usage: wallet-manager bridge <fromChain> <toChain> <fromToken> <toToken> <amount> [--to <recipient>]');
    console.log('  e.g. wallet-manager bridge base arb ETH ETH 0.05');
    console.log('  e.g. wallet-manager bridge base eth USDC USDC 100');
    console.log('  e.g. wallet-manager bridge base bsc ETH BNB 0.001 --to 0xRecipient');
    process.exit(1);
  }
  await swapModule.bridge(fromChain, toChain, fromToken, toToken, amount, slippageBps, recipient);
}

// ── quote (no execution) ──────────────────────────────────────────────────────
async function quoteCmd() {
  const fromChain = process.argv[3], toChain = process.argv[4];
  const fromToken = process.argv[5], toToken = process.argv[6], amount = process.argv[7];
  // Also support same-chain: wallet-manager --chain base quote ETH USDC 0.01
  if (!fromToken) {
    console.log('Usage: wallet-manager quote <fromChain> <toChain> <fromToken> <toToken> <amount>');
    console.log('   or: wallet-manager [--chain base] quote <fromToken> <toToken> <amount>  (same-chain)');
    process.exit(1);
  }
  if (toToken && amount) {
    // cross-chain form
    await swapModule.quoteOnly(fromChain, toChain, fromToken, toToken, amount);
  } else {
    // same-chain form: fromChain=fromToken, toChain=toToken, fromToken=amount
    const chain = getChain();
    await swapModule.quoteOnly(chain.key, chain.key, fromChain, toChain, fromToken);
  }
}

// ── guardian-chains ─────────────────────────────────────────────────────────────
async function guardianChainsCmd() {
  await swapModule.listChains();
}

// ── set-rpc ───────────────────────────────────────────────────────────────────
// Persist a custom RPC for a chain. Pass "" or "default" to reset.
function setRpc() {
  const key = (chainArg || DEFAULT_CHAIN).toLowerCase();
  const url = process.argv[3];
  if (!url) {
    console.log(`Usage: wallet-manager --chain <chain> set-rpc <url|default>`);
    console.log(`       wallet-manager --chain base set-rpc https://base-mainnet.g.alchemy.com/v2/YOUR_KEY`);
    process.exit(1);
  }
  if (!CHAINS[key]) {
    console.error(`❌ Unknown chain: ${key}`); process.exit(1);
  }
  const reset = url === 'default' || url === '';
  CHAINS[key].rpcOverride = reset ? null : url;
  saveChains();
  if (reset) {
    console.log(`✅ [${key.toUpperCase()}] RPC reset to default: ${CHAINS[key].rpc}`);
  } else {
    console.log(`✅ [${key.toUpperCase()}] Custom RPC saved: ${url}`);
    console.log(`   Default was: ${CHAINS[key].rpc}`);
  }
}

// ── get-rpc ───────────────────────────────────────────────────────────────────
function getRpc() {
  console.log('=== RPC Configuration ===');
  for (const [key, cfg] of Object.entries(CHAINS)) {
    const active = cfg.rpcOverride || cfg.rpc;
    const isCustom = !!cfg.rpcOverride;
    const tag = isCustom ? '🔧 custom' : '   default';
    console.log(`  ${key.toUpperCase().padEnd(8)} [${tag}] ${active}`);
    if (isCustom) console.log(`  ${''.padEnd(8)}           (default: ${cfg.rpc})`);
  }
  console.log('\nSet custom: wallet-manager --chain <chain> set-rpc <url>');
  console.log('Reset:      wallet-manager --chain <chain> set-rpc default');
  console.log('One-shot:   wallet-manager --chain <chain> --rpc <url> status');
}

// ── backup ────────────────────────────────────────────────────────────────────
async function backup() {
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const outPath = process.argv[3] || `./aawp-backup-${today}.tar.gz`;

  // Collect files into a staging dir with portable structure
  const staging = `/tmp/aawp-backup-stage-${Date.now()}`;
  fs.mkdirSync(staging, { recursive: true });

  const copyTo = (src, relDst) => {
    if (!fs.existsSync(src)) return false;
    const dst = path.join(staging, relDst);
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(src, dst);
    return true;
  };

  let count = 0;
  // Core shards & keys (portable relative paths)
  if (copyTo(path.join(C, 'seed.enc'),              'agent-config/seed.enc'))       count++;
  if (copyTo(path.join(S, 'core/aawp-core.node'),   'core/aawp-core.node'))         count++;
  if (copyTo('/var/lib/aawp/.cache/fonts.idx',       'system/fonts.idx'))            count++;
  if (copyTo('/etc/machine-id',                      'system/machine-id'))           count++;
  if (copyTo('/var/lib/aawp/host.salt',              'system/host.salt'))            count++;
  if (copyTo(path.join(S, 'config/guardian.json'),   'config/guardian.json'))         count++;

  // Walk .agent-config dir for any additional files
  if (fs.existsSync(C)) {
    const walk = (dir, rel) => {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, e.name);
        const r = path.join(rel, e.name);
        if (e.isDirectory()) walk(full, r);
        else if (copyTo(full, path.join('agent-config', r))) count++;
      }
    };
    walk(C, '');
  }

  if (count === 0) { console.log('❌ No files to backup.'); process.exit(1); }

  // Write manifest with metadata
  const manifest = {
    version: 2,
    createdAt: new Date().toISOString(),
    skillDir: S,
    configDir: C,
    platform: process.platform,
    arch: process.arch,
  };
  fs.writeFileSync(path.join(staging, 'manifest.json'), JSON.stringify(manifest, null, 2));

  execSync(`tar czf "${path.resolve(outPath)}" -C "${staging}" .`, { stdio: 'inherit' });
  execSync(`rm -rf "${staging}"`);

  const sha = execSync(`sha256sum "${outPath}" | cut -d' ' -f1`).toString().trim();
  console.log('✅ Backup:', outPath);
  console.log('   Files :', count);
  console.log('   SHA256:', sha);
  console.log('\nRestore with: wallet-manager restore', outPath);
  return { outPath: path.resolve(outPath), sha };
}

// ── restore ───────────────────────────────────────────────────────────────────
// Handled by restore-impl.js (early exit at module load, before addon require)

// ── history ────────────────────────────────────────────────────────────────────
async function historyCmd() {
  // Parse inline flags from remaining args
  const args = process.argv.slice(3);
  let limit = 20, hChain = null, hType = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--limit' && args[i+1]) { limit = parseInt(args[++i], 10); }
    else if (args[i] === '--chain' && args[i+1]) { hChain = args[++i]; }
    else if (args[i] === '--type' && args[i+1]) { hType = args[++i]; }
  }
  const entries = txHistory.query({ chain: hChain || (chainArg || undefined), limit, type: hType });
  if (entries.length === 0) { console.log('No transaction history found.'); return; }
  console.log('Time                     | Chain    | Type       | Amount          | TX Hash      | Status');
  console.log('-'.repeat(100));
  for (const e of entries) {
    const ts = (e.ts ? new Date(e.ts).toISOString().slice(0, 19) : '').padEnd(24);
    const chain = (e.chain || '').padEnd(8);
    const type = (e.type || '').padEnd(10);
    const amt = `${e.amount || '?'} ${e.token || ''}`.padEnd(15);
    const hash = (e.txHash || '').slice(0, 12) + '...';
    const status = e.status || '?';
    console.log(`${ts} | ${chain} | ${type} | ${amt} | ${hash} | ${status}`);
  }
}

// ── approve / allowance / revoke ──────────────────────────────────────────────
async function approveCmd() {
  const tokenArg = process.argv[3], spender = process.argv[4], amount = process.argv[5];
  if (!tokenArg || !spender || !amount) {
    console.log('Usage: wallet-manager [--chain <chain>] approve <token> <spender> <amount>'); process.exit(1);
  }
  const chain = getChain();
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const tokenAddr = resolveToken(chain, tokenArg);
  const tok = new ethers.Contract(tokenAddr, ERC20_ABI, p);
  const [sym, dec] = await Promise.all([tok.symbol(), tok.decimals()]);
  const amtWei = ethers.parseUnits(amount, dec);
  const iface = new ethers.Interface(ERC20_ABI);
  const data = iface.encodeFunctionData('approve', [spender, amtWei]);
  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
  const nonce = await nonceManager.getNonce(p, walletAddr, chain.chainId, w);
  const deadline = Math.floor(Date.now() / 1000) + 3600;
  console.log(`Approving ${amount} ${sym} for ${spender} on ${chain.name}`);
  try {
    const txHash = await signAndSend(chain, walletAddr, tokenAddr, 0n, data, nonce, deadline);
    console.log(`✅ TX: ${chain.explorer}/tx/${txHash}`);
    const receipt = await p.waitForTransaction(txHash, 1, 120000);
    console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'}`);
  } finally { nonceManager.confirm(walletAddr, chain.chainId); }
}

async function allowanceCmd() {
  const tokenArg = process.argv[3], spender = process.argv[4];
  if (!tokenArg || !spender) {
    console.log('Usage: wallet-manager [--chain <chain>] allowance <token> <spender>'); process.exit(1);
  }
  const chain = getChain();
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const tokenAddr = resolveToken(chain, tokenArg);
  const tok = new ethers.Contract(tokenAddr, ERC20_ABI, p);
  const [sym, dec, allowance] = await Promise.all([tok.symbol(), tok.decimals(), tok.allowance(walletAddr, spender)]);
  console.log(`${sym} allowance for ${spender}: ${ethers.formatUnits(allowance, dec)} ${sym}`);
}

async function revokeCmd() {
  // Revoke = approve 0
  process.argv[5] = '0';
  if (!process.argv[3] || !process.argv[4]) {
    console.log('Usage: wallet-manager [--chain <chain>] revoke <token> <spender>'); process.exit(1);
  }
  await approveCmd();
}

// ── batch (multicall) ─────────────────────────────────────────────────────────
async function batchCmd() {
  const jsonFile = process.argv[3];
  if (!jsonFile) { console.log('Usage: wallet-manager [--chain <chain>] batch <calls.json>'); process.exit(1); }
  if (!fs.existsSync(jsonFile)) { console.log(`❌ File not found: ${jsonFile}`); process.exit(1); }
  const calls = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));
  const chain = getChain();
  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);

  const txHash = await batchExecute(calls, walletAddr, chain, socketQuery, async () => {
    return nonceManager.getNonce(p, walletAddr, chain.chainId, w);
  });
  console.log(`✅ Batch TX: ${chain.explorer}/tx/${txHash}`);
  const receipt = await p.waitForTransaction(txHash, 1, 120000);
  console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'} | Gas: ${receipt.gasUsed}`);
  nonceManager.confirm(walletAddr, chain.chainId);
}

async function portfolio() {
  const https = require('https');
  const targetChain = chainArg ? chainArg.toLowerCase() : null;

  // CoinGecko symbol → id mapping
  const SYM_TO_GECKO = {
    ETH: 'ethereum', WETH: 'ethereum', BNB: 'binancecoin', MATIC: 'matic-network',
    USDC: 'usd-coin', USDT: 'tether', DAI: 'dai',
  };

  // Fetch USD prices from CoinGecko
  let prices = {};
  try {
    const ids = [...new Set(Object.values(SYM_TO_GECKO))].join(',');
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd`;
    prices = await new Promise((resolve, reject) => {
      https.get(url, { headers: { 'User-Agent': 'AAWP/1.0' }, timeout: 10000 }, (res) => {
        let d = '';
        res.on('data', c => d += c);
        res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({}); } });
      }).on('error', () => resolve({}));
    });
  } catch { /* proceed without prices */ }

  function getUsd(sym) {
    const id = SYM_TO_GECKO[sym.toUpperCase()];
    return id && prices[id] ? prices[id].usd : 0;
  }

  const { signer, guardian, logicHash } = await getAddresses();
  const rows = [];
  let totalUsd = 0;

  const chainsToCheck = targetChain ? { [targetChain]: CHAINS[targetChain] } : CHAINS;

  for (const [key, cfg] of Object.entries(chainsToCheck)) {
    if (!cfg || !cfg.deployed || cfg.factory === ethers.ZeroAddress) continue;
    try {
      const p = new ethers.JsonRpcProvider(cfg.rpcOverride || cfg.rpc);
      const factory = new ethers.Contract(cfg.factory, FACTORY_ABI, p);
      const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);
      const code = await p.getCode(walletAddr);
      if (code.length <= 2) continue;

      // Native balance
      const nativeBal = await p.getBalance(walletAddr);
      const nativeNum = parseFloat(ethers.formatEther(nativeBal));
      const nativeUsd = nativeNum * getUsd(cfg.nativeCurrency);
      rows.push({ chain: key.toUpperCase(), token: cfg.nativeCurrency, balance: nativeNum.toFixed(6), usd: nativeUsd });
      totalUsd += nativeUsd;

      // ERC-20 tokens
      for (const [sym, addr] of Object.entries(cfg.tokens || {})) {
        try {
          const tok = new ethers.Contract(addr, ERC20_ABI, p);
          const [bal, dec] = await Promise.all([tok.balanceOf(walletAddr), tok.decimals()]);
          const num = parseFloat(ethers.formatUnits(bal, dec));
          const usd = num * getUsd(sym);
          rows.push({ chain: key.toUpperCase(), token: sym, balance: num.toFixed(6), usd });
          totalUsd += usd;
        } catch {
          rows.push({ chain: key.toUpperCase(), token: sym, balance: 'error', usd: 0 });
        }
      }
    } catch (e) {
      console.log(`  ⚠️  ${key}: ${e.message}`);
    }
  }

  console.log('\n=== AAWP Portfolio ===');
  console.log(`${'Chain'.padEnd(10)}${'Token'.padEnd(8)}${'Balance'.padStart(18)}${'USD Value'.padStart(14)}`);
  for (const r of rows) {
    const usdStr = r.balance === 'error' ? '—' : `$${r.usd.toFixed(2)}`;
    console.log(`${r.chain.padEnd(10)}${r.token.padEnd(8)}${String(r.balance).padStart(18)}${usdStr.padStart(14)}`);
  }
  console.log('─'.repeat(50));
  console.log(`${'Total'.padEnd(36)}${'$' + totalUsd.toFixed(2)}`);
}

// ── call (contract interaction) ───────────────────────────────────────────────
async function callContract() {
  // Parse: call [--value <eth>] [--abi <file>] [--gas-limit <n>] <to> <methodSig> [args...]
  const args = process.argv.slice(3);
  let valueSend = '0', abiFile = null, gasLimitOverride = null;
  const posArgs = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--value'     && args[i+1]) { valueSend        = args[++i]; continue; }
    if (args[i] === '--abi'       && args[i+1]) { abiFile          = args[++i]; continue; }
    if (args[i] === '--gas-limit' && args[i+1]) { gasLimitOverride = args[++i]; continue; }
    posArgs.push(args[i]);
  }

  const toRaw = posArgs[0], methodSig = posArgs[1];
  const callArgs = posArgs.slice(2);
  if (!toRaw || !methodSig) {
    console.log('Usage: wallet-manager [--chain <chain>] call [--value <eth>] [--abi <file>] <to> <methodSig> [args...]');
    console.log('  e.g. wallet-manager call 0xABC... "transfer(address,uint256)" 0xDEF... 1000000');
    process.exit(1);
  }

  const to = addressBook.resolve(toRaw);
  const chain = getChain();
  if (!chain.deployed) { console.log(`❌ ${chain.name} not deployed.`); process.exit(1); }

  const p = new ethers.JsonRpcProvider(chain.rpc);
  const { signer, guardian, logicHash } = await getAddresses();
  const factory = new ethers.Contract(chain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, logicHash, guardian);

  // Build calldata
  let data;
  if (methodSig.startsWith('0x')) {
    // Raw calldata mode — methodSig IS the hex data
    data = methodSig;
    console.log(`Raw calldata (${data.length} chars)`);
  } else {
    let iface, fragment;
    if (abiFile) {
      const abi = JSON.parse(fs.readFileSync(abiFile, 'utf8'));
      const abiArr = abi.abi || abi;
      iface = new ethers.Interface(abiArr);
      fragment = iface.getFunction(methodSig);
    } else {
      iface = new ethers.Interface([`function ${methodSig}`]);
      fragment = iface.fragments[0];
    }

    // Auto-cast arguments
    const typedArgs = fragment.inputs.map((inp, i) => {
      const raw = callArgs[i] || '0';
      if (inp.type === 'bool') return raw === 'true';
      if (inp.type.startsWith('uint') || inp.type.startsWith('int')) return BigInt(raw);
      return raw;
    });

    data = iface.encodeFunctionData(fragment, typedArgs);
  }
  const value = ethers.parseEther(valueSend);

  const w = new ethers.Contract(walletAddr, WALLET_ABI, p);
  const nonce = await w.nonce();
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  console.log(`Calling ${to}${methodSig.startsWith('0x') ? ' (raw)' : '.' + fragment.name + '(' + callArgs.join(', ') + ')'}`);
  if (value > 0n) console.log(`  Value: ${valueSend} ${chain.nativeCurrency}`);

  const txHash = await signAndSend(chain, walletAddr, to, value, data, nonce, deadline, gasLimitOverride);
  console.log(`✅ TX: ${chain.explorer}/tx/${txHash}`);
  const receipt = await p.waitForTransaction(txHash, 1, 120000);
  console.log(`Status: ${receipt.status === 1 ? 'confirmed ✅' : 'REVERTED ❌'} | Gas: ${receipt.gasUsed}`);
}

// ── read (view/pure contract call) ────────────────────────────────────────────
async function readContract() {
  const args = process.argv.slice(3);
  const posArgs = [];
  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith('--')) posArgs.push(args[i]);
  }

  const toRaw = posArgs[0], methodSig = posArgs[1];
  const callArgs = posArgs.slice(2);
  if (!toRaw || !methodSig) {
    console.log('Usage: wallet-manager [--chain <chain>] read <to> <methodSig> [args...]');
    process.exit(1);
  }

  const to = addressBook.resolve(toRaw);
  const chain = getChain();
  const p = new ethers.JsonRpcProvider(chain.rpc);

  // Auto-detect return type: if sig has "returns" use as-is, else default string for display
  const fullSig = methodSig.includes('returns')
    ? `function ${methodSig}`
    : `function ${methodSig} returns (bytes)`;
  const iface = new ethers.Interface([fullSig]);
  const fragment = iface.fragments[0];

  const typedArgs = fragment.inputs.map((inp, i) => {
    const raw = callArgs[i] || '0';
    if (inp.type === 'bool') return raw === 'true';
    if (inp.type.startsWith('uint') || inp.type.startsWith('int')) return BigInt(raw);
    return raw;
  });

  const data = iface.encodeFunctionData(fragment, typedArgs);
  const result = await p.call({ to, data });

  // Try to decode — if returns bytes fallback, try utf8 string decode
  try {
    const decoded = iface.decodeFunctionResult(fragment, result);
    const fmt = (v) => {
      if (typeof v === 'bigint') return v.toString();
      if (v instanceof Uint8Array || (typeof v === 'string' && v.startsWith('0x'))) {
        try { return ethers.toUtf8String(v); } catch { return v.toString(); }
      }
      return v.toString();
    };
    console.log('Result:', decoded.length === 1 ? fmt(decoded[0]) : decoded.map(fmt));
  } catch {
    // last resort: try utf8 decode of raw bytes
    try { console.log('Result:', ethers.toUtf8String(result)); }
    catch { console.log('Raw result:', result); }
  }
}

// ── addr (address book) ───────────────────────────────────────────────────────
function addrCmd() {
  const sub = process.argv[3];
  switch (sub) {
    case 'add': {
      const name = process.argv[4], address = process.argv[5];
      if (!name || !address) { console.log('Usage: wallet-manager addr add <name> <address>'); process.exit(1); }
      const resolved = addressBook.add(name, address);
      console.log(`✅ Added: ${name} → ${resolved}`);
      break;
    }
    case 'list': {
      const entries = addressBook.list();
      const keys = Object.keys(entries);
      if (keys.length === 0) { console.log('Address book is empty.'); return; }
      console.log('=== Address Book ===');
      for (const [name, addr] of Object.entries(entries)) {
        console.log(`  ${name.padEnd(20)} ${addr}`);
      }
      break;
    }
    case 'remove': {
      const name = process.argv[4];
      if (!name) { console.log('Usage: wallet-manager addr remove <name>'); process.exit(1); }
      if (addressBook.remove(name)) console.log(`✅ Removed: ${name}`);
      else console.log(`❌ Not found: ${name}`);
      break;
    }
    case 'get': {
      const name = process.argv[4];
      if (!name) { console.log('Usage: wallet-manager addr get <name>'); process.exit(1); }
      const addr = addressBook.get(name);
      console.log(addr || `❌ Not found: ${name}`);
      break;
    }
    default:
      console.log('Usage: wallet-manager addr <add|list|remove|get> [args]');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════════

async function main() {
  const cmd = process.argv[2];

  const chains = Object.keys(CHAINS).join('|');
  const help = `
Usage: wallet-manager [--chain <chain>] [--rpc <url>] [--slippage <bps>] <command> [args]
       wallet-manager status [--all]

Commands:
  status              Wallet status (active chain or --all)
  balance             Native + ERC-20 balances
  send <to> <amt>     Send native currency
  send-token <TKN|addr> <to> <amt>  Send ERC-20
  swap <from> <to> <amt>   Same-chain swap via Relay (e.g. ETH → USDC)
  bridge <fc> <tc> <ft> <tt> <amt>  Cross-chain bridge via Relay [--to <recipient>]
  quote  <fc> <tc> <ft> <tt> <amt>  Get quote without executing
  guardian-chains             List all Supported chains
  approve <token> <spender> <amt>   Set ERC-20 approval
  allowance <token> <spender>       Query current allowance
  revoke <token> <spender>          Revoke approval (set to 0)
  history [--limit N] [--type swap|send]  Transaction history
  batch <calls.json>       Multicall batch execution
  compute-address     Predict wallet address on all chains
  upgrade-signer      Update aiSigner after binary upgrade
  portfolio           Show balances + USD values across all chains
  call <to> <sig> [args]   Call a contract method (state-changing)
  read <to> <sig> [args]   Read-only contract call (view/pure)
  addr add|list|remove|get  Manage address book
  get-rpc             Show active RPC for all chains
  set-rpc <url>       Persist custom RPC for --chain (use "default" to reset)
  backup [path]       Export seed/config bundle
  restore <path>      Import from backup bundle

Flags:
  --chain <chain>     Target chain (default: ${DEFAULT_CHAIN})
  --slippage <bps>    Slippage tolerance in basis points (default: 50 = 0.5%)
  --rpc <url>         One-shot RPC override

Chains: ${chains}
`;

  switch (cmd) {
    case 'status':          await status(); break;
    case 'balance':         await balance(); break;
    case 'send':            await send(); break;
    case 'send-token':      await sendToken(); break;
    case 'create':          await createWallet(); break;
    case 'compute-address': await computeAddr(); break;
    case 'upgrade-signer':  await upgradeSigner(); break;
    case 'swap':            await swapCmd(); break;
    case 'bridge':          await bridgeCmd(); break;
    case 'quote':           await quoteCmd(); break;
    case 'guardian-chains':    await guardianChainsCmd(); break;
    case 'get-rpc':         getRpc(); break;
    case 'set-rpc':         setRpc(); break;
    case 'approve':         await approveCmd(); break;
    case 'allowance':       await allowanceCmd(); break;
    case 'revoke':          await revokeCmd(); break;
    case 'history':         await historyCmd(); break;
    case 'batch':           await batchCmd(); break;
    case 'backup':          await backup(); break;
    case 'restore':         await restore(); break;
    case 'portfolio':       await portfolio(); break;
    case 'call':            await callContract(); break;
    case 'read':            await readContract(); break;
    case 'addr':            addrCmd(); break;
    default:
      console.log(help);
      if (cmd) console.log(`Unknown command: ${cmd}`);
  }
}

main().catch(e => {
  const msg = String(e && e.message ? e.message : e);
  if (msg.includes('E_AI_GATE') || msg.includes('hmac_mismatch')) {
    console.error('❌ Daemon state mismatch — run: scripts/restart-daemon.sh (from skill directory)');
  } else if (msg.includes('GenericFailure') || msg.includes('E00')) {
    console.error('❌ Signer seed/config error — check .agent-config and shard files first');
  } else {
    console.error('❌', msg);
  }
  process.exit(1);
});
