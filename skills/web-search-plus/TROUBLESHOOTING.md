# Troubleshooting Guide

## Caching Issues (v2.7.0+)

### Cache not working / always fetching fresh

**Symptoms:**
- Every request hits the API
- `"cached": false` even for repeated queries

**Solutions:**
1. Check cache directory exists and is writable:
   ```bash
   ls -la .cache/  # Should exist in skill directory
   ```
2. Verify `--no-cache` isn't being passed
3. Check disk space isn't full
4. Ensure query is EXACTLY the same (including provider and max_results)

### Stale results from cache

**Symptoms:**
- Getting outdated information
- Cache TTL seems too long

**Solutions:**
1. Use `--no-cache` to force fresh results
2. Reduce TTL: `--cache-ttl 1800` (30 minutes)
3. Clear cache: `python3 scripts/search.py --clear-cache`

### Cache growing too large

**Symptoms:**
- Disk space filling up
- Many .json files in `.cache/`

**Solutions:**
1. Clear cache periodically:
   ```bash
   python3 scripts/search.py --clear-cache
   ```
2. Set up a cron job to clear weekly
3. Use a smaller TTL so entries expire faster

### "Permission denied" when caching

**Symptoms:**
- Cache write errors in stderr
- Searches work but don't cache

**Solutions:**
1. Check directory permissions: `chmod 755 .cache/`
2. Use custom cache dir: `export WSP_CACHE_DIR="/tmp/wsp-cache"`

---

## Common Issues

### "No API key found" error

**Symptoms:**
```
Error: No API key found for serper
```

**Solutions:**
1. Check `.env` exists in skill folder with `export VAR=value` format
2. Keys auto-load from skill's `.env` since v2.2.0
3. Or set in system environment: `export SERPER_API_KEY="..."`
4. Verify key format in config.json:
   ```json
   { "serper": { "api_key": "your-key" } }
   ```

**Priority order:** config.json > .env > environment variable

---

### Getting empty results

**Symptoms:**
- Search returns no results
- `"results": []` in JSON output

**Solutions:**
1. Check API key is valid (try the provider's web dashboard)
2. Try a different provider with `-p`
3. Some queries have no results (very niche topics)
4. Check if provider is rate-limited
5. Verify internet connectivity

**Debug:**
```bash
python3 scripts/search.py -q "test query" --verbose
```

---

### Rate limited

**Symptoms:**
```
Error: 429 Too Many Requests
Error: Rate limit exceeded
```

**Good news:** Since v2.2.5, automatic fallback kicks in! If one provider hits rate limits, the script automatically tries the next provider.

**Solutions:**
1. Wait for rate limit to reset (usually 1 hour or end of day)
2. Use a different provider: `-p tavily` instead of `-p serper`
3. Check free tier limits:
   - Serper: 2,500 free total
   - Tavily: 1,000/month free
   - Exa: 1,000/month free
4. Upgrade to paid tier for higher limits
5. Use SearXNG (self-hosted, unlimited)

**Fallback info:** Response will include `routing.fallback_used: true` when fallback was used.

---

### SearXNG: "403 Forbidden"

**Symptoms:**
```
Error: 403 Forbidden
Error: JSON format not allowed
```

**Cause:** Most public SearXNG instances disable JSON API to prevent bot abuse.

**Solution:** Self-host your own instance:
```bash
docker run -d -p 8080:8080 searxng/searxng
```

Then enable JSON in `settings.yml`:
```yaml
search:
  formats:
    - html
    - json  # Add this!
```

Restart the container and update your config:
```json
{
  "searxng": {
    "instance_url": "http://localhost:8080"
  }
}
```

---

### SearXNG: Slow responses

**Symptoms:**
- SearXNG takes 2-5 seconds
- Other providers are faster

**Explanation:** This is expected behavior. SearXNG queries 70+ upstream engines in parallel, which takes longer than direct API calls.

**Trade-off:** Slower but privacy-preserving + multi-source + $0 cost.

**Solutions:**
1. Accept the trade-off for privacy benefits
2. Limit engines for faster results:
   ```bash
   python3 scripts/search.py -p searxng -q "query" --engines "google,bing"
   ```
3. Use SearXNG as fallback (put last in priority list)

---

### Auto-routing picks wrong provider

**Symptoms:**
- Query about research goes to Serper
- Query about shopping goes to Tavily

**Debug:**
```bash
python3 scripts/search.py --explain-routing -q "your query"
```

This shows the full analysis:
```json
{
  "query": "how much does iPhone 16 Pro cost",
  "routing_decision": {
    "provider": "serper",
    "confidence": 0.68,
    "reason": "moderate_confidence_match"
  },
  "scores": {"serper": 7.0, "tavily": 0.0, "exa": 0.0},
  "top_signals": [
    {"matched": "how much", "weight": 4.0},
    {"matched": "brand + product detected", "weight": 3.0}
  ]
}
```

**Solutions:**
1. Override with explicit provider: `-p tavily`
2. Rephrase query to be more explicit about intent
3. Adjust `confidence_threshold` in config.json (default: 0.3)

---

### Config not loading

**Symptoms:**
- Changes to config.json not applied
- Using default values instead

**Solutions:**
1. Check JSON syntax (use a validator)
2. Ensure file is in skill directory: `/path/to/skills/web-search-plus/config.json`
3. Check file permissions
4. Run setup wizard to regenerate:
   ```bash
   python3 scripts/setup.py --reset
   ```

**Validate JSON:**
```bash
python3 -m json.tool config.json
```

---

### Python dependencies missing

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip3 install requests
```

Or install all dependencies:
```bash
pip3 install -r requirements.txt
```

---

### Timeout errors

**Symptoms:**
```
Error: Request timeout after 30s
```

**Causes:**
- Slow network connection
- Provider API issues
- SearXNG instance overloaded

**Solutions:**
1. Try again (temporary issue)
2. Switch provider: `-p serper`
3. Check your internet connection
4. If using SearXNG, check instance health

---

### Duplicate results

**Symptoms:**
- Same result appears multiple times
- Results overlap between providers

**Solution:** This is expected when using auto-fallback or multiple providers. The skill doesn't deduplicate across providers.

For single-provider results:
```bash
python3 scripts/search.py -p serper -q "query"
```

---

## Debug Mode

For detailed debugging:

```bash
# Verbose output
python3 scripts/search.py -q "query" --verbose

# Show routing decision
python3 scripts/search.py -q "query" --explain-routing

# Dry run (no actual search)
python3 scripts/search.py -q "query" --dry-run

# Test specific provider
python3 scripts/search.py -p tavily -q "query" --verbose
```

---

## Getting Help

**Still stuck?**

1. Check the full documentation in `README.md`
2. Run the setup wizard: `python3 scripts/setup.py`
3. Review `FAQ.md` for common questions
4. Open an issue: https://github.com/robbyczgw-cla/web-search-plus/issues
