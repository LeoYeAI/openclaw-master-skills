# Disaster Recovery Runbook

Two-person team (Adam, Chris) controlling physical machines with AI. Update after every incident.

Last reviewed: 2026-02-12

---

## 1. Credential Recovery

### Credential Inventory

| Credential | Env Var | Rotation |
|---|---|---|
| Stripe secret key | `KILN_STRIPE_SECRET_KEY` | 90 days |
| Stripe webhook secret | `KILN_STRIPE_WEBHOOK_SECRET` | 90 days |
| Circle API key | `KILN_CIRCLE_API_KEY` | 90 days |
| Circle entity secret | `KILN_CIRCLE_ENTITY_SECRET` | 90 days |
| Circle wallet ID | `KILN_CIRCLE_WALLET_ID` | Static |
| Printer API keys | `KILN_PRINTER_API_KEY` | 90 days |
| Bambu access code | `KILN_PRINTER_ACCESS_CODE` | 90 days |
| Marketplace keys | `KILN_MMF_API_KEY`, `KILN_CULTS3D_API_KEY`, `KILN_THINGIVERSE_TOKEN` (deprecated), `KILN_CRAFTCLOUD_API_KEY`, `KILN_MESHY_API_KEY` | 90 days |
| Kiln auth token | `KILN_API_AUTH_TOKEN` | 30 days |
| Kiln master key | `KILN_MASTER_KEY` | On compromise |
| GitHub tokens | GitHub Settings | 30 days |
| Domain DNS | kiln3d.com registrar | N/A |

### Storage and Recovery

- **1Password team vault**: All production credentials. Both maintainers have vault access.
- **Never** commit credentials to git.
- Kiln's credential store (`~/.kiln/credentials.db`) encrypts at rest via `KILN_MASTER_KEY` (PBKDF2 + XOR). Master key auto-generates to `~/.kiln/master.key` if unset -- back this up.
- Auth keys support rotation with grace periods: `auth.rotate_key(old, new, grace_period=86400)`.

**To recover**: 1Password vault -> export to `.env` -> for Circle wallets, re-run `CircleProvider.setup_entity_secret()` and `setup_wallet()` if entity secret is lost (creates new infrastructure; old wallets unrecoverable).

---

## 2. Infrastructure Recovery

### SQLite (default)

- **Location**: `~/.kiln/kiln.db` (override: `KILN_DB_PATH`)
- **Backup**: `0 3 * * * cp ~/.kiln/kiln.db ~/.kiln/backups/kiln-$(date +\%Y\%m\%d).db`
- **Restore**: Stop Kiln, replace DB file, restart. Also back up `~/.kiln/credentials.db`.

### PostgreSQL (multi-node)

- Enabled via `KILN_POSTGRES_DSN`. Auto-detected by `KilnDB`.
- **Backup**: `pg_dump "$KILN_POSTGRES_DSN" > kiln-$(date +%Y%m%d).sql`
- **Restore**: `psql "$KILN_POSTGRES_DSN" < backup.sql`

### Configuration

- `~/.kiln/config.yaml` -- back up with the DB.
- If config lost: `kiln scan` rediscovers printers via mDNS, then re-register.
- If `~/.kiln/master.key` lost: all credential store entries are unrecoverable. Regenerate from 1Password.

### Audit Log Integrity

After any restore, verify HMAC signatures:
```
verify_audit_integrity()  # MCP tool
# Or: get_db().verify_audit_log() -> {"total": N, "valid": N, "invalid": 0}
```
If `invalid > 0`: chain is broken (tamper or partial restore). Document invalid entries, cross-reference backups, flag in incident report.

---

## 3. Printer Fleet Recovery

### Single Printer Offline

1. Ping printer IP. Check network.
2. OctoPrint: `sudo systemctl restart octoprint`
3. Klipper: `sudo systemctl restart klipper moonraker`
4. Bambu: Power cycle. Verify LAN mode + access code matches `KILN_PRINTER_ACCESS_CODE`.
5. Serial: Check USB, `ls /dev/tty*`, verify `KILN_PRINTER_SERIAL_PORT`.
6. Confirm: `kiln status --printer <name>`

### Firmware Corruption

- **Marlin**: Re-flash via USB + PlatformIO. See [marlinfw.org](https://marlinfw.org).
- **Klipper**: `cd ~/klipper && make menuconfig && make flash`
- **Bambu**: Push firmware via Bambu Studio.

### Safety Profile Mismatch

After firmware changes, verify `get_profile("model")` limits match new firmware. If changed, update `kiln/src/kiln/data/safety_profiles.json` and run tests.

### Full Fleet Cold Start

Order matters:
1. Power on all printers (wait 30-60s for firmware boot)
2. Verify firmware via web UI / display
3. Start Kiln: `python3 -m kiln`
4. Discover: `kiln scan`, register missing printers
5. Preflight: `kiln preflight --printer <name>` per printer
6. Verify: `kiln fleet-status` -- all should show IDLE

---

## 4. Code Recovery

GitHub: `https://github.com/codeofaxel/Kiln.git` (MIT License).

```bash
git clone https://github.com/codeofaxel/Kiln.git && cd Kiln
pip3 install -e "./kiln[dev,bambu,serial,postgres]"
pip3 install -e "./octoprint-cli[dev]"
python3 -m pytest kiln/tests/ -x -q && python3 -m pytest octoprint-cli/tests/ -x -q
```

Institutional knowledge lives in: `CLAUDE.md` (architecture, patterns), `.dev/LESSONS_LEARNED.md` (debugging), `.dev/COMPLETED_TASKS.md` (feature history), and 3,900+ tests as executable spec.

---

## 5. Incident Response

| Level | What | Response |
|---|---|---|
| **S1** | Physical damage risk (fire, thermal runaway) | Immediate |
| **S2** | Print failure cascade, safety bypass | < 1 hour |
| **S3** | API/service down | < 4 hours |
| **S4** | Degraded (single printer offline, slow) | < 24 hours |

### S1: Physical Danger

1. `emergency_stop()` -- sends M112, M104 S0, M140 S0, M107 to all printers. If server is down, **pull power cables**.
2. **Disconnect power** physically. Software stop is not sufficient alone.
3. Document: timestamp, printer, what happened, photos.
4. **Call** the other maintainer immediately.
5. Do not reconnect until root cause is identified.

### S2-S4

1. Identify scope (which printers/services/agents).
2. Isolate (pause printers, disable tools).
3. Fix or roll back.
4. Preflight before resuming.
5. Post-mortem for S2+.

### Communication

- S1-S2: Direct call/text between maintainers.
- S3-S4: Async message.
- Tracking: GitHub Issues with `incident` label.

### Post-Mortem Format

Title, date, severity, duration. Then: What happened (2-3 sentences), Timeline (timestamped events), Root cause, Fixes applied, Action items with owners.

---

## 6. Bus Factor Mitigation

### Access Parity (audit quarterly)

Both Adam and Chris must independently have: GitHub admin, 1Password vault, domain registrar (kiln3d.com), Stripe dashboard, Circle dashboard, SSH to all printer hosts.

If either person cannot restore the full system solo, fix the gap immediately.

### Knowledge Redundancy

| Asset | Mechanism |
|---|---|
| Architecture | `CLAUDE.md` -- 700+ lines of patterns and decisions |
| Debugging | `.dev/LESSONS_LEARNED.md` -- auto-updated |
| Behavior spec | 3,900+ pytest tests |
| Ops history | HMAC-signed audit logs |
| Feature log | `.dev/COMPLETED_TASKS.md` |
| Code access | MIT License, public GitHub repo |

If a maintainer is unavailable: the other has full access, `CLAUDE.md` enables onboarding, tests validate correctness, and the MIT license guarantees project continuity.
