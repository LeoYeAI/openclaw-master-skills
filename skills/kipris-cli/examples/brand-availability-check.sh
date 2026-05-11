#!/usr/bin/env bash
# brand-availability-check.sh — quick TM availability snapshot for a candidate brand name.
#
# Checks NICE classes 9 (software/electronics), 35 (advertising/business),
# 42 (SaaS/scientific) — the typical SaaS-startup trio — and reports per-class
# counts of registered + pending marks containing the candidate string.
#
# Usage:
#   KIPRIS_PLUS_KEY=xxx ./brand-availability-check.sh "AURORA"

set -euo pipefail

BRAND="${1:?usage: brand-availability-check.sh BRAND}"
CLI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/kipris-cli"

echo "# Brand availability — \"$BRAND\""
echo
printf '%-8s | %-12s | %-12s | %s\n' "NICE" "registered" "pending" "verdict"
printf -- "---------|--------------|--------------|--------\n"

for CLS in 9 35 42; do
  REG=$("$CLI" trademark --word "$BRAND" --class "$CLS" --reg-status registered --rows 100 \
        | grep -c '^{[^_]' || true)
  PEND=$("$CLI" trademark --word "$BRAND" --class "$CLS" --reg-status pending --rows 100 \
        | grep -c '^{[^_]' || true)

  if [ "$REG" -gt 0 ]; then
    VERDICT="❌ blocked ($REG registered)"
  elif [ "$PEND" -gt 0 ]; then
    VERDICT="⚠️  pending ($PEND in queue)"
  else
    VERDICT="✅ clear"
  fi

  printf '%-8s | %-12s | %-12s | %s\n' "$CLS" "$REG" "$PEND" "$VERDICT"
  sleep 0.1
done

echo
echo "(NICE 9=software/electronics, 35=advertising/biz, 42=SaaS/research)"
echo "Caveat: KIPRIS keyword search returns substring matches — manual review recommended for exact-string hits."
