---
name: system-integrity-and-backup
description: Encrypted backups, integrity verification, and data retention enforcement for Greek legal requirements (5-20 year retention). AES-256.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "backup", "integrity", "disaster-recovery"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "openssl", "tar"], "env": ["OPENCLAW_DATA_DIR", "OPENCLAW_ENCRYPTION_KEY"]}, "notes": "Uses openssl for AES-256 backup encryption and SHA-256 integrity hashing. All operations are local to OPENCLAW_DATA_DIR. OPENCLAW_ENCRYPTION_KEY must be provided via environment variable — never stored on disk."}}
---

# System Integrity and Backup

This skill protects everything the OpenClaw Greek Accounting system holds. It runs silently in the background — verifying that data has not been corrupted or unexpectedly deleted, managing encrypted backups to local storage, enforcing the retention obligations that Greek law places on accounting firms, and handling the schema migrations that keep the system consistent as skills evolve.

No accounting firm could professionally deploy a system handling client financial records without this layer. Greek accounting firms are legally obligated to retain certain records for up to 20 years. A backup that has never been tested is not a backup. An integrity system that only runs when something breaks is too late.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
export OPENCLAW_ENCRYPTION_KEY="your-256-bit-key"  # Never store on disk
which jq openssl tar || sudo apt install jq openssl tar
mkdir -p $OPENCLAW_DATA_DIR/backups
```

Uses openssl for AES-256 backup encryption and SHA-256 integrity verification. The encryption key must be provided via environment variable — it is never written to disk.


## Core Philosophy

- **Silent Until Needed, Auditable Always**: Integrity checks run on schedule without interrupting accounting operations. Every result — pass or fail — is permanently logged so the firm can demonstrate to a regulator or auditor that the system has been actively monitored
- **Verified Backups, Not Just Created Ones**: A backup is only as good as its last successful restore test. This skill tests backup archives on a regular schedule and flags any that cannot be verified
- **Greek Legal Retention by Default**: The retention schedule is pre-configured for Greek accounting law. Records are not deleted at retention expiry — they are flagged for human review and then archived or deleted only with explicit approval
- **Migrations Are Versioned and Reversible**: When a skill update changes a data structure, the migration is applied as a numbered, logged operation. Every migration can be inspected; failed migrations are rolled back automatically
- **No Silent Failures**: If a backup fails, if an integrity check finds corruption, if a retention flag is triggered — the firm is notified through the dashboard. Nothing fails quietly

---

## OpenClaw Commands

### Integrity Checks
```bash
# Full system integrity check
openclaw integrity check --all
openclaw integrity check --all --verbose

# Check specific data trees
openclaw integrity check --dir /data/clients/
openclaw integrity check --dir /data/compliance/
openclaw integrity check --afm EL123456789    # Single client full check

# Hash registry operations
openclaw integrity hash-update --dir /data/clients/    # Rebuild hash registry after known change
openclaw integrity hash-verify --dir /data/clients/    # Verify current files against registry
openclaw integrity hash-diff --since yesterday          # Show files changed since timestamp

# Audit log
openclaw integrity audit-log --last 30-days
openclaw integrity audit-log --failures-only
openclaw integrity audit-log --afm EL123456789 --last 90-days

# Generate integrity report (suitable for audit/regulatory inspection)
openclaw integrity report --period 2026-01 --format pdf
openclaw integrity report --year 2025 --full --format pdf
openclaw integrity report --format json --output /data/reports/system/
```

### Backup Management
```bash
# Manual backup triggers
openclaw backup run --type full
openclaw backup run --type incremental
openclaw backup run --type clients --afm EL123456789   # Single client snapshot
openclaw backup run --type compliance --period 2026-01  # Post-filing snapshot

# Backup schedule configuration
openclaw backup schedule --full weekly --day sunday --time 02:00
openclaw backup schedule --incremental daily --time 03:00
openclaw backup schedule --event-driven --on submission-complete
openclaw backup schedule --show

# Backup verification (restore test without overwriting live data)
openclaw backup verify --latest
openclaw backup verify --backup-id BACKUP-20260218-001
openclaw backup verify --all --last 30-days
openclaw backup verify --restore-test --target /tmp/verify-restore/  # Full restore to temp

# Backup listing and status
openclaw backup list --all
openclaw backup list --type full --last 10
openclaw backup status --show-verified --show-unverified --show-failed
openclaw backup manifest --update    # Rebuild manifest from actual backup files

# Off-site export (manual — operator copies encrypted files to external media)
openclaw backup export --backup-id BACKUP-20260218-001 --output /mnt/external/
openclaw backup export --latest-full --output /mnt/external/
```

### Retention Management
```bash
# Check retention status
openclaw retention check --all-clients
openclaw retention check --afm EL123456789 --verbose
openclaw retention flagged --show-all    # Records past retention date awaiting action

# Retention schedule management
openclaw retention schedule-view         # Show current retention rules
openclaw retention schedule-update --record-type financial-statements --years 10

# Archiving and deletion (always requires explicit approval)
openclaw retention archive --afm EL123456789 --record-type invoices --older-than 7-years --approved-by "yannis.k"
openclaw retention delete --afm EL123456789 --record-type payroll-detail --older-than 5-years --approved-by "yannis.k" --confirm
openclaw retention report --period 2026-01 --records-archived --records-deleted
```

### Schema Migration
```bash
# Migration status
openclaw migrate status           # Current schema version and pending migrations
openclaw migrate list --pending   # Migrations not yet applied
openclaw migrate list --applied   # Applied migrations with dates

# Apply migrations
openclaw migrate run --next       # Apply next pending migration
openclaw migrate run --all        # Apply all pending migrations
openclaw migrate run --id v2.1_20260301_add-financial-statements-index

# Rollback
openclaw migrate rollback --last  # Rollback the most recent migration
openclaw migrate rollback --to v2.0

# Migration inspection
openclaw migrate diff --migration v2.1_20260301_add-financial-statements-index
openclaw migrate dry-run --next   # Show what would change without applying
```

### Health Dashboard Feed
```bash
# Status outputs consumed by the dashboard
openclaw integrity health-status   # Single-call summary: backup age, last check, any failures
openclaw backup age                 # Time since last successful full backup
openclaw retention due              # Records due for retention action this month
```

---

## Integrity Check Design

### What Is Checked

```yaml
Integrity_Check_Scope:

  file_existence:
    description: "Every file referenced in index files and registries actually exists on disk"
    checks:
      - "/data/clients/_index.json entries → /data/clients/{AFM}/ directories exist"
      - "/data/clients/{AFM}/documents/registry.json entries → files exist"
      - "/data/compliance/submissions/ receipts → referenced filing XML files exist"
      - "/data/clients/{AFM}/financial-statements/index.json → statement files exist"

  hash_verification:
    description: "SHA256 hash of every canonical data file matches the registered hash"
    hash_registry: "/data/system/integrity/hash-registry.json"
    when_hash_registered: "On every write to a canonical file (all skills call openclaw integrity hash-update on write)"
    on_mismatch: "Flag as CORRUPTION. Alert immediately. Do not proceed with accounting operations on affected client until resolved."
    on_new_file_not_in_registry: "Flag as UNREGISTERED_WRITE. Log for investigation."

  structural_validation:
    description: "Key JSON files conform to expected schema"
    files_validated:
      - "/data/clients/{AFM}/profile.json"
      - "/data/clients/{AFM}/compliance/filings.json"
      - "/data/clients/_index.json"
      - "/data/system/skill-versions.json"
    on_schema_mismatch: "Flag as SCHEMA_DRIFT. Usually indicates a migration is pending."

  referential_integrity:
    description: "Cross-references between files are consistent"
    checks:
      - "Every AFM in _index.json has a corresponding directory"
      - "Every filing in filings.json has a corresponding submission receipt"
      - "Every financial statement in the index actually exists as a file"
      - "No orphaned files in /data/compliance/ without a corresponding client"

  storage_health:
    description: "Disk usage and growth rate"
    checks:
      - "Total /data/ usage against configured storage limit"
      - "Growth rate per directory — flag if growing faster than baseline"
      - "Memory directory size against configured maximum"
```

### Check Scheduling

```yaml
Integrity_Schedule:
  full_check:
    frequency: "Weekly — Sunday 04:00 Athens time (after backup)"
    scope: "All directories, all files, all cross-references"
    duration_estimate: "5-15 minutes depending on data volume"

  quick_check:
    frequency: "Daily — 05:00 Athens time"
    scope: "Hash verification of client and compliance directories only"
    duration_estimate: "1-3 minutes"

  event_driven:
    triggers:
      - "After any government submission (verify submission receipt written correctly)"
      - "After any schema migration (verify migration applied cleanly)"
      - "After any backup restore test (verify restored data matches original)"
    scope: "Targeted — only the affected files and directories"

  never_during:
    - "Business hours (08:00-18:00 Athens time) — scheduled checks only"
    - "Active monthly processing run — wait for pipeline completion"
```

---

## Backup Architecture

### Backup Types and Schedule

```yaml
Backup_Types:

  full_backup:
    frequency: "Weekly — Sunday 02:00 Athens time"
    scope: "Complete /data/ tree excluding /data/processing/ (ephemeral)"
    encryption: "AES-256 with key stored in /data/auth/backup-key.enc"
    filename: "full_{YYYYMMDD}_{HHMMSS}.tar.enc"
    retention: "Keep last 8 full backups (8 weeks rolling)"
    verify_schedule: "Tested within 24 hours of creation"

  incremental_backup:
    frequency: "Daily — Monday through Saturday, 03:00 Athens time"
    scope: "Files modified since last backup (using hash registry delta)"
    filename: "incremental_{YYYYMMDD}_{HHMMSS}.tar.enc"
    retention: "Keep last 30 incremental backups"
    verify_schedule: "Spot-tested weekly (every 7th incremental)"

  event_driven_snapshot:
    triggers:
      - "After any government submission (VAT, EFKA, E1, corporate tax)"
      - "After any client onboarding (new client record created)"
      - "After any schema migration"
    scope: "Specific affected directories only"
    filename: "snapshot_{event-type}_{AFM}_{YYYYMMDD}_{HHMMSS}.tar.enc"
    retention: "Keep indefinitely — these are milestone records"
    verify_schedule: "Verified immediately after creation"
```

### Backup Verification

```yaml
Backup_Verification:
  method: "Restore to isolated temporary directory, run integrity check against restored data"
  what_is_verified:
    - "Archive can be decrypted with current key"
    - "Archive is not corrupted (tar integrity check)"
    - "File count matches manifest"
    - "Sample file hashes match registered hashes"
    - "No files present in manifest that are missing from archive"

  result_states:
    VERIFIED: "Archive passed all checks — recorded in manifest"
    PARTIAL: "Archive intact but some files could not be verified against hash registry"
    FAILED: "Archive corrupted, undecryptable, or missing files — immediate alert"

  on_failed_backup:
    action_1: "Alert dashboard immediately"
    action_2: "Trigger new backup attempt within 1 hour"
    action_3: "If second attempt also fails: alert senior accountant via dashboard critical alert"
    action_4: "Log failure to /data/system/integrity/audit-log.json"
    never: "Never silently mark a failed backup as OK"
```

### Backup File Structure

```yaml
Backup_Manifest_Entry_Fields:
  - backup_id           # BACKUP-{YYYYMMDD}-{3digits}
  - type                # full / incremental / snapshot
  - created_at_utc      # ISO timestamp
  - filename            # Exact filename in /data/backups/
  - size_bytes
  - file_count
  - scope               # What directories were included
  - trigger             # scheduled / event:submission / event:onboarding / manual
  - verified            # true / false / pending
  - verified_at_utc     # ISO timestamp of last verification
  - verify_result       # VERIFIED / PARTIAL / FAILED / pending
  - event_reference     # If event-driven: filing ID, AFM, etc.
```

---

## Retention Schedule

Greek accounting law sets minimum retention periods. This skill enforces them with a conservative approach — when in doubt, retain longer and require human approval before deletion.

```yaml
Retention_Schedule:

  financial_records:
    types:
      - "VAT returns and supporting documents"
      - "Financial statements (P&L, Balance Sheet)"
      - "Invoice records (sales and purchases)"
      - "Bank reconciliation reports"
    minimum_retention_years: 5
    recommended_retention_years: 7
    legal_basis: "Greek VAT Code Article 36, Law 4308/2014"

  payroll_records:
    types:
      - "Employee payroll records"
      - "EFKA contribution calculations"
      - "Employment contracts"
      - "Payslips"
    minimum_retention_years: 5
    note: "EFKA may audit up to 5 years back"

  government_submission_receipts:
    types:
      - "AADE submission references"
      - "myDATA transmission records"
      - "EFKA declaration receipts"
    system_default: "Retain indefinitely unless explicitly deleted"
    note: "Storage cost is negligible; risk of needing them is real"

  client_contracts_and_identity:
    types:
      - "Client engagement letters"
      - "AFM verification records"
      - "GDPR consent records"
    minimum_retention_years: 5
    post_relationship_retention: 5
    note: "5 years after end of client relationship, not from document creation"

  correspondence:
    types:
      - "Outgoing letters (Skill 16 sent records)"
      - "Inbound email classifications"
    minimum_retention_years: 5

  audit_and_integrity_logs:
    types:
      - "/data/system/integrity/audit-log.json"
      - "/data/auth/logs/"
    retention: "Permanent — never deleted"
    reason: "Regulatory and professional liability"

  processing_and_temp_files:
    types:
      - "/data/processing/ (all subdirectories)"
      - "/data/memory/episodes/ and /data/memory/failures/"
    retention_days: 90
    action: "Auto-purge after 90 days — these are operational, not legal records"
    exception: "Memory patterns/ and corrections/ — retained indefinitely as system learning assets"
```

### Retention Action Workflow

```yaml
Retention_Action:
  step_1: "Flag records past retention date in /data/system/integrity/retention-schedule.json"
  step_2: "Alert dashboard — show which records are due for action"
  step_3: "Human reviews: openclaw retention flagged --show-all"
  step_4: "Human chooses: archive (cold storage) or delete"
  step_5: "Archive: openclaw retention archive --approved-by {username}"
           "Delete: openclaw retention delete --approved-by {username} --confirm"
  step_6: "Action logged permanently in integrity audit-log"
  never: "Auto-delete any client financial record without explicit human approval"
```

---

## Schema Migration

```yaml
Migration_System:

  version_format: "v{MAJOR}.{MINOR}_{YYYYMMDD}_{description}"
  examples:
    - "v1.0_20260101_initial-schema"
    - "v2.0_20260218_add-financial-statements"
    - "v2.1_20260301_add-correspondence-tree"

  migration_file_contents:
    - description: "Plain English description of what changes"
    - affects: "List of directories and file patterns affected"
    - forward_steps: "Ordered list of operations to apply the migration"
    - rollback_steps: "Ordered list of operations to reverse the migration"
    - validation: "Checks to run after applying — confirms migration succeeded"
    - estimated_duration: "Expected time to apply"

  safety_rules:
    - "Never modify production data without taking a snapshot backup first"
    - "Run dry-run before applying any migration to production"
    - "Apply one migration at a time — never batch-apply untested migrations"
    - "All migrations tested in an isolated restore before production application"
    - "Failed migration triggers automatic rollback — never leaves data in partial state"

  current_schema_version:
    location: "/data/system/skill-versions.json"
    field: "schema_version"
```

---

## File System

```yaml
Skill_17_File_Paths:
  owns:
    - "/data/backups/"
    - "/data/system/integrity/"
    - "/data/system/backups/backup-manifest.json"
    - "/data/reports/system/"

  writes_on_event:
    - "/data/system/integrity/audit-log.json"
    - "/data/system/integrity/hash-registry.json"
    - "/data/system/integrity/last-check-results.json"
    - "/data/system/integrity/retention-schedule.json"

  reports:
    location: "/data/reports/system/"
    files:
      - "{YYYY-MM}_integrity_report.pdf"
      - "{YYYY-MM}_backup_status_report.pdf"
      - "{YYYY-MM}_retention_action_report.pdf"
```

---

## Dashboard Integration

```yaml
Dashboard_Feeds:
  health_status_card:
    data_source: "/data/system/integrity/last-check-results.json"
    fields_shown:
      - "Last full check: [date] — [PASS / ISSUES FOUND]"
      - "Last backup: [date] — [VERIFIED / UNVERIFIED / FAILED]"
      - "Storage used: X GB of Y GB"
      - "Retention flags: N records awaiting action"

  alerts:
    integrity_failure: "CRITICAL — Data integrity issue detected in {directory}. Accounting operations suspended for affected clients."
    backup_failed: "CRITICAL — Backup failed. Last verified backup: {N} days ago."
    backup_unverified: "WARNING — Latest backup not yet verified."
    retention_due: "INFO — {N} records are past retention date and require action."
    storage_at_80_percent: "WARNING — Storage at {X}% capacity. Review and archive."
```

---

## Memory Integration (Phase 4 — Skill 19 hooks)

```yaml
Memory_Integration:
  log_episodes: true
  episode_types:
    - backup_completed_and_verified
    - integrity_check_passed
    - migration_applied_successfully
    - retention_action_completed

  log_failures: true
  failure_types:
    - backup_failed
    - backup_verification_failed
    - integrity_check_found_corruption
    - migration_rollback_triggered
    - hash_mismatch_detected

  rate_limit_group: "system_operations"
  note: "System integrity failures must always be logged regardless of rate limits — no token budget applies here"
```

---

## Error Handling

```yaml
Severity_Levels:

  CRITICAL:
    conditions:
      - Hash mismatch on any file in /data/clients/ or /data/compliance/
      - Backup archive corrupted or undecryptable
      - Schema migration failed and rollback also failed
    response:
      - Suspend accounting operations on affected data
      - Alert dashboard immediately with red banner
      - Log to audit-log with CRITICAL marker

  HIGH:
    conditions:
      - Backup verification failed (archive intact but hash mismatch on restore)
      - Retention-past-date records found
      - Storage above 90% capacity
    response:
      - Dashboard yellow alert
      - Log to audit-log
      - Retry backup verification once before escalating to CRITICAL

  INFO:
    conditions:
      - Unregistered write detected (file not in hash registry)
      - Schema drift detected (file does not match expected structure)
      - Storage above 80% capacity
    response:
      - Dashboard notification
      - Log to audit-log
      - Flag for human review at next session
```

---

## Success Metrics

A successful deployment of this skill should achieve:
- ✅ Every backup verified within 24 hours of creation — zero unverified backups older than 48 hours
- ✅ Full integrity check passes weekly with zero unexplained hash mismatches
- ✅ Every schema migration applied cleanly with no data loss and full rollback capability
- ✅ Retention schedule enforced — no record deleted without explicit human approval
- ✅ Integrity audit log is continuous and permanent — no gaps
- ✅ Dashboard always shows current backup age and last check result — never stale
- ✅ The firm can produce an integrity report for a regulator or auditor at any time covering any past period

Remember: This skill exists so the firm can say — to a client, a regulator, or an auditor — "our systems are maintained, monitored, backed up, and compliant." That statement must be true and provable. Every feature in this skill exists to make it provable.
