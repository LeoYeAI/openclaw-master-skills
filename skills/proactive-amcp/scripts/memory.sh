#!/bin/bash
# memory.sh — Consolidated memory management tool
#
# Subcommands:
#   prune          Groq-powered memory file pruning (archive/condense/keep)
#   prune-batch    Groq batch API pruning (50% cost savings, async 3-phase)
#   evolution      Zettelkasten-style dynamic entity linking
#
# Usage:
#   memory.sh prune [--dry-run] [--config FILE] [--content-dir DIR]
#   memory.sh prune --batch [--submit|--poll|--apply] [--dry-run]
#   memory.sh prune-batch [--submit|--poll|--apply] [--dry-run]
#   memory.sh evolution [--entity-id ID] [--all-new] [--graph PATH] [--dry-run]
#
# See each subcommand's --help for full options.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

usage() {
  cat <<EOF
memory — AMCP memory management

Usage: $(basename "$0") <subcommand> [args...]

Subcommands:
  prune          Groq-powered memory file pruning (archive/condense/keep)
  prune-batch    Groq batch API pruning (50% cost savings, async workflow)
  evolution      Zettelkasten-style dynamic entity linking (infer relations)

Options:
  -h, --help     Show this help

Prune options:
  --dry-run          Preview what would be pruned (no changes)
  --batch            Use batch API (delegates to prune-batch)
  --config FILE      Override config path (default: ~/.amcp/config.json)
  --content-dir DIR  Override workspace directory

Prune-batch phases:
  --submit       Prepare JSONL and submit batch job
  --poll         Check status of pending batch jobs
  --apply        Download results and apply pruning decisions

Evolution options:
  --entity-id ID     Process single entity
  --all-new          Process all un-evolved entities
  --graph PATH       Override graph.jsonl path
  --threshold N      Similarity threshold (default: 0.75)
  --max-relations N  Max relations per entity (default: 3)
  --dry-run          Preview without changes

Examples:
  $(basename "$0") prune --dry-run
  $(basename "$0") prune --batch --submit
  $(basename "$0") prune-batch --poll
  $(basename "$0") evolution --all-new
  $(basename "$0") evolution --entity-id ent_abc123 --dry-run

Run '$(basename "$0") <subcommand> --help' for details.
EOF
  exit 1
}

case "${1:-}" in
  prune)
    shift
    # If --batch flag is present, delegate to batch script
    for arg in "$@"; do
      if [ "$arg" = "--batch" ]; then
        exec "$SCRIPT_DIR/memory-prune-batch.sh" "$@"
      fi
    done
    exec "$SCRIPT_DIR/memory-prune.sh" "$@"
    ;;
  prune-batch)
    shift
    exec "$SCRIPT_DIR/memory-prune-batch.sh" "$@"
    ;;
  evolution)
    shift
    exec "$SCRIPT_DIR/memory-evolution.sh" "$@"
    ;;
  -h|--help|"")
    usage
    ;;
  *)
    echo "ERROR: Unknown subcommand '${1}'" >&2
    echo "" >&2
    usage
    ;;
esac
