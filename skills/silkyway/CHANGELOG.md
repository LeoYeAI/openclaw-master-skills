# Changelog

All notable changes to the SilkyWay SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-12

### Added

- Initial release extracted from monorepo
- Escrow transfer support (`silk pay`, `silk claim`, `silk cancel`)
- On-chain account support with operator delegation and spending limits
- Multi-wallet management (`silk wallet create`, `silk wallet list`)
- Address book for contacts (`silk contacts add/remove/list/get`)
- Claim links for browser-based payment claiming
- Drift protocol integration for yield on account balances
- Multi-cluster support (mainnet-beta and devnet)
- Support chat integration (`silk chat`)
- DevNet faucet for testing (`silk wallet fund`)
- OpenClaw skill integration with ClawHub publishing
- Comprehensive CLI reference and API documentation

### Distribution

- Published to npm registry as `@silkysquad/silk`
- Published to ClawHub as "silkyway" skill
- Dedicated repository at https://github.com/silkysquad/silk

### Requirements

- Node.js 18 or higher
- npm (comes with Node.js)
- Internet connection to Solana RPC and silkyway.ai API

### Security

- Non-custodial: private keys stored locally at `~/.config/silkyway/config.json`
- All authorization enforced on-chain by Solana programs
- Backend never sees private keys (build-sign-submit flow)

[0.1.0]: https://github.com/silkysquad/silk/releases/tag/v0.1.0
