---
name: linux-system-health
description: Diagnose Linux OS-level issues — slow server, OOM kills, disk full, high CPU/load, DNS failures, connection timeouts, port exhaustion, too many open files, zombie processes, browser automation failures, locale problems, and kernel misconfigurations.
version: 1.3.0
tags:
  - linux
  - diagnostics
  - performance
  - memory
  - disk
  - network
  - troubleshooting
metadata:
  openclaw:
    os:
      - linux
    requires:
      bins:
        # Core — used across multiple sections, must be present
        - bash
        - ps          # procps
        - ss          # iproute2
        - ip          # iproute2
        - free        # procps
        - df          # coreutils
        - sysctl      # procps
        - dmesg       # util-linux
        - mount       # util-linux
        - journalctl  # systemd
        - systemctl   # systemd
      optional_bins:
        # Section-specific — script handles absence via 2>/dev/null or fallback chains
        - iptables    # Sec 13 firewall
        - nft         # Sec 13 nftables
        - ufw         # Sec 13 ufw
        - nslookup    # Sec 8  DNS (fallback: dig → getent)
        - dig         # Sec 8  DNS (fallback option)
        - timedatectl # Sec 9  time sync
        - chronyc     # Sec 9  chrony NTP
        - ntpstat     # Sec 9  ntpd status
        - hwclock     # Sec 9  hardware clock
        - ldconfig    # Sec 16 browser deps
        - ldd         # Sec 16 binary link check
        - locale      # Sec 17 locale info
        - localectl   # Sec 17 locale config
    emoji: "\U0001F5A5"
    homepage: https://github.com/ecsgo-helper/openclaw-system-health
---

# Linux System Health Diagnostic Skill

You are a Linux OS diagnostic expert. When a user reports any of the following problems, use this skill:
- **Performance**: server slow, high load, lag, unresponsive
- **Memory**: OOM killed, out of memory, memory leak, swap thrashing
- **Disk**: disk full, read-only filesystem, inode exhaustion, log files too large
- **CPU**: high CPU, IO wait, process stuck, load average spike
- **Network**: DNS failure, connection timeout, port exhaustion, CLOSE_WAIT accumulation, firewall blocking
- **Process**: crash, zombie processes, too many open files, file descriptor limit
- **Browser automation**: missing shared libraries, Chromium sandbox error, headless browser failures
- **Locale/Encoding**: garbled text, character encoding issues, locale not configured

Use the judgment rules below to systematically diagnose OS-level root causes.

**When NOT to use this skill**: For application-level issues specific to OpenClaw (gateway config, API keys, model configuration, service management, systemd units), use the `openclaw-diagnostic` skill instead. This skill only covers OS-level diagnostics.

**Diagnostic workflow**:
1. Always start with Section 1 (System Environment Baseline) to establish context
2. Then run the sections relevant to the user's reported symptoms
3. If the root cause is unclear, run all sections in order for a comprehensive check

> **Commands**: Run the corresponding section in [scripts/diagnostics.sh](scripts/diagnostics.sh). Run as root with `export LANG=C`.
>
> **Issue Registry**: See [reference.md](reference.md) for severity level definitions and the complete issue name table.

**Data access scope** — this skill collects OS-level diagnostic data. Review before running in sensitive environments:

| Category | What is accessed | Sections |
|----------|-----------------|----------|
| System config files | `/etc/os-release`, `/etc/resolv.conf`, `/etc/security/limits.conf`, `/etc/default/locale`, `/etc/locale.conf`, `/etc/systemd/journald.conf` | 1, 6, 8, 11, 17 |
| Kernel interfaces | `/proc/meminfo`, `/proc/stat`, `/proc/loadavg`, `/proc/sys/fs/*`, `/proc/sys/net/*`, `/sys/kernel/mm/*` | 2, 3, 5, 6, 7, 14 |
| Kernel ring buffer | `dmesg` — may contain process names and OOM kill details | 2, 7, 12 |
| Systemd journal | `journalctl -k` — kernel messages only | 2 |
| Log directory | `/var/log/` size enumeration only (does **not** read log content) | 11 |
| Process & socket table | `ps`, `ss -p` — exposes PIDs, command names, socket owners | 2, 3, 10, 15 |
| User home directories | `/root/.cache/ms-playwright`, `/home/*/.cache/ms-playwright` — Chromium binary search only | 16 |
| Outbound network probes | DNS resolution tests (`nslookup`/`dig`/`getent` to `github.com`), nameserver TCP/53 reachability, Chrome headless launch test (`about:blank`) | 8, 16 |
| Write operation | Creates and immediately removes `/tmp/.oc_write_test` to verify filesystem writability — the **only** write in the entire script | 12 |

**Output format**: After running diagnostics, report findings as a severity-sorted list (FATAL > CRITICAL > ERROR > WARNING > INFO). For each issue found, include:
- Issue name (e.g., `OpenClaw.Memory.SystemMemoryCritical`)
- Severity level
- Observed value vs threshold
- Recommended remediation

---

## 1. System Environment Baseline

Collect OS context for subsequent analysis.

**Judgment rules**:
- Record output as **OpenClaw.System.EnvironmentBaseline** (INFO) — no issues, context only.

---

## 2. Memory & OOM

Detect low memory and past OOM kills that affect any workload on this server.

**Judgment rules**:
- MemAvailable / MemTotal < 5% → **OpenClaw.Memory.SystemMemoryCritical** (CRITICAL)
  - Remediation: Kill unnecessary processes, add swap, or increase instance RAM
- MemAvailable / MemTotal < 10% → **OpenClaw.Memory.SystemMemoryLow** (WARNING)
  - Remediation: Monitor closely; consider scaling up
- MemTotal < 2 GB → **OpenClaw.Memory.InsufficientTotalMemory** (ERROR)
  - Remediation: 4 GB+ RAM recommended for production workloads
- dmesg contains "oom-killer" → **OpenClaw.Memory.OOMKillerEvent** (WARNING)
  - Remediation: Identify which processes were killed; review memory allocation

---

## 3. CPU & Performance

Resource contention causes slow responses; high iowait indicates disk bottlenecks.

**Judgment rules**:
- Load average (1 min) > 2x `nproc` → **OpenClaw.CPU.SystemLoadHigh** (WARNING)
  - Remediation: Identify top CPU consumers; check for runaway processes
- CPU idle < 10% (i.e., total utilization > 90%) → **OpenClaw.CPU.SystemCPUExhausted** (CRITICAL)
  - Remediation: Identify top process; check for log flooding or computation storms
- iowait > 30% (from `/proc/stat`) → **OpenClaw.CPU.HighIOWait** (WARNING)
  - Remediation: Check disk I/O — likely excessive logging or disk-bound workload

---

## 4. Network Infrastructure

Basic network configuration, DNS, IPv6, and firewall state.

**Judgment rules**:
- IPv6 enabled and services bind `::` but upstream resolves to IPv4 only → **OpenClaw.Network.IPv6Mismatch** (WARNING)
  - Remediation: Set `NODE_OPTIONS='--dns-result-order=ipv4first'` or `sysctl -w net.ipv6.conf.all.disable_ipv6=1`

---

## 5. Disk & inotify

Disk space exhaustion and inotify limits cause "ENOSPC" errors.

**Judgment rules**:
- Any filesystem usage >= 95% → **OpenClaw.Disk.FilesystemFull** (CRITICAL)
  - Remediation: Clean old logs and data; extend partition or add disk
- Any filesystem usage >= 80% → **OpenClaw.Disk.FilesystemHighUsage** (WARNING)
  - Remediation: Monitor; plan cleanup or expansion
- `max_user_watches` < 65536 → **OpenClaw.Disk.InotifyWatchesTooLow** (ERROR)
  - Remediation: `echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.d/99-inotify.conf && sysctl -p /etc/sysctl.d/99-inotify.conf`
- `max_user_instances` < 256 → **OpenClaw.Disk.InotifyInstancesTooLow** (WARNING)
  - Remediation: `echo 'fs.inotify.max_user_instances=512' >> /etc/sysctl.d/99-inotify.conf && sysctl -p /etc/sysctl.d/99-inotify.conf`

---

## 6. File Descriptor & Process Limits

Low ulimits cause "too many open files" (EMFILE) errors under load.

**Judgment rules**:
- Shell `ulimit -n` < 4096 → **OpenClaw.Limits.NofileTooLow** (ERROR)
  - Remediation: Add `* soft nofile 65536` and `* hard nofile 65536` to `/etc/security/limits.conf`; re-login
- limits.conf `nofile` value > `fs.nr_open` → **OpenClaw.Limits.NofileExceedsKernelMax** (CRITICAL)
  - Remediation: Increase `fs.nr_open` first: `sysctl -w fs.nr_open=1048576` and persist in `/etc/sysctl.d/`
- `file-nr` allocated / max > 80% → **OpenClaw.Limits.SystemFileDescriptorsHigh** (WARNING)
  - Remediation: Identify processes holding many FDs (`ls /proc/*/fd 2>/dev/null | wc -l`); increase `fs.file-max` if needed

---

## 7. Kernel & Sysctl Tuning

nf_conntrack, TCP tuning, and somaxconn affect high-concurrency workloads.

**Judgment rules**:
- `nf_conntrack_max` < 65536 → **OpenClaw.Kernel.NfConntrackMaxTooLow** (ERROR)
  - Remediation: `sysctl -w net.netfilter.nf_conntrack_max=262144` and persist in `/etc/sysctl.d/99-sysctl.conf`
- dmesg contains "nf_conntrack: table full" → **OpenClaw.Kernel.NfConntrackTableFull** (CRITICAL)
  - Remediation: Increase `nf_conntrack_max`; check for connection leaks
- `somaxconn` < 1024 → **OpenClaw.Kernel.SomaxconnTooLow** (WARNING)
  - Remediation: `sysctl -w net.core.somaxconn=4096` and persist
- `tcp_max_tw_buckets` < 10000 → **OpenClaw.Kernel.TcpMaxTwBucketsTooLow** (WARNING)
  - Remediation: `sysctl -w net.ipv4.tcp_max_tw_buckets=262144`
- `tcp_tw_reuse = 0` → **OpenClaw.Kernel.TcpTwReuseNotEnabled** (WARNING)
  - Remediation: `sysctl -w net.ipv4.tcp_tw_reuse=1`
- TIME_WAIT count from `ss -s` > 10000 → **OpenClaw.Kernel.TimeWaitOverflow** (WARNING)
  - Remediation: Enable `tcp_tw_reuse`, increase `tcp_max_tw_buckets`, reduce `tcp_fin_timeout`
- ListenOverflows > 0 in `/proc/net/netstat` → **OpenClaw.Kernel.TcpListenOverflows** (WARNING)
  - Remediation: Increase `somaxconn` and application backlog setting
- `vm.overcommit_memory = 2` and swap < 1 GB → **OpenClaw.Kernel.StrictOvercommitWithLowSwap** (WARNING)
  - Remediation: Add swap space or set `vm.overcommit_memory=0`

---

## 8. DNS Resolution Health

Broken or slow DNS causes `EAI_AGAIN` errors, API timeouts, and silent connectivity failures.

**Judgment rules**:
- `/etc/resolv.conf` is empty or has zero `nameserver` lines → **OpenClaw.Network.NoDNSNameservers** (ERROR)
  - Remediation: Add nameservers — e.g., `echo 'nameserver 8.8.8.8' >> /etc/resolv.conf`; for systemd-resolved check `/etc/systemd/resolved.conf`
- `nslookup`, `dig`, and `getent` all fail for a known-good domain → **OpenClaw.Network.DNSResolutionFailed** (CRITICAL)
  - Remediation: Verify network connectivity; check if nameservers are reachable; inspect firewall rules blocking UDP/TCP port 53
- Any configured nameserver fails TCP/53 reachability test → **OpenClaw.Network.DNSNameserverUnreachable** (WARNING)
  - Remediation: Replace unreachable nameserver in `/etc/resolv.conf`; consider adding a backup nameserver

---

## 9. Time Synchronization

Clock drift causes SSL/TLS certificate validation failures, API auth token rejection, and log timestamp inconsistencies.

**Judgment rules**:
- None of `chronyd`, `ntpd`, or `systemd-timesyncd` is active → **OpenClaw.Time.NTPServiceNotRunning** (ERROR)
  - Remediation: Install and enable a time sync service — `yum install chrony && systemctl enable --now chronyd` (RHEL/CentOS) or `apt install chrony && systemctl enable --now chronyd` (Debian/Ubuntu)
- `timedatectl` shows "NTP synchronized: no" → **OpenClaw.Time.ClockNotSynchronized** (CRITICAL)
  - Remediation: Start NTP service; verify NTP server reachability (`chronyc sources` or `ntpq -p`); check firewall allows UDP port 123
- `chronyc tracking` shows system clock offset > 3 seconds, or hwclock drift > 5 seconds from system time → **OpenClaw.Time.ClockDriftDetected** (WARNING)
  - Remediation: Force sync — `chronyc makestep` or `ntpdate -u pool.ntp.org`; investigate why drift occurred (suspended VM, unreachable NTP server)

---

## 10. Zombie & D-State Processes

Zombie processes indicate child process leaks; D-state (uninterruptible sleep) processes signal I/O hangs that block system operations.

**Judgment rules**:
- Zombie count > 10 → **OpenClaw.Process.ZombieProcessesHigh** (WARNING)
  - Remediation: Identify parent processes (`ps -eo pid,ppid,stat,comm | awk '$3~/Z/'`); the parent is not reaping children — restart or fix the parent process
- D-state process count > 0 → **OpenClaw.Process.DStateProcessesFound** (CRITICAL)
  - Remediation: D-state processes are blocked on I/O — check disk health (`dmesg | grep -i error`), NFS mounts (`mount -t nfs`), and storage subsystem; these processes cannot be killed normally
- Total process count > 80% of `kernel.pid_max` → **OpenClaw.Process.TotalProcessCountHigh** (WARNING)
  - Remediation: Identify process-spawning storms (`ps -eo user --sort=user | uniq -c | sort -rn | head`); increase `kernel.pid_max` if needed

---

## 11. Systemd Journal & Log Disk Usage

Systemd journal grows unbounded on long-running servers, silently consuming disk space — a common hidden root cause of "disk full" events.

**Judgment rules**:
- Journal disk usage > 2 GB → **OpenClaw.Logs.JournalDiskUsageHigh** (WARNING)
  - Remediation: `journalctl --vacuum-size=500M`; set `SystemMaxUse=500M` in `/etc/systemd/journald.conf` and restart `systemd-journald`
- `/var/log` total size > 5 GB → **OpenClaw.Logs.VarLogOversized** (WARNING)
  - Remediation: Identify large files (`find /var/log -type f -size +100M`); configure logrotate; clean old rotated logs

---

## 12. Filesystem Integrity

Read-only filesystem (from ext4/xfs journal errors) prevents writing session data, logs, and PID files. Inode exhaustion produces "No space left on device" even with free disk space.

**Judgment rules**:
- Any non-virtual mount has `ro` flag, or `/tmp` write test fails → **OpenClaw.Disk.ReadOnlyFilesystem** (CRITICAL)
  - Remediation: Check `dmesg` for filesystem errors; run `fsck` on the affected partition (requires unmount or single-user mode); may indicate disk hardware failure
- Any real filesystem inode usage >= 80% → **OpenClaw.Disk.InodeUsageHigh** (WARNING)
  - Remediation: Find directories with many small files (`find / -xdev -printf '%h\n' | sort | uniq -c | sort -rn | head -10`); clean up session/temp files
- `dmesg` contains EXT4-fs error, XFS error, or read-only remount messages → **OpenClaw.Disk.FilesystemErrorsDetected** (CRITICAL)
  - Remediation: Back up data immediately; run `fsck` at next maintenance window; check disk SMART status (`smartctl -a /dev/sdX`)

---

## 13. Firewall & Outbound Connectivity

Firewall rules blocking inbound or outbound traffic are the #1 cause of "port not reachable" and "API connection refused" in self-hosted deployments.

**Judgment rules**:
- DROP or REJECT rules detected on INPUT or OUTPUT chains → **OpenClaw.Network.FirewallDropRulesDetected** (WARNING)
  - Remediation: Review rules — ensure required ports (gateway port, 443 outbound) are allowed; use `iptables -L -n -v` for detailed hit counts
<!-- - Outbound TCP connect to external port 443 fails → **OpenClaw.Network.OutboundHTTPSBlocked** (ERROR)
  - Remediation: Check OUTPUT chain rules; verify cloud security group allows outbound 443; check if proxy is required (`HTTP_PROXY`/`HTTPS_PROXY`) -->
- `ufw status` shows default deny incoming (informational only) → **OpenClaw.Network.UFWDefaultDeny** (INFO)
  - Remediation: No action required if intentional; ensure gateway port is explicitly allowed (`ufw allow <port>/tcp`)

---

## 14. Transparent Hugepages

THP causes latency spikes and memory fragmentation for Node.js workloads. Multiple database and runtime vendors recommend disabling it on servers.

**Judgment rules**:
- THP `enabled` is set to `[always]` → **OpenClaw.Kernel.THPEnabled** (WARNING)
  - Remediation: `echo never > /sys/kernel/mm/transparent_hugepage/enabled`; persist via systemd unit or `/etc/rc.local`
- THP `defrag` is set to `[always]` → **OpenClaw.Kernel.THPDefragEnabled** (INFO)
  - Remediation: `echo never > /sys/kernel/mm/transparent_hugepage/defrag`; reduces latency spikes from compaction

---

## 15. TCP Connection Overload

Excessive network connections exhaust file descriptors, memory, and conntrack table capacity, degrading system-wide performance.

**Judgment rules**:
- Total TCP connections > 10000 → **OpenClaw.Network.TcpConnectionCountHigh** (WARNING)
  - Remediation: Identify top connection-holding processes; check for connection leaks; consider connection pooling
- CLOSE_WAIT count > 500 → **OpenClaw.Network.CloseWaitAccumulation** (ERROR)
  - Remediation: CLOSE_WAIT indicates the local application is not calling `close()` on sockets — identify the leaking process and restart it; this is an application bug
- ESTABLISHED count > 5000 → **OpenClaw.Network.EstablishedConnectionsHigh** (WARNING)
  - Remediation: Review whether all connections are legitimate; check for connection pool exhaustion or slow clients holding connections open
- Ephemeral ports in use > 80% of available range → **OpenClaw.Network.EphemeralPortExhaustion** (CRITICAL)
  - Remediation: Widen range `sysctl -w net.ipv4.ip_local_port_range='1024 65535'`; enable `tcp_tw_reuse`; check for connection leaks

---

## 16. Headless Browser / Chromium Dependencies

OpenClaw skills that use browser automation (Playwright, Puppeteer) require Chromium shared libraries and headless mode. The diagnostic first tests whether Chrome can actually launch in headless mode. Dependency diagnosis is only performed when Chrome fails or is absent.

**Judgment rules**:
- Chrome headless launch test (`--headless=new --dump-dom about:blank`) succeeds → no issue, skip dependency checks
- Chrome headless launch test fails → proceed with dependency diagnosis below:
  - Any of the 7 critical shared library stems (libnss3, libatk-bridge-2.0, libgbm, libxkbcommon, libdrm, libgtk-3, libasound) is absent from `ldconfig -p` → **OpenClaw.Browser.ChromiumDependenciesMissing** (ERROR)
    - Remediation: On Debian/Ubuntu: `apt install -y libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libdrm2 libgtk-3-0 libasound2`; on RHEL/CentOS: `yum install -y nss atk at-spi2-atk mesa-libgbm libxkbcommon libdrm gtk3 alsa-lib`
  - `ldd` on chromium binary shows one or more "not found" entries → **OpenClaw.Browser.ChromiumBinaryLddFailures** (CRITICAL)
    - Remediation: Install the specific missing libraries identified by `ldd`; run `ldconfig` after installation to update the dynamic linker cache
  - `/proc/sys/kernel/unprivileged_userns_clone` is `0` → **OpenClaw.Browser.UserNamespaceDisabled** (ERROR)
    - Remediation: `sysctl -w kernel.unprivileged_userns_clone=1` and persist in `/etc/sysctl.d/99-userns.conf`; or configure Chromium with `--no-sandbox` (less secure, not recommended for production)

---

## 17. Locale & Encoding Configuration

Missing or misconfigured locale causes garbled text output, incorrect sorting in logs, and subtle bugs like backspace deleting two characters over SSH (when client sends UTF-8 but server expects ASCII). OpenClaw's text processing relies on correct UTF-8 support.

**Judgment rules** (use the persistent `LANG` value read from `/etc/default/locale` or `/etc/locale.conf`, **not** the runtime `$LANG` which may be overridden to `C` by the diagnostic runner):
- Persistent `LANG` is empty, unset, or set to `POSIX`/`C` → **OpenClaw.Locale.LocaleNotConfigured** (ERROR)
  - Remediation: On Debian/Ubuntu: `apt install locales && dpkg-reconfigure locales`, then set `LANG=en_US.UTF-8` in `/etc/default/locale`; on RHEL/CentOS: `localectl set-locale LANG=en_US.UTF-8`
- The persistent `LANG` value does not appear in `locale -a` output (configured but not generated/installed) → **OpenClaw.Locale.LocaleNotGenerated** (WARNING)
  - Remediation: On Debian/Ubuntu: uncomment the locale in `/etc/locale.gen` and run `locale-gen`; on RHEL/CentOS: `localedef -i en_US -f UTF-8 en_US.UTF-8`
- Persistent `LANG` does not contain `UTF-8` or `utf8` → **OpenClaw.Locale.NonUTF8LocaleDetected** (WARNING)
  - Remediation: Change to a UTF-8 variant: `localectl set-locale LANG=en_US.UTF-8`; re-login for the change to take effect
