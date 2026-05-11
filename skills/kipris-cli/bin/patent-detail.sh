#!/usr/bin/env bash
# kipris-cli patent-detail — bibliographic detail by 출원번호.
# Endpoint: patUtiModInfoSearchSevice/patUtiModBibliographicInfoSearch

set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_kipris_common.sh"

usage() {
  cat <<'EOF'
kipris-cli patent-detail — Patent bibliographic detail by application number

USAGE:
  kipris-cli patent-detail --app-no <13-digit>

FLAGS:
  --app-no <num>     Application number (출원번호), 13 digits, e.g. 1020230012345
  --format json|xml|jsonl
  --key <KEY>

EXAMPLE:
  kipris-cli patent-detail --app-no 1020230012345
EOF
}

declare -a REMAINING
parse_common_flags "$@"
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

APP=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --app-no|--applicationNumber) APP="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (try --help)" ;;
  esac
done

[ -n "$APP" ] || die "--app-no is required"

# Strip any dashes/spaces in the application number.
APP="${APP//[- ]/}"
case "$APP" in
  [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;;
  *) die "--app-no must be 13 digits (got: $APP)" ;;
esac

kipris_get "patUtiModInfoSearchSevice/patUtiModBibliographicInfoSearch" \
  "applicationNumber=${APP}" \
  | emit_output "body/items/item"
