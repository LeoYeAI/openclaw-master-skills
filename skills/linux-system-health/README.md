# linux-system-health

Diagnose OS-level issues on Linux servers — memory, CPU, disk, network, kernel tuning, resource limits, DNS, time sync, filesystem integrity, browser dependencies, and locale configuration.

This skill helps AI agents systematically diagnose system-level root causes of performance problems, resource exhaustion, and misconfigurations. It is **framework-agnostic** and contains zero application-specific logic.

> **Platform**: Linux only. This skill is not applicable on Windows or macOS.

## What It Checks

1. **System Environment Baseline** — OS, kernel, architecture, uptime, load
2. **Memory & OOM** — Available memory, total RAM, OOM killer events
3. **CPU & Performance** — Load average, CPU utilization, IO wait
4. **Network Infrastructure** — DNS resolution, IPv6 configuration, firewall rules
5. **Disk & inotify** — Filesystem usage, inotify watch/instance limits
6. **File Descriptor & Process Limits** — ulimit, kernel file-nr, per-process nofile
7. **Kernel & Sysctl Tuning** — nf_conntrack, somaxconn, TCP tuning, overcommit
8. **DNS Resolution Health** — Nameserver configuration, DNS reachability, resolution tests
9. **Time Synchronization** — NTP service status, clock drift, hardware clock
10. **Zombie & D-State Processes** — Zombie process leaks, uninterruptible sleep, process count
11. **Systemd Journal & Log Disk Usage** — Journal size, /var/log growth, large log files
12. **Filesystem Integrity** — Read-only mounts, filesystem errors, inode exhaustion
13. **Firewall & Outbound Connectivity** — iptables/nftables DROP rules, outbound HTTPS test, ufw
14. **Transparent Hugepages** — THP enabled/defrag status, latency impact
15. **TCP Connection Overload** — Connection state distribution, CLOSE_WAIT leaks, ephemeral ports
16. **Headless Browser / Chromium Dependencies** — Shared library availability, ldd validation, user namespace sandbox
17. **Locale & Encoding Configuration** — LANG/LC_ALL settings, locale generation, UTF-8 support

## Prerequisites

- Linux server (Ubuntu, Debian, CentOS, RHEL, Amazon Linux, etc.)
- Root or sudo access
- Standard coreutils and system tools: `free`, `df`, `ps`, `ss`, `sysctl`, `iptables`, `dmesg`, `journalctl`, `timedatectl`, `ldconfig`, `ldd`, `locale`, `mount`, `nft`, `ufw`

## Usage

### Install from ClawHub

```bash
clawhub install linux-system-health
```

### Manual

Copy the `SKILL.md` file into your AI agent's skill directory. For OpenClaw:

```bash
mkdir -p ~/.openclaw/skills/linux-system-health
cp SKILL.md ~/.openclaw/skills/linux-system-health/
```

### With other AI agent frameworks

| Framework | Method |
|-----------|--------|
| OpenClaw | `clawhub install linux-system-health` |
| Qoder | Copy to `.qoder/skills/linux-system-health/SKILL.md` |
| Claude Code | See below |
| Cursor | Reference in `.cursorrules` |
| Codex | Reference in `AGENTS.md` |

### Claude Code

**Method 1: One-command install (recommended)**

```bash
claude install-skill https://raw.githubusercontent.com/ecsgo-helper/openclaw-system-health/main/linux-system-health/SKILL.md
```

This installs the skill to `.claude/skills/` and makes it available as a slash command in Claude Code sessions.

**Method 2: Manual install**

```bash
mkdir -p .claude/skills
cp SKILL.md .claude/skills/linux-system-health.md
```

**Method 3: Reference in CLAUDE.md** (always active)

Add to your project's `CLAUDE.md`:

```markdown
## Linux Diagnostics

When diagnosing Linux server issues (performance, memory, disk, network, processes),
follow the diagnostic procedures in `.claude/skills/linux-system-health.md`.
```

## Issue Domains (53 issues)

| Domain | Count | Examples |
|--------|-------|----------|
| `System` | 1 | EnvironmentBaseline |
| `Memory` | 4 | SystemMemoryCritical, SystemMemoryLow, InsufficientTotalMemory, OOMKillerEvent |
| `CPU` | 3 | SystemLoadHigh, SystemCPUExhausted, HighIOWait |
| `Network` | 10 | IPv6Mismatch, NoDNSNameservers, DNSResolutionFailed, DNSNameserverUnreachable, FirewallDropRulesDetected, UFWDefaultDeny, TcpConnectionCountHigh, CloseWaitAccumulation, EstablishedConnectionsHigh, EphemeralPortExhaustion |
| `Disk` | 7 | FilesystemFull, FilesystemHighUsage, InotifyWatchesTooLow, InotifyInstancesTooLow, ReadOnlyFilesystem, InodeUsageHigh, FilesystemErrorsDetected |
| `Limits` | 3 | NofileTooLow, NofileExceedsKernelMax, SystemFileDescriptorsHigh |
| `Kernel` | 10 | NfConntrackMaxTooLow, NfConntrackTableFull, SomaxconnTooLow, TcpMaxTwBucketsTooLow, TcpTwReuseNotEnabled, TimeWaitOverflow, TcpListenOverflows, StrictOvercommitWithLowSwap, THPEnabled, THPDefragEnabled |
| `Time` | 3 | NTPServiceNotRunning, ClockNotSynchronized, ClockDriftDetected |
| `Process` | 3 | ZombieProcessesHigh, DStateProcessesFound, TotalProcessCountHigh |
| `Logs` | 2 | JournalDiskUsageHigh, VarLogOversized |
| `Browser` | 3 | ChromiumDependenciesMissing, ChromiumBinaryLddFailures, UserNamespaceDisabled |
| `Locale` | 3 | LocaleNotConfigured, LocaleNotGenerated, NonUTF8LocaleDetected |

## Severity Levels

| Level | Meaning |
|-------|---------|
| **FATAL** | System cannot support workloads at all |
| **CRITICAL** | Major functionality broken or at risk |
| **ERROR** | Partial service degradation |
| **WARNING** | Potential risk under load |
| **INFO** | Informational, no action needed |

## Related Skills

- [openclaw-diagnostic](../openclaw-diagnostic/) — OpenClaw-specific diagnostics (installation, gateway, API connectivity, service management, application logs)

## License

[MIT-0](./LICENSE.md)
