# Backup-Strategien Referenz

## 3-2-1-Regel
- **3** Kopien der Daten (1 Original + 2 Backups)
- **2** verschiedene Medientypen (z.B. SSD + Band)
- **1** Kopie offsite (Cloud oder externer Standort)

## Backup-Typen

| Typ | Sichert | Wiederherstellung | Speicher | Zeit |
|-----|---------|-------------------|----------|------|
| Vollbackup | Alle Daten | Schnell (1 Backup) | Hoch | Lang |
| Differentiell | Änderungen seit letztem Voll | Mittel (Voll + letztes Diff) | Mittel | Mittel |
| Inkrementell | Änderungen seit letztem Backup | Langsam (Voll + alle Inkr.) | Niedrig | Kurz |

## Speicherberechnung (Beispiel)
- Datenmenge: 500 GB
- Tägliche Änderung: 20 GB (4%)
- Zeitraum: 1 Woche

**Wochenplan (Voll-Sonntag + Inkrementell Mo-Sa):**
| Tag | Typ | Größe | Kumuliert |
|-----|-----|-------|-----------|
| So | Voll | 500 GB | 500 GB |
| Mo | Inkr | 20 GB | 520 GB |
| Di | Inkr | 20 GB | 540 GB |
| Mi | Inkr | 20 GB | 560 GB |
| Do | Inkr | 20 GB | 580 GB |
| Fr | Inkr | 20 GB | 600 GB |
| Sa | Inkr | 20 GB | 620 GB |

## RPO und RTO
- **RPO** (Recovery Point Objective): Maximaler akzeptabler Datenverlust (Zeit)
- **RTO** (Recovery Time Objective): Maximale akzeptable Wiederherstellungszeit
