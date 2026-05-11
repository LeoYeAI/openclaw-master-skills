# Dictionaries (market/selection names)

**Package:** `@azuro-org/dictionaries` (npm).

- **getMarketName({ outcomeId })** → market label (e.g. "Total Goals", "1st Half - Winner"). Pass `outcomeId` as returned by the subgraph (string or number).
- **getSelectionName({ outcomeId, withPoint? })** → selection label (e.g. "Over", "Under"). Use **withPoint: true** so the line is included when present (e.g. "Over (2.5)", "Under (2.5)") for markets like Total Goals. On failure, fall back to `outcomeId` or a placeholder.
