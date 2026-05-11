# Index Maintenance

## Tier A: AI Agent Self-Maintenance (Real-time)

**Directive**: Every code modification MUST include atomic updates to the relevant Tier A indexes. A code change is NOT complete until the indexes reflect it.

| Trigger | Required Action |
|---------|----------------|
| File added | Add entry to parent `INDEX.md` Files table |
| File renamed/moved | Update parent `INDEX.md`; update `AGENTS.md` if in navigation table |
| File deleted | Remove from parent `INDEX.md`; update `AGENTS.md` if in navigation table |
| Module added | Create `INDEX.md` with all sections; update `AGENTS.md` directory map + navigation |
| Module removed | Delete `INDEX.md`; update `AGENTS.md` directory map + navigation table |
| Public API signature changed | Update `INDEX.md`: Public API table, Interface Contract, Modification Risk |
| New dependency added | Update this module's `INDEX.md` Dependencies (Fan-out count) |
| New caller of this module | Update this module's `INDEX.md` Dependents (Fan-in count) |
| Cross-cutting pattern changed | Update `AGENTS.md` Cross-Cutting Patterns section |
| Test added/removed/renamed | Update `INDEX.md` Tests section |
| File header contract changed | Ensure L2 header matches actual function signatures and behavior |

**Anti-patterns**:
- Stale `INDEX.md` → AI navigates to wrong file or misses dependencies
- Stale Dependents list → AI misses affected callers during refactoring (**most dangerous**)
- Updating Tier B docs during active development → wasted tokens, lower quality output

## Tier B: Iteration-End Documentation Sync (Batch)

At the end of a development iteration (sprint, milestone, or feature completion), sync Tier B documents from Tier A indexes:

1. **Review changes**: Scan all `INDEX.md` and `AGENTS.md` modifications since last sync
2. **Update `architecture.md`**: If module structure, dependency graph, or cross-cutting patterns changed
3. **Create/update ADRs**: For any significant architectural decisions made during the iteration
4. **Update API docs**: Derive from `INDEX.md` Public API tables and L2 contract headers
5. **Update `README.md`**: If project scope, build commands, or quick-start steps changed
6. **Update developer guides**: If workflows or deployment steps changed
7. **Update `docs/*/INDEX.md`**: Sync doc directory indexes with any new/removed documents

**Tier B documents reference Tier A as source of truth** — prefer links to `INDEX.md` sections over duplicating content. This keeps human docs shorter and reduces staleness risk.

**AI instruction**: When the user requests "documentation sync", "update docs", or "iteration end", execute this Tier B batch workflow. During normal development, ignore Tier B files entirely.
