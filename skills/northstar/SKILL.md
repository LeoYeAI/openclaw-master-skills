# Northstar - Daily Business Briefing

Northstar delivers a clean daily business briefing to your preferred channel every morning. Connect your Stripe and/or Shopify accounts, configure your schedule, and wake up knowing.

No more tab-hopping. Your agent does the work while you sleep.

## What It Does

Every morning at your configured time, Northstar:
1. Pulls yesterday's revenue from Stripe (MRR, new subs, churn, payment failures)
2. Pulls order data from Shopify (orders, refunds, top products)
3. Calculates week-over-week and month-to-date metrics
4. Flags anything that needs attention (unusual churn, payment retries, large refunds)
5. Delivers a clean briefing via your preferred channel (iMessage, Slack, Telegram, or Email)

## Example Output

```
📊 Northstar Daily Briefing - March 22
Revenue yesterday: $1,247 (+12% vs last week)
Active subscribers: 342 (+3 new, -1 churn)
Month-to-date: $18,430 (74% of $24,900 goal)

Shopify: 23 orders fulfilled | 8 open | 1 refund ($47)

⚠️ 2 payment retries pending - review in Stripe
Next: 6 days left in month, on track.
```

## Quick Start

### 1. Install and try the demo

```bash
clawhub install northstar
northstar demo    # See a sample briefing immediately - no config needed
```

### 2. Set up (interactive wizard, ~4 minutes)

```bash
northstar setup
```

The setup wizard walks you through everything: tier selection, API keys, delivery channel, and schedule. No JSON editing required.

### 3. Test with your real data

```bash
northstar test
```

Dry-run briefing printed to terminal. No message sent until you're ready.

### 4. Go live

```bash
northstar run    # Send briefing now
```

Or schedule it (add to OpenClaw cron via `openclaw cron edit`):

```
# Northstar daily briefing at 6:00 AM
0 6 * * * northstar run
```

### Manual configuration (optional)

If you prefer editing config directly instead of using the setup wizard:

```bash
cp ~/.clawd/skills/northstar/config/northstar.json.example ~/.clawd/skills/northstar/config/northstar.json
```

Edit `northstar.json` with your API keys. See **Configuration** section below.

## Configuration

Config file: `~/.clawd/skills/northstar/config/northstar.json`

```json
{
  "delivery": {
    "channel": "imessage",
    "recipient": "+15551234567"
  },
  "schedule": {
    "hour": 6,
    "timezone": "America/New_York"
  },
  "stripe": {
    "enabled": true,
    "api_key": "sk_live_YOUR_KEY_HERE",
    "monthly_revenue_goal": 24900
  },
  "shopify": {
    "enabled": false,
    "shop_domain": "your-store.myshopify.com",
    "access_token": "shpat_YOUR_TOKEN_HERE"
  },
  "alerts": {
    "payment_failures": true,
    "churn_threshold": 3,
    "large_refund_threshold": 100
  }
}
```

### Delivery Channels

| Channel | Config value | Recipient format |
|---------|-------------|-----------------|
| iMessage | `"imessage"` | Phone number: `"+15551234567"` |
| Slack | `"slack"` | Webhook URL |
| Telegram | `"telegram"` | Chat ID (numeric) |
| Email | `"email"` | SMTP config (Gmail App Password supported) |
| Terminal only | `"none"` | n/a (dry-run mode) |

### Stripe Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Create a **Restricted Key** with read-only access to:
   - `charges` (read)
   - `customers` (read)
   - `subscriptions` (read)
   - `invoices` (read)
3. Paste the key into `stripe.api_key`

Set `monthly_revenue_goal` to your MRR target **in dollars** (e.g., `24900` = $24,900/month goal).

### Shopify Setup

1. Go to your Shopify Admin > Apps > Develop apps
2. Create a custom app with read access to:
   - `read_orders`
   - `read_products`
3. Install the app and copy the Admin API access token
4. Set `shopify.enabled: true`, add your shop domain and token

## Commands

| Command | Description |
|---------|-------------|
| `northstar demo` | **Start here.** Sample briefing with demo data -- no config needed |
| `northstar run` | Run briefing now, send to configured channel |
| `northstar test` | Dry-run - print briefing to terminal, no message sent |
| `northstar status` | Show config status and last run info |
| `northstar stripe` | Show Stripe data only (debug) |
| `northstar shopify` | Show Shopify data only (debug) |
| `northstar digest` | [Pro] Run weekly digest (7-day rollup, Sunday format) |
| `northstar trend` | [Pro] Show 7-day revenue trend with sparkline |

## Metrics Calculated

### Stripe Metrics
- **Yesterday's revenue** - total charges, successful only
- **Active subscribers** - current subscription count
- **New subscribers** - started in last 24 hours
- **Churned subscribers** - canceled in last 24 hours
- **Net new MRR** - (new MRR) - (churned MRR)
- **Month-to-date revenue** - vs. your goal
- **Payment failures** - retries and failed charges

### Shopify Metrics
- **Orders fulfilled** - yesterday
- **Open orders** - pending fulfillment
- **Refunds** - count and total value yesterday
- **Top product** - highest-selling SKU yesterday

### Calculated
- **Week-over-week revenue change** - yesterday vs. same day last week
- **Month-to-date pacing** - % of monthly goal, days remaining, on-track status

## Requirements

- Python 3.9+
- OpenClaw with cron support
- `stripe` Python package (`pip install stripe`)
- `requests` Python package (for Shopify, usually pre-installed)

The install script handles dependencies automatically.

## Pricing

Available on [ClawHub](https://clawhub.ai/Daveglaser0823/northstar):

| Tier | Price | Features |
|------|-------|---------|
| **Lite** | Free | Stripe only, terminal output, manual run |
| **Standard** | $19/month | Stripe + Shopify, all delivery channels, scheduled runs |
| **Pro** | $49/month | Multi-channel delivery, custom metrics, weekly digest |

To purchase Standard or Pro: open a [GitHub issue](https://github.com/Daveglaser0823/northstar-skill/issues/new?title=License+Request:+Standard&labels=license-request,standard) or visit the [landing page](https://daveglaser0823.github.io/northstar-skill/) for the purchase link. After checkout, run `northstar activate YOUR-LICENSE-KEY` to activate.

## Privacy

Northstar runs entirely on your machine. Your Stripe and Shopify API keys are stored locally in `~/.clawd/skills/northstar/config/northstar.json` and are only used to call Stripe and Shopify directly from your local agent -- they are never sent to Northstar servers or third parties.

**License activation:** If you activate a Standard or Pro license key, the `northstar activate` command validates the key locally using HMAC verification. No data is transmitted to external servers during activation.

## Support

- GitHub Issues: [github.com/Daveglaser0823/northstar-skill](https://github.com/Daveglaser0823/northstar-skill)
- Follow the build story: [Man and Machine on LinkedIn](https://www.linkedin.com/in/daveglaser/)

---
