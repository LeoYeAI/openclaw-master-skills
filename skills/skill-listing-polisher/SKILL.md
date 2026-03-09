---
name: skill-listing-polisher
description: Improve a skill's public listing before publish. Use when tightening title, description, tags, changelog, and scan-friendly packaging so the listing looks clearer and less suspicious.
version: 0.1.0
---

# Skill Listing Polisher

Use this skill before publishing or updating a public ClawHub skill.

## What to improve

- title clarity
- description length and truncation risk
- tags that match the actual use case
- changelog that says what changed in plain language
- public package surface that looks normal in review

## Review order

1. shorten the public description if it gets cut off
2. remove internal-only scripts and private identifiers
3. tighten tags to actual buyer intent
4. make the changelog specific and boring
5. check that the package only contains user-facing files

## Fast checks

Run the bundled script:

```bash
./scripts/check-listing.sh /path/to/skill
```

## Output style

When reviewing a skill, return:

1. what weakens trust
2. what weakens discoverability
3. the smallest edit that improves both
