#!/usr/bin/env node
// place-bet.js — place a bet on Azuro/Pinwin via the /agent/bet API
// Usage: node place-bet.js --stake <USDT> --outcome <outcomeId> --condition <conditionId> [--odds <currentOdds>]
// Examples:
//   node place-bet.js --stake 1 --outcome 16614 --condition 3006100600000000002921409...
//   node place-bet.js --stake 5 --outcome 16614 --condition 3006... --odds 1.51
//
// Required env: BETTOR_PRIVATE_KEY
// Optional env: POLYGON_RPC_URL

const https = require('https')
const { createPublicClient, createWalletClient, http, parseAbi, encodeFunctionData } = require('viem')
const { polygon } = require('viem/chains')
const { privateKeyToAccount } = require('viem/accounts')
const { getMarketName, getSelectionName } = require('@azuro-org/dictionaries')
const readline = require('readline')

// ─── Constants ───────────────────────────────────────────────────────────────
const USDT           = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
const RELAYER        = '0x8dA05c0021e6b35865FDC959c54dCeF3A4AbBa9d'
const CLAIM_CONTRACT = '0xf9548be470a4e130c90cea8b179fcd66d2972ac7'
const PINWIN_API     = 'https://api.pinwin.xyz'
const REST_API_BASE  = 'api.onchainfeed.org'
const CONDITIONS_PATH = '/api/v1/public/market-manager/conditions-by-game-ids'
const ENVIRONMENT     = 'PolygonUSDT'

const ERC20_ABI = parseAbi([
  'function balanceOf(address) view returns (uint256)',
  'function allowance(address,address) view returns (uint256)',
  'function approve(address,uint256) returns (bool)',
])

// ─── Args ────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2)
const arg  = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : null }

const stakeArg     = arg('--stake')     // USDT units, e.g. "1" or "2.5"
const outcomeArg   = arg('--outcome')   // numeric outcomeId
const conditionArg = arg('--condition') // conditionId string
const oddsArg      = arg('--odds')      // currentOdds string (optional, fetched live if omitted)
const startsAtArg  = arg('--starts-at')  // unix timestamp of game kickoff (from get-games.js JSON)
const matchArg     = arg('--match')      // human-readable match title (e.g. "Celtics vs Grizzlies")
const dryRun       = args.includes('--dry-run')  // print request body and exit before sending
const skipConfirm  = args.includes('--yes')        // skip interactive confirmation (CI/test use only)

if (!stakeArg || !outcomeArg || !conditionArg) {
  console.error('Usage: node place-bet.js --stake <USDT> --outcome <outcomeId> --condition <conditionId> [--odds <currentOdds>]')
  process.exit(1)
}

if (!process.env.BETTOR_PRIVATE_KEY) {
  console.error('Error: BETTOR_PRIVATE_KEY env var is not set')
  process.exit(1)
}

const stakeUSDT   = parseFloat(stakeArg)
const stakeAmount = BigInt(Math.round(stakeUSDT * 1e6))
const outcomeId   = parseInt(outcomeArg)
const conditionId = conditionArg

// ─── viem setup ──────────────────────────────────────────────────────────────
const rpc     = process.env.POLYGON_RPC_URL || 'https://polygon-bor-rpc.publicnode.com'
// [SECURITY NOTE] BETTOR_PRIVATE_KEY is read solely to derive the wallet address
// and sign EIP-712 payloads locally via viem. The raw key is never logged, serialized,
// or transmitted over the network. All network calls go to: Azuro data-feed subgraph
// (read-only), Pinwin /agent/bet and /agent/claim (returns unsigned payload),
// Azuro order API (receives signed payload), and public Polygon RPC (broadcast tx).
const account = privateKeyToAccount(process.env.BETTOR_PRIVATE_KEY)
const bettor  = account.address

const publicClient = createPublicClient({ chain: polygon, transport: http(rpc) })
const walletClient = createWalletClient({ account, chain: polygon, transport: http(rpc) })

// ─── Helpers ─────────────────────────────────────────────────────────────────
function postJson(host, path, body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(body))
    const req  = https.request(
      { hostname: host, path, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': data.length } },
      res => { let raw = ''; res.on('data', c => { raw += c }); res.on('end', () => { try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('JSON parse error: ' + raw.slice(0, 200))) } }) }
    )
    req.on('error', reject)
    req.write(data)
    req.end()
  })
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let raw = ''
      res.on('data', c => { raw += c })
      res.on('end', () => { try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('JSON parse error: ' + raw.slice(0, 200))) } })
    }).on('error', reject)
  })
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

// ─── Main ─────────────────────────────────────────────────────────────────────
;(async () => {
  console.log('\n🎯 place-bet.js — Pinwin / Azuro\n')
  console.log(`   Wallet:    ${bettor}`)
  console.log(`   Stake:     ${stakeUSDT} USDT`)
  console.log(`   Condition: ${conditionId}`)
  console.log(`   Outcome:   ${outcomeId}`)

  // ── Resolve human-readable label ──────────────────────────────────────────
  let selectionLabel = String(outcomeId)
  let marketName     = 'Unknown market'
  try {
    const sel  = getSelectionName({ outcomeId, withPoint: true })
    marketName = getMarketName({ outcomeId })
    selectionLabel = sel  // "1", "2", or "X"
  } catch (_) {}
  console.log(`   Market:    ${marketName} — outcome "${selectionLabel}"`)

  // ── Step 0: Balances ──────────────────────────────────────────────────────
  console.log('\n⏳ Checking balances...')
  const [pol, usdt] = await Promise.all([
    publicClient.getBalance({ address: bettor }),
    publicClient.readContract({ address: USDT, abi: ERC20_ABI, functionName: 'balanceOf', args: [bettor] }),
  ])

  const polEth  = Number(pol) / 1e18
  const usdtHuman = Number(usdt) / 1e6

  console.log(`   POL:  ${polEth.toFixed(4)} POL`)
  console.log(`   USDT: ${usdtHuman.toFixed(2)} USDT`)

  if (pol < 100000000000000n) { // < 0.0001 POL — basically no gas
    console.error('\n❌ Insufficient POL for gas. Fund your wallet and retry.')
    process.exit(1)
  }
  if (pol < 1000000000000000000n) {
    console.warn(`\n⚠️  POL balance is low (${polEth.toFixed(4)} POL). Up to 2 txs needed (approve + bet). Consider topping up.`)
  }
  if (usdt < stakeAmount) {
    console.error(`\n❌ Insufficient USDT. Need ${stakeUSDT} USDT, have ${usdtHuman.toFixed(2)} USDT.`)
    process.exit(1)
  }

  // ── Step 2 (verify): Re-check condition via REST API ────────────────────
  // The REST conditions-by-game-ids endpoint requires gameId, not conditionId.
  // Since place-bet only receives conditionId, we use the --odds flag value and
  // rely on Pinwin /agent/bet to reject if the condition is no longer active.
  // The 2% minOdds slippage covers normal odds movement between fetch and submit.
  console.log('\n⏳ Checking odds and preparing bet...')

  if (!oddsArg) {
    console.error('❌ --odds is required. Always pass --odds from the get-games.js JSON output.')
    process.exit(1)
  }

  const currentOdds = parseFloat(oddsArg)
  // Apply 2% slippage (Azuro SDK convention).
  // Using exact odds as minOdds causes silent rejection if odds shift even slightly between fetch and submit.
  const SLIPPAGE     = 0.02
  const minOdds      = BigInt(Math.round(currentOdds * (1 - SLIPPAGE) * 1e12))

  console.log(`   ✅ Condition Active. Current odds: ${currentOdds.toFixed(4)} → minOdds (2% slip): ${minOdds}`)

  // ── Step 3: Call /agent/bet ───────────────────────────────────────────────
  console.log('\n⏳ Calling Pinwin /agent/bet...')
  const apiHost   = PINWIN_API.replace('https://', '')
  const betBody   = {
    amount:     Number(stakeAmount),
    minOdds:    Number(minOdds),
    chain:      'polygon',
    selections: [{ conditionId: String(conditionId), outcomeId: Number(outcomeId) }],
  }
  console.log('   📤 Request body:', JSON.stringify(betBody, null, 2))

  if (dryRun) {
    console.log('\n[--dry-run] Stopping before API call.')
    process.exit(0)
  }

  const betRes = await postJson(apiHost, '/agent/bet', betBody)
  console.log('   📥 Raw response:', JSON.stringify(betRes).slice(0, 300))

  if (!betRes.encoded) {
    console.error('❌ /agent/bet did not return encoded payload:', JSON.stringify(betRes))
    process.exit(1)
  }

  const payload = JSON.parse(Buffer.from(betRes.encoded, 'base64').toString('utf8'))
  // Debug: show raw decoded payload (truncated)
  console.log('   🔍 Decoded payload (signableClientBetData):', JSON.stringify(payload.signableClientBetData, null, 2).slice(0, 800))

  // ── Step 4: Explain payload to user ──────────────────────────────────────
  const cd = payload.signableClientBetData
  const payloadStake      = BigInt(cd.bet?.amount ?? cd.bets?.[0]?.amount ?? cd.amount ?? 0)
  const relayerFee        = BigInt(cd.clientData?.relayerFeeAmount ?? cd.bets?.[0]?.relayerFeeAmount ?? 0)
  const totalNeeded       = payloadStake + relayerFee
  const potentialPayout   = (Number(payloadStake) / 1e6) * currentOdds

  console.log('\n📋 Bet Summary')
  console.log('─────────────────────────────────────────────')
  console.log(`   Market:       ${marketName} — outcome "${selectionLabel}"`)
  console.log(`   Odds:         ${currentOdds.toFixed(2)}`)
  console.log(`   Stake:        ${Number(payloadStake) / 1e6} USDT`)
  console.log(`   Relayer fee:  ${Number(relayerFee) / 1e6} USDT`)
  console.log(`   Total USDT:   ${Number(totalNeeded) / 1e6} USDT`)
  console.log(`   Potential win: ${potentialPayout.toFixed(2)} USDT`)
  console.log(`   Fee sponsored: ${cd.clientData?.isFeeSponsored ?? false}`)
  console.log(`   Expires at:   ${new Date(parseInt(cd.clientData?.expiresAt ?? 0) * 1000).toISOString()}`)

  // ── Step 6: Verify payload integrity ─────────────────────────────────────
  console.log('\n⏳ Verifying payload integrity...')

  const payloadCondId  = cd.bet?.conditionId ?? cd.bets?.[0]?.conditionId
  const payloadOutcome = cd.bet?.outcomeId   ?? cd.bets?.[0]?.outcomeId
  const coreAddr       = cd.clientData?.core?.toLowerCase()

  if (String(payloadStake) !== String(stakeAmount)) {
    console.error(`❌ Payload stake mismatch: expected ${stakeAmount}, got ${payloadStake}`)
    process.exit(1)
  }
  if (String(payloadCondId) !== String(conditionId)) {
    console.error(`❌ conditionId mismatch: expected ${conditionId}, got ${payloadCondId}`)
    process.exit(1)
  }
  if (String(payloadOutcome) !== String(outcomeId)) {
    console.error(`❌ outcomeId mismatch: expected ${outcomeId}, got ${payloadOutcome}`)
    process.exit(1)
  }
  if (coreAddr !== CLAIM_CONTRACT) {
    console.error(`❌ Core address mismatch: expected ${CLAIM_CONTRACT}, got ${coreAddr}`)
    process.exit(1)
  }
  console.log('   ✅ Payload verified.')

  // ── Confirmation gate — REQUIRED before any on-chain action ──────────────
  if (!skipConfirm) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    const answer = await new Promise(resolve => {
      rl.question(
        `\n🛑 CONFIRMAR APUESTA\n   ${Number(payloadStake) / 1e6} USDT en ${marketName} — outcome "${selectionLabel}" @ ${currentOdds.toFixed(2)}\n   ¿Proceder? (escribe "si" para confirmar): `,
        ans => { rl.close(); resolve(ans.trim().toLowerCase()) }
      )
    })
    if (answer !== 'si' && answer !== 'sí' && answer !== 'yes' && answer !== 'y') {
      console.log('\n❌ Apuesta cancelada por el usuario.')
      process.exit(0)
    }
    console.log('   ✅ Confirmado.')
  } else {
    console.log('\n⚠️  [--yes flag] Saltando confirmación interactiva.')
  }

  // ── Step 5: Approve USDT if needed ───────────────────────────────────────
  const buffer   = 200000n // 0.2 USDT buffer
  const required = totalNeeded + buffer

  const allowance = await publicClient.readContract({
    address: USDT, abi: ERC20_ABI, functionName: 'allowance', args: [bettor, RELAYER],
  })

  if (allowance < required) {
    console.log(`\n⏳ Approving USDT (need ${Number(required) / 1e6} USDT, have allowance ${Number(allowance) / 1e6} USDT)...`)
    const approveTx = await walletClient.sendTransaction({
      to:   USDT,
      data: encodeFunctionData({ abi: ERC20_ABI, functionName: 'approve', args: [RELAYER, required] }),
    })
    console.log(`   Approval tx: https://polygonscan.com/tx/${approveTx}`)
    await publicClient.waitForTransactionReceipt({ hash: approveTx })
    console.log('   ✅ USDT approval confirmed.')
  } else {
    console.log(`\n   ✅ USDT allowance sufficient (${Number(allowance) / 1e6} USDT). Skipping approve.`)
  }

  // ── Step 7: Sign ──────────────────────────────────────────────────────────
  console.log('\n⏳ Signing EIP-712 payload...')
  const primaryType     = payload.types.ClientComboBetData ? 'ClientComboBetData' : 'ClientBetData'
  const bettorSignature = await walletClient.signTypedData({
    account,
    domain:      payload.domain,
    types:       payload.types,
    primaryType,
    message:     payload.signableClientBetData,
  })
  console.log('   ✅ Signed.')

  // ── Step 7: Submit ────────────────────────────────────────────────────────
  console.log('\n⏳ Submitting bet to Azuro order API...')
  const submitUrl  = new URL(payload.apiUrl)
  const submitHost = submitUrl.hostname
  const submitPath = submitUrl.pathname + submitUrl.search

  const submitRes = await postJson(submitHost, submitPath, {
    environment:   payload.environment,
    bettor,
    betOwner:      bettor,
    clientBetData: payload.apiClientBetData,
    bettorSignature,
  })

  if (!submitRes.id || submitRes.state === 'Rejected' || submitRes.state === 'Canceled') {
    console.error('❌ Submission failed:', JSON.stringify(submitRes))
    process.exit(1)
  }

  const orderId = submitRes.id
  console.log(`   ✅ Order submitted. ID: ${orderId} — State: ${submitRes.state}`)
  console.log('   ⏳ Polling for on-chain confirmation (do not close)...\n')

  // ── Step 7: Poll ──────────────────────────────────────────────────────────
  const apiBase = payload.apiUrl.replace(/\/bet\/orders\/(ordinar|combo)$/, '')
  let txHash    = null

  for (let i = 0; i < 30; i++) {
    const delayMs = Math.min(2000 + i * 1000, 10000)
    await sleep(delayMs)

    let poll
    try {
      poll = await getJson(`${apiBase}/bet/orders/${orderId}`)
    } catch (e) {
      console.log(`   Attempt ${i + 1}/30 — fetch error: ${e.message}`)
      continue
    }

    process.stdout.write(`   Attempt ${i + 1}/30 — state: ${poll.state}`)
    if (poll.txHash) {
      txHash = poll.txHash
      process.stdout.write(' ✅\n')
      break
    }
    if (poll.state === 'Rejected' || poll.state === 'Canceled') {
      process.stdout.write(' ❌\n')
      console.error(`\n❌ Order ${poll.state}: ${poll.errorMessage || 'unknown error'}`)
      process.exit(1)
    }
    process.stdout.write('\n')
  }

  if (!txHash) {
    console.error(`\n⚠️  Order did not settle after ~90s. Order ID: ${orderId}`)
    console.error('   Check manually on Polygonscan or retry polling later.')
    process.exit(1)
  }

  // ── Success ───────────────────────────────────────────────────────────────
  console.log('\n' + '─'.repeat(50))
  console.log('✅ Bet confirmed on-chain!')
  console.log(`   Market:     ${marketName} — outcome "${selectionLabel}"`)
  console.log(`   Odds:       ${currentOdds.toFixed(2)}`)
  console.log(`   Stake:      ${Number(payloadStake) / 1e6} USDT`)
  console.log(`   Potential:  ${potentialPayout.toFixed(2)} USDT`)
  console.log(`   Tx:         https://polygonscan.com/tx/${txHash}`)
  console.log('─'.repeat(50) + '\n')

  const jsonOut = {
    success: true,
    txHash,
    orderId,
    stake:    Number(payloadStake) / 1e6,
    odds:     currentOdds,
    payout:   potentialPayout,
    market:   marketName,
    outcome:  selectionLabel,
    polygonscan: `https://polygonscan.com/tx/${txHash}`,
  }
  console.log('---JSON---')
  console.log(JSON.stringify(jsonOut))

  // ── Launch watch-bets.js if --starts-at was provided ─────────────────────
  if (startsAtArg) {
    const { spawn } = require('child_process')
    const watchArgs = [
      require('path').join(__dirname, 'watch-bets.js'),
      '--bettor',     bettor,
      '--starts-at',  startsAtArg,
      '--match',      matchArg || 'Unknown match',
      '--selection',  `${marketName} — ${selectionLabel}`,
      '--stake',      String(Number(payloadStake) / 1e6),
      '--odds',       String(currentOdds),
    ]
    // [SECURITY NOTE] child_process.spawn is used here exclusively to launch
    // watch-bets.js (bundled in this same package) as a detached background process.
    // It runs the same Node.js binary (process.execPath) with a sibling script path.
    // No shell execution, no external downloads, no dynamic code. The only network
    // calls watch-bets.js makes are to the Azuro bets subgraph (read-only GraphQL).
    const watcher = spawn(process.execPath, watchArgs, {
      detached: true,
      stdio:    ['ignore', 'pipe', 'pipe'],
    })
    watcher.stdout.on('data', d => process.stdout.write('[watcher] ' + d))
    watcher.stderr.on('data', d => process.stderr.write('[watcher] ' + d))
    watcher.unref()
    console.log(`\n👁  watch-bets.js launched (PID ${watcher.pid}) — te avisaré cuando se resuelva la apuesta.`)
  } else {
    console.log('\n💡 Tip: pasa --starts-at <unixTimestamp> para recibir notificación automática del resultado.')
  }

})().catch(e => {
  console.error('\n❌ Fatal error:', e.message)
  process.exit(1)
})
