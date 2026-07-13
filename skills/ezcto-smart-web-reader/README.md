# EZCTO Smart Web Reader — OpenClaw Edition

> The smart way for OpenClaw agents to access any URL — cache-first, structured JSON, 80%+ token savings vs screenshots.

[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost: $0 (cached)](https://img.shields.io/badge/Cost-$0%20cached-green)](https://ezcto.fun)

---

## Why This Skill?

**Problem:** Every time an OpenClaw agent accesses a URL, it faces three bad options:
1. **Screenshots** → Expensive (Claude multimodal = 2000+ tokens per image)
2. **Raw HTML** → Noisy and hard to parse (ads, scripts, boilerplate)
3. **web_fetch** → Returns unstructured text, agent still has to spend tokens parsing it

**Solution:** This skill is a transparent replacement for `web_fetch`. It intercepts URL access and returns clean, structured JSON — letting the agent immediately understand page content without token-heavy parsing.

### Before vs After

**Before (raw web_fetch or screenshot):**
```
User: "What's on pump.fun?"
OpenClaw: *fetches raw HTML* → sends to Claude for parsing
Cost: ~3000 tokens | Time: 8 seconds
```

**After (this skill — transparent, automatic):**
```
User: "What's on pump.fun?"
OpenClaw: *checks EZCTO cache, returns structured JSON*
Cost: 0 tokens (cache hit) | Time: 1 second
```

---

## Quick Start

### Installation

1. **Clone into your OpenClaw skills directory:**
   ```bash
   cd ~/.openclaw/skills
   git clone https://github.com/pearl799/ezcto-web-translator ezcto-smart-web-reader
   ```

2. **Or copy manually:**
   ```bash
   cp -r ezcto-smart-web-reader ~/.openclaw/skills/
   ```

3. **Verify installation:**
   ```bash
   openclaw skills list | grep ezcto-smart-web-reader
   ```

### First Use

```bash
# Start OpenClaw
openclaw

# Just mention any URL — the skill fires automatically
You: What's on pump.fun?

# OpenClaw reads it without you asking
OpenClaw: ✓ Read pump.fun (cache hit, 0 tokens, 1.2s)
         Site type: crypto
         Primary action: Start Trading
         Cached at: ~/.ezcto/cache/abc123.json
```

---

## File Structure

```
ezcto-smart-web-reader/
├── SKILL.md                          ← OpenClaw reads this for workflow
├── README.md                         ← You are here
├── references/
│   ├── translate-prompt.md           ← LLM parsing prompt
│   ├── output-schema.md              ← JSON output specification
│   ├── site-type-detection.md        ← Zero-token site type detection
│   ├── openclaw-integration.md       ← OpenClaw integration guide
│   └── extensions/
│       ├── crypto-fields.md          ← Crypto/Web3 enhanced extraction
│       ├── ecommerce-fields.md       ← E-commerce enhanced extraction
│       └── restaurant-fields.md      ← Restaurant enhanced extraction
└── examples/
    └── openclaw-output-example.json  ← Full output example
```

---

## Key Features

### 1. Transparent URL Interception
- Fires automatically whenever agent needs to access a URL
- No user action required — agent gets structured data, not raw HTML
- Works for any URL: crypto, e-commerce, restaurants, SaaS, blogs, etc.

### 2. Cache-First Strategy
- Checks EZCTO public library first → **0 tokens if cached**
- Local cache at `~/.ezcto/cache/` → Instant repeat access
- Community contributions → Growing cache coverage

### 3. Zero-Token Site Detection
- Auto-detects crypto/ecommerce/restaurant sites via text pattern matching
- No LLM calls for detection — pure regex/string matching
- Loads type-specific extraction rules automatically

### 4. OpenClaw-Native Output
- JSON result wrapped with metadata for skill chaining
- Markdown summary at `~/.ezcto/cache/{hash}.meta.md` for quick reference
- Agent suggestions for next actions and skill combinations

### 5. Smart Error Handling
- Structured error codes: `fetch_failed`, `parse_failed`, `validation_failed`
- Recovery suggestions for each error type
- Never silently fails — always returns actionable feedback

---

## Configuration

### Environment Variables (Optional)

```bash
# Custom cache location (default: ~/.ezcto/cache/)
export EZCTO_CACHE_DIR=~/custom/cache/path

# Custom EZCTO API endpoint (default: https://api.ezcto.fun)
export EZCTO_API_URL=https://custom-api.example.com

# Cache TTL in hours (default: 24)
export EZCTO_CACHE_TTL=48
```

### OpenClaw Tool Dependencies

This skill requires the following OpenClaw tools to be enabled:

```yaml
# In your ~/.openclaw/config.yaml
tools:
  web_fetch: enabled      # Fetch HTML content
  exec: enabled           # Run curl/sha256sum
  filesystem: enabled     # Read/write cache files
```

**Verify tools are enabled:**
```bash
openclaw tools list | grep -E "web_fetch|exec|filesystem"
```

---

## Cost Analysis

| Scenario | Tokens | Time | API Calls | Cost |
|----------|--------|------|-----------|------|
| **Cache hit (EZCTO library)** | 0 | ~1s | 1 (cache check) | $0 |
| **Cache hit (local)** | 0 | <0.5s | 0 | $0 |
| **Cache miss (simple page)** | 500-1000 | ~5s | 1 (LLM) + 1 (cache) | ~$0.003 |
| **Cache miss (complex page)** | 1500-2000 | ~10s | 1 (LLM) + 1 (cache) | ~$0.006 |
| **Screenshot alternative** | 3000+ | ~8s | 1 (Vision) | ~$0.09 |

**Savings:** 80-95% token reduction vs multimodal approaches.

---

## Testing

### Test Suite

```bash
# Test 1: Cache hit (should be instant)
openclaw chat "What's on ezcto.fun?"

# Test 2: Crypto site detection
openclaw chat "Check https://pump.fun"
# Expected: site_type = ["crypto"], extracts contract addresses

# Test 3: E-commerce site
openclaw chat "What does shopify.com offer?"
# Expected: site_type = ["ecommerce"], extracts products

# Test 4: Error handling (invalid URL)
openclaw chat "Look at https://this-does-not-exist-12345.com"
# Expected: Returns structured error with code "fetch_failed"

# Test 5: Large HTML (>500KB)
openclaw chat "Read https://en.wikipedia.org/wiki/Artificial_intelligence"
# Expected: Truncates to <body> only, still succeeds
```

### Verify Cache

```bash
# Check local cache
ls -lh ~/.ezcto/cache/

# Read a cached result (JSON)
cat ~/.ezcto/cache/*.json | jq .

# Read Markdown summary
cat ~/.ezcto/cache/*.meta.md
```

---

## Skill Chaining (Advanced)

### Example 1: Price Tracking
```
User: "Track price of this product: https://amazon.com/dp/B08N5WRWNW"

OpenClaw workflow:
1. ezcto-smart-web-reader → Extract product details
2. price-tracker skill → Monitor price changes
3. email-notifier skill → Alert on price drop
```

### Example 2: Crypto Research
```
User: "Research this token: https://pump.fun/coin/abc123"

OpenClaw workflow:
1. ezcto-smart-web-reader → Extract contract, tokenomics
2. blockchain-explorer skill → Check on-chain data
3. sentiment-analyzer skill → Analyze social mentions
4. markdown-report skill → Generate research report
```

### Example 3: Competitive Analysis
```
User: "Compare these 3 e-commerce sites: [URLs]"

OpenClaw workflow:
1. ezcto-smart-web-reader (3x parallel) → Extract all products
2. product-comparison skill → Generate comparison table
3. chart-generator skill → Visualize pricing
```

---

## Security & Privacy

### What This Skill Does
- Fetches publicly accessible web pages
- Stores parsed results locally in `~/.ezcto/cache/`
- Contributes **non-sensitive** data to EZCTO asset library

### What This Skill Does NOT Do
- Access password-protected sites (no auth bypass)
- Store or transmit API keys, passwords, or PII
- Execute JavaScript or interact with pages (read-only)
- Modify or fabricate URLs in output

### Data Sharing
When you use this skill, **only these data points** are sent to EZCTO API:
1. The URL you asked to read
2. SHA256 hash of the HTML content
3. The structured JSON result

**NOT shared:** Your IP, OpenClaw config, other browsing history.

You can disable asset library contribution by setting:
```bash
export EZCTO_CONTRIBUTE=false
```

---

## Troubleshooting

### Issue: "Tool 'exec' not enabled"
```bash
nano ~/.openclaw/config.yaml
# tools:
#   exec: enabled
```

### Issue: "Cache directory not writable"
```bash
mkdir -p ~/.ezcto/cache
chmod 755 ~/.ezcto/cache
```

### Issue: "Parse validation failed"
**Cause:** LLM returned malformed JSON (rare with Claude)
- Check `~/.openclaw/logs/` for the raw LLM output
- Try again (may be transient LLM issue)
- Report to EZCTO if persistent

### Issue: "EZCTO API timeout"
```bash
# Test API connectivity
curl -s "https://api.ezcto.fun/v1/translate?url=https://ezcto.fun"
# If slow/timeout, skill automatically falls back to local parsing
```

---

## Learn More

- **EZCTO Website:** https://ezcto.fun
- **API Documentation:** https://ezcto.fun/api-docs
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Report Issues:** https://github.com/pearl799/ezcto-web-translator/issues
- **Community Discord:** https://discord.gg/ezcto

---

## License

MIT License — see LICENSE file for details.

---

## Credits

- Built for [OpenClaw](https://openclaw.ai) by [EZCTO Team](https://ezcto.fun)
- Powered by Claude (Anthropic) for LLM-based HTML parsing
- Community contributions welcome!
