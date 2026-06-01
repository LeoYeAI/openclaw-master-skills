---
name: tpn-proxy
aliases: [tpn, subnet-65, sn65, proxy, socks5]
description: Make web requests through decentralized SOCKS5 proxies via the Tao Private Network (TPN). This skill is also known as "TPN", "TPN proxy", "subnet 65", or "SN65" — if the user asks to "run TPN", "use a proxy", "use TPN to open", or references "subnet 65", this is the skill they mean. Use when the user wants to route HTTP traffic through a proxy, make anonymous web requests, access geo-restricted content, use a decentralized VPN, fetch a URL through a SOCKS5 proxy, or needs residential proxy IPs. Supports both centralised API key authentication and decentralised x402 micropayments.
metadata: { "openclaw": { "emoji": "📡", "requires": { "bins": ["curl"], "env": ["TPN_API_KEY"] }, "primaryEnv": "TPN_API_KEY" } }
---

# TPN Decentralized SOCKS5 Proxy

Route web traffic through Tao Private Network's decentralized SOCKS5 proxies — a Bittensor subnet (SN65) with commercial and residential exit nodes across 80+ countries.

Ask this skill things like:

- Open https://ipv4.icanhazip.com through a proxy in Germany
- Show me a curl command that proxies google.com through a US ip address
- I need a socks5 proxy in Japan for 30 minutes
- Which countries are available on TPN for proxies?

---

## Security Posture

| Aspect | Detail |
|--------|--------|
| Environment variables | `TPN_API_KEY` — existence-checked only (`[ -n "$TPN_API_KEY" ]`), never echoed or logged |
| Files read/written | None |
| Other secrets accessed | None — no signing keys, no credentials beyond `TPN_API_KEY` |
| Network destinations | `api.taoprivatenetwork.com` (API calls) + user-specified URLs (validated per Step 5) |
| x402 signing | Handled entirely by external libraries (`@x402/*`); this skill provides endpoint URLs only |

---

## This is an action skill

This skill executes API calls and returns results directly — it does not output documentation or instructions for the user to follow.

**Expected behaviour:**

- Call the TPN API yourself (via `curl` or equivalent) and return the full proxy credentials to the user.
- When the user asks you to fetch a URL through a proxy, make that request yourself too.
- Show the full SOCKS5 credentials (username, password, host, port) — these are short-lived and scoped to the proxy lease.
- The only time you should show the user how to call the API is when they explicitly ask "how do I do this myself?" or similar.
- If no API key exists, guide the user through account setup — that's the one step only they can do.

**A good check:** if your response contains "you can run this command to…" or "use this curl to generate…", reconsider — the user invoked this skill expecting you to run the command and hand them the output.

---

## Step-by-Step Procedure

Follow this procedure every time the user requests a proxy or asks you to fetch something through a proxy.

### Security: Input validation (mandatory)

Before constructing any shell command, **validate every user-provided value**. Never interpolate raw user input into shell commands.

| Input              | Validation rule                                                                                     |
|--------------------|------------------------------------------------------------------------------------------------------|
| `geo`              | Must be exactly 2 uppercase ASCII letters (ISO 3166-1 alpha-2). Reject anything else.                |
| `minutes`          | Must be a positive integer between 1 and 1440. Reject non-numeric or out-of-range values.            |
| `connection_type`  | Must be one of: `any`, `datacenter`, `residential`. Reject anything else.                            |
| `format`           | Must be one of: `text`, `json`. Reject anything else.                                                |
| URLs (for Step 5)  | Must start with `http://` or `https://`, contain no shell metacharacters (`` ` `` `$` `(` `)` `;` `&` `|` `<` `>` `\n`), and be a well-formed URL. |

**Rules:**

- **Never** interpolate raw user input directly into shell commands. Always validate first.
- **Never** construct `-d` JSON payloads via string concatenation with user input. Use a safe static template and only insert validated values.
- When using `curl`, always **quote** the URL and proxy URI arguments.
- Prefer using the agent's built-in HTTP tools (e.g. `WebFetch`) for fetching user-specified URLs rather than constructing `curl` commands.

### Step 1: Resolve the API key

Check whether `$TPN_API_KEY` is set in the environment (OpenClaw injects this automatically from your config):

1. Test the variable: `[ -n "$TPN_API_KEY" ] && echo "API key is set" || echo "API key is not set"` — **never** echo, log, or display the key value itself.
2. If not set → check if the user can pay via [x402](https://www.x402.org) (no API key needed), otherwise guide them through account setup (see the "Set up TPN" example)

### Step 2: Choose response format

| Situation | Use `format` | Why |
|-----------|--------------|-----|
| Just need a working proxy URI | `text` (default) | No parsing needed |
| Need to show structured host/port/user/pass breakdown | `json` | Gives individual fields |
| Not sure | `text` | Simpler, fewer things to break |

If you choose `json`, parse the response with `jq`:

```bash
curl -s ... | jq -r '.vpnConfig.username'
```

If `jq` is not available, use `format=text` instead — it returns a plain `socks5://` URI that needs no parsing.

> **Do not** use `python -c`, `grep`, `cut`, or other shell-based JSON parsing fallbacks. These patterns risk shell injection when combined with dynamic inputs. Stick to `jq` or `format=text`.

### Step 3: Generate the proxy

```bash
curl -s -X POST https://api.taoprivatenetwork.com/api/v1/proxy/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $TPN_API_KEY" \
  -d '{"minutes": 60, "format": "text", "connection_type": "any"}'
```

Map the user's request to these parameters:

| Field             | Type    | Required | Default | Description                                    |
|-------------------|---------|----------|---------|------------------------------------------------|
| `minutes`         | integer | yes      | —       | Lease duration (1–1440). Default to 60 if not specified. |
| `geo`             | string  | no       | any     | ISO country code (e.g. `"US"`, `"DE"`, `"JP"`) |
| `format`          | string  | no       | `text`  | `"text"` for URI string, `"json"` for object   |
| `connection_type` | string  | no       | `any`   | `"any"`, `"datacenter"`, or `"residential"`    |

> **Safe JSON body construction:** Always build the `-d` JSON payload as a static single-quoted string with only validated values inserted. Validate `geo` (2 uppercase letters), `minutes` (integer 1–1440), `connection_type` (enum), and `format` (enum) per the validation rules above **before** constructing the curl command. Never concatenate raw user input into the JSON body or any part of the command.

### Step 4: Present the result

Show the **full proxy credentials** so the user can immediately connect. These are temporary (scoped to the lease duration) and safe to display in context. Use the `socks5h://` scheme (with `h`) to ensure DNS resolves through the proxy — this protects user DNS privacy. (When the agent fetches URLs in Step 5, it uses `socks5://` instead — see Step 5.) Include:

- Structured config block (host, port, username, password, scheme, expiry)
- Full `socks5h://` URI
- A ready-to-paste `curl` example when relevant

### Step 5: If the user asked you to fetch a URL

After generating the proxy, make the request yourself. Use `socks5://` (not `socks5h://`) so DNS resolves locally — the validated IP is the connected IP.

**Use the agent's built-in HTTP tools** (e.g. `WebFetch`) to fetch the URL through the proxy. This is the preferred method — it avoids shell command construction entirely.

**URL validation — every check must pass before fetching:**

1. Scheme must be `http://` or `https://`
2. No shell metacharacters: `` ` `` `$` `(` `)` `;` `&` `|` `<` `>` newlines
3. Domain names only — reject raw IP addresses (IPv4 or IPv6)
4. Reject internal hostnames: `*.internal`, `*.local`, `*.localhost`, `*.localdomain`, `*.corp`, `*.lan`, `metadata.*`, single-label hostnames
5. Hostname must resolve via local DNS — reject unresolvable hostnames
6. Resolved IP must be publicly routable — reject `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`, `fd00::/8`, `169.254.169.254`

**Fallback — curl** (only if WebFetch is unavailable). Always double-quote the URL and proxy URI:

```bash
curl --proxy "socks5://username:password@ip:port" \
  --connect-timeout 10 --max-time 30 \
  "https://validated-target-url.com"
```

Return the response content to the user — the goal is a complete answer, not a proxy they still need to use themselves.

---

## Examples

These show exactly what users ask and what you should respond. Study these — they are the gold standard.

---

**User:** "Give me a socks5 config for Belgium"

**You:** *(generate a BE proxy yourself, then respond:)*

> Here's your Belgian SOCKS5 proxy (valid 60 minutes):
>
> ```
> Host:     185.42.170.3
> Port:     1080
> Username: u_0CKaBqdE
> Password: p_sT6yM3zabqRuhqrahzGOl4i4RTEDgQ7V
> Scheme:   socks5h
> Expires:  2026-02-16T15:30:00Z
> ```
>
> **Full URI:** `socks5h://u_0CKaBqdE:p_sT6yM3zabqRuhqrahzGOl4i4RTEDgQ7V@185.42.170.3:1080`
>
> **curl example:**
>
> ```bash
> curl --proxy socks5h://u_0CKaBqdE:p_sT6yM3zabqRuhqrahzGOl4i4RTEDgQ7V@185.42.170.3:1080 \
>   --connect-timeout 10 --max-time 30 \
>   https://ipv4.icanhazip.com
> ```
>
> This should return a Belgian IP. The proxy expires in 60 minutes — let me know if you need a longer lease.

---

**User:** "Show me a curl command that proxies over Germany"

**You:** *(generate a DE proxy yourself, then respond:)*

> Here's a curl command routed through a German proxy:
>
> ```bash
> curl --proxy socks5h://u_0E4k7kJ6:p_z2HsXTEXJHYiobwCcfOaU1YMS1tg3m0i@5.39.255.64:1080 \
>   --connect-timeout 10 --max-time 30 \
>   https://example.com
> ```
>
> Replace `https://example.com` with your target URL. This proxy expires at 2026-02-16T14:47:20Z.

---

**User:** "Call icanhazip.com from the Netherlands"

**You:** *(generate an NL proxy yourself, fetch icanhazip.com through it, then respond:)*

> I fetched `https://ipv4.icanhazip.com` through a Dutch proxy. The response:
>
> ```
> 82.148.30.91
> ```
>
> That's the exit IP in the Netherlands. The proxy is still active until 2026-02-16T15:12:00Z if you need more requests.

---

**User:** "I need a residential US proxy for 2 hours"

**You:** *(generate a US residential proxy with minutes=120, then respond:)*

> Here's your US residential proxy (valid 2 hours, 25 credits):
>
> ```
> Host:     68.210.185.149
> Port:     1080
> Username: u_02NyffuT
> Password: p_CIYLqgIyLZ1rSvZGQbdh3lyxQQBcBsQn
> Scheme:   socks5h
> Type:     residential
> Expires:  2026-02-16T16:41:00Z
> ```
>
> **Full URI:** `socks5h://u_02NyffuT:p_CIYLqgIyLZ1rSvZGQbdh3lyxQQBcBsQn@68.210.185.149:1080`
>
> Residential IPs are less likely to be blocked. Let me know if you need a different country.

---

**User:** "How many credits do I have left?"

**You:** *(call `GET /api/v1/user/balance` yourself, then respond:)*

> You have **74 credits** remaining.
>
> For reference, a 60-minute proxy costs 20 credits and a 10-minute proxy costs 10 credits. You can buy more at https://api.taoprivatenetwork.com — packages start at 1,000 credits for $9.99.

---

**User:** "Use a proxy to check if my site looks right from Germany"

**You:** *(generate a DE proxy, fetch their site through it, then respond:)*

> I fetched your site through a German proxy (IP: `91.203.50.12`):
>
> - **Status:** 200 OK
> - **Content-Language:** `de` — looks like your site detected the German IP and served the German version
> - **Page title:** "Willkommen bei Example"
>
> Everything seems to be working correctly for German visitors. Want me to check from another country?

---

**User:** "Set up TPN" / "How do I get started with TPN?"

**You:** *(check if a key already exists — if yes, tell them they're set up; if no:)*

> To get started with TPN:
>
> 1. Go to https://api.taoprivatenetwork.com and create an account
> 2. From the dashboard, create an API key (it'll look like `tpn-abc123...`)
> 3. Your first key comes with **100 free credits** — enough for about 5 one-hour proxies
>
> Once you have the key, share it with me and I'll save it for future sessions. Then I can generate proxies for you anytime.

---

The pattern: **the user asks, you act, you return results.** You never tell the user how to call the API — you call it yourself and hand them the output.

---

## API Reference

**Base URL:** `https://api.taoprivatenetwork.com`

**Authentication:** Pass `X-API-Key: <your-key>` as a request header. Not `Authorization: Bearer`.

### Endpoints

| Method | Path                          | Auth       | Description                     |
|--------|-------------------------------|------------|---------------------------------|
| POST   | `/api/v1/proxy/generate`      | API key    | Generate SOCKS5 proxy           |
| POST   | `/api/v1/vpn/generate`        | API key    | Generate WireGuard VPN          |
| GET    | `/api/v1/user/balance`        | API key    | Check credit balance            |
| GET    | `/api/v1/vpn/countries`       | none       | List available countries        |
| POST   | `/api/v1/vpn/cost`            | none       | Calculate credit cost           |
| GET    | `/api/v1/vpn/stats`           | none       | Network statistics              |
| GET    | `/api/v1/health`              | none       | Health check                    |
| POST   | `/api/v1/x402/proxy/generate` | x402       | Generate SOCKS5 proxy (x402)    |
| POST   | `/api/v1/x402/vpn/generate`   | x402       | Generate WireGuard VPN (x402)   |

### Response shapes

**`/proxy/generate` with `format=text`:**

```json
{
  "success": true,
  "vpnConfig": "socks5://u_02NyffuT:p_CIYLqgIyLZ1rSvZGQbdh3lyxQQBcBsQn@9.160.73.2:1080",
  "minutes": 60,
  "expiresAt": "2026-02-14T19:08:25.690Z",
  "creditsUsed": 20,
  "type": "socks5"
}
```

**`/proxy/generate` with `format=json`:**

```json
{
  "success": true,
  "vpnConfig": {
    "username": "u_0CKaBqdE",
    "password": "p_sT6yM3zabqRuhqrahzGOl4i4RTEDgQ7V",
    "ip_address": "68.210.185.149",
    "port": 1080
  },
  "minutes": 60,
  "expiresAt": "2026-02-14T19:08:23.958Z",
  "creditsUsed": 20,
  "usedFallback": false,
  "type": "socks5",
  "connection_type": "any"
}
```

### `/vpn/countries` query parameters

| Param             | Type   | Default | Description                                      |
|-------------------|--------|---------|--------------------------------------------------|
| `format`          | string | `json`  | `"json"` for array, `"text"` for newline-separated |
| `type`            | string | `code`  | `"code"` for ISO codes, `"name"` for full names   |
| `connection_type` | string | `any`   | `"any"`, `"datacenter"`, or `"residential"`       |

### Using the proxy (for user-facing code examples)

Only show these if the user explicitly asks "how do I use this in my code?" — otherwise just hand them the config.

> **User-facing code should always use `socks5h://`** (with `h`) to resolve DNS through the proxy, preserving DNS privacy. (The agent uses `socks5://` for its own fetching in Step 5, where local DNS resolution is a security feature — see Step 5.)

> If proxy credentials contain special characters (`@`, `:`, `/`, `#`, `?`), percent-encode them (e.g. `p@ss` → `p%40ss`).

**curl:**

```bash
curl --proxy socks5h://username:password@ip_address:port \
  --connect-timeout 10 --max-time 30 \
  https://ipv4.icanhazip.com
```

**Node.js:**

```js
import { SocksProxyAgent } from 'socks-proxy-agent'
import fetch from 'node-fetch'

const agent = new SocksProxyAgent( 'socks5h://username:password@ip_address:1080' )
const controller = new AbortController()
const timeout = setTimeout( () => controller.abort(), 30_000 )

const response = await fetch( 'https://ipv4.icanhazip.com', { agent, signal: controller.signal } )
clearTimeout( timeout )
console.log( await response.text() )
```

**Python:**

```python
import requests

proxies = {
    'http': 'socks5h://username:password@ip_address:1080',
    'https': 'socks5h://username:password@ip_address:1080'
}

response = requests.get( 'https://ipv4.icanhazip.com', proxies=proxies, timeout=( 10, 30 ) )
print( response.text )
```

See `{baseDir}/references/api-examples.md` for end-to-end examples (generate + use) in curl, JS, Node.js, and Python.

---

## Credit Costs

Formula: `credits = ceil( 4.1 × minutes ^ 0.375 )`

| Duration | Credits |
|----------|---------|
| 1 min    | 5       |
| 5 min    | 8       |
| 10 min   | 10      |
| 30 min   | 15      |
| 60 min   | 20      |
| 120 min  | 25      |
| 720 min  | 49      |
| 1440 min | 63      |

Use `POST /api/v1/vpn/cost` with `{"minutes": N}` to calculate before purchasing.

Credit packages: Starter 1,000/$9.99 · Pro 5,000/$49.99 · Premium 20,000/$199.99

---

## Troubleshooting & Operational Notes

| Problem                   | Solution                                                       |
|---------------------------|----------------------------------------------------------------|
| `401 Unauthorized`        | Verify API key is valid — use `X-API-Key` header, not Bearer   |
| `402 Payment Required`    | Insufficient credits — buy more or use the x402 flow           |
| `503 Service Unavailable` | No miners available — credits are refunded, retry later        |
| Connection timeout        | Proxy lease may have expired — generate a new one              |
| DNS not resolving (user)  | Use `socks5h://` (with `h`) for remote DNS resolution          |
| DNS not resolving (agent) | Agent uses `socks5://` — verify local DNS resolution in check 5 |

**Operational rules:**

- User-facing credentials and code examples: always use `socks5h://` for DNS privacy
- Agent-side fetching (Step 5): always use `socks5://` so local DNS validation is authoritative
- Check credit balance with `GET /api/v1/user/balance` before generating proxies in bulk
- Proxy leases expire at `expiresAt` — never cache or reuse credentials beyond that time
- If a `503` occurs, credits are refunded automatically — retry after a short delay

---

## x402 Payment Flow (Advanced)

The [x402 protocol](https://www.x402.org) enables pay-per-request access using USDC on Base. No account or API key needed — ideal for autonomous agents that already support x402.

If you are an x402-capable agent, you already know how to handle the payment handshake. The TPN x402 endpoints follow the standard protocol:

1. `POST /api/v1/x402/proxy/generate` — returns `HTTP 402` with a standard `payment-required` header
2. Complete the x402 payment flow per the [protocol specification](https://www.x402.org)
3. Retry with the payment header to receive SOCKS5 credentials

Same request body as the centralised endpoint. No `X-API-Key` needed.

See `{baseDir}/references/x402-examples.md` for curl and browser JS examples, and the [x402 spec](https://www.x402.org) for full protocol details. Signing is handled entirely by external libraries — this skill provides endpoint URLs only.

---

## Links

- Dashboard & Account: https://api.taoprivatenetwork.com
- API Docs: https://api.taoprivatenetwork.com/docs/getting-started/
- Swagger UI: https://api.taoprivatenetwork.com/api-docs/
- OpenAPI Spec: https://api.taoprivatenetwork.com/api-docs/openapi.json
- LLM-friendly docs: https://api.taoprivatenetwork.com/docs/llms-full.txt
- x402 Protocol: https://www.x402.org
