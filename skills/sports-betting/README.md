# Sports betting skill

AI agent skill for **Polygon** betting via [Pinwin](https://pinwin.xyz), with on-chain execution. This skill covers **Polygon only**. Fetch prematch and live games, markets, and odds from the **Azuro subgraph**; optionally place bets and claim winnings through the Pinwin API. Use it from [OpenClaw](https://docs.openclaw.ai) (or any AgentSkills-compatible assistant)—e.g. to list games only, or to bet and claim.

- **Entry point:** [SKILL.md](SKILL.md). Reference details in **references/** (api, subgraph, dictionaries, polygon, viem).
- **Invocation:** The skill is **invocation-only** (`disable-model-invocation: true`): the assistant will not use it automatically. You must explicitly ask (e.g. “place a bet with Pinwin”) or use the slash command (e.g. `/sports_betting`). This avoids accidental bets.
- **Packaging:** ZIP this folder for upload (ClawHub, etc.).
