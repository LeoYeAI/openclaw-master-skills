#!/usr/bin/env node
// skills/xaut-trade/scripts/limit-order.js
//
// Usage:
//   node limit-order.js place  --token-in <addr> --token-out <addr> \
//                               --amount-in <uint> --min-amount-out <uint> \
//                               --expiry <seconds> --wallet <addr> \
//                               --chain-id <int> --api-url <url>
//   node limit-order.js status --order-hash <0x...> --api-url <url> --chain-id <int>
//   node limit-order.js list   --wallet <addr> --api-url <url> --chain-id <int> [--order-status open|filled|expired|cancelled]
//   node limit-order.js cancel --order-hash <0x...>   (reads nonce from ~/.aurehub/orders/)
//   node limit-order.js cancel --nonce <uint>          (fallback)
//
// Signing mode: delegates to swap.js sign (supports both WDK and Foundry).
//   PRIVATE_KEY runtime signing is intentionally not supported.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import yaml from 'js-yaml';
import { computeNonceComponents, checkPrecision, resolveExpiry } from './helpers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);
const { ethers } = require('ethers');
const { DutchOrderBuilder } = require('@uniswap/uniswapx-sdk');

// ethers v5 BigNumber (SDK uses .gte() etc — native BigInt not compatible)
const BN = ethers.BigNumber;

const [,, subcommand, ...argv] = process.argv;

// Load defaults from ~/.aurehub/config.yaml
function loadDefaults() {
  try {
    const configDir = path.join(os.homedir(), '.aurehub');
    const raw = fs.readFileSync(path.join(configDir, 'config.yaml'), 'utf8');
    const cfg = yaml.load(raw, { schema: yaml.JSON_SCHEMA }) ?? {};
    return {
      apiUrl: cfg.limit_order?.uniswapx_api || null,
      chainId: String(cfg.networks?.ethereum_mainnet?.chain_id || '1'),
      limitOrderCfg: cfg.limit_order ?? {},
    };
  } catch { return { apiUrl: null, chainId: '1', limitOrderCfg: {} }; }
}

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    if (i + 1 >= args.length) {
      console.error(`Missing value for flag: ${args[i]}`);
      process.exit(1);
    }
    const key = args[i].replace(/^--/, '').replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    result[key] = args[i + 1];
  }
  return result;
}

async function main() {
  const args = parseArgs(argv);
  // Apply config.yaml defaults for apiUrl and chainId when not provided via CLI
  const defaults = loadDefaults();
  if (!args.apiUrl && defaults.apiUrl) args.apiUrl = defaults.apiUrl;
  if (!args.chainId && defaults.chainId) args.chainId = defaults.chainId;
  args._limitOrderCfg = defaults.limitOrderCfg;
  switch (subcommand) {
    case 'place':  return await place(args);
    case 'status': return await status(args);
    case 'list':   return await list(args);
    case 'cancel': return await cancel(args);
    default:
      console.error('Usage: limit-order.js <place|status|list|cancel> [options]');
      process.exit(1);
  }
}

main().catch(err => { console.error(err.message); process.exit(1); });

async function place(args) {
  const {
    tokenIn, tokenOut, amountIn, minAmountOut,
    expiry, wallet, chainId, apiUrl,
  } = args;

  // 1. Validate required args
  const required = { tokenIn, tokenOut, amountIn, minAmountOut, wallet, chainId, apiUrl };
  for (const [k, v] of Object.entries(required)) {
    if (!v) { console.error(`Missing required argument: --${k.replace(/([A-Z])/g, '-$1').toLowerCase()}`); process.exit(1); }
  }

  // Precision check: both XAUT and USDT have 6 decimals max
  if (!checkPrecision(amountIn, 6)) {
    console.error('ERROR: amountIn exceeds maximum precision (6 decimal places)');
    process.exit(1);
  }
  if (!checkPrecision(minAmountOut, 6)) {
    console.error('ERROR: minAmountOut exceeds maximum precision (6 decimal places)');
    process.exit(1);
  }

  const chainIdNum = parseInt(chainId, 10);
  if (Number.isNaN(chainIdNum) || chainIdNum <= 0) {
    console.error('ERROR: --chain-id must be a positive integer');
    process.exit(1);
  }
  const limitOrderCfg = args._limitOrderCfg || {};
  const expiryLimits = {
    defaultSeconds: limitOrderCfg.default_expiry_seconds ?? 86400,
    minSeconds: limitOrderCfg.min_expiry_seconds ?? 300,
    maxSeconds: limitOrderCfg.max_expiry_seconds ?? 2592000,
  };
  const rawExpiry = expiry ? parseInt(expiry, 10) : null;
  if (rawExpiry !== null && (Number.isNaN(rawExpiry) || rawExpiry <= 0)) {
    console.error('ERROR: --expiry must be a positive integer (seconds)');
    process.exit(1);
  }
  const expirySec = resolveExpiry(rawExpiry, expiryLimits);
  const deadline = Math.floor(Date.now() / 1000) + expirySec;

  // 2. Validate amounts (invariant — does not depend on nonce)
  const amountInBN = BN.from(amountIn);
  const minAmountOutBN = BN.from(minAmountOut);
  if (minAmountOutBN.lte(BN.from(0))) {
    console.error('ERROR: --min-amount-out must be greater than 0');
    process.exit(1);
  }

  // 3. Fetch nonce from UniswapX API
  // UniswapX API requires Origin header matching app.uniswap.org; may break if Uniswap changes policy
  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const uniswapHeaders = {
    'Origin': 'https://app.uniswap.org',
    'User-Agent': 'Mozilla/5.0',
    ...(apiKey ? { 'x-api-key': apiKey } : {}),
  };
  const nonceRes = await fetch(`${apiUrl}/nonce?address=${wallet}&chainId=${chainId}`, { headers: uniswapHeaders });
  if (!nonceRes.ok) throw new Error(`Nonce fetch failed: ${nonceRes.status} ${await nonceRes.text()}`);
  const nonceData = await nonceRes.json();
  let nonce = nonceData.nonce;

  // 4. Build, sign, and submit order with nonce retry logic (max 5 attempts)
  const MAX_NONCE_RETRIES = 5;
  for (let attempt = 0; attempt < MAX_NONCE_RETRIES; attempt++) {
    // Build order (must rebuild each attempt — nonce changes on retry)
    // Fixed-price limit order: decayStart == decayEnd == deadline so the
    // DutchOrder never decays — the swapper receives exactly minAmountOut
    // (no Dutch-auction price improvement, but also no price deterioration).
    const builder = new DutchOrderBuilder(chainIdNum);
    const order = builder
      .deadline(deadline)
      .decayStartTime(deadline)
      .decayEndTime(deadline)
      .nonce(BN.from(nonce))
      .swapper(wallet)
      .input({ token: tokenIn, startAmount: amountInBN, endAmount: amountInBN })
      .output({
        token: tokenOut,
        startAmount: minAmountOutBN,
        endAmount: minAmountOutBN,
        recipient: wallet,
      })
      .build();

    // Sign via EIP-712
    const { domain, types, values } = order.permitData();
    const bnReplacer = (_, v) => (v && v.type === 'BigNumber' && v.hex) ? v.hex : v;
    const eip712Domain = [
      { name: 'name', type: 'string' },
      ...(domain.version !== undefined ? [{ name: 'version', type: 'string' }] : []),
      ...(domain.chainId !== undefined ? [{ name: 'chainId', type: 'uint256' }] : []),
      ...(domain.verifyingContract !== undefined ? [{ name: 'verifyingContract', type: 'address' }] : []),
    ];
    const primaryType = 'PermitWitnessTransferFrom';
    const typesWithDomain = { EIP712Domain: eip712Domain, ...types };
    const typedDataJson = JSON.stringify({ domain, types: typesWithDomain, primaryType, message: values }, bnReplacer);
    let signature;

    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'limit-order-'));
    const tmpFile = path.join(tmpDir, 'typed-data.json');
    fs.writeFileSync(tmpFile, typedDataJson);
    try {
      const signResult = spawnSync(
        process.execPath,
        [path.join(__dirname, 'swap.js'), 'sign', '--data-file', tmpFile],
        { encoding: 'utf8', timeout: 30_000 }
      );
      if (signResult.error) {
        throw new Error(`Failed to spawn swap.js sign: ${signResult.error.message}`);
      }
      if (signResult.status !== 0) {
        throw new Error(signResult.stderr?.trim() || 'swap.js sign failed');
      }
      signature = signResult.stdout.trim();
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }

    // Submit to UniswapX API
    const encodedOrder = order.serialize();
    const orderHash = order.hash();

    const submitRes = await fetch(`${apiUrl}/order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...uniswapHeaders },
      body: JSON.stringify({ encodedOrder, signature, chainId: chainIdNum }),
    });

    if (!submitRes.ok) {
      const body = await submitRes.text();
      if (body.includes('NonceUsed') && attempt < MAX_NONCE_RETRIES - 1) {
        nonce = BN.from(nonce).add(BN.from(1)).toString();
        continue;
      }
      throw new Error(`Order submission failed: ${submitRes.status} ${body}`);
    }

    // 5. Auto-save order to ~/.aurehub/orders/ for later cancellation
    const orderData = {
      orderHash,
      nonce,
      deadline: new Date(deadline * 1000).toISOString(),
      deadlineUnix: deadline,
      tokenIn,
      tokenOut,
      amountIn,
      minAmountOut,
      wallet,
      createdAt: new Date().toISOString(),
    };
    const ordersDir = path.join(os.homedir(), '.aurehub', 'orders');
    fs.mkdirSync(ordersDir, { recursive: true });
    fs.writeFileSync(
      path.join(ordersDir, `${orderHash.slice(0, 10)}.json`),
      JSON.stringify(orderData, null, 2)
    );

    // 6. Output JSON for SKILL.md to parse
    console.log(JSON.stringify({
      address: wallet,
      orderHash,
      deadline: orderData.deadline,
      deadlineUnix: deadline,
      nonce,
    }));
    return;
  }
}

async function status(args) {
  const { orderHash, apiUrl, chainId } = args;
  if (!orderHash || !apiUrl || !chainId) {
    console.error('Missing required: --order-hash, --api-url, --chain-id');
    process.exit(1);
  }

  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const res = await fetch(
    `${apiUrl}/orders?orderHash=${orderHash}&chainId=${chainId}`,
    { headers: {
      'Origin': 'https://app.uniswap.org',
      'User-Agent': 'Mozilla/5.0',
      ...(apiKey ? { 'x-api-key': apiKey } : {}),
    }}
  );
  if (!res.ok) throw new Error(`Status fetch failed: ${res.status} ${await res.text()}`);

  const data = await res.json();
  const orders = data.orders || [];

  if (orders.length === 0) {
    console.log(JSON.stringify({ status: 'not_found', orderHash }));
    return;
  }

  const o = orders[0];
  console.log(JSON.stringify({
    status: o.orderStatus,
    orderHash: o.orderHash,
    deadline: o.deadline ? new Date(o.deadline * 1000).toISOString() : null,
    txHash: o.txHash || null,
    settledAmounts: o.settledAmounts || null,
  }));
}

async function list(args) {
  const { wallet, apiUrl, chainId, orderStatus } = args;
  if (!wallet || !apiUrl || !chainId) {
    console.error('Missing required: --wallet, --api-url, --chain-id');
    process.exit(1);
  }

  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const headers = {
    'Origin': 'https://app.uniswap.org',
    'User-Agent': 'Mozilla/5.0',
    ...(apiKey ? { 'x-api-key': apiKey } : {}),
  };

  // The UniswapX API ignores the offerer param when orderStatus is omitted,
  // returning unrelated orders. Work around by querying each status separately.
  const statuses = orderStatus
    ? [orderStatus]
    : ['open', 'filled', 'expired', 'cancelled'];

  const allOrders = [];
  const walletLower = wallet.toLowerCase();

  for (const s of statuses) {
    const url = `${apiUrl}/orders?offerer=${wallet}&chainId=${chainId}&orderStatus=${s}`;
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`List fetch failed (${s}): ${res.status} ${await res.text()}`);
    const data = await res.json();
    for (const o of (data.orders || [])) {
      // Double-check swapper matches our wallet
      if ((o.swapper || '').toLowerCase() === walletLower) {
        allOrders.push(o);
      }
    }
  }

  const orders = allOrders.map(o => ({
    orderHash: o.orderHash,
    status: o.orderStatus,
    inputToken: o.input?.token,
    inputAmount: o.input?.startAmount,
    outputToken: (o.outputs?.[0])?.token,
    outputAmount: (o.outputs?.[0])?.startAmount,
    txHash: o.txHash || null,
    createdAt: o.createdAt ? new Date(o.createdAt * 1000).toISOString() : null,
  }));

  console.log(JSON.stringify({ address: wallet, total: orders.length, orders }));
}

async function cancel(args) {
  let { nonce, orderHash } = args;

  // Resolve nonce from local order file if --order-hash is provided
  if (!nonce && orderHash) {
    const ordersDir = path.join(os.homedir(), '.aurehub', 'orders');
    if (fs.existsSync(ordersDir)) {
      const files = fs.readdirSync(ordersDir).filter(f => f.endsWith('.json'));
      const prefix = orderHash.toLowerCase();
      if (prefix.length < 10) {
        console.error('ERROR: --order-hash prefix too short (minimum 10 characters, e.g. "0x9079c4f2")');
        process.exit(1);
      }
      const match = files.find(f => {
        try {
          const data = JSON.parse(fs.readFileSync(path.join(ordersDir, f), 'utf8'));
          return data.orderHash && data.orderHash.toLowerCase().startsWith(prefix);
        } catch { return false; }
      });
      if (match) {
        const data = JSON.parse(fs.readFileSync(path.join(ordersDir, match), 'utf8'));
        nonce = data.nonce;
      }
    }
  }

  if (!nonce) {
    console.error('Missing required: --nonce or --order-hash (with matching local order file)');
    process.exit(1);
  }

  const { wordPos, mask } = computeNonceComponents(BigInt(nonce));

  console.log(JSON.stringify({
    wordPos: wordPos.toString(),
    mask: mask.toString(),
    permit2: '0x000000000022D473030F116dDEE9F6B43aC78BA3',
  }));
}
