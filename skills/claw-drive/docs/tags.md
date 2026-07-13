# Tags

Tags enable cross-category search. A file lives in one folder but can have multiple tags.

## How It Works

Tags are stored in the Tags column of `INDEX.md`:

```
| Date | Path | Description | Tags | Source |
|------|------|-------------|------|--------|
| 2026-02-15 | medical/sorbet-vet-invoice.pdf | VEG emergency | medical, invoice, sorbet, emergency | email |
```

Searching by any tag returns matching files:

```bash
claw-drive search sorbet
claw-drive search invoice
claw-drive tags            # list all tags with usage counts
```

## Guidelines

- **1-5 tags** per file, comma-separated
- **Lowercase**, single words or short hyphenated phrases
- **Always include** the category name as a tag (e.g. `medical`)
- **Add cross-cutting tags** for: entity names (`sorbet`), document type (`invoice`, `receipt`), context (`emergency`, `tax-2025`)
- **Reuse existing tags** — run `claw-drive tags` before inventing new ones

## Examples

| File | Tags |
|------|------|
| Vet invoice in `medical/` | `medical, invoice, sorbet, emergency` |
| W-2 in `finance/` | `finance, tax-2025` |
| Trip itinerary in `travel/` | `travel, japan` |
| Lease agreement in `contracts/` | `contracts, lease, apartment` |
