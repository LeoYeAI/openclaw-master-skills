# RAID-Level Vergleich

| Eigenschaft | RAID 0 | RAID 1 | RAID 5 | RAID 6 | RAID 10 |
|-------------|--------|--------|--------|--------|---------|
| Min. Platten | 2 | 2 | 3 | 4 | 4 |
| Redundanz | Keine | Spiegelung | 1 Parität | 2 Paritäten | Spiegelung |
| Kapazität | n×Platte | n/2×Platte | (n-1)×Platte | (n-2)×Platte | n/2×Platte |
| Leseperformance | Sehr hoch | Hoch | Hoch | Hoch | Sehr hoch |
| Schreibperformance | Sehr hoch | Mittel | Mittel | Niedrig | Hoch |
| Ausfalltoleranz | 0 Platten | 1 Platte | 1 Platte | 2 Platten | 1 pro Spiegel |
| Rebuild-Zeit | - | Schnell | Langsam | Sehr langsam | Schnell |
| Einsatz | Temp-Daten | OS, kritisch | Fileserver | Archiv | Datenbanken |

## Kapazitätsberechnung (Beispiel: 8 × 2 TB)

| RAID | Nutzbar | Verlust |
|------|---------|---------|
| RAID 0 | 16 TB | 0 TB |
| RAID 1 | 8 TB | 8 TB (50%) |
| RAID 5 | 14 TB | 2 TB (12.5%) |
| RAID 6 | 12 TB | 4 TB (25%) |
| RAID 10 | 8 TB | 8 TB (50%) |
