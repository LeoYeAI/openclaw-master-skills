---
name: Security Joes AI Analyst
description: SecOps checks for endpoints: EDR, Sysmon, updates, EVTX on heartbeat, least privilege, network visibility, credential protection (Kerberos/NTLM/pass-the-hash), device inventory and known vulnerabilities, weekly assessment, and skill integrity (hash-on-wake, version-aware). Use when implementing or reviewing host posture, heartbeat logic, EDR/Sysmon/EVTX, privilege, network exposure, credential hardening, vuln assessment, weekly SecOps review, or skill compromise checks.
version: 1.0.0
author: Security Joes
authorUrl: https://www.securityjoes.com
homepage: https://www.securityjoes.com
license: MIT
metadata:
  openclaw:
    emoji: "🔒"
    category: "security"
tags:
  - security
  - secops
  - clawhub
  - edr
  - sysmon
  - evtx
---

# Security Joes AI Analyst

You guide and implement SecOps checks for endpoints. Focus: **EDR**, **Sysmon**, **updates**, **EVTX on heartbeat**, **least privilege**, **network visibility**, **credential protection** (Kerberos/NTLM/pass-the-hash), **device inventory and known vulnerabilities**, and **weekly assessment**. Targets Windows; use PowerShell/WMI/registry and EVTX where appropriate.

## Responsibilities

1. **EDR sensor** – Detect at least one EDR (Defender, CrowdStrike, etc.). Report presence/absence and basic health.
2. **Sysmon** – Confirm Sysmon is installed and logging; identify log location (typically EVTX).
3. **System up-to-date** – Check OS/build and patch level; report stale if beyond policy (e.g. 30+ days).
4. **Heartbeat + EVTX** – On heartbeat, query Security/Sysmon/Defender EVTX for recent alerts; attach summary or raise alert.
5. **Least privilege** – Check if the device/user runs with least privilege (not admin, UAC/token elevation as expected).
6. **Network visibility** – What other networks/interfaces the device sees (interfaces, ARP, WiFi, domain trust, net view/session).
7. **Credential protection (network level)** – Kerberos/NTLM hardening and pass-the-hash resistance (SMB signing, LDAP signing, NTLM restrictions, Credential Guard).
8. **Device details and known vulnerabilities** – Inventory OS, patches, installed software; correlate with known CVEs or vuln data for assessment.
9. **Weekly assessment** – Run a full SecOps checklist weekly; produce assessment report and optionally emit as event.
10. **Skill integrity** – On first wake, hash this skill and other known skills; store hashes. On each wake, re-hash and compare; use version changes to treat upgrades vs compromise and alert on unexpected changes.

## When to apply

- User asks for host posture, endpoint health, “is this machine secure?”, or weekly SecOps review.
- Implementing or extending collector/heartbeat logic.
- User mentions EDR, Sysmon, EVTX, least privilege, network exposure, Kerberos, pass-the-hash, credential protection, vulnerabilities, weekly assessment, or skill integrity / compromise check.
- Reviewing or designing what “healthy endpoint” means for the dashboard.

---

## 1. EDR sensor checks

**Microsoft Defender**

- Service: `WinDefend` (Get-Service WinDefend).
- Optional: `Get-MpComputerStatus` (or `MpCmdRun.exe -GetStatus`) for signature version and real-time protection state.
- Registry (if needed): `HKLM\SOFTWARE\Microsoft\Windows Defender` and related product state keys.

**CrowdStrike Falcon**

- Service: `CsAgent` (Get-Service CsAgent -ErrorAction SilentlyContinue).
- Registry: `HKLM\SYSTEM\CurrentControlSet\Services\CsAgent` or Falcon-specific keys under `HKLM\SOFTWARE\CrowdStrike`.

**Others (SentinelOne, Carbon Black, etc.)**

- Prefer service name + optional registry/process check. Document which EDR is “primary” for the environment.

**Output**

- At least: `edr_present: true|false`, `edr_name: "Defender"|"CrowdStrike"|...`, optional `edr_healthy: true|false` (e.g. service running, real-time on).

---

## 2. Sysmon

- **Service**: `Sysmon64` or `Sysmon` (Get-Service Sysmon64, Sysmon -ErrorAction SilentlyContinue).
- **Log**: Usually EVTX – `Microsoft-Windows-Sysmon%4Operational` under `C:\Windows\System32\winevt\Logs\` (path: `...\Microsoft-Windows-Sysmon%4Operational.evtx`).
- **Config**: Optional – check for Sysmon config (e.g. `Sysmon64 -s` or known config path) to confirm logging scope.

**Output**

- `sysmon_installed: true|false`, `sysmon_log_path: "..."` (if available), optional `sysmon_service_running: true|false`.

---

## 3. System up-to-date

- **Quick**: `Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1` for last patch date; or `(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuild` (and optionally UB R) for build.
- **Stricter**: Windows Update status – e.g. WMI `Win32_QuickFixEngineering` or COM `Microsoft.Update.Session` to see last install time / pending reboots.
- **Policy**: Define “stale” (e.g. no patch in 30+ days or build behind current branch) and report `up_to_date: true|false` and optional `last_patch_date` or `build`.

---

## 4. Heartbeat and EVTX alerts

On **heartbeat** (or on a scheduled check that aligns with heartbeats):

1. **Which EVTX**
   - Security: `C:\Windows\System32\winevt\Logs\Security.evtx`
   - Sysmon: `Microsoft-Windows-Sysmon%4Operational.evtx`
   - Microsoft-Windows-Windows Defender/Operational (Defender alerts)
   - Optional: Application, System for context.

2. **What to look for**
   - Security: logon failures (e.g. 4625), sensitive privilege use (4672, 4688), account lockout, etc.
   - Sysmon: creation of executables in temp, suspicious parent/child, etc. (event IDs depend on config).
   - Defender: detection events (e.g. 1116, 1117), threats (1006, 1015).
   - Prefer time-bounded queries (e.g. last N minutes since previous heartbeat or last 24h) to avoid overload.

3. **Implementation options**
   - PowerShell: `Get-WinEvent -FilterHashtable @{ LogName='Security'; StartTime=$since }` (and similar for Sysmon/Defender).
   - Or use a small script/tool that reads EVTX and outputs a compact JSON (event IDs, time, count) for the collector to emit as `details` or as an alert.

4. **Emit**
   - Attach to heartbeat `details` (e.g. `evtx_alert_count`, `evtx_summary[]`) or raise an **alert** event when thresholds are exceeded (e.g. > N failures, or any Defender detection).

---

## 5. Least privilege

Check whether the device/user runs with least privilege (not over-privileged).

- **Current user elevation**: `whoami /groups` to see group membership; token elevation type via `(Get-Process -Id $PID).StartInfo.Verb` or WMI/CIM. For elevation: check if process token has elevation (e.g. `[System.Security.Principal.WindowsIdentity]::GetCurrent().Groups` and look for S-1-16-12288 = High Mandatory Level).
- **Admin membership**: `net localgroup Administrators` (or `Get-LocalGroupMember -Group Administrators`) – report if the current user or common service accounts are in Administrators.
- **UAC**: Registry `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA` = 1 (UAC on). Optional: ConsentPromptBehaviorAdmin, PromptOnSecureDesktop.
- **Privileged sessions**: Optional – check for RDP/admin logons (Security EVTX 4624, logon type 10) and whether interactive admin is expected.

**Output**

- `least_privilege: true|false`, `current_user_elevated: true|false`, `in_local_admins: true|false`, optional `uac_enabled: true|false`.

---

## 6. Network visibility (what networks the device sees)

Assess what networks and neighbors the device can see (exposure and lateral movement surface).

- **Interfaces**: `Get-NetAdapter`, `Get-NetIPAddress` – list adapters, IPs, gateways. Optional: `Get-NetRoute`.
- **ARP table**: `Get-NetNeighbor` or `arp -a` – what other hosts the device has recently talked to (L2/L3 neighbors).
- **WiFi**: `netsh wlan show networks` or `Get-NetAdapter | Where-Object {$_.InterfaceDescription -match 'Wi-Fi'}` plus WLAN profile – SSIDs the device sees or is configured for.
- **Domain / trust**: `systeminfo`, `nltest /domain_trusts` (or Get-ADDomainTrust if RSAT) – domain membership and trust relationships.
- **Net view / session**: `net view` (browsed shares), `net session` (who is connected to this box) – optional; may require admin. Use to see “who can this device see” and “who is using this device.”

**Output**

- `interfaces[]` (name, IP, gateway), `arp_count` or `neighbors_count`, optional `wifi_ssids[]`, `domain_member: true|false`, `domain_name`, `trusts[]`, optional `net_view_count` / `net_session_count`.

---

## 7. Credential protection (network level – Kerberos, NTLM, pass-the-hash)

Check network-level credential hardening to resist Kerberos/NTLM abuse and pass-the-hash.

- **SMB signing**: `Get-SmbClientConfiguration` (RequireSecuritySignature) and `Get-SmbServerConfiguration` (RequireSecuritySignature, EnableSecuritySignature). Prefer **required** on server and client where possible to mitigate NTLM relay.
- **LDAP signing / channel binding**: Domain controllers – LDAP signing (e.g. `HKLM\SYSTEM\CurrentControlSet\Services\NTDS\Parameters\LDAPServerIntegrity`), LDAP channel binding. Client-side: check if environment enforces signed LDAP.
- **NTLM restrictions**: `HKLM\SYSTEM\CurrentControlSet\Control\Lsa`: LmCompatibilityLevel (e.g. 5+ to avoid NTLMv1), RestrictNTLMInDomain / RestrictNTLMOutbound if available. NTLM audit or block policies (RestrictNTLMInDomain = 1, 2, 3).
- **Credential Guard / LSA protection**: `Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard` or registry `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LsaCfgFlags` – Credential Guard (1) and/or LSA run as Protected Process Light to protect hashes in memory.
- **Pass-the-hash**: Mitigations above (Credential Guard, LSA protection, NTLM restrictions) reduce pass-the-hash; report “credential protection” as a summary (e.g. Credential Guard on, SMB signing required, NTLM restricted).

**Output**

- `smb_signing_required_client: true|false`, `smb_signing_required_server: true|false`, optional `ldap_signing`, `lm_compat_level`, `credential_guard: true|false`, `lsa_protected: true|false`, `credential_protection_summary: "strong|partial|weak"`.

---

## 8. Device details and known vulnerabilities

Inventory device and correlate with known vulnerabilities for assessment.

- **OS and build**: `Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"` – ProductName, CurrentBuild, UBR, DisplayVersion. Optional: `Get-ComputerInfo`.
- **Patches**: `Get-HotFix` or WMI `Win32_QuickFixEngineering` – list KBs and InstalledOn. Use for “last patch date” and to cross-reference with CVE data.
- **Installed software**: `Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*`, `HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*` – DisplayName, DisplayVersion, Publisher. Avoid `Get-WmiObject Win32_Product` (slow and triggers reconfigure). Use for vulnerable software inventory.
- **Known vulnerabilities**: Cross-reference OS build and installed product versions with a vulnerability source (e.g. NVD, OSV, vendor advisories, or internal vuln DB). Check for: end-of-life OS, unpatched KBs for known CVEs, outdated browsers/RDP/OpenSSL/etc. Report count or list of “known vulns” (CVE IDs and severity) without dumping full CPE if not needed.

**Output**

- `os_name`, `os_build`, `last_patch_date`, `hotfix_count`, optional `installed_products[]` (name, version), `known_vuln_count`, optional `known_vulns[]` (cve_id, severity, product).

---

## 9. Weekly assessment

Conduct a **weekly** SecOps assessment: run the full checklist and produce a report (and optionally emit an event).

**Checklist (run weekly)**

- [ ] EDR sensor present and healthy (section 1)
- [ ] Sysmon installed and logging (section 2)
- [ ] System up-to-date (section 3)
- [ ] EVTX: recent alerts summary (section 4)
- [ ] Least privilege (section 5)
- [ ] Network visibility: interfaces, neighbors, domain/trust (section 6)
- [ ] Credential protection: SMB/LDAP/NTLM/Credential Guard (section 7)
- [ ] Device inventory and known vulnerabilities (section 8)
- [ ] Skill integrity: hashes match or version-bumped (section 10)

**Workflow**

1. Run all checks (or call scripts that aggregate them).
2. Produce **weekly assessment report** using the Host posture report template (below), extended with network, credential, and vuln sections.
3. Optionally emit a dedicated event: `type: 'weekly_assessment'` (or `config_change` with details.assessment = true), with summary and `details` containing aggregate results (counts, booleans, no PII). Dashboard or rules can surface “last weekly assessment” and failures.

**Schedule**

- Trigger weekly (e.g. cron/Task Scheduler or collector job every 7 days). Store last run time to avoid duplicate runs in the same week.

---

## 10. Skill integrity (hash on wake, version-aware)

On **first wake** (when this skill is first applied or when no stored hashes exist), hash this skill and all other known skills; store the hashes. On **each wake**, re-hash and compare to stored hashes. Use **version** in skill frontmatter to distinguish **upgrades** (intentional version change) from **compromise** (hash changed but version unchanged or missing).

**Scope**

- **What to hash**: Each known skill directory under `.cursor/skills/` (project) or `~/.cursor/skills/` (personal). Per skill: `SKILL.md` (required), and optionally `reference.md`, `examples.md` (if present). Do not hash `scripts/` contents unless you explicitly include them; prefer SKILL.md + optional reference/examples for a stable baseline.
- **Algorithm**: SHA-256 of file contents (UTF-8 or raw bytes consistently). Normalize line endings (e.g. LF) before hashing if skills may be edited on different OSes.

**Storage**

- **Path**: Project scope: `.cursor/skills/.skill-integrity.json`. Personal scope: `~/.cursor/skills/.skill-integrity.json` (or one file that lists both project and personal paths). Do not commit `.skill-integrity.json` to version control if it contains machine-specific or sensitive metadata; add to `.gitignore` or keep local-only.
- **Format** (per skill, keyed by skill name or relative path):

```json
{
  "skills": {
    "security-joes-ai-analyst": {
      "version": "1.0",
      "fileHashes": {
        "SKILL.md": "sha256hex...",
        "reference.md": "sha256hex..."
      },
      "lastChecked": "ISO8601"
    }
  },
  "firstRun": "ISO8601"
}
```

**First wake**

1. Enumerate all skill directories (project `.cursor/skills/*`, optionally personal `~/.cursor/skills/*`).
2. For each skill: read `version` from SKILL.md frontmatter (if present). Compute SHA-256 for SKILL.md and any reference.md/examples.md.
3. Write `.skill-integrity.json` with `skills`, `firstRun`, and `lastChecked` = now.

**Each wake**

1. Load `.skill-integrity.json` (if missing, treat as first wake and run first-wake steps).
2. Enumerate the same skill directories; for each skill, read current `version` from frontmatter and compute current hashes for SKILL.md (and optional reference/examples).
3. **Compare**:
   - **Hash match**: No change. Update `lastChecked` for that skill.
   - **Hash mismatch + version in file changed**: Treat as **upgrade**. Update stored `version` and `fileHashes` for that skill; update `lastChecked`. Do not alert.
   - **Hash mismatch + version unchanged or missing**: Treat as **potential compromise**. Do not overwrite stored hashes with the new ones. Emit an **alert** (e.g. “Skill integrity: [skill name] content changed without version bump – possible tampering”). Optionally record in details: skill name, which file(s) changed (hash diff), stored version vs current version.
4. **New skill** (present on disk but not in stored hashes): On first wake for that skill, add it to storage with current version and hashes. Do not treat as compromise.

**Version in frontmatter**

- Skills should include `version: "x.y"` in YAML frontmatter. When you **intentionally upgrade** a skill, bump the version (e.g. `1.0` → `1.1`) so the next wake treats the hash change as an upgrade, not compromise.
- If a skill has no `version` field, any hash change is treated as potential compromise (no way to distinguish upgrade).

**Output**

- On each wake: `skill_integrity: ok | compromised | upgraded`. If compromised: list skills (and optionally files) with unexpected changes. Do not log full file contents; only hashes and version.

**Integration**

- Run this check when the agent “wakes” (e.g. at start of a session or when this skill is first applied). Optionally include skill integrity in the **weekly assessment** checklist (section 9). Emit MoltSOC **alert** on compromise (type: `alert`, severity: high, summary like “Skill integrity: unexpected change in [skill]”, details with skill name and which hashes changed).

---

## Host posture report template

When producing a host posture, heartbeat summary, or weekly assessment, use a structure like:

```markdown
## Host posture – [host_id]

- **EDR:** [present/absent] – [name], [healthy/unhealthy]
- **Sysmon:** [installed/not installed], log: [path or N/A], service: [running/stopped]
- **Updates:** [up_to_date/stale], last patch: [date], build: [optional]
- **EVTX (since last heartbeat):** [count or summary], alerts: [brief list or "none"]
- **Least privilege:** [yes/no] – elevated: [yes/no], in local admins: [yes/no], UAC: [on/off]
- **Networks:** interfaces: [count], neighbors/ARP: [count], domain: [name or N/A], trusts: [brief]
- **Credential protection:** SMB signing: [required/optional], Credential Guard: [on/off], NTLM: [restricted/audit/off], summary: [strong/partial/weak]
- **Device & vulns:** OS: [name build], products: [count], known vulns: [count] – [brief list or "none"]
- **Weekly assessment:** last run: [date], result: [pass/fail], failures: [brief list or "none"]
- **Skill integrity:** [ok/compromised/upgraded], last check: [date], unexpected: [skill names or "none"]
```

---

## Integration with MoltSOC

- Heartbeat events already exist (`type: 'heartbeat'`). Extend `details` with EDR/Sysmon/update/EVTX, least privilege, network visibility, credential protection, and vuln summary so the dashboard or rules can show “endpoint healthy” or specific failures.
- New **alerts** (e.g. “EDR missing”, “Sysmon stopped”, “EVTX detection”, “over-privileged”, “credential protection weak”, “known vulns”, **“Skill integrity: unexpected change in [skill]”**) follow the same event schema (type: `alert`, severity, summary, details with rule/evidence).
- **Skill integrity**: On compromise (hash change without version bump), emit alert with skill name and which file hashes changed; do not include file contents.
- **Weekly assessment**: Emit `type: 'weekly_assessment'` (or `config_change` with `details.assessment: true`) with aggregate results; dashboard can show “last weekly assessment” and failed checks.
- Prefer **metadata-only** in events (counts, booleans, event IDs, timestamps); do not log raw payloads, PII, or full network/ARP tables in event details.

---

## Privacy and safety

- Do not include raw log content or PII in events; use counts, event IDs, and short summaries.
- EVTX queries should be scoped to security-relevant channels and time windows; avoid dumping full logs into the collector.
- For network visibility and vuln output: report counts and summaries (e.g. neighbor count, vuln count); do not dump full ARP tables, SSID lists, or CPE/vuln payloads unless needed for a specific alert.

---

## About Security Joes

[Security Joes](https://www.securityjoes.com) provides SecOps guidance, endpoint visibility, and security analyst workflows for agents and automation. This skill (Security Joes AI Analyst) is maintained by Security Joes for use with ClawHub and compatible agent platforms.

- **Website:** [https://www.securityjoes.com](https://www.securityjoes.com)
- **About:** [https://www.securityjoes.com/about](https://www.securityjoes.com/about)
