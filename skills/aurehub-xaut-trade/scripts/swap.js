/**
 * swap.js — CLI entry point for market operations.
 *
 * Usage:
 *   node swap.js <command> [options]
 *
 * Commands:
 *   address    — output wallet address
 *   balance    — output ETH, USDT, XAUT balances
 *   allowance  — output ERC-20 allowance  (requires --token)
 *   quote      — get a Uniswap V3 quote   (requires --side, --amount)
 *   approve    — approve a token spender  (requires --token, --amount)
 *   swap       — execute a swap           (requires --side, --amount, --min-out)
 */

import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';
import { formatUnits, Interface } from 'ethers6';
import { loadConfig, resolveToken, validateContracts } from './lib/config.js';
import { createProvider } from './lib/provider.js';
import { createSigner } from './lib/signer.js';
import { getBalance, getAllowance, approve } from './lib/erc20.js';
import { quote, buildSwap } from './lib/uniswap.js';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const VALID_COMMANDS = new Set(['quote', 'balance', 'allowance', 'approve', 'swap', 'address', 'sign', 'cancel-nonce']);

// ---------------------------------------------------------------------------
// CLI argument parser — exported for unit-testing without RPC
// ---------------------------------------------------------------------------

/**
 * Parse raw argv (everything after "node swap.js") into a structured object.
 *
 * @param {string[]} argv  e.g. ['quote', '--side', 'buy', '--amount', '100']
 * @returns {{ command: string, side?: string, amount?: string, minOut?: string, token?: string, configDir?: string }}
 */
export function parseCliArgs(argv) {
  const [command, ...rest] = argv;

  if (!VALID_COMMANDS.has(command)) {
    throw new Error(`Unknown command: "${command}". Valid commands: ${[...VALID_COMMANDS].join(', ')}`);
  }

  const parsed = { command };

  for (let i = 0; i < rest.length; i++) {
    const flag = rest[i];
    const value = rest[i + 1];

    switch (flag) {
      case '--side':
        parsed.side = value;
        i++;
        break;
      case '--amount':
        parsed.amount = value;
        i++;
        break;
      case '--min-out':
        parsed.minOut = value;
        i++;
        break;
      case '--token':
        parsed.token = value;
        i++;
        break;
      case '--config-dir':
        parsed.configDir = value;
        i++;
        break;
      case '--data-file':
        parsed.dataFile = value;
        i++;
        break;
      case '--word-pos':
        parsed.wordPos = value;
        i++;
        break;
      case '--mask':
        parsed.mask = value;
        i++;
        break;
      case '--spender':
        parsed.spender = value;
        i++;
        break;
      default:
        // Ignore unknown flags silently
        break;
    }
  }

  if ((command === 'quote' || command === 'swap') && parsed.side) {
    const normalized = String(parsed.side).trim().toLowerCase();
    if (normalized !== 'buy' && normalized !== 'sell') {
      throw new Error(`Invalid --side value "${parsed.side}". Expected "buy" or "sell".`);
    }
    parsed.side = normalized;
  }

  return parsed;
}

// ---------------------------------------------------------------------------
// Subcommand implementations
// ---------------------------------------------------------------------------

async function runAddress(cfg, provider) {
  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);
  console.log(JSON.stringify({ address: signer.address }, null, 2));
}

async function runBalance(cfg, provider) {
  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);
  const address = signer.address;

  const tokens = cfg.yaml?.tokens ?? {};
  const usdtToken = resolveToken(cfg, 'USDT');
  const xautToken = resolveToken(cfg, 'XAUT');

  const [usdtBalance, xautBalance, ethBalanceRaw] = await Promise.all([
    getBalance(usdtToken, address, provider),
    getBalance(xautToken, address, provider),
    provider.getBalance(address),
  ]);

  // ethBalanceRaw is a hex string from the raw JSON-RPC; convert to ETH string
  const ethBig = BigInt(ethBalanceRaw);
  const ethBalance = formatUnits(ethBig, 18);

  console.log(JSON.stringify({ address, ETH: ethBalance, USDT: usdtBalance, XAUT: xautBalance }, null, 2));
}

async function runAllowance(cfg, provider, args) {
  if (!args.token) throw new Error('--token is required for allowance');

  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);
  const address = signer.address;

  const token = resolveToken(cfg, args.token);
  const contracts = cfg.yaml?.contracts ?? {};
  const spender = args.spender || contracts.router;
  if (!spender) throw new Error('--spender or contracts.router must be set');

  const allowance = await getAllowance(token, address, spender, provider);
  console.log(JSON.stringify({ address, token: args.token, allowance, spender }, null, 2));
}

async function runQuote(cfg, provider, args) {
  if (!args.side) throw new Error('--side is required for quote');
  if (!args.amount) throw new Error('--amount is required for quote');
  if (args.side !== 'buy' && args.side !== 'sell') throw new Error('--side must be "buy" or "sell"');

  // Resolve pair: buy = USDT→XAUT, sell = XAUT→USDT
  const isBuy = args.side === 'buy';
  const tokenIn = resolveToken(cfg, isBuy ? 'USDT' : 'XAUT');
  const tokenOut = resolveToken(cfg, isBuy ? 'XAUT' : 'USDT');

  const fee = _resolveFee(cfg, isBuy ? 'USDT' : 'XAUT', isBuy ? 'XAUT' : 'USDT');
  const contracts = cfg.yaml?.contracts ?? {};
  if (!contracts.quoter) throw new Error('contracts.quoter not set in config.yaml');

  const result = await quote({
    tokenIn,
    tokenOut,
    amountIn: args.amount,
    fee,
    contracts,
    provider,
  });

  // Convert bigints to strings for JSON output
  console.log(JSON.stringify({
    side: args.side,
    amountIn: args.amount,
    amountOut: result.amountOut,
    amountOutRaw: result.amountOutRaw.toString(),
    sqrtPriceX96: result.sqrtPriceX96.toString(),
    gasEstimate: result.gasEstimate.toString(),
  }, null, 2));
}

async function runApprove(cfg, provider, args) {
  if (!args.token) throw new Error('--token is required for approve');
  if (!args.amount) throw new Error('--amount is required for approve');

  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);
  const token = resolveToken(cfg, args.token);
  const contracts = cfg.yaml?.contracts ?? {};
  const spender = args.spender || contracts.router;
  if (!spender) throw new Error('--spender or contracts.router must be set');

  // Check token_rules for requiresResetApprove; skip reset if allowance is already 0
  const tokenRules = cfg.yaml?.token_rules ?? {};
  const rules = tokenRules[args.token] ?? {};
  let requiresResetApprove = rules.requires_reset_approve ?? false;
  if (requiresResetApprove && provider) {
    const currentAllowance = await getAllowance(token, signer.address, spender, provider);
    if (parseFloat(currentAllowance) === 0) requiresResetApprove = false;
  }

  const result = await approve(token, spender, args.amount, signer, { requiresResetApprove, fallbackProvider: provider });

  console.log(JSON.stringify({ address: signer.address, token: args.token, amount: args.amount, spender, txHash: result.hash }, null, 2));
}

async function runSwap(cfg, provider, args) {
  if (!args.side) throw new Error('--side is required for swap');
  if (!args.amount) throw new Error('--amount is required for swap');
  if (!args.minOut) throw new Error('--min-out is required for swap');
  if (!args.minOut || Number.isNaN(Number(args.minOut)) || Number(args.minOut) <= 0) throw new Error('--min-out must be a positive number greater than 0');
  if (args.side !== 'buy' && args.side !== 'sell') throw new Error('--side must be "buy" or "sell"');

  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);
  const address = signer.address;

  const isBuy = args.side === 'buy';
  const tokenIn = resolveToken(cfg, isBuy ? 'USDT' : 'XAUT');
  const tokenOut = resolveToken(cfg, isBuy ? 'XAUT' : 'USDT');

  const fee = _resolveFee(cfg, isBuy ? 'USDT' : 'XAUT', isBuy ? 'XAUT' : 'USDT');
  const contracts = cfg.yaml?.contracts ?? {};
  if (!contracts.router) throw new Error('contracts.router not set in config.yaml');

  const risk = cfg.yaml?.risk ?? {};
  const deadline = Math.floor(Date.now() / 1000) + (risk.deadline_seconds ?? 300);

  const tx = buildSwap({
    tokenIn,
    tokenOut,
    amountIn: args.amount,
    minAmountOut: args.minOut,
    fee,
    recipient: address,
    deadline,
    contracts,
  });

  const timeoutMs = (risk.deadline_seconds ?? 300) * 1000;

  // Send transaction — if this throws, the tx was never broadcast (safe to retry)
  const sentTx = await signer.sendTransaction(tx);

  // Use fallback-aware receipt wait when available (RPC resilience)
  const waitFn = provider?.waitForTransaction
    ? provider.waitForTransaction(sentTx.hash, 1, timeoutMs)
    : sentTx.wait();

  // Wait for confirmation — if this throws, the tx WAS broadcast but confirmation
  // failed (RPC error, timeout). Output txHash so caller can verify before retrying.
  let receipt;
  let confirmTimer;
  try {
    receipt = await Promise.race([
      waitFn,
      new Promise((_, reject) => {
        confirmTimer = setTimeout(() => reject(new Error(
          `Transaction not confirmed within ${timeoutMs / 1000}s (txHash: ${sentTx.hash}). It may still be pending — check on Etherscan.`
        )), timeoutMs);
      }),
    ]);
  } catch (confirmErr) {
    clearTimeout(confirmTimer);
    console.log(JSON.stringify({
      address,
      side: args.side,
      amountIn: args.amount,
      minAmountOut: args.minOut,
      txHash: sentTx.hash,
      status: 'unconfirmed',
      warning: `Transaction was broadcast but confirmation failed: ${confirmErr.message}. Check balance or Etherscan before retrying — the swap may have succeeded.`,
    }, null, 2));
    process.exit(1);
  }
  clearTimeout(confirmTimer);

  if (!receipt) {
    console.log(JSON.stringify({
      address,
      side: args.side,
      amountIn: args.amount,
      minAmountOut: args.minOut,
      txHash: sentTx.hash,
      status: 'unknown',
      warning: 'Transaction receipt is null — tx may have been dropped from mempool. Check on Etherscan.',
    }, null, 2));
    process.exit(1);
  }
  const failed = receipt.status !== 1;
  const result = {
    address,
    side: args.side,
    amountIn: args.amount,
    minAmountOut: args.minOut,
    txHash: sentTx.hash,
    status: failed ? 'failed' : 'success',
    gasUsed: receipt.gasUsed.toString(),
  };
  if (failed) {
    result.warning = 'Swap failed. A token approval may still be active — revoke it if you do not intend to retry.';
  }
  console.log(JSON.stringify(result, null, 2));
  if (failed) process.exit(1);
}

async function runSign(cfg, args) {
  if (!args.dataFile) throw new Error('--data-file is required for sign');

  const raw = readFileSync(args.dataFile, 'utf8');
  const { domain, types, message } = JSON.parse(raw);

  // ethers v6 derives EIP712Domain automatically — strip it to avoid conflicts
  const cleanTypes = { ...types };
  delete cleanTypes.EIP712Domain;

  const signer = await createSigner(cfg, null);
  const signature = await signer.signTypedData(domain, cleanTypes, message);
  // Output raw signature string (no JSON) to match cast wallet sign format
  process.stdout.write(signature);
}

async function runCancelNonce(cfg, provider, args) {
  if (!args.wordPos) throw new Error('--word-pos is required for cancel-nonce');
  if (!args.mask) throw new Error('--mask is required for cancel-nonce');

  // Validate wordPos and mask as valid uint256 values
  let wordPosBig, maskBig;
  try { wordPosBig = BigInt(args.wordPos); } catch { throw new Error(`--word-pos is not a valid integer: ${args.wordPos}`); }
  try { maskBig = BigInt(args.mask); } catch { throw new Error(`--mask is not a valid integer: ${args.mask}`); }
  if (wordPosBig < 0n || wordPosBig >= (1n << 248n)) throw new Error(`--word-pos out of range: ${args.wordPos}`);
  if (maskBig <= 0n || maskBig >= (1n << 256n)) throw new Error(`--mask out of range: ${args.mask}`);

  const signer = await createSigner(cfg, provider ? provider.getEthersProvider() : null);

  const permit2 = '0x000000000022D473030F116dDEE9F6B43aC78BA3';
  const iface = new Interface(['function invalidateUnorderedNonces(uint256 wordPos, uint256 mask)']);
  const data = iface.encodeFunctionData('invalidateUnorderedNonces', [wordPosBig, maskBig]);

  const tx = await signer.sendTransaction({ to: permit2, data });
  const receipt = await tx.wait();

  if (!receipt) {
    console.log(JSON.stringify({
      address: signer.address,
      txHash: tx.hash,
      status: 'unknown',
      warning: 'Transaction receipt is null — tx may have been dropped from mempool. Check on Etherscan.',
    }, null, 2));
    process.exit(1);
  }

  const failed = receipt.status !== 1;
  console.log(JSON.stringify({
    address: signer.address,
    txHash: tx.hash,
    status: failed ? 'failed' : 'success',
  }, null, 2));
  if (failed) process.exit(1);
}

// ---------------------------------------------------------------------------
// Helper: resolve pool fee from config.yaml pairs
// ---------------------------------------------------------------------------

function _resolveFee(cfg, symbolIn, symbolOut) {
  // Note: resolveToken() already restricts symbols to known tokens (USDT, XAUT),
  // so this function is only called with whitelisted pairs. The default fallback
  // exists as a safety net but should never be reached in normal operation.
  const pairs = cfg.yaml?.pairs ?? [];
  for (const pair of pairs) {
    if (!pair.enabled) continue;
    if (
      (pair.token_in === symbolIn && pair.token_out === symbolOut) ||
      (pair.token_in === symbolOut && pair.token_out === symbolIn)
    ) {
      return pair.fee_tier;
    }
  }
  throw new Error(`No enabled pair found for ${symbolIn}/${symbolOut} in config.yaml. Check your pairs configuration.`);
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

const isDirectRun =
  process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];

if (isDirectRun) {
  const argv = process.argv.slice(2);

  let parsed;
  try {
    parsed = parseCliArgs(argv);
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  }

  const cfg = loadConfig(parsed.configDir);
  validateContracts(cfg);
  const COMMANDS_NEEDING_PROVIDER = new Set([
    'address',
    'balance',
    'allowance',
    'quote',
    'approve',
    'swap',
    'cancel-nonce',
  ]);

  (async () => {
    try {
      const provider = COMMANDS_NEEDING_PROVIDER.has(parsed.command)
        ? createProvider(cfg.env)
        : null;

      switch (parsed.command) {
        case 'address':
          await runAddress(cfg, provider);
          break;
        case 'balance':
          await runBalance(cfg, provider);
          break;
        case 'allowance':
          await runAllowance(cfg, provider, parsed);
          break;
        case 'quote':
          await runQuote(cfg, provider, parsed);
          break;
        case 'approve':
          await runApprove(cfg, provider, parsed);
          break;
        case 'swap':
          await runSwap(cfg, provider, parsed);
          break;
        case 'sign':
          await runSign(cfg, parsed);
          break;
        case 'cancel-nonce':
          await runCancelNonce(cfg, provider, parsed);
          break;
      }
      process.exit(0);
    } catch (err) {
      console.error(JSON.stringify({ error: err.message }));
      process.exit(1);
    }
  })();
}
