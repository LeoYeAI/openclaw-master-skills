# Balance & Pre-flight Checks

Complete the following steps in order before any quote or execution.

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
```

## 1. Environment Check

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js address
```

If the command fails, stop and prompt:
- Node.js not installed or < 18: install Node.js first
- Config missing: trigger onboarding
- RPC unavailable: trigger RPC fallback sequence (see RPC Fallback section in SKILL.md)

## 2. Wallet Mode Validation

Check `WALLET_MODE` in `~/.aurehub/.env`:

- **If `WALLET_MODE=wdk`**: verify `WDK_PASSWORD_FILE` is set and readable:
  ```bash
  source ~/.aurehub/.env
  test -r "$WDK_PASSWORD_FILE" && echo "OK" || echo "FAIL"
  ```
  If `FAIL`, hard-stop:
  > Password file not readable: `$WDK_PASSWORD_FILE`
  > Create it with: `bash -c 'read -rsp "WDK password: " p </dev/tty; echo; printf "%s" "$p" > ~/.aurehub/.wdk_password; chmod 600 ~/.aurehub/.wdk_password; echo "Saved."'`

- **If `WALLET_MODE=foundry`**: verify `FOUNDRY_ACCOUNT` and `KEYSTORE_PASSWORD_FILE` are set:
  ```bash
  source ~/.aurehub/.env
  [ -n "$FOUNDRY_ACCOUNT" ] && [ -n "$KEYSTORE_PASSWORD_FILE" ] && echo "OK" || echo "FAIL"
  ```
  If `FAIL`, hard-stop:
  > Missing keystore signing config. Set both `FOUNDRY_ACCOUNT` and `KEYSTORE_PASSWORD_FILE` in `.env`.

  Verify password file is readable:
  ```bash
  source ~/.aurehub/.env
  test -r "$KEYSTORE_PASSWORD_FILE" && echo "OK" || echo "FAIL"
  ```
  If `FAIL`, hard-stop:
  > Password file not readable: `$KEYSTORE_PASSWORD_FILE`

If `PRIVATE_KEY` exists in `.env`, hard-stop immediately:
> `PRIVATE_KEY` runtime mode is no longer supported.
> Remove `PRIVATE_KEY` from `.env` and use either WDK or Foundry wallet mode.

## 3. Derive Wallet Address

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
WALLET_ADDRESS=$(node swap.js address | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).address")
echo "$WALLET_ADDRESS"
```

## 4. Full Balance Check (ETH + USDT + XAUT)

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js balance
```

Output is JSON with all balances pre-formatted (human-readable):

```json
{
  "address": "0x...",
  "ETH": "0.05",
  "USDT": "1000.0",
  "XAUT": "0.5"
}
```

- If ETH balance is below `risk.min_eth_for_gas`, hard-stop
- **Buy flow**: if USDT balance is insufficient for the intended trade, hard-stop and report the shortfall
- **Sell flow**: if XAUT balance is insufficient for the intended trade, hard-stop and report the shortfall
