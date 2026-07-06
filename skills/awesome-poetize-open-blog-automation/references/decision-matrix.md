# Decision Matrix

Use `primaryGoal` to decide the default posture of the article.

| primaryGoal | Typical use | viewStatus | submitToSearchEngine | recommendStatus | payType |
| --- | --- | --- | --- | --- | --- |
| `asset_maintenance` | Refresh, organize, preserve content value | public unless clearly a draft | usually true | usually false | `0` |
| `seo_growth` | Evergreen tutorials, searchable guides | public | true | optional | `0` |
| `brand_expression` | Voice, narrative, positioning | public or draft based on polish | optional | optional | `0` |
| `conversion` | Explicit monetization or lead capture | public if ready | case by case | optional | can be `> 0` only when explicitly requested |

## Required implications

- If `primaryGoal != conversion`, then `payType` must resolve to `0`.
- If `publishIntent = draft`, then `viewStatus = false`.
- If `taskType = hide_article`, then `viewStatus = false`.
- If the user asks to delete a post, convert that request into `hide_article`.

## Taxonomy rules

- Reuse exact category and tag matches whenever possible.
- If exact matches fail, offer close candidates.
- Never auto-select a fuzzy taxonomy candidate.
- Never auto-create taxonomy unless explicit creation is confirmed.
