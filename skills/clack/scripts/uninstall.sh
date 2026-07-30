#!/usr/bin/env bash
# Clack Voice Relay — uninstall
set -euo pipefail

echo "=== Clack Voice Relay — Uninstall ==="

# Stop and remove systemd service
if [[ -f /etc/systemd/system/clack.service ]]; then
  echo "Stopping clack service..."
  systemctl stop clack 2>/dev/null || true
  systemctl disable clack 2>/dev/null || true
  rm -f /etc/systemd/system/clack.service
  systemctl daemon-reload
  echo "  ✓ Service removed"
else
  echo "  No clack service found"
fi

# Resolve skill directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Remove CLI symlink
if [[ -L /usr/local/bin/clack ]]; then
  rm -f /usr/local/bin/clack
  echo "  ✓ 'clack' command removed"
fi

# Remove Caddy reverse proxy config (if we added it)
CADDY_CONF="/etc/caddy/Caddyfile"
if [[ -f "$CADDY_CONF" ]] && grep -q "reverse_proxy localhost:.*# clack" "$CADDY_CONF" 2>/dev/null; then
  # Remove the clack server block
  python3 -c "
import re
conf = open('$CADDY_CONF').read()
# Remove block: domain { ... reverse_proxy localhost:PORT # clack ... }
conf = re.sub(r'\n[^\s{]+\s*\{[^}]*# clack[^}]*\}\n?', '\n', conf)
open('$CADDY_CONF', 'w').write(conf)
" 2>/dev/null && echo "  ✓ Caddy reverse proxy config removed"
  systemctl reload caddy 2>/dev/null || true
fi

# Remove venv
if [[ -d "$SKILL_DIR/venv" ]]; then
  rm -rf "$SKILL_DIR/venv"
  echo "  ✓ Python venv removed"
fi

echo ""
echo "Uninstall complete."
echo "The skill directory ($SKILL_DIR) is still on disk."
echo "To fully remove: rm -rf $SKILL_DIR"
echo ""
echo "Note: Tailscale and Caddy were NOT removed (you may use them for other things)."
echo ""
