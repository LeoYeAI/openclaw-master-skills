#!/usr/bin/env node
/**
 * AAWP Limit Order Manager — CoW Protocol
 *
 * Creates gasless limit orders via CoW Protocol (EIP-712 signed, no on-chain gas).
 * Supported chains: eth, base, arb, op, polygon
 *
 * Usage:
 *   limit-order.js --chain base create ETH USDC 0.1 2700     Sell 0.1 ETH if price >= 2700 USDC
 *   limit-order.js --chain base create USDC ETH 1000 0.00037 Buy ETH with 1000 USDC at 0.00037 ETH/USDC
 *   limit-order.js --chain base list                          List open orders
 *   limit-order.js --chain base cancel <orderUid>            Cancel an order
 *   limit-order.js --chain base history                       Filled/expired orders
 *
 * How it works:
 *   1. Get token addresses and decimals from config
 *   2. Call CoW API to get quote (for order hash)
 *   3. Sign the EIP-712 order via AAWP daemon
 *   4. POST signed order to CoW API — no gas paid by user
 */
'use strict';

const net = require('net');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const https = require('https');

const S = path.join(__dirname, '..');
const ENSURE_SCRIPT = path.join(__dirname, 'ensure-daemon.sh');
const CHAINS_FILE = path.join(S, 'config/chains.json');
const CHAINS = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));

// ── CoW Protocol config (non-BSC chains) ─────────────────────────────────────
const COW_API = {
  eth:     'https://api.cow.fi/mainnet',
  base:    'https://api.cow.fi/base',
  arb:     'https://api.cow.fi/arbitrum_one',
  op:      'https://api.cow.fi/optimism',
  polygon: 'https://api.cow.fi/polygon',
};

// ── 1inch Limit Order Protocol (BSC) ─────────────────────────────────────────
// 1inch Limit Order Contract v4 on BSC
const INCH_LO_CONTRACT_BSC = '0x111111125421cA6dc452d289314280a0f8842A65';
const INCH_API_BSC = 'https://api.1inch.dev/orderbook/v4.0/56';

// 1inch Limit Order EIP-712 domain + types
const INCH_DOMAIN_BSC = {
  name: '1inch Aggregation Router',
  version: '6',
  chainId: 56,
  verifyingContract: INCH_LO_CONTRACT_BSC,
};

const INCH_ORDER_TYPES = {
  Order: [
    { name: 'salt',           type: 'uint256' },
    { name: 'maker',          type: 'address' },
    { name: 'receiver',       type: 'address' },
    { name: 'makerAsset',     type: 'address' },
    { name: 'takerAsset',     type: 'address' },
    { name: 'makingAmount',   type: 'uint256' },
    { name: 'takingAmount',   type: 'uint256' },
    { name: 'makerTraits',    type: 'uint256' },
  ],
};

// CoW Protocol settlement contract (same on all chains)
const COW_SETTLEMENT = '0x9008D19f58AAbD9eD0D60971565AA8510560ab41';

// CoW VaultRelayer — needs token approval (not the settlement contract)
const COW_VAULT_RELAYER = {
  eth:     '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
  base:    '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
  arb:     '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
  op:      '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
  polygon: '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
};

// ERC-20 wrapped native tokens (CoW doesn't accept raw ETH/MATIC)
const WRAPPED_NATIVE = {
  eth:     '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', // WETH
  base:    '0x4200000000000000000000000000000000000006', // WETH
  arb:     '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', // WETH
  op:      '0x4200000000000000000000000000000000000006', // WETH
  polygon: '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270', // WMATIC
};

// Token registry (same as yield.js + extras)
const TOKENS = {
  eth: {
    ETH:  '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', // CoW uses this for native
    WETH: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    USDC: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    USDT: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    DAI:  '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    WBTC: '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
  },
  base: {
    ETH:  '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    WETH: '0x4200000000000000000000000000000000000006',
    USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    USDbC:'0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
    cbBTC:'0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
  },
  arb: {
    ETH:  '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    WETH: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    USDC: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    USDT: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
    WBTC: '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
    DAI:  '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
  },
  op: {
    ETH:  '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    WETH: '0x4200000000000000000000000000000000000006',
    USDC: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    USDT: '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
    DAI:  '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
    WBTC: '0x68f180fcCe6836688e9084f035309E29Bf0A2095',
  },
  polygon: {
    MATIC:'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    WMATIC:'0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
    USDC: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    USDT: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
    WETH: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
    DAI:  '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
    WBTC: '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
  },
  bsc: {
    BNB:  '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    WBNB: '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    USDC: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
    USDT: '0x55d398326f99059fF775485246999027B3197955',
    BUSD: '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    BTCB: '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
    ETH:  '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
    CAKE: '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
    XVS:  '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63',
  },
};

// Token decimals cache
const TOKEN_DECIMALS = {
  USDC: 6, USDT: 6, USDbC: 6, DAI: 18,
  WETH: 18, ETH: 18, WBTC: 8,
  MATIC: 18, WMATIC: 18, cbBTC: 8,
};

const ERC20_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function decimals() view returns (uint8)',
];

// ── Parse args ────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
let chainArg = 'base';
let expiryHours = 24; // default order validity
const filteredArgv = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chain' && argv[i + 1])   { chainArg = argv[++i]; }
  else if (argv[i] === '--expiry' && argv[i + 1]) { expiryHours = parseFloat(argv[++i]); }
  else filteredArgv.push(argv[i]);
}
const cmd = filteredArgv[0];

// ── Helpers ───────────────────────────────────────────────────────────────────
function getChain(key) {
  const cfg = CHAINS[key];
  if (!cfg) { console.error(`❌ Unknown chain: ${key}`); process.exit(1); }
  if (!COW_API[key] && key !== 'bsc') {
    console.error(`❌ Limit orders not supported on ${key}. Supported: ${[...Object.keys(COW_API), 'bsc'].join(', ')}`);
    process.exit(1);
  }
  return { key, ...cfg };
}

function isBSC(key) { return key === 'bsc'; }

function getProvider(cfg) {
  return new ethers.JsonRpcProvider(cfg.rpcOverride || cfg.rpc);
}

function resolveToken(chainKey, sym) {
  const t = TOKENS[chainKey] || {};
  const upper = sym.toUpperCase();
  const addr = t[upper];
  if (!addr) {
    if (sym.startsWith('0x')) return { address: sym, symbol: sym.slice(0, 8), decimals: 18 };
    console.error(`❌ Unknown token ${sym} on ${chainKey}. Known: ${Object.keys(t).join(', ')}`);
    process.exit(1);
  }
  return { address: addr, symbol: upper, decimals: TOKEN_DECIMALS[upper] ?? 18 };
}

function httpRequest(method, url, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = {
      hostname: u.hostname,
      path: u.pathname + u.search,
      method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'AAWP-LimitOrder/1.0',
      },
    };
    const bodyStr = body ? JSON.stringify(body) : undefined;
    if (bodyStr) opts.headers['Content-Length'] = Buffer.byteLength(bodyStr);

    const req = https.request(opts, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

// ── Daemon comms ──────────────────────────────────────────────────────────────
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
    const client = net.createConnection(sock, () => client.end(JSON.stringify(obj)));
    let buf = '';
    client.on('data', d => buf += d.toString());
    client.on('end', () => {
      try { resolve(JSON.parse(buf)); } catch { reject(new Error('Bad daemon response: ' + buf)); }
    });
    client.on('error', reject);
    setTimeout(() => { client.destroy(); reject(new Error('Daemon timeout')); }, 30000);
  });
}

async function getWalletAddress() {
  const resp = await socketQuery({ cmd: 'address' });
  if (resp.error) throw new Error(resp.error);
  return resp.address;
}

async function signTypedData(domain, types, value) {
  const resp = await socketQuery({
    cmd: 'sign_typed',
    domain,
    types,
    value,
  });
  if (resp.error) throw new Error(resp.error);
  return resp.signature;
}

async function sendTx(chain, txRequest) {
  const walletAddr = await getWalletAddress();
  const provider = getProvider(chain);
  const [nonce, feeData, gasEstimate] = await Promise.all([
    provider.getTransactionCount(walletAddr, 'latest'),
    provider.getFeeData(),
    provider.estimateGas({ ...txRequest, from: walletAddr }).catch(() => BigInt(100000)),
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
  if (!tx.maxFeePerGas) {
    tx.gasPrice = feeData.gasPrice;
    delete tx.maxFeePerGas;
    delete tx.maxPriorityFeePerGas;
  }
  const resp = await socketQuery({ cmd: 'sign_transaction', ...tx });
  if (resp.error) throw new Error(resp.error);
  const sent = await provider.broadcastTransaction(resp.signed);
  console.log(`📡 TX: ${sent.hash}`);
  return await sent.wait(1);
}

// ── CoW Order EIP-712 types ───────────────────────────────────────────────────
const COW_DOMAIN = (chainId) => ({
  name: 'Gnosis Protocol',
  version: 'v2',
  chainId,
  verifyingContract: COW_SETTLEMENT,
});

const COW_ORDER_TYPES = {
  Order: [
    { name: 'sellToken',         type: 'address' },
    { name: 'buyToken',          type: 'address' },
    { name: 'receiver',          type: 'address' },
    { name: 'sellAmount',        type: 'uint256' },
    { name: 'buyAmount',         type: 'uint256' },
    { name: 'validTo',           type: 'uint32'  },
    { name: 'appData',           type: 'bytes32' },
    { name: 'feeAmount',         type: 'uint256' },
    { name: 'kind',              type: 'string'  },
    { name: 'partiallyFillable', type: 'bool'    },
    { name: 'sellTokenBalance',  type: 'string'  },
    { name: 'buyTokenBalance',   type: 'string'  },
  ],
};

// ── Ensure token approval ─────────────────────────────────────────────────────
async function ensureApproval(chain, tokenAddr, walletAddr, amount) {
  if (tokenAddr === '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE') return; // native, skip
  const provider = getProvider(chain);
  const token = new ethers.Contract(tokenAddr, ERC20_ABI, provider);
  const relayer = chain.key === 'bsc' ? INCH_LO_CONTRACT_BSC : COW_VAULT_RELAYER[chain.key];
  const allowance = await token.allowance(walletAddr, relayer);
  if (allowance >= amount) return;

  console.log(`🔑 Approving token for CoW VaultRelayer...`);
  const iface = new ethers.Interface(ERC20_ABI);
  const data = iface.encodeFunctionData('approve', [relayer, ethers.MaxUint256]);
  const receipt = await sendTx(chain, { to: tokenAddr, data, value: BigInt(0) });
  console.log(`✅ Approved (block ${receipt.blockNumber})`);
}

// ── 1inch BSC Commands ────────────────────────────────────────────────────────

async function inchCreate(chain, sellSymbol, buySymbol, sellAmount, limitPrice) {
  const walletAddr = await getWalletAddress();
  const sell = resolveToken(chain.key, sellSymbol);
  const buy  = resolveToken(chain.key, buySymbol);

  const sellAmtWei = ethers.parseUnits(sellAmount.toString(), TOKEN_DECIMALS[sell.symbol] ?? 18);
  const buyAmtFloat = parseFloat(sellAmount) * parseFloat(limitPrice);
  const buyAmtWei  = ethers.parseUnits(buyAmtFloat.toFixed(TOKEN_DECIMALS[buy.symbol] ?? 18), TOKEN_DECIMALS[buy.symbol] ?? 18);

  // Approve 1inch LO contract
  await ensureApproval(chain, sell.address, walletAddr, sellAmtWei);

  const salt = BigInt(Date.now());
  const expiry = Math.floor(Date.now() / 1000) + Math.round(expiryHours * 3600);
  // makerTraits encodes expiry in high bits (1inch v4 format)
  const makerTraits = (BigInt(expiry) << BigInt(216));

  const orderStruct = {
    salt,
    maker:        walletAddr,
    receiver:     walletAddr,
    makerAsset:   sell.address,
    takerAsset:   buy.address,
    makingAmount: sellAmtWei,
    takingAmount: buyAmtWei,
    makerTraits,
  };

  console.log(`\n📋 Creating 1inch Limit Order — BSC`);
  console.log(`   Sell: ${sellAmount} ${sell.symbol}`);
  console.log(`   Buy:  ${buyAmtFloat.toFixed(6)} ${buy.symbol}  (price: ${limitPrice} ${buy.symbol}/${sell.symbol})`);
  console.log(`   Expires: ${new Date(expiry * 1000).toISOString()}`);
  console.log(`\n✍️  Signing (EIP-712)...`);

  // Convert BigInts to strings for signing
  const signable = {
    salt: salt.toString(),
    maker: orderStruct.maker,
    receiver: orderStruct.receiver,
    makerAsset: orderStruct.makerAsset,
    takerAsset: orderStruct.takerAsset,
    makingAmount: sellAmtWei.toString(),
    takingAmount: buyAmtWei.toString(),
    makerTraits: makerTraits.toString(),
  };

  const signature = await signTypedData(INCH_DOMAIN_BSC, INCH_ORDER_TYPES, signable);

  const payload = {
    orderHash: ethers.TypedDataEncoder.hash(INCH_DOMAIN_BSC, INCH_ORDER_TYPES, signable),
    signature,
    data: signable,
  };

  console.log(`\n📤 Submitting to 1inch Orderbook (BSC)...`);
  const resp = await httpRequest('POST', `${INCH_API_BSC}/order`, payload);

  if (resp.status === 201 || resp.status === 200) {
    const orderHash = payload.orderHash;
    console.log(`\n✅ Order created!`);
    console.log(`   Order Hash: ${orderHash}`);
    console.log(`   Explorer:   https://app.1inch.io/#/56/limit-order/${orderHash}`);
    // Save locally
    const ordersFile = path.join(S, 'config/limit-orders.json');
    let orders = [];
    try { orders = JSON.parse(fs.readFileSync(ordersFile, 'utf8')); } catch {}
    orders.push({
      uid: orderHash, chain: 'bsc', protocol: '1inch',
      sell: { symbol: sell.symbol, amount: sellAmount },
      buy:  { symbol: buy.symbol,  amount: buyAmtFloat.toFixed(6) },
      price: limitPrice, expiry, createdAt: new Date().toISOString(), status: 'open',
    });
    fs.writeFileSync(ordersFile, JSON.stringify(orders, null, 2));
  } else {
    console.error(`❌ 1inch API error ${resp.status}:`);
    console.error(JSON.stringify(resp.body, null, 2));
    process.exit(1);
  }
}

async function inchList(chain) {
  const walletAddr = await getWalletAddress();
  console.log(`\n📋 Open 1inch Limit Orders — BSC`);
  console.log(`   Wallet: ${walletAddr}\n`);
  const resp = await httpRequest('GET', `${INCH_API_BSC}/address/${walletAddr}?page=1&limit=20&statuses[]=1`);
  if (resp.status !== 200) { console.error(`❌ 1inch API error: ${resp.status}`); return; }
  const orders = resp.body;
  if (!orders?.length) { console.log('   No open orders.'); return; }
  for (const o of orders) {
    console.log(`   [OPEN] ${(o.orderHash || '').slice(0, 18)}...`);
    console.log(`          Sell: ${o.data?.makingAmount} of ${o.data?.makerAsset?.slice(0, 10)}...`);
    console.log(`          Buy:  ${o.data?.takingAmount} of ${o.data?.takerAsset?.slice(0, 10)}...`);
    console.log();
  }
}

async function inchCancel(chain, orderHash) {
  const walletAddr = await getWalletAddress();
  const provider = getProvider(chain);
  // 1inch cancel is on-chain (cancelOrder call)
  const CANCEL_ABI = ['function cancelOrder(uint256 makerTraits, bytes32 orderHash)'];
  const iface = new ethers.Interface(CANCEL_ABI);
  // Fetch order to get makerTraits
  const resp = await httpRequest('GET', `${INCH_API_BSC}/order/${orderHash}`);
  if (resp.status !== 200) { console.error(`❌ Order not found`); process.exit(1); }
  const makerTraits = resp.body?.data?.makerTraits || '0';
  console.log(`\n❌ Cancelling 1inch order: ${orderHash}`);
  const data = iface.encodeFunctionData('cancelOrder', [BigInt(makerTraits), orderHash]);
  const receipt = await sendTx(chain, { to: INCH_LO_CONTRACT_BSC, data, value: BigInt(0) });
  console.log(`✅ Cancelled! TX: ${chain.explorer}/tx/${receipt.hash}`);
}

// ── CoW Commands ──────────────────────────────────────────────────────────────

async function cmdCreate(chainKey, sellSymbol, buySymbol, sellAmount, limitPrice) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress();
  const apiBase = COW_API[chainKey];

  const sell = resolveToken(chainKey, sellSymbol);
  const buy  = resolveToken(chainKey, buySymbol);

  const sellAmtWei = ethers.parseUnits(sellAmount.toString(), sell.decimals);
  // buyAmount = sellAmount * limitPrice (price is buy-per-sell)
  const buyAmtFloat = parseFloat(sellAmount) * parseFloat(limitPrice);
  const buyAmtWei = ethers.parseUnits(buyAmtFloat.toFixed(buy.decimals), buy.decimals);
  const validTo = Math.floor(Date.now() / 1000) + Math.round(expiryHours * 3600);

  console.log(`\n📋 Creating Limit Order — ${chain.name}`);
  console.log(`   Sell: ${sellAmount} ${sell.symbol}  (${sell.address.slice(0,10)}...)`);
  console.log(`   Buy:  ${buyAmtFloat.toFixed(6)} ${buy.symbol}  (price: ${limitPrice} ${buy.symbol}/${sell.symbol})`);
  console.log(`   Expires: ${new Date(validTo * 1000).toISOString()} (${expiryHours}h)`);

  // Ensure approval (skip for native ETH/MATIC which CoW handles via WETH wrapping)
  await ensureApproval(chain, sell.address, walletAddr, sellAmtWei);

  // CoW app data (empty hash = default)
  const appData = '0x0000000000000000000000000000000000000000000000000000000000000000';

  const orderStruct = {
    sellToken:         sell.address,
    buyToken:          buy.address,
    receiver:          walletAddr,
    sellAmount:        sellAmtWei.toString(),
    buyAmount:         buyAmtWei.toString(),
    validTo,
    appData,
    feeAmount:         '0', // CoW Protocol takes 0 fee from user
    kind:              'sell',
    partiallyFillable: false,
    sellTokenBalance:  'erc20',
    buyTokenBalance:   'erc20',
  };

  // Sign EIP-712 order
  console.log(`\n✍️  Signing order (EIP-712, gasless)...`);
  const domain = COW_DOMAIN(chain.chainId);

  let signature;
  try {
    signature = await signTypedData(domain, COW_ORDER_TYPES, orderStruct);
  } catch (e) {
    // Fallback: use ethers local signing if daemon doesn't support sign_typed
    // This path should not be needed in production AAWP
    console.error(`❌ EIP-712 signing failed: ${e.message}`);
    console.log(`   Tip: Ensure your AAWP daemon supports 'sign_typed' command.`);
    process.exit(1);
  }

  // POST order to CoW API
  const orderPayload = {
    ...orderStruct,
    signingScheme: 'eip712',
    signature,
    from: walletAddr,
    quoteId: null,
  };

  console.log(`\n📤 Submitting to CoW Protocol...`);
  const resp = await httpRequest('POST', `${apiBase}/api/v1/orders`, orderPayload);

  if (resp.status === 201 || resp.status === 200) {
    const orderUid = typeof resp.body === 'string' ? resp.body.replace(/"/g, '') : resp.body;
    console.log(`\n✅ Order created!`);
    console.log(`   Order UID: ${orderUid}`);
    console.log(`   Explorer:  https://explorer.cow.fi/orders/${orderUid}`);

    // Save to local orders file
    const ordersFile = path.join(S, 'config/limit-orders.json');
    let orders = [];
    try { orders = JSON.parse(fs.readFileSync(ordersFile, 'utf8')); } catch {}
    orders.push({
      uid: orderUid,
      chain: chainKey,
      sell: { symbol: sell.symbol, amount: sellAmount, address: sell.address },
      buy:  { symbol: buy.symbol,  amount: buyAmtFloat.toFixed(6), address: buy.address },
      price: limitPrice,
      validTo,
      createdAt: new Date().toISOString(),
      status: 'open',
    });
    fs.writeFileSync(ordersFile, JSON.stringify(orders, null, 2));
    console.log(`   Saved to config/limit-orders.json`);
  } else {
    console.error(`❌ CoW API error ${resp.status}:`);
    console.error(JSON.stringify(resp.body, null, 2));
    process.exit(1);
  }
}

async function cmdList(chainKey) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress();
  const apiBase = COW_API[chainKey];

  console.log(`\n📋 Open Limit Orders — ${chain.name}`);
  console.log(`   Wallet: ${walletAddr}\n`);

  const resp = await httpRequest('GET', `${apiBase}/api/v1/account/${walletAddr}/orders?status=open&limit=20`);
  if (resp.status !== 200) {
    console.error(`❌ CoW API error: ${resp.status}`);
    return;
  }

  const orders = resp.body;
  if (!orders || orders.length === 0) {
    console.log('   No open orders.');
    return;
  }

  console.log(`   ${'UID'.padEnd(12)} ${'Sell'.padEnd(18)} ${'Buy'.padEnd(18)} ${'Status'.padEnd(12)} Expires`);
  console.log('   ' + '─'.repeat(72));
  for (const o of orders) {
    const uid = (o.uid || '').slice(0, 10) + '...';
    const sell = `${ethers.formatUnits(o.sellAmount || '0', 18).slice(0, 8)} ${o.sellToken?.slice(0, 8)}`;
    const buy  = `${ethers.formatUnits(o.buyAmount || '0', 18).slice(0, 8)} ${o.buyToken?.slice(0, 8)}`;
    const exp  = new Date((o.validTo || 0) * 1000).toLocaleString();
    console.log(`   ${uid.padEnd(12)} ${sell.padEnd(18)} ${buy.padEnd(18)} ${(o.status || '?').padEnd(12)} ${exp}`);
  }
  console.log();
}

async function cmdHistory(chainKey) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress();
  const apiBase = COW_API[chainKey];

  console.log(`\n📚 Order History — ${chain.name}`);
  console.log(`   Wallet: ${walletAddr}\n`);

  const resp = await httpRequest('GET', `${apiBase}/api/v1/account/${walletAddr}/orders?limit=20`);
  if (resp.status !== 200) {
    console.error(`❌ CoW API error: ${resp.status}`);
    return;
  }

  const orders = resp.body || [];
  if (orders.length === 0) { console.log('   No orders found.'); return; }

  for (const o of orders) {
    const uid = (o.uid || '').slice(0, 16) + '...';
    const status = (o.status || '?').toUpperCase();
    const created = new Date((o.creationDate || 0)).toLocaleString();
    console.log(`   [${status}] ${uid}  ${created}`);
    if (o.executedSellAmount) {
      console.log(`          Executed: ${ethers.formatUnits(o.executedSellAmount, 18)} → ${ethers.formatUnits(o.executedBuyAmount || '0', 18)}`);
    }
  }
  console.log();
}

async function cmdCancel(chainKey, orderUid) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress();
  const apiBase = COW_API[chainKey];

  console.log(`\n❌ Cancelling order: ${orderUid}`);

  // CoW cancel requires EIP-712 signature of the order UID
  const cancelDomain = COW_DOMAIN(chain.chainId);
  const cancelTypes = {
    OrderCancellations: [
      { name: 'orderUids', type: 'bytes[]' },
    ],
  };
  const cancelValue = { orderUids: [orderUid] };

  let signature;
  try {
    signature = await signTypedData(cancelDomain, cancelTypes, cancelValue);
  } catch (e) {
    console.error(`❌ Signing failed: ${e.message}`);
    process.exit(1);
  }

  const resp = await httpRequest('DELETE', `${apiBase}/api/v1/orders/${orderUid}`, {
    signature,
    signingScheme: 'eip712',
    from: walletAddr,
  });

  if (resp.status === 200 || resp.status === 204) {
    console.log(`✅ Order cancelled successfully.`);
    // Update local file
    const ordersFile = path.join(S, 'config/limit-orders.json');
    try {
      const orders = JSON.parse(fs.readFileSync(ordersFile, 'utf8'));
      const updated = orders.map(o => o.uid === orderUid ? { ...o, status: 'cancelled' } : o);
      fs.writeFileSync(ordersFile, JSON.stringify(updated, null, 2));
    } catch {}
  } else {
    console.error(`❌ Cancel failed (${resp.status}):`);
    console.error(JSON.stringify(resp.body, null, 2));
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (!cmd) {
    console.log(`
AAWP Limit Order Manager — CoW Protocol (Gasless)

Usage: limit-order.js [--chain <chain>] <command> [args]

Commands:
  create <sell> <buy> <sellAmt> <price>   Create limit order
  list                                    List open orders on CoW
  history                                 All orders (filled/expired/open)
  cancel <orderUid>                       Cancel an open order

Options:
  --chain   eth | base | arb | op | polygon  (default: base)
  --expiry  hours until order expires         (default: 24)

Examples:
  limit-order.js --chain base create ETH USDC 0.1 2700
      → Sell 0.1 ETH when price reaches 2700 USDC/ETH

  limit-order.js --chain eth create USDC ETH 1000 0.00037
      → Buy ETH with 1000 USDC at 0.00037 ETH/USDC

  limit-order.js --chain base list
  limit-order.js --chain base cancel 0xabc123...

Notes:
  - Orders are gasless (signed EIP-712, settled by CoW solvers)
  - CoW Protocol matches orders off-chain for best prices
  - Requires token approval for CoW VaultRelayer (one-time, ~gas)
  - Native ETH/MATIC is auto-handled as WETH/WMATIC by CoW
`);
    process.exit(0);
  }

  const chain = getChain(chainArg);
  const bsc = isBSC(chainArg);

  switch (cmd) {
    case 'create': {
      const [, sellSym, buySym, sellAmt, price] = filteredArgv;
      if (!sellSym || !buySym || !sellAmt || !price) {
        console.error('Usage: limit-order.js --chain <chain> create <sell> <buy> <sellAmount> <limitPrice>');
        process.exit(1);
      }
      bsc ? await inchCreate(chain, sellSym, buySym, sellAmt, price) : await cmdCreate(chainArg, sellSym, buySym, sellAmt, price);
      break;
    }
    case 'list':
      bsc ? await inchList(chain) : await cmdList(chainArg);
      break;
    case 'history':
      if (bsc) { console.log('BSC history: check https://app.1inch.io/#/56/limit-order'); break; }
      await cmdHistory(chainArg);
      break;
    case 'cancel': {
      const [, uid] = filteredArgv;
      if (!uid) { console.error('Usage: limit-order.js --chain <chain> cancel <orderHash>'); process.exit(1); }
      bsc ? await inchCancel(chain, uid) : await cmdCancel(chainArg, uid);
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
