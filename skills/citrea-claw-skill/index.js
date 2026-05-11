import { walletBalance }                          from './src/commands/balance.js'
import { getRecentPools, getLatestPool, monitorPools } from './src/commands/pools.js'
import { poolLiquidity }                          from './src/commands/liquidity.js'
import { checkArb, scanAllArb, monitorArb }       from './src/commands/arb.js'
import { priceCheck, poolPrice }                  from './src/commands/prices-cli.js'
import { txHistory }                              from './src/commands/txns.js'

const [,, command, ...args] = process.argv

if (!command) {
  console.log(`
🦞 citrea-claw-skill — Citrea L2 DeFi CLI

Usage:
  node index.js <command> [args]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WALLET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  balance <address>                     cBTC + token balances

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  price <token>                         USD price from RedStone oracle
  pool:price <tokenA> <tokenB>          Implied price from each DEX side by side

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  POOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  pools:recent [hours]                  New pools in last N hours (default 24)
  pools:latest                          Most recent pool per DEX
  pools:monitor                         Live new pool watcher

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LIQUIDITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  pool:liquidity <poolAddr>             TVL by pool address
  pool:liquidity <tokenA> <tokenB>      TVL by pair
  pool:liquidity <token>                All pools for a token

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ARBITRAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  arb:check <tokenA> <tokenB>           Check a specific pair
  arb:scan                              Scan all pairs once
  arb:monitor                           Live monitor with Telegram alerts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TRANSACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  txns <address> [hours]                Recent swap activity (default 24h)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tokens:  wcBTC  ctUSD  USDC.e  USDT.e  WBTC.e  JUSD
DEXes:   JuiceSwap  Satsuma
  `)
  process.exit(0)
}

switch (command) {
  case 'balance':        await walletBalance(args);              break
  case 'price':          await priceCheck(args);                 break
  case 'pool:price':     await poolPrice(args);                  break
  case 'pools:recent':   await getRecentPools(args);             break
  case 'pools:latest':   await getLatestPool();                  break
  case 'pools:monitor':  await monitorPools();                   break
  case 'pool:liquidity': await poolLiquidity(args);              break
  case 'arb:check':      await checkArb(args);                   break
  case 'arb:scan':       await scanAllArb();                     break
  case 'arb:monitor':    await monitorArb();                     break
  case 'txns':           await txHistory(args);                  break
  default:
    console.log(`❌ Unknown command "${command}". Run without arguments to see usage.`)
    process.exit(1)
}
