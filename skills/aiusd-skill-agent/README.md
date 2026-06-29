# AIUSD Skill for OpenClaw/ClawdBot

The official AIUSD trading skill for your personal AI assistant. Trade cryptocurrencies, check balances, and manage your AIUSD account through natural language conversations in Telegram, Discord, WhatsApp, or any platform your bot supports.

## 🚀 Quick Start

### Step 1: Install the Skill

**Option A: Drag & Drop (Easiest)**
1. Download the skill file: **[Download aiusd-skill-agent.skill](https://github.com/galpha-ai/aiusd-skills/releases/download/v1.0.0/aiusd-skill-agent.skill)**
2. Start your ClawdBot/OpenClaw assistant
3. Open your chat (Telegram, Discord, WhatsApp, etc.)
4. Drag and drop the downloaded `.skill` file into the chat
5. Your bot will automatically install the skill

**Option B: Manual Installation**
1. Download and extract the skill file: **[Download aiusd-skill-agent.skill](https://github.com/galpha-ai/aiusd-skills/releases/download/v1.0.0/aiusd-skill-agent.skill)**
2. Extract: `tar -xzf aiusd-skill-agent.skill`
3. Copy the extracted folder to your OpenClaw skills directory
4. Restart your bot

### Step 2: Authentication Setup

The bot will automatically handle authentication when you first use AIUSD features. If automatic login fails, simply tell your bot: *"re-login"* in the chat.

### Step 3: Start Trading!

Now you can talk to your bot naturally:

- *"What's my AIUSD balance?"*
- *"Buy $100 worth of SOL with USDC"*
- *"Show my recent transactions"*
- *"What are my trading addresses?"*

## 💬 What You Can Ask Your Bot

### Check Balance & Accounts
- *"Check my AIUSD balance"*
- *"How much do I have in my account?"*
- *"What's my total portfolio value?"*
- *"Show me my trading addresses"*

### Execute Trades
- *"Buy $50 of SOL with USDC"*
- *"Sell 100 USDC for ETH"*
- *"Swap 0.1 ETH to SOL"*
- *"Trade 1000 USDC for BTC"*

### Staking Operations
- *"Stake 500 AIUSD"*
- *"Unstake my AIUSD"*
- *"How much am I earning from staking?"*

### Transaction History
- *"Show my last 10 transactions"*
- *"What trades did I make today?"*
- *"Check my transaction history"*

### Account Management
- *"Withdraw 100 USDC to my wallet"*
- *"Top up gas for Solana"*
- *"Ensure I have enough gas"*

### Deposits & Recharge
- *"How can I add funds to my account?"*
- *"I want to deposit money"*
- *"Where can I recharge?"*

## 💰 Adding Funds to Your Account

Your bot will guide you through two deposit options:

### Option 1: Direct USDC Deposit
- **USDC only** - other coins not supported for direct deposit
- Ask your bot: *"What are my deposit addresses?"*
- Send USDC to your Solana or EVM trading address

### Option 2: All Coins via Website
- Visit **https://aiusd.ai**
- Login with the same wallet you use for trading
- Supports all stablecoins (USDT, DAI, BUSD, etc.)

**Important**: For coins other than USDC, you must use the website - direct deposits only accept USDC.

## ⚙️ Supported Platforms

This skill works with OpenClaw/ClawdBot on:
- **Telegram** - Private chats and groups
- **Discord** - Direct messages and server channels
- **WhatsApp** - Personal and business accounts
- **Slack** - Workspaces and direct messages
- **SMS** - Text message interface
- **CLI** - Command line interface

## 🔒 Privacy & Security

- **Local First**: Your bot runs locally, your data stays private
- **Secure Storage**: Authentication tokens stored locally on your device
- **No Data Sharing**: AIUSD skill only communicates with official AIUSD servers
- **Open Source**: Skill code is transparent and auditable

## 📱 Example Conversation

```
You: Hey bot, what's my AIUSD balance?

Bot: 🔍 Checking your AIUSD account...

✅ Your AIUSD Balance:
• Custody Account: 1,250.75 AIUSD
• Staking Account: 2,500.00 sAIUSD
• Total Value: $3,750.75 USD

You: Buy $100 worth of SOL with USDC

Bot: 🔄 Executing trade: Buy SOL with $100 USDC...

✅ Trade completed successfully!
• Bought: 0.234 SOL
• Spent: $100.00 USDC
• Transaction ID: abc123...
```

## 🌟 Why Use This Skill?

- **Natural Language**: No complex commands - just talk normally
- **Real-time**: Instant balance checks and trade execution
- **Multi-platform**: Works wherever your bot is available
- **Secure**: OAuth authentication with official AIUSD servers
- **Comprehensive**: Full trading, staking, and account management

---

**Get Started**: **[Download the skill file](https://github.com/galpha-ai/aiusd-skills/releases/download/v1.0.0/aiusd-skill-agent.skill)** and drop it into your bot's chat to start trading!

**Version**: 1.0.0 | **License**: MIT | **Support**: https://aiusd.ai