# WEEX Futures Trading Skill 🔵

An **Open AI Agent Skill** for trading USDT-margined perpetual futures on [WEEX](https://www.weex.com) exchange with up to 125x leverage.

> **Universal Compatibility**: This skill works with any AI agent that supports bash/curl commands, including Claude, GPT-4, Gemini, LLaMA, Mistral, and other LLM-based coding assistants.

## Features

- **Market Data** - Real-time ticker, order book, trades, candlesticks, funding rates
- **Account Management** - Check balances, positions, leverage settings
- **Order Operations** - Place market/limit orders, cancel orders, close positions
- **Position Management** - Open long/short, close positions, adjust margin
- **Trigger Orders** - Stop-loss, take-profit, and conditional orders
- **TP/SL Orders** - Position-level take-profit and stop-loss
- **AI Integration** - Log AI trading decisions to WEEX
- **Python CLI Client** - Command-line tool for quick API interactions

## Supported AI Agents

| Agent | Status | Notes |
|-------|--------|-------|
| Claude (Anthropic) | ✅ Fully Supported | Claude Code, API |
| GPT-4 (OpenAI) | ✅ Fully Supported | ChatGPT, API with code interpreter |
| Gemini (Google) | ✅ Fully Supported | Gemini Pro, API |
| LLaMA (Meta) | ✅ Fully Supported | With code execution capability |
| Mistral | ✅ Fully Supported | With code execution capability |
| Other LLMs | ✅ Compatible | Any agent supporting bash/curl |

## Installation

### As AI Agent Skill

The skill can be loaded by any AI agent that reads markdown-based skill definitions:

```bash
# Clone the repository
git clone https://github.com/bowen31337/weex-futures-trading-skill.git

# Or download just the skill file
curl -L -o SKILL.md \
  https://raw.githubusercontent.com/bowen31337/weex-futures-trading-skill/main/weex-trading/SKILL.md
```

### For Claude Code

```bash
# Install to Claude Code skills directory
cp SKILL.md ~/.claude/skills/weex-trading.md
```

### For Other AI Agents

Most AI agents can use this skill by:
1. Loading the `SKILL.md` file into the conversation context
2. Or referencing it as a system prompt
3. Or using your agent's skill/plugin installation mechanism

### As Standalone Python Client

```bash
git clone https://github.com/bowen31337/weex-futures-trading-skill.git
cd weex-futures-trading-skill
pip install requests
```

## Configuration

Set your WEEX API credentials as environment variables:

```bash
export WEEX_API_KEY=your_api_key
export WEEX_API_SECRET=your_api_secret
export WEEX_PASSPHRASE=your_passphrase
export WEEX_BASE_URL=https://api-contract.weex.com  # Optional
```

### Getting API Keys

1. Log in to your WEEX account at [weex.com](https://www.weex.com)
2. Navigate to **API Management** in account settings
3. Create a new API key with required permissions:
   - **Read** - View account info, positions, order history
   - **Trade** - Place and cancel orders
4. Save your **API Key**, **API Secret**, and **Passphrase** securely

## Usage

### Python CLI Client

```bash
# Market Data (no authentication required)
python scripts/weex_client.py time                    # Server time
python scripts/weex_client.py ticker cmt_btcusdt      # Get BTC price
python scripts/weex_client.py depth cmt_btcusdt       # Order book
python scripts/weex_client.py funding cmt_btcusdt     # Funding rate

# Account Info (authentication required)
python scripts/weex_client.py assets                  # Account balances
python scripts/weex_client.py positions               # All positions
python scripts/weex_client.py orders                  # Open orders
python scripts/weex_client.py settings                # Leverage settings

# Trading
python scripts/weex_client.py buy cmt_btcusdt 10              # Market buy 10 contracts
python scripts/weex_client.py buy cmt_btcusdt 10 95000        # Limit buy at $95,000
python scripts/weex_client.py sell cmt_btcusdt 10             # Market short 10 contracts
python scripts/weex_client.py close_long cmt_btcusdt 10       # Close long position
python scripts/weex_client.py close_short cmt_btcusdt 10      # Close short position

# Order Management
python scripts/weex_client.py cancel 1234567890       # Cancel order by ID
python scripts/weex_client.py cancel_all              # Cancel all orders
python scripts/weex_client.py close_all               # Close all positions

# Account Settings
python scripts/weex_client.py leverage cmt_btcusdt 20 # Set 20x leverage
```

### With AI Agents

Once loaded as a skill, any compatible AI agent can help you trade on WEEX:

```
You: What's the current BTC price on WEEX?
Agent: [Fetches ticker data and displays price]

You: Open a long position on BTC with 10 contracts
Agent: [Confirms order details and executes after your approval]

You: Show my current positions
Agent: [Displays all open positions with PnL]

You: Set a stop-loss at $90,000 for my BTC position
Agent: [Creates trigger order for risk management]
```

The skill provides curl commands that any AI agent with shell access can execute.

## API Reference

### Order Types

| Type | Description |
|------|-------------|
| `1` | Open Long (buy to open) |
| `2` | Open Short (sell to open) |
| `3` | Close Long (sell to close) |
| `4` | Close Short (buy to close) |

### Execution Types

| Type | Description |
|------|-------------|
| `0` | Normal order |
| `1` | Post-only (maker only) |
| `2` | FOK (fill or kill) |
| `3` | IOC (immediate or cancel) |

### Margin Modes

| Mode | Description |
|------|-------------|
| `1` | Cross margin |
| `3` | Isolated margin |

### Popular Trading Pairs

| Symbol | Description |
|--------|-------------|
| `cmt_btcusdt` | Bitcoin / USDT |
| `cmt_ethusdt` | Ethereum / USDT |
| `cmt_solusdt` | Solana / USDT |
| `cmt_xrpusdt` | XRP / USDT |
| `cmt_dogeusdt` | Dogecoin / USDT |

## Rate Limits

| Category | IP Limit | UID Limit |
|----------|----------|-----------|
| Market Data | 20 req/sec | N/A |
| Account Info | 10 req/sec | 10 req/sec |
| Order Operations | 10 req/sec | 10 req/sec |

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `40001` | Invalid parameter | Check parameter format |
| `40101` | Authentication failed | Verify credentials and timestamp |
| `40301` | IP not whitelisted | Add IP to API whitelist |
| `42901` | Rate limit exceeded | Reduce request frequency |

## Safety Notes

- **Always verify** order details before confirming trades
- **Check balance** before placing orders
- **Understand leverage risks** - higher leverage = higher risk
- **Use stop-loss orders** to manage risk
- **Start with small positions** when testing

## Project Structure

```
weex-trading/
├── SKILL.md                 # Open AI Agent skill definition (37 API endpoints)
├── README.md                # This file
├── scripts/
│   └── weex_client.py       # Python CLI client
└── references/
    └── api_reference.md     # API endpoint quick reference
```

## Skill Coverage

The SKILL.md provides complete coverage of the WEEX Futures API:

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Market Data | 13 | Tickers, order book, candles, funding rates |
| Account | 8 | Balances, settings, leverage, margin |
| Position | 3 | View and manage positions |
| Order | 9 | Place, cancel, query orders |
| Trigger Order | 4 | Stop-loss, take-profit triggers |
| TP/SL | 2 | Position-level TP/SL orders |
| AI Integration | 1 | Log AI trading decisions |
| **Total** | **38** | **100% API coverage** |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## What is an Open Agent Skill?

An **Open Agent Skill** is a markdown-based skill definition that can be used by any AI agent with code execution capabilities. Unlike proprietary plugin formats, open agent skills:

- 📖 **Human-readable** - Written in Markdown with embedded code blocks
- 🔌 **Universal** - Work with any AI agent (Claude, GPT, Gemini, LLaMA, etc.)
- 🛠️ **Self-contained** - Include all necessary code snippets and documentation
- 🔒 **Transparent** - Users can inspect exactly what commands will be executed
- 🤝 **Shareable** - Easy to distribute, fork, and contribute to

## Links

- [WEEX Exchange](https://www.weex.com)
- [WEEX API Documentation](https://www.weex.com/help)
- [Releases](https://github.com/bowen31337/weex-futures-trading-skill/releases)
- [Open Agent Skills Community](https://github.com/topics/open-agent-skills)
