# Supported Services

List of services with known credential patterns that the skill can auto-detect and normalize.

## Social & Agent Networks

### X (Twitter)
**File patterns:** `x/credentials.json`, `twitter/credentials.json`

**Keys:**
```env
X_CONSUMER_KEY=...
X_CONSUMER_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
X_BEARER_TOKEN=...
X_USERNAME=...
X_USER_ID=...
```

### Molten
**File patterns:** `molten-creds.json`, `molten/credentials.json`

**Keys:**
```env
MOLTEN_API_KEY=molten_...
MOLTEN_AGENT_NAME=...
MOLTEN_AGENT_ID=...
```

### Moltbook
**File patterns:** `moltbook-creds.json`, `moltbook/credentials.json`

**Keys:**
```env
MOLTBOOK_API_KEY=moltbook_sk_...
MOLTBOOK_AGENT_NAME=...
MOLTBOOK_PROFILE_URL=...
```

### Botchan / 4claw
**File patterns:** `4claw/credentials.json`, `botchan/credentials.json`

**Keys:**
```env
BOTCHAN_API_KEY=clawchan_...
BOTCHAN_AGENT_NAME=...
```

## AI Providers

### OpenAI
**Keys:**
```env
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
```

### Anthropic
**Keys:**
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### Google / Gemini
**Keys:**
```env
GOOGLE_API_KEY=...
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GEMINI_API_KEY=...
```

### OpenRouter
**Keys:**
```env
OPENROUTER_API_KEY=sk-or-...
```

## Development Tools

### GitHub
**Keys:**
```env
GITHUB_TOKEN=ghp_...
GITHUB_PAT=ghp_...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

### GitLab
**Keys:**
```env
GITLAB_TOKEN=glpat-...
GITLAB_API_KEY=...
```

## Cloud Providers

### AWS
**Keys:**
```env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_DEFAULT_REGION=us-east-1
```

### Google Cloud
**Keys:**
```env
GCP_PROJECT_ID=...
GCP_SERVICE_ACCOUNT_KEY=...
GOOGLE_CLOUD_PROJECT=...
```

### Azure
**Keys:**
```env
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
AZURE_SUBSCRIPTION_ID=...
```

## Databases

### PostgreSQL
**Keys:**
```env
POSTGRES_HOST=...
POSTGRES_PORT=5432
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
DATABASE_URL=postgresql://...
```

### MongoDB
**Keys:**
```env
MONGODB_URI=mongodb://...
MONGODB_HOST=...
MONGODB_USER=...
MONGODB_PASSWORD=...
```

### Redis
**Keys:**
```env
REDIS_URL=redis://...
REDIS_HOST=...
REDIS_PORT=6379
REDIS_PASSWORD=...
```

## Communication

### Telegram
**Keys:**
```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_CHAT_ID=...
```

### Discord
**Keys:**
```env
DISCORD_BOT_TOKEN=...
DISCORD_CLIENT_ID=...
DISCORD_CLIENT_SECRET=...
DISCORD_WEBHOOK_URL=...
```

### Slack
**Keys:**
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
SLACK_WEBHOOK_URL=...
```

### WhatsApp
**Keys:**
```env
WHATSAPP_PHONE_NUMBER=...
WHATSAPP_API_KEY=...
WHATSAPP_BUSINESS_ID=...
```

## Payment Processing

### Stripe
**Keys:**
```env
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### PayPal
**Keys:**
```env
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=sandbox|live
```

## Analytics

### Google Analytics
**Keys:**
```env
GA_TRACKING_ID=UA-...
GA_MEASUREMENT_ID=G-...
```

### Mixpanel
**Keys:**
```env
MIXPANEL_TOKEN=...
MIXPANEL_SECRET=...
```

## Email Services

### SendGrid
**Keys:**
```env
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=...
```

### Mailgun
**Keys:**
```env
MAILGUN_API_KEY=...
MAILGUN_DOMAIN=...
```

### SMTP (Generic)
**Keys:**
```env
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=...
```

## Web3 / Blockchain

### Ethereum
**Keys:**
```env
ETH_PRIVATE_KEY=0x...
ETH_RPC_URL=...
INFURA_API_KEY=...
ALCHEMY_API_KEY=...
ETHERSCAN_API_KEY=...
```

### Solana
**Keys:**
```env
SOLANA_PRIVATE_KEY=...
SOLANA_RPC_URL=...
```

## Storage

### AWS S3
**Keys:**
```env
AWS_S3_BUCKET=...
AWS_S3_REGION=...
# (Uses AWS credentials above)
```

### Cloudflare R2
**Keys:**
```env
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET=...
```

### Pinata (IPFS)
**Keys:**
```env
PINATA_API_KEY=...
PINATA_SECRET_API_KEY=...
PINATA_JWT=...
```

## Search

### Algolia
**Keys:**
```env
ALGOLIA_APP_ID=...
ALGOLIA_API_KEY=...
ALGOLIA_SEARCH_KEY=...
```

### Brave Search
**Keys:**
```env
BRAVE_API_KEY=...
```

## Generic Patterns

The skill also detects generic patterns:

- `*_API_KEY`
- `*_SECRET`
- `*_TOKEN`
- `*_PASSWORD`
- `*_CLIENT_ID`
- `*_CLIENT_SECRET`
- `*_ACCESS_KEY`

These are normalized to UPPER_SNAKE_CASE and prefixed with the service name if detected.

## Adding Custom Services

To add support for a new service, edit `scripts/consolidate.py` and add to `SERVICE_MAPPINGS`:

```python
SERVICE_MAPPINGS = {
    'myservice': {
        'api_key': 'MYSERVICE_API_KEY',
        'secret': 'MYSERVICE_SECRET',
    },
    # ... existing services
}
```

Then the skill will auto-detect and normalize your service's credentials.
