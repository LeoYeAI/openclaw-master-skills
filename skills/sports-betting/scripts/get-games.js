#!/usr/bin/env node
// get-games.js — fetch games from Azuro REST API and display main market odds
// Usage:
//   node get-games.js [sport-slug] [league-slug] [count]   # browse by sport/league
//   node get-games.js --search "<query>" [count]           # search by team/match name
// Examples:
//   node get-games.js                              # top 20 games all sports
//   node get-games.js basketball nba 10            # NBA only
//   node get-games.js football premier-league 10   # Premier League
//   node get-games.js hockey 5                     # NHL/ice-hockey
//   node get-games.js --search "Real Madrid" 5     # search by team name
//   node get-games.js --search "Celtics" 3         # search by team name
//   node get-games.js --search "Lakers vs" 5       # search by match title
//
// No longer requires @azuro-org/dictionaries — REST API returns human-readable titles directly.

const https = require('https')

const API_HOST        = 'api.onchainfeed.org'
const SPORTS_PATH     = '/api/v1/public/market-manager/sports'
const CONDITIONS_PATH = '/api/v1/public/market-manager/conditions-by-game-ids'
const SEARCH_PATH     = '/api/v1/public/market-manager/search'
const ENVIRONMENT     = 'PolygonUSDT'

const MAIN_MARKET_KEYWORDS = ['match winner', 'full time result', 'winner', 'fight winner', 'moneyline']

const SPORT_SLUG_ALIASES = {
  'hockey': 'ice-hockey', 'nhl': 'ice-hockey', 'ice-hockey': 'ice-hockey', 'icehockey': 'ice-hockey',
  'soccer': 'football', 'basketball': 'basketball', 'nba': 'basketball',
  'mma': 'mma', 'baseball': 'baseball', 'mlb': 'baseball',
  'american-football': 'american-football', 'nfl': 'american-football',
}

const args         = process.argv.slice(2)
const searchIdx    = args.indexOf('--search')
const searchQuery  = searchIdx !== -1 ? args[searchIdx + 1] : null

// If --search mode, remaining args after the query value are count
const countArgSearch = searchIdx !== -1 ? args[searchIdx + 2] : null

// If not --search mode, parse positional args
const positional    = searchQuery ? [] : args
const [sportSlugRaw, leagueSlugRaw, countArg] = positional
const sportSlug     = sportSlugRaw  ? (SPORT_SLUG_ALIASES[sportSlugRaw.toLowerCase()]  || sportSlugRaw.toLowerCase())  : null
const isLeagueCount = leagueSlugRaw && !isNaN(leagueSlugRaw)
const leagueSlug    = !isLeagueCount && leagueSlugRaw ? leagueSlugRaw.toLowerCase() : null
const count         = parseInt(countArgSearch) || parseInt(countArg) || (isLeagueCount ? parseInt(leagueSlugRaw) : 20)

function getJson(path) {
  return new Promise((resolve, reject) => {
    https.get({ hostname: API_HOST, path, headers: { Accept: 'application/json' } }, res => {
      let raw = ''; res.on('data', c => { raw += c }); res.on('end', () => { try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('Parse: ' + raw.slice(0, 200))) } })
    }).on('error', reject)
  })
}

function postJson(path, body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(body))
    const req  = https.request({ hostname: API_HOST, path, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': data.length } }, res => {
      let raw = ''; res.on('data', c => { raw += c }); res.on('end', () => { try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('Parse: ' + raw.slice(0, 200))) } })
    })
    req.on('error', reject); req.write(data); req.end()
  })
}

function resolveTitle(t) {
  if (!t) return ''
  if (typeof t === 'string') return t
  return t.en || t.EN || Object.values(t)[0] || ''
}

function isMainMarket(title) {
  const t = resolveTitle(title).toLowerCase()
  return MAIN_MARKET_KEYWORDS.some(k => t.includes(k))
}

function extractGames(data, stateName) {
  const games = []
  for (const sport of (data.sports || [])) {
    for (const country of (sport.countries || [])) {
      for (const league of (country.leagues || [])) {
        for (const game of (league.games || [])) {
          games.push({ ...game, state: stateName, sportName: sport.name, leagueName: league.name })
        }
      }
    }
  }
  return games
}

;(async () => {
  let allGames = []

  if (searchQuery) {
    // ── Search mode ────────────────────────────────────────────────────────
    console.log(`🔍 Searching for: "${searchQuery}"...`)
    try {
      const params = new URLSearchParams({ environment: ENVIRONMENT, request: searchQuery, page: '1', perPage: String(Math.max(count * 2, 20)) })
      const res = await getJson(`${SEARCH_PATH}?${params.toString()}`)
      allGames = (res.games || []).map(g => ({
        ...g,
        state:     g.state || 'Prematch',
        sportName: g.sport?.name || 'Unknown',
        leagueName: g.league?.name || 'Unknown',
      }))
      if (res.total > 0) console.log(`   Found ${res.total} result(s) — showing top ${Math.min(count, allGames.length)}`)
    } catch (e) { console.error('Search failed:', e.message); process.exit(1) }
  } else {
    // ── Browse mode ────────────────────────────────────────────────────────
    const baseParams = { environment: ENVIRONMENT, conditionState: 'Active', orderBy: 'turnover', orderDirection: 'desc', numberOfGames: String(count) }
    if (sportSlug)  baseParams.sportSlug  = sportSlug
    if (leagueSlug) baseParams.leagueSlug = leagueSlug

    const pPrematch = new URLSearchParams({ ...baseParams, gameState: 'Prematch' })
    const pLive     = new URLSearchParams({ ...baseParams, gameState: 'Live' })

    try {
      const [live, prematch] = await Promise.all([
        getJson(`${SPORTS_PATH}?${pLive.toString()}`),
        getJson(`${SPORTS_PATH}?${pPrematch.toString()}`),
      ])
      allGames = [...extractGames(live, 'Live'), ...extractGames(prematch, 'Prematch')]
    } catch (e) { console.error('Failed to fetch games:', e.message); process.exit(1) }
  }

  if (!allGames.length) { console.log('No games found for the given filters.'); process.exit(0) }

  // Deduplicate, keep up to count
  const seen = new Set(), games = []
  for (const g of allGames) {
    const id = String(g.gameId)
    if (!seen.has(id)) { seen.add(id); games.push(g) }
    if (games.length >= count) break
  }

  // Fetch conditions (odds)
  let conditionsMap = {}
  try {
    const res = await postJson(CONDITIONS_PATH, { gameIds: games.map(g => g.gameId), environment: ENVIRONMENT })
    for (const cond of (res.conditions || [])) {
      const gid = String(cond.game?.gameId)
      if (!conditionsMap[gid]) conditionsMap[gid] = []
      conditionsMap[gid].push(cond)
    }
  } catch (e) { console.error('Failed to fetch conditions:', e.message); process.exit(1) }

  // Build results
  const results = []
  for (const game of games) {
    const gid        = String(game.gameId)
    const conditions = (conditionsMap[gid] || []).filter(c => c.state === 'Active')
    if (!conditions.length) continue

    const mainCond   = conditions.find(c => isMainMarket(c.title)) || conditions[0]
    const marketName = resolveTitle(mainCond.title) || 'Main Market'
    const parts      = game.participants || []

    const selections = (mainCond.outcomes || []).map((o, idx) => {
      const t = resolveTitle(o.title)
      let label = t
      if      (t === '1'   && parts[0]) label = parts[0].name
      else if (t === '2'   && parts[1]) label = parts[1].name
      else if (t.toLowerCase() === 'x' || t.toLowerCase() === 'draw') label = 'Draw'
      else if (!t          && parts[idx]) label = parts[idx].name
      return { label, odds: parseFloat(o.odds).toFixed(2), outcomeId: parseInt(o.outcomeId), conditionId: mainCond.conditionId }
    })

    if (!selections.length) continue

    const startsAt = parseInt(game.startsAt)
    const kickoff  = new Date(startsAt * 1000).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' })

    results.push({ gameId: gid, title: game.title, state: game.state, kickoff, startsAt, sport: game.sportName, league: game.leagueName, market: marketName, selections })
  }

  if (!results.length) { console.log('No games with active conditions found.'); process.exit(0) }

  let currentSport = ''
  results.forEach((g, i) => {
    if (g.sport !== currentSport) { currentSport = g.sport; console.log('\n' + g.sport + ' — ' + g.league) }
    const status   = g.state === 'Live' ? '[LIVE 🔴]' : `[Prematch, ${g.kickoff}]`
    const oddsLine = g.selections.map(s => `${s.label} ${s.odds}`).join(' | ')
    console.log(`${i + 1}. ${g.title}  ${status}`)
    console.log(`   ${g.market}: ${oddsLine}`)
  })

  console.log('\n---JSON---')
  console.log(JSON.stringify(results))

})().catch(e => { console.error('Fatal error:', e.message); process.exit(1) })
