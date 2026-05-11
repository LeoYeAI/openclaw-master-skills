# Environment Initialization (Onboarding)

Run this on first use or when the environment is incomplete. Return to the original user intent after completion.

---

## Automated Setup (recommended)

Run the setup script — it handles all steps automatically and clearly marks the steps that require manual action:

```bash
_saved=$(cat ~/.aurehub/.setup_path 2>/dev/null); [ -f "$_saved" ] && SETUP_PATH="$_saved"
[ -z "$SETUP_PATH" ] && { GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/skills/xaut-trade/scripts/setup.sh" ] && SETUP_PATH="$GIT_ROOT/skills/xaut-trade/scripts/setup.sh"; }
[ -z "$SETUP_PATH" ] && SETUP_PATH=$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)
[ -n "$SETUP_PATH" ] && [ -f "$SETUP_PATH" ] && bash "$SETUP_PATH"
```

If the script exits with an error, follow the manual steps below for the failed step only.

---

## Manual Steps (fallback)

### Step 0: Choose Wallet Mode

**Skip this step if wallet mode was already chosen** (e.g. selected during the environment readiness prompt before entering this flow). Use the previously chosen mode and proceed to the appropriate branch.

Otherwise, two wallet modes are available. Choose one:

**WDK (recommended)** — lightweight, no external tools:
- Encrypted vault stored at `~/.aurehub/.wdk_vault`
- Requires only Node.js >= 18
- See [wallet-modes.md](wallet-modes.md) for details

**Foundry** — uses Foundry keystore:
- Requires Foundry (`cast`) to be installed
- Standard Web3 keystore at `~/.foundry/keystores/`
- See [wallet-modes.md](wallet-modes.md) for details

Ask the user which mode they prefer. Default to WDK if they have no preference.

---

### WDK Branch (if user chose WDK)

#### Step W1: Check Node.js

```bash
node -v
# Must be >= 18. If not found or < 18: https://nodejs.org
```

#### Step W2: Prepare Password File

Check if `~/.aurehub/.wdk_password` exists and is non-empty:

```bash
mkdir -p ~/.aurehub
[ -s ~/.aurehub/.wdk_password ] && echo "ready" || echo "missing or empty"
```

If missing or empty, instruct the user to run in their terminal (password will not appear in chat):

```
Please run the following in your terminal (password input will be hidden):

bash -c 'read -rsp "WDK password (min 12 chars): " p </dev/tty; echo; printf "%s" "$p" > ~/.aurehub/.wdk_password; chmod 600 ~/.aurehub/.wdk_password; echo "✓ Password saved to ~/.aurehub/.wdk_password"'

Copy the entire line above, paste into your terminal, and press Enter.
Tell me when done.
```

Wait for user confirmation, then verify:

```bash
[ -s ~/.aurehub/.wdk_password ] && echo "ready" || echo "still empty"
```

If still empty, repeat the prompt.

#### Step W3: Create WDK Wallet

First check if a WDK vault already exists:

```bash
[ -f ~/.aurehub/.wdk_vault ] && echo "EXISTS" || echo "NOT_FOUND"
```

If `EXISTS`: the wallet is already created. Skip to Step W4. Inform the user:
> "WDK wallet already exists at ~/.aurehub/.wdk_vault. Skipping creation."

If `NOT_FOUND`: resolve scripts directory and create the wallet:

```bash
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SCRIPTS_DIR=$(dirname "$SETUP_PATH")
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -d "$GIT_ROOT/skills/xaut-trade/scripts" ]; then
  SCRIPTS_DIR="$GIT_ROOT/skills/xaut-trade/scripts"
else
  SCRIPTS_DIR=$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")
fi
cd "$SCRIPTS_DIR" && npm install
node "$SCRIPTS_DIR/lib/create-wallet.js" --password-file ~/.aurehub/.wdk_password
```

This creates `~/.aurehub/.wdk_vault` with the encrypted seed.

#### Step W3b: Security reminder — back up your seed phrase

**IMPORTANT**: After wallet creation, always present this security notice to the user:

> **Back up your seed phrase now.**
>
> Your wallet is protected by an encrypted vault. If the vault file (`~/.aurehub/.wdk_vault`) or password file (`~/.aurehub/.wdk_password`) is lost or corrupted, **your funds cannot be recovered** without the seed phrase.
>
> Run this command in a **private** terminal to display your 12-word mnemonic:
>
> ```bash
> node <scripts_dir>/lib/export-seed.js
> ```
>
> - Write the 12 words on paper and store offline (safe, lockbox).
> - **Never** save the seed phrase in cloud storage, screenshots, or chat.
> - **Never** share it with anyone — no legitimate service will ask for it.

Do NOT print the seed phrase in the chat. Only provide the export command.

#### Step W4: Write .env for WDK

If `~/.aurehub/.env` does not exist, create it:

```bash
cat > ~/.aurehub/.env << 'EOF'
WALLET_MODE=wdk
ETH_RPC_URL=https://eth.llamarpc.com
ETH_RPC_URL_FALLBACK=https://eth.merkle.io,https://rpc.flashbots.net/fast,https://eth.drpc.org,https://ethereum.publicnode.com
WDK_PASSWORD_FILE=~/.aurehub/.wdk_password
EOF
chmod 600 ~/.aurehub/.env
```

If `~/.aurehub/.env` already exists (e.g. switching from Foundry), only update the wallet-related fields — do NOT overwrite the entire file (to preserve UNISWAPX_API_KEY, RANKINGS, etc.):

```bash
# Update or add each key, preserving other settings
for kv in "WALLET_MODE=wdk" "WDK_PASSWORD_FILE=~/.aurehub/.wdk_password"; do
  key="${kv%%=*}"
  grep -q "^${key}=" ~/.aurehub/.env && sed -i.bak "s|^${key}=.*|${kv}|" ~/.aurehub/.env || echo "$kv" >> ~/.aurehub/.env
done
rm -f ~/.aurehub/.env.bak
grep -q "^ETH_RPC_URL=" ~/.aurehub/.env || echo "ETH_RPC_URL=https://eth.llamarpc.com" >> ~/.aurehub/.env
```

> If the user has a paid RPC (e.g. Alchemy/Infura), replace `ETH_RPC_URL` or prepend it to `ETH_RPC_URL_FALLBACK` for automatic failover.

Now skip to **Step C1: Write config.yaml** below.

---

### Foundry Branch (if user chose Foundry)

#### Step F1: Install Foundry (if `cast` is unavailable)

> **Security note**: The command below pipes a remote script directly into your shell.
> This is the official Foundry installation method. To verify the installer before running,
> you can download and inspect it first: `curl -L https://foundry.paradigm.xyz -o foundryup-install.sh`
> then review `foundryup-install.sh` before executing it with `bash foundryup-install.sh`.

```bash
curl -L https://foundry.paradigm.xyz | bash && \
  export PATH="$HOME/.foundry/bin:$PATH" && \
  foundryup
cast --version   # Expected output: cast Version: x.y.z
```

> After installation, open a new terminal or run `source ~/.zshrc` (zsh) / `source ~/.bashrc` (bash) so `cast` is available in future sessions.

Skip this step if `cast --version` succeeds.

#### Step F2: Prepare Password File

Check if `~/.aurehub/.wallet.password` exists and is non-empty:

```bash
mkdir -p ~/.aurehub
[ -s ~/.aurehub/.wallet.password ] && echo "ready" || echo "missing or empty"
```

If missing or empty, instruct the user to run in their terminal (password will not appear in chat):

```
Please run the following in your terminal (password input will be hidden):

bash -c 'read -rsp "Keystore password: " p </dev/tty; echo; printf "%s" "$p" > ~/.aurehub/.wallet.password; chmod 600 ~/.aurehub/.wallet.password; echo "✓ Password saved to ~/.aurehub/.wallet.password"'

Copy the entire line above, paste into your terminal, and press Enter.
Tell me when done.
```

Wait for user confirmation, then verify:

```bash
[ -s ~/.aurehub/.wallet.password ] && echo "ready" || echo "still empty"
```

If still empty, repeat the prompt.

#### Step F3: Wallet Setup

**Auto-detect**: if the keystore account already exists, skip this step.

```bash
# Use defaults here because ~/.aurehub/.env may not be created yet in manual flow.
FOUNDRY_ACCOUNT=${FOUNDRY_ACCOUNT:-aurehub-wallet}
KEYSTORE_PASSWORD_FILE=${KEYSTORE_PASSWORD_FILE:-~/.aurehub/.wallet.password}
cast wallet list 2>/dev/null | grep -qF "$FOUNDRY_ACCOUNT" && echo "exists" || echo "missing"
```

If missing, choose one method:

Import an existing private key into keystore:

```bash
cast wallet import "$FOUNDRY_ACCOUNT" --interactive
```

Or create a new wallet directly in keystore:

```bash
mkdir -p ~/.foundry/keystores
cast wallet new ~/.foundry/keystores "$FOUNDRY_ACCOUNT" \
  --password-file "$KEYSTORE_PASSWORD_FILE"
```

> Default values: `FOUNDRY_ACCOUNT=aurehub-wallet`, `KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password`

#### Step F4: Write .env for Foundry

If `~/.aurehub/.env` does not exist, create it:

```bash
cat > ~/.aurehub/.env << 'EOF'
WALLET_MODE=foundry
ETH_RPC_URL=https://eth.llamarpc.com
ETH_RPC_URL_FALLBACK=https://eth.merkle.io,https://rpc.flashbots.net/fast,https://eth.drpc.org,https://ethereum.publicnode.com
FOUNDRY_ACCOUNT=aurehub-wallet
KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password
EOF
chmod 600 ~/.aurehub/.env
```

If `~/.aurehub/.env` already exists (e.g. switching from WDK), only update the wallet-related fields:

```bash
for kv in "WALLET_MODE=foundry" "FOUNDRY_ACCOUNT=aurehub-wallet" "KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password"; do
  key="${kv%%=*}"
  grep -q "^${key}=" ~/.aurehub/.env && sed -i.bak "s|^${key}=.*|${kv}|" ~/.aurehub/.env || echo "$kv" >> ~/.aurehub/.env
done
rm -f ~/.aurehub/.env.bak
grep -q "^ETH_RPC_URL=" ~/.aurehub/.env || echo "ETH_RPC_URL=https://eth.llamarpc.com" >> ~/.aurehub/.env
```

> If the user has a paid RPC (e.g. Alchemy/Infura), replace `ETH_RPC_URL` or prepend it to `ETH_RPC_URL_FALLBACK` for automatic failover.

Now continue to **Step C1: Write config.yaml** below.

---

### Common Steps (both modes converge here)

#### Step C1: Write config.yaml

Copy contract config (defaults are ready to use — no user edits needed):

```bash
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SKILL_DIR=$(cd "$(dirname "$SETUP_PATH")/.." && pwd)
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -f "$GIT_ROOT/skills/xaut-trade/config.example.yaml" ]; then
  SKILL_DIR="$GIT_ROOT/skills/xaut-trade"
else
  SKILL_DIR=$(cd "$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")/.." && pwd)
fi
cp "$SKILL_DIR/config.example.yaml" ~/.aurehub/config.yaml
```

`WALLET_MODE` is already set in `~/.aurehub/.env` (written in Step W4 or F4). No config.yaml change needed.

#### Step C2: Install Node.js dependencies

```bash
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SCRIPTS_DIR=$(dirname "$SETUP_PATH")
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -d "$GIT_ROOT/skills/xaut-trade/scripts" ]; then
  SCRIPTS_DIR="$GIT_ROOT/skills/xaut-trade/scripts"
else
  SCRIPTS_DIR=$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")
fi
cd "$SCRIPTS_DIR" && npm install

# Save scripts path for future sessions
printf '%s/setup.sh\n' "$SCRIPTS_DIR" > ~/.aurehub/.setup_path
```

#### Step C3: Verify

```bash
source ~/.aurehub/.env
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SCRIPTS_DIR=$(dirname "$SETUP_PATH")
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -d "$GIT_ROOT/skills/xaut-trade/scripts" ]; then
  SCRIPTS_DIR="$GIT_ROOT/skills/xaut-trade/scripts"
else
  SCRIPTS_DIR=$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")
fi
cd "$SCRIPTS_DIR" && node swap.js address
```

Expected output: `{ "address": "0x..." }`

If successful, inform the user:

```
Environment initialized. Wallet address: <address from output>
Make sure the wallet holds a small amount of ETH (>= 0.005) for gas.
```

---

## Runtime Dependencies (required for market and limit orders)

### 1. Install Node.js and scripts dependencies (>= 18)

```bash
node --version   # If version < 18 or command not found: https://nodejs.org
SETUP_PATH=$(cat ~/.aurehub/.setup_path 2>/dev/null)
if [ -f "$SETUP_PATH" ]; then
  SCRIPTS_DIR=$(dirname "$SETUP_PATH")
elif GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [ -d "$GIT_ROOT/skills/xaut-trade/scripts" ]; then
  SCRIPTS_DIR="$GIT_ROOT/skills/xaut-trade/scripts"
else
  SCRIPTS_DIR=$(dirname "$(find "$HOME" -maxdepth 6 -type f -path "*/xaut-trade/scripts/setup.sh" 2>/dev/null | head -1)")
fi
cd "$SCRIPTS_DIR" && npm install
```

### 2. Get a UniswapX API Key (required for limit orders only)

Limit orders require a UniswapX API Key to submit and query orders.

How to obtain (about 5 minutes, free):
1. Visit https://developers.uniswap.org/dashboard
2. Sign in with Google / GitHub
3. Generate a Token (choose Free tier)

Add the key to `~/.aurehub/.env`:

```bash
echo 'UNISWAPX_API_KEY=your_key_here' >> ~/.aurehub/.env
```

Node.js and npm dependencies are required for both market and limit orders.
Only `UNISWAPX_API_KEY` is limit-order specific.

---

## Activity Rankings (optional)

To join the XAUT trade activity rankings, add the following to `~/.aurehub/.env`:

```bash
echo 'RANKINGS_OPT_IN=true' >> ~/.aurehub/.env
echo 'NICKNAME=YourName' >> ~/.aurehub/.env
```

This shares your wallet address and nickname with https://xaue.com after your first trade. You can disable it anytime by setting `RANKINGS_OPT_IN=false`.

If you do not add these lines, no data is sent — rankings are opt-in only.
