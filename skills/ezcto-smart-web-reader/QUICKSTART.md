# Quick Start Guide — EZCTO Smart Web Reader

Get started in 5 minutes. After installing, OpenClaw automatically reads any URL you mention — no special commands needed.

---

## Installation

### Option 1: Clone into OpenClaw skills directory
```bash
cd ~/.openclaw/skills
git clone https://github.com/pearl799/ezcto-web-translator ezcto-smart-web-reader
```

### Option 2: Copy manually
```bash
cp -r ezcto-smart-web-reader ~/.openclaw/skills/
```

### Verify installation
```bash
openclaw skills list | grep ezcto-smart-web-reader
# Should show: ✓ ezcto-smart-web-reader (enabled)
```

---

## Enable Required Tools

Edit your OpenClaw config:
```bash
nano ~/.openclaw/config.yaml
```

Ensure these tools are enabled:
```yaml
tools:
  web_fetch: enabled
  exec: enabled
  filesystem: enabled
```

Restart OpenClaw:
```bash
openclaw restart
```

---

## First Test

Start OpenClaw:
```bash
openclaw
```

Try these examples:

### Test 1: Instant read (cache hit)
```
You: What's on ezcto.fun?

OpenClaw: ✓ Read ezcto.fun
          Source: cache (0 tokens, 1.2s)
          Site type: general
          Title: EZCTO - Smart Web Access for AI Agents
          Primary action: Try it now

          Cached at: ~/.ezcto/cache/abc123.json
          View summary: cat ~/.ezcto/cache/abc123.meta.md
```

### Test 2: Crypto site (fresh parse)
```
You: What's on pump.fun?

OpenClaw: ✓ Read pump.fun
          Source: fresh parse (1,234 tokens, 5.4s)
          Site type: crypto

          Key findings:
          - Token: PUMP on Solana
          - Contract: PUMPxxx...
          - Total supply: 1B tokens
          - DEX: Raydium, Jupiter
          - Community: 8.5K Telegram members

          Suggested next steps:
          1. Verify contract on Solscan
          2. Check liquidity on DexScreener
          3. Analyze community sentiment

          Use /chain to execute suggested skills automatically.
```

### Test 3: E-commerce site
```
You: What does shopify.com offer?

OpenClaw: ✓ Read shopify.com
          Site type: ecommerce

          Products found: 8
          Featured: Shopify Plus ($2,000/month)
          Payment methods: Credit card, PayPal

          Primary action: Start Free Trial
```

---

## Verify Cache

Check what's been cached locally:
```bash
ls -lh ~/.ezcto/cache/

# View a parsed result (JSON)
cat ~/.ezcto/cache/*.json | jq '.meta.title'

# View markdown summary
cat ~/.ezcto/cache/*.meta.md
```

---

## Skill Chaining (Advanced)

Let OpenClaw execute multi-step workflows:

```
You: Research this crypto token: https://pump.fun/coin/abc123

OpenClaw: Executing research workflow...

          Step 1/4: Reading website ✓
          Step 2/4: Checking blockchain data ✓
          Step 3/4: Analyzing sentiment ✓
          Step 4/4: Generating report ✓

          Research complete! See: ~/reports/pump-abc123.md
```

---

## Configuration (Optional)

### Custom cache location
```bash
export EZCTO_CACHE_DIR=~/my-custom-cache
```

### Disable contribution to asset library
```bash
export EZCTO_CONTRIBUTE=false
```

### Custom API endpoint
```bash
export EZCTO_API_URL=https://my-proxy.example.com
```

---

## Troubleshooting

### Skill not found
```bash
ls ~/.openclaw/skills/ezcto-smart-web-reader/SKILL.md
openclaw restart
```

### "exec tool not enabled"
```bash
nano ~/.openclaw/config.yaml
# Set: exec: enabled
# Save and restart OpenClaw
```

### Cache directory error
```bash
mkdir -p ~/.ezcto/cache
chmod 755 ~/.ezcto/cache
```

### Page parsing fails
```bash
# Check logs
tail -f ~/.openclaw/logs/skills/ezcto-smart-web-reader.log

# Test URL directly
curl -s "https://api.ezcto.fun/v1/translate?url=YOUR_URL"
```

---

## Next Steps

- **Read full workflow:** `less SKILL.md`
- **Explore examples:** `ls examples/`
- **Customize detection:** Edit `references/site-type-detection.md`
- **Add new site types:** Create `references/extensions/yourtype-fields.md`
- **Join community:** https://discord.gg/ezcto

---

## Cost Tracking

View your usage:
```bash
openclaw stats skills --filter ezcto-smart-web-reader
```

Expected output:
```
ezcto-smart-web-reader
  Invocations: 45
  Cache hits: 33 (73%)
  Total tokens: 12,500 (avg 277 per call)
  Total cost: $0.037
  Avg latency: 3.2s
```

---

## Support

- **GitHub Issues:** https://github.com/pearl799/ezcto-web-translator/issues
- **Discord:** https://discord.gg/ezcto
- **Email:** support@ezcto.fun
- **Docs:** https://ezcto.fun/docs
