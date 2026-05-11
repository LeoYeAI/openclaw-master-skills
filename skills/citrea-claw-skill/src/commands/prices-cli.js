import 'dotenv/config'
import { createPublicClient, http } from 'viem'
import { fetchRedStonePrices, formatUSD } from '../lib/prices.js'

const citrea = {
  id: 4114,
  name: 'Citrea Mainnet',
  nativeCurrency: { name: 'Citrea Bitcoin', symbol: 'cBTC', decimals: 18 },
  rpcUrls: { default: { http: ['https://rpc.mainnet.citrea.xyz'] } },
}

const client = createPublicClient({ chain: citrea, transport: http() })

const ALL_TOKENS = [
  { symbol: 'ctUSD',  address: '0x8D82c4E3c936C7B5724A382a9c5a4E6Eb7aB6d5D', decimals: 18 },
  { symbol: 'wcBTC',  address: '0x3100000000000000000000000000000000000006', decimals: 18 },
  { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
  { symbol: 'JUSD',   address: '0x0987D3720D38847ac6dBB9D025B9dE892a3CA35C', decimals: 18 },
]

const BTC_TOKENS    = ['wcBTC', 'WBTC.e', 'cBTC']
const STABLE_TOKENS = ['USDC.e', 'USDT.e', 'ctUSD', 'JUSD']

const JUICESWAP_FACTORY = '0xd809b1285aDd8eeaF1B1566Bf31B2B4C4Bba8e82'
const SATSUMA_FACTORY   = '0x10253594A832f967994b44f33411940533302ACb'

const POOL_ADDRESS_OVERRIDE = {
  '0x0987d3720d38847ac6dbb9d025b9de892a3ca35c': '0x1b70ae756b1089cc5948e4f8a2AD498DF30E897d',
}

function getPoolQueryAddress(address) {
  return POOL_ADDRESS_OVERRIDE[address.toLowerCase()] || address
}

// ─── ABIs ─────────────────────────────────────────────────────────────────────

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

const SLOT0_ABI = [
  {
    name: 'slot0',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [
      { name: 'sqrtPriceX96', type: 'uint160' },
      { name: 'tick',         type: 'int24'   },
    ],
  },
  { name: 'fee', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint24' }] },
]

const GLOBAL_STATE_ABI = [
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

// ─── Helpers ──────────────────────────────────────────────────────────────────

function resolveToken(input) {
  const lower = input.toLowerCase()
  return ALL_TOKENS.find(t =>
    t.symbol.toLowerCase() === lower ||
    t.address.toLowerCase() === lower
  ) || null
}

function sqrtPriceX96ToRaw(sqrtPriceX96) {
  const Q96       = 2 ** 96
  const sqrtFloat = Number(sqrtPriceX96) / Q96
  return sqrtFloat * sqrtFloat
}

// Convert raw price to human price, with sanity checking.
// Some pools encode human price directly, others encode raw token ratios.
// We detect which by checking if the result is in a sensible range.
// Returns null if the pool appears to be uninitialized or badly initialized.
function adjustForDecimals(rawPrice, token0, token1) {
  const isBtc0    = BTC_TOKENS.includes(token0.symbol)
  const isBtc1    = BTC_TOKENS.includes(token1.symbol)
  const isStable0 = STABLE_TOKENS.includes(token0.symbol)
  const isStable1 = STABLE_TOKENS.includes(token1.symbol)

  if (token0.decimals === token1.decimals) {
    // Same decimals — raw price = human price
    // Sanity check for BTC/BTC: should be near 1.0
    if (isBtc0 && isBtc1) {
      if (rawPrice > 1000 || rawPrice < 0.001) return null // badly initialized
    }
    // Sanity check for stable/stable: should be near 1.0
    if (isStable0 && isStable1) {
      if (rawPrice > 1000 || rawPrice < 0.001) return null
    }
    return rawPrice
  }

  // Different decimals — try adjustment
  const adjusted = rawPrice * (10 ** token0.decimals) / (10 ** token1.decimals)

  if (isStable0 && isStable1) {
    // stable/stable should be near 1.0
    if (adjusted > 1000 || adjusted < 0.001) return rawPrice  // pool uses human price
    return adjusted
  }

  if ((isBtc0 && isStable1) || (isStable0 && isBtc1)) {
    // BTC/stable: expect 1,000–500,000 range
    if (adjusted >= 1000 && adjusted <= 1e8) return adjusted  // adjustment worked
    if (rawPrice >= 1000 && rawPrice <= 1e8) return rawPrice  // pool uses human price
    return null // neither makes sense
  }

  return adjusted
}

function formatPrice(price, symbol) {
  if (STABLE_TOKENS.includes(symbol)) return formatUSD(price)
  if (price < 0.0001) return price.toFixed(10)
  if (price < 1)      return price.toFixed(6)
  if (price < 1000)   return price.toFixed(4)
  return price.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

function getOraclePrice(symbol, prices) {
  const map = {
    'cBTC':   prices?.BTC,
    'wcBTC':  prices?.BTC,
    'WBTC.e': prices?.BTC,
    'USDC.e': prices?.USDC,
    'USDT.e': prices?.USDT,
    'ctUSD':  prices?.USDC,
    'JUSD':   prices?.USDC,
  }
  return map[symbol] || null
}

// Returns { baseSymbol, quoteSymbol, displayPrice } or null if pool is invalid
function computeDisplayPrice(sqrtPriceX96, tokenA, tokenB, queryAddrA, queryAddrB) {
  const token0IsA  = queryAddrA.toLowerCase() < queryAddrB.toLowerCase()
  const token0     = token0IsA ? tokenA : tokenB
  const token1     = token0IsA ? tokenB : tokenA

  const rawPrice   = sqrtPriceX96ToRaw(sqrtPriceX96)
  const humanPrice = adjustForDecimals(rawPrice, token0, token1)

  if (humanPrice === null) return null
  // humanPrice = token1 per token0 in human units

  const isBtcA = BTC_TOKENS.includes(tokenA.symbol)
  const isBtcB = BTC_TOKENS.includes(tokenB.symbol)

  if (isBtcA && !isBtcB) {
    // want: 1 BTC = X stable
    if (token0IsA) {
      // token0=BTC → humanPrice = stable/BTC ✓
      return { baseSymbol: tokenA.symbol, quoteSymbol: tokenB.symbol, displayPrice: humanPrice }
    } else {
      // token0=stable → humanPrice = BTC/stable → invert
      return { baseSymbol: tokenA.symbol, quoteSymbol: tokenB.symbol, displayPrice: 1 / humanPrice }
    }
  } else if (!isBtcA && isBtcB) {
    // want: 1 BTC = X stable (tokenB is BTC)
    if (token0IsA) {
      // token0=stable → humanPrice = BTC/stable → invert → stable/BTC
      return { baseSymbol: tokenB.symbol, quoteSymbol: tokenA.symbol, displayPrice: 1 / humanPrice }
    } else {
      // token0=BTC → humanPrice = stable/BTC ✓
      return { baseSymbol: tokenB.symbol, quoteSymbol: tokenA.symbol, displayPrice: humanPrice }
    }
  } else {
    // stable/stable or BTC/BTC → 1 tokenA = X tokenB
    if (token0IsA) {
      // token0=tokenA → humanPrice = tokenB/tokenA ✓
      return { baseSymbol: tokenA.symbol, quoteSymbol: tokenB.symbol, displayPrice: humanPrice }
    } else {
      // token0=tokenB → humanPrice = tokenA/tokenB → invert
      return { baseSymbol: tokenA.symbol, quoteSymbol: tokenB.symbol, displayPrice: 1 / humanPrice }
    }
  }
}

// ─── Price Command ────────────────────────────────────────────────────────────

export async function priceCheck(args) {
  if (!args[0]) {
    console.log(`
Usage:
  price <token>    Show current USD price from RedStone oracle

Examples:
  node index.js price wcBTC
  node index.js price USDC.e
  node index.js price ctUSD
  node index.js price JUSD
    `)
    return
  }

  const token = resolveToken(args[0])
  if (!token) {
    console.log(`❌ Unknown token "${args[0]}"`)
    return
  }

  console.log(`\n🔍 Fetching price for ${token.symbol}...`)

  const prices = await fetchRedStonePrices()
  const price  = getOraclePrice(token.symbol, prices)

  if (!price) {
    console.log(`⚠️  No RedStone price feed available for ${token.symbol}\n`)
    return
  }

  console.log(`
💰 ${token.symbol} Price
━━━━━━━━━━━━━━━━━━━━━━━━
   Token:    ${token.symbol}
   Address:  ${token.address}
   Price:    ${formatUSD(price)}
   Source:   RedStone oracle (on-chain)
━━━━━━━━━━━━━━━━━━━━━━━━
  `)
}

// ─── Pool Price Command ───────────────────────────────────────────────────────

export async function poolPrice(args) {
  if (!args[0] || !args[1]) {
    console.log(`
Usage:
  pool:price <tokenA> <tokenB>    Show implied price from each DEX

Examples:
  node index.js pool:price wcBTC USDC.e
  node index.js pool:price JUSD wcBTC
  node index.js pool:price ctUSD USDC.e
    `)
    return
  }

  const tokenA = resolveToken(args[0])
  const tokenB = resolveToken(args[1])

  if (!tokenA) { console.log(`❌ Unknown token "${args[0]}"`); return }
  if (!tokenB) { console.log(`❌ Unknown token "${args[1]}"`); return }

  console.log(`\n🔍 Fetching pool prices for ${tokenA.symbol} / ${tokenB.symbol}...`)

  const rows     = []
  const feeTiers = [500, 3000, 10000]

  const queryA = getPoolQueryAddress(tokenA.address)
  const queryB = getPoolQueryAddress(tokenB.address)

  // JuiceSwap pools
  for (const fee of feeTiers) {
    try {
      const poolAddr = await client.readContract({
        address: JUICESWAP_FACTORY,
        abi: UNIV3_FACTORY_ABI,
        functionName: 'getPool',
        args: [queryA, queryB, fee],
      })
      if (poolAddr === '0x0000000000000000000000000000000000000000') continue

      const [slot0, feeRaw] = await Promise.all([
        client.readContract({ address: poolAddr, abi: SLOT0_ABI, functionName: 'slot0' }),
        client.readContract({ address: poolAddr, abi: SLOT0_ABI, functionName: 'fee'   }),
      ])

      const result = computeDisplayPrice(slot0[0], tokenA, tokenB, queryA, queryB)
      if (!result) continue // skip badly initialized pools

      rows.push({
        dex:          'JuiceSwap',
        fee:          `${(Number(feeRaw) / 10000).toFixed(2)}%`,
        pool:         poolAddr,
        ...result,
      })
    } catch {}
  }

  // Satsuma pool
  try {
    const poolAddr = await client.readContract({
      address: SATSUMA_FACTORY,
      abi: ALGEBRA_FACTORY_ABI,
      functionName: 'poolByPair',
      args: [tokenA.address, tokenB.address],
    })
    if (poolAddr !== '0x0000000000000000000000000000000000000000') {
      const state = await client.readContract({
        address: poolAddr,
        abi: GLOBAL_STATE_ABI,
        functionName: 'globalState',
      })

      const result = computeDisplayPrice(state[0], tokenA, tokenB, tokenA.address, tokenB.address)
      if (result) {
        rows.push({
          dex:  'Satsuma',
          fee:  `${(Number(state[2]) / 10000).toFixed(2)}%`,
          pool: poolAddr,
          ...result,
        })
      }
    }
  } catch {}

  if (rows.length === 0) {
    console.log(`⚠️  No valid pools found for ${tokenA.symbol} / ${tokenB.symbol}\n`)
    return
  }

  const prices = await fetchRedStonePrices()

  console.log(`
💱 ${tokenA.symbol} / ${tokenB.symbol} Pool Prices
━━━━━━━━━━━━━━━━━━━━━━━━`)

  for (const row of rows) {
    const oraclePrice = getOraclePrice(row.baseSymbol, prices)
    const deviation   = oraclePrice
      ? ` (${((row.displayPrice - oraclePrice) / oraclePrice * 100).toFixed(3)}% vs oracle)`
      : ''
    console.log(`   ${row.dex.padEnd(10)} ${row.fee.padEnd(8)}  1 ${row.baseSymbol} = ${formatPrice(row.displayPrice, row.quoteSymbol)}${deviation}`)
    console.log(`   Pool: ${row.pool}`)
    console.log()
  }

  const oraclePrice = getOraclePrice(rows[0].baseSymbol, prices)
  if (oraclePrice) {
    console.log(`   Oracle price:  1 ${rows[0].baseSymbol} = ${formatUSD(oraclePrice)} (RedStone)`)
  }
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━`)
  console.log()
}
