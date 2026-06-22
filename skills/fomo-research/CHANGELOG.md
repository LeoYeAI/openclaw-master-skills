# Changelog — fomo-research skill

## [0.3.0] - 2026-02-21
### Added
- **Traders search** (`GET /v1/traders/search`) — compound filtering by win rate, PnL, trades, chain
- **Handle positions** (`GET /v1/handle/:handle/positions`) — computed open/closed positions from activity data
- **Handle theses** (`GET /v1/handle/:handle/theses`) — all Fomo thesis comments by a specific trader
- New workflow examples: elite trader search, position checking, trader thesis lookup
- Updated API reference with response schemas and query params for all v0.3.0 endpoints

## [0.2.0] - 2026-02-18
### Added
- **Convergence events** (`GET /v1/convergence`) — real-time detection when 2+ elite wallets buy the same token, with ATH tracking
- **Trader stats** (`GET /v1/handle/:handle/stats`) — aggregated PnL, win rate, ROI, per-chain breakdown, top trades
- **Token thesis** (`GET /v1/tokens/:mint/thesis`) — buy theses from Fomo traders with position data and sentiment summary
- **Hot tokens** (`GET /v1/tokens/hot`) — trending tokens by unique buyer count
- New workflow examples: convergence checking, trader lookup, thesis queries, hot token scanning
- Updated API reference with full response schemas for all new endpoints

## [0.1.1] - 2026-02-14
### Added
- Data model documentation: Activity vs Trades vs Holdings explained
- Guidance on interpreting buy/sell signals and presenting data to humans
- Clear labeling rules for new buys, exits, and position changes

## [0.1.0] - 2026-02-13
### Added
- Initial skill release
- Registration, watchlist management, activity polling
- Leaderboard, trending handles, Fomo sync
- x402 payment integration docs
- Poll → Fetch pattern for minimizing paid calls
- Convergence detection pattern
- Heartbeat integration guide
