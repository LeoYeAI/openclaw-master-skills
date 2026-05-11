#!/bin/bash
# collect-env.sh — Collect environment information, output JSON
# Timeout: 15s | Compatible: macOS (darwin) + Linux
set -euo pipefail

get_os() {
  uname -s
}

get_os_version() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    sw_vers -productVersion 2>/dev/null || uname -r
  else
    # Try /etc/os-release first (systemd distros), fallback to uname
    source /etc/os-release 2>/dev/null && echo "${PRETTY_NAME:-$(uname -r)}" || uname -r
  fi
}

get_arch() {
  uname -m
}

get_node_version() {
  node --version 2>/dev/null | tr -d 'v' || echo "NOT_FOUND"
}

get_npm_version() {
  npm --version 2>/dev/null || echo "NOT_FOUND"
}

get_pnpm_version() {
  pnpm --version 2>/dev/null || echo "NOT_FOUND"
}

# Parse "🦞 OpenClaw 2026.3.2 (85377a2) — The lobster in your shell. 🦞" format
get_openclaw_info() {
  local raw
  raw=$(openclaw --version 2>/dev/null) || { echo '{"available":false,"raw":"NOT_FOUND"}'; return; }
  local version commit
  version=$(echo "$raw" | grep -oE 'OpenClaw [0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?' | awk '{print $2}' | head -1)
  commit=$(echo "$raw"  | grep -oE '\([0-9a-f]{6,}\)' | tr -d '()' | head -1)
  version="${version:-UNKNOWN}"
  commit="${commit:-UNKNOWN}"
  printf '{"available":true,"version":"%s","commit":"%s","raw":"%s"}' \
    "$version" "$commit" "$(echo "$raw" | head -1 | sed 's/"/\\"/g')"
}

get_clawhub_version() {
  clawhub --version 2>/dev/null | head -1 | sed 's/"/\\"/g' || echo "NOT_FOUND"
}

get_memory_total_mb() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1048576}'
  else
    awk '/MemTotal/{printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0
  fi
}

get_memory_available_mb() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    local page_size free_pages inactive_pages
    page_size=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    free_pages=$(vm_stat 2>/dev/null | awk '/Pages free/{gsub(/\./,""); print $3}' || echo 0)
    inactive_pages=$(vm_stat 2>/dev/null | awk '/Pages inactive/{gsub(/\./,""); print $3}' || echo 0)
    echo $(( (free_pages + inactive_pages) * page_size / 1048576 ))
  else
    awk '/MemAvailable/{printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || \
    free -m 2>/dev/null | awk '/Mem:/{print $7}'
  fi
}

# Disk: use df -k (1024-byte blocks, works on both macOS and Linux)
# Convert KB → GB (SI, 1 GB = 10^9 bytes): blocks * 1024 / 1_000_000_000
# Divisor: 1_000_000_000 / 1024 = 976562.5 ≈ 976563
get_disk_total_gb() {
  df -k / 2>/dev/null | awk 'NR==2{printf "%.1f", $2/976563}'
}

get_disk_available_gb() {
  df -k / 2>/dev/null | awk 'NR==2{printf "%.1f", $4/976563}'
}

get_cpu_cores() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    sysctl -n hw.logicalcpu 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 0
  else
    nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 0
  fi
}

get_cpu_load() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    # vm.loadavg format: "{ 1.23 2.34 3.45 }"
    sysctl -n vm.loadavg 2>/dev/null | awk '{
      # strip leading { and trailing } — field 2 is 1-min load
      for(i=1;i<=NF;i++) if($i~/^[0-9]/) {print $i; exit}
    }'
  else
    awk '{print $1}' /proc/loadavg 2>/dev/null || echo "0.0"
  fi
}

# macOS: parse boot timestamp robustly from kern.boottime
# Format: { sec = 1741219200, usec = 0 } Mon Mar  3 00:00:00 2026
get_uptime_hours() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    local boot_sec now
    boot_sec=$(sysctl -n kern.boottime 2>/dev/null \
      | grep -oE 'sec = [0-9]+' \
      | grep -oE '[0-9]+')
    if [[ -n "$boot_sec" && "$boot_sec" =~ ^[0-9]+$ ]]; then
      now=$(date +%s)
      echo $(( (now - boot_sec) / 3600 ))
    else
      echo 0
    fi
  else
    awk '{printf "%d", $1/3600}' /proc/uptime 2>/dev/null || echo 0
  fi
}

# Output JSON
openclaw_info=$(get_openclaw_info)

cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system": {
    "platform": "$(get_os)",
    "os_version": "$(get_os_version | sed 's/"/\\"/g')",
    "arch": "$(get_arch)"
  },
  "versions": {
    "node": "$(get_node_version)",
    "npm": "$(get_npm_version)",
    "pnpm": "$(get_pnpm_version)",
    "openclaw": $openclaw_info,
    "clawhub": "$(get_clawhub_version)"
  },
  "memory": {
    "total_mb": $(get_memory_total_mb),
    "available_mb": $(get_memory_available_mb)
  },
  "disk": {
    "total_gb": $(get_disk_total_gb),
    "available_gb": $(get_disk_available_gb)
  },
  "cpu": {
    "cores": $(get_cpu_cores),
    "load_avg_1m": $(get_cpu_load)
  },
  "uptime_hours": $(get_uptime_hours)
}
EOF
