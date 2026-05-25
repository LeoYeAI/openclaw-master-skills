#!/usr/bin/env bash
# linux-system-health diagnostic commands
# Run as root with: export LANG=C
# Each section is independent — run sections relevant to the reported symptoms.
#
# DATA ACCESS SCOPE — this script reads the following system areas:
#   Filesystem config : /etc/os-release, /etc/resolv.conf, /etc/security/limits.conf,
#                       /etc/default/locale, /etc/locale.conf, /etc/systemd/journald.conf
#   Kernel interfaces : /proc/meminfo, /proc/stat, /proc/loadavg, /proc/sys/fs/*,
#                       /proc/sys/kernel/*, /proc/sys/net/*, /sys/kernel/mm/*
#   Kernel ring buffer: dmesg (may contain process names and OOM details)
#   Systemd journal   : journalctl (kernel messages only, via -k flag)
#   Log directory     : /var/log/ (size enumeration only, does NOT read log content)
#   Process table     : ps, ss -p (exposes PID, command names, socket owners)
#   User home dirs    : /root/.cache/ms-playwright, /home/*/.cache/ms-playwright
#                       (Section 16 only — searches for Chromium binaries)
#   Network probes    : DNS resolution tests (nslookup/dig/getent to github.com),
#                       nameserver TCP/53 reachability, Chrome headless launch test
#
# WRITE OPERATIONS:
#   Section 12 only — creates and immediately removes /tmp/.oc_write_test
#   to verify filesystem writability. No other writes are performed.

###############################################
# Section 1: System Environment Baseline
###############################################

# OS identification
cat /etc/os-release 2>/dev/null || cat /etc/system-release 2>/dev/null

# Kernel and architecture
uname -r
uname -m

# Uptime and load
uptime

# Memory overview
free -h

# Disk overview
df -Th

# CPU count
nproc

###############################################
# Section 2: Memory & OOM
###############################################

# Current memory
free -h

# Detailed memory info
cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree'

# Kernel OOM events
dmesg | grep -iE 'out of memory|oom-killer|killed process'

# Journal OOM events
journalctl --no-pager -k | grep -iE 'oom-killer|killed process' 2>/dev/null

# Syslog OOM events
grep -iE 'out of memory|oom-killer' /var/log/messages /var/log/syslog 2>/dev/null | tail -20

# Which processes were OOM-killed
dmesg | grep -i 'oom-killer' | grep -oP 'comm="\K[^"]+' 2>/dev/null | sort | uniq -c | sort -rn | head -5

# Top memory consumers
ps -eo rss,pid,comm --sort=-rss | head -11

###############################################
# Section 3: CPU & Performance
###############################################

# System load overview
top -bn1 | head -5

# CPU time breakdown
cat /proc/stat | head -1
# Format: cpu user nice system idle iowait irq softirq steal

# Load averages and CPU count
cat /proc/loadavg
nproc

# Top CPU consumers
ps -eo %cpu,pid,comm --sort=-%cpu | head -11

###############################################
# Section 4: Network Infrastructure
###############################################

# All listening TCP ports
ss -tlnp

# Network interfaces — IPv4 vs IPv6
ip addr show | grep -E 'inet |inet6 '

# IPv6 state
sysctl net.ipv6.conf.all.disable_ipv6 2>/dev/null

# DNS configuration
cat /etc/resolv.conf

# Firewall rules
iptables -L -n 2>/dev/null | head -20

###############################################
# Section 5: Disk & inotify
###############################################

# Disk usage
df -Th

# Inode usage
df -ih

# inotify limits
cat /proc/sys/fs/inotify/max_user_watches
cat /proc/sys/fs/inotify/max_user_instances

###############################################
# Section 6: File Descriptor & Process Limits
###############################################

# Current shell nofile limit
ulimit -n

# System-wide limits config
cat /etc/security/limits.conf 2>/dev/null | grep -v '^#' | grep -i nofile

# Kernel maximums
sysctl fs.nr_open
sysctl fs.file-max

# Current system-wide file descriptor usage
cat /proc/sys/fs/file-nr
# Format: allocated  free  max

# PID space
sysctl kernel.pid_max

###############################################
# Section 7: Kernel & Sysctl Tuning
###############################################

# Key kernel parameters
sysctl -a 2>/dev/null | grep -E \
  'net.core.somaxconn|net.ipv4.tcp_max_tw_buckets|net.netfilter.nf_conntrack_max|net.ipv4.tcp_tw_reuse|net.ipv4.ip_local_port_range|net.ipv4.tcp_fin_timeout|net.core.netdev_max_backlog|vm.swappiness|vm.overcommit_memory'

# Conntrack overflow events
dmesg | grep -i 'nf_conntrack.*table full'

# TCP connection state summary
ss -s

# TCP extended stats
cat /proc/net/netstat | grep -E 'TcpExt|ListenOverflows|ListenDrops'

# Swap info
swapon --show 2>/dev/null

###############################################
# Section 8: DNS Resolution Health
###############################################

# DNS configuration
cat /etc/resolv.conf

# Count nameserver lines
grep -c '^nameserver' /etc/resolv.conf 2>/dev/null

# Resolution test (multiple methods, fallback chain)
timeout 5 nslookup github.com 2>&1 || timeout 5 dig +short github.com 2>&1 || timeout 5 getent hosts github.com 2>&1

# Nameserver reachability
for ns in $(grep '^nameserver' /etc/resolv.conf | awk '{print $2}'); do
  timeout 3 bash -c "echo >/dev/tcp/$ns/53" 2>/dev/null && echo "$ns reachable" || echo "$ns UNREACHABLE"
done

# systemd-resolved status
systemctl is-active systemd-resolved 2>/dev/null
resolvectl status 2>/dev/null | head -10

###############################################
# Section 9: Time Synchronization
###############################################

# Time and NTP status
timedatectl 2>/dev/null

# NTP service status (check all common implementations)
systemctl is-active chronyd 2>/dev/null || echo "chronyd not active"
systemctl is-active ntpd 2>/dev/null || echo "ntpd not active"
systemctl is-active systemd-timesyncd 2>/dev/null || echo "systemd-timesyncd not active"

# Clock offset (chrony)
chronyc tracking 2>/dev/null | grep -E 'System time|Last offset'

# Clock offset (ntpd)
ntpstat 2>/dev/null

# Hardware clock vs system clock
hwclock --show 2>/dev/null
date '+%Y-%m-%d %H:%M:%S %Z'

###############################################
# Section 10: Zombie & D-State Processes
###############################################

# Zombie process count
ZOMBIE_COUNT=$(ps aux | awk '$8 ~ /^Z/ {count++} END {print count+0}')
echo "Zombie processes: $ZOMBIE_COUNT"

# List zombies with parent
ps -eo pid,ppid,stat,comm | awk '$3 ~ /^Z/'

# D-state (uninterruptible sleep) processes
DSTATE_COUNT=$(ps aux | awk '$8 ~ /^D/ {count++} END {print count+0}')
echo "D-state processes: $DSTATE_COUNT"
ps -eo pid,stat,wchan,comm | awk '$2 ~ /^D/'

# Total process count vs limit
echo "Total processes: $(ps -e --no-headers | wc -l)"
sysctl kernel.pid_max

###############################################
# Section 11: Systemd Journal & Log Disk Usage
###############################################

# Journal disk usage
journalctl --disk-usage 2>/dev/null

# Journal retention config
grep -E 'SystemMaxUse|SystemKeepFree|MaxRetentionSec' /etc/systemd/journald.conf 2>/dev/null

# /var/log total size
du -sh /var/log/ 2>/dev/null

# Largest log files
find /var/log -type f -size +100M 2>/dev/null | head -10

###############################################
# Section 12: Filesystem Integrity
###############################################

# Read-only filesystem detection (exclude virtual filesystems)
mount | grep -E '\bro\b' | grep -v 'proc\|sys\|cgroup\|tmpfs\|squashfs\|snap'

# Filesystem errors in dmesg
dmesg | grep -iE 'EXT4-fs error|XFS.*error|remount.*read-only|I/O error' | tail -10

# Inode usage — high inode consumption on any filesystem
df -ih | awk 'NR>1 && $5 ~ /%/ {gsub(/%/,"",$5); if ($5+0 >= 80) print}'

# Write test (self-cleaning)
touch /tmp/.oc_write_test 2>/dev/null && rm -f /tmp/.oc_write_test && echo "Write OK" || echo "Write FAILED"

###############################################
# Section 13: Firewall & Outbound Connectivity
###############################################

# iptables DROP/REJECT rules on INPUT and OUTPUT
iptables -L INPUT -n --line-numbers 2>/dev/null | grep -iE 'DROP|REJECT'
iptables -L OUTPUT -n --line-numbers 2>/dev/null | grep -iE 'DROP|REJECT'

# nftables (modern replacement for iptables)
nft list ruleset 2>/dev/null | grep -iE 'drop|reject' | head -10

# ufw status
ufw status 2>/dev/null

# Outbound HTTPS connectivity test (generic target)
# timeout 5 bash -c 'echo >/dev/tcp/1.1.1.1/443' 2>/dev/null && echo "Outbound 443 OK" || echo "Outbound 443 BLOCKED"

# Outbound HTTP connectivity test
# timeout 5 bash -c 'echo >/dev/tcp/1.1.1.1/80' 2>/dev/null && echo "Outbound 80 OK" || echo "Outbound 80 BLOCKED"

###############################################
# Section 14: Transparent Hugepages
###############################################

# THP status
cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null

# THP defrag status
cat /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null

# Current AnonHugePages usage
grep AnonHugePages /proc/meminfo 2>/dev/null

###############################################
# Section 15: TCP Connection Overload
###############################################

# Total TCP connections by state
ss -ant | awk 'NR>1 {state[$1]++} END {for (s in state) print s, state[s]}' | sort -k2 -rn

# Total TCP connection count
ss -ant | tail -n +2 | wc -l

# CLOSE_WAIT connections (application not closing sockets properly)
CLOSE_WAIT_COUNT=$(ss -ant state close-wait | tail -n +2 | wc -l)
echo "CLOSE_WAIT connections: $CLOSE_WAIT_COUNT"

# CLOSE_WAIT by process (identify leaking applications)
ss -antp state close-wait 2>/dev/null | awk '{print $NF}' | sort | uniq -c | sort -rn | head -10

# ESTABLISHED connections count
ESTAB_COUNT=$(ss -ant state established | tail -n +2 | wc -l)
echo "ESTABLISHED connections: $ESTAB_COUNT"

# Top processes by connection count
ss -antp 2>/dev/null | awk -F'"' '{print $2}' | sort | uniq -c | sort -rn | head -10

# Ephemeral port range and usage
sysctl net.ipv4.ip_local_port_range
ss -ant | awk 'NR>1 {split($4,a,":"); if(a[length(a)]>=32768) count++} END {print "Ephemeral ports in use:", count+0}'

###############################################
# Section 16: Headless Browser / Chromium Dependencies
###############################################

# Step 1: Locate chromium binary (system-installed and Playwright-bundled)
CHROME_BIN=""
for candidate in $(which chromium chromium-browser google-chrome google-chrome-stable 2>/dev/null); do
  [ -x "$candidate" ] && CHROME_BIN="$candidate" && break
done
if [ -z "$CHROME_BIN" ]; then
  CHROME_BIN=$(find /root/.cache/ms-playwright /home/*/.cache/ms-playwright -name chrome -type f 2>/dev/null | head -1)
fi
echo "Chrome binary: ${CHROME_BIN:-not found}"

# Step 2: If Chrome binary found, test if it launches in headless mode
if [ -n "$CHROME_BIN" ]; then
  CHROME_TEST=$(timeout 5 "$CHROME_BIN" --headless=new --no-sandbox --disable-gpu --dump-dom about:blank 2>&1)
  CHROME_EXIT=$?
  if [ $CHROME_EXIT -eq 0 ]; then
    echo "Chrome headless test: OK"
    # Chrome works — skip dependency diagnosis
  else
    echo "Chrome headless test: FAILED (exit $CHROME_EXIT)"
    echo "$CHROME_TEST" | tail -5

    # Step 3: Diagnose dependencies only when Chrome is broken
    # Use lib stem patterns for cross-distro matching:
    #   Debian: libgtk-3-0.so  vs  RHEL: libgtk-3.so.0  →  match on "libgtk-3"
    LDCONFIG_BIN=$(which ldconfig 2>/dev/null || echo "/sbin/ldconfig")
    for lib_pattern in libnss3 libatk-bridge-2.0 libgbm libxkbcommon \
                       libdrm libgtk-3 libasound; do
      $LDCONFIG_BIN -p 2>/dev/null | grep -q "$lib_pattern" && echo "$lib_pattern OK" || echo "$lib_pattern MISSING"
    done

    # ldd on chromium binary (detect unresolvable dynamic links)
    ldd "$CHROME_BIN" 2>/dev/null | grep 'not found'

    # User namespace clone support (Chrome sandbox requirement)
    cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo "sysctl not present (likely allowed)"
  fi
else
  echo "No Chrome/Chromium binary found — skipping headless test"
fi

###############################################
# Section 17: Locale & Encoding Configuration
###############################################

# Resolve locale binary (may not be in non-root user's PATH)
LOCALE_BIN=$(command -v locale 2>/dev/null || echo /usr/bin/locale)
[ ! -x "$LOCALE_BIN" ] && echo "locale command not found" && LOCALE_BIN=""

# Read configured locale from PERSISTENT config files (not $LANG, which may
# have been overridden to "C" by the diagnostic runner).
# Priority: /etc/default/locale (Debian/Ubuntu) → /etc/locale.conf (RHEL/systemd)
CONFIGURED_LOCALE=""
if [ -f /etc/default/locale ]; then
  CONFIGURED_LOCALE=$(grep -m1 '^LANG=' /etc/default/locale 2>/dev/null | cut -d= -f2 | tr -d '"')
fi
if [ -z "$CONFIGURED_LOCALE" ] && [ -f /etc/locale.conf ]; then
  CONFIGURED_LOCALE=$(grep -m1 '^LANG=' /etc/locale.conf 2>/dev/null | cut -d= -f2 | tr -d '"')
fi
# Fallback: localectl (works on systemd systems)
if [ -z "$CONFIGURED_LOCALE" ]; then
  CONFIGURED_LOCALE=$(localectl show-locale 2>/dev/null | grep -m1 '^LANG=' | cut -d= -f2)
fi
echo "Persistent LANG=${CONFIGURED_LOCALE:-not configured}"

# Show locale vars using the persistent LANG (not the runtime LANG=C from diagnostic runner)
[ -n "$LOCALE_BIN" ] && [ -n "$CONFIGURED_LOCALE" ] && LANG="$CONFIGURED_LOCALE" $LOCALE_BIN 2>/dev/null

# Available UTF-8 locales
[ -n "$LOCALE_BIN" ] && $LOCALE_BIN -a 2>/dev/null | grep -iE 'utf-?8' | head -20

# Check if the persistently configured locale is actually installed
# Note: LANG uses "en_US.UTF-8" but locale -a outputs "en_US.utf8", so normalize before comparison
if [ -n "$LOCALE_BIN" ] && [ -n "$CONFIGURED_LOCALE" ] && [ "$CONFIGURED_LOCALE" != "C" ] && [ "$CONFIGURED_LOCALE" != "POSIX" ]; then
  NORMALIZED=$(echo "$CONFIGURED_LOCALE" | sed 's/UTF-8/utf8/g')
  $LOCALE_BIN -a 2>/dev/null | grep -qiF "$NORMALIZED" && \
    echo "Locale $CONFIGURED_LOCALE installed" || echo "Locale $CONFIGURED_LOCALE NOT INSTALLED"
fi

# Persistent locale config
cat /etc/default/locale 2>/dev/null
cat /etc/locale.conf 2>/dev/null
