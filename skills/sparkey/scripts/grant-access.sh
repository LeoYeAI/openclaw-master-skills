#!/usr/bin/env bash
set -uo pipefail

ca_dir="/etc/ssh"
ca_name="agent_ca"
duration="4h"
profile="diagnostic"
use_ca=true
target_host=""
agent_pubkey=""
key_dir="/tmp"
log_file="/var/log/agent-support.log"
with_pty=false
dry_run=false

# Track provisioned artifacts for cleanup on failure
_cleanup_agent_user=""
_cleanup_support_shell=""
_cleanup_key_path=""
_cleanup_cleanup_script=""

die()  { printf 'ERROR: %s\n' "${1}" >&2; exit 1; }
warn() { printf 'WARNING: %s\n' "${1}" >&2; }

cleanup_on_failure() {
  local exit_code=$?
  if [[ ${exit_code} -ne 0 ]]; then
    printf '\nERROR: Script failed (exit %d). Cleaning up provisioned artifacts...\n' "${exit_code}" >&2
    if [[ -n "${_cleanup_agent_user}" ]] && id "${_cleanup_agent_user}" &>/dev/null; then
      userdel -r "${_cleanup_agent_user}" 2>/dev/null && printf '  Removed account: %s\n' "${_cleanup_agent_user}" >&2
    fi
    if [[ -n "${_cleanup_support_shell}" ]] && [[ -f "${_cleanup_support_shell}" ]]; then
      rm -f "${_cleanup_support_shell}" && printf '  Removed shell: %s\n' "${_cleanup_support_shell}" >&2
    fi
    if [[ -n "${_cleanup_key_path}" ]]; then
      rm -f "${_cleanup_key_path}" "${_cleanup_key_path}.pub" "${_cleanup_key_path}-cert.pub" 2>/dev/null && printf '  Removed keys: %s*\n' "${_cleanup_key_path}" >&2
    fi
    if [[ -n "${_cleanup_cleanup_script}" ]] && [[ -f "${_cleanup_cleanup_script}" ]]; then
      rm -f "${_cleanup_cleanup_script}" && printf '  Removed cleanup script: %s\n' "${_cleanup_cleanup_script}" >&2
    fi
    printf 'Cleanup complete. No artifacts should remain from this failed session.\n' >&2
  fi
}
trap cleanup_on_failure EXIT

usage() {
  cat <<EOF
Usage: $(basename "${0}") [OPTIONS]

Provision temporary SSH access for an AI agent support session.

Required:
  --host HOST           Target server hostname or IP

Options:
  --duration DUR        Access duration: e.g. 30m, 4h, 1d (default: 4h)
  --allow PROFILE       Command profile: diagnostic, remediation, full (default: diagnostic)
  --agent-pubkey PATH   Path to the agent's existing SSH public key (recommended)
  --ca-dir DIR          CA key directory (default: /etc/ssh)
  --no-ca               Use authorized_keys with expiry-time instead of CA signing
  --with-pty            Allow interactive shell (default: command-only)
  --dry-run             Show planned actions without executing
  --help                Show this help message
EOF
  exit 0
}

check_dependencies() {
  local missing=()
  for cmd in ssh-keygen useradd userdel usermod passwd pkill getent; do
    command -v "${cmd}" &>/dev/null || missing+=("${cmd}")
  done
  if ! command -v xxd &>/dev/null && ! command -v od &>/dev/null; then
    missing+=("xxd-or-od")
  fi
  if [[ ${#missing[@]} -gt 0 ]]; then
    printf 'ERROR: Missing required dependencies: %s\n\nInstall them with:\n' "${missing[*]}" >&2
    if command -v apt-get &>/dev/null; then
      printf '  sudo apt-get install -y openssh-client coreutils passwd at e2fsprogs procps\n' >&2
    elif command -v apk &>/dev/null; then
      printf '  apk add openssh-keygen bash shadow coreutils util-linux procps at e2fsprogs\n' >&2
    elif command -v dnf &>/dev/null; then
      printf '  sudo dnf install -y openssh-clients coreutils shadow-utils at e2fsprogs procps-ng\n' >&2
    elif command -v yum &>/dev/null; then
      printf '  sudo yum install -y openssh-clients coreutils shadow-utils at e2fsprogs procps\n' >&2
    else
      printf '  Install the packages providing: %s\n' "${missing[*]}" >&2
    fi
    exit 1
  fi
  command -v chattr &>/dev/null || warn "'chattr' not found. authorized_keys immutability will not be enforced."
  command -v shred &>/dev/null || warn "'shred' not found. Keys will be deleted with rm (less secure)."
  if ! command -v at &>/dev/null && ! command -v systemd-run &>/dev/null; then
    warn "Neither 'at' nor 'systemd-run' found. Auto-cleanup will NOT be scheduled."
  fi
}

parse_duration() {
  local raw="${1}"
  [[ -n "${raw}" ]] || die "Duration cannot be empty"
  local num unit
  if [[ "${raw}" =~ ^([0-9]+)([hHdDmM])$ ]]; then
    num="${BASH_REMATCH[1]}"
    unit="${BASH_REMATCH[2]}"
  elif [[ "${raw}" =~ ^([0-9]+)$ ]]; then
    num="${BASH_REMATCH[1]}"
    unit="s"
  else
    die "Invalid duration '${raw}'. Use: 30m, 4h, 1d, or raw seconds"
  fi
  [[ "${num}" -gt 0 ]] || die "Duration must be a positive number"
  case "${unit}" in
    h|H) printf '%d' $((num * 3600)) ;;
    d|D) printf '%d' $((num * 86400)) ;;
    m|M) printf '%d' $((num * 60)) ;;
    *)   printf '%d' "${num}" ;;
  esac
}

generate_hex_bytes() {
  if command -v xxd &>/dev/null; then
    head -c"${1}" /dev/urandom | xxd -p
  else
    head -c"${1}" /dev/urandom | od -An -tx1 | tr -d ' \n'
  fi
}

generate_unique_user() {
  local attempt suffix user
  for attempt in 1 2 3 4 5; do
    suffix="$(generate_hex_bytes 4)"
    user="agent_support_${suffix}"
    if ! id "${user}" &>/dev/null; then
      printf '%s' "${user}"
      return 0
    fi
  done
  die "Could not generate unique username after 5 attempts"
}

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --host)         [[ $# -ge 2 ]] || die "--host requires a value"; target_host="${2}"; shift 2 ;;
    --duration)     [[ $# -ge 2 ]] || die "--duration requires a value"; duration="${2}"; shift 2 ;;
    --allow)        [[ $# -ge 2 ]] || die "--allow requires a value"; profile="${2}"; shift 2 ;;
    --agent-pubkey) [[ $# -ge 2 ]] || die "--agent-pubkey requires a value"; agent_pubkey="${2}"; shift 2 ;;
    --ca-dir)       [[ $# -ge 2 ]] || die "--ca-dir requires a value"; ca_dir="${2}"; shift 2 ;;
    --no-ca)        use_ca=false; shift ;;
    --with-pty)     with_pty=true; shift ;;
    --dry-run)      dry_run=true; shift ;;
    --help)         usage ;;
    *)              die "Unknown option: ${1}" ;;
  esac
done

[[ -n "${target_host}" ]] || die "--host is required"
[[ ${EUID} -eq 0 ]] || die "This script must be run as root (sudo)"

check_dependencies

if [[ -n "${agent_pubkey}" ]]; then
  [[ -f "${agent_pubkey}" ]] || die "Agent public key file not found: ${agent_pubkey}"
  ssh-keygen -l -f "${agent_pubkey}" &>/dev/null || die "Invalid SSH public key: ${agent_pubkey}"
fi

duration_secs=$(parse_duration "${duration}") || exit 1
[[ "${duration_secs}" -ge 60 ]] || die "Duration must be at least 1 minute (60s)"
[[ "${duration_secs}" -le 86400 ]] || warn "Duration exceeds 24 hours. Consider shorter access windows."

case "${profile}" in
  diagnostic|remediation|full) ;;
  *) die "Unknown profile '${profile}'. Use: diagnostic, remediation, full" ;;
esac

# Pre-flight: check target sshd version for expiry-time support (OpenSSH >= 8.2)
check_target_sshd() {
  local host="${1}"
  printf 'Pre-flight: checking sshd version on %s...\n' "${host}"
  local sshd_version
  sshd_version=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
    "${host}" 'sshd -V 2>&1 || ssh -V 2>&1' 2>/dev/null) || true
  if [[ -z "${sshd_version}" ]]; then
    warn "Could not determine sshd version on ${host}. Verify manually that:"
    warn "  - OpenSSH >= 8.2 (for expiry-time in authorized_keys)"
    warn "  - TrustedUserCAKeys is configured (for CA mode)"
    return 0
  fi
  printf '  Target sshd: %s\n' "${sshd_version}"
  local version_num
  version_num=$(printf '%s' "${sshd_version}" | grep -oP 'OpenSSH_\K[0-9]+\.[0-9]+' || true)
  if [[ -n "${version_num}" ]]; then
    local major minor
    major="${version_num%%.*}"
    minor="${version_num##*.}"
    if [[ "${major}" -lt 8 ]] || { [[ "${major}" -eq 8 ]] && [[ "${minor}" -lt 2 ]]; }; then
      warn "OpenSSH ${version_num} detected. expiry-time requires >= 8.2."
      warn "The --no-ca authorized_keys approach may not enforce key expiry on this target."
    fi
  fi
}

if [[ "${dry_run}" == false ]]; then
  check_target_sshd "${target_host}" 2>/dev/null || true
fi

session_id="$(date +%Y%m%d%H%M%S)-$(generate_hex_bytes 4)"
agent_user="$(generate_unique_user)"
support_shell="/usr/local/bin/agent-support-shell-${session_id}"
cleanup_script="/usr/local/sbin/agent-cleanup-${session_id}.sh"
key_path="${key_dir}/agent_session_${session_id}"

mkdir -p /usr/local/bin /usr/local/sbin

if [[ "${dry_run}" == true ]]; then
  printf '=== DRY RUN — No changes will be made ===\n'
  printf 'Session ID:   %s\n' "${session_id}"
  printf 'Target Host:  %s\n' "${target_host}"
  printf 'Username:     %s\n' "${agent_user}"
  printf 'Duration:     %s (%ds)\n' "${duration}" "${duration_secs}"
  printf 'Profile:      %s\n' "${profile}"
  printf 'Auth mode:    %s\n' "$([[ "${use_ca}" == true ]] && printf 'certificate' || printf 'authorized_keys')"
  printf 'Key source:   %s\n' "$([[ -n "${agent_pubkey}" ]] && printf 'agent-provided' || printf 'generated')"
  printf '\nPlanned actions:\n'
  printf '  [1] Create account: %s (expires: %s)\n' "${agent_user}" "$(date -d "+$((duration_secs + 3600)) seconds" +%Y-%m-%d 2>/dev/null || printf 'N/A')"
  if [[ "${profile}" != "full" ]]; then
    printf '  [2] Install restriction shell: %s (%s profile)\n' "${support_shell}" "${profile}"
  fi
  if [[ -n "${agent_pubkey}" ]]; then
    printf '  [3] Sign agent pubkey: %s\n' "${agent_pubkey}"
  else
    printf '  [3] Generate keypair: %s\n' "${key_path}"
  fi
  if [[ "${use_ca}" == true ]]; then
    printf '  [4] Sign certificate with CA (TTL: %s)\n' "${duration}"
  else
    printf '  [4] Install authorized_keys with expiry-time\n'
  fi
  printf '  [5] Schedule cleanup: %d minutes after grant\n' "$(( (duration_secs + 600 + 59) / 60 ))"
  printf '  [6] Log to: %s\n' "${log_file}"
  printf '\n=== DRY RUN COMPLETE — No system state was changed ===\n'
  trap - EXIT
  exit 0
fi

printf '=== Granting Temporary SSH Access ===\n'
printf 'Session ID: %s\nTarget:     %s\nDuration:   %s (%ds)\n' "${session_id}" "${target_host}" "${duration}" "${duration_secs}"
printf 'Profile:    %s\nAccount:    %s\n' "${profile}" "${agent_user}"
printf 'Auth mode:  %s\nKey source: %s\n\n' \
  "$([[ "${use_ca}" == true ]] && printf 'certificate' || printf 'authorized_keys')" \
  "$([[ -n "${agent_pubkey}" ]] && printf 'agent-provided' || printf 'generated')"

touch "${log_file}" 2>/dev/null || {
  log_file="/tmp/agent-support-${session_id}.log"
  warn "Cannot write to /var/log/agent-support.log, using ${log_file}"
  touch "${log_file}"
}

printf '[1/6] Creating agent account...\n'

expiry_date=$(date -d "+$((duration_secs + 3600)) seconds" +%Y-%m-%d 2>/dev/null || \
  date -v+"$((duration_secs + 3600))"S +%Y-%m-%d 2>/dev/null)

useradd \
  --expiredate "${expiry_date}" \
  --shell /bin/bash \
  --create-home \
  --comment "AI Agent Support [${session_id}]" \
  "${agent_user}"
_cleanup_agent_user="${agent_user}"

passwd -l "${agent_user}" >/dev/null 2>&1

agent_home=$(getent passwd "${agent_user}" | cut -d: -f6)
if [[ -z "${agent_home}" ]]; then
  userdel -r "${agent_user}" 2>/dev/null || true
  die "Could not determine home directory for ${agent_user}"
fi

mkdir -p "${agent_home}/.ssh"
chmod 700 "${agent_home}/.ssh"
chown "${agent_user}:${agent_user}" "${agent_home}/.ssh"

printf '  Account created: %s (expires: %s)\n' "${agent_user}" "${expiry_date}"

printf '[2/6] Installing command restriction shell (%s)...\n' "${profile}"

generate_support_shell() {
  local target_profile="${1}"
  local shell_path="${2}"
  local log_path="${3}"

  cat > "${shell_path}" <<SHELL_COMMON
#!/usr/bin/env bash
set -uo pipefail

LOG="${log_path}"
CMD="\${SSH_ORIGINAL_COMMAND:-}"

if [[ -z "\${CMD}" ]]; then
  printf 'Restricted support session. Send commands via: ssh ... '\''command'\''\nProfile: ${target_profile}\n'
  exit 1
fi

log_event() {
  printf '[%s] AGENT_%s: %s\n' "\$(date -u +%Y-%m-%dT%H:%M:%SZ)" "\${1}" "\$(printf '%q' "\${CMD}")" >> "\${LOG}"
}

if printf '%s' "\${CMD}" | grep -qE '[;\|&\$\`(){}<>\\\\]'; then
  log_event "BLOCKED"
  printf 'ERROR: Shell metacharacters are not allowed.\n'
  exit 1
fi

if [[ "\${CMD}" == *\$'\\n'* ]] || [[ "\${CMD}" == *\$'\\r'* ]]; then
  log_event "BLOCKED"
  printf 'ERROR: Newlines are not allowed.\n'
  exit 1
fi

read -ra PARTS <<< "\${CMD}"
[[ \${#PARTS[@]} -gt 0 ]] || { log_event "DENIED"; printf 'ERROR: Empty command.\n'; exit 1; }

COMMAND="\${PARTS[0]}"
ARGS=()
if [[ \${#PARTS[@]} -gt 1 ]]; then
  ARGS=("\${PARTS[@]:1}")
fi

if [[ "\${COMMAND}" == /* ]] || [[ "\${COMMAND}" == ./* ]] || [[ "\${COMMAND}" == ../* ]]; then
  log_event "BLOCKED"
  printf 'ERROR: Commands must be specified by name, not by path.\n'
  exit 1
fi

for arg in "\${ARGS[@]+"\${ARGS[@]}"}"; do
  if [[ "\${arg}" == *".."* ]]; then
    log_event "BLOCKED"
    printf 'ERROR: Path traversal (..) is not allowed.\n'
    exit 1
  fi
done

run_cmd() {
  log_event "EXEC"
  if [[ \${#ARGS[@]} -eq 0 ]]; then
    timeout 300 "\${COMMAND}"
  else
    timeout 300 "\${COMMAND}" "\${ARGS[@]}"
  fi
}

check_paths() {
  local -n allowed_prefixes="\${1}"
  shift
  for arg in "\$@"; do
    [[ "\${arg}" == -* ]] && continue
    if [[ "\${arg}" == /* ]]; then
      local resolved
      resolved=\$(readlink -f "\${arg}" 2>/dev/null || printf '%s' "\${arg}")
      local matched=false
      for prefix in "\${allowed_prefixes[@]}"; do
        if [[ "\${resolved}" == "\${prefix}"* ]]; then
          matched=true
          break
        fi
      done
      if [[ "\${matched}" == false ]]; then
        log_event "BLOCKED"
        printf 'ERROR: Path '\''%s'\'' outside allowed directories.\n' "\${arg}"
        exit 1
      fi
    fi
  done
}
SHELL_COMMON

  case "${target_profile}" in
    diagnostic)
      cat >> "${shell_path}" <<'DIAG_END'

ALLOWED_READ_PATHS=("/var/log/" "/proc/" "/sys/" "/run/" "/tmp/")

dispatch() {
  local sub
  case "${COMMAND}" in
    uptime|hostname|whoami|id|w|uname|df|free|lsblk|mount|ps|journalctl|dmesg|ss|netstat|lsof)
      run_cmd ;;
    dig|nslookup|ping|traceroute|mtr)
      run_cmd ;;
    top)
      if [[ " ${ARGS[*]:-} " == *" -b "* ]] || [[ "${ARGS[0]:-}" == "-bn"* ]]; then
        run_cmd
      else
        log_event "DENIED"; printf 'ERROR: '\''top'\'' requires -b (batch mode).\n'; exit 1
      fi ;;
    cat|head|tail|less|wc|grep|ls)
      check_paths ALLOWED_READ_PATHS "${ARGS[@]}"
      run_cmd ;;
    systemctl)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        status|list-units|is-active|is-enabled|show) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''systemctl %s'\'' not allowed in diagnostic.\n' "${sub}"; exit 1 ;;
      esac ;;
    ip)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        addr|route|link|neigh|rule) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''ip %s'\'' not allowed.\n' "${sub}"; exit 1 ;;
      esac ;;
    docker)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        ps|logs|stats|inspect|images|info|version|top) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''docker %s'\'' not allowed in diagnostic.\n' "${sub}"; exit 1 ;;
      esac ;;
    nginx)
      case "${ARGS[0]:-}" in
        -t|-T|-v) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: Only '\''nginx -t/-T/-v'\'' allowed.\n'; exit 1 ;;
      esac ;;
    apache2ctl|apachectl)
      case "${ARGS[0]:-}" in
        -t|-S|-v) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: Only config test/status allowed.\n'; exit 1 ;;
      esac ;;
    *)
      log_event "DENIED"
      printf 'ERROR: '\''%s'\'' not in allowlist for diagnostic profile.\n' "${COMMAND}"
      exit 1 ;;
  esac
}
dispatch
DIAG_END
      ;;

    remediation)
      cat >> "${shell_path}" <<'REMED_END'

ALLOWED_READ_PATHS=("/var/log/" "/proc/" "/sys/" "/run/" "/tmp/" "/etc/" "/home/")
ALLOWED_WRITE_PATHS=("/etc/" "/var/" "/tmp/" "/home/")

dispatch() {
  local sub
  case "${COMMAND}" in
    uptime|hostname|whoami|id|w|uname|df|free|lsblk|mount|ps|kill|pkill|journalctl|dmesg|ss|netstat|lsof|curl|wget)
      run_cmd ;;
    dig|nslookup|ping|traceroute|mtr)
      run_cmd ;;
    top)
      if [[ " ${ARGS[*]:-} " == *" -b "* ]] || [[ "${ARGS[0]:-}" == "-bn"* ]]; then
        run_cmd
      else
        log_event "DENIED"; printf 'ERROR: '\''top'\'' requires -b (batch mode).\n'; exit 1
      fi ;;
    cat|head|tail|less|wc|grep|sed|awk|ls)
      check_paths ALLOWED_READ_PATHS "${ARGS[@]}"
      run_cmd ;;
    cp|mv|mkdir|chmod|chown)
      check_paths ALLOWED_WRITE_PATHS "${ARGS[@]}"
      run_cmd ;;
    systemctl)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        status|list-units|is-active|is-enabled|show|restart|start|stop|reload|daemon-reload) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''systemctl %s'\'' not allowed.\n' "${sub}"; exit 1 ;;
      esac ;;
    ip)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        addr|route|link|neigh|rule) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''ip %s'\'' not allowed.\n' "${sub}"; exit 1 ;;
      esac ;;
    docker)
      sub="${ARGS[0]:-}"
      case "${sub}" in
        ps|logs|stats|inspect|images|info|version|top|restart|stop|start|exec) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''docker %s'\'' not allowed.\n' "${sub}"; exit 1 ;;
      esac ;;
    nginx)
      case "${ARGS[0]:-}" in
        -t|-T|-v|-s) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''nginx %s'\'' not allowed.\n' "${ARGS[*]:-}"; exit 1 ;;
      esac ;;
    apache2ctl|apachectl)
      case "${ARGS[0]:-}" in
        -t|-S|-v|graceful|restart) run_cmd ;;
        *) log_event "DENIED"; printf 'ERROR: '\''apache %s'\'' not allowed.\n' "${ARGS[*]:-}"; exit 1 ;;
      esac ;;
    *)
      log_event "DENIED"
      printf 'ERROR: '\''%s'\'' not in allowlist for remediation profile.\n' "${COMMAND}"
      exit 1 ;;
  esac
}
dispatch
REMED_END
      ;;
  esac

  chmod 755 "${shell_path}"
}

if [[ "${profile}" != "full" ]]; then
  generate_support_shell "${profile}" "${support_shell}" "${log_file}"
  _cleanup_support_shell="${support_shell}"
  printf '  Restricted shell installed at %s\n' "${support_shell}"
else
  printf '  Profile '\''full'\'': no command restrictions (use with extreme caution)\n'
fi

printf '[3/6] Setting up key material...\n'

pubkey_path=""

if [[ -n "${agent_pubkey}" ]]; then
  pubkey_path="${agent_pubkey}"
  printf '  Using agent-provided public key: %s\n' "${agent_pubkey}"
else
  ssh-keygen -t ed25519 -N "" -f "${key_path}" -C "agent-support-${session_id}" -q
  _cleanup_key_path="${key_path}"
  chmod 600 "${key_path}"
  chmod 644 "${key_path}.pub"
  pubkey_path="${key_path}.pub"
  printf '  Generated session key pair: %s\n' "${key_path}"
  warn "You must securely deliver ${key_path} to the AI agent."
fi

printf '[4/6] Configuring authentication...\n'

cert_options=""
if [[ "${with_pty}" == false ]]; then
  cert_options="-O no-pty"
fi
if [[ "${profile}" != "full" ]]; then
  cert_options="${cert_options} -O force-command=${support_shell}"
fi

if [[ "${use_ca}" == true ]]; then
  ca_private="${ca_dir}/${ca_name}"
  if [[ ! -f "${ca_private}" ]]; then
    userdel -r "${agent_user}" 2>/dev/null || true
    die "CA private key not found at ${ca_private}. Run setup-ca.sh first, or use --no-ca."
  fi

  # shellcheck disable=SC2086
  if ! ssh-keygen -s "${ca_private}" \
    -I "agent-support-${session_id}" \
    -n "${agent_user}" \
    -V "+${duration}" \
    -O no-port-forwarding \
    -O no-x11-forwarding \
    -O no-agent-forwarding \
    ${cert_options} \
    -q "${pubkey_path}"; then
    userdel -r "${agent_user}" 2>/dev/null || true
    rm -f "${support_shell}" "${key_path}" "${key_path}.pub" 2>/dev/null || true
    die "Certificate signing failed. Account and artifacts cleaned up."
  fi

  cert_path="${pubkey_path%.pub}-cert.pub"
  printf '  Certificate signed: %s (valid: +%s)\n  Principals: %s\n' "${cert_path}" "${duration}" "${agent_user}"
else
  expiry_timestamp=$(date -u -d "+${duration_secs} seconds" +%Y%m%d%H%M%S 2>/dev/null || \
    date -u -v+"${duration_secs}"S +%Y%m%d%H%M%S 2>/dev/null)

  ak_options="expiry-time=\"${expiry_timestamp}\",restrict"
  if [[ "${profile}" != "full" ]]; then
    ak_options="${ak_options},command=\"${support_shell}\""
  fi
  if [[ "${with_pty}" == true ]]; then
    ak_options="${ak_options},pty"
  fi

  printf '%s %s\n' "${ak_options}" "$(cat "${pubkey_path}")" > "${agent_home}/.ssh/authorized_keys"
  chmod 600 "${agent_home}/.ssh/authorized_keys"
  chown "${agent_user}:${agent_user}" "${agent_home}/.ssh/authorized_keys"
  chattr +i "${agent_home}/.ssh/authorized_keys" 2>/dev/null || true
  chattr +i "${agent_home}/.ssh" 2>/dev/null || true

  printf '  authorized_keys configured with expiry: %s UTC\n' "${expiry_timestamp}"
fi

printf '[5/6] Scheduling automatic cleanup...\n'

shred_cmd="shred -u"
command -v shred &>/dev/null || shred_cmd="rm -f"

cat > "${cleanup_script}" <<CLEANUP
#!/usr/bin/env bash
set -uo pipefail

printf '[%s] SESSION_END: ${session_id} reason=ttl_expired\n' "\$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${log_file}"

pkill -u "${agent_user}" 2>/dev/null || true
sleep 2
pkill -9 -u "${agent_user}" 2>/dev/null || true

chattr -i "${agent_home}/.ssh/authorized_keys" 2>/dev/null || true
chattr -i "${agent_home}/.ssh" 2>/dev/null || true

mkdir -p /var/log/agent-support-archive
grep "${session_id}" "${log_file}" > "/var/log/agent-support-archive/${session_id}.log" 2>/dev/null || true

userdel -r "${agent_user}" 2>/dev/null || true
${shred_cmd} "${key_path}" "${key_path}.pub" "${key_path}-cert.pub" 2>/dev/null || true
rm -f "${support_shell}"
rm -f "\${0}"

printf '[%s] CLEANUP_COMPLETE: ${session_id}\n' "\$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${log_file}"
CLEANUP

chmod 700 "${cleanup_script}"
_cleanup_cleanup_script="${cleanup_script}"

cleanup_delay_mins=$(( (duration_secs + 600 + 59) / 60 ))

if command -v at &>/dev/null; then
  printf 'bash %s\n' "${cleanup_script}" | at "now + ${cleanup_delay_mins} minutes" 2>&1 | tail -1
  printf '  Cleanup scheduled via at(1) in %d minutes\n' "${cleanup_delay_mins}"
elif command -v systemd-run &>/dev/null; then
  systemd-run --on-active="$((cleanup_delay_mins * 60))s" \
    --unit="agent-cleanup-${session_id}" \
    --description="Cleanup agent support session ${session_id}" \
    bash "${cleanup_script}"
  printf '  Cleanup scheduled via systemd timer in %d minutes\n' "${cleanup_delay_mins}"
else
  printf '  WARNING: No scheduler available. Manual cleanup required:\n'
  printf '    sudo bash %s\n' "${cleanup_script}"
fi

printf '[%s] SESSION_START: %s user=%s host=%s ttl=%s profile=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${session_id}" "${agent_user}" \
  "${target_host}" "${duration}" "${profile}" >> "${log_file}"

printf '[6/6] Done.\n\n'
printf '===========================================\n'
printf '  Temporary SSH Access Granted\n'
printf '===========================================\n'
printf '  Session ID:   %s\n' "${session_id}"
printf '  Target Host:  %s\n' "${target_host}"
printf '  Username:     %s\n' "${agent_user}"
printf '  Duration:     %s (%ds)\n' "${duration}" "${duration_secs}"
printf '  Profile:      %s\n' "${profile}"

expiry_time=$(date -u -d "+${duration_secs} seconds" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
  date -u -v+"${duration_secs}"S +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)
printf '  Expires:      %s\n' "${expiry_time}"

if [[ -n "${agent_pubkey}" ]]; then
  printf '\n  Agent connects with their own key:\n'
  printf '    ssh -i <agent-private-key> %s@%s\n' "${agent_user}" "${target_host}"
  if [[ "${use_ca}" == true ]]; then
    printf '\n  Deliver this certificate to the agent:\n    %s\n' "${cert_path}"
  fi
else
  printf '\n  Private Key:  %s\n' "${key_path}"
  if [[ "${use_ca}" == true ]]; then
    printf '  Certificate:  %s-cert.pub\n' "${key_path}"
  fi
  printf '\n  IMPORTANT: Securely deliver the private key to the AI agent.\n'
  printf '  Connect with:\n    ssh -i %s %s@%s\n' "${key_path}" "${agent_user}" "${target_host}"
fi

printf '\n  Example commands:\n'
printf '    ssh ... %s@%s '\''uptime'\''\n' "${agent_user}" "${target_host}"
printf '    ssh ... %s@%s '\''df -h'\''\n' "${agent_user}" "${target_host}"
printf '    ssh ... %s@%s '\''journalctl -n 50 --no-pager'\''\n' "${agent_user}" "${target_host}"
printf '\n  Revoke immediately:\n'
printf '    sudo bash scripts/revoke-access.sh --session %s\n' "${session_id}"
printf '===========================================\n'

# Success — disable failure cleanup trap
trap - EXIT
