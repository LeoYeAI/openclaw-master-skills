#!/usr/bin/env bash
# m-and-a-ip-snapshot.sh — IP portfolio snapshot for an M&A target.
#
# Given an applicant name (Korean corporate full name), returns a one-screen summary:
#   - Total active patent filings
#   - Recent (last 12 months) filings
#   - Top 5 IPC classes
#   - Trademark count and recent filings
#   - Design count
#
# Pairs naturally with `nts-bizno-cli` (resolve 사업자번호 → 법인명) and
# `opendart-cli` (cross-reference disclosure obligations).
#
# Usage:
#   KIPRIS_PLUS_KEY=xxx ./m-and-a-ip-snapshot.sh "현대자동차주식회사"

set -euo pipefail

NAME="${1:?usage: m-and-a-ip-snapshot.sh APPLICANT_NAME}"
CLI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/kipris-cli"

YEAR_AGO=$(date -v-12m +%Y%m%d 2>/dev/null || date -d '12 months ago' +%Y%m%d)

echo "# IP snapshot — $NAME"
echo "_generated $(date -u +%Y-%m-%dT%H:%M:%SZ)_"
echo

echo "## Patents"
ALL=$("$CLI" applicant --name "$NAME" --rows 500)
TOTAL=$(printf '%s\n' "$ALL" | grep -c '^{[^_]' || true)
RECENT=$("$CLI" applicant --name "$NAME" --start-date "$YEAR_AGO" --rows 500 \
         | grep -c '^{[^_]' || true)
echo "- Total active filings (page 1, ≤500 rows): **$TOTAL**"
echo "- Filed in last 12 months (since $YEAR_AGO): **$RECENT**"

echo
echo "## Top IPC classes (from page 1)"
printf '%s\n' "$ALL" \
  | python3 -c "
import sys,json,re
from collections import Counter
c=Counter()
for line in sys.stdin:
  line=line.strip()
  if not line or not line.startswith('{'): continue
  try: d=json.loads(line)
  except: continue
  ipc=d.get('ipcNumber') or d.get('ipc') or ''
  for code in re.findall(r'[A-H]\d{2}[A-Z]?', ipc.upper()):
    c[code[:4]]+=1
for k,v in c.most_common(5):
  print(f'- {k}: {v}')
"

echo
echo "## Trademarks"
TM=$("$CLI" trademark --applicant "$NAME" --rows 500 | grep -c '^{[^_]' || true)
TM_REC=$("$CLI" trademark --applicant "$NAME" --start-date "$YEAR_AGO" --rows 500 \
         | grep -c '^{[^_]' || true)
echo "- Total marks: **$TM**, recent 12 mo: **$TM_REC**"

echo
echo "## Designs"
DS=$("$CLI" design --applicant "$NAME" --rows 500 | grep -c '^{[^_]' || true)
echo "- Registered/applied designs: **$DS**"

echo
echo "_Diligence note_: KIPRIS counts include pending + abandoned + expired filings."
echo "Cross-reference with opendart-cli for material IP-related disclosures."
