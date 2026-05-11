#!/usr/bin/env bash
# kipris-cli trademark — search Korean trademarks (상표).
# Endpoint: TrademarkInfoSearchService/trademarkInfoSearchInfo

set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_kipris_common.sh"

usage() {
  cat <<'EOF'
kipris-cli trademark — Search Korean trademarks (상표)

USAGE:
  kipris-cli trademark [flags]

FLAGS:
  --word "<query>"        Brand name / character search
  --applicant "<name>"    Applicant (출원인)
  --class N               NICE classification (1..45)
  --reg-status <s>        registered | pending | rejected | expired
  --start-date YYYYMMDD   출원일 since
  --end-date YYYYMMDD     출원일 until
  --rows N                Page size (default 30, max 500)
  --page N                Page number (default 1)
  --format json|xml|jsonl
  --key <KEY>

At least one of --word / --applicant is required.

EXAMPLE:
  kipris-cli trademark --word "AURORA" --class 9
  kipris-cli trademark --applicant "스타벅스" --reg-status registered
EOF
}

declare -a REMAINING
parse_common_flags "$@"
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

WORD=""; APPLICANT=""; CLS=""; STATUS=""; SD=""; ED=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --word) WORD="$2"; shift 2 ;;
    --applicant) APPLICANT="$2"; shift 2 ;;
    --class) CLS="$2"; shift 2 ;;
    --reg-status) STATUS="$2"; shift 2 ;;
    --start-date) SD="$2"; shift 2 ;;
    --end-date) ED="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (try --help)" ;;
  esac
done

if [ -z "$WORD$APPLICANT" ]; then
  die "need at least one of --word / --applicant"
fi

# Map friendly status to KIPRIS application boolean flags.
APP_FLAGS=""
case "$STATUS" in
  ""|all)        APP_FLAGS="" ;;
  registered)    APP_FLAGS="&registration=true" ;;
  pending)       APP_FLAGS="&application=true&publication=true&registration=false" ;;
  rejected)      APP_FLAGS="&rejection=true" ;;
  expired)       APP_FLAGS="&expiration=true" ;;
  *) die "unknown --reg-status: $STATUS (use registered|pending|rejected|expired)" ;;
esac

QS=""
[ -n "$WORD" ]      && QS="${QS}&trademarkName=$(urlencode "$WORD")"
[ -n "$APPLICANT" ] && QS="${QS}&applicantName=$(urlencode "$APPLICANT")"
[ -n "$CLS" ]       && QS="${QS}&classification=${CLS}"
[ -n "$SD" ]        && QS="${QS}&applicationDate=$(urlencode "$SD")"
[ -n "$ED" ]        && QS="${QS}&applicationDateTo=$(urlencode "$ED")"
[ -n "$ROWS" ]      && QS="${QS}&numOfRows=${ROWS}"
[ -n "$PAGE" ]      && QS="${QS}&pageNo=${PAGE}"
QS="${QS}${APP_FLAGS}"
QS="${QS#&}"

kipris_get "TrademarkInfoSearchService/trademarkInfoSearchInfo" "$QS" \
  | emit_output "body/items/item"
