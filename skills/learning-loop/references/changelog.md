# Changelog

## v1.3.0

### WAL Protocol (Write-Ahead Log)

Ensures critical information survives compaction. Write to file BEFORE responding.

**Scan EVERY message for WAL triggers:**
- Corrections, proper nouns, preferences, decisions, specific values

**Usage:**
```bash
bash wal-capture.sh /path/to/workspace correction "It's 4pm not 5pm"
bash wal-capture.sh /path/to/workspace decision "Use Kimi for all sub-agents"
bash wal-capture.sh /path/to/workspace preference "No em dashes anywhere"
bash wal-capture.sh /path/to/workspace fact "API key expires March 13, 2027"
```

## v1.2.0
- Category consolidation: 25 to 8 unified categories
- Violation auto-tracking via track-violations.sh
- Application auto-tracking via track-applications.sh
- Event archival via archive-events.sh
- Dynamic rule injection via rule-check.sh
- Guard protocol (R-030)

## v1.1.0
- Confidence scoring for lessons (0.0-1.0)
- Feature request detection
- Knowledge gap detection
- 80+ feedback signal patterns (up from 40)
