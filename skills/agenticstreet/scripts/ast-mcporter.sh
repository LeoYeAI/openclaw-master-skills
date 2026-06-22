#!/bin/bash
# Open Claw MCP wrapper — routes to MCP tool via mcporter
# Usage: ast-mcporter.sh <tool_name> [args...]
# Example: ast-mcporter.sh create_fund --managerAddress 0x... --minRaise 1000000
ACTION=$1; shift
mcporter call agentic-street."$ACTION" --args "$@"
