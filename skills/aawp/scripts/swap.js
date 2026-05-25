#!/usr/bin/env node
/**
 * AAWP Swap — Relay Bridge integration
 * Supports: same-chain swap + cross-chain bridge across 6 chains
 *
 * Usage (standalone):
 *   node swap.js [--chain <chain>] [--rpc <url>] swap <fromToken> <toToken> <amount>
 *   node swap.js bridge <fromChain> <toChain> <fromToken> <toToken> <amount>
 *   node swap.js quote <fromChain> <toChain> <fromToken> <toToken> <amount>
 *   node swap.js chains    — list supported chains on Relay
 *
 * Or via wallet-manager:
 *   wallet-manager [--chain base] swap ETH USDC 0.01
 *   wallet-manager bridge base arb ETH ETH 0.01
 *   wallet-manager quote  base arb USDC USDC 100
 */
'use strict';

const net  = require('net');
const path = require('path');
const fs   = require('fs');
const https = require('https');

// ── Shared setup (also used when required from wallet-manager) ────────────────
const addon = require(process.env.AAWP_CORE || require('path').join(__dirname, '..', 'core', 'aawp-core.node'));
const C = process.env.AAWP_CONFIG || require('path').join(__dirname, '..', '.agent-config');
const S = process.env.AAWP_SKILL || require('path').resolve(__dirname, '..');

const CHAINS_FILE = path.join(S, 'config/chains.json');
const CHAINS = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));

// ── Relay API ─────────────────────────────────────────────────────────────────
const nonceManager = require(path.join(__dirname, '../lib/nonce-manager'));
const { getGasPrice: getGasPriceEstimate } = require(path.join(__dirname, '../lib/gas-estimator'));
const txHistory = require(path.join(__dirname, '../lib/tx-history'));

const RELAY_API  = 'https://api.relay.link';
const RELAY_TIMEOUT = 30000;

// Native token placeholder
const NATIVE = '0x0000000000000000000000000000000000000000';

// Chain ID map
const CHAIN_IDS = Object.fromEntries(
  Object.entries(CHAINS).map(([k, v]) => [k, v.chainId])
);

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Simple HTTPS fetch → JSON */
function relayFetch(method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const url = new URL(RELAY_API + urlPath);
    const opts = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'AAWP/1.0',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
      timeout: RELAY_TIMEOUT,
    };
    const req = https.request(opts, (res) => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => {
        try { resolve(JSON.parse(raw)); }
        catch (e) { reject(new Error(`Relay parse error: ${raw.slice(0, 200)}`)); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Relay API timeout')); });
    if (data) req.write(data);
    req.end();
  });
}

/** Resolve token symbol → contract address for a given chain key */
function resolveToken(chainKey, tokenArg) {
  if (tokenArg === 'ETH' || tokenArg === 'BNB' || tokenArg === 'MATIC' ||
      tokenArg.toLowerCase() === 'native' || tokenArg === '0x0') {
    return NATIVE;
  }
  if (tokenArg.startsWith('0x') && tokenArg.length === 42) return tokenArg;
  const cfg = CHAINS[chainKey];
  const sym = tokenArg.toUpperCase();
  if (cfg?.tokens?.[sym]) return cfg.tokens[sym];
  throw new Error(`Unknown token "${tokenArg}" on ${chainKey}. Use address or: ${Object.keys(cfg?.tokens || {}).join(', ')}, native`);
}

/** Get the active RPC for a chain (respects rpcOverride) */
function chainRpc(chainKey) {
  const cfg = CHAINS[chainKey];
  return cfg.rpcOverride || cfg.rpc;
}

function chainById(id) {
  return Object.entries(CHAINS).find(([, v]) => v.chainId === id)?.[0];
}

/** Format token amount for display */
function fmtAmt(amountRaw, decimals = 18) {
  const { ethers } = require('ethers');
  return ethers.formatUnits(BigInt(amountRaw), decimals);
}

// ── Socket daemon ─────────────────────────────────────────────────────────────
let _sock = null;
function getSock() {
  if (!_sock) {
    // Connect to existing daemon — do NOT start a new one.
    const DAEMON_LOCK = '/tmp/.aawp-daemon.lock';
    try {
      const lockData = JSON.parse(require('fs').readFileSync(DAEMON_LOCK, 'utf8'));
      if (lockData.sock && require('fs').existsSync(lockData.sock)) {
        addon._i0(C, S);
        _sock = lockData.sock;
      } else {
        throw new Error('socket not found');
      }
    } catch (e) {
      console.error('❌ AAWP daemon not running. Start via OpenClaw first.');
      process.exit(1);
    }
  }
  return _sock;
}

let _aiGateToken = process.env.AAWP_AI_TOKEN || null;
try {
  const persisted = fs.readFileSync('/tmp/.aawp-ai-token', 'utf8').trim();
  if (persisted && persisted.length === 64) _aiGateToken = persisted;
} catch (_) {}

function socketQuery(obj) {
  const sock = getSock();
  const ts   = Math.floor(Date.now() / 1000);
  const hmac = addon._h0(ts);
  const isSign = typeof obj !== 'string' && (!obj.cmd || obj.cmd === 'sign' || obj.cmd === 'sign_message' || obj.cmd === 'sign_hash' || obj.cmd === 'sign_typed');
  const aiFields = (isSign && _aiGateToken) ? { ai_token: _aiGateToken } : {};
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

function loadGuardianRecord() {
  const p = path.join(S, 'config/guardian.json');
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (_) { return null; }
}

function ensureLocalGuardian() {
  let rec = loadGuardianRecord();
  if (rec && rec.address && rec.privateKey) return rec;
  const w = ethers.Wallet.createRandom();
  rec = { address: w.address, privateKey: w.privateKey, createdAt: new Date().toISOString() };
  fs.writeFileSync(path.join(S, 'config/guardian.json'), JSON.stringify(rec, null, 2));
  return rec;
}

async function getAddresses() {
  const [a, l] = await Promise.all([
    socketQuery('address'),
    socketQuery('logichash'),
  ]);
  const guardianRec = ensureLocalGuardian();
  return { signer: a.address, guardian: guardianRec.address, binaryHash: l.logicHash };
}

// ── Core: get quote from Relay ────────────────────────────────────────────────

/**
 * getQuote — calls Relay /quote/v2
 * @param {object} opts
 *   user            wallet address (origin)
 *   recipient       destination address (default = user)
 *   originChainId
 *   destinationChainId
 *   originCurrency  token address (0x0 = native)
 *   destinationCurrency
 *   amount          string, in smallest unit
 *   tradeType       EXACT_INPUT | EXACT_OUTPUT (default EXACT_INPUT)
 */
async function getQuote(opts) {
  const body = {
    user: opts.user,
    recipient: opts.recipient || opts.user,
    originChainId: opts.originChainId,
    destinationChainId: opts.destinationChainId,
    originCurrency: opts.originCurrency,
    destinationCurrency: opts.destinationCurrency,
    amount: opts.amount,
    tradeType: opts.tradeType || 'EXACT_INPUT',
  };
  const quote = await relayFetch('POST', '/quote/v2', body);
  if (quote.message && !quote.steps) {
    throw new Error(`Relay quote error: ${quote.message}`);
  }
  return quote;
}

// ── Core: execute Relay steps via AAWP wallet ─────────────────────────────────

/**
 * Execute all steps returned by Relay quote.
 * For AAWP wallets: all "transaction" steps are submitted via the signed execute() flow.
 * Signature steps: sign raw message/typed data via socket then POST back.
 */
async function executeSteps(steps, walletAddr, originChainKey) {
  const { ethers } = require('ethers');
  const chain = CHAINS[originChainKey];
  const rpc   = chainRpc(originChainKey);
  const p     = new ethers.JsonRpcProvider(rpc);

  const WALLET_ABI = (() => {
    try { return require('/root/aawp-contracts/out/AAWPWallet.sol/AAWPWallet.json').abi; }
    catch { return ['function nonce() view returns (uint256)']; }
  })();

  const wallet = new ethers.Contract(walletAddr, WALLET_ABI, p);

  for (let si = 0; si < steps.length; si++) {
    const step = steps[si];
    if (!step.items || step.items.length === 0) continue;

    console.log(`\n⟳ Step ${si + 1}/${steps.length}: ${step.id || step.action || 'execute'}`);

    for (let ii = 0; ii < step.items.length; ii++) {
      const item = step.items[ii];
      if (!item) continue;

      // ── Transaction step ──────────────────────────────────────────────────
      if (item.data && item.data.to) {
        const tx = item.data;
        const toAddr   = tx.to;
        const value    = BigInt(tx.value || '0');
        let   data     = tx.data || '0x';
        if (typeof data === 'string') {
          if (!data.startsWith('0x')) data = '0x' + data;
          if ((data.length % 2) !== 0) data = '0x0' + data.slice(2);
        }
        const gasLimit = tx.gas ? Number(tx.gas) : undefined;

        // Auto max-approve: if this is an approve step, replace amount with MaxUint256
        // so future swaps for this token skip the approve step entirely.
        const stepId = (step.id || step.action || '').toLowerCase();
        if (stepId === 'approve' && data.length >= 10 && data.slice(0, 10) === '0x095ea7b3') {
          const MAX_UINT256 = 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff';
          // ERC-20 approve(address,uint256): 4 bytes selector + 32 bytes addr + 32 bytes amount
          data = data.slice(0, 10 + 64) + MAX_UINT256;
          console.log(`  ↑ Auto max-approve: upgrading to MaxUint256 for future swaps`);
        }

        // Get current wallet nonce via NonceManager
        let wNonce;
        try { wNonce = await nonceManager.getNonce(p, walletAddr, chain.chainId, wallet); } catch { wNonce = 0; }
        const deadline = Math.floor(Date.now() / 1000) + 3600;

        // Dynamic gas price
        let gasPriceFields = {};
        try { gasPriceFields = await getGasPriceEstimate(p, originChainKey); } catch {}

        console.log(`  → tx to ${toAddr} value ${ethers.formatEther(value)} ETH data[${data.length}]`);

        const result = await socketQuery({
          cmd:      'sign',
          wallet:   walletAddr,
          to:       toAddr,
          value:    '0x' + value.toString(16),
          nonce:    Number(wNonce),
          deadline,
          chain_id: chain.chainId,
          rpc,
          data,
          gas_key: process.env.AAWP_GUARDIAN_KEY || process.env.AAWP_GAS_KEY || ensureLocalGuardian().privateKey,
          // Relay gas estimates are for direct EOA calls. AAWP smart contract wallet
          // needs extra gas for EIP-712 hashing + ECDSA verification + SSTORE (nonce).
          // Apply 3x multiplier with a 300k minimum to prevent out-of-gas reverts.
          ...(gasLimit ? { gas_limit: Math.max(gasLimit * 3, 300_000) } : { gas_limit: 300_000 }),
          ...(gasPriceFields.gasPrice ? { gas_price: '0x' + gasPriceFields.gasPrice.toString(16) } : {}),
          ...(gasPriceFields.maxFeePerGas ? { max_fee: '0x' + gasPriceFields.maxFeePerGas.toString(16), max_priority_fee: '0x' + gasPriceFields.maxPriorityFeePerGas.toString(16) } : {}),
        });

        if (result.error) {
          nonceManager.confirm(walletAddr, chain.chainId);
          throw new Error(`Sign failed: ${result.error}`);
        }
        const txHash = result.result;
        console.log(`  ✅ TX submitted: ${chain.explorer}/tx/${txHash}`);

        // Wait for confirmation
        process.stdout.write('  Confirming');
        const receipt = await p.waitForTransaction(txHash, 1, 120000);
        nonceManager.confirm(walletAddr, chain.chainId);
        console.log(receipt.status === 1 ? ' ✅' : ' ❌ REVERTED');
        if (receipt.status !== 1) throw new Error(`Transaction reverted: ${txHash}`);

        // If this is a cross-chain step, poll Relay for destination fill
        if (item.check?.endpoint) {
          await pollRelayStatus(item.check.endpoint, txHash);
        }
      }

      // ── Signature step ────────────────────────────────────────────────────
      else if (item.data?.sign) {
        const sign = item.data.sign;
        console.log(`  → signature request (${sign.signatureKind})`);

        let sig;
        if (sign.signatureKind === 'eip191') {
          const result = await socketQuery({
            cmd: 'sign_message',
            message: sign.message,
          });
          if (result.error) throw new Error(`Sign message failed: ${result.error}`);
          sig = result.signature;
        } else if (sign.signatureKind === 'eip712') {
          const result = await socketQuery({
            cmd: 'sign_typed',
            domain: sign.domain,
            types: sign.types,
            value: sign.value || sign.data,
          });
          if (result.error) throw new Error(`Sign typed failed: ${result.error}`);
          sig = result.signature;
        } else {
          throw new Error(`Unknown signatureKind: ${sign.signatureKind}`);
        }

        // POST signature back to Relay
        if (item.data.post) {
          const post = item.data.post;
          const postUrl = new URL(post.endpoint, RELAY_API);
          await relayFetch('POST', postUrl.pathname + postUrl.search, {
            ...post.body,
            signature: sig,
          });
          console.log('  ✅ Signature posted');
        }
      }
    }
  }
}

/** Wait for Relay fill via WebSocket (preferred) or HTTP polling (fallback) */
async function pollRelayStatus(endpoint, txHash, timeoutMs = 300000) {
  // Try WebSocket first
  let WebSocket;
  try { WebSocket = require('ws'); } catch { WebSocket = null; }

  if (WebSocket) {
    try {
      const filled = await waitForRelayFillWs(WebSocket, txHash, timeoutMs);
      if (filled !== null) return; // resolved via WS
    } catch {
      // WS failed, fall through to polling
    }
  }

  // Fallback: HTTP polling
  process.stdout.write('  Waiting for destination fill (polling)');
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const url = endpoint.includes('?')
        ? `${endpoint}&txHash=${txHash}`
        : `${endpoint}?txHash=${txHash}`;
      const status = await relayFetch('GET', url.replace(RELAY_API, ''));
      const state = status?.status || status?.data?.status;
      if (state === 'success' || state === 'completed') {
        console.log(' ✅ Filled!');
        return;
      }
      if (state === 'failed' || state === 'refunded') {
        console.log(` ❌ ${state}`);
        return;
      }
    } catch { /* continue polling */ }
    process.stdout.write('.');
    await new Promise(r => setTimeout(r, 3000));
  }
  console.log(' ⏱ Timeout — check Relay explorer manually');
}

/** WebSocket-based Relay status monitoring */
function waitForRelayFillWs(WebSocket, txHash, timeoutMs) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket('wss://api.relay.link/ws');
    const timer = setTimeout(() => {
      ws.close();
      resolve(null); // timeout → fallback to polling
    }, Math.min(timeoutMs, 30000)); // give WS 30s max before fallback

    ws.on('open', () => {
      process.stdout.write('  Waiting for destination fill (ws)');
      ws.send(JSON.stringify({ type: 'subscribe', txHash }));
    });

    ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());
        if (msg.status === 'success' || msg.status === 'completed') {
          console.log(' ✅ Filled!');
          clearTimeout(timer);
          ws.close();
          resolve(true);
        } else if (msg.status === 'failed' || msg.status === 'refunded') {
          console.log(` ❌ ${msg.status}`);
          clearTimeout(timer);
          ws.close();
          resolve(true);
        } else {
          process.stdout.write('.');
        }
      } catch { /* ignore parse errors */ }
    });

    ws.on('error', () => {
      clearTimeout(timer);
      ws.close();
      resolve(null); // fallback to polling
    });

    ws.on('close', () => {
      clearTimeout(timer);
      // If not resolved yet, fallback
    });
  });
}

// ── Print quote summary ───────────────────────────────────────────────────────
function printQuote(quote, fromChain, toChain, fromToken, toToken) {
  const { ethers } = require('ethers');
  const details = quote.details || {};
  const fees    = quote.fees    || {};

  console.log('\n── Relay Quote ──────────────────────────────');

  if (details.currencyIn) {
    const cin  = details.currencyIn;
    const cout = details.currencyOut;
    const amtIn  = fmtAmt(cin.amount?.amount  || cin.amount  || '0', cin.currency?.decimals  || 18);
    const amtOut = fmtAmt(cout.amount?.amount || cout.amount || '0', cout.currency?.decimals || 18);
    const symIn  = cin.currency?.symbol  || fromToken;
    const symOut = cout.currency?.symbol || toToken;
    console.log(`  You send:    ${amtIn} ${symIn}  (${fromChain.toUpperCase()})`);
    console.log(`  You receive: ${amtOut} ${symOut}  (${toChain.toUpperCase()})`);
  }

  if (details.rate)         console.log(`  Rate:        ${details.rate}`);
  // slippageTolerance not returned by Relay API in details — omit

  if (fees.relayer) {
    const f = fees.relayer;
    const fAmt = fmtAmt(f.amount || '0', f.currency?.decimals || 18);
    console.log(`  Relay fee:   ${fAmt} ${f.currency?.symbol || ''}`);
  }
  if (fees.gas) {
    const g = fees.gas;
    const gAmt = fmtAmt(g.amount || '0', g.currency?.decimals || 18);
    console.log(`  Est. gas:    ${gAmt} ${g.currency?.symbol || 'ETH'}`);
  }

  const eta = details.timeEstimate;
  if (eta) console.log(`  Est. time:   ~${eta}s`);
  console.log('─────────────────────────────────────────────');
}

// ══════════════════════════════════════════════════════════════════════════════
// PUBLIC API (called from wallet-manager or standalone)
// ══════════════════════════════════════════════════════════════════════════════

/**
 * swap — same-chain swap via Relay
 * @param {string} chainKey   e.g. 'base'
 * @param {string} fromToken  symbol or address
 * @param {string} toToken    symbol or address
 * @param {string} amountHuman human-readable amount (e.g. "0.01")
 */
async function swap(chainKey, fromToken, toToken, amountHuman, _unused, slippageBps = 50) {
  const { ethers } = require('ethers');
  const chain = CHAINS[chainKey];
  if (!chain) throw new Error(`Unknown chain: ${chainKey}`);

  const { signer, guardian, binaryHash } = await getAddresses();

  // Get wallet address
  const rpc = chainRpc(chainKey);
  const p   = new ethers.JsonRpcProvider(rpc);
  const FACTORY_ABI = ['function computeAddress(address,bytes32,address) view returns (address)'];
  const factoryAddr = chain.factory;
  if (!factoryAddr || factoryAddr === ethers.ZeroAddress) {
    throw new Error(`AAWP Factory not deployed on ${chainKey}. Deploy first.`);
  }
  const factory  = new ethers.Contract(factoryAddr, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, binaryHash, guardian);

  const code = await p.getCode(walletAddr);
  if (code.length <= 2) throw new Error(`Wallet not deployed on ${chainKey}: ${walletAddr}`);

  const fromAddr = resolveToken(chainKey, fromToken);
  const toAddr   = resolveToken(chainKey, toToken);

  // Determine decimals for amount
  let decimals = 18;
  if (fromAddr !== NATIVE) {
    try {
      const tok = new ethers.Contract(fromAddr, ['function decimals() view returns (uint8)'], p);
      decimals = await tok.decimals();
    } catch { decimals = 18; }
  }
  const amountWei = ethers.parseUnits(amountHuman, decimals).toString();

  console.log(`\n🔄 Swap on ${chain.name}`);
  console.log(`   ${amountHuman} ${fromToken} → ${toToken}`);
  console.log(`   Wallet: ${walletAddr}`);

  // Get quote
  const quote = await getQuote({
    user:                 walletAddr,
    originChainId:        chain.chainId,
    destinationChainId:   chain.chainId,
    originCurrency:       fromAddr,
    destinationCurrency:  toAddr,
    amount:               amountWei,
    slippageTolerance:    (slippageBps / 10000).toString(),
  });

  printQuote(quote, chainKey, chainKey, fromToken, toToken);

  if (!quote.steps || quote.steps.length === 0) {
    throw new Error('No execution steps returned from Relay.');
  }

  await executeSteps(quote.steps, walletAddr, chainKey);
  txHistory.append({ chain: chainKey, type: 'swap', from: walletAddr, to: walletAddr, amount: amountHuman, token: `${fromToken}→${toToken}`, txHash: 'relay', status: 'completed' });
  console.log('\n✅ Swap complete!');

  // Auto-unwrap WETH → ETH if destination token is WETH
  if (chain.tokens?.WETH && toAddr.toLowerCase() === chain.tokens.WETH.toLowerCase()) {
    await unwrapWeth(walletAddr, chainKey, p);
  }
}

/**
 * bridge — cross-chain bridge via Relay
 */
async function bridge(fromChainKey, toChainKey, fromToken, toToken, amountHuman, slippageBps = 50, recipient = null) {
  const { ethers } = require('ethers');
  const fromChain = CHAINS[fromChainKey];
  const toChain   = CHAINS[toChainKey];
  if (!fromChain) throw new Error(`Unknown origin chain: ${fromChainKey}`);
  if (!toChain)   throw new Error(`Unknown destination chain: ${toChainKey}`);

  const { signer, guardian, binaryHash } = await getAddresses();

  const rpc = chainRpc(fromChainKey);
  const p   = new ethers.JsonRpcProvider(rpc);
  const FACTORY_ABI = ['function computeAddress(address,bytes32,address) view returns (address)'];

  if (!fromChain.factory || fromChain.factory === ethers.ZeroAddress) {
    throw new Error(`AAWP Factory not deployed on ${fromChainKey}.`);
  }
  const factory    = new ethers.Contract(fromChain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, binaryHash, guardian);

  const code = await p.getCode(walletAddr);
  if (code.length <= 2) throw new Error(`Wallet not deployed on ${fromChainKey}: ${walletAddr}`);

  const fromAddr = resolveToken(fromChainKey, fromToken);

  // Destination address — custom recipient or same wallet address
  const destAddr = recipient || walletAddr;
  const toAddr   = resolveToken(toChainKey, toToken);

  let decimals = 18;
  if (fromAddr !== NATIVE) {
    try {
      const tok = new ethers.Contract(fromAddr, ['function decimals() view returns (uint8)'], p);
      decimals = await tok.decimals();
    } catch { decimals = 18; }
  }
  const amountWei = ethers.parseUnits(amountHuman, decimals).toString();

  console.log(`\n🌉 Bridge: ${fromChain.name} → ${toChain.name}`);
  console.log(`   ${amountHuman} ${fromToken} → ${toToken}`);
  console.log(`   From wallet: ${walletAddr}`);
  console.log(`   To address:  ${destAddr}`);

  const quote = await getQuote({
    user:                 walletAddr,
    recipient:            destAddr,
    originChainId:        fromChain.chainId,
    destinationChainId:   toChain.chainId,
    originCurrency:       fromAddr,
    destinationCurrency:  toAddr,
    amount:               amountWei,
    slippageTolerance:    (slippageBps / 10000).toString(),
  });

  printQuote(quote, fromChainKey, toChainKey, fromToken, toToken);

  if (!quote.steps || quote.steps.length === 0) {
    throw new Error('No execution steps returned from Relay.');
  }

  await executeSteps(quote.steps, walletAddr, fromChainKey);
  txHistory.append({ chain: fromChainKey, type: 'bridge', from: walletAddr, to: destAddr, amount: amountHuman, token: `${fromToken}→${toToken}`, txHash: 'relay', status: 'initiated' });
  console.log('\n✅ Bridge initiated! Destination fill in progress.');

  // Auto-unwrap WETH on destination chain if toToken is WETH
  if (toChain.tokens?.WETH && toAddr.toLowerCase() === toChain.tokens.WETH.toLowerCase()) {
    const destRpc = toChain.rpcOverride || toChain.rpc;
    const destP   = new ethers.JsonRpcProvider(destRpc);
    await unwrapWeth(destAddr, toChainKey, destP);
  }
}

/**
 * quoteOnly — print quote without executing
 */
async function quoteOnly(fromChainKey, toChainKey, fromToken, toToken, amountHuman) {
  const { ethers } = require('ethers');
  const fromChain = CHAINS[fromChainKey];
  const toChain   = CHAINS[toChainKey];
  if (!fromChain) throw new Error(`Unknown chain: ${fromChainKey}`);
  if (!toChain)   throw new Error(`Unknown chain: ${toChainKey}`);

  const { signer, guardian, binaryHash } = await getAddresses();
  const rpc  = chainRpc(fromChainKey);
  const p    = new ethers.JsonRpcProvider(rpc);
  const FACTORY_ABI = ['function computeAddress(address,bytes32,address) view returns (address)'];
  const factory    = new ethers.Contract(fromChain.factory, FACTORY_ABI, p);
  const walletAddr = process.env.AAWP_WALLET || await factory.computeAddress(signer, binaryHash, guardian);

  const fromAddr = resolveToken(fromChainKey, fromToken);
  const toAddr   = resolveToken(toChainKey,   toToken);

  let decimals = 18;
  if (fromAddr !== NATIVE) {
    try {
      const tok = new ethers.Contract(fromAddr, ['function decimals() view returns (uint8)'], p);
      decimals = await tok.decimals();
    } catch {}
  }
  const amountWei = ethers.parseUnits(amountHuman, decimals).toString();

  const isSameChain = fromChain.chainId === toChain.chainId;
  console.log(isSameChain
    ? `\n💱 Swap quote on ${fromChain.name}: ${amountHuman} ${fromToken} → ${toToken}`
    : `\n🌉 Bridge quote: ${fromChain.name} → ${toChain.name}: ${amountHuman} ${fromToken} → ${toToken}`
  );

  const quote = await getQuote({
    user:                walletAddr,
    originChainId:       fromChain.chainId,
    destinationChainId:  toChain.chainId,
    originCurrency:      fromAddr,
    destinationCurrency: toAddr,
    amount:              amountWei,
  });

  printQuote(quote, fromChainKey, toChainKey, fromToken, toToken);
  console.log('(Quote only — run swap/bridge to execute)');
}

/** List Relay supported chains */
async function listChains() {
  console.log('Fetching Relay supported chains...');
  const data = await relayFetch('GET', '/chains?limit=50');
  const chains = data.chains || data || [];
  console.log(`\n── Relay Supported Chains (${chains.length}) ────────`);
  for (const c of chains) {
    const local = chainById(c.id);
    const tag = local ? ` ← ${local.toUpperCase()}` : '';
    console.log(`  ${String(c.id).padEnd(8)} ${(c.name || c.displayName || '').padEnd(25)}${tag}`);
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// STANDALONE CLI
// ══════════════════════════════════════════════════════════════════════════════

if (require.main === module) {
  const args = process.argv.slice(2);
  let chainKey = 'base';
  const filtered = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--chain' && args[i+1]) { chainKey = args[++i]; }
    else filtered.push(args[i]);
  }

  const cmd = filtered[0];

  const run = async () => {
    switch (cmd) {
      case 'swap':
        await swap(chainKey, filtered[1], filtered[2], filtered[3]);
        break;
      case 'bridge':
        await bridge(filtered[1], filtered[2], filtered[3], filtered[4], filtered[5]);
        break;
      case 'quote':
        await quoteOnly(filtered[1], filtered[2], filtered[3], filtered[4], filtered[5]);
        break;
      case 'chains':
        await listChains();
        break;
      default:
        console.log(`
AAWP Swap — Relay Bridge

Usage:
  node swap.js [--chain <chain>] swap <fromToken> <toToken> <amount>
  node swap.js bridge <fromChain> <toChain> <fromToken> <toToken> <amount>
  node swap.js quote  <fromChain> <toChain> <fromToken> <toToken> <amount>
  node swap.js chains

Examples:
  node swap.js --chain base swap ETH USDC 0.01
  node swap.js bridge base arb ETH ETH 0.05
  node swap.js bridge base eth USDC USDC 100
  node swap.js quote base polygon ETH MATIC 0.1
  node swap.js chains

Tokens: ETH, BNB, MATIC, USDC, USDT, WETH, DAI — or any 0x address
Chains: ${Object.keys(CHAINS).join(', ')}
`);
    }
  };

  run().catch(e => { console.error('❌', e.message); process.exit(1); });
}

/**
 * unwrapWeth — auto-unwrap WETH balance to ETH via wallet.execute()
 * Called automatically after swap/bridge when destination token is WETH.
 */
async function unwrapWeth(walletAddr, chainKey, provider) {
  const { ethers } = require('ethers');
  const chain = CHAINS[chainKey];
  const wethAddr = chain.tokens?.WETH;
  if (!wethAddr) return;

  const WETH_ABI = [
    'function balanceOf(address) view returns (uint256)',
    'function withdraw(uint256) returns ()',
  ];
  const WALLET_ABI = ['function nonce() view returns (uint256)'];

  const weth   = new ethers.Contract(wethAddr, WETH_ABI, provider);
  const wallet = new ethers.Contract(walletAddr, WALLET_ABI, provider);

  // Small delay to let balance settle after fill
  await new Promise(r => setTimeout(r, 2000));
  const bal = await weth.balanceOf(walletAddr);
  if (bal === 0n) return;

  console.log(`\n🔓 Auto-unwrapping ${ethers.formatEther(bal)} WETH → ETH...`);

  const iface = new ethers.Interface(WETH_ABI);
  const data  = iface.encodeFunctionData('withdraw', [bal]);
  const nonce = await wallet.nonce();
  const deadline = Math.floor(Date.now() / 1000) + 3600;
  const rpc = chain.rpcOverride || chain.rpc;

  const result = await socketQuery({
    cmd:      'sign',
    wallet:   walletAddr,
    to:       wethAddr,
    value:    '0x0',
    nonce:    Number(nonce),
    deadline,
    chain_id: chain.chainId,
    rpc,
    data,
  });

  if (result.error) {
    console.log(`  ⚠️  Unwrap failed: ${result.error} (manual: wallet.execute WETH.withdraw(${bal}))`);
    return;
  }

  console.log(`  ✅ Unwrap TX: ${chain.explorer}/tx/${result.result}`);
  const receipt = await provider.waitForTransaction(result.result, 1, 60000);
  if (receipt.status === 1) {
    const ethBal = await provider.getBalance(walletAddr);
    console.log(`  ETH balance: ${ethers.formatEther(ethBal)} ETH`);
  }
}

module.exports = { swap, bridge, quoteOnly, listChains, resolveToken, getQuote, unwrapWeth };
