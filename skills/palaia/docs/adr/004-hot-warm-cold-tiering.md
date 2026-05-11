# ADR-004: HOT/WARM/COLD Tiering Struktur

**Status:** Draft
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Memory-Dateien wachsen unbegrenzt. Ältere, selten genutzte Inhalte blähen den Context auf.
Automatisches Tiering hält den aktiven Context klein ohne Daten zu verlieren.

## Entscheidung (Draft)

**Drei-Tier-Dateistruktur, automatisch verwaltet von Palaia.**

```
.palaia/
  hot/       # aktiv genutzt (< 7 Tage oder hoher Decay-Score)
  warm/      # gelegentlich genutzt (7-30 Tage)
  cold/      # selten genutzt (> 30 Tage)
  wal/       # Write-Ahead Log
  index/     # Suchindex (BM25 + optional Embeddings)
```

### Decay-Scoring

Jede Memory-Einheit hat einen Score:
```
score = base_relevance * recency_factor * access_frequency
recency_factor = exp(-lambda * days_since_last_access)
```

Palaia verschiebt automatisch:
- HOT → WARM: Score < 0.5 UND > 7 Tage nicht zugegriffen
- WARM → COLD: Score < 0.1 UND > 30 Tage nicht zugegriffen
- COLD → WARM: Bei Zugriff (Promotion)

### Query-Verhalten

- Default-Query: durchsucht HOT + WARM
- `--all` Flag: durchsucht auch COLD
- Immer: Index wird abgefragt, nicht Rohdateien

## Offene Fragen

- Schwellwerte konfigurierbar machen? (ja, in palaia.yaml)
- Maximale HOT-Größe? (Config-gesteuert, Default: 50 Einträge)
- Manuelles Promoten von COLD zu HOT?

## Konsequenzen

**Positiv:**
- Context bleibt klein ohne manuelle Arbeit
- Kein Datenverlust — COLD ist archiviert, nicht gelöscht
- Suchindex macht Tier-Übergreifende Suche effizient

**Negativ:**
- Komplexere Implementierung als flache Struktur
- Decay-Tuning braucht echte Nutzungsdaten
