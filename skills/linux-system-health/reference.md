# Linux System Health — Reference

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **FATAL** | System cannot support workloads at all | Must fix before launching any service |
| **CRITICAL** | Major functionality broken or at risk of crashing | Fix immediately |
| **ERROR** | Partial degradation of system services | Fix soon |
| **WARNING** | Potential risk; may cause problems under load | Recommended fix |
| **INFO** | Informational observation | No action needed |

## Issue Name Registry

All issue types defined in this skill:

| # | Issue Name | Sev |
|---|-----------|-----|
| 1 | OpenClaw.System.EnvironmentBaseline | INFO |
| 2 | OpenClaw.Memory.SystemMemoryCritical | CRITICAL |
| 3 | OpenClaw.Memory.SystemMemoryLow | WARNING |
| 4 | OpenClaw.Memory.InsufficientTotalMemory | ERROR |
| 5 | OpenClaw.Memory.OOMKillerEvent | WARNING |
| 6 | OpenClaw.CPU.SystemLoadHigh | WARNING |
| 7 | OpenClaw.CPU.SystemCPUExhausted | CRITICAL |
| 8 | OpenClaw.CPU.HighIOWait | WARNING |
| 9 | OpenClaw.Network.IPv6Mismatch | WARNING |
| 10 | OpenClaw.Disk.FilesystemFull | CRITICAL |
| 11 | OpenClaw.Disk.FilesystemHighUsage | WARNING |
| 12 | OpenClaw.Disk.InotifyWatchesTooLow | ERROR |
| 13 | OpenClaw.Disk.InotifyInstancesTooLow | WARNING |
| 14 | OpenClaw.Limits.NofileTooLow | ERROR |
| 15 | OpenClaw.Limits.NofileExceedsKernelMax | CRITICAL |
| 16 | OpenClaw.Limits.SystemFileDescriptorsHigh | WARNING |
| 17 | OpenClaw.Kernel.NfConntrackMaxTooLow | ERROR |
| 18 | OpenClaw.Kernel.NfConntrackTableFull | CRITICAL |
| 19 | OpenClaw.Kernel.SomaxconnTooLow | WARNING |
| 20 | OpenClaw.Kernel.TcpMaxTwBucketsTooLow | WARNING |
| 21 | OpenClaw.Kernel.TcpTwReuseNotEnabled | WARNING |
| 22 | OpenClaw.Kernel.TimeWaitOverflow | WARNING |
| 23 | OpenClaw.Kernel.TcpListenOverflows | WARNING |
| 24 | OpenClaw.Kernel.StrictOvercommitWithLowSwap | WARNING |
| 25 | OpenClaw.Network.NoDNSNameservers | ERROR |
| 26 | OpenClaw.Network.DNSResolutionFailed | CRITICAL |
| 27 | OpenClaw.Network.DNSNameserverUnreachable | WARNING |
| 28 | OpenClaw.Time.NTPServiceNotRunning | ERROR |
| 29 | OpenClaw.Time.ClockNotSynchronized | CRITICAL |
| 30 | OpenClaw.Time.ClockDriftDetected | WARNING |
| 31 | OpenClaw.Process.ZombieProcessesHigh | WARNING |
| 32 | OpenClaw.Process.DStateProcessesFound | CRITICAL |
| 33 | OpenClaw.Process.TotalProcessCountHigh | WARNING |
| 34 | OpenClaw.Logs.JournalDiskUsageHigh | WARNING |
| 35 | OpenClaw.Logs.VarLogOversized | WARNING |
| 36 | OpenClaw.Disk.ReadOnlyFilesystem | CRITICAL |
| 37 | OpenClaw.Disk.InodeUsageHigh | WARNING |
| 38 | OpenClaw.Disk.FilesystemErrorsDetected | CRITICAL |
| 39 | OpenClaw.Network.FirewallDropRulesDetected | WARNING |
<!-- | 40 | OpenClaw.Network.OutboundHTTPSBlocked | ERROR | -->
| 41 | OpenClaw.Network.UFWDefaultDeny | INFO |
| 42 | OpenClaw.Kernel.THPEnabled | WARNING |
| 43 | OpenClaw.Kernel.THPDefragEnabled | INFO |
| 44 | OpenClaw.Network.TcpConnectionCountHigh | WARNING |
| 45 | OpenClaw.Network.CloseWaitAccumulation | ERROR |
| 46 | OpenClaw.Network.EstablishedConnectionsHigh | WARNING |
| 47 | OpenClaw.Network.EphemeralPortExhaustion | CRITICAL |
| 48 | OpenClaw.Browser.ChromiumDependenciesMissing | ERROR |
| 49 | OpenClaw.Browser.ChromiumBinaryLddFailures | CRITICAL |
| 50 | OpenClaw.Browser.UserNamespaceDisabled | ERROR |
| 51 | OpenClaw.Locale.LocaleNotConfigured | ERROR |
| 52 | OpenClaw.Locale.LocaleNotGenerated | WARNING |
| 53 | OpenClaw.Locale.NonUTF8LocaleDetected | WARNING |
