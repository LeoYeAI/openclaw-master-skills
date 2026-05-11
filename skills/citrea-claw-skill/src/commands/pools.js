import 'dotenv/config'
import { createPublicClient, http, parseAbiItem } from 'viem'
import { sendTelegram } from '../lib/telegram.js'

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

// ─── DEX Config ───────────────────────────────────────────────────────────────
const DEX = {
  JuiceSwap: {
    factory: '0xd809b1285aDd8eeaF1B1566Bf31B2B4C4Bba8e82',
    type: 'univ3',
    url: 'https://juiceswap.com',
  },
  Satsuma: {
    factory: '0x10253594A832f967994b44f33411940533302ACb',
    type: 'algebra',
    url: 'https://satsuma.exchange',
  },
}

// ─── RPC Limit ────────────────────────────────────────────────────────────────
const CHUNK = 1000n

// ─── Events ───────────────────────────────────────────────────────────────────
const UNIV3_POOL_CREATED = parseAbiItem(
  'event PoolCreated(address indexed token0, address indexed token1, uint24 indexed fee, int24 tickSpacing, address pool)'
)

const ALGEBRA_POOL_CREATED = parseAbiItem(
  'event Pool(address indexed token0, address indexed token1, address pool)'
)

const ERC20_ABI = [
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'string' }],
  },
]

// ─── Known Tokens ─────────────────────────────────────────────────────────────
const KNOWN_TOKENS = {
  '0x8d82c4e3c936c7b5724a382a9c5a4e6eb7ab6d5d': 'ctUSD',
  '0x3100000000000000000000000000000000000006': 'wcBTC',
  '0xe045e6c36cf77faa2cfb54466d71a3aef7bbe839': 'USDC.e',
  '0x9f3096bac87e7f03dc09b0b416eb0df837304dc4': 'USDT.e',
  '0xdf240dc08b0fdad1d93b74d5048871232f6bea3d': 'WBTC.e',
  '0x0987d3720d38847ac6dbb9d025b9de892a3ca35c': 'JUSD',
  '0x1b70ae756b1089cc5948e4f8a2ad498df30e897d': 'svJUSD',
  '0x2a36f2b204b46fd82653cd06d00c7ff757c99ae4': 'JUICE',
}

const EXPLORER_TX   = 'https://explorer.mainnet.citrea.xyz/tx'
const EXPLORER_ADDR = 'https://explorer.mainnet.citrea.xyz/address'

const client = createPublicClient({
  chain: citrea,
  transport: http()
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function getTokenSymbol(address) {
  const lower = address.toLowerCase()
  if (KNOWN_TOKENS[lower]) return KNOWN_TOKENS[lower]
  try {
    return await client.readContract({
      address,
      abi: ERC20_ABI,
      functionName: 'symbol',
    })
  } catch {
    return address.slice(0, 8) + '...'
  }
}

function formatFee(fee) {
  return (fee / 10000).toFixed(2) + '%'
}

// ─── Pool Formatters ──────────────────────────────────────────────────────────

function formatUniv3Pool(dexName, log, t0, t1) {
  return [
    `🆕 NEW POOL — ${dexName}`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
    `   Pair:   ${t0} / ${t1}`,
    `   Fee:    ${formatFee(log.args.fee)}`,
    `   Pool:   ${log.args.pool}`,
    `   Block:  #${log.blockNumber}`,
    `   Tx:     ${EXPLORER_TX}/${log.transactionHash}`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
  ].join('\n')
}

function formatAlgebraPool(dexName, log, t0, t1) {
  return [
    `🆕 NEW POOL — ${dexName}`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
    `   Pair:   ${t0} / ${t1}`,
    `   Fee:    Dynamic (Algebra)`,
    `   Pool:   ${log.args.pool}`,
    `   Block:  #${log.blockNumber}`,
    `   Tx:     ${EXPLORER_TX}/${log.transactionHash}`,
    `━━━━━━━━━━━━━━━━━━━━━━━━`,
  ].join('\n')
}

async function fetchPoolLogs(dexName, dex, fromBlock, toBlock) {
  const event = dex.type === 'algebra' ? ALGEBRA_POOL_CREATED : UNIV3_POOL_CREATED
  const logs  = await client.getLogs({
    address: dex.factory,
    event,
    fromBlock,
    toBlock,
  }).catch(() => [])
  return logs
}

// ─── Recent Pools ─────────────────────────────────────────────────────────────

async function getRecentPools(args = []) {
  const limitHours = parseInt(args[0] || '24', 10)

  try {
    const latestBlock = await client.getBlockNumber()
    const blocksBack  = BigInt(Math.floor(limitHours * 1800))
    const startBlock  = latestBlock - blocksBack

    const lines = [
      `🏊 New Pools — Last ${limitHours}h`,
      `━━━━━━━━━━━━━━━━━━━━━━━━`,
    ]

    let totalFound = 0

    for (const [dexName, dex] of Object.entries(DEX)) {
      const allLogs = []

      let fromBlock = startBlock
      while (fromBlock <= latestBlock) {
        const toBlock = fromBlock + CHUNK - 1n < latestBlock
          ? fromBlock + CHUNK - 1n
          : latestBlock

        const logs = await fetchPoolLogs(dexName, dex, fromBlock, toBlock)
        allLogs.push(...logs)
        fromBlock = toBlock + 1n
      }

      if (allLogs.length === 0) {
        lines.push(``)
        lines.push(`✅ ${dexName}: no new pools in last ${limitHours}h`)
        continue
      }

      lines.push(``)
      lines.push(`🔶 ${dexName} — ${allLogs.length} new pool${allLogs.length > 1 ? 's' : ''}`)

      for (const log of allLogs.slice(0, 10)) {
        const [t0, t1] = await Promise.all([
          getTokenSymbol(log.args.token0),
          getTokenSymbol(log.args.token1),
        ])

        lines.push(``)
        lines.push(`   📌 ${t0} / ${t1}`)

        if (dex.type === 'univ3') {
          lines.push(`      Fee:   ${formatFee(log.args.fee)}`)
        } else {
          lines.push(`      Fee:   Dynamic (Algebra)`)
        }

        lines.push(`      Pool:  ${EXPLORER_ADDR}/${log.args.pool}`)
        lines.push(`      Tx:    ${EXPLORER_TX}/${log.transactionHash}`)
        totalFound++
      }
    }

    lines.push(``)
    lines.push(`━━━━━━━━━━━━━━━━━━━━━━━━`)
    lines.push(`Total: ${totalFound} new pool${totalFound !== 1 ? 's' : ''} found`)

    console.log(lines.join('\n'))

  } catch (error) {
    console.error(`❌ Error fetching pools: ${error.message}`)
  }
}

// ─── Latest Pool ──────────────────────────────────────────────────────────────

async function getLatestPool() {
  try {
    const latestBlock = await client.getBlockNumber()

    const lines = [
      `🏊 Most Recent Pool — JuiceSwap & Satsuma`,
      `━━━━━━━━━━━━━━━━━━━━━━━━`,
    ]

    for (const [dexName, dex] of Object.entries(DEX)) {
      lines.push(``)
      lines.push(`🔶 ${dexName}`)

      let found    = false
      let toBlock  = latestBlock

      while (toBlock > 0n && !found) {
        const fromBlock = toBlock >= CHUNK ? toBlock - CHUNK + 1n : 0n
        process.stdout.write(`   Scanning blocks ${fromBlock}-${toBlock}...\r`)

        const logs = await fetchPoolLogs(dexName, dex, fromBlock, toBlock)

        if (logs.length > 0) {
          const log      = logs[logs.length - 1]
          const [t0, t1] = await Promise.all([
            getTokenSymbol(log.args.token0),
            getTokenSymbol(log.args.token1),
          ])

          process.stdout.write(`                                              \r`)

          lines.push(`   📌 ${t0} / ${t1}`)

          if (dex.type === 'univ3') {
            lines.push(`      Fee:   ${formatFee(log.args.fee)}`)
          } else {
            lines.push(`      Fee:   Dynamic (Algebra)`)
          }

          lines.push(`      Pool:  ${EXPLORER_ADDR}/${log.args.pool}`)
          lines.push(`      Tx:    ${EXPLORER_TX}/${log.transactionHash}`)
          lines.push(`      Block: #${log.blockNumber}`)
          found = true
        }

        toBlock = fromBlock - 1n
      }

      if (!found) {
        process.stdout.write(`                                              \r`)
        lines.push(`   No pools found on this DEX yet.`)
      }
    }

    lines.push(``)
    lines.push(`━━━━━━━━━━━━━━━━━━━━━━━━`)
    console.log(lines.join('\n'))

  } catch (error) {
    console.error(`❌ Error fetching latest pool: ${error.message}`)
  }
}

// ─── Live Monitor ─────────────────────────────────────────────────────────────

async function monitorPools() {
  console.log(`🔍 Watching for new pools on: ${Object.keys(DEX).join(', ')}`)
  console.log(`   Telegram alerts enabled for all new pools.`)
  console.log(`   Press Ctrl+C to stop.\n`)

  let lastCheckedBlock = await client.getBlockNumber()

  const poll = async () => {
    try {
      const latestBlock = await client.getBlockNumber()
      if (latestBlock <= lastCheckedBlock) return

      const fromBlock = latestBlock - lastCheckedBlock > CHUNK
        ? latestBlock - CHUNK
        : lastCheckedBlock + 1n

      for (const [dexName, dex] of Object.entries(DEX)) {
        const logs = await fetchPoolLogs(dexName, dex, fromBlock, latestBlock)

        for (const log of logs) {
          const [t0, t1] = await Promise.all([
            getTokenSymbol(log.args.token0),
            getTokenSymbol(log.args.token1),
          ])

          const msg = dex.type === 'algebra'
            ? formatAlgebraPool(dexName, log, t0, t1)
            : formatUniv3Pool(dexName, log, t0, t1)

          console.log(msg)
          console.log()

          // Send Telegram alert for every new pool
          await sendTelegram(`<pre>${msg}</pre>`)
        }
      }

      lastCheckedBlock = latestBlock

    } catch (err) {
      console.error(`⚠️  Poll error: ${err.message}`)
    }
  }

  await poll()
  setInterval(poll, 10_000)
}

export { getRecentPools, getLatestPool, monitorPools }
