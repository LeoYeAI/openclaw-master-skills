# ADR-001: Semantische Suche — Tiered Approach

**Status:** Accepted
**Datum:** 2026-03-11
**Kontext:** #palaia

---

## Kontext

Palaia will semantische Suche ohne Hard-Dependency ermöglichen.
Reine Keyword-Suche (BM25) ist nicht semantisch — ein lokales Embedding-Modell ist die beste Alternative, aber eine zusätzliche Dependency.

## Entscheidung

**Tiered-Approach: Palaia erkennt automatisch was verfügbar ist.**

```
Tier 1 (immer):      BM25/TF-IDF        — Pure Python, zero install
Tier 2 (wenn da):    Lokales Embedding   — ollama (nomic-embed-text)
Tier 3 (wenn da):    API Embeddings      — OpenAI / Voyage AI (wenn Key vorhanden)
```

Palaia prüft beim Start:
1. Ist `ollama` im PATH und `nomic-embed-text` geladen? → Tier 2
2. Ist ein API-Key in Config? → Tier 3
3. Sonst → Tier 1

Der User merkt nichts — Qualität steigt automatisch mit verfügbarer Infrastruktur.

## Konsequenzen

**Positiv:**
- Zero hard dependencies bleibt gewahrt
- Transparentes Upgrade ohne Konfiguration
- Lokale Privatsphäre in Tier 1 + 2

**Negativ:**
- BM25 ist nicht semantisch (Known Limitation — offen kommunizieren)
- Tier 2 erfordert ollama-Setup (dokumentieren)

## Alternativen verworfen

- **Nur BM25:** Nicht ausreichend für Similarity-Search
- **Nur API:** Verletzt Zero-Dependency-Prinzip
- **llama.cpp direkt:** Zu komplex für Nutzer-Setup, ollama ist einfacher
