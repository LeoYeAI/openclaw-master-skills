#!/usr/bin/env node
/**
 * AAWP Yield Manager — Aave V3 DeFi Integration
 *
 * Supports: supply, withdraw, borrow, repay, positions, rates
 * Chains:   base, eth, arb, op, polygon (Aave V3 deployed)
 *           bsc — Venus Protocol fallback
 *
 * Usage:
 *   yield.js --chain base positions              Show all Aave positions
 *   yield.js --chain base rates                  Show current APY rates
 *   yield.js --chain base supply USDC 1000       Supply 1000 USDC
 *   yield.js --chain base withdraw USDC 500      Withdraw 500 USDC
 *   yield.js --chain base borrow USDC 200        Borrow 200 USDC (variable rate)
 *   yield.js --chain base repay USDC 200         Repay 200 USDC
 *   yield.js --chain base borrow USDC 200 --rate stable   Stable rate borrow
 *   yield.js --chain eth supply ETH 0.1          Supply native ETH (wrapped)
 */
'use strict';

const net = require('net');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const S = path.join(__dirname, '..');
const ENSURE_SCRIPT = path.join(__dirname, 'ensure-daemon.sh');
const CHAINS_FILE = path.join(S, 'config/chains.json');
const CHAINS = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));

// ── Aave V3 Pool addresses (official deployments) ────────────────────────────
const AAVE_POOLS = {
  eth:     '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
  base:    '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5',
  arb:     '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
  op:      '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
  polygon: '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
};

// Aave V3 Pool Data Provider (for rates/balances)
const AAVE_DATA_PROVIDERS = {
  eth:     '0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3',
  base:    '0x2d8A3C5677189723C4cB8873CfC9C8976dfe98b8',
  arb:     '0x69FA688f1Dc47d4B5d8029D5a35FB7a548310654',
  op:      '0x69FA688f1Dc47d4B5d8029D5a35FB7a548310654',
  polygon: '0x9441B65EE553F70df9C77d45d3283B6BC24F222d',
};

// ── Venus Protocol (BSC) ──────────────────────────────────────────────────────
// Venus V4 Core Pool on BSC
const VENUS_COMPTROLLER = '0xfD36E2c2a6789Db23113685031d7F16329158384';
const VENUS_LENS        = '0x8Ed9f862363A7CCa2D75bb4Ff071F5a6506df6DE';

// Venus vToken addresses (BSC mainnet)
const VENUS_VTOKENS = {
  BNB:  '0xA07c5b74C9B40447a954e1466938b865b6BBea36', // vBNB
  USDC: '0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8', // vUSDC
  USDT: '0xfD5840Cd36d94D7229439859C0112a4185BC0255', // vUSDT
  BUSD: '0x95c78222B3D6e262426483D42CfA53685A67Ab9D', // vBUSD
  BTC:  '0x882C173bC7Ff3b7786CA16dfeD3DFFfb9Ee7847B', // vBTC
  ETH:  '0xf508fCD89b8bd15579dc79A6827cB4686A3592c8', // vETH
  XVS:  '0x151B1e2635A717bcDc836ECd6FbB62B674FE3E1D', // vXVS
};

const VENUS_VTOKEN_ABI = [
  'function mint(uint256 mintAmount) returns (uint256)',          // supply ERC-20
  'function mint() payable',                                      // supply BNB
  'function redeem(uint256 redeemTokens) returns (uint256)',      // withdraw by vToken
  'function redeemUnderlying(uint256 redeemAmount) returns (uint256)', // withdraw by underlying
  'function borrow(uint256 borrowAmount) returns (uint256)',
  'function repayBorrow(uint256 repayAmount) returns (uint256)',
  'function repayBorrow() payable',                               // repay BNB
  'function balanceOf(address owner) view returns (uint256)',
  'function balanceOfUnderlying(address owner) returns (uint256)',
  'function borrowBalanceCurrent(address account) returns (uint256)',
  'function exchangeRateCurrent() returns (uint256)',
  'function supplyRatePerBlock() view returns (uint256)',
  'function borrowRatePerBlock() view returns (uint256)',
  'function getCash() view returns (uint256)',
  'function underlying() view returns (address)',
];

const VENUS_COMPTROLLER_ABI = [
  'function getAccountLiquidity(address account) view returns (uint256 err, uint256 liquidity, uint256 shortfall)',
  'function enterMarkets(address[] calldata vTokens) returns (uint256[])',
  'function getAssetsIn(address account) view returns (address[])',
];

const BSC_BLOCKS_PER_YEAR = 10512000; // ~3s block time

// WETHGateway for native ETH supply/withdraw on ETH/Optimism/Arbitrum/Base
const WETH_GATEWAYS = {
  eth:     '0xD322A49006FC828F9B5B37Ab215F99B4E5caB19C',
  base:    '0x3D452F37b3C72F08B7f2Ad3a6Eb71d58a25dCFCA', // may vary, use supply with WETH
  arb:     '0xbcca60bb61934080951369a648fb03df4f96263c',
  op:      '0xbcca60bb61934080951369a648fb03df4f96263c',
  polygon: '0xAeBF56223F044a73D90b1d7113d53faF767B8dF4',
};

// Common WETH addresses
const WETH = {
  eth:     '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  base:    '0x4200000000000000000000000000000000000006',
  arb:     '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
  op:      '0x4200000000000000000000000000000000000006',
  polygon: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
};

// Aave V3 Pool ABI (minimal)
const POOL_ABI = [
  'function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)',
  'function withdraw(address asset, uint256 amount, address to) returns (uint256)',
  'function borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)',
  'function repay(address asset, uint256 amount, uint256 interestRateMode, address onBehalfOf) returns (uint256)',
  'function getUserAccountData(address user) view returns (uint256 totalCollateralBase, uint256 totalDebtBase, uint256 availableBorrowsBase, uint256 currentLiquidationThreshold, uint256 ltv, uint256 healthFactor)',
];

// Aave Data Provider ABI
const DATA_PROVIDER_ABI = [
  'function getReserveData(address asset) view returns (uint256 unbacked, uint256 accruedToTreasuryScaled, uint256 totalAToken, uint256 totalStableDebt, uint256 totalVariableDebt, uint256 liquidityRate, uint256 variableBorrowRate, uint256 stableBorrowRate, uint256 averageStableBorrowRate, uint256 liquidityIndex, uint256 variableBorrowIndex, uint40 lastUpdateTimestamp)',
  'function getUserReserveData(address asset, address user) view returns (uint256 currentATokenBalance, uint256 currentStableDebt, uint256 currentVariableDebt, uint256 principalStableDebt, uint256 scaledVariableDebt, uint256 stableBorrowRate, uint256 liquidityRate, uint40 stableRateLastUpdated, bool usageAsCollateralEnabled)',
  'function getAllReservesTokens() view returns (tuple(string symbol, address tokenAddress)[])',
];

const ERC20_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function balanceOf(address) view returns (uint256)',
];

// ── Token address registry per chain ─────────────────────────────────────────
// BSC token addresses (for approve checks in Venus)
const BSC_TOKENS = {
  USDC: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
  USDT: '0x55d398326f99059fF775485246999027B3197955',
  BUSD: '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
  BTC:  '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c', // BTCB
  ETH:  '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
  XVS:  '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63',
};

const TOKEN_ADDRESSES = {
  eth: {
    USDC: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    USDT: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    DAI:  '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    WBTC: '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    WETH: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  },
  base: {
    USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    WETH: '0x4200000000000000000000000000000000000006',
    cbBTC:'0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
    USDbC:'0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
  },
  arb: {
    USDC: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    USDT: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
    WETH: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    WBTC: '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
    DAI:  '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
  },
  op: {
    USDC: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    USDT: '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
    WETH: '0x4200000000000000000000000000000000000006',
    DAI:  '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
    WBTC: '0x68f180fcCe6836688e9084f035309E29Bf0A2095',
  },
  polygon: {
    USDC: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    USDT: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
    WETH: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
    WBTC: '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
    DAI:  '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
    WMATIC:'0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
  },
  bsc: BSC_TOKENS,
};

// ── Parse args ────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
let chainArg = 'base';
let rateMode = 2; // 1=stable, 2=variable
const filteredArgv = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chain' && argv[i + 1]) { chainArg = argv[++i]; }
  else if ((argv[i] === '--rate' || argv[i] === '--rate-mode') && argv[i + 1]) {
    const m = argv[++i];
    rateMode = (m === 'stable' || m === '1') ? 1 : 2;
  } else filteredArgv.push(argv[i]);
}

const cmd = filteredArgv[0];

// ── Helpers ───────────────────────────────────────────────────────────────────
function getChain(key) {
  const cfg = CHAINS[key];
  if (!cfg) {
    console.error(`❌ Unknown chain: ${key}. Valid: ${Object.keys(CHAINS).join(', ')}`);
    process.exit(1);
  }
  if (!AAVE_POOLS[key] && key !== 'bsc') {
    console.error(`❌ No yield protocol on ${key}. Supported: ${[...Object.keys(AAVE_POOLS), 'bsc'].join(', ')}`);
    process.exit(1);
  }
  return cfg;
}

function isBSC(key) { return key === 'bsc'; }

function resolveVenusToken(sym) {
  const upper = sym.toUpperCase();
  const vToken = VENUS_VTOKENS[upper];
  if (!vToken) {
    console.error(`❌ Unknown Venus token: ${sym}. Supported: ${Object.keys(VENUS_VTOKENS).join(', ')}`);
    process.exit(1);
  }
  return { vToken, symbol: upper, isNative: upper === 'BNB' };
}

// ── Venus (BSC) helpers ───────────────────────────────────────────────────────

async function venusRates(chain) {
  const provider = getProvider(chain);
  console.log(`\n📊 Venus Protocol Rates — ${chain.name}\n`);
  console.log(`${'Token'.padEnd(8)} ${'Supply APY'.padStart(12)} ${'Borrow APY'.padStart(12)}`);
  console.log('─'.repeat(36));
  for (const [sym, vAddr] of Object.entries(VENUS_VTOKENS)) {
    try {
      const vt = new ethers.Contract(vAddr, VENUS_VTOKEN_ABI, provider);
      const [supplyRate, borrowRate] = await Promise.all([
        vt.supplyRatePerBlock(),
        vt.borrowRatePerBlock(),
      ]);
      const supplyAPY = ((Number(supplyRate) / 1e18) * BSC_BLOCKS_PER_YEAR * 100).toFixed(2) + '%';
      const borrowAPY = ((Number(borrowRate) / 1e18) * BSC_BLOCKS_PER_YEAR * 100).toFixed(2) + '%';
      console.log(`${sym.padEnd(8)} ${supplyAPY.padStart(12)} ${borrowAPY.padStart(12)}`);
    } catch {
      console.log(`${sym.padEnd(8)} ${'N/A'.padStart(12)} ${'N/A'.padStart(12)}`);
    }
  }
  console.log();
}

async function venusPositions(chain) {
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const comptroller = new ethers.Contract(VENUS_COMPTROLLER, VENUS_COMPTROLLER_ABI, provider);

  console.log(`\n🏦 Venus Protocol Positions — ${chain.name}`);
  console.log(`   Wallet: ${walletAddr}`);

  const [, liquidity, shortfall] = await comptroller.getAccountLiquidity(walletAddr);
  console.log(`   Available Liquidity: $${(Number(liquidity) / 1e18).toFixed(2)}`);
  if (Number(shortfall) > 0) console.log(`   ⚠️  SHORTFALL: $${(Number(shortfall) / 1e18).toFixed(2)} — RISK OF LIQUIDATION`);

  console.log(`\n   ${'Token'.padEnd(8)} ${'Supplied'.padStart(14)} ${'Borrowed'.padStart(14)}`);
  console.log('   ' + '─'.repeat(40));

  let hasPos = false;
  for (const [sym, vAddr] of Object.entries(VENUS_VTOKENS)) {
    try {
      const vt = new ethers.Contract(vAddr, VENUS_VTOKEN_ABI, provider);
      const [supplied, borrowed] = await Promise.all([
        vt.balanceOfUnderlying(walletAddr),
        vt.borrowBalanceCurrent(walletAddr),
      ]);
      const s = Number(supplied) / 1e18;
      const b = Number(borrowed) / 1e18;
      if (s > 0.000001 || b > 0.000001) {
        hasPos = true;
        console.log(`   ${sym.padEnd(8)} ${s.toFixed(6).padStart(14)} ${b.toFixed(6).padStart(14)}`);
      }
    } catch {}
  }
  if (!hasPos) console.log('   No active positions.');
  console.log();
}

async function venusSupply(chain, sym, amount) {
  const { vToken, symbol, isNative } = resolveVenusToken(sym);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);
  const comptroller = new ethers.Contract(VENUS_COMPTROLLER, VENUS_COMPTROLLER_ABI, provider);

  // Enter market first (enables as collateral)
  const assetsIn = await comptroller.getAssetsIn(walletAddr);
  if (!assetsIn.map(a => a.toLowerCase()).includes(vToken.toLowerCase())) {
    console.log(`📌 Entering Venus market for ${symbol}...`);
    const iface = new ethers.Interface(VENUS_COMPTROLLER_ABI);
    const data = iface.encodeFunctionData('enterMarkets', [[vToken]]);
    const r = await sendTx(chain, { to: VENUS_COMPTROLLER, data, value: BigInt(0) });
    console.log(`✅ Market entered (block ${r.blockNumber})`);
  }

  const amountWei = ethers.parseEther(amount.toString());
  console.log(`\n💰 Supplying ${amount} ${symbol} to Venus (BSC)...`);

  if (isNative) {
    // vBNB: call mint() payable
    const iface = new ethers.Interface(VENUS_VTOKEN_ABI);
    const data = iface.encodeFunctionData('mint()');
    const receipt = await sendTx(chain, { to: vToken, data, value: amountWei });
    console.log(`✅ Supplied BNB! Block: ${receipt.blockNumber}\n   TX: ${chain.explorer}/tx/${receipt.hash}`);
  } else {
    // ERC-20: approve then mint(amount)
    const underlying = BSC_TOKENS[symbol];
    if (!underlying) { console.error(`❌ No underlying address for ${symbol}`); process.exit(1); }
    const token = new ethers.Contract(underlying, ERC20_ABI, provider);
    const decimals = await token.decimals();
    const amt = ethers.parseUnits(amount.toString(), decimals);

    const allowance = await token.allowance(walletAddr, vToken);
    if (allowance < amt) {
      console.log(`🔑 Approving ${symbol}...`);
      const appIface = new ethers.Interface(ERC20_ABI);
      const appData = appIface.encodeFunctionData('approve', [vToken, ethers.MaxUint256]);
      const ar = await sendTx(chain, { to: underlying, data: appData, value: BigInt(0) });
      console.log(`✅ Approved (block ${ar.blockNumber})`);
    }
    const iface = new ethers.Interface(VENUS_VTOKEN_ABI);
    const data = iface.encodeFunctionData('mint(uint256)', [amt]);
    const receipt = await sendTx(chain, { to: vToken, data, value: BigInt(0) });
    console.log(`✅ Supplied! Block: ${receipt.blockNumber}\n   TX: ${chain.explorer}/tx/${receipt.hash}`);
  }
}

async function venusWithdraw(chain, sym, amount) {
  const { vToken, symbol, isNative } = resolveVenusToken(sym);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);
  const vt = new ethers.Contract(vToken, VENUS_VTOKEN_ABI, provider);
  const iface = new ethers.Interface(VENUS_VTOKEN_ABI);

  let data;
  if (amount === 'max' || amount === 'all') {
    const bal = await vt.balanceOf(walletAddr); // vToken balance
    data = iface.encodeFunctionData('redeem', [bal]);
    console.log(`\n🏧 Withdrawing all ${symbol} from Venus (BSC)...`);
  } else {
    const underlying = isNative ? null : BSC_TOKENS[symbol];
    const decimals = underlying ? Number(await new ethers.Contract(underlying, ERC20_ABI, provider).decimals()) : 18;
    const amt = ethers.parseUnits(amount.toString(), decimals);
    data = iface.encodeFunctionData('redeemUnderlying', [amt]);
    console.log(`\n🏧 Withdrawing ${amount} ${symbol} from Venus (BSC)...`);
  }

  const receipt = await sendTx(chain, { to: vToken, data, value: BigInt(0) });
  console.log(`✅ Withdrawn! Block: ${receipt.blockNumber}\n   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function venusBorrow(chain, sym, amount) {
  const { vToken, symbol, isNative } = resolveVenusToken(sym);
  const underlying = isNative ? null : BSC_TOKENS[symbol];
  const provider = getProvider(chain);
  const decimals = underlying ? Number(await new ethers.Contract(underlying, ERC20_ABI, provider).decimals()) : 18;
  const amt = ethers.parseUnits(amount.toString(), decimals);
  const iface = new ethers.Interface(VENUS_VTOKEN_ABI);
  const data = iface.encodeFunctionData('borrow', [amt]);

  console.log(`\n📥 Borrowing ${amount} ${symbol} from Venus (BSC)...`);
  const receipt = await sendTx(chain, { to: vToken, data, value: BigInt(0) });
  console.log(`✅ Borrowed! Block: ${receipt.blockNumber}\n   TX: ${chain.explorer}/tx/${receipt.hash}`);
  console.log(`   ⚠️  Monitor liquidity to avoid liquidation!`);
}

async function venusRepay(chain, sym, amount) {
  const { vToken, symbol, isNative } = resolveVenusToken(sym);
  const iface = new ethers.Interface(VENUS_VTOKEN_ABI);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);

  let data, value = BigInt(0);
  if (isNative) {
    if (amount === 'max' || amount === 'all') {
      const vt = new ethers.Contract(vToken, VENUS_VTOKEN_ABI, provider);
      const borrowed = await vt.borrowBalanceCurrent(walletAddr);
      value = borrowed * BigInt(101) / BigInt(100); // +1% buffer
    } else {
      value = ethers.parseEther(amount.toString());
    }
    data = iface.encodeFunctionData('repayBorrow()');
    console.log(`\n💳 Repaying ${ethers.formatEther(value)} BNB to Venus (BSC)...`);
  } else {
    const underlying = BSC_TOKENS[symbol];
    const decimals = Number(await new ethers.Contract(underlying, ERC20_ABI, provider).decimals());
    let amt;
    if (amount === 'max' || amount === 'all') {
      amt = ethers.MaxUint256;
    } else {
      amt = ethers.parseUnits(amount.toString(), decimals);
    }
    // Approve
    const token = new ethers.Contract(underlying, ERC20_ABI, provider);
    const allowance = await token.allowance(walletAddr, vToken);
    if (allowance < amt) {
      console.log(`🔑 Approving ${symbol} for repayment...`);
      const appIface = new ethers.Interface(ERC20_ABI);
      const appData = appIface.encodeFunctionData('approve', [vToken, ethers.MaxUint256]);
      const ar = await sendTx(chain, { to: underlying, data: appData, value: BigInt(0) });
      console.log(`✅ Approved (block ${ar.blockNumber})`);
    }
    data = iface.encodeFunctionData('repayBorrow(uint256)', [amt]);
    console.log(`\n💳 Repaying ${amount} ${symbol} to Venus (BSC)...`);
  }

  const receipt = await sendTx(chain, { to: vToken, data, value });
  console.log(`✅ Repaid! Block: ${receipt.blockNumber}\n   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

function getProvider(cfg) {
  return new ethers.JsonRpcProvider(cfg.rpcOverride || cfg.rpc);
}

function resolveToken(chainKey, symbolOrAddr) {
  if (symbolOrAddr.startsWith('0x')) return { address: symbolOrAddr, symbol: symbolOrAddr.slice(0, 8) };
  const tokens = TOKEN_ADDRESSES[chainKey] || {};
  const addr = tokens[symbolOrAddr.toUpperCase()];
  if (!addr) {
    console.error(`❌ Unknown token ${symbolOrAddr} on ${chainKey}. Known: ${Object.keys(tokens).join(', ')}`);
    process.exit(1);
  }
  return { address: addr, symbol: symbolOrAddr.toUpperCase() };
}

function formatRay(ray) {
  // Aave rates are in RAY (1e27). Convert to APY %
  const rate = Number(ray) / 1e27;
  const apy = (Math.pow(1 + rate / 31536000, 31536000) - 1) * 100;
  return apy.toFixed(2) + '%';
}

function formatUSD(baseUnits) {
  // Aave base units = USD with 8 decimals
  return '$' + (Number(baseUnits) / 1e8).toFixed(2);
}

// ── Daemon signing (same pattern as wallet-manager) ──────────────────────────
function signViaSocket(payload) {
  return new Promise((resolve, reject) => {
    const { execSync } = require('child_process');
    try { execSync(`bash "${ENSURE_SCRIPT}"`, { stdio: 'ignore' }); } catch {}

    const lockFile = '/tmp/.aawp-daemon.lock';
    if (!fs.existsSync(lockFile)) {
      return reject(new Error('Daemon not running. Run: bash scripts/ensure-daemon.sh'));
    }
    const socketPath = fs.readFileSync(lockFile, 'utf8').trim().split('\n')[1];
    if (!socketPath) return reject(new Error('Socket path not found in lock file'));

    const client = net.createConnection(socketPath);
    let buf = '';
    client.on('connect', () => client.write(JSON.stringify(payload) + '\n'));
    client.on('data', d => { buf += d.toString(); });
    client.on('end', () => {
      try { resolve(JSON.parse(buf)); } catch (e) { reject(new Error('Bad daemon response: ' + buf)); }
    });
    client.on('error', reject);
    setTimeout(() => { client.destroy(); reject(new Error('Daemon timeout')); }, 15000);
  });
}

async function getWalletAddress(chain) {
  const resp = await signViaSocket({
    action: 'get_address',
    chain_id: chain.chainId,
  });
  if (resp.error) throw new Error(resp.error);
  return resp.address;
}

async function sendTx(chain, txRequest) {
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);

  // Fill gas
  const [nonce, feeData, gasEstimate] = await Promise.all([
    provider.getTransactionCount(walletAddr, 'latest'),
    provider.getFeeData(),
    provider.estimateGas({ ...txRequest, from: walletAddr }).catch(() => BigInt(300000)),
  ]);

  const tx = {
    ...txRequest,
    from: walletAddr,
    nonce,
    chainId: chain.chainId,
    gasLimit: gasEstimate * BigInt(12) / BigInt(10),
    maxFeePerGas: feeData.maxFeePerGas || feeData.gasPrice,
    maxPriorityFeePerGas: feeData.maxPriorityFeePerGas || BigInt(1000000),
  };

  // Remove type=2 fields if no EIP-1559
  if (!tx.maxFeePerGas) {
    tx.gasPrice = feeData.gasPrice;
    delete tx.maxFeePerGas;
    delete tx.maxPriorityFeePerGas;
  }

  const resp = await signViaSocket({
    action: 'sign_transaction',
    chain_id: chain.chainId,
    tx,
  });
  if (resp.error) throw new Error(resp.error);

  const sent = await provider.broadcastTransaction(resp.signed);
  console.log(`📡 TX broadcast: ${sent.hash}`);
  console.log(`   Waiting for confirmation...`);
  const receipt = await sent.wait(1);
  return receipt;
}

// ── Commands ──────────────────────────────────────────────────────────────────

async function cmdRates(chainKey) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const dataProvider = new ethers.Contract(AAVE_DATA_PROVIDERS[chainKey], DATA_PROVIDER_ABI, provider);

  const tokens = TOKEN_ADDRESSES[chainKey] || {};
  if (Object.keys(tokens).length === 0) {
    console.log('No known tokens for this chain.');
    return;
  }

  console.log(`\n📊 Aave V3 Rates — ${chain.name}\n`);
  console.log(`${'Token'.padEnd(8)} ${'Supply APY'.padStart(12)} ${'Var Borrow APY'.padStart(16)} ${'Stable Borrow APY'.padStart(18)}`);
  console.log('─'.repeat(60));

  for (const [symbol, addr] of Object.entries(tokens)) {
    try {
      const data = await dataProvider.getReserveData(addr);
      const supplyAPY  = formatRay(data.liquidityRate);
      const varBorAPY  = formatRay(data.variableBorrowRate);
      const stabBorAPY = formatRay(data.stableBorrowRate);
      console.log(`${symbol.padEnd(8)} ${supplyAPY.padStart(12)} ${varBorAPY.padStart(16)} ${stabBorAPY.padStart(18)}`);
    } catch {
      console.log(`${symbol.padEnd(8)} ${'N/A'.padStart(12)} ${'N/A'.padStart(16)} ${'N/A'.padStart(18)}`);
    }
  }
  console.log();
}

async function cmdPositions(chainKey) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const pool = new ethers.Contract(AAVE_POOLS[chainKey], POOL_ABI, provider);
  const dataProvider = new ethers.Contract(AAVE_DATA_PROVIDERS[chainKey], DATA_PROVIDER_ABI, provider);

  const acct = await pool.getUserAccountData(walletAddr);
  console.log(`\n🏦 Aave V3 Positions — ${chain.name}`);
  console.log(`   Wallet: ${walletAddr}`);
  console.log(`   Total Supplied:      ${formatUSD(acct.totalCollateralBase)}`);
  console.log(`   Total Borrowed:      ${formatUSD(acct.totalDebtBase)}`);
  console.log(`   Available to Borrow: ${formatUSD(acct.availableBorrowsBase)}`);
  console.log(`   Health Factor:       ${Number(acct.healthFactor) === Number(ethers.MaxUint256) ? '∞' : (Number(acct.healthFactor) / 1e18).toFixed(3)}`);

  const tokens = TOKEN_ADDRESSES[chainKey] || {};
  let hasPositions = false;
  console.log(`\n   ${'Token'.padEnd(8)} ${'Supplied'.padStart(14)} ${'Var Debt'.padStart(14)} ${'Stable Debt'.padStart(14)}`);
  console.log('   ' + '─'.repeat(54));

  for (const [symbol, addr] of Object.entries(tokens)) {
    try {
      const ud = await dataProvider.getUserReserveData(addr, walletAddr);
      const token = new ethers.Contract(addr, ERC20_ABI, provider);
      const decimals = await token.decimals();
      const div = BigInt(10) ** decimals;

      const supplied = Number(ud.currentATokenBalance) / Number(div);
      const varDebt  = Number(ud.currentVariableDebt) / Number(div);
      const stabDebt = Number(ud.currentStableDebt) / Number(div);

      if (supplied > 0 || varDebt > 0 || stabDebt > 0) {
        hasPositions = true;
        console.log(`   ${symbol.padEnd(8)} ${supplied.toFixed(4).padStart(14)} ${varDebt.toFixed(4).padStart(14)} ${stabDebt.toFixed(4).padStart(14)}`);
      }
    } catch { /* skip */ }
  }

  if (!hasPositions) console.log('   No active positions.');
  console.log();
}

async function cmdSupply(chainKey, tokenSymbol, amount) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const { address: tokenAddr, symbol } = resolveToken(chainKey, tokenSymbol);

  const token = new ethers.Contract(tokenAddr, ERC20_ABI, provider);
  const decimals = await token.decimals();
  const amountWei = ethers.parseUnits(amount.toString(), decimals);
  const poolAddr = AAVE_POOLS[chainKey];

  // Check allowance
  const allowance = await token.allowance(walletAddr, poolAddr);
  if (allowance < amountWei) {
    console.log(`🔑 Approving ${symbol} for Aave Pool...`);
    const approveFace = new ethers.Interface(ERC20_ABI);
    const approveData = approveFace.encodeFunctionData('approve', [poolAddr, ethers.MaxUint256]);
    const approveReceipt = await sendTx(chain, { to: tokenAddr, data: approveData, value: BigInt(0) });
    console.log(`✅ Approved (block ${approveReceipt.blockNumber})`);
  }

  console.log(`\n💰 Supplying ${amount} ${symbol} to Aave V3 on ${chain.name}...`);
  const poolFace = new ethers.Interface(POOL_ABI);
  const data = poolFace.encodeFunctionData('supply', [tokenAddr, amountWei, walletAddr, 0]);
  const receipt = await sendTx(chain, { to: poolAddr, data, value: BigInt(0) });
  console.log(`✅ Supplied! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function cmdWithdraw(chainKey, tokenSymbol, amount) {
  const chain = getChain(chainKey);
  const { address: tokenAddr, symbol } = resolveToken(chainKey, tokenSymbol);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);
  const poolAddr = AAVE_POOLS[chainKey];

  let amountWei;
  if (amount === 'max' || amount === 'all') {
    amountWei = ethers.MaxUint256; // Aave uses MaxUint256 for full withdrawal
  } else {
    const token = new ethers.Contract(tokenAddr, ERC20_ABI, provider);
    const decimals = await token.decimals();
    amountWei = ethers.parseUnits(amount.toString(), decimals);
  }

  console.log(`\n🏧 Withdrawing ${amount} ${symbol} from Aave V3 on ${chain.name}...`);
  const poolFace = new ethers.Interface(POOL_ABI);
  const data = poolFace.encodeFunctionData('withdraw', [tokenAddr, amountWei, walletAddr]);
  const receipt = await sendTx(chain, { to: poolAddr, data, value: BigInt(0) });
  console.log(`✅ Withdrawn! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function cmdBorrow(chainKey, tokenSymbol, amount, interestRateMode) {
  const chain = getChain(chainKey);
  const { address: tokenAddr, symbol } = resolveToken(chainKey, tokenSymbol);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);

  const token = new ethers.Contract(tokenAddr, ERC20_ABI, provider);
  const decimals = await token.decimals();
  const amountWei = ethers.parseUnits(amount.toString(), decimals);
  const poolAddr = AAVE_POOLS[chainKey];
  const modeStr = interestRateMode === 1 ? 'stable' : 'variable';

  console.log(`\n📥 Borrowing ${amount} ${symbol} (${modeStr} rate) from Aave V3 on ${chain.name}...`);
  const poolFace = new ethers.Interface(POOL_ABI);
  const data = poolFace.encodeFunctionData('borrow', [tokenAddr, amountWei, interestRateMode, 0, walletAddr]);
  const receipt = await sendTx(chain, { to: poolAddr, data, value: BigInt(0) });
  console.log(`✅ Borrowed! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
  console.log(`   ⚠️  Remember to monitor your health factor!`);
}

async function cmdRepay(chainKey, tokenSymbol, amount, interestRateMode) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const { address: tokenAddr, symbol } = resolveToken(chainKey, tokenSymbol);

  const token = new ethers.Contract(tokenAddr, ERC20_ABI, provider);
  const decimals = await token.decimals();
  let amountWei;
  if (amount === 'max' || amount === 'all') {
    amountWei = ethers.MaxUint256;
  } else {
    amountWei = ethers.parseUnits(amount.toString(), decimals);
  }

  const poolAddr = AAVE_POOLS[chainKey];

  // Approve
  const allowance = await token.allowance(walletAddr, poolAddr);
  if (allowance < amountWei && amount !== 'max') {
    console.log(`🔑 Approving ${symbol} for repayment...`);
    const approveFace = new ethers.Interface(ERC20_ABI);
    const approveData = approveFace.encodeFunctionData('approve', [poolAddr, ethers.MaxUint256]);
    const approveReceipt = await sendTx(chain, { to: tokenAddr, data: approveData, value: BigInt(0) });
    console.log(`✅ Approved (block ${approveReceipt.blockNumber})`);
  }

  const modeStr = interestRateMode === 1 ? 'stable' : 'variable';
  console.log(`\n💳 Repaying ${amount} ${symbol} (${modeStr} debt) on Aave V3 ${chain.name}...`);
  const poolFace = new ethers.Interface(POOL_ABI);
  const data = poolFace.encodeFunctionData('repay', [tokenAddr, amountWei, interestRateMode, walletAddr]);
  const receipt = await sendTx(chain, { to: poolAddr, data, value: BigInt(0) });
  console.log(`✅ Repaid! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (!cmd) {
    console.log(`
AAWP Yield Manager — Aave V3

Usage: yield.js [--chain <chain>] <command> [args]

Commands:
  rates                      Show current supply/borrow APY for all tokens
  positions                  Show your active Aave positions
  supply <token> <amount>    Supply tokens as collateral
  withdraw <token> <amount>  Withdraw supplied tokens (use 'max' for all)
  borrow <token> <amount>    Borrow tokens (--rate stable|variable)
  repay <token> <amount>     Repay borrowed tokens (use 'max' for full repay)

Supported chains: ${Object.keys(AAVE_POOLS).join(', ')}
Supported tokens per chain: see TOKEN_ADDRESSES in this file

Examples:
  yield.js --chain base rates
  yield.js --chain base positions
  yield.js --chain base supply USDC 1000
  yield.js --chain base withdraw USDC 500
  yield.js --chain base borrow USDC 200 --rate variable
  yield.js --chain base repay USDC max
`);
    process.exit(0);
  }

  const chain = getChain(chainArg);
  const bsc = isBSC(chainArg);

  switch (cmd) {
    case 'rates':
      bsc ? await venusRates(chain) : await cmdRates(chainArg);
      break;
    case 'positions':
      bsc ? await venusPositions(chain) : await cmdPositions(chainArg);
      break;
    case 'supply': {
      const [, tokenSym, amt] = filteredArgv;
      if (!tokenSym || !amt) { console.error('Usage: yield.js --chain <chain> supply <token> <amount>'); process.exit(1); }
      bsc ? await venusSupply(chain, tokenSym, amt) : await cmdSupply(chainArg, tokenSym, amt);
      break;
    }
    case 'withdraw': {
      const [, tokenSym, amt] = filteredArgv;
      if (!tokenSym || !amt) { console.error('Usage: yield.js --chain <chain> withdraw <token> <amount|max>'); process.exit(1); }
      bsc ? await venusWithdraw(chain, tokenSym, amt) : await cmdWithdraw(chainArg, tokenSym, amt);
      break;
    }
    case 'borrow': {
      const [, tokenSym, amt] = filteredArgv;
      if (!tokenSym || !amt) { console.error('Usage: yield.js --chain <chain> borrow <token> <amount>'); process.exit(1); }
      bsc ? await venusBorrow(chain, tokenSym, amt) : await cmdBorrow(chainArg, tokenSym, amt, rateMode);
      break;
    }
    case 'repay': {
      const [, tokenSym, amt] = filteredArgv;
      if (!tokenSym || !amt) { console.error('Usage: yield.js --chain <chain> repay <token> <amount|max>'); process.exit(1); }
      bsc ? await venusRepay(chain, tokenSym, amt) : await cmdRepay(chainArg, tokenSym, amt, rateMode);
      break;
    }
    default:
      console.error(`❌ Unknown command: ${cmd}`);
      process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
