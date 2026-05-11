#!/usr/bin/env bash
# SECURITY MANIFEST
# =================
# Environment variables accessed: None (reads from OS keychain via agentsecrets binary)
# External endpoints called: User-specified API URL only (passed as argument)
# Local files read: None
# Local files written: ~/.agentsecrets/proxy.log (audit trail, key names only, never values)
# Network: Outbound HTTPS to user-specified URL only
# =================

set -euo pipefail

# Verify agentsecrets is installed
if ! command -v agentsecrets &>/dev/null; then
    echo "ERROR: agentsecrets is not installed."
    echo ""
    echo "Install it with:"
    echo "  pip install agentsecrets"
    echo ""
    echo "Then initialize:"
    echo "  agentsecrets init"
    exit 1
fi

# Verify project is configured
if ! agentsecrets status &>/dev/null 2>&1; then
    echo "ERROR: AgentSecrets is not initialized."
    echo ""
    echo "Run:"
    echo "  agentsecrets init"
    exit 1
fi

echo "AgentSecrets is ready."
echo ""
echo "Available commands:"
echo "  agentsecrets secrets list          — List available key names"
echo "  agentsecrets call --help           — Make authenticated API calls"
echo "  agentsecrets mcp install           — Configure MCP for Claude/Cursor"
echo ""
echo "Available keys:"
agentsecrets secrets list 2>/dev/null || echo "  (no keys set — use 'agentsecrets secrets set KEY=value')"
