#!/usr/bin/env bash
# kipris-cli design — search Korean industrial designs (디자인).
# Endpoint: DesignInfoSearchService/designInfoSearchInfo

set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_kipris_common.sh"

usage() {
  cat <<'EOF'
kipris-cli design — Search Korean industrial designs (디자인)

USAGE:
  kipris-cli design [flags]

FLAGS:
  --word "<query>"        Free-text search (Korean or English)
  --applicant "<name>"    Applicant (출원인)
  --locarno "<class>"     Locarno classification (e.g. 14-04)
  --start-date YYYYMMDD   출원일 since
  --end-date YYYYMMDD     출원일 until
  --rows N                Page size (default 30, max 500)
  --page N                Page number (default 1)
  --format json|xml|jsonl
  --key <KEY>

At least one of --word / --applicant is required.

EXAMPLE:
  kipris-cli design --word "smart watch" --rows 10
EOF
}

declare -a REMAINING
parse_common_flags "$@"
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

WORD=""; APPLICANT=""; LOCARNO=""; SD=""; ED=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --word) WORD="$2"; shift 2 ;;
    --applicant) APPLICANT="$2"; shift 2 ;;
    --locarno) LOCARNO="$2"; shift 2 ;;
    --start-date) SD="$2"; shift 2 ;;
    --end-date) ED="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (try --help)" ;;
  esac
done

if [ -z "$WORD$APPLICANT" ]; then
  die "need at least one of --word / --applicant"
fi

QS=""
[ -n "$WORD" ]      && QS="${QS}&designName=$(urlencode "$WORD")"
[ -n "$APPLICANT" ] && QS="${QS}&applicantName=$(urlencode "$APPLICANT")"
[ -n "$LOCARNO" ]   && QS="${QS}&designClass=$(urlencode "$LOCARNO")"
[ -n "$SD" ]        && QS="${QS}&applicationDate=$(urlencode "$SD")"
[ -n "$ED" ]        && QS="${QS}&applicationDateTo=$(urlencode "$ED")"
[ -n "$ROWS" ]      && QS="${QS}&numOfRows=${ROWS}"
[ -n "$PAGE" ]      && QS="${QS}&pageNo=${PAGE}"
QS="${QS#&}"

kipris_get "DesignInfoSearchService/designInfoSearchInfo" "$QS" \
  | emit_output "body/items/item"
