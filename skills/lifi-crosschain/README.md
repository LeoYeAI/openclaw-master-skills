# LI.FI Cross-Chain Skill for OpenClaw

An [OpenClaw](https://openclaw.ai) skill that enables AI agents to perform cross-chain token swaps, bridges, route comparison, transfer tracking, and DeFi zap composition via the [LI.FI](https://li.fi) protocol.

## Install

```bash
clawhub install lifi-crosschain
```

## What it does

- **Swap & Bridge** tokens across 35+ blockchains with a single command
- **Compare routes** across dozens of bridges (Stargate, Hop, Across) and DEXes (Uniswap, SushiSwap, 1inch)
- **Track transfers** — monitor cross-chain bridge progress in real-time
- **Zaps** — compose multi-step DeFi operations (bridge + swap + deposit) in one transaction
- **Discovery** — look up supported chains, tokens, and available routes

## Usage

Once installed, invoke the skill in your OpenClaw agent:

```
/lifi swap 1 ETH to USDC on Polygon
/lifi bridge 100 USDC from Ethereum to Arbitrum
/lifi track 0xabc123...
/lifi routes 1 ETH to USDC on Base
/lifi zap bridge ETH to Polygon and deposit into Aave
```

## How it works

The skill teaches agents to interact with the [LI.FI REST API](https://docs.li.fi). It provides:

1. **API reference** with ready-to-use curl commands for every endpoint
2. **Step-by-step workflows** for common operations (swap, bridge, compare, track, zap)
3. **Safety protocol** — mandatory validation rules for addresses, amounts, slippage, and token approvals
4. **Error handling** guidance for rate limits, failed routes, and partial completions

The API returns `transactionRequest` objects ready to sign — agents provide these to their wallet for execution.

## Requirements

- `curl` (used for HTTP calls to the LI.FI API)
- `LIFI_API_KEY` (optional — for higher rate limits)

## Links

- [LI.FI Documentation](https://docs.li.fi)
- [LI.FI API Reference](https://apidocs.li.fi)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub Listing](https://clawhub.ai/skill/lifi-crosschain)
