# ADR-005: Git als Wissensaustausch-Plattform

**Status:** Accepted
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Multi-Team-Szenarien brauchen einen Kanal für kontrollierten Wissenstransfer.
Für ein Open-Source-Projekt soll die Lösung dezentral, auditierbar und ohne proprietary Cloud sein.

## Entscheidung

**Git als nativer Sync-Mechanismus für `public`-tagged Memories.**

### Wie es funktioniert

```
Team A (Publisher)                    Team B (Consumer)
-----------------                    ----------------
palaia export                        palaia import <git-url>
  → filtert scope:public             → validiert Scopes
  → erstellt Export-Branch           → importiert nur public
  → pushed zu git remote             → merged in lokale Memory
```

### Technisches Design

1. `palaia export` — erstellt Branch `palaia/export/<timestamp>`
   - Nur Memories mit `scope: public`
   - YAML Frontmatter bleibt erhalten
   - Automatischer Commit-Message mit Manifest

2. `palaia import <url> [--branch <branch>]`
   - Validiert jeden Entry: `scope: team` aus fremdem Workspace → rejected
   - Dedup via Hash-Vergleich (keine Duplikate)
   - Dry-Run-Modus (`--dry-run`) zeigt was importiert werden würde

3. **Vertrauen ist bilateral:** Beide Teams entscheiden explizit was sie teilen / importieren

### Warum Git?

- **Open Source-kompatibel:** Jeder hat git. Kein proprietärer Hub nötig
- **Auditierbar:** Vollständige History, wer hat was wann geteilt
- **Dezentral:** Kein zentraler Server erforderlich
- **Versioniert:** Rollback jederzeit möglich
- **Selbst-hostbar:** GitHub, GitLab, Gitea, bare repo — alles funktioniert

## Konsequenzen

**Positiv:**
- Passt perfekt zur Open-Source-Philosophie
- Keine neue Infrastruktur nötig
- Enterprise kann private git repos nutzen

**Negativ:**
- Kein Real-Time-Sync (Pull-basiert)
- Git-Kenntnisse für Advanced-Use-Cases nötig
- Konfliktauflösung bei gleichzeitigen Edits (→ Palaia-Merge-Strategie definieren)

## Alternativen verworfen

- **Palaia Cloud Sync:** Verletzt Zero-Dependency für Core, bleibt als opt-in Enterprise-Feature
- **rsync/SCP:** Kein Versioning, kein Audit-Trail
- **CRDTs:** Zu komplex für den Use Case
