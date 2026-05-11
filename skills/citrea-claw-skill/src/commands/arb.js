import 'dotenv/config'
import { createPublicClient, http } from 'viem'
import { fetchRedStonePrices, tokenAmountToUSD, formatUSD } from '../lib/prices.js'
import { sendTelegram } from '../lib/telegram.js'

// ─── Env Config ───────────────────────────────────────────────────────────────
const ARB_ALERT_THRESHOLD_BPS = parseInt(process.env.ARB_ALERT_THRESHOLD_BPS || '50', 10)
const ARB_MONITOR_INTERVAL_MS = parseInt(process.env.ARB_MONITOR_INTERVAL_SEC || '30', 10) * 1000

// ─── Gas Estimate ─────────────────────────────────────────────────────────────
const ESTIMATED_GAS_UNITS = 120000
const ESTIMATED_GAS_GWEI  = 0.1
const ESTIMATED_GAS_CBTC  = (ESTIMATED_GAS_UNITS * ESTIMATED_GAS_GWEI) / 1e9

// ─── Citrea Mainnet Config ────────────────────────────────────────────────────
const citrea = {
  id: 4114,
  name: 'Citrea Mainnet',
  nativeCurrency: { name: 'Citrea Bitcoin', symbol: 'cBTC', decimals: 18 },
  rpcUrls: { default: { http: ['https://rpc.mainnet.citrea.xyz'] } },
  blockExplorers: {
    default: {
      name: 'Citrea Explorer',
      url: 'https://explorer.mainnet.citrea.xyz'
    }
  }
}

// ─── Contract Addresses ───────────────────────────────────────────────────────
const JUICESWAP_FACTORY = '0xd809b1285aDd8eeaF1B1566Bf31B2B4C4Bba8e82'
const SATSUMA_FACTORY   = '0x10253594A832f967994b44f33411940533302ACb'

// ─── Pool Address Overrides ───────────────────────────────────────────────────
// JuiceSwap uses svJUSD in pools instead of plain JUSD
const POOL_ADDRESS_OVERRIDE = {
  '0x0987d3720d38847ac6dbb9d025b9de892a3ca35c': '0x1b70ae756b1089cc5948e4f8a2AD498DF30E897d',
}

function getPoolQueryAddress(address) {
  return POOL_ADDRESS_OVERRIDE[address.toLowerCase()] || address
}

// ─── Token Registry ───────────────────────────────────────────────────────────
const TOKEN_REGISTRY = {
  'ctusd':  { symbol: 'ctUSD',  address: '0x8D82c4E3c936C7B5724A382a9c5a4E6Eb7aB6d5D', decimals: 18 },
  'wcbtc':  { symbol: 'wcBTC',  address: '0x3100000000000000000000000000000000000006', decimals: 18 },
  'usdc.e': { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  'usdc':   { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  'usdt.e': { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  'usdt':   { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  'wbtc.e': { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
  'wbtc':   { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
  'jusd':   { symbol: 'JUSD',   address: '0x0987D3720D38847ac6dBB9D025B9dE892a3CA35C', decimals: 18 },
}

const ALL_TOKENS = [
  { symbol: 'ctUSD',  address: '0x8D82c4E3c936C7B5724A382a9c5a4E6Eb7aB6d5D', decimals: 18 },
  { symbol: 'wcBTC',  address: '0x3100000000000000000000000000000000000006', decimals: 18 },
  { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
  { symbol: 'JUSD',   address: '0x0987D3720D38847ac6dBB9D025B9dE892a3CA35C', decimals: 18 },
]

const TOKEN_PAIRS = [
  ['ctUSD',  'wcBTC' ],
  ['ctUSD',  'USDC.e'],
  ['ctUSD',  'USDT.e'],
  ['ctUSD',  'WBTC.e'],
  ['wcBTC',  'USDC.e'],
  ['wcBTC',  'USDT.e'],
  ['wcBTC',  'WBTC.e'],
  ['USDC.e', 'USDT.e'],
  ['JUSD',   'wcBTC' ],
  ['JUSD',   'USDC.e'],
  ['JUSD',   'USDT.e'],
  ['JUSD',   'ctUSD' ],
]

// ─── ABIs ─────────────────────────────────────────────────────────────────────

const UNIV3_POOL_ABI = [
  { name: 'token0',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'token1',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'liquidity', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint128' }] },
  { name: 'fee',       type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint24'  }] },
  {
    name: 'slot0',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [
      { name: 'sqrtPriceX96',              type: 'uint160' },
      { name: 'tick',                       type: 'int24'   },
      { name: 'observationIndex',           type: 'uint16'  },
      { name: 'observationCardinality',     type: 'uint16'  },
      { name: 'observationCardinalityNext', type: 'uint16'  },
      { name: 'feeProtocol',                type: 'uint8'   },
      { name: 'unlocked',                   type: 'bool'    },
    ],
  },
]

const ALGEBRA_POOL_ABI = [
  { name: 'token0',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'token1',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'liquidity', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint128' }] },
  {
    name: 'globalState',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [
      { name: 'sqrtPriceX96', type: 'uint160' },
      { name: 'tick',         type: 'int24'   },
      { name: 'fee',          type: 'uint16'  },
    ],
  },
]

const UNIV3_FACTORY_ABI = [
  {
    name: 'getPool',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'tokenA', type: 'address' },
      { name: 'tokenB', type: 'address' },
      { name: 'fee',    type: 'uint24'  },
    ],
    outputs: [{ name: 'pool', type: 'address' }],
  },
]

const ALGEBRA_FACTORY_ABI = [
  {
    name: 'poolByPair',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'tokenA', type: 'address' },
      { name: 'tokenB', type: 'address' },
    ],
    outputs: [{ name: 'pool', type: 'address' }],
  },
]

const client = createPublicClient({
  chain: citrea,
  transport: http()
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getTokenBySymbol(symbol) {
  return ALL_TOKENS.find(t => t.symbol === symbol)
}

function resolveToken(input) {
  if (input.startsWith('0x') && input.length === 42) {
    return ALL_TOKENS.find(t => t.address.toLowerCase() === input.toLowerCase())
      || { address: input, symbol: input.slice(0, 8) + '...', decimals: 18 }
  }
  return TOKEN_REGISTRY[input.toLowerCase()] || null
}

function feeLabel(fee) {
  return `${(fee / 10000).toFixed(2)}% fee`
}

function shortAddr(addr) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`
}

// ─── Suggested Trade Size ─────────────────────────────────────────────────────

const TARGET_NOTIONAL_USD = 50

function getSuggestedTradeSize(symbolA, prices) {
  const btcPrice    = prices?.BTC  || 70000
  const stablePrice = prices?.USDC || 1

  const btcTokens    = ['wcBTC', 'WBTC.e']
  const stableTokens = ['USDC.e', 'USDT.e', 'ctUSD', 'JUSD']

  if (btcTokens.includes(symbolA))    return TARGET_NOTIONAL_USD / btcPrice
  if (stableTokens.includes(symbolA)) return TARGET_NOTIONAL_USD / stablePrice
  return TARGET_NOTIONAL_USD
}

// ─── Pool State Fetcher ───────────────────────────────────────────────────────

async function getPoolState(poolAddress, poolType) {
  try {
    const abi = poolType === 'algebra' ? ALGEBRA_POOL_ABI : UNIV3_POOL_ABI

    const [token0, token1, liquidity] = await Promise.all([
      client.readContract({ address: poolAddress, abi, functionName: 'token0'    }),
      client.readContract({ address: poolAddress, abi, functionName: 'token1'    }),
      client.readContract({ address: poolAddress, abi, functionName: 'liquidity' }),
    ])

    let sqrtPriceX96, fee

    if (poolType === 'algebra') {
      const state = await client.readContract({
        address: poolAddress, abi, functionName: 'globalState',
      })
      sqrtPriceX96 = state[0]
      fee          = Number(state[2])
    } else {
      const [slot0, feeRaw] = await Promise.all([
        client.readContract({ address: poolAddress, abi, functionName: 'slot0' }),
        client.readContract({ address: poolAddress, abi, functionName: 'fee'   }),
      ])
      sqrtPriceX96 = slot0[0]
      fee          = Number(feeRaw)
    }

    return { poolAddress, poolType, token0, token1, liquidity, sqrtPriceX96, fee }

  } catch {
    return null
  }
}

// ─── Pool Lookup ──────────────────────────────────────────────────────────────

async function findAllPools(tokenA, tokenB) {
  const pools    = []
  const feeTiers = [500, 3000, 10000]

  const queryA = getPoolQueryAddress(tokenA)
  const queryB = getPoolQueryAddress(tokenB)

  for (const fee of feeTiers) {
    try {
      const pool = await client.readContract({
        address: JUICESWAP_FACTORY,
        abi: UNIV3_FACTORY_ABI,
        functionName: 'getPool',
        args: [queryA, queryB, fee],
      })
      if (pool !== '0x0000000000000000000000000000000000000000') {
        pools.push({ dex: 'JuiceSwap', pool, type: 'univ3' })
      }
    } catch {}
  }

  try {
    const pool = await client.readContract({
      address: SATSUMA_FACTORY,
      abi: ALGEBRA_FACTORY_ABI,
      functionName: 'poolByPair',
      args: [tokenA, tokenB],
    })
    if (pool !== '0x0000000000000000000000000000000000000000') {
      pools.push({ dex: 'Satsuma', pool, type: 'algebra' })
    }
  } catch {}

  return pools
}

// ─── Arb Math ─────────────────────────────────────────────────────────────────

function detectArb(stateA, stateB, dexA, dexB) {
  if (stateA.liquidity === 0n || stateB.liquidity === 0n) return null
  if (stateA.sqrtPriceX96 === 0n || stateB.sqrtPriceX96 === 0n) return null

  const sqrtA = stateA.sqrtPriceX96
  const sqrtB = stateB.sqrtPriceX96

  let sqrtHigh, sqrtLow, dexHigh, dexLow, stateHigh, stateLow
  if (sqrtA > sqrtB) {
    sqrtHigh = sqrtA; sqrtLow = sqrtB
    dexHigh  = dexA;  dexLow  = dexB
    stateHigh = stateA; stateLow = stateB
  } else {
    sqrtHigh = sqrtB; sqrtLow = sqrtA
    dexHigh  = dexB;  dexLow  = dexA
    stateHigh = stateB; stateLow = stateA
  }

  const PRECISION      = 10000n
  const sqrtSpread     = ((sqrtHigh - sqrtLow) * PRECISION) / sqrtLow
  const priceSpreadBps = Number(sqrtSpread * 2n)
  const combinedFeeBps = (stateA.fee / 100) + (stateB.fee / 100)
  const netProfitBps   = priceSpreadBps - combinedFeeBps

  if (netProfitBps <= 0) return null

  return {
    profitable:      true,
    netProfitBps,
    netProfitPct:    (netProfitBps / 100).toFixed(4),
    priceSpreadBps,
    combinedFeeBps,
    buyOn:           dexLow,
    sellOn:          dexHigh,
    buyFee:          stateLow.fee,
    sellFee:         stateHigh.fee,
    buyPool:         stateLow.poolAddress,
    sellPool:        stateHigh.poolAddress,
    suggestedTrade:  null,
    estProfitTokens: null,
    estProfitUSD:    null,
    gasCostUSD:      null,
    netProfitUSD:    null,
  }
}

// ─── Formatters ───────────────────────────────────────────────────────────────

function formatTokenAmount(n) {
  if (n === 0)    return '0'
  if (n < 0.0001) return n.toFixed(8)
  if (n < 1)      return n.toFixed(6)
  if (n < 1000)   return n.toFixed(4)
  return n.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

function formatArbResult(arb, symbolA, symbolB, usdTradeSize = null) {
  const tradeStr = arb.suggestedTrade != null
    ? `~${formatTokenAmount(arb.suggestedTrade)} ${symbolA}${usdTradeSize ? ` (${formatUSD(usdTradeSize)})` : ''}`
    : 'n/a'

  const profitStr = arb.estProfitTokens != null
    ? `~${formatTokenAmount(arb.estProfitTokens)} ${symbolA}${arb.estProfitUSD ? ` (${formatUSD(arb.estProfitUSD)})` : ''}`
    : 'n/a'

  const buyLabel  = `${arb.buyOn} (${feeLabel(arb.buyFee)})`
  const sellLabel = `${arb.sellOn} (${feeLabel(arb.sellFee)})`

  const sameDex   = arb.buyOn === arb.sellOn
  const poolLines = sameDex ? [
    `   Buy pool:        ${arb.buyPool}`,
    `   Sell pool:       ${arb.sellPool}`,
  ] : [
    `   Buy pool:        ${shortAddr(arb.buyPool)}`,
    `   Sell pool:       ${shortAddr(arb.sellPool)}`,
  ]

  const netColor = arb.netProfitUSD != null
    ? arb.netProfitUSD > 0 ? '✅' : '❌'
    : ''

  return [
    ``,
    `🚨 ARB OPPORTUNITY DETECTED`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
    `   Pair:             ${symbolA} / ${symbolB}`,
    `   Buy on:           ${buyLabel}`,
    `   Sell on:          ${sellLabel}`,
    ...poolLines,
    `   Price spread:     ${(arb.priceSpreadBps / 100).toFixed(4)}%`,
    `   Combined fee:     ${(arb.combinedFeeBps / 100).toFixed(4)}%`,
    `   Est. profit %:    ${arb.netProfitPct}% after fees`,
    `   Suggested trade:  ${tradeStr}`,
    `   Est. profit $:    ${profitStr}`,
    `   Gas cost (est):   ${arb.gasCostUSD != null ? formatUSD(arb.gasCostUSD) : 'n/a'}`,
    `   Net after gas:    ${arb.netProfitUSD != null ? `${netColor} ${formatUSD(arb.netProfitUSD)}` : 'n/a'}`,
    ``,
    `⚠️  Always verify on-chain before executing.`,
    `   Prices can change between detection and execution.`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
  ].join('\n')
}

// ─── Check Pair for Arb ───────────────────────────────────────────────────────

async function checkPairArb(symbolA, symbolB, cachedPrices = null) {
  const tokenA = getTokenBySymbol(symbolA)
  const tokenB = getTokenBySymbol(symbolB)
  if (!tokenA || !tokenB) return null

  const pools = await findAllPools(tokenA.address, tokenB.address)
  if (pools.length < 2) return null

  const states = await Promise.all(
    pools.map(p => getPoolState(p.pool, p.type).then(s => s ? { ...s, dex: p.dex } : null))
  )
  const valid = states.filter(Boolean)
  if (valid.length < 2) return null

  const opportunities = []
  for (let i = 0; i < valid.length; i++) {
    for (let j = i + 1; j < valid.length; j++) {
      const arb = detectArb(valid[i], valid[j], valid[i].dex, valid[j].dex)
      if (arb) opportunities.push({ arb, poolA: valid[i], poolB: valid[j] })
    }
  }

  if (opportunities.length === 0) return null

  opportunities.sort((a, b) => b.arb.netProfitBps - a.arb.netProfitBps)

  // Use cached prices if provided — avoids redundant fetches and stale warnings
  const prices            = cachedPrices || await fetchRedStonePrices()
  const btcPrice          = prices?.BTC  || 70000
  const suggestedTrade    = getSuggestedTradeSize(symbolA, prices)
  const usdTradeSize      = await tokenAmountToUSD(suggestedTrade, symbolA, prices)
  const netProfitFraction = opportunities[0].arb.netProfitBps / 10000
  const estProfitTokens   = suggestedTrade * netProfitFraction
  const estProfitUSD      = usdTradeSize != null ? usdTradeSize * netProfitFraction : null
  const gasCostUSD        = ESTIMATED_GAS_CBTC * btcPrice
  const netProfitUSD      = estProfitUSD != null ? estProfitUSD - gasCostUSD : null

  opportunities[0].arb.suggestedTrade  = suggestedTrade
  opportunities[0].arb.estProfitTokens = estProfitTokens
  opportunities[0].arb.estProfitUSD    = estProfitUSD
  opportunities[0].arb.gasCostUSD      = gasCostUSD
  opportunities[0].arb.netProfitUSD    = netProfitUSD

  return {
    best: { ...opportunities[0], usdTradeSize },
    all:  opportunities,
    symbolA,
    symbolB,
  }
}

// ─── Debounce State ───────────────────────────────────────────────────────────

const lastAlerted = new Map()
const DEBOUNCE_MS = parseInt(process.env.ARB_DEBOUNCE_MIN || '30', 10) * 60 * 1000

function shouldAlert(pairKey, netProfitBps) {
  if (netProfitBps < ARB_ALERT_THRESHOLD_BPS) return false
  const last = lastAlerted.get(pairKey)
  if (!last) return true
  const profitJump  = netProfitBps - last.netProfitBps
  const timeElapsed = Date.now() - last.timestamp
  return timeElapsed >= DEBOUNCE_MS || profitJump >= 25
}

function markAlerted(pairKey, netProfitBps) {
  lastAlerted.set(pairKey, { netProfitBps, timestamp: Date.now() })
}

// ─── Single Pair Check ────────────────────────────────────────────────────────

async function checkArb(args) {
  if (!args[0] || !args[1]) {
    console.log(`
Usage:
  arb:check <tokenA> <tokenB>    Check a specific pair for arb opportunities

Examples:
  node index.js arb:check ctUSD wcBTC
  node index.js arb:check wcBTC USDC.e
    `)
    return
  }

  const resolvedA = resolveToken(args[0])
  const resolvedB = resolveToken(args[1])

  if (!resolvedA) { console.log(`❌ Unknown token "${args[0]}"`); return }
  if (!resolvedB) { console.log(`❌ Unknown token "${args[1]}"`); return }

  console.log(`\n🔍 Checking arb for ${resolvedA.symbol} / ${resolvedB.symbol}...`)

  const result = await checkPairArb(resolvedA.symbol, resolvedB.symbol)

  if (!result) {
    console.log(`✅ No arb opportunity found for ${resolvedA.symbol} / ${resolvedB.symbol}.`)
    console.log(`   Either only one DEX has this pool, or spread is within fees.\n`)
    return
  }

  console.log(formatArbResult(
    result.best.arb,
    result.symbolA,
    result.symbolB,
    result.best.usdTradeSize
  ))
  console.log()
}

// ─── Scan All Pairs ───────────────────────────────────────────────────────────

async function scanAllArb() {
  console.log(`\n🔍 Scanning all pairs for arb opportunities...\n`)

  // Fetch prices once — shared across all pair checks
  const prices        = await fetchRedStonePrices()
  const opportunities = []

  for (const [symA, symB] of TOKEN_PAIRS) {
    process.stdout.write(`   Checking ${symA.padEnd(7)} / ${symB.padEnd(7)}...\r`)
    const result = await checkPairArb(symA, symB, prices)
    if (result) opportunities.push(result)
  }

  process.stdout.write(`                                             \r`)

  if (opportunities.length === 0) {
    console.log(`✅ No arb opportunities found across all pairs.`)
    console.log(`   All spreads are within combined fee thresholds.\n`)
    return
  }

  opportunities.sort((a, b) => b.best.arb.netProfitBps - a.best.arb.netProfitBps)
  console.log(`🚨 Found ${opportunities.length} arb opportunit${opportunities.length > 1 ? 'ies' : 'y'}:`)

  for (const opp of opportunities) {
    console.log(formatArbResult(
      opp.best.arb,
      opp.symbolA,
      opp.symbolB,
      opp.best.usdTradeSize
    ))
  }
  console.log()
}

// ─── Live Monitor ─────────────────────────────────────────────────────────────

async function monitorArb() {
  console.log(`🔍 Monitoring all pairs for arb opportunities...`)
  console.log(`   Threshold: ${ARB_ALERT_THRESHOLD_BPS}bps (${(ARB_ALERT_THRESHOLD_BPS / 100).toFixed(2)}%)`)
  console.log(`   Interval:  ${ARB_MONITOR_INTERVAL_MS / 1000}s`)
  console.log(`   Press Ctrl+C to stop.\n`)

  const scan = async () => {
    const timestamp = new Date().toLocaleTimeString()
    process.stdout.write(`   [${timestamp}] Scanning all pairs...`)

    // Fetch prices once per scan cycle
    const prices        = await fetchRedStonePrices()
    const opportunities = []

    for (const [symA, symB] of TOKEN_PAIRS) {
      const result = await checkPairArb(symA, symB, prices)
      if (result) opportunities.push(result)
    }

    if (opportunities.length === 0) {
      process.stdout.write(`  ✅ No opportunities found.\r`)
    } else {
      process.stdout.write(`\n`)
      opportunities.sort((a, b) => b.best.arb.netProfitBps - a.best.arb.netProfitBps)

      for (const opp of opportunities) {
        const msg       = formatArbResult(
          opp.best.arb,
          opp.symbolA,
          opp.symbolB,
          opp.best.usdTradeSize
        )
        const pairKey   = `${opp.symbolA}/${opp.symbolB}`
        const profitBps = opp.best.arb.netProfitBps

        console.log(msg)

        if (shouldAlert(pairKey, profitBps)) {
          await sendTelegram(`<pre>${msg}</pre>`)
          markAlerted(pairKey, profitBps)
        }
      }
    }
  }

  await scan()
  setInterval(scan, ARB_MONITOR_INTERVAL_MS)
}

// ─── Summary for liquidity.js ─────────────────────────────────────────────────

async function getArbSummaryForPair(symbolA, symbolB) {
  const result = await checkPairArb(symbolA, symbolB)
  if (!result) return null
  return formatArbResult(
    result.best.arb,
    result.symbolA,
    result.symbolB,
    result.best.usdTradeSize
  )
}

// ─── Exports ──────────────────────────────────────────────────────────────────

export { checkArb, scanAllArb, monitorArb, getArbSummaryForPair }
