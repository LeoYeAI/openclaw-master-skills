#!/usr/bin/env bash
# kipris-cli patent — search patents and utility models.
# Endpoint: patUtiModInfoSearchSevice/patUtiModInfoSearch

set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_kipris_common.sh"

usage() {
  cat <<'EOF'
kipris-cli patent — Search Korean patents (특허) and utility models (실용신안)

USAGE:
  kipris-cli patent [flags]

FLAGS:
  --word "<query>"       Free-text search (Korean or English)
  --applicant "<name>"   Filter by applicant name (출원인)
  --inventor "<name>"    Filter by inventor name (발명자)
  --ipc "<code>"         Filter by IPC class (e.g. G06N, A61K)
  --pat true|false       Include 특허 (default: true)
  --utility true|false   Include 실용신안 (default: true)
  --start-date YYYYMMDD  출원일 since
  --end-date YYYYMMDD    출원일 until
  --rows N               Page size (default 30, max 500)
  --page N               Page number (default 1)
  --format json|xml|jsonl
  --key <KEY>            Override $KIPRIS_PLUS_KEY

At least one of --word / --applicant / --inventor / --ipc is required.

EXAMPLE:
  kipris-cli patent --word "양자컴퓨팅" --applicant "삼성전자" --rows 20
EOF
}

declare -a REMAINING
parse_common_flags "$@"
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

WORD=""; APPLICANT=""; INVENTOR=""; IPC=""
PAT="true"; UTI="true"; SD=""; ED=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --word) WORD="$2"; shift 2 ;;
    --applicant) APPLICANT="$2"; shift 2 ;;
    --inventor) INVENTOR="$2"; shift 2 ;;
    --ipc) IPC="$2"; shift 2 ;;
    --pat) PAT="$2"; shift 2 ;;
    --utility|--uti) UTI="$2"; shift 2 ;;
    --start-date) SD="$2"; shift 2 ;;
    --end-date) ED="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown flag: $1 (try --help)" ;;
  esac
done

if [ -z "$WORD$APPLICANT$INVENTOR$IPC" ]; then
  die "need at least one of --word / --applicant / --inventor / --ipc"
fi

QS=""
[ -n "$WORD" ]      && QS="${QS}&word=$(urlencode "$WORD")"
[ -n "$APPLICANT" ] && QS="${QS}&applicant=$(urlencode "$APPLICANT")"
[ -n "$INVENTOR" ]  && QS="${QS}&inventors=$(urlencode "$INVENTOR")"
[ -n "$IPC" ]       && QS="${QS}&ipcNumber=$(urlencode "$IPC")"
[ -n "$SD" ]        && QS="${QS}&applicationDate=$(urlencode "$SD")"
[ -n "$ED" ]        && QS="${QS}&applicationDateTo=$(urlencode "$ED")"
[ -n "$ROWS" ]      && QS="${QS}&numOfRows=${ROWS}"
[ -n "$PAGE" ]      && QS="${QS}&pageNo=${PAGE}"
QS="${QS}&patent=${PAT}&utility=${UTI}"
QS="${QS#&}"

kipris_get "patUtiModInfoSearchSevice/patUtiModInfoSearch" "$QS" \
  | emit_output "body/items/item"
