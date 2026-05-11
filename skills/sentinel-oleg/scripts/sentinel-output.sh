#!/usr/bin/env bash
# sentinel-output.sh — Output monitor for OpenClaw agents
# Scans agent responses for secret leakage, credential exposure,
# and suspicious command requests before they reach the user.
#
# Usage:
#   echo "$AGENT_RESPONSE" | sentinel-output.sh [--json] [--strict]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load config
CONFIG_FILE="${HOME}/.sentinel/config.sh"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

SENTINEL_LOG="${SENTINEL_LOG:-$HOME/.sentinel/threats.jsonl}"
SENTINEL_CHECK_SECRETS="${SENTINEL_CHECK_SECRETS:-true}"
SENTINEL_CRYPTO_PATTERNS="${SENTINEL_CRYPTO_PATTERNS:-true}"

JSON_MODE=false
STRICT_MODE=false
for arg in "$@"; do
  case "$arg" in
    --json)   JSON_MODE=true ;;
    --strict) STRICT_MODE=true ;;
  esac
done

INPUT=$(cat || true)

if [[ -z "$INPUT" ]]; then
  [[ "$JSON_MODE" == true ]] && echo '{"status":"clean","threats":[]}'
  exit 0
fi

THREATS=()
SEVERITY="CLEAN"
CATEGORIES=()

update_severity() {
  local new="$1"
  case "$SEVERITY" in
    CLEAN)   SEVERITY="$new" ;;
    WARNING) [[ "$new" == "HIGH" || "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
    HIGH)    [[ "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
  esac
}

# --- API KEY PATTERNS ---
if [[ "$SENTINEL_CHECK_SECRETS" == true ]]; then

  # OpenAI
  if echo "$INPUT" | grep -qP 'sk-proj-[A-Za-z0-9_-]{20,}'; then
    THREATS+=("secret_leak: OpenAI API key (sk-proj-...)")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Anthropic
  if echo "$INPUT" | grep -qP 'sk-ant-[A-Za-z0-9_-]{20,}'; then
    THREATS+=("secret_leak: Anthropic API key (sk-ant-...)")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # AWS Access Key
  if echo "$INPUT" | grep -qE '(AKIA|ASIA)[A-Z0-9]{16}'; then
    THREATS+=("secret_leak: AWS Access Key ID")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # AWS Secret Key (40 char base64-like after common prefixes)
  if echo "$INPUT" | grep -qP '(?i)(aws_secret|secret_key|secretaccesskey)["\s:=]+[A-Za-z0-9/+=]{40}'; then
    THREATS+=("secret_leak: AWS Secret Access Key")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Google Cloud / GCP
  if echo "$INPUT" | grep -qP 'AIza[A-Za-z0-9_\\-]{35}'; then
    THREATS+=("secret_leak: Google API key")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Stripe
  if echo "$INPUT" | grep -qP '(sk|rk)_(live|test)_[A-Za-z0-9]{20,}'; then
    THREATS+=("secret_leak: Stripe API key")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # GitHub Token
  if echo "$INPUT" | grep -qP '(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}'; then
    THREATS+=("secret_leak: GitHub token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Telegram Bot Token
  if echo "$INPUT" | grep -qP '[0-9]{8,10}:[A-Za-z0-9_-]{35}'; then
    THREATS+=("secret_leak: Telegram Bot Token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Slack token
  if echo "$INPUT" | grep -qP 'xox[bpsa]-[A-Za-z0-9-]{10,}'; then
    THREATS+=("secret_leak: Slack token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # SendGrid API key
  if echo "$INPUT" | grep -qP 'SG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{40,}'; then
    THREATS+=("secret_leak: SendGrid API key")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # HuggingFace token
  if echo "$INPUT" | grep -qP 'hf_[A-Za-z0-9]{34,}'; then
    THREATS+=("secret_leak: HuggingFace token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # Replicate token
  if echo "$INPUT" | grep -qP 'r8_[A-Za-z0-9]{34,}'; then
    THREATS+=("secret_leak: Replicate token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # GitLab token
  if echo "$INPUT" | grep -qP '(glpat|gldt|glrt)-[A-Za-z0-9_-]{20,}'; then
    THREATS+=("secret_leak: GitLab token")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # SSH Private Key
  if echo "$INPUT" | grep -qE '\-\-\-\-\-BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY\-\-\-\-\-'; then
    THREATS+=("secret_leak: SSH/PGP private key")
    CATEGORIES+=("secret_leak")
    update_severity "CRITICAL"
  fi

  # JWT Token
  if echo "$INPUT" | grep -qP 'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+'; then
    THREATS+=("secret_leak: JWT token")
    CATEGORIES+=("secret_leak")
    update_severity "HIGH"
  fi

  # Database connection strings
  if echo "$INPUT" | grep -qPi '(postgres|mysql|mongodb|redis|amqp)://[^"\s]{10,}'; then
    THREATS+=("secret_leak: Database connection string")
    CATEGORIES+=("secret_leak")
    update_severity "HIGH"
  fi

  # Bearer token
  if echo "$INPUT" | grep -qPi 'bearer [A-Za-z0-9_\-\.]{20,}'; then
    THREATS+=("secret_leak: Bearer token")
    CATEGORIES+=("secret_leak")
    update_severity "HIGH"
  fi

  # Bulk .env patterns (3+ KEY=VALUE on separate lines)
  ENV_COUNT=$(echo "$INPUT" | grep -cP '^[A-Z_]{3,}=\S+' || true)
  if [[ $ENV_COUNT -ge 3 ]]; then
    THREATS+=("secret_leak: Possible .env file contents ($ENV_COUNT key=value pairs)")
    CATEGORIES+=("secret_leak")
    update_severity "HIGH"
  fi
fi

# --- CRYPTO-SPECIFIC PATTERNS ---
if [[ "$SENTINEL_CRYPTO_PATTERNS" == true ]]; then

  # Ethereum/EVM private key (64 hex chars, often with 0x prefix)
  if echo "$INPUT" | grep -qP '(0x)?[0-9a-fA-F]{64}'; then
    # Additional check: must not be a SHA256 hash context
    if ! echo "$INPUT" | grep -qPi '(sha256|hash|checksum|digest|commit)'; then
      THREATS+=("crypto_leak: Possible private key (64 hex chars)")
      CATEGORIES+=("crypto_leak")
      update_severity "CRITICAL"
    fi
  fi

  # BIP-39 Seed Phrase detection (12 or 24 common BIP-39 words in sequence)
  # Check for sequences of 12+ lowercase words that match common seed word patterns
  BIP39_COMMON="abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alcohol|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amateur|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another"
  WORD_COUNT=$(echo "$INPUT" | grep -oP '\b[a-z]{3,8}\b' | wc -l)
  if [[ $WORD_COUNT -ge 12 ]]; then
    SEED_MATCH=$(echo "$INPUT" | grep -oP '\b[a-z]{3,8}\b' | grep -cP "^($BIP39_COMMON)$" || true)
    if [[ $SEED_MATCH -ge 10 ]]; then
      THREATS+=("crypto_leak: Possible BIP-39 seed phrase ($SEED_MATCH/12+ matching words)")
      CATEGORIES+=("crypto_leak")
      update_severity "CRITICAL"
    fi
  fi

  # Solana private key (base58, 76-88 chars)
  if echo "$INPUT" | grep -qP '[1-9A-HJ-NP-Za-km-z]{76,88}'; then
    THREATS+=("crypto_leak: Possible Solana private key (base58)")
    CATEGORIES+=("crypto_leak")
    update_severity "CRITICAL"
  fi

  # BTC WIF private key (starts with 5, K, or L, 51-52 chars base58)
  if echo "$INPUT" | grep -qP '(?<![A-Za-z0-9])(5|K|L)[1-9A-HJ-NP-Za-km-z]{50,51}(?![A-Za-z0-9])'; then
    THREATS+=("crypto_leak: Possible BTC WIF private key")
    CATEGORIES+=("crypto_leak")
    update_severity "CRITICAL"
  fi

  # Exchange API keys (binance, coinbase, kraken etc.)
  if echo "$INPUT" | grep -qPi '(binance|coinbase|kraken|ftx|bybit|okx|kucoin|huobi|gate\.?io|bitfinex|bitstamp|gemini).*(api|secret)\s*(key)?\s*[:=]\s*[A-Za-z0-9+/=-]{16,}'; then
    THREATS+=("crypto_leak: Exchange API key")
    CATEGORIES+=("crypto_leak")
    update_severity "CRITICAL"
  fi

  # Infura / Alchemy / node provider keys in URLs
  if echo "$INPUT" | grep -qPi '(infura\.io|alchemy\.com|quicknode\.com|chainstack\.com)/[A-Za-z0-9_/-]*[A-Za-z0-9]{20,}'; then
    THREATS+=("crypto_leak: Node provider API key in URL")
    CATEGORIES+=("crypto_leak")
    update_severity "CRITICAL"
  fi
fi

# --- SUSPICIOUS COMMANDS IN RESPONSE ---
LOWER=$(echo "$INPUT" | tr '[:upper:]' '[:lower:]')

CMD_RESPONSE_PATTERNS=(
  "please (run|execute|type|enter|paste).*\b(curl|wget|pip|npm|bash|sh|python)\b"
  "(run|execute|type) (this|the following) (command|in your terminal)"
  "copy (and |& )paste (this |the following )?(into|in) (your )?(terminal|shell)"
  "install (this|the) (dependency|package|tool) (by running|with|using)"
  "add (this|the following) to (your )?crontab"
  "disable (your )?(firewall|antivirus|security|windows defender)"
  "turn off (your )?(firewall|antivirus|security)"
  "send (me|us|to) your (password|api.?key|token|private.?key|seed.?phrase|mnemonic)"
  "share your (credentials|login|password)"
  "i need your (api.?key|token|password|credentials)"
  "for (debugging|testing|verification).*(share|send|provide|paste) your"
  "add (this|the following) to (your )?(\.bashrc|\.zshrc|\.profile|\.env)"
)

for pattern in "${CMD_RESPONSE_PATTERNS[@]}"; do
  if echo "$LOWER" | grep -qPi "$pattern"; then
    THREATS+=("suspicious_output: Agent asking user to '$pattern'")
    CATEGORIES+=("suspicious_command")
    update_severity "HIGH"
  fi
done

# ============================================================
# Premium patterns check (if installed)
# ============================================================
PREMIUM_CHECK="$SCRIPT_DIR/sentinel-premium-check.sh"
if [[ -x "$PREMIUM_CHECK" ]]; then
  PREMIUM_RESULT=$(echo "$INPUT" | bash "$PREMIUM_CHECK" output 2>/dev/null || true)
  if echo "$PREMIUM_RESULT" | grep -q '"threat_count"'; then
    P_COUNT=$(echo "$PREMIUM_RESULT" | grep -oP '"threat_count":\K[0-9]+' || echo 0)
    P_SEV=$(echo "$PREMIUM_RESULT" | grep -oP '"severity":"\K[^"]+' || echo "")
    P_THREATS=$(echo "$PREMIUM_RESULT" | grep -oP '"threats":\[\K[^\]]+' || echo "")
    if [[ $P_COUNT -gt 0 ]]; then
      while IFS= read -r pt; do
        pt_clean=$(echo "$pt" | tr -d '"')
        [[ -n "$pt_clean" ]] && THREATS+=("premium:$pt_clean") && CATEGORIES+=("$pt_clean")
      done < <(echo "$P_THREATS" | tr ',' '\n')
      [[ -n "$P_SEV" ]] && update_severity "$P_SEV"
    fi
  fi
fi

# ============================================================
# Output results
# ============================================================
UNIQUE_CATS=($(printf '%s\n' "${CATEGORIES[@]}" 2>/dev/null | sort -u || true))
CAT_STRING=$(IFS='+'; echo "${UNIQUE_CATS[*]}" 2>/dev/null || echo "none")
THREAT_COUNT=${#THREATS[@]}

# Log
if [[ $THREAT_COUNT -gt 0 ]]; then
  mkdir -p "$(dirname "$SENTINEL_LOG")"
  SNIPPET=$(echo "$INPUT" | head -c 200 | tr '\n' ' ')
  LOG_ENTRY="{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"direction\":\"output\",\"severity\":\"$SEVERITY\",\"categories\":\"$CAT_STRING\",\"threat_count\":$THREAT_COUNT,\"snippet\":\"$(echo "$SNIPPET" | sed 's/"/\\"/g')\"}"
  echo "$LOG_ENTRY" >> "$SENTINEL_LOG" 2>/dev/null || true
fi

if [[ "$JSON_MODE" == true ]]; then
  if [[ $THREAT_COUNT -eq 0 ]]; then
    echo '{"status":"clean","severity":"CLEAN","threats":[]}'
    exit 0
  else
    THREATS_JSON="["
    for i in "${!THREATS[@]}"; do
      [[ $i -gt 0 ]] && THREATS_JSON+=","
      THREATS_JSON+="\"$(echo "${THREATS[$i]}" | sed 's/"/\\"/g')\""
    done
    THREATS_JSON+="]"
    echo "{\"status\":\"threat\",\"severity\":\"$SEVERITY\",\"categories\":\"$CAT_STRING\",\"threat_count\":$THREAT_COUNT,\"threats\":$THREATS_JSON}"
    exit 1
  fi
fi

if [[ $THREAT_COUNT -eq 0 ]]; then
  echo "✅ Output clean — no leaks detected"
  exit 0
fi

case "$SEVERITY" in
  CRITICAL) EMOJI="🔴" ;;
  HIGH)     EMOJI="🟠" ;;
  WARNING)  EMOJI="🟡" ;;
  *)        EMOJI="⚪" ;;
esac

echo "$EMOJI $SEVERITY [$CAT_STRING]: $THREAT_COUNT leak(s) detected in agent output"
echo ""
for threat in "${THREATS[@]}"; do
  echo "  → $threat"
done
echo ""
echo "⚠️  Do NOT send this response externally. Remove sensitive data first."

[[ "$SEVERITY" == "CRITICAL" || "$SEVERITY" == "HIGH" ]] && exit 1
[[ "$STRICT_MODE" == true ]] && exit 1
exit 2
