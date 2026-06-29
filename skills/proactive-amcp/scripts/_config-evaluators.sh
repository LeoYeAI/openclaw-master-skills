#!/bin/bash
# _config-evaluators.sh — Manage evaluators array and consensus config in ~/.amcp/config.json
# Invoked via: config.sh evaluators (or directly for backwards compat)
#
# Usage:
#   config-evaluators.sh list                    List configured evaluators
#   config-evaluators.sh add <type> [options]    Add an evaluator
#   config-evaluators.sh remove <type|index>     Remove an evaluator
#   config-evaluators.sh set-consensus <key> <val>  Set consensus config
#   config-evaluators.sh show                    Show evaluators + consensus config
#
# Options for add:
#   --model <model>     Model name (e.g. openai/gpt-oss-20b, llama3.2)
#   --weight <weight>   Weight for consensus (0-1, default 1.0)
#   --api-key <key>     API key for this evaluator
#
# Examples:
#   config-evaluators.sh add groq --model openai/gpt-oss-20b --weight 0.6
#   config-evaluators.sh add ollama --model llama3.2 --weight 0.4
#   config-evaluators.sh remove ollama
#   config-evaluators.sh set-consensus strategy weighted_average
#   config-evaluators.sh set-consensus minJudges 2

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"

# Known evaluator types
KNOWN_TYPES="groq ollama openai anthropic"

usage() {
  cat <<EOF
proactive-amcp config evaluators — Manage evaluator configuration

Usage:
  config evaluators list                         List configured evaluators
  config evaluators add <type> [options]         Add an evaluator
  config evaluators remove <type|index>          Remove an evaluator by type or index
  config evaluators set-consensus <key> <value>  Set consensus config option
  config evaluators show                         Show evaluators + consensus config

Add options:
  --model <model>     Model name (e.g. openai/gpt-oss-20b, llama3.2)
  --weight <weight>   Weight for consensus (0.0-1.0, default 1.0)
  --api-key <key>     API key for this evaluator instance

Evaluator types: $KNOWN_TYPES

Consensus keys:
  strategy              weighted_average | majority | unanimous | quorum
  minJudges             Minimum evaluators required (default: 2)
  quorumThreshold       For quorum strategy (0-1, default: 0.66)
  tieBreaker            keep | discard | escalate (default: keep)
  disagreementThreshold Variance that triggers escalation (0-1, default: 0.3)

Examples:
  config evaluators add groq --model openai/gpt-oss-20b --weight 0.6
  config evaluators add ollama --model llama3.2 --weight 0.4
  config evaluators remove ollama
  config evaluators set-consensus strategy weighted_average
  config evaluators set-consensus minJudges 2
  config evaluators show

Config path: $CONFIG_FILE
EOF
  exit 1
}

# Ensure config file exists
ensure_config_file() {
  local config_dir
  config_dir="$(dirname "$CONFIG_FILE")"
  mkdir -p "$config_dir"
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "{}" > "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
  fi
}

# ============================================================
# list — Show configured evaluators
# ============================================================
do_list() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "(no config file — default: single groq evaluator)"
    exit 0
  fi

  python3 << 'PYEOF'
import json, os, sys

config_path = os.path.expanduser(os.environ.get("_CE_CONFIG", "~/.amcp/config.json"))
try:
    with open(config_path) as f:
        cfg = json.load(f)
except (IOError, json.JSONDecodeError):
    cfg = {}

evaluators = cfg.get("evaluators", [])
if not evaluators:
    print("(no evaluators configured — default: single groq evaluator)")
    sys.exit(0)

print(f"Configured evaluators ({len(evaluators)}):")
for i, ev in enumerate(evaluators):
    ev_type = ev.get("type", "unknown")
    model = ev.get("model", "(default)")
    weight = ev.get("weight", 1.0)
    has_key = "yes" if ev.get("apiKey") else "no"
    print(f"  [{i}] type={ev_type}  model={model}  weight={weight}  apiKey={has_key}")
PYEOF
}

# ============================================================
# add — Add an evaluator to the array
# ============================================================
do_add() {
  local eval_type="${1:-}"
  shift || true

  if [ -z "$eval_type" ]; then
    echo "ERROR: Usage: config evaluators add <type> [--model MODEL] [--weight WEIGHT] [--api-key KEY]" >&2
    exit 1
  fi

  # Warn on unknown types (don't block — allow custom adapters)
  local known=false
  for t in $KNOWN_TYPES; do
    [ "$t" = "$eval_type" ] && known=true
  done
  if ! $known; then
    echo "WARNING: '$eval_type' is not a known evaluator type ($KNOWN_TYPES)" >&2
    echo "  Make sure scripts/lib/evaluators/${eval_type}.sh exists" >&2
  fi

  # Parse options
  local model="" weight="" api_key=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --model)   model="${2:-}"; shift 2 ;;
      --weight)  weight="${2:-}"; shift 2 ;;
      --api-key) api_key="${2:-}"; shift 2 ;;
      *)
        echo "ERROR: Unknown option '$1'" >&2
        exit 1
        ;;
    esac
  done

  # Validate weight if provided
  if [ -n "$weight" ]; then
    python3 -c "
w = float('$weight')
assert 0.0 <= w <= 1.0, f'Weight must be 0.0-1.0, got {w}'
" 2>/dev/null || { echo "ERROR: Weight must be a number between 0.0 and 1.0" >&2; exit 1; }
  fi

  ensure_config_file

  _CE_CONFIG="$CONFIG_FILE" \
  _CE_TYPE="$eval_type" \
  _CE_MODEL="$model" \
  _CE_WEIGHT="$weight" \
  _CE_APIKEY="$api_key" \
  python3 << 'PYEOF'
import json, os

config_path = os.path.expanduser(os.environ["_CE_CONFIG"])
eval_type = os.environ["_CE_TYPE"]
model = os.environ["_CE_MODEL"]
weight = os.environ["_CE_WEIGHT"]
api_key = os.environ["_CE_APIKEY"]

with open(config_path) as f:
    cfg = json.load(f)

evaluators = cfg.get("evaluators", [])

# Check for duplicate type
for ev in evaluators:
    if ev.get("type") == eval_type:
        print(f"WARNING: Evaluator '{eval_type}' already configured — updating")
        if model:
            ev["model"] = model
        if weight:
            ev["weight"] = float(weight)
        if api_key:
            ev["apiKey"] = api_key
        with open(config_path, "w") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")
        print(f"Updated evaluator: {eval_type}")
        raise SystemExit(0)

# Build new evaluator entry
entry = {"type": eval_type}
if model:
    entry["model"] = model
if weight:
    entry["weight"] = float(weight)
if api_key:
    entry["apiKey"] = api_key

evaluators.append(entry)
cfg["evaluators"] = evaluators

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")

print(f"Added evaluator: {eval_type} (total: {len(evaluators)})")
PYEOF

  chmod 600 "$CONFIG_FILE"
}

# ============================================================
# remove — Remove an evaluator by type or index
# ============================================================
do_remove() {
  local target="${1:-}"

  if [ -z "$target" ]; then
    echo "ERROR: Usage: config evaluators remove <type|index>" >&2
    exit 1
  fi

  if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: No config file at $CONFIG_FILE" >&2
    exit 1
  fi

  _CE_CONFIG="$CONFIG_FILE" \
  _CE_TARGET="$target" \
  python3 << 'PYEOF'
import json, os, sys

config_path = os.path.expanduser(os.environ["_CE_CONFIG"])
target = os.environ["_CE_TARGET"]

with open(config_path) as f:
    cfg = json.load(f)

evaluators = cfg.get("evaluators", [])

if not evaluators:
    print("No evaluators configured — nothing to remove")
    sys.exit(0)

# Try as index first
removed = None
try:
    idx = int(target)
    if 0 <= idx < len(evaluators):
        removed = evaluators.pop(idx)
    else:
        print(f"ERROR: Index {idx} out of range (0-{len(evaluators)-1})", file=sys.stderr)
        sys.exit(1)
except ValueError:
    # Try as type name
    for i, ev in enumerate(evaluators):
        if ev.get("type") == target:
            removed = evaluators.pop(i)
            break

if removed is None:
    print(f"ERROR: No evaluator matching '{target}' found", file=sys.stderr)
    sys.exit(1)

cfg["evaluators"] = evaluators

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")

print(f"Removed evaluator: {removed.get('type', 'unknown')} (remaining: {len(evaluators)})")
PYEOF

  chmod 600 "$CONFIG_FILE"
}

# ============================================================
# set-consensus — Set a consensus config key
# ============================================================
do_set_consensus() {
  local key="${1:-}"
  local value="${2:-}"

  if [ -z "$key" ] || [ -z "$value" ]; then
    echo "ERROR: Usage: config evaluators set-consensus <key> <value>" >&2
    echo "  Keys: strategy, minJudges, quorumThreshold, tieBreaker, disagreementThreshold" >&2
    exit 1
  fi

  # Validate key
  case "$key" in
    strategy)
      case "$value" in
        weighted_average|majority|unanimous|quorum) ;;
        *) echo "ERROR: strategy must be one of: weighted_average, majority, unanimous, quorum" >&2; exit 1 ;;
      esac
      ;;
    minJudges)
      python3 -c "assert int('$value') >= 1" 2>/dev/null || {
        echo "ERROR: minJudges must be a positive integer" >&2; exit 1
      }
      ;;
    quorumThreshold|disagreementThreshold)
      python3 -c "v = float('$value'); assert 0.0 <= v <= 1.0" 2>/dev/null || {
        echo "ERROR: $key must be a number between 0.0 and 1.0" >&2; exit 1
      }
      ;;
    tieBreaker)
      case "$value" in
        keep|discard|escalate) ;;
        *) echo "ERROR: tieBreaker must be one of: keep, discard, escalate" >&2; exit 1 ;;
      esac
      ;;
    *)
      echo "WARNING: Unknown consensus key '$key' — setting anyway" >&2
      ;;
  esac

  ensure_config_file

  _CE_CONFIG="$CONFIG_FILE" \
  _CE_KEY="$key" \
  _CE_VALUE="$value" \
  python3 << 'PYEOF'
import json, os

config_path = os.path.expanduser(os.environ["_CE_CONFIG"])
key = os.environ["_CE_KEY"]
value = os.environ["_CE_VALUE"]

with open(config_path) as f:
    cfg = json.load(f)

consensus = cfg.get("consensus", {})

# Type coercion
if value.lower() == "true":
    value = True
elif value.lower() == "false":
    value = False
else:
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass

consensus[key] = value
cfg["consensus"] = consensus

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")

print(f"Set consensus.{key} = {value}")
PYEOF

  chmod 600 "$CONFIG_FILE"
}

# ============================================================
# show — Show evaluators + consensus config together
# ============================================================
do_show() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "(no config file — using defaults)"
    echo ""
    echo "Evaluators: [single groq evaluator (default)]"
    echo "Consensus:  weighted_average, minJudges=2, tieBreaker=keep"
    exit 0
  fi

  _CE_CONFIG="$CONFIG_FILE" \
  python3 << 'PYEOF'
import json, os

config_path = os.path.expanduser(os.environ["_CE_CONFIG"])
try:
    with open(config_path) as f:
        cfg = json.load(f)
except (IOError, json.JSONDecodeError):
    cfg = {}

# Evaluators
evaluators = cfg.get("evaluators", [])
if not evaluators:
    print("Evaluators: (none configured — default: single groq evaluator)")
else:
    print(f"Evaluators ({len(evaluators)}):")
    for i, ev in enumerate(evaluators):
        ev_type = ev.get("type", "unknown")
        model = ev.get("model", "(default)")
        weight = ev.get("weight", 1.0)
        has_key = "configured" if ev.get("apiKey") else "not set"
        print(f"  [{i}] {ev_type}: model={model}, weight={weight}, apiKey={has_key}")

print("")

# Consensus
consensus = cfg.get("consensus", {})
if not consensus:
    print("Consensus: (not configured — defaults apply)")
    print("  strategy: weighted_average")
    print("  minJudges: 2")
    print("  quorumThreshold: 0.66")
    print("  tieBreaker: keep")
    print("  disagreementThreshold: 0.3")
else:
    print("Consensus:")
    defaults = {
        "strategy": "weighted_average",
        "minJudges": 2,
        "quorumThreshold": 0.66,
        "tieBreaker": "keep",
        "disagreementThreshold": 0.3,
    }
    for key in ["strategy", "minJudges", "quorumThreshold", "tieBreaker", "disagreementThreshold"]:
        val = consensus.get(key, defaults.get(key))
        is_default = key not in consensus
        suffix = " (default)" if is_default else ""
        print(f"  {key}: {val}{suffix}")

    # Show any extra keys
    for key in sorted(consensus.keys()):
        if key not in defaults:
            print(f"  {key}: {consensus[key]}")
PYEOF
}

# ============================================================
# Main
# ============================================================

SUBCOMMAND="${1:-}"
shift || true

case "$SUBCOMMAND" in
  list)
    _CE_CONFIG="$CONFIG_FILE" do_list
    ;;
  add)
    do_add "$@"
    ;;
  remove)
    do_remove "$@"
    ;;
  set-consensus)
    do_set_consensus "$@"
    ;;
  show)
    do_show
    ;;
  -h|--help|"")
    usage
    ;;
  *)
    echo "ERROR: Unknown evaluators command '$SUBCOMMAND'" >&2
    usage
    ;;
esac
