# citrea-claw-skill — Setup Guide

A CLI tool for monitoring the [Citrea](https://citrea.xyz) Bitcoin L2 ecosystem.
Tracks DEX pools, liquidity, arbitrage opportunities, and sends Telegram alerts.

## Requirements

- Node.js v18 or higher
- A Telegram account (optional, for alerts)

## Installation
```bash
git clone https://github.com/yourname/citrea-claw-skill.git
cd citrea-claw-skill
npm install
```

## Configuration

Copy the example env file:
```bash
cp .env.example .env
```

Then edit `.env` with your own values. All fields are optional — the tool works
without Telegram configured, alerts will just be skipped.

### Getting your Telegram bot token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. BotFather will give you a token like `123456:ABC-DEF1234...`
4. Paste it into `TELEGRAM_BOT_TOKEN` in your `.env`

### Getting your Telegram chat ID

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. It will instantly reply with your numeric ID, e.g. `Your Telegram ID: 123456789`
4. Paste that number into `TELEGRAM_CHAT_ID` in your `.env`

> Note: do NOT use `getUpdates` to find your chat ID if your bot is connected
> to OpenClaw — OpenClaw consumes incoming messages before `getUpdates` can see them.

### Test your Telegram setup
```bash
node telegram-test.js
```

You should receive a test message from your bot within a few seconds.

## Usage
```bash
node index.js                                    # show all commands

# Wallet
node index.js balance <address>                  # cBTC + token balances with USD values

# Prices
node index.js price <token>                      # USD price from RedStone oracle
node index.js pool:price <tokenA> <tokenB>       # implied price from each DEX side by side

# Pools
node index.js pools:recent [hours]               # new pools in last N hours (default 24)
node index.js pools:latest                       # most recent pool per DEX
node index.js pools:monitor                      # live new pool watcher with Telegram alerts

# Liquidity
node index.js pool:liquidity <poolAddr>          # TVL by pool address
node index.js pool:liquidity <tokenA> <tokenB>   # TVL by pair
node index.js pool:liquidity <token>             # all pools for a token

# Arbitrage
node index.js arb:check <tokenA> <tokenB>        # check a specific pair
node index.js arb:scan                           # scan all pairs once
node index.js arb:monitor                        # live monitor with Telegram alerts

# Transactions
node index.js txns <address> [hours]             # recent swap activity (default 24h)
```

## Arb monitor alert threshold

In your `.env`, set `ARB_ALERT_THRESHOLD_BPS` to control sensitivity:

| Value | Meaning         |
|-------|-----------------|
| 25    | 0.25% — noisy   |
| 50    | 0.50% — default |
| 100   | 1.00% — strict  |

## Supported tokens

| Symbol  | Description                          |
|---------|--------------------------------------|
| wcBTC   | Wrapped Citrea Bitcoin               |
| ctUSD   | Citrea USD stablecoin                |
| USDC.e  | Bridged USDC (LayerZero)             |
| USDT.e  | Bridged USDT (LayerZero)             |
| WBTC.e  | Bridged Wrapped Bitcoin (LayerZero)  |
| JUSD    | BTC-backed stablecoin (JuiceDollar)  |

## Supported DEXes

- **JuiceSwap** — Uniswap V3 fork, multiple fee tiers (0.05%, 0.30%, 1.00%)
- **Satsuma** — Algebra fork, single pool per pair with dynamic fees

## Running 24/7 (Deployment)

The CLI tools work fine locally, but `arb:monitor` and `pools:monitor` need to
run continuously to be useful. For this you need a server.

### Recommended: VPS with PM2

Any cheap VPS works — DigitalOcean, Hetzner, Linode, etc. A $6/month droplet
is more than enough.

**1. Copy your project to the server**
```bash
rsync -avz --exclude node_modules /path/to/citrea-claw-skill/ user@YOUR_SERVER_IP:/root/citrea-claw-skill/
```

**2. SSH in and install dependencies**
```bash
ssh user@YOUR_SERVER_IP
cd /root/citrea-claw-skill
npm install
```

**3. Create your `.env` on the server**
```bash
nano .env
```

Paste in your values — same as your local `.env`. At minimum:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ARB_ALERT_THRESHOLD_BPS=50
ARB_MONITOR_INTERVAL_SEC=15
```

**4. Install PM2 and start the monitors**

[PM2](https://pm2.keymetrics.io/) is a process manager that keeps your scripts
running forever and restarts them automatically if they crash.
```bash
npm install -g pm2

# Start arb monitor
pm2 start index.js --name "arb-monitor" -- arb:monitor

# Start pool monitor
pm2 start index.js --name "pool-monitor" -- pools:monitor

# Save so monitors survive server reboots
pm2 save
pm2 startup
```

**5. Verify everything is running**
```bash
pm2 status
```

You should see both processes with status `online`. Stream logs with:
```bash
pm2 logs arb-monitor
pm2 logs pool-monitor
```

**6. Updating after code changes**
```bash
rsync -avz --exclude node_modules /path/to/citrea-claw-skill/ user@YOUR_SERVER_IP:/root/citrea-claw-skill/
ssh user@YOUR_SERVER_IP "cd /root/citrea-claw-skill && npm install && pm2 restart all"
```

### PM2 cheatsheet

| Command | Description |
|---------|-------------|
| `pm2 status` | Show all running processes |
| `pm2 logs <name>` | Stream logs for a process |
| `pm2 restart <name>` | Restart a process |
| `pm2 stop <name>` | Stop a process |
| `pm2 delete <name>` | Remove a process from PM2 |
| `pm2 monit` | Live dashboard with CPU/memory |

> **Note:** Never commit your `.env` file to git. The `.gitignore` already
> excludes it — double check with `git status` before pushing.

## Notes

- All data is read directly from Citrea mainnet — no third-party APIs
- Prices are sourced from RedStone push oracles deployed on Citrea
- Arb detection is indicative only — always verify on-chain before executing
- RPC calls use the public endpoint `https://rpc.mainnet.citrea.xyz`
- JuiceSwap pools use svJUSD internally — JUSD pairs are handled transparently

## License

MIT
