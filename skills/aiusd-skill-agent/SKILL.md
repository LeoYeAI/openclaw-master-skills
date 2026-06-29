---
name: aiusd-skill
description: "AIUSD trading and account management skill for cryptocurrency trading and account management."
license: MIT
---

# AIUSD Skill (Agent Reference)

This skill calls the AIUSD backend via MCP. Auth is resolved in order: env `MCP_HUB_TOKEN`, mcporter OAuth, or local `~/.mcp-hub/token.json`. Ensure a valid Bearer token is available before calling. **Before invoking the CLI**, read **Common Pitfalls and Solutions** to avoid parameter, escaping, and intent mistakes.

## ⚠️ Agent Output Guidelines

**CRITICAL - ABSOLUTELY FORBIDDEN PHRASES**:
Agents must NEVER use these words or phrases when responding to users:

**TEMPLATE-RELATED (COMPLETELY BANNED)**:
- "template" (any form: template, templates)
- "example" (when referring to trading examples: Example 1, Example 12, etc.)
- "pattern" (when referring to trading patterns)
- "using template", "get template", "trading template", "buy template"
- "use Example [number]", "based on template", "following template"

**VERIFICATION-RELATED (COMPLETELY BANNED)**:
- "skill verification", "verification"

**WHAT TO SAY INSTEAD**:
- Instead of "using template": say "executing the trade" or "placing the order"
- Instead of "get template": say "preparing the trade" or "setting up the order"
- Instead of "Example 12 template": say "the trade configuration" or simply describe the action

**ZERO TOLERANCE**: Any use of the word "template" in trading contexts is STRICTLY PROHIBITED.

**Authentication Response Guidelines**:
**CRITICAL**: When users request re-authentication, respond ONLY with:
- "The browser window should have opened for you"
- "If it didn't open automatically, please tell the agent to re-login again (or type 'reauth' again)"
- "After completing authentication, you can check your account balance or wallet status in chat"

**NEVER return the login URL to the user**: Do NOT ever show or tell the user `https://mcp.alpha.dev/oauth/login`. If the browser did not open, do NOT give them the URL—only tell them to ask the agent to re-login / type 'reauth' again.

**STRICTLY FORBIDDEN**:
- Do NOT include or mention the login URL (e.g. mcp.alpha.dev/oauth/login) in your response to the user
- Do NOT include numbered steps like "1. Open page: [URL]", "2. Connect wallet", etc.
- Do NOT mention any specific auth/login URLs in the response
- Do NOT say "waiting for authentication completion" or similar waiting phrases
- Do NOT provide detailed step-by-step browser instructions
- Do NOT create bulleted lists of authentication steps
- Do NOT say phrases like "browser has been opened for you", "please complete the following steps in browser"
- Simply guide them to the browser and, if it didn't open, only say to re-login / type reauth again

Use natural, direct language to describe trading operations and system status. Simply describe what the trade will do without referencing templates or examples.

## Important URLs

- **Login/Auth**: `https://mcp.alpha.dev/oauth/login` - Only for getting authentication token
- **Official Website**: `https://aiusd.ai` - For trading operations, recharge, troubleshooting, and all user interactions

## Common Pitfalls and Solutions

**Read this before invoking the skill CLI** (e.g. when using the installed skill via `aiusd-skill` or `node dist/index.js`). These prevent the most frequent failures.

### 1. CLI parameter passing

- **Wrong**: `node dist/index.js call genalpha_execute_intent '{"intent": "..."}'` (positional JSON)
- **Right**: `node dist/index.js call genalpha_execute_intent --params '{"intent": "..."}'`
- The CLI expects JSON via the **`--params`** flag, not as a positional argument.

### 2. Passing JSON from code (shell escaping)

- **Problem**: Complex XML inside JSON is hard to escape correctly in shell.
- **Solution**: When invoking the CLI from code, use **spawn** (not `execSync`) and pass params as a single string to avoid shell interpretation:
  - `args = ['dist/index.js', 'call', toolName, '--params', JSON.stringify(params)]`
  - `spawn('node', args, { stdio: 'pipe' })`

### 3. Intent XML semantics (`genalpha_execute_intent`)

- **`<buy>`**: `amount` = amount of **QUOTE** token to spend.
- **`<sell>`**: `amount` = amount of **BASE** token to sell.
- **AIUSD constraint**: AIUSD can only be converted to stablecoins (USDC/USDT/USD1). To buy a non-stable (e.g. SOL): first convert AIUSD→USDC, then USDC→target token.
- **Selling AIUSD**: use `<buy>` with `<quote>AIUSD</quote>` and `<base>USDC_ADDRESS</base>` (you are “buying” USDC with AIUSD).
- **Buying a token**: use `<buy>` with `<quote>USDC_ADDRESS</quote>` and `<base>TOKEN_SYMBOL</base>`; `amount` is the USDC amount to spend.

### 4. Code references (if extending or debugging the skill)

- **MCP client**: Import **`MCPClient`** (capital C), not `McpClient`.
- **TokenManager**: Use **`TokenManager.getToken()`** (static method), not `new TokenManager(); tokenManager.getToken()`.

### 5. Error handling

- On tool failure, **check parameters against the latest `tools --detailed` output** before retrying. Do not retry with the same payload blindly.
- Always obtain and use the live schema from `tools --detailed`; do not rely on static examples in docs.

### 6. Debugging commands

```bash
# Current tool schemas and examples
node dist/index.js tools --detailed
# Or after install: aiusd-skill tools --detailed

# Test connection
node dist/index.js test

# Quick balance check
node dist/index.js balances

# Transaction history
node dist/index.js call genalpha_get_transactions --params '{}'
```

### 7. Common error messages

| Message | Meaning / action |
|--------|-------------------|
| `Missing or invalid 'intent' parameter` | Check JSON structure and that `intent` is present and valid; compare with `tools --detailed`. |
| `insufficient liquidity` | Token may have no/low liquidity on that chain; try another chain or token. |
| `Jwt is missing` / 401 | Auth issue; run reauth (e.g. `npm run reauth` or installer’s reauth command). |

## Installation Pitfalls and Solutions

**For installers and users setting up the skill.** Auth setup is the most error-prone step; prefer a one-click reauth script when available.

### 1. CLI / hub install not finding the skill

- **Problem**: `clawdbot install aiusd-skill-agent` or install by repo path reports "Skill not found".
- **Workaround**: Manual download, then unzip:
  ```bash
  curl -L "https://auth.clawdhub.com/api/v1/download?slug=aiusd-skill-agent" -o aiusd-skill.zip
  unzip aiusd-skill.zip
  ```

### 2. Security scan warnings

- **Possible**: VirusTotal / OpenClaw may flag "Suspicious" (e.g. undeclared auth dependencies or installer code).
- **Recommendation**: Review the code and use an official or trusted source before continuing.

### 3. Dependency install timeout or failure

- **Problem**: `npm install` times out or fails (network, conflicts).
- **Solution**:
  ```bash
  rm -rf node_modules package-lock.json
  npm cache clean --force
  npm install
  ```

### 4. TypeScript / build failures

- **Problem**: Build errors such as "Cannot find module 'commander'" or "Cannot find name 'process'".
- **Solution**: Install full dev dependencies and Node types:
  ```bash
  npm install --include=dev
  # or
  npm install @types/node --save-dev
  ```

### 5. Auth setup (mcporter, OAuth, ports)

- **Problems**: mcporter config, OAuth timeout, or port conflicts.
- **Recommended flow**: Install → build → ensure mcporter → run reauth once:
  ```bash
  cd aiusd-skill
  npm install && npm run build
  which mcporter || npm install -g mcporter
  npm run reauth
  ```
  Or: `npx mcporter auth https://mcp.alpha.dev/api/mcp-hub/mcp`. Prefer the project’s **one-click reauth script** when provided.

### 6. OAuth callback / browser not opening

- **Problems**: Default callback port in use, browser does not open.
- **Solutions**: Check port usage (e.g. `lsof -i :59589`), or run reauth again; if the environment supports it, use a different port via `PORT=59589 npm run reauth`. Do **not** give users the login URL; tell them to run reauth again or use the one-click auth script.

### 7. Auth file locations and full reset

- **Auth state** may live in: `~/.mcporter/credentials.json`, `~/.mcp-hub/token.json`, or env `MCP_HUB_TOKEN`.
- **Full auth reset**:
  ```bash
  rm -rf ~/.mcporter ~/.mcp-hub
  unset MCP_HUB_TOKEN
  npm run reauth
  ```

### 8. Module export name (when extending the skill)

- **Problem**: `import { McpClient } from '...'` fails (no export named `McpClient`).
- **Fix**: Use **`MCPClient`** (capital C). See Common Pitfalls §4.

### 9. Post-install verification

- **Problem**: `npm test` or first tool call fails with "Jwt is missing" or auth errors.
- **Checklist**:
  1. Download/unzip (or install via supported method).
  2. `npm install` (postinstall runs if configured).
  3. `npm run build`; confirm `dist/` exists.
  4. `npm run reauth` and complete OAuth in the browser.
  5. `node dist/index.js balances` (or `aiusd-skill balances`).
  6. `node dist/index.js tools --detailed` to confirm tool list.

### 10. Debug and network checks

```bash
# Verbose reauth
DEBUG=* npm run reauth

# Reachability
curl -I https://mcp.alpha.dev/api/mcp-hub/mcp

# Check mcporter credential file exists
node -e "console.log(require('fs').existsSync(require('os').homedir() + '/.mcporter/credentials.json'))"
```

### 11. Common error codes (install/runtime)

| Code | Meaning / action |
|------|-------------------|
| ENOTFOUND | Network/DNS; check connectivity. |
| ECONNREFUSED | Service unreachable; retry or check URL. |
| ETIMEDOUT | OAuth or network timeout; retry `npm run reauth`. |
| Permission denied | Check file/dir permissions (e.g. `~/.mcporter`, `~/.mcp-hub`). |

## Tool Overview

**CRITICAL**: Always run `aiusd-skill tools --detailed` FIRST to get the current live schema and available tools before making any calls. Tool parameters and available tools may change.

| Tool | Purpose | Typical user intents |
|------|---------|----------------------|
| genalpha_get_balances | Query account balances | balance, how much, account balance |
| genalpha_get_trading_accounts | Get trading accounts / addresses | my account, trading account, wallet address |
| genalpha_execute_intent | Execute trade intent (buy/sell/swap) | buy, sell, buy SOL with USDC, swap |
| genalpha_stake_aiusd | Stake AIUSD | stake, stake AIUSD |
| genalpha_unstake_aiusd | Unstake | unstake |
| genalpha_withdraw_to_wallet | Withdraw to external wallet | withdraw, transfer out |
| genalpha_ensure_gas | Top up Gas for on-chain account | top up gas, ensure gas |
| genalpha_get_transactions | Query transaction history | history, recent transactions |
| recharge / top up | Guide user to recharge account | recharge, top up, deposit, add funds |
| reauth / login | Re-authenticate / login | login, re-login, auth expired, 401 |

**NOTE**: This list shows commonly available tools. NEW TOOLS may be added. Always check `tools --detailed` to discover any additional tools that may better serve the user's specific intent.

## Tool Reference and Call Usage

**MANDATORY**: Before calling ANY tool, run `aiusd-skill tools --detailed` to get current parameters, examples, and any new tools.

### genalpha_get_balances

- **Purpose**: Return user AIUSD custody and staking account balances.
- **When to use**: User asks for balance, how much, account assets.
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_get_trading_accounts

- **Purpose**: Return user trading accounts (addresses, etc.) per chain.
- **When to use**: User asks "my account", "trading account", "wallet address".
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_execute_intent

- **Purpose**: Execute buy/sell/swap (e.g. buy SOL with USDC, sell ETH).
- **When to use**: User clearly wants to place order, buy, sell, swap.
- **Parameters**: Check `tools --detailed` for current schema and XML examples.
- **IMPORTANT**: Intent format may change. Always use examples from live schema.

### genalpha_stake_aiusd

- **Purpose**: Stake AIUSD for yield (e.g. sAIUSD).
- **When to use**: User says stake, stake AIUSD.
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_unstake_aiusd

- **Purpose**: Unstake AIUSD (e.g. redeem sAIUSD).
- **When to use**: User says unstake, redeem.
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_withdraw_to_wallet

- **Purpose**: Withdraw stablecoin (e.g. USDC) to user-specified external wallet address.
- **When to use**: User says withdraw, transfer out.
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_ensure_gas

- **Purpose**: Top up native Gas for user trading account on a given chain.
- **When to use**: User says top up gas, ensure gas, or chain has low gas.
- **Parameters**: Check `tools --detailed` for current schema.

### genalpha_get_transactions

- **Purpose**: Return user transaction history (list, may include status).
- **When to use**: User asks history, recent transactions, order status.
- **Parameters**: Check `tools --detailed` for current schema and filtering options.

### recharge / top up

- **Purpose**: Guide user to recharge their AIUSD account with funds.
- **When to use**: User asks to recharge, top up, deposit, or add funds to their account.
- **Response Options**:
  - **Option 1 - Direct deposit**: Only USDC stablecoins accepted. Other stablecoins must use official website.
  - **Option 2 - Official website**: https://aiusd.ai (supports all tokens, login with same wallet)
- **Important**: For direct deposits, only send USDC to the provided addresses. For other stablecoins (USDT, DAI, etc.), user must use the official website.
- **Example response**: "For recharge, you have two options: 1) Direct USDC deposit to your trading addresses, or 2) Visit https://aiusd.ai for all token types (login with same wallet). Direct deposits only accept USDC - other stablecoins must use the website."

### reauth / login (Re-authenticate)

- **Purpose**: Clear all cached auth and run OAuth login again.
- **When to use**: User has 401 Unauthorized, "Session ID is required", token expired, auth failure, user asks to re-login, or switch account.
- **Params**: None. Pass `{}`.
- **Example**:
  - `npm run reauth`
  - `npm run login`
  - `node scripts/reauth.js`
- **Steps**:
  1. Clear mcporter cache (`~/.mcporter/`)
  2. Clear local token file (`~/.mcp-hub/`)
  3. Clear other auth cache files
  4. Start browser OAuth login
  5. Verify new auth works
- **Sample dialogue**:
  ```
  User: "I'm getting 401"
  Claude: Looks like an auth issue; re-authenticating...
  [Run: npm run reauth]
  Claude: Re-auth done; you can use the skill again.

  User: "Re-login"
  Claude: Clearing cache and re-logging in...
  [Run: npm run login]
  ```

## Usage Flow (for Agent Reasoning)

1. **Get current tools**: ALWAYS run `aiusd-skill tools --detailed` first to discover all available tools and their current schemas.
2. **Parse intent**: Map natural language to the most appropriate tool. Check if newer tools better match the user's intent.
3. **Prepare params**: Build JSON parameters strictly from the live schema obtained in step 1.
4. **Call**: Invoke the skill's call interface with tool name and params.
5. **Handle result**: Format tool JSON/text for the user; on error, retry or prompt (e.g. auth expired → prompt re-login).

**CRITICAL**: Never use parameter examples from this documentation. Always use the live schema from `tools --detailed`.

## Auth and Error Handling

### Auth error auto-fix

On auth-related errors, Claude should run re-auth:

- **401 Unauthorized** → run `npm run reauth`
- **Session ID is required** → run `npm run reauth`
- **Token invalid or expired** → run `npm run reauth`
- **Auth failed** → run `npm run reauth`

### Error handling flow

1. **Detect auth error** → run `npm run reauth`
2. **Business error** → relay server error to user; do not invent causes
3. **Network/timeout** → retry once; then ask user to check network or try later
4. **Trading issues/failures** → direct user to official website https://aiusd.ai for manual operations and support

### Sample error dialogues

#### Auth Error
```
User: "Check balance"
[Tool returns 401]
Claude: Auth expired; re-authenticating...
[Run: npm run reauth]
Claude: Re-auth done. Fetching balance...
[Call: genalpha_get_balances]
```

#### Trading Error
```
User: "Buy 100 USDC worth of SOL"
[Tool returns trading error]
Claude: I encountered an issue with the trade execution. For manual trading operations, please visit https://aiusd.ai and use the same wallet you use for authentication.
```

## Getting Current Tools and Schema

**MANDATORY FIRST STEP**: Before performing any user task, run:

```bash
aiusd-skill tools --detailed
```

This command returns:
1. **Complete list of available tools** (may include new tools not listed in this document)
2. **Current parameter schemas** for all tools
3. **Working examples** and proper formatting
4. **Any tool-specific instructions** or constraints

**Why this is critical**:
- Tools may be added, modified, or deprecated
- Parameter formats can change
- New tools may better serve specific user intents
- Examples in this document may become outdated

Always base your tool calls on the live output from `tools --detailed`, not on static examples in this documentation.
