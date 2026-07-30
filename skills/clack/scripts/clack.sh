#!/usr/bin/env bash
# Clack CLI — thin wrapper
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." 2>/dev/null && pwd)" || SKILL_DIR=""

# If installed via symlink, resolve the real path
if [[ -L "$0" ]]; then
  REAL_PATH="$(readlink -f "$0")"
  SKILL_DIR="$(cd "$(dirname "$REAL_PATH")/.." && pwd)"
fi

usage() {
  echo "Usage: clack <command>"
  echo ""
  echo "Commands:"
  echo "  update      Pull latest code and restart"
  echo "  setup       Run interactive setup"
  echo "  uninstall   Remove Clack service and venv"
  echo "  pair        Generate a new pairing code"
  echo "  status      Show service status"
  echo "  logs        Tail service logs"
  echo "  restart     Restart the Clack service"
  echo ""
}

case "${1:-}" in
  update)
    echo "Updating Clack..."
    git -C "$SKILL_DIR" pull --ff-only && systemctl restart clack && echo "✓ Updated and restarted"
    ;;
  setup)
    bash "$SKILL_DIR/scripts/setup.sh" "${@:2}"
    ;;
  uninstall)
    bash "$SKILL_DIR/scripts/uninstall.sh"
    ;;
  pair)
    bash "$SKILL_DIR/scripts/pair.sh"
    ;;
  status)
    systemctl status clack 2>/dev/null || echo "Clack service not installed. Run: clack setup"
    ;;
  logs)
    journalctl -u clack -f
    ;;
  restart)
    systemctl restart clack && echo "✓ Clack restarted"
    ;;
  *)
    usage
    ;;
esac
