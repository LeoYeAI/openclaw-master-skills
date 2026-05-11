#!/usr/bin/env node
// watch-bets.js — wait for a bet to resolve and notify the user
//
// Waits until startsAt + 2h, then queries the bets subgraph once.
// If still unresolved, retries every 2h until resolved (max 24h total).
// Sends a notification via sendPrompt (OpenClaw) when resolved.
//
// Usage (launched automatically by place-bet.js):
//   node watch-bets.js --bettor <address> --starts-at <unixTimestamp> \
//                      --match "<Team A vs Team B>" --selection "<label>" \
//                      --stake <USDT> --odds <odds>
//
// Optional:
//   --delay-hours <N>   Check N hours after startsAt (default: 2)
//   --max-hours <N>     Give up after N hours total (default: 24)

const https = require('https')

// ─── Args ────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2)
const arg  = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : null }

const bettor       = arg('--bettor')
const startsAtStr  = arg('--starts-at')
const matchTitle   = arg('--match')     || 'Unknown match'
const selection    = arg('--selection') || 'Unknown selection'
const stakeStr     = arg('--stake')     || '0'
const oddsStr      = arg('--odds')      || '0'
const delayHours   = parseFloat(arg('--delay-hours') || '2')
const maxHours     = parseFloat(arg('--max-hours')   || '24')

if (!bettor || !startsAtStr) {
  console.error('Usage: node watch-bets.js --bettor <address> --starts-at <unixTimestamp> [options]')
  process.exit(1)
}

const startsAt   = parseInt(startsAtStr)
const stake      = parseFloat(stakeStr)
const odds       = parseFloat(oddsStr)
const potential  = (stake * odds).toFixed(2)
const delayMs    = delayHours * 60 * 60 * 1000
const maxMs      = maxHours   * 60 * 60 * 1000

const BETS_SUBGRAPH = 'thegraph.onchainfeed.org'
const BETS_PATH     = '/subgraphs/name/azuro-protocol/azuro-api-polygon-v3'

// ─── Helpers ─────────────────────────────────────────────────────────────────
function postJson(host, path, body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(body))
    const req  = https.request(
      { hostname: host, path, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': data.length } },
      res => { let raw = ''; res.on('data', c => { raw += c }); res.on('end', () => { try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('JSON parse: ' + raw.slice(0, 200))) } }) }
    )
    req.on('error', reject)
    req.write(data)
    req.end()
  })
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

function formatMs(ms) {
  const m = Math.round(ms / 60000)
  if (m < 60) return `${m} min`
  const h = (ms / 3600000).toFixed(1)
  return `${h}h`
}

// ─── Notify via OpenClaw sendPrompt ──────────────────────────────────────────
// sendPrompt is injected by OpenClaw into the global scope when running inside a skill.
// If not available (standalone run), fall back to console output.
function notify(message) {
  if (typeof sendPrompt === 'function') {
    sendPrompt(message)
  } else {
    console.log('\n📣 NOTIFICATION:\n' + message)
  }
}

// ─── Query bets subgraph ─────────────────────────────────────────────────────
async function fetchBet() {
  const res = await postJson(BETS_SUBGRAPH, BETS_PATH, {
    query: `query {
      v3Bets(
        where: { bettor: "${bettor.toLowerCase()}" }
        first: 10
        orderBy: createdBlockTimestamp
        orderDirection: desc
      ) {
        betId status result isRedeemable isRedeemed amount payout createdBlockTimestamp
      }
    }`
  })

  if (res.errors) throw new Error('Subgraph error: ' + JSON.stringify(res.errors))

  const bets = res.data?.v3Bets || []

  // Find the most recently placed bet that is not yet redeemed
  // (placed after startsAt - 3h to avoid picking up old bets)
  const cutoff = startsAt - 3 * 3600
  const relevant = bets.filter(b => parseInt(b.createdBlockTimestamp) >= cutoff)

  return relevant.length > 0 ? relevant[0] : null
}

// ─── Main ─────────────────────────────────────────────────────────────────────
;(async () => {
  const startedAt  = Date.now()
  const firstCheck = startsAt * 1000 + delayMs
  const waitFirst  = firstCheck - Date.now()

  console.log(`\n👁  watch-bets.js started`)
  console.log(`   Match:     ${matchTitle}`)
  console.log(`   Selection: ${selection} @ ${odds}`)
  console.log(`   Stake:     ${stake} USDT (potential: ${potential} USDT)`)
  console.log(`   Bettor:    ${bettor}`)
  console.log(`   Kickoff:   ${new Date(startsAt * 1000).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`)
  console.log(`   First check: ${new Date(firstCheck).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })} (kickoff + ${delayHours}h)`)
  console.log(`   Max wait:  ${maxHours}h total\n`)

  if (waitFirst > 0) {
    console.log(`⏳ Waiting ${formatMs(waitFirst)} until first check...`)
    await sleep(waitFirst)
  } else {
    console.log(`⏳ Kickoff already passed — checking immediately...`)
  }

  let attempt = 0

  while (true) {
    attempt++
    const elapsed = Date.now() - startedAt

    if (elapsed > maxMs) {
      const msg = `⚠️ Apuesta sin resolver tras ${maxHours}h\n\n🏟 ${matchTitle}\n🎯 ${selection} @ ${odds}\n💰 ${stake} USDT apostados\n\nAzuro puede estar tardando en resolver. Comprueba manualmente en Pinwin.xyz o pide al agente que revise el estado.`
      console.log(`\n⚠️  Max wait (${maxHours}h) reached. Notifying user and exiting.`)
      notify(msg)
      process.exit(0)
    }

    console.log(`\n🔍 Attempt ${attempt} — ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`)

    let bet = null
    try {
      bet = await fetchBet()
    } catch (e) {
      console.error(`   Subgraph error: ${e.message} — will retry in ${delayHours}h`)
      await sleep(delayMs)
      continue
    }

    if (!bet) {
      console.log(`   No matching bet found yet — will retry in ${delayHours}h`)
      await sleep(delayMs)
      continue
    }

    console.log(`   Bet found — status: ${bet.status}, result: ${bet.result || '—'}, isRedeemable: ${bet.isRedeemable}`)

    if (bet.status === 'Accepted') {
      console.log(`   Still pending — will retry in ${delayHours}h`)
      await sleep(delayMs)
      continue
    }

    // ── Resolved or Canceled ──────────────────────────────────────────────
    if (bet.status === 'Resolved' && bet.result === 'Won') {
      const payout = parseFloat(bet.payout || potential).toFixed(2)
      const profit = (parseFloat(payout) - stake).toFixed(2)
      const msg = [
        `🎉 ¡APUESTA GANADA! 🎉`,
        ``,
        `🏟 ${matchTitle}`,
        `🎯 Selección: ${selection} @ ${odds}`,
        `💰 Stake: ${stake} USDT`,
        `✅ Payout: ${payout} USDT (+${profit} USDT)`,
        ``,
        `¿Quieres reclamar tus ganancias ahora? Di "sí, reclama" y lo gestiono.`,
      ].join('\n')
      console.log('\n🎉 WON! Notifying user.')
      notify(msg)

    } else if (bet.status === 'Resolved' && bet.result === 'Lost') {
      const msg = [
        `😔 Apuesta perdida`,
        ``,
        `🏟 ${matchTitle}`,
        `🎯 Selección: ${selection} @ ${odds}`,
        `💰 Stake: ${stake} USDT`,
        ``,
        `No hay suerte esta vez. ¿Quieres ver los partidos de esta noche?`,
      ].join('\n')
      console.log('\n😔 Lost. Notifying user.')
      notify(msg)

    } else if (bet.status === 'Canceled') {
      const msg = [
        `ℹ️ Apuesta cancelada (stake reembolsable)`,
        ``,
        `🏟 ${matchTitle}`,
        `🎯 Selección: ${selection} @ ${odds}`,
        `💰 Stake: ${stake} USDT — reembolsable`,
        ``,
        `El evento fue cancelado por Azuro. ¿Quieres reclamar el reembolso?`,
      ].join('\n')
      console.log('\n ℹ️ Canceled. Notifying user.')
      notify(msg)
    }

    // Done
    process.exit(0)
  }

})().catch(e => {
  console.error('\n❌ Fatal error:', e.message)
  process.exit(1)
})
