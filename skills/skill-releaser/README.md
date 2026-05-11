# skill-releaser

Release agent skills to ClawhHub through a full publication pipeline.

## What It Does

Takes any skill with a finished SKILL.md and handles everything needed to publish it:

1. **Scaffolds** missing structure files (README, CHANGELOG, tests, skill.yml) from SKILL.md
2. **Scans** for OPSEC violations (secrets, personal info, hardcoded paths)
3. **Reviews** via dual process — agent checklist + user approval
4. **Stages** in a private repo for user review on any device
5. **Publishes** by erasing history (force push) and flipping repo to public, then ClawhHub

## When to Use

- "Release {skill-name} to ClawhHub"
- "Is {skill-name} ready for release?"
- "Which skills are ready to publish?"
- "Prepare {skill-name} for release"

## Key Design Decisions

- **History erased at release** — orphan branch + force push gives a single clean commit
- **One repo per skill** — starts private for staging, flipped to public at release
- **User approval is a hard gate** — nothing goes public without explicit "approve"
- **Boilerplate is auto-generated** — only SKILL.md content needs to be written by hand
- **Security scan verified** — uses browser to check VirusTotal + OpenClaw scan results on ClawhHub before declaring release complete

## Prerequisites

- `gh` CLI authenticated
- `clawhub` CLI installed
- Shell access for git operations
- Browser tool available (for ClawhHub security scan verification)

## License

MIT

## Future Work

### Multi-Agent Architecture
When release volume justifies it, refactor from single-agent to multi-agent:

```
Dispatcher (coordinator)
  ├── Scaffolder (Steps 1-2): boilerplate, validation → flash-lite
  ├── Publisher (Steps 3-10): git ops, staging, OPSEC, publish → flash-lite
  ├── Verifier (Step 11): browser-based scan verification → sonnet
  └── Dispatcher delivers Step 12 summary
```

**Triggers:** 5+ skills per session, browser failures cascading into re-runs, rate limit cascades.

**Prerequisite:** Ship 3-5 more skills through single-agent first. Refactor with evidence, not speculation.

### ClawhHub Version Purge
No per-version deletion exists. `delete` is soft-delete (preserves versions). If a version leaks PII: full delete + re-publish (loses download counts) or contact ClawhHub support. Monitor for `clawhub delete-version` in future CLI releases.
