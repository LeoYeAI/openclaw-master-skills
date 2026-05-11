# ADR-002: Scope-Tags und Cross-Team Knowledge Transfer

**Status:** Accepted
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Agents in einem Team teilen Wissen. Aber nicht alles darf raus.
Klare, explizite Regeln sind nötig — besonders für Multi-Team-Setups.

## Entscheidung

**Jede Memory-Einheit bekommt beim Schreiben einen Scope-Tag (YAML Frontmatter).**

```yaml
---
scope: private           # nur dieser Agent, nie exportiert
scope: team              # alle Agents im selben Workspace
scope: shared:projektname  # nur Agents die dem Projekt angehören
scope: public            # exportierbar an andere Teams via git
---
```

**Grundsatz: Sharing ist immer explizit (opt-in), nie implizit.**

### Regeln

| Scope | Sichtbar für | Export möglich |
|-------|-------------|---------------|
| private | Nur schreibender Agent | Nein |
| team | Alle Agents im Workspace | Nein |
| shared:X | Agents mit Zugriff auf Projekt X | Nein |
| public | Alle Agents im Workspace | Ja (git) |

### Cross-Team via Git

- Git-Export erstellt Branch mit **nur** `scope: public` Memories
- Beim Import: Palaia lehnt alles mit `scope: team` aus fremdem Workspace ab
- Kein "alles oder nichts" — granulare Kontrolle

## Konsequenzen

**Positiv:**
- Klare Compliance-Basis für Enterprise
- Kein versehentliches Leaken von internem Wissen
- Git als Austauschplattform: Open Source, versioniert, auditierbar

**Negativ:**
- Agents müssen beim Schreiben den richtigen Scope setzen
- Default-Scope muss sinnvoll sein (→ `team` als Default)

## Alternativen verworfen

- **Kein Scoping:** Zu gefährlich für Multi-Team
- **Whitelist-basiert (welche Felder):** Zu komplex, schwer wartbar
- **Zentralisiertes Berechtigungssystem:** Verletzt Zero-Dependency-Prinzip
