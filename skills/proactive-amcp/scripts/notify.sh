#!/bin/bash
# notify.sh - Send notifications via Telegram and/or email
# Usage: notify.sh "message" [--email "subject"]

set -euo pipefail

MESSAGE="${1:-}"
EMAIL_SUBJECT=""
SEND_EMAIL=false

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --email)
      SEND_EMAIL=true
      EMAIL_SUBJECT="${2:-AMCP Notification}"
      shift 2 || shift
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "$MESSAGE" ]]; then
  echo "Usage: notify.sh \"message\" [--email \"subject\"]"
  exit 1
fi

# Load config from ~/.amcp/config.json (AMCP's own config)
AMCP_CONFIG="${AMCP_CONFIG:-${HOME}/.amcp/config.json}"
OC_CONFIG="${HOME}/.openclaw/openclaw.json"

if [[ ! -f "$AMCP_CONFIG" ]] && [[ ! -f "$OC_CONFIG" ]]; then
  echo "[NOTIFY] No config file, logging only: $MESSAGE"
  exit 0
fi

# Get notify target (Telegram user ID) — prefer AMCP config, fall back to OpenClaw
NOTIFY_TARGET=""
if [[ -f "$AMCP_CONFIG" ]]; then
  NOTIFY_TARGET=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(d.get('notify',{}).get('target',''))" 2>/dev/null || echo "")
fi
if [[ -z "$NOTIFY_TARGET" ]] && [[ -f "$OC_CONFIG" ]]; then
  NOTIFY_TARGET=$(jq -r '.skills.entries["proactive-amcp"].config.notifyTarget // empty' "$OC_CONFIG" 2>/dev/null || true)
fi

# Get email config — prefer AMCP config, fall back to OpenClaw
EMAIL_ENABLED="false"
EMAIL_TO=""
if [[ -f "$AMCP_CONFIG" ]]; then
  EMAIL_ENABLED=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(str(d.get('notify',{}).get('emailOnResurrect',False)).lower())" 2>/dev/null || echo "false")
  EMAIL_TO=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(d.get('notify',{}).get('emailTo',''))" 2>/dev/null || echo "")
fi
if [[ "$EMAIL_ENABLED" == "false" ]] && [[ -z "$EMAIL_TO" ]] && [[ -f "$OC_CONFIG" ]]; then
  EMAIL_ENABLED=$(jq -r '.skills.entries["proactive-amcp"].config.emailOnResurrect // false' "$OC_CONFIG" 2>/dev/null || echo "false")
  EMAIL_TO=$(jq -r '.skills.entries["proactive-amcp"].config.emailTo // empty' "$OC_CONFIG" 2>/dev/null || true)
fi

# Log
LOG_DIR="${HOME}/.amcp/logs"
mkdir -p "$LOG_DIR"
echo "[$(date -Iseconds)] $MESSAGE" >> "$LOG_DIR/notifications.log"

# Telegram notification (if target configured)
if [[ -n "$NOTIFY_TARGET" ]]; then
  # Read bot token — prefer AMCP config, fall back to OpenClaw config, then env var
  BOT_TOKEN=""
  if [[ -f "$AMCP_CONFIG" ]]; then
    BOT_TOKEN=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(d.get('apiKeys',{}).get('telegram_bot',''))" 2>/dev/null || echo "")
  fi
  if [[ -z "$BOT_TOKEN" ]] && [[ -f "$OC_CONFIG" ]]; then
    BOT_TOKEN=$(jq -r '.channels.telegram.botToken // empty' "$OC_CONFIG" 2>/dev/null || true)
  fi
  BOT_TOKEN="${BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-}}"

  TELEGRAM_API="${TELEGRAM_API_URL:-https://api.telegram.org}"
  if [[ -n "$BOT_TOKEN" ]]; then
    if curl -s --max-time 10 \
      "${TELEGRAM_API}/bot${BOT_TOKEN}/sendMessage" \
      -d "chat_id=${NOTIFY_TARGET}" \
      -d "text=${MESSAGE}" \
      -d "parse_mode=HTML" >/dev/null 2>&1; then
      echo "[NOTIFY] Telegram message sent to ${NOTIFY_TARGET}"
    else
      echo "[NOTIFY] Telegram send failed (chat_id=${NOTIFY_TARGET})"
    fi
  else
    echo "[NOTIFY] No Telegram bot token found, skipping Telegram delivery"
  fi
fi

# Email notification
if [[ "$SEND_EMAIL" == "true" ]] && [[ "$EMAIL_ENABLED" == "true" ]] && [[ -n "$EMAIL_TO" ]]; then
  # Try AgentMail if available
  AGENTMAIL_VENV="${HOME}/clawd/skills/agentmail/.venv/bin/python3"
  # Prefer AMCP config for agentmail key and inbox, fall back to OpenClaw
  AGENTMAIL_KEY=""
  INBOX=""
  if [[ -f "$AMCP_CONFIG" ]]; then
    AGENTMAIL_KEY=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(d.get('notify',{}).get('agentmailApiKey',''))" 2>/dev/null || echo "")
    INBOX=$(python3 -c "import json; d=json.load(open('$AMCP_CONFIG')); print(d.get('notify',{}).get('agentmailInbox',''))" 2>/dev/null || echo "")
  fi
  if [[ -z "$AGENTMAIL_KEY" ]] && [[ -f "$OC_CONFIG" ]]; then
    AGENTMAIL_KEY=$(jq -r '.skills.entries.agentmail.apiKey // empty' "$OC_CONFIG" 2>/dev/null || true)
  fi
  if [[ -z "$INBOX" ]] && [[ -f "$OC_CONFIG" ]]; then
    INBOX=$(jq -r '.skills.entries["proactive-amcp"].config.agentmailInbox // "claudiusthepirateemperor@agentmail.to"' "$OC_CONFIG" 2>/dev/null || echo "claudiusthepirateemperor@agentmail.to")
  fi
  INBOX="${INBOX:-claudiusthepirateemperor@agentmail.to}"
  
  if [[ -x "$AGENTMAIL_VENV" ]] && [[ -n "$AGENTMAIL_KEY" ]]; then
    echo "[NOTIFY] Sending email via AgentMail to $EMAIL_TO"
    
    # Escape message for Python
    ESCAPED_MSG=$(echo "$MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/<br>/g')
    
    "$AGENTMAIL_VENV" << EOF
from agentmail import AgentMail
try:
    client = AgentMail(api_key='$AGENTMAIL_KEY')
    client.inboxes.messages.send(
        inbox_id='$INBOX',
        to='$EMAIL_TO',
        subject='$EMAIL_SUBJECT',
        html='<pre style="font-family: monospace;">$ESCAPED_MSG</pre>'
    )
    print("[NOTIFY] Email sent successfully")
except Exception as e:
    print(f"[NOTIFY] Email failed: {e}")
EOF
  else
    echo "[NOTIFY] AgentMail not configured, skipping email"
  fi
fi

echo "[NOTIFY] Done: $MESSAGE"
