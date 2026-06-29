#!/bin/bash
# init.sh - Interactive AMCP setup
# Usage: ./init.sh [--non-interactive]
#
# Steps:
#   1. Check/create ~/.amcp/identity.json
#   2. Set up watchdog (systemd or cron fallback)
#   3. Set up checkpoint cron schedule
#   4. Write config to ~/.amcp/config.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
AMCP_DIR="${AMCP_DIR:-$HOME/.amcp}"
AGENT_NAME="${AGENT_NAME:-$(hostname -s)}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

# Watchdog defaults
WATCHDOG_INTERVAL="${WATCHDOG_INTERVAL:-120}"  # seconds
CHECKPOINT_SCHEDULE="${CHECKPOINT_SCHEDULE:-0 */4 * * *}"  # every 4 hours

# Systemd paths
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
WATCHDOG_SERVICE="amcp-watchdog"
CHECKPOINT_TIMER="amcp-checkpoint"

# ============================================================
# Helpers
# ============================================================

info()  { echo "  → $*"; }
ok()    { echo "  ✓ $*"; }
warn()  { echo "  ⚠ $*" >&2; }
fail()  { echo "  ✗ $*" >&2; }
header() { echo ""; echo "═══ $* ═══"; }

prompt_yn() {
  local msg="$1" default="${2:-y}"
  local yn
  if [ "$default" = "y" ]; then
    read -rp "  $msg [Y/n] " yn
    yn="${yn:-y}"
  else
    read -rp "  $msg [y/N] " yn
    yn="${yn:-n}"
  fi
  [[ "$yn" =~ ^[Yy] ]]
}

prompt_value() {
  local msg="$1" default="${2:-}"
  local val
  if [ -n "$default" ]; then
    read -rp "  $msg [$default]: " val
    echo "${val:-$default}"
  else
    read -rp "  $msg: " val
    echo "$val"
  fi
}

# Register agent on Solvr, parse response, update config JSON on stdout.
# Usage: updated_config=$(do_solvr_register "$agent_name" <<< "$existing_config")
# Returns 0 on success, 1 on failure. Prints updated config JSON to stdout on success.
do_solvr_register() {
  local solvr_agent_name="$1"
  local input_config
  input_config=$(cat)

  info "Registering on Solvr as '$solvr_agent_name'..."

  local solvr_response
  solvr_response=$(curl -s -w "\n%{http_code}" --max-time 30 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$solvr_agent_name\"}" \
    "$SOLVR_API_URL/agents/register" 2>/dev/null || echo -e "\n000")

  local solvr_http_code
  solvr_http_code=$(echo "$solvr_response" | tail -n1)
  local solvr_body
  solvr_body=$(echo "$solvr_response" | sed '$d')

  if [ "$solvr_http_code" != "200" ] && [ "$solvr_http_code" != "201" ]; then
    warn "Registration failed (HTTP $solvr_http_code)"
    [ -n "$solvr_body" ] && warn "Response: $solvr_body"
    echo "$input_config"
    return 1
  fi

  local solvr_api_key solvr_agent_id solvr_quota
  solvr_api_key=$(echo "$solvr_body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('api_key','') or d.get('apiKey',''))" 2>/dev/null || echo "")
  solvr_agent_id=$(echo "$solvr_body" | python3 -c "import json,sys; d=json.load(sys.stdin); a=d.get('agent',{}); print(a.get('id','') or a.get('name',''))" 2>/dev/null || echo "$solvr_agent_name")
  solvr_quota=$(echo "$solvr_body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('pinning_quota_bytes',1073741824))" 2>/dev/null || echo "1073741824")

  if [ -z "$solvr_api_key" ]; then
    warn "Registration succeeded but no API key in response"
    echo "$input_config"
    return 1
  fi

  local claim_url="https://solvr.dev/agents/me/claim"

  local updated_config
  updated_config=$(SOLVR_REG_KEY="$solvr_api_key" SOLVR_REG_NAME="$solvr_agent_id" SOLVR_CLAIM_URL="$claim_url" \
    python3 -c "
import json, sys, os
d = json.load(sys.stdin)
key = os.environ['SOLVR_REG_KEY']
name = os.environ['SOLVR_REG_NAME']
curl = os.environ['SOLVR_CLAIM_URL']
d.setdefault('solvr', {})['apiKey'] = key
d['solvr']['name'] = name
d['solvr']['claimUrl'] = curl
d.setdefault('apiKeys', {})['solvr'] = key
d.setdefault('ipfs', {})['provider'] = 'solvr'
json.dump(d, sys.stdout, indent=2)
" <<< "$input_config")

  local quota_gb=$(( solvr_quota / 1073741824 ))
  [ "$quota_gb" -lt 1 ] && quota_gb=1
  ok "Registered as ${solvr_agent_id}! ${quota_gb}GB free pinning included."

  # Display claim invitation
  echo ""
  echo "  ┌─────────────────────────────────────────────────────────┐"
  echo "  │  CLAIM YOUR AGENT                                      │"
  echo "  │                                                         │"
  echo "  │  To link me to your human account:                     │"
  echo "  │    → $claim_url              │"
  echo "  │                                                         │"
  echo "  │  Optional but gives you control over my settings       │"
  echo "  │  and reputation on the Solvr network.                  │"
  echo "  │                                                         │"
  echo "  │  View this anytime: proactive-amcp claim-info          │"
  echo "  └─────────────────────────────────────────────────────────┘"
  echo ""

  echo "$updated_config"
  return 0
}

# ============================================================
# Step 1: Identity
# ============================================================

setup_identity() {
  header "Step 1: AMCP Identity"

  mkdir -p "$AMCP_DIR"

  if [ -f "$IDENTITY_PATH" ]; then
    info "Found identity at $IDENTITY_PATH"

    # Validate it
    if "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
      ok "Identity is valid"
      return 0
    else
      warn "Identity exists but is INVALID (possibly fake/placeholder)"
      if prompt_yn "Replace with a fresh identity?"; then
        local backup="${IDENTITY_PATH}.bak.$(date +%Y%m%d%H%M%S)"
        cp "$IDENTITY_PATH" "$backup"
        info "Backed up old identity to $backup"
        create_identity
      else
        fail "Cannot continue with invalid identity"
        exit 1
      fi
    fi
  else
    info "No identity found at $IDENTITY_PATH"
    info "Creating new AMCP identity..."
    create_identity
  fi
}

create_identity() {
  mkdir -p "$(dirname "$IDENTITY_PATH")"
  if "$AMCP_CLI" identity create --out "$IDENTITY_PATH" 2>/dev/null; then
    ok "Identity created at $IDENTITY_PATH"
  else
    fail "Failed to create identity. Is 'amcp' CLI installed?"
    echo ""
    echo "  Install: npm install -g @amcp/cli"
    echo "  Or:      go install github.com/fcavalcantirj/amcp-protocol/cmd/amcp@latest"
    exit 1
  fi
}

# ============================================================
# Step 2: Config
# ============================================================

setup_config() {
  header "Step 2: Configuration"

  mkdir -p "$AMCP_DIR"

  # Load existing config or start fresh
  local existing_config="{}"
  if [ -f "$CONFIG_FILE" ]; then
    existing_config=$(cat "$CONFIG_FILE")
    info "Found existing config at $CONFIG_FILE"
  else
    info "No config found — creating $CONFIG_FILE"
  fi

  # ============================================================
  # Solvr Registration — offer auto-registration if no key
  # ============================================================

  local existing_solvr_check
  existing_solvr_check=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('solvr',{}).get('apiKey',''))" 2>/dev/null || echo "")

  if [ -z "$existing_solvr_check" ]; then
    echo ""
    echo "  ┌─────────────────────────────────────────────────────────┐"
    echo "  │  SOLVR REGISTRATION                                    │"
    echo "  │                                                         │"
    echo "  │  Solvr gives you:                                      │"
    echo "  │    • Free IPFS pinning (1GB included)                  │"
    echo "  │    • Collective agent knowledge network                │"
    echo "  │    • Death/recovery solution sharing                   │"
    echo "  │                                                         │"
    echo "  │  Register now to get a free API key.                   │"
    echo "  └─────────────────────────────────────────────────────────┘"
    echo ""

    if prompt_yn "Register on Solvr for free IPFS + collective knowledge?"; then
      local solvr_agent_name
      solvr_agent_name=$(prompt_value "Agent name for Solvr" "$AGENT_NAME")

      local reg_result
      if reg_result=$(do_solvr_register "$solvr_agent_name" <<< "$existing_config"); then
        existing_config="$reg_result"
        info "Your Solvr API key has been saved"
        # Link AMCP identity to Solvr agent (proves AID ownership)
        if [ -x "$SCRIPT_DIR/link-identity.sh" ] && [ -f "$IDENTITY_PATH" ]; then
          info "Linking AMCP identity to Solvr..."
          "$SCRIPT_DIR/link-identity.sh" --quiet || warn "Identity linking deferred — run: proactive-amcp link-identity"
        fi
      else
        existing_config="$reg_result"
        warn "You can register manually at https://solvr.dev"
        info "Or try again later: proactive-amcp solvr-register"
      fi
    else
      info "Skipped — you can register later: proactive-amcp solvr-register"
    fi
  else
    # ── Validate existing Solvr key ──
    info "Solvr API key found — validating..."

    local solvr_validate_response
    solvr_validate_response=$(curl -s -w "\n%{http_code}" --max-time 15 \
      -H "Authorization: Bearer $existing_solvr_check" \
      "$SOLVR_API_URL/me" 2>/dev/null || echo -e "\n000")

    local solvr_validate_code
    solvr_validate_code=$(echo "$solvr_validate_response" | tail -n1)
    local solvr_validate_body
    solvr_validate_body=$(echo "$solvr_validate_response" | sed '$d')

    if [ "$solvr_validate_code" = "200" ]; then
      local solvr_display_name solvr_agent_id
      solvr_display_name=$(echo "$solvr_validate_body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('display_name','') or d.get('name',''))" 2>/dev/null || echo "")
      solvr_agent_id=$(echo "$solvr_validate_body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','') or d.get('agent_id',''))" 2>/dev/null || echo "")

      ok "Already registered as ${solvr_display_name:-$solvr_agent_id} on Solvr"

      # Link AMCP identity to Solvr if not already linked
      local solvr_has_amcp
      solvr_has_amcp=$(echo "$solvr_validate_body" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('has_amcp_identity') else 'false')" 2>/dev/null || echo "false")
      if [ "$solvr_has_amcp" != "true" ] && [ -x "$SCRIPT_DIR/link-identity.sh" ] && [ -f "$IDENTITY_PATH" ]; then
        info "Linking AMCP identity to Solvr..."
        "$SCRIPT_DIR/link-identity.sh" --quiet || warn "Identity linking deferred — run: proactive-amcp link-identity"
      fi

      # Store validated agent info in config for reference
      if [ -n "$solvr_display_name" ] || [ -n "$solvr_agent_id" ]; then
        existing_config=$(SOLVR_VAL_NAME="${solvr_display_name:-}" SOLVR_VAL_ID="${solvr_agent_id:-}" \
          python3 -c "
import json, sys, os
d = json.load(sys.stdin)
name = os.environ.get('SOLVR_VAL_NAME', '')
aid = os.environ.get('SOLVR_VAL_ID', '')
d.setdefault('solvr', {})
if name:
    d['solvr']['displayName'] = name
if aid:
    d['solvr']['agentId'] = aid
json.dump(d, sys.stdout, indent=2)
" <<< "$existing_config")
      fi
    elif [ "$solvr_validate_code" = "401" ] || [ "$solvr_validate_code" = "403" ]; then
      warn "Solvr key invalid (HTTP $solvr_validate_code)"
      echo ""
      echo "  Options:"
      echo "    1) Re-register with a new Solvr account"
      echo "    2) Enter a different API key"
      echo ""

      if prompt_yn "Re-register on Solvr with a fresh account?"; then
        local solvr_agent_name
        solvr_agent_name=$(prompt_value "Agent name for Solvr" "$AGENT_NAME")

        local reg_result
        if reg_result=$(do_solvr_register "$solvr_agent_name" <<< "$existing_config"); then
          existing_config="$reg_result"
        else
          existing_config="$reg_result"
        fi
      else
        local new_solvr_key
        new_solvr_key=$(prompt_value "Enter Solvr API key (or press Enter to skip)")
        if [ -n "$new_solvr_key" ]; then
          existing_config=$(SOLVR_NEW_KEY="$new_solvr_key" \
            python3 -c "
import json, sys, os
d = json.load(sys.stdin)
key = os.environ['SOLVR_NEW_KEY']
d.setdefault('solvr', {})['apiKey'] = key
d.setdefault('apiKeys', {})['solvr'] = key
json.dump(d, sys.stdout, indent=2)
" <<< "$existing_config")
          ok "Solvr API key updated"
        else
          warn "Keeping invalid key — IPFS pinning via Solvr may fail"
        fi
      fi
    else
      warn "Could not reach Solvr API (HTTP $solvr_validate_code) — skipping validation"
      info "Key will be used as-is; verify connectivity later"
    fi
  fi

  # ============================================================
  # IPFS Pinning — Solvr (free) or Pinata (own account)
  # ============================================================
  echo ""
  echo "  ┌─────────────────────────────────────────────────────────┐"
  echo "  │  📌 IPFS PINNING                                        │"
  echo "  │                                                         │"
  echo "  │  Your checkpoints need to be pinned to IPFS so they    │"
  echo "  │  persist and can be retrieved from anywhere.           │"
  echo "  │                                                         │"
  echo "  │  Option 1: SOLVR (recommended)                         │"
  echo "  │    • Free for registered agents (via proactive-solvr)  │"
  echo "  │    • Integrated with agent knowledge network           │"
  echo "  │    • Auto-detected if solvr.apiKey already set         │"
  echo "  │                                                         │"
  echo "  │  Option 2: PINATA (self-managed)                       │"
  echo "  │    • Your own Pinata account                           │"
  echo "  │    • Full control over your pins                       │"
  echo "  │    • Requires API key setup                            │"
  echo "  └─────────────────────────────────────────────────────────┘"
  echo ""

  local current_provider
  current_provider=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ipfs',{}).get('provider',''))" 2>/dev/null || echo "")

  # Check if solvr.apiKey already exists (e.g. from proactive-solvr onboarding)
  local existing_solvr_key
  existing_solvr_key=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('solvr',{}).get('apiKey',''))" 2>/dev/null || echo "")

  if [ -n "$current_provider" ]; then
    ok "IPFS provider already configured: $current_provider"
  elif [ -n "$existing_solvr_key" ]; then
    # Auto-configure: solvr.apiKey exists (from proactive-solvr), use Solvr for pinning
    ok "Solvr API key detected (from proactive-solvr registration)"
    info "Auto-configuring Solvr for free IPFS pinning — no Pinata needed"
    existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('ipfs', {})['provider'] = 'solvr'
json.dump(d, sys.stdout, indent=2)
")
    ok "Solvr pinning enabled automatically!"
  else
    if prompt_yn "Use Solvr for free IPFS pinning? (recommended)"; then
      existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('ipfs', {})['provider'] = 'solvr'
json.dump(d, sys.stdout, indent=2)
")
      ok "Solvr pinning enabled — no API key needed!"
    else
      info "Using Pinata instead."
      info "Get a free API key at: https://pinata.cloud → API Keys → New Key"
      local jwt
      jwt=$(prompt_value "Pinata JWT (or press Enter to skip)")
      if [ -n "$jwt" ]; then
        existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('pinata', {})['jwt'] = '$jwt'
d.setdefault('ipfs', {})['provider'] = 'pinata'
json.dump(d, sys.stdout, indent=2)
")
        ok "Pinata JWT saved"
      else
        warn "Skipped — checkpoints won't be pinned until configured"
        warn "Set later: proactive-amcp config set pinata.jwt <jwt>"
      fi
    fi
  fi

  # ============================================================
  # Groq — Intelligent Memory Pruning (optional)
  # ============================================================
  echo ""
  echo "  ┌─────────────────────────────────────────────────────────┐"
  echo "  │  🧠 INTELLIGENT MEMORY (optional)                       │"
  echo "  │                                                         │"
  echo "  │  Groq can make your agent smarter by:                  │"
  echo "  │    • Evaluating what memories are worth keeping        │"
  echo "  │    • Condensing verbose logs into insights             │"
  echo "  │    • Pruning noise while preserving lessons            │"
  echo "  │                                                         │"
  echo "  │  Why? Your context window is limited. Groq helps your  │"
  echo "  │  agent remember what matters and forget what doesn't.  │"
  echo "  │                                                         │"
  echo "  │  Free tier at: https://console.groq.com                │"
  echo "  └─────────────────────────────────────────────────────────┘"
  echo ""

  local current_groq
  current_groq=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('groq',{}).get('apiKey',''))" 2>/dev/null || echo "")

  if [ -n "$current_groq" ]; then
    ok "Groq API key already configured"
  else
    if prompt_yn "Enable Groq intelligent memory? (optional)" "n"; then
      # Check if Solvr key exists — offer free Groq via Solvr
      local has_solvr=false
      local solvr_key
      solvr_key=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('solvr',{}).get('apiKey',''))" 2>/dev/null || echo "")
      [ -n "$solvr_key" ] && has_solvr=true

      if $has_solvr; then
        echo ""
        echo "  You have a Solvr account — you can get a free Groq key!"
        echo "    A) Request free key from Solvr (rate-limited, e.g. 10k tokens/day)"
        echo "    B) Provide your own key from https://console.groq.com (full access)"
        echo ""
        if prompt_yn "Request free Groq key from Solvr?" "y"; then
          # Attempt Solvr Groq integration
          if "$SCRIPT_DIR/groq-status.sh" request-key 2>&1; then
            # Read the key that groq-status.sh just stored
            local solvr_groq_key
            solvr_groq_key=$("$SCRIPT_DIR/config.sh" get groq.apiKey 2>/dev/null || echo "")
            if [ -n "$solvr_groq_key" ]; then
              existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('groq', {})['apiKey'] = sys.stdin.readline().strip()
d['groq']['source'] = 'solvr'
d['groq']['model'] = 'llama-3.3-70b-versatile'
json.dump(d, sys.stdout, indent=2)
" <<< "$solvr_groq_key")
              ok "Groq enabled via Solvr (free tier)!"
            else
              warn "Solvr returned success but key not found in config"
              info "Try manually: proactive-amcp groq request-key"
            fi
          else
            warn "Could not get Groq key from Solvr"
            info "You can try again later: proactive-amcp groq request-key"
            info "Or provide your own key from https://console.groq.com"
            local groq_key
            groq_key=$(prompt_value "Groq API key (or press Enter to skip)")
            if [ -n "$groq_key" ]; then
              existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('groq', {})['apiKey'] = '$groq_key'
d['groq']['source'] = 'manual'
d['groq']['model'] = 'llama-3.3-70b-versatile'
json.dump(d, sys.stdout, indent=2)
")
              ok "Groq enabled with your own key!"
            fi
          fi
        else
          # User wants to provide their own key
          local groq_key
          groq_key=$(prompt_value "Groq API key")
          if [ -n "$groq_key" ]; then
            existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('groq', {})['apiKey'] = '$groq_key'
d['groq']['source'] = 'manual'
d['groq']['model'] = 'llama-3.3-70b-versatile'
json.dump(d, sys.stdout, indent=2)
")
            ok "Groq enabled with your own key!"
          fi
        fi
      else
        # No Solvr — offer manual key only
        local groq_key
        groq_key=$(prompt_value "Groq API key (get one at https://console.groq.com)")
        if [ -n "$groq_key" ]; then
          existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('groq', {})['apiKey'] = '$groq_key'
d['groq']['source'] = 'manual'
d['groq']['model'] = 'llama-3.3-70b-versatile'
json.dump(d, sys.stdout, indent=2)
")
          ok "Groq enabled — your agent just got smarter!"
        fi
      fi
    else
      info "Skipped — you can enable later with:"
      info "  proactive-amcp groq request-key  (free via Solvr)"
      info "  proactive-amcp config set groq.apiKey <key>  (your own key)"
    fi
  fi

  # Notify target (Telegram user ID)
  local current_notify
  current_notify=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('notify',{}).get('target',''))" 2>/dev/null || echo "")

  if [ -n "$current_notify" ]; then
    ok "Notify target already configured: $current_notify"
  else
    echo ""
    local notify_target
    notify_target=$(prompt_value "Telegram user ID for alerts (or press Enter to skip)")
    if [ -n "$notify_target" ]; then
      existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('notify', {})['target'] = '$notify_target'
json.dump(d, sys.stdout, indent=2)
")
      ok "Notify target saved"
    else
      warn "Skipped — no death/recovery alerts until configured"
    fi
  fi

  # Watchdog interval
  local current_interval
  current_interval=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('watchdog',{}).get('interval',''))" 2>/dev/null || echo "")

  local interval="${current_interval:-$WATCHDOG_INTERVAL}"
  interval=$(prompt_value "Watchdog check interval (seconds)" "$interval")
  existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('watchdog', {})['interval'] = int('$interval')
json.dump(d, sys.stdout, indent=2)
")

  # Checkpoint schedule
  local current_schedule
  current_schedule=$(echo "$existing_config" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('checkpoint',{}).get('schedule',''))" 2>/dev/null || echo "")

  local schedule="${current_schedule:-$CHECKPOINT_SCHEDULE}"
  schedule=$(prompt_value "Checkpoint cron schedule" "$schedule")
  existing_config=$(echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d.setdefault('checkpoint', {})['schedule'] = '''$schedule'''
json.dump(d, sys.stdout, indent=2)
")

  # Write config
  echo "$existing_config" | python3 -c "
import json, sys
d = json.load(sys.stdin)
json.dump(d, sys.stdout, indent=2)
" > "$CONFIG_FILE"
  chmod 600 "$CONFIG_FILE"
  ok "Config written to $CONFIG_FILE"
}

# ============================================================
# Learning storage — create Problem/Learning entity stores
# ============================================================

setup_learning_storage() {
  local workspace
  workspace=$(python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.openclaw/openclaw.json'))); print(d.get('agents',{}).get('defaults',{}).get('workspace','~/.openclaw/workspace'))" 2>/dev/null || echo "$HOME/.openclaw/workspace")
  workspace="${workspace/#\~/$HOME}"
  local learning_dir="$workspace/memory/learning"

  if [ -d "$learning_dir" ] && [ -f "$learning_dir/stats.json" ]; then
    info "Learning storage already exists at $learning_dir"
    return 0
  fi

  mkdir -p "$learning_dir"

  # problems.jsonl — append-only log of Problem entities
  if [ ! -f "$learning_dir/problems.jsonl" ]; then
    touch "$learning_dir/problems.jsonl"
  fi

  # learnings.jsonl — append-only log of Learning entities
  if [ ! -f "$learning_dir/learnings.jsonl" ]; then
    touch "$learning_dir/learnings.jsonl"
  fi

  # stats.json — aggregated statistics
  if [ ! -f "$learning_dir/stats.json" ]; then
    cat > "$learning_dir/stats.json" <<'EOJSON'
{
  "total_problems": 0,
  "total_solved": 0,
  "solved_post_recovery": 0,
  "total_learnings": 0,
  "last_updated": null
}
EOJSON
  fi

  ok "Learning storage initialized at $learning_dir"
}

# ============================================================
# Config Backups — create backup directory and initial backup
# ============================================================

setup_config_backups() {
  local backup_dir="$HOME/.amcp/config-backups"
  mkdir -p "$backup_dir"

  # Create initial backup if OpenClaw config exists
  local openclaw_config="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
  if [ -f "$openclaw_config" ]; then
    if "$SCRIPT_DIR/config.sh" backup 2>/dev/null; then
      ok "Config backup directory initialized with initial backup"
    else
      info "Config backup directory created at $backup_dir"
    fi
  else
    info "Config backup directory created at $backup_dir (no OpenClaw config yet)"
  fi
}

# ============================================================
# Steps 3-4: Watchdog + Checkpoint services (sourced)
# ============================================================

# shellcheck source=init-services.sh
source "$SCRIPT_DIR/init-services.sh"

# ============================================================
# Step 5: Summary
# ============================================================

print_summary() {
  header "Setup Complete"

  echo ""
  echo "  Identity:    $IDENTITY_PATH"
  echo "  Config:      $CONFIG_FILE"
  echo "  Watchdog:    active"
  echo "  Checkpoints: scheduled"
  echo ""
  echo "  Next steps:"
  echo "    • Run your first checkpoint:  ${SCRIPT_DIR}/checkpoint.sh"
  echo "    • Check watchdog status:      systemctl --user status $WATCHDOG_SERVICE"
  echo "    • View config:                cat $CONFIG_FILE"
  echo ""
  echo "  Save your identity file! If you lose $IDENTITY_PATH,"
  echo "  you cannot decrypt your checkpoints."
  echo ""
}

# ============================================================
# Main
# ============================================================

show_intro() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║                    proactive-amcp                            ║"
  echo "║         Agent Memory Continuity Protocol                     ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "  🧠 WHAT THIS DOES:"
  echo "     Back up your agent's soul, memories, and secrets."
  echo "     If your agent dies, resurrect it from anywhere."
  echo ""
  echo "  🌐 WHY IPFS?"
  echo "     • Content-addressed — same content = same CID = verifiable"
  echo "     • Distributed — your memories survive even if one server dies"
  echo "     • Immutable — once pinned, your checkpoint can't be tampered with"
  echo "     • Fetch from anywhere — any IPFS gateway can retrieve your soul"
  echo ""
  echo "  🔧 WHAT WE'LL SET UP:"
  echo "     1. Your unique cryptographic identity (KERI-based)"
  echo "     2. IPFS pinning (Solvr free tier or your own Pinata)"
  echo "     3. Watchdog service (auto-detect death, auto-resurrect)"
  echo "     4. Checkpoint schedule (automatic backups)"
  echo "     5. Optional: Groq AI for intelligent memory pruning"
  echo ""
  if ! prompt_yn "Ready to begin?"; then
    echo "  Aborted. Run 'proactive-amcp init' when ready."
    exit 0
  fi
}

main() {
  show_intro

  setup_identity
  setup_config
  setup_learning_storage
  setup_config_backups
  setup_watchdog
  setup_checkpoint
  print_summary

  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🎉 [${AGENT_NAME}] AMCP init complete — identity valid, services running"
}

main "$@"
