# breeze-x402-payment-api

Agent skill for operating Breeze via x402-paid HTTP endpoints on Solana.

## How to use this skill

1. Put this skill folder in your platform's skills directory (for example, project-level `skills/` or platform-specific skills path).
2. Ensure required environment variables are available to the agent runtime.
3. Start an agent session and ask for Breeze actions such as:
   - "Check my Breeze balances"
   - "Deposit 10 USDC into Breeze"
   - "Withdraw 5 USDC from Breeze"
4. The agent should auto-select this skill from `SKILL.md` metadata and follow the workflow defined there.

## What this skill does

- Checks Breeze balances and yield data
- Builds deposit and withdrawal transactions
- Signs and broadcasts returned Solana transactions
- Handles x402 payment-gated requests through the configured client flow

## Skill entrypoint

- `SKILL.md` is the canonical agent instruction file

Discovery and activation are based on `SKILL.md` frontmatter (`name` and `description`).

## Requirements

- Node.js runtime
- Network access to:
  - `X402_API_URL` (default: `https://x402.breeze.baby`)
  - `SOLANA_RPC_URL` (default: `https://api.mainnet-beta.solana.com`)
- Solana wallet funded for x402 USDC micropayments

## Environment variables

- `WALLET_PRIVATE_KEY` (required)
- `STRATEGY_ID` (optional, defaults to `43620ba3-354c-456b-aa3c-5bf7fa46a6d4` — any valid strategy ID works)
- `X402_API_URL` (optional)
- `SOLANA_RPC_URL` (optional)
- `BASE_ASSET` (optional)

## Notes

- Keep operational logic and workflow details in `SKILL.md`.
- Use this README for human-facing context and repository navigation.
- For publishing to skills registries, keep this README and `SKILL.md` in sync.
