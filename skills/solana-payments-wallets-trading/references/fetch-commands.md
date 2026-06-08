# Fetch Commands Reference

## sol fetch

```bash
sol fetch <url> [options]
```

Fetch a URL, automatically paying if the server returns HTTP 402
Payment Required. Works like `curl` — the response body goes to
stdout, payment info goes to stderr, so piped output stays clean.

Supports the [x402 protocol](https://x402.org) (v1 and v2), which
lets servers charge per-request in USDC. The server provides the
fee payer and submits the transaction — your wallet only partially
signs.

### How it works

1. Makes the initial HTTP request
2. If the response is not 402, prints the body and exits
3. On 402, parses payment requirements (amount, recipient, network)
4. Builds a USDC transfer transaction, partially signs it
5. Retries the request with the payment attached in a header
6. Prints the response body to stdout

The CLI handles the version negotiation automatically:
- **v1 servers**: payment goes in the `X-PAYMENT` header
- **v2 servers**: payment goes in the `PAYMENT-SIGNATURE` header
  with the full accepted requirements and resource URL

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-X, --method <method>` | GET (or POST if body given) | HTTP method |
| `-d, --body <data>` | — | Request body (sets method to POST) |
| `-H, --header <header...>` | — | Custom headers, repeatable |
| `--max <amount>` | — | Max USDC to spend (rejects if cost exceeds) |
| `--dry-run` | — | Show payment requirements without paying |
| `--wallet <name>` | default wallet | Wallet to sign payments with |

### Examples

```bash
# Simple GET — auto-pays if 402
sol fetch https://api.example.com/data

# Check the price before paying
sol fetch https://api.example.com/data --dry-run

# Set a spending cap
sol fetch https://api.example.com/data --max 0.05

# POST with JSON body and headers (like curl)
sol fetch https://api.example.com/rpc \
  -X POST \
  -d '{"jsonrpc":"2.0","id":1,"method":"getSlot"}' \
  -H "Content-Type: application/json"

# Multiple headers
sol fetch https://api.example.com/search \
  -H "Accept: application/json" \
  -H "X-Custom: value"

# Non-402 URLs work like curl — just prints the body
sol fetch https://httpbin.org/get

# Pipe to jq (payment info on stderr, body on stdout)
sol fetch https://api.example.com/data | jq .price

# Use a specific wallet
sol fetch https://api.example.com/data --wallet trading
```

### curl flag mapping

| curl | sol fetch | Notes |
|------|-----------|-------|
| `curl <url>` | `sol fetch <url>` | |
| `-X POST` | `-X POST` | Same |
| `-d '{"key":"val"}'` | `-d '{"key":"val"}'` | Same; implies POST |
| `-H "Content-Type: application/json"` | `-H "Content-Type: application/json"` | Same; repeatable |
| `-o file.json` | `sol fetch <url> > file.json` | Redirect stdout |
| `-s` (silent) | `2>/dev/null` | Payment info is on stderr |
| `-v` (verbose) | `--verbose` | Global flag |

Not supported: `-u` (auth), `-F` (multipart), `-L` (redirects),
`-k` (insecure), `-b`/`-c` (cookies). For those, use curl directly.

### Example Output

Dry-run:

```
Payment Required (x402)
  Amount:    $0.001000 USDC
  Recipient: Gzeh...QWa
  Network:   solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp

Run without --dry-run to pay and fetch the resource.
```

Paid:

```
Paid $0.001000 USDC to Gzeh...QWa        # ← stderr
{"solana":{"usd":81.65}}                  # ← stdout
```

Use `--json` for the structured envelope (see json-output-format.md).

### Error codes

| Code | Meaning |
|------|---------|
| `FETCH_FAILED` | Request failed, payment rejected, or spending cap exceeded |

### Spending caps

Use `--max` to set a ceiling in USDC. If the server asks for more
than your cap, the command fails without signing anything:

```bash
$ sol fetch https://api.example.com/expensive --max 0.001
Error: Payment of $0.010000 USDC exceeds --max cap of $0.001 USDC
```

### Permission

Gated by the `canFetch` permission. Set `canFetch = false` in
`~/.sol/config.toml` under `[permissions]` to disable the command
entirely.
