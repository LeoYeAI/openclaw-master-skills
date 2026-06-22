#!/usr/bin/env bash
# Umbrella HaS CLI — dispatches to text/image sub-CLIs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

print_help() {
  cat <<'EOF'
usage: has <text|image> ...

Namespaces:
  text   Text anonymization and restoration
  image  Image privacy scanning and masking

Examples:
  has text scan --type "person name" --file note.txt
  has text hide --type "person name" --file note.txt --mapping-output note.mapping.json
  has text restore --mapping mapping.json --file anonymized.txt
  has image scan --type face --image photo.jpg
  has image hide --type face --image photo.jpg
  has image categories
EOF
}

emit_error() {
  local code="$1"
  local message="$2"
  python3 - "$code" "$message" <<'PY'
import json
import sys

payload = {
    "schema_version": "1",
    "error": {
        "code": sys.argv[1],
        "message": sys.argv[2],
    },
}
print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
PY
}

if [[ $# -eq 0 ]]; then
  emit_error "missing_namespace" "Choose a namespace: text or image."
  exit 1
fi

case "$1" in
  -h|--help|help)
    print_help
    exit 0
    ;;
  text)
    shift
    export HAS_CLI_PROG="has text"
    exec "$SCRIPT_DIR/has-text.sh" "$@"
    ;;
  image)
    shift
    export HAS_CLI_PROG="has image"
    exec "$SCRIPT_DIR/has-image.sh" "$@"
    ;;
  *)
    emit_error "invalid_namespace" "Unknown namespace '$1'. Choose text or image."
    exit 1
    ;;
esac
