#!/bin/bash
# Uninstall Team Dispatch watcher from background scheduler.
# Usage:
#   bash <SKILL_DIR>/scripts/watch-uninstall.sh
#   bash <SKILL_DIR>/scripts/watch-uninstall.sh --backend auto|auto-system-first|openclaw-cron|launchd|systemd|cron
#   bash <SKILL_DIR>/scripts/watch-uninstall.sh --dry-run

set -euo pipefail

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

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="openclaw.team-dispatch.watch"
OLD_LABEL="team-dispatch.watch"
OS="$(uname -s)"

watcher_job_name() {
  node -e "
    try{
      const fs=require('fs');
      const home=process.env.HOME;
      const up=home+'/.openclaw/configs/team-dispatch.json';
      const sp='$SKILL_DIR/config.json';
      const p=fs.existsSync(up)?up:sp;
      const j=JSON.parse(fs.readFileSync(p,'utf8'));
      process.stdout.write(String(j.team?.watcher?.jobName||'Team Dispatch watcher'));
    }catch(e){process.stdout.write('Team Dispatch watcher');}
  "
}

uninstall_openclaw_cron() {
  if ! command -v openclaw >/dev/null 2>&1; then return 0; fi
  if ! openclaw cron status >/dev/null 2>&1; then return 0; fi

  local NAME JOB_ID
  NAME="$(watcher_job_name)"
  JOB_ID=$(openclaw cron list --json 2>/dev/null | node -e "
    let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{
      try{const j=JSON.parse(s);const jobs=j.jobs||j;const hit=(jobs||[]).find(x=>x.name==='${NAME}');
      process.stdout.write(hit?.jobId||hit?.id||'');}catch(e){process.stdout.write('');}
    });
  ")

  if [ -n "$JOB_ID" ]; then
    run openclaw cron rm "$JOB_ID"
    say "✅ removed OpenClaw cron job: $JOB_ID ($NAME)"
  else
    say "⏭️  no OpenClaw cron job found: $NAME"
  fi
}

uninstall_launchd() {
  # best-effort: remove both old and new labels for compatibility
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] launchctl bootout gui/$(id -u) $LABEL (best-effort)"
    echo "[dry-run] launchctl bootout gui/$(id -u) $OLD_LABEL (best-effort)"
  else
    launchctl bootout "gui/$(id -u)" "$LABEL" >/dev/null 2>&1 || true
    launchctl bootout "gui/$(id -u)" "$OLD_LABEL" >/dev/null 2>&1 || true
  fi
  say "✅ launchd unloaded: $LABEL (and $OLD_LABEL if existed)"
}

uninstall_systemd() {
  if ! command -v systemctl >/dev/null 2>&1; then
    say "⏭️  systemctl not found"; return 0
  fi
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] systemctl --user disable --now team-dispatch-watch.service (best-effort)"
  else
    systemctl --user disable --now team-dispatch-watch.service >/dev/null 2>&1 || true
  fi
  run rm -f "$HOME/.config/systemd/user/team-dispatch-watch.service"
  run systemctl --user daemon-reload
  say "✅ systemd service removed: team-dispatch-watch.service"
}

uninstall_cron() {
  if ! command -v crontab >/dev/null 2>&1; then
    say "⏭️  no crontab found"; return 0
  fi
  local CURRENT NEW
  CURRENT="$(crontab -l 2>/dev/null || true)"
  NEW="$(echo "$CURRENT" | grep -v "team-dispatch/scripts/watch.sh" || true)"
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] crontab remove entries containing team-dispatch/scripts/watch.sh"
  else
    printf '%s\n' "$NEW" | crontab -
  fi
  say "✅ removed crontab entries containing team-dispatch/scripts/watch.sh"
}

say "🧹 Uninstalling Team Dispatch watcher"
say "- requested backend: $BACKEND"

# auto modes: remove openclaw-cron best-effort + remove system scheduler for this OS
if [ "$BACKEND" = "auto" ] || [ "$BACKEND" = "auto-system-first" ]; then
  uninstall_openclaw_cron || true
  case "$OS" in
    Darwin) uninstall_launchd ;;
    Linux)  if command -v systemctl >/dev/null 2>&1; then uninstall_systemd; else uninstall_cron; fi ;;
    *)      uninstall_cron ;;
  esac
  exit 0
fi

case "$BACKEND" in
  openclaw-cron) uninstall_openclaw_cron ;;
  launchd) uninstall_launchd ;;
  systemd) uninstall_systemd ;;
  cron) uninstall_cron ;;
  *) echo "Unknown backend: $BACKEND"; exit 2 ;;
esac
