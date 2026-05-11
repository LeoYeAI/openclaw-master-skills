import 'dotenv/config'
import { createPublicClient, http, formatUnits } from 'viem'
import { fetchRedStonePrices, formatUSD } from '../lib/prices.js'

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

// ─── Token Registry ───────────────────────────────────────────────────────────
const TOKENS = [
  { symbol: 'ctUSD',  address: '0x8D82c4E3c936C7B5724A382a9c5a4E6Eb7aB6d5D', decimals: 18 },
  { symbol: 'wcBTC',  address: '0x3100000000000000000000000000000000000006', decimals: 18 },
  { symbol: 'USDC.e', address: '0xE045e6c36cF77FAA2CfB54466D71A3aEF7bbE839', decimals: 6  },
  { symbol: 'USDT.e', address: '0x9f3096Bac87e7F03DC09b0B416eB0DF837304dc4', decimals: 6  },
  { symbol: 'WBTC.e', address: '0xDF240DC08B0FdaD1d93b74d5048871232f6BEA3d', decimals: 8  },
  { symbol: 'JUSD',   address: '0x0987D3720D38847ac6dBB9D025B9dE892a3CA35C', decimals: 18 },
]

const ERC20_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs:  [{ name: 'account', type: 'address' }],
    outputs: [{ name: '',        type: 'uint256'  }],
  },
]

const client = createPublicClient({
  chain: citrea,
  transport: http()
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatTokenAmount(n) {
  if (n === 0)    return '0'
  if (n < 0.0001) return n.toFixed(8)
  if (n < 1)      return n.toFixed(6)
  if (n < 1000)   return n.toFixed(4)
  return n.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

function getUSDPrice(symbol, prices) {
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

// ─── Wallet Balance ───────────────────────────────────────────────────────────

export async function walletBalance(args) {
  if (!args[0]) {
    console.log(`
Usage:
  balance <address>    Show cBTC + token balances for a wallet

Examples:
  node index.js balance 0xYourAddress
    `)
    return
  }

  const address = args[0]

  if (!address.startsWith('0x') || address.length !== 42) {
    console.log(`❌ Invalid address "${address}" — must be a 42-character hex address`)
    return
  }

  console.log(`\n🔍 Fetching balances for ${address}...`)

  const [nativeBalance, ...tokenBalances] = await Promise.all([
    client.getBalance({ address }),
    ...TOKENS.map(t =>
      client.readContract({
        address:      t.address,
        abi:          ERC20_ABI,
        functionName: 'balanceOf',
        args:         [address],
      }).catch(() => 0n)
    ),
  ])

  const prices = await fetchRedStonePrices()

  const rows = []
  let totalUSD = 0

  // Native cBTC
  const cbtcAmount = Number(formatUnits(nativeBalance, 18))
  const cbtcPrice  = getUSDPrice('cBTC', prices)
  const cbtcUSD    = cbtcPrice ? cbtcAmount * cbtcPrice : null
  if (cbtcUSD) totalUSD += cbtcUSD
  rows.push({
    symbol:  'cBTC',
    amount:  cbtcAmount,
    usd:     cbtcUSD,
    nonZero: cbtcAmount > 0,
  })

  // ERC20 tokens
  for (let i = 0; i < TOKENS.length; i++) {
    const token  = TOKENS[i]
    const raw    = tokenBalances[i]
    const amount = Number(formatUnits(raw, token.decimals))
    const price  = getUSDPrice(token.symbol, prices)
    const usd    = price ? amount * price : null
    if (usd) totalUSD += usd
    rows.push({
      symbol:  token.symbol,
      amount,
      usd,
      nonZero: amount > 0,
    })
  }

  console.log(`
💼 Wallet Balance
━━━━━━━━━━━━━━━━━━━━━━━━
   Address: ${address}
   Network: Citrea Mainnet
━━━━━━━━━━━━━━━━━━━━━━━━`)

  for (const row of rows) {
    const amountStr = formatTokenAmount(row.amount).padEnd(20)
    const usdStr    = row.usd != null ? formatUSD(row.usd) : ''
    const zeroMark  = row.nonZero ? '  ' : '  ·'
    console.log(`${zeroMark}  ${row.symbol.padEnd(8)}  ${amountStr}  ${usdStr}`)
  }

  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━`)
  console.log(`   Total value:  ${formatUSD(totalUSD)}`)
  console.log(`   Explorer:     https://explorer.mainnet.citrea.xyz/address/${address}`)
  console.log()
}
