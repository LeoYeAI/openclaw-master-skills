#!/bin/bash
# Install Team Dispatch watcher as a cross-platform background task.
# Supports:
# - macOS: LaunchAgent (launchctl)
# - Linux: systemd --user service (preferred) or crontab @reboot fallback
#
# Usage:
#   bash <SKILL_DIR>/scripts/watch-install.sh
#   INTERVAL=300 GRACE=20 bash <SKILL_DIR>/scripts/watch-install.sh
#   bash <SKILL_DIR>/scripts/watch-install.sh --backend auto|openclaw-cron|launchd|systemd|cron
#   bash <SKILL_DIR>/scripts/watch-install.sh --dry-run

set -e

BACKEND="auto"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --backend) BACKEND="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run]'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

say() { echo "$@"; }

INTERVAL=${INTERVAL:-300}
GRACE=${GRACE:-20}

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_TPL="$SKILL_DIR/assets/launchd/openclaw.team-dispatch.watch.plist.xml"
PLIST_DST="$HOME/Library/LaunchAgents/openclaw.team-dispatch.watch.plist"
LABEL="openclaw.team-dispatch.watch"

OS="$(uname -s)"

choose_backend() {
  if [ "$BACKEND" != "auto" ] && [ "$BACKEND" != "auto-system-first" ]; then
    echo "$BACKEND"; return
  fi

  # Default strategy: system scheduler first (no model tokens), then OpenClaw cron fallback.
  case "$OS" in
    Darwin)
      echo "launchd"; return
      ;;
    Linux)
      if command -v systemctl >/dev/null 2>&1; then echo "systemd"; else echo "cron"; fi
      return
      ;;
    *)
      # unknown OS: prefer classic cron
      echo "cron"; return
      ;;
  esac
}

B="$(choose_backend)"

say "🧭 Installing Team Dispatch watcher"
say "- requested backend: $BACKEND"
say "- selected backend: $B"
say "- INTERVAL=$INTERVAL GRACE=$GRACE"

try_openclaw_fallback() {
  # Only in auto modes.
  if [ "$BACKEND" != "auto" ] && [ "$BACKEND" != "auto-system-first" ]; then
    return 1
  fi
  if command -v openclaw >/dev/null 2>&1 && openclaw cron status >/dev/null 2>&1; then
    echo "⚠️  system scheduler install failed; trying OpenClaw cron fallback..." >&2
    install_openclaw_cron
    return $?
  fi
  return 1
}

install_openclaw_cron() {
  # Create/patch a cron job that runs watch.py once per interval.
  # It runs as an isolated agent turn under agentId=main and does not deliver output.
  # Configurable via ~/.openclaw/configs/team-dispatch.json (team.watcher.jobName/jobDescription)
  # Prefer user override; else fall back to skill root config.json
  NAME=$(node -e "try{const fs=require('fs');const home=process.env.HOME;const up=home+'/.openclaw/configs/team-dispatch.json';const sp='$SKILL_DIR/config.json';const p=fs.existsSync(up)?up:sp;const j=JSON.parse(fs.readFileSync(p,'utf8'));process.stdout.write(String(j.team?.watcher?.jobName||'Team Dispatch watcher'));}catch(e){process.stdout.write('Team Dispatch watcher');}")
  DESC=$(node -e "try{const fs=require('fs');const home=process.env.HOME;const up=home+'/.openclaw/configs/team-dispatch.json';const sp='$SKILL_DIR/config.json';const p=fs.existsSync(up)?up:sp;const j=JSON.parse(fs.readFileSync(p,'utf8'));process.stdout.write(String(j.team?.watcher?.jobDescription||'Low-frequency reconciliation: scan tasks/active for overdue in-progress tasks and reset to pending when retries remain.'));}catch(e){process.stdout.write('Low-frequency reconciliation: scan tasks/active for overdue in-progress tasks and reset to pending when retries remain.');}")
  EVERY="${INTERVAL}s"
  WATCH_PY="$HOME/.openclaw/skills/team-dispatch/scripts/watch.py"

  if [ ! -f "$WATCH_PY" ]; then
    echo "Missing watcher script at $WATCH_PY (is the skill symlink installed?)" >&2
    return 2
  fi

  MSG=$(cat <<EOF
Run Team Dispatch watcher once.

Execute:
python3 "$WATCH_PY" --once --tasks-dir "$HOME/.openclaw/workspace/tasks" --grace $GRACE

If command fails, print the error and exit nonzero.
EOF
)

  # Find existing job by name
  JOB_ID=$(openclaw cron list --json 2>/dev/null | node -e "
    const fs=require('fs');
    let s=''; process.stdin.on('data',d=>s+=d); process.stdin.on('end',()=>{
      try{const j=JSON.parse(s); const jobs=j.jobs||j; const hit=(jobs||[]).find(x=>x.name==='${NAME}');
      process.stdout.write(hit?.jobId||hit?.id||'');}catch(e){process.stdout.write('');}
    });
  ")

  if [ -n "$JOB_ID" ]; then
    openclaw cron edit "$JOB_ID" \
      --every "$EVERY" \
      --session isolated \
      --agent main \
      --message "$MSG" \
      --no-deliver \
      --description "$DESC" >/dev/null
    echo "✅ OpenClaw cron watcher updated: $JOB_ID"
  else
    JOB_ID=$(openclaw cron add \
      --name "$NAME" \
      --every "$EVERY" \
      --session isolated \
      --agent main \
      --message "$MSG" \
      --no-deliver \
      --description "$DESC" \
      --json | node -e "let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{try{const j=JSON.parse(s);process.stdout.write(j.jobId||j.id||'');}catch(e){process.stdout.write('');}});")
    echo "✅ OpenClaw cron watcher installed: $JOB_ID"
  fi
}

# If system scheduler install fails in auto modes, fall back to OpenClaw cron (token-costly but managed).
if [ "$BACKEND" = "auto" ] || [ "$BACKEND" = "auto-system-first" ]; then
  # We'll attempt system scheduler first via selected B.
  :
fi

if [ "$B" = "openclaw-cron" ]; then
  if command -v openclaw >/dev/null 2>&1; then
    if install_openclaw_cron; then
      exit 0
    fi
  fi

  # If explicitly requested openclaw-cron, do not fallback.
  if [ "$BACKEND" = "openclaw-cron" ]; then
    echo "Failed to install watcher via OpenClaw cron" >&2
    exit 1
  fi

  # Auto mode fallback continues below.
  echo "⚠️  OpenClaw cron install failed; falling back to system scheduler..." >&2
  case "$OS" in
    Darwin) B="launchd";;
    Linux)  if command -v systemctl >/dev/null 2>&1; then B="systemd"; else B="cron"; fi ;;
    *)      B="cron";;
  esac
fi

if [ "$B" = "launchd" ]; then
  if [ ! -f "$PLIST_TPL" ]; then
    echo "Missing plist template: $PLIST_TPL" >&2
    if try_openclaw_fallback; then exit 0; fi
    exit 1
  fi

  mkdir -p "$HOME/Library/LaunchAgents"
  WATCH_SH="$HOME/.openclaw/skills/team-dispatch/scripts/watch.sh"
  STDOUT_LOG="$HOME/.openclaw/workspace/tasks/watch.out.log"
  STDERR_LOG="$HOME/.openclaw/workspace/tasks/watch.err.log"
  mkdir -p "$(dirname "$STDOUT_LOG")"

  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] render plist: $PLIST_TPL -> $PLIST_DST"
  else
    python3 - <<PY
import os, plistlib
src = os.path.expanduser("$PLIST_TPL")
dst = os.path.expanduser("$PLIST_DST")
home = os.path.expanduser("~")
with open(src, "rb") as f:
    data = plistlib.load(f)
data["ProgramArguments"] = ["/bin/bash", os.path.join(home, ".openclaw/skills/team-dispatch/scripts/watch.sh")]
data["StandardOutPath"] = os.path.join(home, ".openclaw/workspace/tasks/watch.out.log")
data["StandardErrorPath"] = os.path.join(home, ".openclaw/workspace/tasks/watch.err.log")
data["EnvironmentVariables"] = {
    **(data.get("EnvironmentVariables") or {}),
    "INTERVAL": str(os.environ.get("INTERVAL", "$INTERVAL")),
    "GRACE": str(os.environ.get("GRACE", "$GRACE")),
}
with open(dst, "wb") as f:
    plistlib.dump(data, f)
PY
  fi

  # Note: keep env in both plist and launchctl setenv so manual reruns inherit overrides too.
  run launchctl setenv INTERVAL "$INTERVAL"
  run launchctl setenv GRACE "$GRACE"

  # best-effort unload previous (try bootout first, then remove as fallback)
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] launchctl bootout gui/$(id -u) $LABEL (best-effort)"
  else
    if ! launchctl bootout "gui/$(id -u)" "$LABEL" >/dev/null 2>&1; then
      # bootout may fail with EIO if service is in bad state; try remove as fallback
      launchctl remove "$LABEL" >/dev/null 2>&1 || true
    fi
  fi
  run launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
  say "✅ LaunchAgent installed: $LABEL"
  exit 0
fi

if [ "$B" = "systemd" ]; then
  if ! command -v systemctl >/dev/null 2>&1; then
    echo "systemctl not found" >&2
    if try_openclaw_fallback; then exit 0; fi
    exit 1
  fi
  UNIT_DIR="$HOME/.config/systemd/user"
  mkdir -p "$UNIT_DIR"

  # Render unit with correct path to this skill dir.
  SERVICE_DST="$UNIT_DIR/team-dispatch-watch.service"
  cat > "$SERVICE_DST" <<EOF
[Unit]
Description=Team Dispatch low-frequency watcher
After=network.target

[Service]
Type=simple
Environment=INTERVAL=$INTERVAL
Environment=GRACE=$GRACE
ExecStart=/bin/bash $SKILL_DIR/scripts/watch.sh
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

  run systemctl --user daemon-reload
  run systemctl --user enable --now team-dispatch-watch.service
  say "✅ systemd --user service installed: team-dispatch-watch.service"
  exit 0
fi

if [ "$B" = "cron" ]; then
  # Fallback: install @reboot entry that starts watch.sh in background.
  # We do a best-effort idempotent install.
  LINE="@reboot INTERVAL=$INTERVAL GRACE=$GRACE /bin/bash $SKILL_DIR/scripts/watch.sh >> $HOME/.openclaw/workspace/tasks/watch.out.log 2>> $HOME/.openclaw/workspace/tasks/watch.err.log &"

  if command -v crontab >/dev/null 2>&1; then
    CURRENT="$(crontab -l 2>/dev/null || true)"
    if echo "$CURRENT" | grep -F "team-dispatch/scripts/watch.sh" >/dev/null 2>&1; then
      say "⏭️  cron entry already exists (skip)"
    else
      NEW="$CURRENT
$LINE"
      if [ "$DRY_RUN" = "1" ]; then
        echo "[dry-run] crontab install line: $LINE"
      else
        printf '%s\n' "$NEW" | crontab -
      fi
      say "✅ crontab @reboot installed"
    fi
    exit 0
  fi

  echo "No supported scheduler found (no launchctl/systemctl/crontab)." >&2
  if try_openclaw_fallback; then exit 0; fi
  exit 1
fi

echo "Unknown backend: $B"; exit 2
