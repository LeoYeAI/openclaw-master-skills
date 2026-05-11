#!/usr/bin/env bash
# kipris-cli applicant — search patents by applicant name.
# Endpoint: patUtiModInfoSearchSevice/patUtiModInfoSearchByApplicantName

set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_kipris_common.sh"

usage() {
  cat <<'EOF'
kipris-cli applicant — All patent / utility-model filings by applicant (출원인)

USAGE:
  kipris-cli applicant --name "<applicant>" [flags]

FLAGS:
  --name "<name>"        Applicant name (Korean or English, exact match preferred)
  --pat true|false       Include 특허 (default: true)
  --utility true|false   Include 실용신안 (default: true)
  --start-date YYYYMMDD  출원일 since
  --end-date YYYYMMDD    출원일 until
  --rows N               Page size (default 30, max 500)
  --page N               Page number (default 1)
  --format json|xml|jsonl
  --key <KEY>

EXAMPLE:
  kipris-cli applicant --name "삼성전자주식회사" --rows 100
  kipris-cli applicant --name "Apple Inc." --start-date 20240101
EOF
}

declare -a REMAINING
parse_common_flags "$@"
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

NAME=""; PAT="true"; UTI="true"; SD=""; ED=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --name|--applicant) NAME="$2"; shift 2 ;;
    --pat) PAT="$2"; shift 2 ;;
    --utility|--uti) UTI="$2"; shift 2 ;;
    --start-date) SD="$2"; shift 2 ;;
    --end-date) ED="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (try --help)" ;;
  esac
done

[ -n "$NAME" ] || die "--name is required"

QS="applicantName=$(urlencode "$NAME")&patent=${PAT}&utility=${UTI}"
[ -n "$SD" ]   && QS="${QS}&applicationDate=$(urlencode "$SD")"
[ -n "$ED" ]   && QS="${QS}&applicationDateTo=$(urlencode "$ED")"
[ -n "$ROWS" ] && QS="${QS}&numOfRows=${ROWS}"
[ -n "$PAGE" ] && QS="${QS}&pageNo=${PAGE}"

kipris_get "patUtiModInfoSearchSevice/patUtiModInfoSearchByApplicantName" "$QS" \
  | emit_output "body/items/item"
