#!/usr/bin/env bash
set -euo pipefail

readonly LOG_FILE="/var/log/agent-support.log"
readonly ARCHIVE_DIR="/var/log/agent-support-archive"

shred_cmd="shred -u"
command -v shred &>/dev/null || shred_cmd="rm -f"

session_id=""
agent_user=""
revoke_all=false

die() { printf 'ERROR: %s\n' "${1}" >&2; exit 1; }

usage() {
  cat <<EOF
Usage: $(basename "${0}") [OPTIONS]

Immediately revoke temporary SSH access for an AI agent.

Options:
  --session ID    Revoke by session ID
  --user NAME     Revoke by account username
  --all           Revoke ALL active agent support sessions
  --help          Show this help message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --session) [[ $# -ge 2 ]] || die "--session requires a value"; session_id="${2}"; shift 2 ;;
    --user)    [[ $# -ge 2 ]] || die "--user requires a value"; agent_user="${2}"; shift 2 ;;
    --all)     revoke_all=true; shift ;;
    --help)    usage ;;
    *)         die "Unknown option: ${1}" ;;
  esac
done

[[ -n "${session_id}" || -n "${agent_user}" || "${revoke_all}" == true ]] || die "Specify --session, --user, or --all"
[[ ${EUID} -eq 0 ]] || die "This script must be run as root (sudo)"

for cmd in usermod userdel pkill getent; do
  command -v "${cmd}" &>/dev/null || die "Required command '${cmd}' not found"
done

resolve_user_from_session() {
  grep "AI Agent Support \[${1}\]" /etc/passwd 2>/dev/null | cut -d: -f1 || true
}

resolve_session_from_user() {
  local gecos
  gecos=$(getent passwd "${1}" 2>/dev/null | cut -d: -f5)
  printf '%s' "$(printf '%s' "${gecos}" | sed -n 's/.*\[\([^]]*\)\].*/\1/p')"
}

revoke_single() {
  local target_user="${1}"
  local target_sid="${2:-unknown}"

  printf '%s Revoking access for: %s (session: %s) ---\n' '---' "${target_user}" "${target_sid}"

  printf '  [1/7] Locking account...\n'
  usermod -L "${target_user}" 2>/dev/null && printf '    Locked.\n' || printf '    Already locked or not found.\n'

  printf '  [2/7] Terminating active sessions...\n'
  if pkill -u "${target_user}" 2>/dev/null; then
    sleep 2
    pkill -9 -u "${target_user}" 2>/dev/null || true
    printf '    Sessions terminated.\n'
  else
    printf '    No active sessions found.\n'
  fi

  printf '  [3/7] Removing file protections...\n'
  local target_home
  target_home=$(getent passwd "${target_user}" 2>/dev/null | cut -d: -f6) || target_home="/home/${target_user}"
  chattr -i "${target_home}/.ssh/authorized_keys" 2>/dev/null || true
  chattr -i "${target_home}/.ssh" 2>/dev/null || true
  printf '    Done.\n'

  printf '  [4/7] Archiving session logs...\n'
  mkdir -p "${ARCHIVE_DIR}"
  if [[ -f "${LOG_FILE}" ]] && grep -q "${target_sid}" "${LOG_FILE}" 2>/dev/null; then
    grep "${target_sid}" "${LOG_FILE}" > "${ARCHIVE_DIR}/${target_sid}.log"
    printf '    Archived to %s/%s.log\n' "${ARCHIVE_DIR}" "${target_sid}"
  else
    printf '    No log entries found for session.\n'
  fi

  printf '  [5/7] Removing user account...\n'
  userdel -r "${target_user}" 2>/dev/null && printf '    Account removed.\n' || printf '    Account already removed.\n'

  printf '  [6/7] Destroying session keys...\n'
  local key_base="/tmp/agent_session_${target_sid}"
  local destroyed=0
  for key_file in "${key_base}" "${key_base}.pub" "${key_base}-cert.pub"; do
    if [[ -f "${key_file}" ]]; then
      ${shred_cmd} "${key_file}" 2>/dev/null && destroyed=$((destroyed + 1))
    fi
  done
  printf '    Destroyed %d key file(s).\n' "${destroyed}"

  printf '  [7/7] Cancelling scheduled cleanup...\n'
  if command -v atq &>/dev/null; then
    local pending_jobs
    pending_jobs=$(atq 2>/dev/null | awk '{print $1}')
    for job_id in ${pending_jobs}; do
      if at -c "${job_id}" 2>/dev/null | grep -q "${target_sid}"; then
        atrm "${job_id}" 2>/dev/null
        printf '    Cancelled at job #%s.\n' "${job_id}"
      fi
    done
  fi
  systemctl stop "agent-cleanup-${target_sid}" 2>/dev/null || true
  systemctl reset-failed "agent-cleanup-${target_sid}" 2>/dev/null || true

  for artifact in "/usr/local/sbin/agent-cleanup-${target_sid}.sh" "/usr/local/bin/agent-support-shell-${target_sid}"; do
    if [[ -f "${artifact}" ]]; then
      rm -f "${artifact}"
      printf '    Removed %s\n' "$(basename "${artifact}")"
    fi
  done

  printf '[%s] SESSION_REVOKED: %s user=%s reason=manual_revoke\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${target_sid}" "${target_user}" >> "${LOG_FILE}"

  # Post-revocation verification
  printf '  [VERIFY] Checking artifact removal...\n'
  local verify_pass=true
  if id "${target_user}" &>/dev/null; then
    printf '    FAIL: Account %s still exists\n' "${target_user}"
    verify_pass=false
  else
    printf '    PASS: Account removed\n'
  fi
  for vf in "/tmp/agent_session_${target_sid}" "/tmp/agent_session_${target_sid}.pub" "/tmp/agent_session_${target_sid}-cert.pub"; do
    if [[ -f "${vf}" ]]; then
      printf '    FAIL: Key file still exists: %s\n' "${vf}"
      verify_pass=false
    fi
  done
  if [[ ! -f "/tmp/agent_session_${target_sid}" ]] && [[ ! -f "/tmp/agent_session_${target_sid}.pub" ]]; then
    printf '    PASS: Session keys removed\n'
  fi
  if [[ -f "/usr/local/bin/agent-support-shell-${target_sid}" ]]; then
    printf '    FAIL: Support shell still exists\n'
    verify_pass=false
  else
    printf '    PASS: Support shell removed\n'
  fi
  if [[ -f "/usr/local/sbin/agent-cleanup-${target_sid}.sh" ]]; then
    printf '    FAIL: Cleanup script still exists\n'
    verify_pass=false
  else
    printf '    PASS: Cleanup script removed\n'
  fi
  if [[ "${verify_pass}" == true ]]; then
    printf '  [VERIFY] All artifacts confirmed removed.\n'
  else
    printf '  [VERIFY] WARNING: Some artifacts could not be removed. Manual cleanup required.\n'
  fi

  printf '%s Access revoked for %s ---\n\n' '---' "${target_user}"
}

if [[ "${revoke_all}" == true ]]; then
  printf '=== Revoking ALL Agent Support Sessions ===\n\n'

  found_users=$(getent passwd 2>/dev/null | grep '^agent_support_' | cut -d: -f1)
  [[ -n "${found_users}" ]] || found_users=$(grep '^agent_support_' /etc/passwd 2>/dev/null | cut -d: -f1)

  if [[ -z "${found_users}" ]]; then
    printf 'No active agent support accounts found.\n'
    exit 0
  fi

  for found_user in ${found_users}; do
    revoke_single "${found_user}" "$(resolve_session_from_user "${found_user}")"
  done

  if ! grep -q '^agent_support_' /etc/passwd 2>/dev/null; then
    rm -f /usr/local/bin/agent-support-shell-* /usr/local/sbin/agent-cleanup-*.sh 2>/dev/null || true
    printf 'All session-specific files removed.\n'
  fi

  printf '=== All sessions revoked ===\n'

elif [[ -n "${session_id}" ]]; then
  if [[ -z "${agent_user}" ]]; then
    agent_user=$(resolve_user_from_session "${session_id}")
    if [[ -z "${agent_user}" ]]; then
      printf 'WARNING: Could not find account for session %s.\n' "${session_id}"
      printf 'The account may have already been cleaned up.\nAttempting key destruction anyway...\n'
      for orphan in "/tmp/agent_session_${session_id}" "/tmp/agent_session_${session_id}.pub" "/tmp/agent_session_${session_id}-cert.pub"; do
        ${shred_cmd} "${orphan}" 2>/dev/null || true
      done
      rm -f "/usr/local/bin/agent-support-shell-${session_id}" "/usr/local/sbin/agent-cleanup-${session_id}.sh" 2>/dev/null || true
      exit 1
    fi
  fi
  revoke_single "${agent_user}" "${session_id}"

elif [[ -n "${agent_user}" ]]; then
  revoke_single "${agent_user}" "$(resolve_session_from_user "${agent_user}")"
fi

printf 'Done. Review archived logs at: %s/\n' "${ARCHIVE_DIR}"
