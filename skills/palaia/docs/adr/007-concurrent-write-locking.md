# ADR-007: Concurrent Write Locking

**Status:** Accepted
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Multi-Agent-Setups bedeuten parallele Writes. Ohne Locking: Race Conditions, korrupte Dateien, verlorene Writes.

## Entscheidung

**File-based Locking mit fcntl (Unix) / msvcrt (Windows).**

- Lock-Granularität: Pro Operation (nicht pro Datei)
- Lock-Datei: `.palaia/.lock`
- Timeout: 5 Sekunden, dann Fehler
- Lock ist advisory (reicht für Agent-Prozesse)

### Flow

```
1. Acquire lock (.palaia/.lock)
2. WAL-Entry schreiben
3. Operation durchführen
4. WAL committen
5. Release lock
```

### Stale Lock Detection

- Lock-Datei enthält PID + Timestamp
- Beim Acquire: Prüfe ob PID noch lebt
- Wenn PID tot → Lock übernehmen (mit Warning)

## Konsequenzen

**Positiv:**
- Einfach, robust, zero dependencies
- Stale-Lock-Recovery automatisch

**Negativ:**
- Advisory Locks — böswillige Prozesse könnten ignorieren (akzeptabel für Agent-Usecase)
- Kein verteiltes Locking (nur lokal — passt zu "Local first")
