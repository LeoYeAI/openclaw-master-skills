# PR Credits — Thank After V2 Goes Live

When V2 is pushed to the public repo, comment on each PR to thank the contributor and let them know their work was integrated.

## Integrated (cherry-picked into V2)

| PR | Author | What | Status |
|---|---|---|---|
| [#17](https://github.com/mvanhorn/last30days-skill/pull/17) | **@JosephOIbrahim** | Windows Unicode fix (cp1252 emoji crash) | Merge or close with thanks |
| [#16](https://github.com/mvanhorn/last30days-skill/pull/16) | **@levineam** | Handle 403 model access errors + gpt-4.1 fallback | Merge or close with thanks |
| [#18](https://github.com/mvanhorn/last30days-skill/pull/18) | **@jonthebeef** | `--days=N` configurable lookback flag | Merge or close with thanks |
| [#1](https://github.com/mvanhorn/last30days-skill/pull/1) | **@galligan** (Matt Galligan) | Marketplace plugin conversion — we took a lighter approach inspired by his PR | Close with thanks, explain lighter approach |

## Already Fixed in V2 (close with thanks)

| PR | Author | What |
|---|---|---|
| [#15](https://github.com/mvanhorn/last30days-skill/pull/15) | **@rszrszrsz** | YAML argument-hint fix — already fixed in V2 |
| [#11](https://github.com/mvanhorn/last30days-skill/pull/11) | **@nerveband** | Same YAML fix (earlier) — already fixed in V2 |

## Not Integrated (close with explanation)

| PR | Author | What | Why |
|---|---|---|---|
| [#5](https://github.com/mvanhorn/last30days-skill/pull/5) | **@jblwilliams** | Codex auth with OpenAI Responses API | Good idea, too complex for now (358 lines SSE/JWT). May revisit. |
| [#14](https://github.com/mvanhorn/last30days-skill/pull/14) | **@thangman1** | WebSearch-first, API keys optional | Philosophical shift — V2 already does WebSearch in parallel |
| [#10](https://github.com/mvanhorn/last30days-skill/pull/10) | **@thetechreviewer** | OpenRouter API integration | Too large (1029 lines), adds MCP server |

## Suggested Comment Template

> Thanks for this PR! We integrated your [fix/feature] into V2 (commit XXXXX). Really appreciate the contribution. 🙏
>
> Closing this PR since the changes are now in main via a different commit, but full credit to you for the idea and implementation.
