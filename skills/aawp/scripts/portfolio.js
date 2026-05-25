#!/usr/bin/env node
/**
 * AAWP Cross-Chain Portfolio View
 *
 * Aggregates native + ERC-20 balances across ALL 6 chains in parallel.
 * Fetches USD prices from CoinGecko (public API, no key needed).
 * Uses Multicall3 per chain → single RPC call per chain for all token balances.
 *
 * Usage:
 *   portfolio.js                     Full cross-chain summary
 *   portfolio.js --chain base        Single chain only
 *   portfolio.js --no-prices         Skip USD conversion (faster)
 *   portfolio.js --json              Output raw JSON
 *   portfolio.js --hide-zero         Hide zero balances
 */
'use strict';

const net  = require('net');
const { ethers } = require('ethers');
const fs   = require('fs');
const path = require('path');
const https = require('https');

const S            = path.join(__dirname, '..');
const ENSURE_SCRIPT = path.join(__dirname, 'ensure-daemon.sh');
const CHAINS_FILE  = path.join(S, 'config/chains.json');
const CHAINS       = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));

// ── Multicall3 (deployed at same address on all major chains) ─────────────────
const MC3_ADDR = '0xcA11bde05977b3631167028862bE2a173976CA11';
const MC3_ABI  = [
  'function aggregate3(tuple(address target,bool allowFailure,bytes callData)[] calls) view returns (tuple(bool success,bytes returnData)[] returnData)',
];
const ERC20_IFACE = new ethers.Interface([
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
]);

// ── Factory ABI (to compute wallet address) ───────────────────────────────────
const FACTORY_ABI = [
  'function computeAddress(address signer, bytes32 logicHash, address guardian) view returns (address)',
];

// ── Extended token registry (more tokens than chains.json) ────────────────────
const EXTRA_TOKENS = {
  base: {
    USDC:  '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    WETH:  '0x4200000000000000000000000000000000000006',
    cbBTC: '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
    USDbC: '0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
    DAI:   '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
    AERO:  '0x940181a94A35A4569E4529A3CDfB74e38FD98631',
  },
  eth: {
    USDC:  '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    USDT:  '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    WETH:  '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    DAI:   '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    WBTC:  '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    LINK:  '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    UNI:   '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
    PEPE:  '0x6982508145454Ce325dDbE47a25d4ec3d2311933',
  },
  arb: {
    USDC:  '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    USDT:  '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
    WETH:  '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    DAI:   '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
    WBTC:  '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
    ARB:   '0x912CE59144191C1204E64559FE8253a0e49E6548',
    GMX:   '0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a',
  },
  op: {
    USDC:  '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    USDT:  '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
    WETH:  '0x4200000000000000000000000000000000000006',
    DAI:   '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
    WBTC:  '0x68f180fcCe6836688e9084f035309E29Bf0A2095',
    OP:    '0x4200000000000000000000000000000000000042',
  },
  polygon: {
    USDC:  '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    USDT:  '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
    WETH:  '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
    DAI:   '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
    WBTC:  '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
    WMATIC:'0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
    POL:   '0x0000000000000000000000000000000000001010',
  },
  bsc: {
    USDC:  '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
    USDT:  '0x55d398326f99059fF775485246999027B3197955',
    BUSD:  '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    WBNB:  '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    BTCB:  '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
    ETH:   '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
    CAKE:  '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
    XVS:   '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63',
  },
};

// ── CoinGecko symbol → ID mapping ─────────────────────────────────────────────
const CG_IDS = {
  ETH: 'ethereum', WETH: 'ethereum',
  BTC: 'bitcoin',  WBTC: 'wrapped-bitcoin', BTCB: 'bitcoin',
  BNB: 'binancecoin', WBNB: 'wbnb',
  MATIC: 'matic-network', WMATIC: 'wmatic', POL: 'matic-network',
  USDC: 'usd-coin', USDT: 'tether', DAI: 'dai', BUSD: 'binance-usd', USDbC: 'usd-coin',
  ARB: 'arbitrum', OP: 'optimism', LINK: 'chainlink',
  UNI: 'uniswap', CAKE: 'pancakeswap-token', XVS: 'venus',
  AERO: 'aerodrome-finance', GMX: 'gmx', PEPE: 'pepe', cbBTC: 'coinbase-wrapped-btc',
};

// ── Parse args ────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
let chainFilter = null;
let noPrices    = false;
let jsonOut     = false;
let hideZero    = false;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chain' && argv[i + 1]) chainFilter = argv[++i];
  else if (argv[i] === '--no-prices')        noPrices    = true;
  else if (argv[i] === '--json')             jsonOut     = true;
  else if (argv[i] === '--hide-zero')        hideZero    = true;
}

// ── Daemon ────────────────────────────────────────────────────────────────────
function getSock() {
  try { require('child_process').execSync(`bash "${ENSURE_SCRIPT}"`, { stdio: 'ignore' }); } catch {}
  const lockFile = '/tmp/.aawp-daemon.lock';
  if (!fs.existsSync(lockFile)) throw new Error('Daemon not running. Run: bash scripts/ensure-daemon.sh');
  const lines = fs.readFileSync(lockFile, 'utf8').trim().split('\n');
  if (!lines[1]) throw new Error('Socket path not found in lock file');
  return lines[1];
}

function socketQuery(obj) {
  const sock = getSock();
  return new Promise((resolve, reject) => {
    const c = net.createConnection(sock, () => c.end(JSON.stringify(obj)));
    let d = '';
    c.on('data', x => d += x);
    c.on('end', () => { try { resolve(JSON.parse(d)); } catch { reject(new Error('Bad response: ' + d)); } });
    c.on('error', reject);
    setTimeout(() => { c.destroy(); reject(new Error('Daemon timeout')); }, 15000);
  });
}

async function getWalletAddress(chain) {
  // Try AAWP_WALLET env first
  if (process.env.AAWP_WALLET) return process.env.AAWP_WALLET;

  const [addrResp, hashResp] = await Promise.all([
    socketQuery({ cmd: 'address' }),
    socketQuery({ cmd: 'logichash' }),
  ]);
  if (addrResp.error) throw new Error(addrResp.error);

  // Load guardian
  const guardianFile = path.join(S, 'config/guardian.json');
  const guardian = JSON.parse(fs.readFileSync(guardianFile, 'utf8'));

  const provider = new ethers.JsonRpcProvider(chain.rpcOverride || chain.rpc);
  const factory  = new ethers.Contract(chain.factory, FACTORY_ABI, provider);
  return await factory.computeAddress(addrResp.address, hashResp.logicHash, guardian.address);
}

// ── CoinGecko price fetch ─────────────────────────────────────────────────────
function fetchPrices(symbols) {
  const ids = [...new Set(symbols.map(s => CG_IDS[s]).filter(Boolean))];
  if (!ids.length) return Promise.resolve({});

  return new Promise((resolve) => {
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids.join(',')}&vs_currencies=usd`;
    https.get(url, { headers: { 'User-Agent': 'AAWP-Portfolio/1.0' } }, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try {
          const raw = JSON.parse(data);
          // Map back: { SYMBOL: usdPrice }
          const out = {};
          for (const sym of symbols) {
            const id = CG_IDS[sym];
            if (id && raw[id]?.usd) out[sym] = raw[id].usd;
          }
          resolve(out);
        } catch { resolve({}); }
      });
    }).on('error', () => resolve({}));
  });
}

// ── Per-chain balance query ───────────────────────────────────────────────────
async function queryChain(chainKey, cfg, walletAddr) {
  const provider = new ethers.JsonRpcProvider(cfg.rpcOverride || cfg.rpc);
  const tokens   = EXTRA_TOKENS[chainKey] || {};
  const result   = { chain: chainKey, name: cfg.name, wallet: walletAddr, native: null, tokens: [] };

  // Native balance
  try {
    const nativeBal = await provider.getBalance(walletAddr);
    result.native = {
      symbol:   cfg.nativeCurrency,
      balance:  ethers.formatEther(nativeBal),
      raw:      nativeBal.toString(),
      decimals: 18,
    };
  } catch (e) {
    result.native = { symbol: cfg.nativeCurrency, balance: '0', raw: '0', decimals: 18, error: e.message };
  }

  // ERC-20 via Multicall3 (one RPC call for all tokens)
  const entries = Object.entries(tokens);
  if (entries.length > 0) {
    const calls = entries.flatMap(([, addr]) => [
      { target: addr, allowFailure: true, callData: ERC20_IFACE.encodeFunctionData('decimals') },
      { target: addr, allowFailure: true, callData: ERC20_IFACE.encodeFunctionData('balanceOf', [walletAddr]) },
    ]);

    try {
      const mc3     = new ethers.Contract(MC3_ADDR, MC3_ABI, provider);
      const results = await mc3.aggregate3(calls);

      for (let i = 0; i < entries.length; i++) {
        const [sym, addr] = entries[i];
        const decRes = results[i * 2];
        const balRes = results[i * 2 + 1];
        try {
          if (!decRes.success || !balRes.success) throw new Error('call failed');
          const dec = Number(ERC20_IFACE.decodeFunctionResult('decimals', decRes.returnData)[0]);
          const bal = ERC20_IFACE.decodeFunctionResult('balanceOf', balRes.returnData)[0];
          result.tokens.push({
            symbol:   sym,
            address:  addr,
            balance:  ethers.formatUnits(bal, dec),
            raw:      bal.toString(),
            decimals: dec,
          });
        } catch {
          result.tokens.push({ symbol: sym, address: addr, balance: '0', raw: '0', decimals: 18 });
        }
      }
    } catch {
      // Multicall not available, fall back to individual calls
      for (const [sym, addr] of entries) {
        try {
          const token = new ethers.Contract(addr, ERC20_IFACE, provider);
          const [dec, bal] = await Promise.all([token.decimals(), token.balanceOf(walletAddr)]);
          result.tokens.push({ symbol: sym, address: addr, balance: ethers.formatUnits(bal, Number(dec)), raw: bal.toString(), decimals: Number(dec) });
        } catch {
          result.tokens.push({ symbol: sym, address: addr, balance: '0', raw: '0', decimals: 18 });
        }
      }
    }
  }

  return result;
}

// ── Display ───────────────────────────────────────────────────────────────────
function formatBalance(bal, decimals = 4) {
  const n = parseFloat(bal);
  if (n === 0) return '0';
  if (n < 0.0001) return n.toExponential(2);
  return n.toFixed(decimals);
}

function formatUSD(val) {
  if (val === null || val === undefined) return '';
  if (val >= 1e6)  return `$${(val / 1e6).toFixed(2)}M`;
  if (val >= 1000) return `$${(val / 1000).toFixed(2)}K`;
  return `$${val.toFixed(2)}`;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const targetChains = chainFilter
    ? { [chainFilter]: CHAINS[chainFilter] }
    : CHAINS;

  if (!Object.keys(targetChains).length || (chainFilter && !CHAINS[chainFilter])) {
    console.error(`❌ Unknown chain: ${chainFilter}. Valid: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }

  if (!jsonOut) {
    console.log('\n🌐 AAWP Cross-Chain Portfolio');
    console.log('   Querying all chains in parallel...\n');
  }

  // Get wallet address (use first chain to compute — same address all chains)
  const firstChain = Object.entries(targetChains)[0];
  let walletAddr;
  try {
    walletAddr = await getWalletAddress({ ...firstChain[1] });
  } catch (e) {
    console.error(`❌ Cannot get wallet address: ${e.message}`);
    process.exit(1);
  }

  if (!jsonOut) {
    console.log(`   Wallet: ${walletAddr}\n`);
    console.log('   Fetching balances...');
  }

  // Query all chains in parallel
  const chainResults = await Promise.all(
    Object.entries(targetChains).map(([key, cfg]) =>
      queryChain(key, cfg, walletAddr).catch(e => ({
        chain: key, name: cfg.name, wallet: walletAddr,
        native: null, tokens: [], error: e.message,
      }))
    )
  );

  // Collect all unique symbols for price fetch
  let prices = {};
  if (!noPrices) {
    const allSymbols = new Set();
    for (const r of chainResults) {
      if (r.native) allSymbols.add(r.native.symbol);
      for (const t of r.tokens) allSymbols.add(t.symbol);
    }
    try {
      prices = await fetchPrices([...allSymbols]);
    } catch { /* prices stay empty */ }
  }

  // ── JSON output ──────────────────────────────────────────────────────────────
  if (jsonOut) {
    const out = { wallet: walletAddr, chains: chainResults, prices, timestamp: new Date().toISOString() };
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  // ── Human-readable output ────────────────────────────────────────────────────
  let grandTotal = 0;
  const allRows  = []; // for summary table

  for (const r of chainResults) {
    if (r.error) {
      console.log(`\n❌ ${r.name.toUpperCase()} — Error: ${r.error}`);
      continue;
    }

    const chainTotal = { usd: 0 };
    const rows = [];

    // Native token
    if (r.native) {
      const bal = parseFloat(r.native.balance);
      const usdPrice = prices[r.native.symbol] || null;
      const usd = usdPrice ? bal * usdPrice : null;
      if (usd) chainTotal.usd += usd;
      if (!hideZero || bal > 0) {
        rows.push({ sym: r.native.symbol, bal, usd });
        allRows.push({ chain: r.chain, sym: r.native.symbol, bal, usd });
      }
    }

    // ERC-20 tokens
    for (const t of r.tokens) {
      const bal = parseFloat(t.balance);
      if (hideZero && bal < 0.000001) continue;
      const usdPrice = prices[t.symbol] || null;
      const usd = usdPrice ? bal * usdPrice : null;
      if (usd) chainTotal.usd += usd;
      rows.push({ sym: t.symbol, bal, usd });
      allRows.push({ chain: r.chain, sym: t.symbol, bal, usd });
    }

    grandTotal += chainTotal.usd;

    // Print chain section
    const chainUsdStr = chainTotal.usd > 0 ? `  ${formatUSD(chainTotal.usd)}` : '';
    console.log(`\n  ┌─ ${r.name.toUpperCase()}${chainUsdStr}`);
    for (const row of rows) {
      if (row.bal < 0.000001 && hideZero) continue;
      const balStr = formatBalance(row.bal).padStart(18);
      const usdStr = row.usd ? `  ${formatUSD(row.usd)}` : '';
      console.log(`  │  ${row.sym.padEnd(8)} ${balStr}${usdStr}`);
    }
    if (rows.length === 0) console.log('  │  (no balances)');
    console.log('  └' + '─'.repeat(40));
  }

  // ── Summary ───────────────────────────────────────────────────────────────────
  if (grandTotal > 0) {
    console.log(`\n${'─'.repeat(44)}`);
    console.log(`  TOTAL PORTFOLIO VALUE: ${formatUSD(grandTotal)}`);
    console.log(`${'─'.repeat(44)}`);
  }

  // ── Top holdings ──────────────────────────────────────────────────────────────
  const withUsd = allRows.filter(r => r.usd && r.usd > 0.01);
  if (withUsd.length > 1) {
    withUsd.sort((a, b) => b.usd - a.usd);
    console.log('\n  Top Holdings:');
    for (const r of withUsd.slice(0, 8)) {
      const pct = grandTotal > 0 ? ((r.usd / grandTotal) * 100).toFixed(1) + '%' : '';
      console.log(`    ${r.sym.padEnd(8)} on ${r.chain.padEnd(8)} ${formatBalance(r.bal).padStart(14)}  ${formatUSD(r.usd).padStart(10)}  ${pct}`);
    }
  }

  // ── Per-token aggregation (same token across chains) ──────────────────────────
  const bySymbol = {};
  for (const r of allRows) {
    if (!bySymbol[r.sym]) bySymbol[r.sym] = { bal: 0, usd: 0, chains: [] };
    bySymbol[r.sym].bal += r.bal;
    if (r.usd) bySymbol[r.sym].usd += r.usd;
    if (r.bal > 0.000001) bySymbol[r.sym].chains.push(r.chain);
  }

  const multiChain = Object.entries(bySymbol).filter(([, v]) => v.chains.length > 1 && v.bal > 0.000001);
  if (multiChain.length > 0) {
    console.log('\n  Multi-chain Holdings:');
    for (const [sym, v] of multiChain) {
      const usdStr = v.usd > 0 ? `  ${formatUSD(v.usd)}` : '';
      console.log(`    ${sym.padEnd(8)} ${formatBalance(v.bal).padStart(14)}${usdStr}  [${v.chains.join(', ')}]`);
    }
  }

  if (!noPrices && Object.keys(prices).length === 0) {
    console.log('\n  ⚠️  Price data unavailable (CoinGecko rate limited). Use --no-prices to skip.');
  }

  console.log();
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
