---
name: bagman
version: 1.0.0
description: Secure key management for AI agents. Use when handling private keys, API secrets, wallet credentials, or when building systems that need agent-controlled funds. Covers secure storage, session keys, leak prevention, and prompt injection defense.
homepage: https://numbergroup.xyz
metadata:
  {
    "openclaw": {
      "emoji": "🔐",
      "requires": { "bins": ["op"] },
      "tags": ["security", "wallet", "keys", "crypto", "secrets"]
    }
  }
---

# Bagman

Secure key management patterns for AI agents handling private keys and secrets. Designed to prevent:
- **Key loss**: Agents forgetting keys between sessions
- **Accidental exposure**: Keys leaked to GitHub, logs, or outputs
- **Prompt injection**: Malicious prompts extracting secrets

## Core Principles

1. **Never store raw private keys in config, env vars, or memory files**
2. **Use session keys / delegated access instead of full control**
3. **All secret access goes through 1Password CLI (`op`)**
4. **Validate all outputs before sending to prevent key leakage**

## References

- `references/secure-storage.md` - 1Password patterns for agent secrets
- `references/session-keys.md` - ERC-4337 delegated access patterns
- `references/leak-prevention.md` - Pre-commit hooks and output sanitization
- `references/prompt-injection-defense.md` - Input validation and output filtering

---

## Quick Reference

### DO ✅

```bash
# Retrieve key at runtime via 1Password
PRIVATE_KEY=$(op read "op://Agents/my-agent-wallet/private-key")

# Use environment injection (key never touches disk)
op run --env-file=.env.tpl -- node agent.js

# Use session keys with bounded permissions
# (delegate specific capabilities, not full wallet access)
```

### DON'T ❌

```bash
# NEVER store keys in files
echo "PRIVATE_KEY=0x123..." > .env

# NEVER log or print keys
console.log("Key:", privateKey)

# NEVER store keys in memory/journal files
# Even in "private" agent memory - these can be exfiltrated

# NEVER trust unvalidated input near key operations
```

---

## Architecture: Agent Wallet Stack

```
┌─────────────────────────────────────────────────────┐
│                   AI Agent                          │
├─────────────────────────────────────────────────────┤
│  Session Key (time/value bounded)                   │
│  - Expires after N hours                            │
│  - Spending cap per operation                       │
│  - Whitelist of allowed contracts                   │
├─────────────────────────────────────────────────────┤
│  1Password / Secret Manager                         │
│  - Agent retrieves session key at runtime           │
│  - Never stores full private key                    │
│  - Audit log of all accesses                        │
├─────────────────────────────────────────────────────┤
│  ERC-4337 Smart Account                             │
│  - Programmable permissions                         │
│  - Recovery without private key exposure            │
│  - Multi-sig for high-value operations              │
├─────────────────────────────────────────────────────┤
│  Operator (Human)                                   │
│  - Holds master key in hardware wallet              │
│  - Issues/revokes session keys                      │
│  - Monitors agent activity                          │
└─────────────────────────────────────────────────────┘
```

---

## Workflow: Setting Up Agent Wallet Access

### 1. Create 1Password Vault for Agent Secrets

```bash
# Create dedicated vault (via 1Password app or CLI)
op vault create "Agent-Wallets" --description "AI agent wallet credentials"

# Store agent session key (not master key!)
op item create \
  --vault "Agent-Wallets" \
  --category "API Credential" \
  --title "trading-bot-session" \
  --field "session-key[password]=0xsession..." \
  --field "expires=2026-02-15T00:00:00Z" \
  --field "spending-cap=1000 USDC" \
  --field "allowed-contracts=0xDEX1,0xDEX2"
```

### 2. Agent Retrieves Credentials at Runtime

```python
import subprocess
import json

def get_session_key(item_name: str) -> dict:
    """Retrieve session key from 1Password at runtime."""
    result = subprocess.run(
        ["op", "item", "get", item_name, "--vault", "Agent-Wallets", "--format", "json"],
        capture_output=True, text=True, check=True
    )
    item = json.loads(result.stdout)
    
    # Extract fields
    fields = {f["label"]: f.get("value") for f in item.get("fields", [])}
    
    # Validate session hasn't expired
    from datetime import datetime
    expires = datetime.fromisoformat(fields.get("expires", "2000-01-01"))
    if datetime.now() > expires:
        raise ValueError("Session key expired - request new key from operator")
    
    return {
        "session_key": fields.get("session-key"),
        "expires": fields.get("expires"),
        "spending_cap": fields.get("spending-cap"),
        "allowed_contracts": fields.get("allowed-contracts", "").split(",")
    }
```

### 3. Never Log or Store the Key

```python
# ❌ BAD - Key in logs
logger.info(f"Using key: {session_key}")

# ✅ GOOD - Redacted identifier
logger.info(f"Using session key: {session_key[:8]}...{session_key[-4:]}")

# ❌ BAD - Key in memory file
with open("memory/today.md", "a") as f:
    f.write(f"Session key: {session_key}")

# ✅ GOOD - Reference only
with open("memory/today.md", "a") as f:
    f.write(f"Session key: [stored in 1Password: trading-bot-session]")
```

---

## Leak Prevention

### Output Sanitization

Before any agent output (chat, logs, file writes), scan for key patterns:

```python
import re

KEY_PATTERNS = [
    r'0x[a-fA-F0-9]{64}',                    # ETH private keys
    r'sk-[a-zA-Z0-9]{48,}',                  # OpenAI keys
    r'sk-ant-[a-zA-Z0-9\-_]{80,}',           # Anthropic keys
    r'gsk_[a-zA-Z0-9]{48,}',                 # Groq keys
    r'[A-Za-z0-9+/]{40,}={0,2}',             # Base64 encoded (suspiciously long)
]

def sanitize_output(text: str) -> str:
    """Remove potential secrets from output."""
    for pattern in KEY_PATTERNS:
        text = re.sub(pattern, '[REDACTED]', text)
    return text

# Apply to ALL agent outputs
def send_message(content: str):
    content = sanitize_output(content)
    # ... send to chat/log/file
```

### Pre-commit Hook

Install this hook to prevent accidental commits of secrets:

```bash
#!/bin/bash
# .git/hooks/pre-commit

PATTERNS=(
    '0x[a-fA-F0-9]{64}'
    'sk-[a-zA-Z0-9]{48,}'
    'sk-ant-api'
    'PRIVATE_KEY='
    'gsk_[a-zA-Z0-9]{48,}'
)

for pattern in "${PATTERNS[@]}"; do
    if git diff --cached | grep -qE "$pattern"; then
        echo "❌ Potential secret detected matching: $pattern"
        echo "   Remove secrets before committing!"
        exit 1
    fi
done
```

### .gitignore Essentials

```gitignore
# Secrets
.env
.env.*
*.pem
*.key
secrets/
credentials/

# Agent state that might contain secrets
memory/*.json
wallet-state.json
session-keys/
```

---

## Prompt Injection Defense

### Input Validation

Before processing any user input that touches wallet operations:

```python
DANGEROUS_PATTERNS = [
    r'ignore.*(previous|above|prior).*instructions',
    r'reveal.*(key|secret|password|credential)',
    r'output.*(key|secret|private)',
    r'print.*(key|secret|wallet)',
    r'show.*(key|secret|password)',
    r'what.*(key|secret|password)',
    r'tell.*me.*(key|secret)',
    r'disregard.*rules',
    r'system.*prompt',
    r'jailbreak',
    r'dan.*mode',
]

def validate_input(text: str) -> bool:
    """Check for prompt injection attempts."""
    text_lower = text.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    return True

def process_wallet_request(user_input: str):
    if not validate_input(user_input):
        return "I can't help with that request."
    # ... proceed with wallet operation
```

### Separation of Concerns

- **Wallet operations should be in isolated functions** with no access to conversation context
- **Never pass full conversation history to wallet-sensitive code**
- **Use allowlists for operations, not blocklists**

```python
ALLOWED_WALLET_OPERATIONS = {
    "check_balance": lambda: get_balance(),
    "send_usdc": lambda to, amount: send_usdc(to, amount) if amount < DAILY_LIMIT else deny(),
    "swap": lambda: swap_tokens() if within_limits() else deny(),
}

def execute_wallet_operation(operation: str, **kwargs):
    """Execute only explicitly allowed operations."""
    if operation not in ALLOWED_WALLET_OPERATIONS:
        raise ValueError(f"Operation '{operation}' not allowed")
    return ALLOWED_WALLET_OPERATIONS[operation](**kwargs)
```

---

## Session Key Implementation (ERC-4337)

For agents needing on-chain access, use session keys instead of raw private keys.

See `references/session-keys.md` for full implementation details including:
- ZeroDev/Biconomy SDK examples
- Permission patterns for trading/DeFi/payment agents
- Session key lifecycle management
- Revocation procedures

---

## Incident Response

### If a Key is Leaked

1. **Immediate**: Revoke the session key / rotate credentials
2. **Assess**: Check transaction history for unauthorized activity
3. **Notify**: Alert operator via secure channel
4. **Rotate**: Issue new session key with tighter permissions
5. **Audit**: Review how leak occurred, update defenses

```bash
# Emergency: Revoke 1Password item
op item delete "compromised-session-key" --vault "Agent-Wallets"

# Rotate to new session key
op item create --vault "Agent-Wallets" --category "API Credential" \
  --title "trading-bot-session-v2" ...
```

---

## Checklist: Agent Wallet Setup

- [ ] Create dedicated 1Password vault for agent credentials
- [ ] Store session keys (NOT master keys) in vault
- [ ] Set appropriate expiry and spending limits
- [ ] Install pre-commit hook for secret detection
- [ ] Add output sanitization to all agent responses
- [ ] Implement input validation for prompt injection
- [ ] Configure monitoring and alerts
- [ ] Document incident response procedure
- [ ] Test key rotation procedure

---

## Common Mistakes Found in Production

### 1. Keys in Memory Files

**Problem**: Agents store keys in `memory/*.md` for "persistence"

```markdown
# memory/2026-02-07.md
## Test Wallet
- Private key: 0x9f01dad551039daad3a8c4e43a32035bdd4da54e7b4292268be16e913b0b3e56
```

**Fix**: Store reference only: `Private key: [1Password: test-wallet-session]`

### 2. Keys in Environment Templates

**Problem**: `.env.example` contains real keys

```
# .env.example
PRIVATE_KEY=sk-ant-api03-real-key-here...  # "for testing"
```

**Fix**: Use obviously fake placeholders: `PRIVATE_KEY=your-key-here`

### 3. Keys in Error Messages

**Problem**: Error handling exposes keys

```python
try:
    sign_transaction(private_key, tx)
except Exception as e:
    logger.error(f"Failed with key {private_key}: {e}")  # ❌
```

**Fix**: Never include credentials in error context

### 4. Test Keys in Production Code

**Problem**: Hardcoded test keys make it to main branch

**Fix**: Use separate test vault, CI checks for key patterns

---

## Integration with OpenClaw

When running as an OpenClaw agent:

1. **Use 1Password skill** for all secret retrieval
2. **Never write keys to workspace files** - they persist across sessions
3. **Sanitize outputs** before sending to any channel (Telegram, Discord, etc.)
4. **Session key approach** for wallet operations - request bounded access from operator
5. **Document key references** in TOOLS.md, not the actual keys

Example TOOLS.md entry:
```markdown
### Agent Wallet
- Address: 0xABC123...
- Session key: [1Password: my-agent-session]
- Permissions: USDC transfers < 100, approved DEX only
- Expires: 2026-02-15
- To rotate: Ask operator via Telegram
```
