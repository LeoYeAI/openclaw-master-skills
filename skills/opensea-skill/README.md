# OpenSea Skill

**Query NFT data, trade on the Seaport marketplace, and swap ERC20 tokens** across Ethereum, Base, Arbitrum, Optimism, Polygon, and more.

## What is this?

This is an [Agent Skill](https://skills.sh/docs) for AI coding assistants. Once installed, your agent can interact with the OpenSea API to query NFT data, execute marketplace operations, and swap ERC20 tokens using the [OpenSea CLI](https://github.com/ProjectOpenSea/opensea-cli), shell scripts, or the MCP server.

## Prerequisites

- `OPENSEA_API_KEY` environment variable — for CLI, SDK, and REST API scripts
- `OPENSEA_MCP_TOKEN` environment variable — for the MCP server (separate from API key)
- Node.js >= 18.0.0 — for `@opensea/cli`
- `curl` for REST shell scripts
- `jq` (recommended) for parsing JSON responses

Get both credentials at [opensea.io/settings/developer](https://opensea.io/settings/developer).

## Installing the Skill

### Using npx

```bash
npx skills add ProjectOpenSea/opensea-skill
```

### Using Claude Code

```bash
/skill install ProjectOpenSea/opensea-skill
```

### Manual Installation

Clone this repository to your skills directory:

```bash
git clone https://github.com/ProjectOpenSea/opensea-skill.git ~/.skills/opensea
```

Refer to your AI tool's documentation for skills directory configuration.

## What's Included

### Skill Definition

[`SKILL.md`](SKILL.md) — the main skill file that teaches your agent how to use the OpenSea API, including the CLI, task guides, script references, MCP tool documentation, and end-to-end workflows for buying, selling, and swapping tokens.

### OpenSea CLI (Recommended)

The [`@opensea/cli`](https://github.com/ProjectOpenSea/opensea-cli) package provides a command-line interface and programmatic SDK for all OpenSea API operations. Install with `npm install -g @opensea/cli` or use `npx @opensea/cli`.

```bash
opensea collections get mfers
opensea listings best mfers --limit 5
opensea tokens trending --limit 5
opensea search "cool cats"
opensea swaps quote --from-chain base --from-address 0x0000000000000000000000000000000000000000 \
  --to-chain base --to-address 0xTokenAddress --quantity 0.02 --address 0xYourWallet
```

Supports JSON, table, and [TOON](https://github.com/toon-format/toon) output formats. TOON uses ~40% fewer tokens than JSON, ideal for AI agent context windows (`--format toon`).

See [`SKILL.md`](SKILL.md) for the full CLI command reference and SDK usage.

### Shell Scripts

Ready-to-use scripts in [`scripts/`](scripts/) for common operations (alternative to the CLI):

| Script | Purpose |
|--------|---------|
| `opensea-collection.sh` | Fetch collection by slug |
| `opensea-nft.sh` | Fetch single NFT by chain/contract/token |
| `opensea-best-listing.sh` | Get lowest listing for an NFT |
| `opensea-best-offer.sh` | Get highest offer for an NFT |
| `opensea-swap.sh` | Swap tokens via OpenSea DEX aggregator |
| `opensea-fulfill-listing.sh` | Get buy transaction data |
| `opensea-fulfill-offer.sh` | Get sell transaction data |

See [`SKILL.md`](SKILL.md) for the full scripts reference and usage examples.

### Reference Docs

Detailed API documentation in [`references/`](references/):

- [`rest-api.md`](references/rest-api.md) — REST endpoint families and pagination
- [`marketplace-api.md`](references/marketplace-api.md) — Buy/sell workflows and Seaport details
- [`stream-api.md`](references/stream-api.md) — WebSocket event streaming
- [`seaport.md`](references/seaport.md) — Seaport protocol and NFT purchase execution
- [`token-swaps.md`](references/token-swaps.md) — Token swap workflows via MCP

## OpenSea MCP Server

An official MCP server provides direct LLM integration for token swaps and NFT operations. Add to your MCP config:

```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

See [`SKILL.md`](SKILL.md) for the full list of available MCP tools.

## Example Usage

Once installed, prompt your AI assistant:

```
Get me the floor price for the Pudgy Penguins collection on OpenSea
```

```
Swap 0.02 ETH to USDC on Base using OpenSea
```

```
Show me the best offer on BAYC #1234
```

The agent will use the `opensea` CLI to query the API directly.

## Supported Chains

This skill supports all chains available on OpenSea, including `ethereum`, `solana`, `abstract`, `ape_chain`, `arbitrum`, `avalanche`, `b3`, `base`, `bera_chain`, `blast`, `flow`, `gunzilla`, `hyperevm`, `hyperliquid`, `ink`, `megaeth`, `monad`, `optimism`, `polygon`, `ronin`, `sei`, `shape`, `somnia`, `soneium`, `unichain`, and `zora`.

## Learn More

- [OpenSea CLI](https://github.com/ProjectOpenSea/opensea-cli) — CLI and SDK for OpenSea API
- [OpenSea Developer Docs](https://docs.opensea.io/)
- [OpenSea Developer Portal](https://opensea.io/settings/developer)
- [Agent Skills Directory](https://skills.sh/docs)
