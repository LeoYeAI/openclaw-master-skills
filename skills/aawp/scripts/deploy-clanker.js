#!/usr/bin/env node
/**
 * deploy-clanker.js — Deploy a token on Clanker V4 via your AAWP wallet
 *
 * Supported chains (Clanker V4):
 *   base (8453) · eth (1) · arb (42161) · unichain (130) · bera (143) · bsc (56)
 *
 * Usage:
 *   node deploy-clanker.js              # interactive prompts
 *   node deploy-clanker.js --dry-run    # preview config only, no broadcast
 *
 * Or fill in CONFIG below and run directly.
 */

'use strict';
const { execFileSync } = require('child_process');
const readline         = require('readline');
const path             = require('path');

const SKILL = path.resolve(__dirname, '..');
const WM    = path.resolve(SKILL, 'scripts/wallet-manager.js');

const { createPublicClient, http, encodeFunctionData, formatEther } = require('viem');
const { base, mainnet, arbitrum, bsc }  = require('viem/chains');
const { Clanker }                                         = require('clanker-sdk/v4');
const { ClankerDeployments, POOL_POSITIONS, FEE_CONFIGS } = require('clanker-sdk');

const DRY_RUN = process.argv.includes('--dry-run');

// ─────────────────────────────────────────────────────────────────────────────
// CHAIN CONFIG
// ─────────────────────────────────────────────────────────────────────────────
const CHAINS = {
  base:     { id: 8453,  name: 'Base',      rpc: 'https://mainnet.base.org',           viemChain: base,    explorer: 'https://basescan.org' },
  eth:      { id: 1,     name: 'Ethereum',  rpc: 'https://eth.llamarpc.com',            viemChain: mainnet, explorer: 'https://etherscan.io' },
  arb:      { id: 42161, name: 'Arbitrum',  rpc: 'https://arb1.arbitrum.io/rpc',       viemChain: arbitrum,explorer: 'https://arbiscan.io' },
  unichain: { id: 130,   name: 'Unichain',  rpc: 'https://mainnet.unichain.org',       viemChain: base,    explorer: 'https://uniscan.xyz' },
  bera:     { id: 143,   name: 'Berachain', rpc: 'https://rpc.berachain.com',          viemChain: base,    explorer: 'https://berascan.com' },
  bsc:      { id: 56,    name: 'BSC',       rpc: 'https://bsc-dataseed1.binance.org',  viemChain: bsc,     explorer: 'https://bscscan.com' },
};

// ─────────────────────────────────────────────────────────────────────────────
// ★ EDIT THIS SECTION TO CONFIGURE YOUR TOKEN ★
// ─────────────────────────────────────────────────────────────────────────────
const CONFIG = {

  // ── Chain ──────────────────────────────────────────────────────────────────
  chain: 'base',            // base | eth | arb | unichain | bera | bsc

  // ── Token identity ─────────────────────────────────────────────────────────
  name:        'My Token',
  symbol:      'MTK',
  image:       'https://example.com/logo.png',  // Square image URL (1:1 ratio)
  description: 'A short description of what this token is about.',
  website:     '',                               // Optional: https://yoursite.com
  twitter:     '',                               // Optional: https://x.com/yourhandle

  // ── Pool / market cap ──────────────────────────────────────────────────────
  initialMarketCap: 10,       // ETH value at launch (min ~10 ETH ≈ $25K FDV)
  poolPositions:    'Standard',   // Standard | Project | TwentyETH
  feeConfig:        'StaticBasic',// StaticBasic (1%) | DynamicBasic | Dynamic3

  // ── Dev buy ────────────────────────────────────────────────────────────────
  devBuyEth: 0.003,           // ETH to spend buying at launch. 0 to skip.

  // ── Vault (optional) ───────────────────────────────────────────────────────
  vault: {
    enabled:     false,       // set true to enable
    percentage:  20,          // % of total supply to lock (1–90)
    lockupDays:  7,           // cliff before any unlock (min 7 days)
    vestingDays: 180,         // linear vesting after cliff (0 = instant after cliff)
    // recipient defaults to tokenAdmin (AAWP wallet)
  },

  // ── Admin & rewards ────────────────────────────────────────────────────────
  // null = use AAWP wallet automatically
  tokenAdmin:      null,
  rewardRecipient: null,
};
// ─────────────────────────────────────────────────────────────────────────────

// ── Helpers ──────────────────────────────────────────────────────────────────
const bold   = s => `\x1b[1m${s}\x1b[0m`;
const green  = s => `\x1b[32m${s}\x1b[0m`;
const cyan   = s => `\x1b[36m${s}\x1b[0m`;
const yellow = s => `\x1b[33m${s}\x1b[0m`;
const red    = s => `\x1b[31m${s}\x1b[0m`;

function ask(rl, q) {
  return new Promise(r => rl.question(q, r));
}

function getAawpWallet() {
  if (process.env.AAWP_WALLET) return process.env.AAWP_WALLET;
  try {
    const out = execFileSync(process.execPath, [WM, '--chain', CONFIG.chain, 'status'], {
      encoding: 'utf8', timeout: 15_000, env: { ...process.env },
    });
    const m = out.match(/Wallet[:\s]+0x([0-9a-fA-F]{40})/i) ||
              out.match(/(0x[0-9a-fA-F]{40})/);
    if (m) return m[0].startsWith('0x') ? m[0] : '0x' + m[1];
  } catch {}
  throw new Error(
    'Could not resolve AAWP wallet. Set AAWP_WALLET env or run:\n  node scripts/wallet-manager.js status'
  );
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const chain = CHAINS[CONFIG.chain];
  if (!chain) {
    console.error(red(`Unknown chain "${CONFIG.chain}". Supported: ${Object.keys(CHAINS).join(', ')}`));
    process.exit(1);
  }

  const clankerDeps = ClankerDeployments[chain.id];
  if (!clankerDeps?.clanker_v4) {
    console.error(red(`Clanker V4 not deployed on "${CONFIG.chain}" (chainId: ${chain.id})`));
    process.exit(1);
  }
  const FACTORY = clankerDeps.clanker_v4.address;

  let walletAddr;
  try { walletAddr = getAawpWallet(); }
  catch (e) { console.error(red(e.message)); process.exit(1); }

  const tokenAdmin      = CONFIG.tokenAdmin      ?? walletAddr;
  const rewardRecipient = CONFIG.rewardRecipient ?? walletAddr;

  // ── Config summary ─────────────────────────────────────────────────────────
  console.log('\n' + bold('═══════════════════════════════════════════════'));
  console.log(bold('  Clanker V4 Token Deploy'));
  console.log(bold('═══════════════════════════════════════════════'));
  console.log(`  Chain        : ${cyan(chain.name)} (${chain.id})`);
  console.log(`  Factory      : ${FACTORY}`);
  console.log(`  Name / Ticker: ${bold(CONFIG.name)} / $${CONFIG.symbol}`);
  console.log(`  Image        : ${CONFIG.image}`);
  console.log(`  Initial MCAP : ${CONFIG.initialMarketCap} ETH`);
  console.log(`  Dev buy      : ${CONFIG.devBuyEth} ETH`);
  console.log(`  Fee config   : ${CONFIG.feeConfig}`);
  console.log(`  Pool         : ${CONFIG.poolPositions}`);
  console.log(`  Token admin  : ${tokenAdmin}`);
  console.log(`  LP rewards → : ${rewardRecipient}`);
  if (CONFIG.vault.enabled) {
    console.log(`  Vault        : ${yellow(`${CONFIG.vault.percentage}% | cliff ${CONFIG.vault.lockupDays}d + vest ${CONFIG.vault.vestingDays}d linear`)}`);
  } else {
    console.log(`  Vault        : none (fair launch)`);
  }
  if (CONFIG.website) console.log(`  Website      : ${CONFIG.website}`);
  if (CONFIG.twitter) console.log(`  Twitter      : ${CONFIG.twitter}`);
  console.log('');

  if (DRY_RUN) {
    console.log(yellow('DRY RUN — no transaction broadcast.'));
    return;
  }

  // Interactive confirmation
  if (process.stdin.isTTY) {
    const rl  = readline.createInterface({ input: process.stdin, output: process.stdout });
    const ans = await ask(rl, `Deploy ${bold('$' + CONFIG.symbol)} on ${chain.name}? (yes/no): `);
    rl.close();
    if (ans.trim().toLowerCase() !== 'yes') {
      console.log('Cancelled.');
      process.exit(0);
    }
    console.log('');
  }

  // ── Build token config ─────────────────────────────────────────────────────
  const socialUrls = [];
  if (CONFIG.twitter) socialUrls.push({ platform: 'x',       url: CONFIG.twitter });
  if (CONFIG.website) socialUrls.push({ platform: 'website', url: CONFIG.website });

  const tokenConfig = {
    chainId: chain.id,
    name:    CONFIG.name,
    symbol:  CONFIG.symbol,
    image:   CONFIG.image,
    metadata: {
      description: CONFIG.description,
      ...(socialUrls.length ? { socialMediaUrls: socialUrls } : {}),
    },
    context: {
      interface: 'AAWP',
      platform:  'AAWP',
      messageId: `${CONFIG.symbol.toLowerCase()}-${Date.now()}`,
      id:        CONFIG.symbol,
    },
    tokenAdmin,
    pool: {
      pairedToken:      'WETH',
      initialMarketCap: CONFIG.initialMarketCap,
      positions:        POOL_POSITIONS[CONFIG.poolPositions],
    },
    fees:    FEE_CONFIGS[CONFIG.feeConfig],
    rewards: {
      recipients: [{
        admin:     tokenAdmin,
        recipient: rewardRecipient,
        bps:       10000,
        token:     'Both',
      }],
    },
    ...(CONFIG.devBuyEth > 0 ? { devBuy: { ethAmount: CONFIG.devBuyEth } } : {}),
    ...(CONFIG.vault.enabled ? {
      vault: {
        percentage:      CONFIG.vault.percentage,
        lockupDuration:  CONFIG.vault.lockupDays  * 86400,
        vestingDuration: CONFIG.vault.vestingDays * 86400,
        recipient:       rewardRecipient,
      },
    } : {}),
  };

  // ── Get deploy calldata ────────────────────────────────────────────────────
  console.log('Building calldata...');
  const publicClient = createPublicClient({
    chain: { ...chain.viemChain, id: chain.id },
    transport: http(chain.rpc),
  });
  const clanker  = new Clanker({ publicClient });
  const tx       = await clanker.getDeployTransaction(tokenConfig);
  const calldata = encodeFunctionData({ abi: tx.abi, functionName: tx.functionName, args: tx.args });

  console.log(`  Calldata : ${calldata.length / 2 - 1} bytes`);
  console.log(`  Value    : ${formatEther(tx.value ?? 0n)} ETH\n`);

  // ── Send via AAWP wallet ───────────────────────────────────────────────────
  console.log(`Sending via AAWP wallet ${walletAddr}...`);
  const result = execFileSync(process.execPath, [
    WM,
    '--chain', CONFIG.chain,
    'call',
    '--value',     String(CONFIG.devBuyEth > 0 ? CONFIG.devBuyEth : 0),
    '--gas-limit', '8000000',
    FACTORY,
    calldata,
  ], {
    encoding: 'utf8',
    timeout:  120_000,
    env: { ...process.env, AAWP_WALLET: walletAddr },
  });

  console.log(result);

  // ── Extract token address from receipt ────────────────────────────────────
  const txMatch = result.match(/\/tx\/(0x[0-9a-fA-F]{64})/i) ||
                  result.match(/TX[:\s]+(0x[0-9a-fA-F]{64})/i);
  if (txMatch) {
    try {
      const receipt = await publicClient.getTransactionReceipt({ hash: txMatch[1] });
      const addr    = receipt.logs[0]?.address;
      console.log(green('═══════════════════════════════════'));
      console.log(green('  ✅ Token deployed!'));
      console.log(green('═══════════════════════════════════'));
      if (addr) {
        console.log(`\n  Token    : ${bold(addr)}`);
        console.log(`  Explorer : ${chain.explorer}/address/${addr}`);
        console.log(`  Clanker  : https://clanker.world/clanker/${addr}`);
      }
      console.log(`  TX       : ${chain.explorer}/tx/${txMatch[1]}\n`);
    } catch {}
  }
}

main().catch(e => {
  console.error(red('\n' + (e.shortMessage || e.message || e)));
  if (e.stderr) console.error(e.stderr.toString());
  process.exit(1);
});
