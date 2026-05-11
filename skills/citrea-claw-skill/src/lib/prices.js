import { createPublicClient, http } from 'viem'

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

// ─── RedStone Push Feed Contracts on Citrea ───────────────────────────────────
const PRICE_FEEDS = {
  BTC:  '0xc555c100DB24dF36D406243642C169CC5A937f09',
  USDC: '0xf0DEbDAE819b354D076b0D162e399BE013A856d3',
  USDT: '0x4aF6b78d92432D32E3a635E824d3A541866f7a78',
}

const AGGREGATOR_ABI = [
  {
    name: 'latestRoundData',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [
      { name: 'roundId',         type: 'uint80'  },
      { name: 'answer',          type: 'int256'  },
      { name: 'startedAt',       type: 'uint256' },
      { name: 'updatedAt',       type: 'uint256' },
      { name: 'answeredInRound', type: 'uint80'  },
    ],
  },
  {
    name: 'decimals',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint8' }],
  },
]

// Token → feed mapping
// null  = stablecoin, hardcoded to $1
// false = no feed available
const TOKEN_PRICE_FEED = {
  'cBTC':   'BTC',
  'wcBTC':  'BTC',
  'WBTC.e': 'BTC',
  'ctUSD':  null,    // stablecoin
  'USDC.e': null,    // stablecoin
  'USDT.e': null,    // stablecoin
  'JUSD':   null,    // BTC-backed stablecoin, USD peg
}

const STABLECOIN_PRICE_USD = 1.0

const client = createPublicClient({
  chain: citrea,
  transport: http()
})

// ─── Fetch Prices from RedStone On-Chain Feeds ────────────────────────────────

async function fetchRedStonePrices() {
  try {
    const results = await Promise.all(
      Object.entries(PRICE_FEEDS).map(async ([symbol, address]) => {
        const [roundData, decimals] = await Promise.all([
          client.readContract({
            address,
            abi: AGGREGATOR_ABI,
            functionName: 'latestRoundData',
          }),
          client.readContract({
            address,
            abi: AGGREGATOR_ABI,
            functionName: 'decimals',
          }),
        ])

        const price     = Number(roundData[1]) / 10 ** decimals
        const updatedAt = Number(roundData[3])
        const age       = Math.floor(Date.now() / 1000) - updatedAt

        if (age > 7200) {
          console.warn(`⚠️  ${symbol} price is ${Math.floor(age / 60)} minutes old`)
        }

        return [symbol, price]
      })
    )

    return Object.fromEntries(results)

  } catch (error) {
    console.error(`⚠️  Could not fetch RedStone prices: ${error.message}`)
    return null
  }
}

// ─── Get USD price for a token symbol ────────────────────────────────────────

async function getTokenUSDPrice(symbol, cachedPrices = null) {
  const feedId = TOKEN_PRICE_FEED[symbol]

  // Stablecoin — hardcoded $1
  if (feedId === null) return STABLECOIN_PRICE_USD

  // No feed available for this token
  if (!feedId) return null

  const prices = cachedPrices || await fetchRedStonePrices()
  if (!prices) return null

  return prices[feedId] || null
}

// ─── Convert token amount to USD ─────────────────────────────────────────────

async function tokenAmountToUSD(amount, symbol, cachedPrices = null) {
  const price = await getTokenUSDPrice(symbol, cachedPrices)
  if (price === null) return null
  return amount * price
}

// ─── Format USD value ─────────────────────────────────────────────────────────

function formatUSD(amount) {
  if (amount === null || amount === undefined) return 'N/A'
  if (amount < 0.01)      return '<$0.01'
  if (amount < 1000)      return `$${amount.toFixed(2)}`
  if (amount < 1_000_000) return `$${(amount / 1000).toFixed(2)}K`
  return `$${(amount / 1_000_000).toFixed(2)}M`
}

export { fetchRedStonePrices, getTokenUSDPrice, tokenAmountToUSD, formatUSD }
