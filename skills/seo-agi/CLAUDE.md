# CLAUDE.md

This is **seo-agi** -- a Claude Code skill for Generative Engine Optimization. It writes pages that rank on Google AND get cited by LLMs.

This is not a generic SEO prompt. It enforces 500-token chunk architecture, Reddit Test quality gates, verification tags, "Not For You" blocks, and real competitive data from DataForSEO/Ahrefs/SEMRush/GSC.

## Structure

```
SKILL.md              -- The framework (GEO engine + data layer integration)
SPEC.md               -- Technical architecture for the data layer
scripts/
  research.py         -- CLI: SERP research via DataForSEO
  gsc_pull.py         -- CLI: Google Search Console data
  setup.py            -- Interactive first-run config
  lib/
    env.py            -- Config loader
    dataforseo.py     -- DataForSEO REST API client
    serp_analyze.py   -- Content gap analysis engine
    gsc_client.py     -- Google Search Console client
references/
  page-templates.md   -- Structural templates by page type
  schema-patterns.md  -- JSON-LD schema patterns
fixtures/             -- Mock data for testing without API calls
tests/                -- Unit tests
```

## The Framework (SKILL.md)

The SKILL.md is the living document. It contains:
- Core belief system (anti-generic, LLM retrieval, entity consensus)
- Google AI Search 7 ranking signals
- 500-token chunk architecture
- SEAT signals (Semantic + E-E-A-T + Entity/Knowledge Graph)
- Quality gates: Reddit Test, Prove-It Details, Not For You, Information Gain Test
- Verification tagging system ({{VERIFY}}, {{RESEARCH NEEDED}}, {{SOURCE NEEDED}})
- Vertical-specific instructions (airport/parking, local service, listicle, comparison)
- LLM/AEO citation strategy
- Hub & spoke internal linking
- Execution protocol with data layer integration

## Running Tests

```bash
python3 tests/test_env.py
python3 tests/test_serp_analyze.py
python3 tests/test_dataforseo.py

# Mock mode research:
python3 scripts/research.py "test keyword" --mock
```

## Style

- No em dashes in any output
- No "nestled", no "in today's fast-paced world", no "whether you're a...or a..."
- Numbers and specifics over adjectives
- Every claim tagged with {{VERIFY}} or {{SOURCE NEEDED}}
- Tables are mandatory for comparisons -- never simulate with bullet points
