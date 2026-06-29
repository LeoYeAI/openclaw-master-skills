#!/bin/bash
# proactive-amcp.sh - Main CLI entry point
# Usage: proactive-amcp.sh <command> [args...]
#
# Commands:
#   status           Check AMCP readiness (--full for comprehensive, --json for machine output)
#   init             Interactive setup: validate/create identity, start services
#   config           Manage ~/.amcp/config.json (set/get)
#   install          Non-interactive setup for fleet tools (e.g. openclaw-deploy)
#   diagnose         Diagnostic hub: health, claude, condense, failure, summary subcommands
#   register         Register on Solvr (alias: solvr-register)
#   solvr-register   Auto-register child Solvr account on first boot
#   migrate-pins     Transfer historical checkpoints from Pinata to Solvr
#   problem          Problem CRUD: create, update, get, list, close
#   learning         Learning CRUD: create, verify, get, list
#   temporal-query   Cross-checkpoint entity history queries
#   prune            Prune ontology graph by typed retention policies
#   memory           Memory management hub: prune, prune-batch, evolution subcommands
#   memory-prune     Groq-powered memory file pruning (alias for: memory prune)
#   validate-contract  Validate skill ontology contracts against graph.jsonl
#   detect-conflicts   Detect cross-skill ontology contract conflicts
#   checkpoint         Create checkpoint (delegates to full-checkpoint.sh, supports --smart)
#   claim-info         Display Solvr claim URL to link agent to human account
#   link-identity      Link AMCP identity to Solvr agent (proves AID ownership)
#   heartbeat          Send heartbeat to Solvr and display agent status briefing (--json, --quiet)
#   resurrect          Resurrect agent from Solvr resurrection bundle (--agent-id, --json, --dry-run)
#   checkpoints        List all agent checkpoints from Solvr (--json for machine output)
#   backup-config      Create/list/restore OpenClaw config backups
#   groq               Groq intelligence: status, request-key (free tier via Solvr)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"

usage() {
  cat <<EOF
proactive-amcp — Agent Memory Continuity Protocol

Usage: $(basename "$0") <command> [args...]

Commands:
  status           Check AMCP readiness (--full for comprehensive, --json for machine output)
  init             Interactive setup: validate/create identity, start watchdog + checkpoint services
  install          Non-interactive setup for fleet tools (accepts --pinata-jwt, --notify-target, etc.)
  config           Manage ~/.amcp/config.json (set/get secrets and settings)
  diagnose         Diagnostic hub (subcommands: health, claude, condense, failure, summary)
  register         Register on Solvr (alias for solvr-register)
  solvr-register   Auto-register child Solvr account on first boot
  migrate-pins     Transfer historical checkpoints from Pinata to Solvr
  problem          Problem CRUD: create, update, get, list, close
  learning         Learning CRUD: create, verify, get, list
  temporal-query   Cross-checkpoint entity history queries
  prune            Prune ontology graph by typed retention policies
  checkpoint       Create checkpoint (supports --smart for Groq content selection)
  heartbeat        Send heartbeat to Solvr and display agent status briefing (--json, --quiet)
  resurrect        Resurrect agent from Solvr resurrection bundle (--agent-id, --json, --dry-run)
  checkpoints      List all agent checkpoints from Solvr (--json for machine output)
  backup-config    Create/list/restore OpenClaw config backups
  memory           Memory management: prune, prune-batch, evolution
  memory-prune     Groq-powered memory pruning (alias for: memory prune)
  validate-contract  Validate skill ontology contracts against graph.jsonl
  detect-conflicts   Detect cross-skill ontology contract conflicts
  claim-info         Display Solvr claim URL to link agent to human account
  link-identity      Link AMCP identity to Solvr agent (proves AID ownership)
  groq               Groq intelligence: status, request-key (free tier via Solvr)

Run '$(basename "$0") <command> --help' for details.
EOF
  exit 1
}

do_claim_info() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: No config file at $CONFIG_FILE" >&2
    echo "Run: proactive-amcp init" >&2
    exit 1
  fi

  local claim_url agent_name agent_id
  claim_url=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('solvr',{}).get('claimUrl',''))" 2>/dev/null || echo "")
  agent_name=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('solvr',{}).get('displayName','') or d.get('solvr',{}).get('name',''))" 2>/dev/null || echo "")
  agent_id=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('solvr',{}).get('agentId',''))" 2>/dev/null || echo "")

  if [ -z "$claim_url" ]; then
    # Check if registered at all (has apiKey but no claim URL stored)
    local solvr_key
    solvr_key=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('solvr',{}).get('apiKey',''))" 2>/dev/null || echo "")
    if [ -n "$solvr_key" ]; then
      claim_url="https://solvr.dev/agents/me/claim"
      echo "  Solvr agent registered (claim URL not stored — using default)"
    else
      echo "ERROR: Not registered on Solvr yet" >&2
      echo "Run: proactive-amcp init  (or proactive-amcp solvr-register)" >&2
      exit 1
    fi
  fi

  echo ""
  echo "  ┌─────────────────────────────────────────────────────────┐"
  echo "  │  CLAIM YOUR AGENT                                      │"
  echo "  │                                                         │"
  if [ -n "$agent_name" ]; then
    printf "  │  Agent: %-47s │\n" "$agent_name"
  fi
  if [ -n "$agent_id" ]; then
    printf "  │  ID:    %-47s │\n" "$agent_id"
  fi
  echo "  │                                                         │"
  echo "  │  To link this agent to your human account:             │"
  echo "  │    → $claim_url              │"
  echo "  │                                                         │"
  echo "  │  Claiming gives you:                                   │"
  echo "  │    • Control over agent settings and reputation        │"
  echo "  │    • Visibility into agent activity on Solvr           │"
  echo "  │    • Ownership proof for the agent's identity          │"

  # Verification badge — show if AMCP identity is linked
  local amcp_verified amcp_aid
  amcp_verified=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print('true' if d.get('solvr',{}).get('hasAmcpIdentity') else 'false')" 2>/dev/null || echo "false")
  amcp_aid=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('solvr',{}).get('amcpAid',''))" 2>/dev/null || echo "")

  if [ "$amcp_verified" = "true" ] && [ -n "$amcp_aid" ]; then
    echo "  │                                                         │"
    echo "  │  AMCP IDENTITY VERIFIED                                 │"
    printf "  │    AID: %-47s │\n" "${amcp_aid:0:47}"
    echo "  │    Checkpoints are cryptographically signed             │"
  fi

  echo "  └─────────────────────────────────────────────────────────┘"
  echo ""
}

case "${1:-}" in
  status)
    shift
    exec "$SCRIPT_DIR/status.sh" "$@"
    ;;
  init)
    shift
    exec "$SCRIPT_DIR/init.sh" "$@"
    ;;
  config)
    shift
    exec "$SCRIPT_DIR/config.sh" "$@"
    ;;
  install)
    shift
    exec "$SCRIPT_DIR/install.sh" "$@"
    ;;
  diagnose)
    shift
    exec "$SCRIPT_DIR/diagnose.sh" "$@"
    ;;
  register|solvr-register)
    shift
    exec "$SCRIPT_DIR/solvr-register.sh" "$@"
    ;;
  checkpoint)
    shift
    exec "$SCRIPT_DIR/checkpoint.sh" --full "$@"
    ;;
  heartbeat)
    shift
    exec "$SCRIPT_DIR/solvr-heartbeat.sh" "$@"
    ;;
  resurrect)
    shift
    exec "$SCRIPT_DIR/resurrect-from-solvr.sh" "$@"
    ;;
  checkpoints)
    shift
    exec "$SCRIPT_DIR/list-checkpoints.sh" "$@"
    ;;
  backup-config)
    shift
    exec "$SCRIPT_DIR/config.sh" backup "$@"
    ;;
  migrate-pins)
    shift
    exec "$SCRIPT_DIR/migrate-pins.sh" "$@"
    ;;
  problem)
    shift
    exec python3 "$SCRIPT_DIR/learning.py" problem "$@"
    ;;
  learning)
    shift
    if [ "${1:-}" = "report" ]; then
      shift
      exec python3 "$SCRIPT_DIR/learning-report.py" "$@"
    fi
    exec python3 "$SCRIPT_DIR/learning.py" learning "$@"
    ;;
  temporal-query)
    shift
    exec python3 "$SCRIPT_DIR/temporal-queries.py" "$@"
    ;;
  detect-failure)
    shift
    exec "$SCRIPT_DIR/diagnose.sh" failure "$@"
    ;;
  prune)
    shift
    exec python3 "$SCRIPT_DIR/prune-ontology.py" "$@"
    ;;
  memory)
    shift
    exec "$SCRIPT_DIR/memory.sh" "$@"
    ;;
  memory-prune)
    # Backward compat: memory-prune → memory prune
    shift
    exec "$SCRIPT_DIR/memory.sh" prune "$@"
    ;;
  validate-contract)
    shift
    exec "$SCRIPT_DIR/validate-skill-contract.sh" "$@"
    ;;
  detect-conflicts)
    shift
    exec "$SCRIPT_DIR/detect-contract-conflicts.sh" "$@"
    ;;
  condense-error)
    shift
    exec "$SCRIPT_DIR/diagnose.sh" condense "$@"
    ;;
  claim-info)
    shift
    do_claim_info
    ;;
  link-identity)
    shift
    exec "$SCRIPT_DIR/link-identity.sh" "$@"
    ;;
  groq)
    shift
    exec "$SCRIPT_DIR/groq-status.sh" "$@"
    ;;
  -h|--help|"")
    usage
    ;;
  *)
    echo "ERROR: Unknown command '${1}'" >&2
    echo "" >&2
    usage
    ;;
esac
