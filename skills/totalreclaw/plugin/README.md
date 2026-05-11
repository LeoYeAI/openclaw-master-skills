<p align="center">
  <img src="../../docs/assets/logo.png" alt="TotalReclaw" width="80" />
</p>

<h1 align="center">@totalreclaw/totalreclaw</h1>

<p align="center">
  <strong>End-to-end encrypted memory for OpenClaw -- fully automatic, yours forever</strong>
</p>

<p align="center">
  <a href="https://totalreclaw.xyz">Website</a> &middot;
  <a href="https://www.npmjs.com/package/@totalreclaw/totalreclaw">npm</a> &middot;
  <a href="../../docs/guides/beta-tester-guide.md">Getting Started</a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@totalreclaw/totalreclaw"><img src="https://img.shields.io/npm/v/@totalreclaw/totalreclaw?color=7B5CFF" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/@totalreclaw/totalreclaw"><img src="https://img.shields.io/npm/dm/@totalreclaw/totalreclaw" alt="npm downloads"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
</p>

---

Your AI agent remembers everything -- preferences, decisions, facts -- encrypted so only you can read it. Built for [OpenClaw](https://openclaw.ai) with fully automatic memory extraction and recall.

## Install

Ask your OpenClaw agent:

> "Install the @totalreclaw/totalreclaw plugin"

Or from the terminal:

```bash
openclaw plugins install @totalreclaw/totalreclaw
```

The agent handles setup: generates your encryption keys, asks you to save a 12-word recovery phrase, and registers you. After that, memory is fully automatic.

## How It Works

After setup, everything happens in the background:

- **Start of conversation** -- loads relevant memories from your encrypted vault
- **During conversation** -- extracts facts, preferences, and decisions automatically
- **Before context compaction** -- saves important context before the window is trimmed

All encryption happens client-side using AES-256-GCM. The server never sees your plaintext data.

## Tools

Your agent gets these tools automatically:

| Tool | Description |
|------|-------------|
| `totalreclaw_remember` | Manually store a fact |
| `totalreclaw_recall` | Search memories by natural language |
| `totalreclaw_forget` | Delete a specific memory |
| `totalreclaw_export` | Export all memories as plaintext |
| `totalreclaw_status` | Check billing status and quota |
| `totalreclaw_consolidate` | Merge duplicate memories |
| `totalreclaw_import_from` | Import from Mem0 or MCP Memory Server |

Most of the time you won't use these directly -- the automatic hooks handle memory for you.

## Features

- **End-to-end encrypted** -- AES-256-GCM encryption, blind index search, HKDF auth
- **Automatic extraction** -- LLM extracts facts from conversations, no manual input needed
- **Semantic search** -- Local embeddings + BM25 + cosine reranking with RRF fusion
- **Smart dedup** -- Cosine similarity catches paraphrases; LLM-guided dedup catches contradictions (Pro)
- **On-chain storage** -- Encrypted data stored on Gnosis Chain, indexed by The Graph
- **Portable** -- One 12-word phrase. Any device, same memories, no lock-in
- **Import** -- Migrate from Mem0 or MCP Memory Server

## Free Tier & Pricing

| Tier | Memories | Reads | Storage | Price |
|------|----------|-------|---------|-------|
| **Free** | 500/month | Unlimited | Testnet (trial) | $0 |
| **Pro** | Unlimited | Unlimited | Permanent on-chain (Gnosis) | See `totalreclaw_status` |

Pay with card via Stripe. Use `totalreclaw_status` to check current pricing. Counter resets monthly.

## Using with Other Agents

TotalReclaw also works outside OpenClaw:

- **Claude Desktop / Cursor / Windsurf** -- Use [@totalreclaw/mcp-server](https://www.npmjs.com/package/@totalreclaw/mcp-server)
- **NanoClaw** -- Built-in support via MCP bridge

Same encryption, same recovery phrase, same memories across all agents.

## Learn More

- [Getting Started Guide](../../docs/guides/beta-tester-guide.md)
- [totalreclaw.xyz](https://totalreclaw.xyz)
- [Main Repository](https://github.com/p-diogo/totalreclaw)

## License

MIT
