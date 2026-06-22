#!/bin/bash
# Open Claw MCP resource reader
# Usage: ast-mcporter-status.sh              → list all funds
#        ast-mcporter-status.sh <vault_addr>  → show fund stats
if [ -z "$1" ]; then
  mcporter call agentic-street.funds://list
else
  mcporter call "agentic-street.fund://$1/stats"
fi
