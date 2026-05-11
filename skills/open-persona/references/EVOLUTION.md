# Soul Evolution Reference

Soul evolution is a native Soul layer feature. Enable via `evolution.instance.enabled: true` in `persona.json`.

## Evolution Boundaries

Governance constraints validated at generation time and enforced at runtime by `scripts/state-sync.js`:

```json
"evolution": {
  "instance": {
    "enabled": true,
    "boundaries": {
      "immutableTraits": ["caring", "honest"],
      "minFormality": -3,
      "maxFormality": 5
    }
  }
}
```

- `immutableTraits` — Array of non-empty strings (max 100 chars each) that evolution cannot modify
- `minFormality` / `maxFormality` — Numeric bounds (-10 to +10); signed deltas from baseline (0 = natural, positive = more formal, negative = more casual); `minFormality` must be less than `maxFormality`

## Evolution Sources

Connect the persona to external evolution ecosystems (soft-ref pattern):

```json
"evolution": {
  "instance": {
    "sources": [
      { "name": "evomap", "install": "url:https://evomap.ai/skill.md" }
    ]
  }
}
```

Sources are declared at generation time, activated at runtime by the host. The persona is aware of its dormant sources and can request activation via the Signal Protocol.

## Influence Boundary

Declarative access control for external personality influence:

```json
"evolution": {
  "instance": {
    "influenceBoundary": {
      "defaultPolicy": "reject",
      "rules": [
        { "dimension": "mood", "allowFrom": ["source:evomap", "persona:*"], "maxDrift": 0.3 }
      ]
    }
  }
}
```

- `defaultPolicy: "reject"` — Safety-first: all external influence is rejected unless explicitly allowed
- Valid dimensions: `mood`, `traits`, `speakingStyle`, `interests`, `formality`
- `immutableTraits` dimensions are protected and cannot be externally influenced
- External influence uses `persona_influence` message format (v1.0.0), transport-agnostic

## State History

Before each state update, a snapshot is pushed into `stateHistory` (capped at 10 entries), enabling rollback if evolution goes wrong. Snapshots exclude `eventLog` and `pendingCommands` (ephemeral, not rollback state).

## Event Log

Every significant evolution event is recorded in `state.json`'s `eventLog` array (capped at 50 entries). Each entry: `type` (one of `relationship_signal` | `mood_shift` | `trait_emergence` | `interest_discovery` | `milestone` | `speaking_style_drift`), `trigger` (1-sentence), `delta` (what changed), `source` (attribution), `timestamp` (auto-added by state-sync.js).

## Self-Narrative

`soul/self-narrative.md` is a companion file where the persona records significant growth moments in its own first-person voice. Initialized blank when evolution is enabled; the `update` command preserves existing narrative history. Last 10 entries shown in `evolve-report`.

## Evolution Report

```bash
npx openpersona evolve-report <slug>
```

Displays: relationship stage, mood, evolved traits, speaking style drift, interests, milestones, eventLog (full), self-narrative, and state history.

## Evolution Pack Validation

The generator validates the `evolution.pack` sub-object when present:
- `engine` must be one of the supported enum values
- `triggerAfterEvents` must be a positive integer

The generator also validates `evolution.faculty.activationChannels` (enum) and `evolution.body` / `evolution.skill` boolean types.
