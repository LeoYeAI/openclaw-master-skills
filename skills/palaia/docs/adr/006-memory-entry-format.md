# ADR-006: Memory Entry Format

**Status:** Accepted
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Palaia braucht ein konsistentes, menschenlesbares Format für Memory-Einträge.
Binärformate scheiden aus (Prinzip: Lokal first, Zero Dependencies).

## Entscheidung

**Markdown mit YAML Frontmatter.**

```markdown
---
id: <uuid4>
scope: team
agent: cyberclaw
tags: [project, clawsy]
created: 2026-03-11T10:00:00Z
accessed: 2026-03-11T10:00:00Z
access_count: 1
decay_score: 1.0
content_hash: sha256hex
---

Der eigentliche Memory-Inhalt als Freitext.
```

### Pflichtfelder

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| id | UUID4 | Eindeutige ID |
| scope | string | private/team/shared:X/public |
| created | ISO-8601 | Erstellungszeitpunkt |
| accessed | ISO-8601 | Letzter Zugriff |
| access_count | int | Anzahl Zugriffe |
| decay_score | float | Aktueller Decay-Score (0.0-1.0) |
| content_hash | string | SHA-256 des Body-Texts |

### Optionale Felder

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| agent | string | Name des schreibenden Agents |
| tags | list | Freie Tags für Filterung |
| title | string | Kurztitel |

## Konsequenzen

**Positiv:**
- Menschenlesbar, git-freundlich
- Standard-Tools können Entries lesen/bearbeiten
- YAML Frontmatter ist etablierter Standard

**Negativ:**
- Parsing von YAML Frontmatter nötig (stdlib reicht: split + simple parser)
- Kein Schema-Enforcement ohne Validation-Code
