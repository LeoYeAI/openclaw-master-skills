#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_OPENCLAW=0
INSTALL_HERMES=0
DRY_RUN=0
FORCE=0

usage() {
  cat <<'EOF'
Usage: bash scripts/install.sh [--both|--openclaw|--hermes] [--dry-run] [--force]

Installs Mai as a local skill by symlinking this directory into:
  OpenClaw: ~/.openclaw/workspace/skills/mai
  Hermes:   ~/.hermes/skills/commerce/mai

Environment overrides:
  OPENCLAW_HOME  default: ~/.openclaw
  HERMES_HOME    default: ~/.hermes
EOF
}

if [ "$#" -eq 0 ]; then
  INSTALL_OPENCLAW=1
  INSTALL_HERMES=1
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --both)
      INSTALL_OPENCLAW=1
      INSTALL_HERMES=1
      ;;
    --openclaw)
      INSTALL_OPENCLAW=1
      ;;
    --hermes)
      INSTALL_HERMES=1
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    --force)
      FORCE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ "$INSTALL_OPENCLAW" -eq 0 ] && [ "$INSTALL_HERMES" -eq 0 ]; then
  echo "Choose --both, --openclaw, or --hermes." >&2
  exit 2
fi

install_link() {
  local label="$1"
  local target="$2"
  local parent
  parent="$(dirname "$target")"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would install $label skill: $target -> $ROOT_DIR"
    return
  fi

  mkdir -p "$parent"

  if [ -L "$target" ]; then
    local current
    current="$(readlink "$target")"
    if [ "$(cd "$(dirname "$target")" && cd "$(dirname "$current")" 2>/dev/null && pwd -P)/$(basename "$current")" = "$ROOT_DIR" ] 2>/dev/null; then
      echo "$label skill already installed: $target"
      return
    fi
    if [ "$FORCE" -eq 0 ]; then
      echo "$label target already exists and points elsewhere: $target" >&2
      exit 1
    fi
    rm "$target"
  elif [ -e "$target" ]; then
    if [ "$FORCE" -eq 0 ]; then
      echo "$label target already exists: $target" >&2
      exit 1
    fi
    rm -rf "$target"
  fi

  ln -s "$ROOT_DIR" "$target"
  echo "$label skill installed: $target"
}

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

if [ "$INSTALL_OPENCLAW" -eq 1 ]; then
  install_link "OpenClaw" "$OPENCLAW_HOME/workspace/skills/mai"
fi

if [ "$INSTALL_HERMES" -eq 1 ]; then
  install_link "Hermes" "$HERMES_HOME/skills/commerce/mai"
fi

cat <<EOF

Next:
  OpenClaw: restart OpenClaw or refresh skills, then invoke Mai as a skill/agent.
  Hermes:   run 'hermes -s mai' or start Hermes after installing the skill.
  Smoke:    cd "$ROOT_DIR" && python3 scripts/mai.py --help && python3 scripts/mai_registry.py --help
EOF
