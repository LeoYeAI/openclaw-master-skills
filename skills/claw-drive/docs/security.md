# Security

Claw Drive is local-first. Your files live on your machine. Cloud sync is optional.

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| Cloud provider breach | Sensitive dirs excluded from sync via `.sync-config` |
| Local disk theft | Use FileVault (macOS) for full-disk encryption |
| File tampering | SHA-256 hashes in `.hashes` detect content changes |
| Accidental deletion | Google Drive versioning + local Time Machine |

## Sensitive Categories

The `identity/` category holds passport scans, SSN docs, and other high-sensitivity files. By default, the example `.sync-config` excludes it from sync:

```yaml
exclude:
  - identity/
```

These files are fully functional locally — indexed, tagged, searchable — but never leave the machine.

## INDEX.md

The index contains file descriptions but no file contents. Keep descriptions of sensitive files brief:

```
| 2026-01-01 | identity/passport-scan.pdf | Passport scan | identity, passport | manual |
```

Don't include account numbers, SSNs, or other PII in descriptions.

## Credentials

- **rclone config** lives at `~/.config/rclone/rclone.conf` — standard location, not managed by Claw Drive
- No API keys or tokens are stored in the drive directory
- No credentials are ever written to INDEX.md or log files
