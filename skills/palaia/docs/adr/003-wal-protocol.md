# ADR-003: WAL-Protokoll Design

**Status:** Draft
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Agents können jederzeit unterbrochen werden (Timeout, Crash, Netzwerkfehler).
Ohne Absicherung gehen Memory-Writes verloren oder erzeugen korrupte Dateien.

## Entscheidung (Draft)

**Write-Ahead Log (WAL) vor jeder Memory-Operation.**

```
Write-Flow:
1. Schreibe Intent in .palaia/wal/<timestamp>-<uuid>.json
2. Führe eigentliche Operation durch
3. Schreibe Commit-Marker in WAL-Entry
4. WAL-Entry archivieren (oder löschen nach konfigurierbarer Retention)

Recovery-Flow (bei Start):
1. Prüfe .palaia/wal/ auf uncommitted Entries
2. Replay oder Rollback je nach Entry-Typ
3. Cleanup
```

### WAL-Entry Format (Draft)

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "operation": "write|delete|update",
  "target": "relative/path/to/memory.md",
  "payload_hash": "sha256",
  "status": "pending|committed|rolled_back"
}
```

## Offene Fragen

- WAL-Retention: Wie lange aufbewahren? (Default: 7 Tage)
- Concurrent Writes: File-Lock oder optimistic locking?
- WAL-Komprimierung bei vielen Einträgen?

## Konsequenzen

**Positiv:**
- Crash-Sicherheit ohne externe DB
- Auditierbar (WAL ist lesbar)
- Recovery ist deterministisch

**Negativ:**
- Leichter Write-Overhead (~1ms pro Operation)
- WAL-Verzeichnis braucht Cleanup-Logik
