import 'dotenv/config'
import { createPublicClient, http, formatUnits } from 'viem'

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

const client = createPublicClient({ chain: citrea, transport: http() })

// Router addresses to watch
const ROUTERS = {
  '0x1b9d3E8020Be83C0f2b9eDe6CC6E26C9F2C4Ee2a': 'JuiceSwap',
  '0x3012E9049d05B4B5369D690114D5A5861EbB85cb': 'Satsuma',
}

const TOKEN_MAP = {
  '0x8d82c4e3c936c7b5724a382a9c5a4e6eb7ab6d5d': { symbol: 'ctUSD',  decimals: 18 },
  '0x3100000000000000000000000000000000000006': { symbol: 'wcBTC',  decimals: 18 },
  '0xe045e6c36cf77faa2cfb54466d71a3aef7bbe839': { symbol: 'USDC.e', decimals: 6  },
  '0x9f3096bac87e7f03dc09b0b416eb0df837304dc4': { symbol: 'USDT.e', decimals: 6  },
  '0xdf240dc08b0fdad1d93b74d5048871232f6bea3d': { symbol: 'WBTC.e', decimals: 8  },
  '0x0987d3720d38847ac6dbb9d025b9de892a3ca35c': { symbol: 'JUSD',   decimals: 18 },
}

// ERC20 Transfer event
const TRANSFER_ABI = [{
  name: 'Transfer',
  type: 'event',
  inputs: [
    { name: 'from',  type: 'address', indexed: true  },
    { name: 'to',    type: 'address', indexed: true  },
    { name: 'value', type: 'uint256', indexed: false },
  ],
}]

const CHUNK_SIZE = 1000

function shortAddr(addr) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`
}

function formatAmount(value, decimals, symbol) {
  const n = Number(formatUnits(value, decimals))
  if (n < 0.0001)  return `${n.toFixed(8)} ${symbol}`
  if (n < 1)       return `${n.toFixed(6)} ${symbol}`
  if (n < 1000)    return `${n.toFixed(4)} ${symbol}`
  return `${n.toLocaleString('en-US', { maximumFractionDigits: 2 })} ${symbol}`
}

export async function txHistory(args) {
  if (!args[0]) {
    console.log(`
Usage:
  txns <address> [hours]    Show recent swap activity for a wallet

Examples:
  node index.js txns 0xYourAddress
  node index.js txns 0xYourAddress 24
  node index.js txns 0xYourAddress 168
    `)
    return
  }

  const address  = args[0].toLowerCase()
  const hours    = parseInt(args[1] || '24', 10)
  const lookback = BigInt(Math.floor((hours * 3600) / 2)) // Citrea ~2s blocks

  console.log(`\n🔍 Fetching transactions for ${shortAddr(address)} (last ${hours}h)...`)

  const latest    = await client.getBlockNumber()
  const fromBlock = latest - lookback > 0n ? latest - lookback : 0n

  // Fetch Transfer events involving this address across all known tokens
  const tokenAddresses = Object.keys(TOKEN_MAP)
  const allTransfers   = []

  for (let start = fromBlock; start <= latest; start += BigInt(CHUNK_SIZE)) {
    const end = start + BigInt(CHUNK_SIZE) - 1n < latest ? start + BigInt(CHUNK_SIZE) - 1n : latest

    const logs = await Promise.all(
      tokenAddresses.map(tokenAddr =>
        client.getLogs({
          address:   tokenAddr,
          event:     TRANSFER_ABI[0],
          fromBlock: start,
          toBlock:   end,
        }).catch(() => [])
      )
    )

    for (const tokenLogs of logs) {
      for (const log of tokenLogs) {
        const from = log.args.from?.toLowerCase()
        const to   = log.args.to?.toLowerCase()
        if (from === address || to === address) {
          allTransfers.push(log)
        }
      }
    }
  }

  if (allTransfers.length === 0) {
    console.log(`\n✅ No token transfers found for this address in the last ${hours}h.\n`)
    return
  }

  // Group by transaction hash
  const byTx = new Map()
  for (const log of allTransfers) {
    const hash = log.transactionHash
    if (!byTx.has(hash)) byTx.set(hash, [])
    byTx.get(hash).push(log)
  }

  console.log(`\n📋 Found ${byTx.size} transaction(s) in the last ${hours}h:\n`)
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━`)

  // Fetch block timestamps for ordering
  const blockNums  = [...new Set(allTransfers.map(l => l.blockNumber))]
  const blockTimes = new Map()
  for (const bn of blockNums) {
    try {
      const block = await client.getBlock({ blockNumber: bn })
      blockTimes.set(bn, Number(block.timestamp))
    } catch {}
  }

  // Sort by block descending (newest first)
  const sortedTxs = [...byTx.entries()].sort((a, b) => {
    const blockA = a[1][0].blockNumber
    const blockB = b[1][0].blockNumber
    return blockA > blockB ? -1 : 1
  })

  for (const [hash, logs] of sortedTxs) {
    const blockNum = logs[0].blockNumber
    const ts       = blockTimes.get(blockNum)
    const timeStr  = ts ? new Date(ts * 1000).toLocaleString() : 'unknown time'
    const router   = ROUTERS[logs[0].address] || null

    console.log(`\n🔗 ${hash}`)
    console.log(`   Block:  ${blockNum}  |  ${timeStr}`)
    if (router) console.log(`   DEX:    ${router}`)

    for (const log of logs) {
      const token  = TOKEN_MAP[log.address.toLowerCase()]
      if (!token) continue
      const from   = log.args.from?.toLowerCase()
      const to     = log.args.to?.toLowerCase()
      const dir    = from === address ? '📤 Sent    ' : '📥 Received'
      const amount = formatAmount(log.args.value, token.decimals, token.symbol)
      const counterparty = from === address ? shortAddr(to) : shortAddr(from)
      console.log(`   ${dir}  ${amount.padEnd(28)}  ${from === address ? 'to' : 'from'} ${counterparty}`)
    }

    console.log(`   Explorer: https://explorer.mainnet.citrea.xyz/tx/${hash}`)
  }

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━\n`)
}
