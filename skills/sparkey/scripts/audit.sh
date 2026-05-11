#!/usr/bin/env bash
set -uo pipefail

# Scan for orphaned sparkey artifacts on the operator host.
# Run as root. Reports findings without modifying anything.

readonly LOG_FILE="/var/log/agent-support.log"

die() { printf 'ERROR: %s\n' "${1}" >&2; exit 1; }

[[ ${EUID} -eq 0 ]] || die "This script must be run as root (sudo)"

findings=0

printf '=== sparkey Artifact Audit ===\n\n'

# 1. Orphaned agent_support_* accounts
printf '[1/5] Checking for agent_support_* accounts...\n'
stale_users=$(getent passwd 2>/dev/null | grep '^agent_support_' | cut -d: -f1)
if [[ -z "${stale_users}" ]]; then
  stale_users=$(grep '^agent_support_' /etc/passwd 2>/dev/null | cut -d: -f1)
fi
if [[ -n "${stale_users}" ]]; then
  for u in ${stale_users}; do
    expiry=$(chage -l "${u}" 2>/dev/null | grep 'Account expires' | cut -d: -f2 | xargs)
    printf '  FOUND: %s (expires: %s)\n' "${u}" "${expiry:-unknown}"
    findings=$((findings + 1))
  done
else
  printf '  Clean: no agent_support_* accounts found.\n'
fi

# 2. Stale session keys in /tmp/
printf '\n[2/5] Checking for stale session keys in /tmp/...\n'
stale_keys=$(find /tmp/ -maxdepth 1 -name 'agent_session_*' -o -name 'agent_access_key*' 2>/dev/null)
if [[ -n "${stale_keys}" ]]; then
  while IFS= read -r kf; do
    age_hours=$(( ( $(date +%s) - $(stat -c %Y "${kf}" 2>/dev/null || stat -f %m "${kf}" 2>/dev/null || printf '0') ) / 3600 ))
    printf '  FOUND: %s (age: %dh)\n' "${kf}" "${age_hours}"
    findings=$((findings + 1))
  done <<< "${stale_keys}"
else
  printf '  Clean: no stale session keys found.\n'
fi

# 3. Orphaned support shells in /usr/local/bin/
printf '\n[3/5] Checking for orphaned support shells...\n'
stale_shells=$(find /usr/local/bin/ -maxdepth 1 -name 'agent-support-shell-*' 2>/dev/null)
if [[ -n "${stale_shells}" ]]; then
  while IFS= read -r sf; do
    printf '  FOUND: %s\n' "${sf}"
    findings=$((findings + 1))
  done <<< "${stale_shells}"
else
  printf '  Clean: no orphaned support shells.\n'
fi

# 4. Orphaned cleanup scripts in /usr/local/sbin/
printf '\n[4/5] Checking for orphaned cleanup scripts...\n'
stale_cleanup=$(find /usr/local/sbin/ -maxdepth 1 -name 'agent-cleanup-*.sh' 2>/dev/null)
if [[ -n "${stale_cleanup}" ]]; then
  while IFS= read -r cf; do
    printf '  FOUND: %s\n' "${cf}"
    findings=$((findings + 1))
  done <<< "${stale_cleanup}"
else
  printf '  Clean: no orphaned cleanup scripts.\n'
fi

# 5. Pending at(1) jobs for agent cleanup
printf '\n[5/5] Checking for pending at(1) cleanup jobs...\n'
if command -v atq &>/dev/null; then
  pending_jobs=$(atq 2>/dev/null | awk '{print $1}')
  agent_jobs=0
  for job_id in ${pending_jobs}; do
    if at -c "${job_id}" 2>/dev/null | grep -q 'agent-cleanup-'; then
      printf '  FOUND: at job #%s\n' "${job_id}"
      at -c "${job_id}" 2>/dev/null | grep 'agent-cleanup-' | head -1 | sed 's/^/    /'
      findings=$((findings + 1))
      agent_jobs=$((agent_jobs + 1))
    fi
  done
  if [[ ${agent_jobs} -eq 0 ]]; then
    printf '  Clean: no pending agent cleanup jobs.\n'
  fi
else
  printf '  Skipped: at(1) not available.\n'
fi

# CA key age check
printf '\n[Bonus] CA key status...\n'
ca_key="/etc/ssh/agent_ca"
if [[ -f "${ca_key}" ]]; then
  key_epoch=$(stat -c %Y "${ca_key}" 2>/dev/null || stat -f %m "${ca_key}" 2>/dev/null)
  if [[ -n "${key_epoch:-}" ]]; then
    age_days=$(( ( $(date +%s) - key_epoch ) / 86400 ))
    if [[ ${age_days} -gt 90 ]]; then
      printf '  WARNING: CA key is %d days old (rotation recommended after 90 days)\n' "${age_days}"
    else
      printf '  OK: CA key is %d days old\n' "${age_days}"
    fi
  fi
  perms=$(stat -c %a "${ca_key}" 2>/dev/null || stat -f %Lp "${ca_key}" 2>/dev/null)
  if [[ "${perms}" != "400" ]]; then
    printf '  WARNING: CA key permissions are %s (expected 400)\n' "${perms}"
    findings=$((findings + 1))
  else
    printf '  OK: CA key permissions are 400\n'
  fi
else
  printf '  No CA key found at %s (CA mode not initialized)\n' "${ca_key}"
fi

printf '\n=== Audit Complete ===\n'
if [[ ${findings} -gt 0 ]]; then
  printf 'Findings: %d artifact(s) require attention.\n' "${findings}"
  printf 'To clean up all sessions: sudo bash scripts/revoke-access.sh --all\n'
  exit 1
else
  printf 'No orphaned artifacts found. System is clean.\n'
  exit 0
fi
