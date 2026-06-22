# BrainX V5 Documentation

- [**How It Works**](./HOW-IT-WORKS.md) — Guía funcional completa (empieza aquí)
- [Architecture](./ARCHITECTURE.md)
- [Configuration](./CONFIG.md)
- [CLI Reference](./CLI.md)
- [Database Schema](./SCHEMA.md)
- [Scripts](./SCRIPTS.md)
- [Tests](./TESTS.md)

## V5 "Cerebro Vivo" Scripts

The following scripts implement the auto-feeding pipeline:

| Script | Location | Description |
|--------|----------|-------------|
| session-harvester.js | scripts/ | Extracts memories from OpenClaw sessions |
| memory-bridge.js | scripts/ | Syncs markdown files to vector DB |
| cross-agent-learning.js | scripts/ | Propagates learnings across agents |
| contradiction-detector.js | scripts/ | Finds duplicate/contradictory memories |
| quality-scorer.js | scripts/ | Auto-promotes/degrades by usage |
| context-pack-builder.js | scripts/ | Generates summary packs |
| weekly-dashboard.sh | cron/ | Weekly metrics dashboard |
| ops-alerts.sh | cron/ | Daily operational alerts |
