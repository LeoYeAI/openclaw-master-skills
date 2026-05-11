#!/usr/bin/env bash
# Shared helpers for kipris-cli subcommands.
# Source from: . "$(dirname "${BASH_SOURCE[0]}")/_kipris_common.sh"

KIPRIS_BASE="${KIPRIS_BASE:-http://plus.kipris.or.kr/kipo-api/kipi}"

die() { echo "kipris-cli: $*" >&2; exit 1; }

require_key() {
  local k="${KIPRIS_PLUS_KEY:-${KIPRIS_KEY:-}}"
  if [ -n "${OVERRIDE_KEY:-}" ]; then k="$OVERRIDE_KEY"; fi
  if [ -z "$k" ]; then
    die "missing API key. Set KIPRIS_PLUS_KEY or pass --key. Get one at https://plus.kipris.or.kr"
  fi
  printf '%s' "$k"
}

# urlencode a single string. Pure Python (no extra deps).
urlencode() {
  python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "${1:-}"
}

# Call a KIPRIS Plus REST endpoint.
# args: <service-path> <query-string-WITHOUT-ServiceKey>
# Emits raw XML to stdout, exits 0 on HTTP success regardless of resultCode.
kipris_get() {
  local path="$1" qs="${2:-}"
  local key; key="$(require_key)"
  local sep="?"
  [ -n "$qs" ] && sep="?${qs}&"
  local url="${KIPRIS_BASE}/${path}${sep}ServiceKey=${key}"
  curl -sS --fail-with-body -m 30 -A "kipris-cli/0.1.0" "$url"
}

_KIPRIS_BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# XML→JSONL via Python stdlib only.
# args: <record-xpath>  (default body/items/item)
# stdin: raw XML; stdout: one JSON object per line
xml_to_jsonl() {
  python3 "$_KIPRIS_BIN_DIR/_xml2jsonl.py" "${1:-body/items/item}"
}

# Render output in requested format. Defaults to jsonl.
emit_output() {
  local fmt="${FORMAT:-jsonl}" xpath="${1:-items/item}"
  local raw; raw="$(cat)"
  case "$fmt" in
    xml)
      printf '%s\n' "$raw"
      ;;
    json)
      printf '%s\n' "$raw" | xml_to_jsonl "$xpath" \
        | python3 -c "import sys,json; print(json.dumps([json.loads(l) for l in sys.stdin if l.strip()], ensure_ascii=False, indent=2))"
      ;;
    jsonl|*)
      printf '%s\n' "$raw" | xml_to_jsonl "$xpath"
      ;;
  esac
}

# Parse common flags from "$@", set globals OVERRIDE_KEY/FORMAT/ROWS/PAGE,
# and write the remaining flags to the array REMAINING (must be declared in caller).
parse_common_flags() {
  REMAINING=()
  FORMAT="jsonl"
  ROWS=""
  PAGE=""
  OVERRIDE_KEY=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --key) OVERRIDE_KEY="$2"; shift 2 ;;
      --format) FORMAT="$2"; shift 2 ;;
      --rows) ROWS="$2"; shift 2 ;;
      --page) PAGE="$2"; shift 2 ;;
      *) REMAINING+=("$1"); shift ;;
    esac
  done
}
