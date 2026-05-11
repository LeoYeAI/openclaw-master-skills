import { createPublicClient, http, formatUnits } from 'viem'
import { fetchRedStonePrices, formatUSD } from '../lib/prices.js'
import { getArbSummaryForPair } from './arb.js'

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
const EXPLORER_ADDR     = 'https://explorer.mainnet.citrea.xyz/address'

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
}

const ALL_TOKENS = [
  { symbol: 'ctUSD',  address: '0x8D82c4E3c936C7B5724A382a9c5a4E6Eb7aB6d5D', decimals: 18 },
  { symbol: 'wcBTC',  address: '0x3100000000000000000000000000000000000006', decimals: 18 },
  { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
]

// ─── ABIs ─────────────────────────────────────────────────────────────────────

const ERC20_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'string' }],
  },
  {
    name: 'decimals',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint8' }],
  },
]

const POOL_ABI = [
  { name: 'token0',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'token1',    type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'address' }] },
  { name: 'liquidity', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint128' }] },
  { name: 'fee',       type: 'function', stateMutability: 'view', inputs: [], outputs: [{ name: '', type: 'uint24'  }] },
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

// ─── Token Resolver ───────────────────────────────────────────────────────────

function resolveToken(input) {
  if (input.startsWith('0x') && input.length === 42) {
    return { address: input, symbol: input.slice(0, 8) + '...', decimals: 18 }
  }

  const match = TOKEN_REGISTRY[input.toLowerCase()]
  if (match) return match

  const fuzzy = ALL_TOKENS.filter(t =>
    t.symbol.toLowerCase().includes(input.toLowerCase())
  )

  if (fuzzy.length === 1) return fuzzy[0]
  if (fuzzy.length > 1)   return { suggestions: fuzzy }

  return null
}

function printSuggestions(input, suggestions) {
  console.log(`\n❓ "${input}" didn't match any known token. Did you mean:\n`)
  for (const t of suggestions) {
    console.log(`   ${t.symbol.padEnd(8)}  ${t.address}`)
  }
  console.log(`\nOr use the full token address directly.`)
  console.log(`\nKnown tokens on Citrea:`)
  for (const t of ALL_TOKENS) {
    console.log(`   ${t.symbol.padEnd(8)}  ${t.address}`)
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function getTokenInfo(address) {
  const lower = address.toLowerCase()
  const known = Object.values(TOKEN_REGISTRY).find(
    t => t.address.toLowerCase() === lower
  )
  if (known) return known
  try {
    const [symbol, decimals] = await Promise.all([
      client.readContract({ address, abi: ERC20_ABI, functionName: 'symbol'   }),
      client.readContract({ address, abi: ERC20_ABI, functionName: 'decimals' }),
    ])
    return { symbol, decimals }
  } catch {
    return { symbol: address.slice(0, 8) + '...', decimals: 18 }
  }
}

function formatFee(fee) {
  return (fee / 10000).toFixed(2) + '%'
}

function formatAmount(amount, decimals) {
  const n = parseFloat(formatUnits(amount, decimals))
  if (n === 0) return '0'
  if (n < 0.000001) return '0 (dust)'
  if (n < 1) return n.toFixed(6)
  if (n < 1000) return n.toFixed(4)
  return n.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

// ─── Pool Lookup ──────────────────────────────────────────────────────────────

async function findPool(tokenA, tokenB, fee = null) {
  const results = []
  const feeTiers = fee ? [fee] : [500, 3000, 10000]

  for (const f of feeTiers) {
    try {
      const pool = await client.readContract({
        address: JUICESWAP_FACTORY,
        abi: UNIV3_FACTORY_ABI,
        functionName: 'getPool',
        args: [tokenA, tokenB, f],
      })
      if (pool !== '0x0000000000000000000000000000000000000000') {
        results.push({ dex: 'JuiceSwap', pool, type: 'univ3' })
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
      results.push({ dex: 'Satsuma', pool, type: 'algebra' })
    }
  } catch {}

  return results
}

// ─── Pool TVL ─────────────────────────────────────────────────────────────────

async function getPoolTVL(poolAddress, poolType = 'univ3', dexName = '') {
  try {
    const abi = poolType === 'algebra' ? ALGEBRA_POOL_ABI : POOL_ABI

    const [token0Addr, token1Addr, liquidity] = await Promise.all([
      client.readContract({ address: poolAddress, abi, functionName: 'token0'    }),
      client.readContract({ address: poolAddress, abi, functionName: 'token1'    }),
      client.readContract({ address: poolAddress, abi, functionName: 'liquidity' }),
    ])

    const [token0, token1] = await Promise.all([
      getTokenInfo(token0Addr),
      getTokenInfo(token1Addr),
    ])

    let fee
    if (poolType === 'algebra') {
      const state = await client.readContract({
        address: poolAddress,
        abi,
        functionName: 'globalState',
      })
      fee = state[2]
    } else {
      fee = await client.readContract({
        address: poolAddress,
        abi,
        functionName: 'fee',
      })
    }

    const [balance0Raw, balance1Raw] = await Promise.all([
      client.readContract({
        address: token0Addr,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [poolAddress],
      }),
      client.readContract({
        address: token1Addr,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [poolAddress],
      }),
    ])

    const liquidityStatus = liquidity === 0n
      ? '0 (no active liquidity in current price range)'
      : liquidity.toLocaleString()

    const lines = [
      `💧 Pool TVL${dexName ? ` — ${dexName}` : ''}`,
      `━━━━━━━━━━━━━━━━━━━━━━━━`,
      `   Pair:  ${token0.symbol} / ${token1.symbol}`,
      `   Fee:   ${poolType === 'algebra'
        ? (Number(fee) / 10000).toFixed(4) + '%'
        : formatFee(fee)}`,
      `   Type:  ${poolType === 'algebra' ? 'Algebra (Satsuma)' : 'Uniswap V3 (JuiceSwap)'}`,
      ``,
      `📊 Token Reserves`,
      `   ${token0.symbol.padEnd(8)}  ${formatAmount(balance0Raw, token0.decimals)}`,
      `   ${token1.symbol.padEnd(8)}  ${formatAmount(balance1Raw, token1.decimals)}`,
      ``,
      `📈 Active Liquidity`,
      `   ${liquidityStatus}`,
      ``,
      `🔍 ${EXPLORER_ADDR}/${poolAddress}`,
    ]

    console.log(lines.join('\n'))

  } catch (error) {
    console.error(`❌ Error fetching pool TVL: ${error.message}`)
  }
}

// ─── Main Entry ───────────────────────────────────────────────────────────────

async function poolLiquidity(args) {

  // Usage 1: direct pool address
  if (args[0]?.startsWith('0x') && args[0].length === 42) {
    const poolType = args[1] || 'univ3'
    await getPoolTVL(args[0], poolType)
    return
  }

  // Usage 2: two token symbols or addresses
  if (args[0] && args[1]) {
    const resolvedA = resolveToken(args[0])
    const resolvedB = resolveToken(args[1])

    if (!resolvedA) {
      console.log(`\n❌ Unknown token "${args[0]}"`)
      console.log(`\nKnown tokens:`)
      for (const t of ALL_TOKENS) console.log(`   ${t.symbol.padEnd(8)}  ${t.address}`)
      return
    }
    if (resolvedA.suggestions) { printSuggestions(args[0], resolvedA.suggestions); return }

    if (!resolvedB) {
      console.log(`\n❌ Unknown token "${args[1]}"`)
      console.log(`\nKnown tokens:`)
      for (const t of ALL_TOKENS) console.log(`   ${t.symbol.padEnd(8)}  ${t.address}`)
      return
    }
    if (resolvedB.suggestions) { printSuggestions(args[1], resolvedB.suggestions); return }

    const fee = args[2] ? parseInt(args[2]) : null
    console.log(`\n🔍 Looking up ${resolvedA.symbol} / ${resolvedB.symbol} pools...\n`)

    const pools = await findPool(resolvedA.address, resolvedB.address, fee)

    if (pools.length === 0) {
      console.log(`❌ No pool found for ${resolvedA.symbol} / ${resolvedB.symbol}.`)
      console.log(`   Try a different fee tier: 500, 3000, or 10000`)
      return
    }

    for (const { dex, pool, type } of pools) {
      console.log(`🔶 ${dex}`)
      await getPoolTVL(pool, type, dex)
      console.log()
    }

    // Check for arb opportunity across the pools found
    const arbSummary = await getArbSummaryForPair(resolvedA.symbol, resolvedB.symbol)
    if (arbSummary) console.log(arbSummary)
    return
  }

  // Usage 3: single token — find all pools containing it
  if (args[0]) {
    const resolved = resolveToken(args[0])

    if (!resolved) {
      console.log(`\n❌ Unknown token "${args[0]}"`)
      console.log(`\nKnown tokens:`)
      for (const t of ALL_TOKENS) console.log(`   ${t.symbol.padEnd(8)}  ${t.address}`)
      return
    }
    if (resolved.suggestions) { printSuggestions(args[0], resolved.suggestions); return }

    console.log(`\n🔍 Finding all pools containing ${resolved.symbol}...\n`)

    const otherTokens = ALL_TOKENS.filter(
      t => t.address.toLowerCase() !== resolved.address.toLowerCase()
    )

    let foundAny = false

    for (const other of otherTokens) {
      const pools = await findPool(resolved.address, other.address, null)
      for (const { dex, pool, type } of pools) {
        console.log(`🔶 ${dex} — ${resolved.symbol} / ${other.symbol}`)
        await getPoolTVL(pool, type, dex)
        console.log()
        foundAny = true
      }

      // Check for arb on this pair
      if (foundAny) {
        const arbSummary = await getArbSummaryForPair(resolved.symbol, other.symbol)
        if (arbSummary) console.log(arbSummary)
      }
    }

    if (!foundAny) {
      console.log(`❌ No pools found containing ${resolved.symbol}.`)
    }
    return
  }

  // No args — show help
  console.log(`
Usage:
  pool:liquidity <poolAddress>              Query pool TVL by address (default: univ3)
  pool:liquidity <poolAddress> algebra      Query Satsuma pool by address
  pool:liquidity <tokenA> <tokenB>          Look up pool by token pair
  pool:liquidity <token>                    Find all pools containing a token

Token names accepted: ctUSD, wcBTC, USDC.e, USDT.e, WBTC.e
Or use full 0x addresses.

Examples:
  node index.js pool:liquidity 0xB3dA7635d23610B8C061f14304Be05e93F17B49E
  node index.js pool:liquidity ctUSD wcBTC
  node index.js pool:liquidity ctUSD wcBTC 500
  node index.js pool:liquidity ctUSD
  `)
}

export { poolLiquidity }
