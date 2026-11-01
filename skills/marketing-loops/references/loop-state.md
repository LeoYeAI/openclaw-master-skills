# Loop State & Run Logging

Idempotency is only real if the loop can remember what it already did between runs. This reference defines where that state lives and how to log runs — so loops don't double-act, re-nag the same people, or re-alert the same issue.

## Where state lives

Persist each loop's state in a file under `.agents/loops/` — the same `.agents/` convention this repo uses for `product-marketing.md` and `listening-sources.md`. One state file per loop:

```
.agents/loops/<loop-name>.json     # the loop's memory
.agents/loops/<loop-name>.log      # append-only run log
```

If your scheduler or platform provides its own dedupe/cursor storage, use that instead — the point is durable state, not the specific file. Never keep state only in memory; a loop that forgets on restart will repeat itself.

## What to store

A state file holds whatever the loop needs to not repeat itself:

```json
{
  "loop": "churn-signal",
  "last_run": "2026-07-01T09:00:00Z",
  "cursor": "2026-06-30T23:59:59Z",        // watermark — only process items newer than this
  "handled": ["acct_1042", "acct_1077"],    // dedupe keys already acted on
  "cooldowns": {                             // entity -> next-eligible timestamp
    "acct_1042": "2026-07-15T00:00:00Z"
  },
  "in_flight": ["exp_pricing_v3"],           // actions/tests currently open
  "counters": { "acct_1042_attempts": 2 }    // e.g. dunning/win-back attempt counts
}
```

- **cursor / watermark** — the high-water mark of what's been processed (a timestamp or last ID). The loop only looks at items past it.
- **handled** — dedupe keys for items already acted on, so re-runs skip them.
- **cooldowns** — per-entity suppression windows so you never re-contact someone inside the window.
- **in_flight** — open items (running tests, active interventions) so the loop doesn't start a conflicting one.
- **counters** — attempt counts that drive stop conditions (e.g., "after 2 win-back emails, stop").

Keep state small and prune it: expire old `handled`/`cooldown` entries once they're past their window.

## Idempotency patterns

- **Watermark**: process only items newer than `cursor`; advance `cursor` at the end of a successful run. Safe to re-run — it won't reprocess.
- **Dedupe set**: before acting on an item, check its key against `handled`; add it after acting.
- **Cooldown map**: before contacting an entity, check `cooldowns[entity]`; set it after contact.
- **In-flight guard**: before starting an action that shouldn't overlap (a test, an intervention), check `in_flight`.

## Run logging

Append one line per run, whether or not it acted. This is the audit trail and the vanity-loop detector.

```
2026-07-01T09:00Z  checked=312  acted=2   note="2 accounts newly at-risk, interventions staged"
2026-07-02T09:00Z  checked=298  acted=0   note="no action"
2026-07-03T09:00Z  checked=305  acted=0   note="no action"
```

Log at minimum: timestamp, how many items checked, how many acted on, and a short note. Use it to answer two questions:
- **Is it a vanity loop?** If every run is `acted=0` for weeks and nobody misses it — or it acts every run (a sign it's chasing noise) — reconsider it.
- **Did it double-act?** Two runs acting on the same entity means the dedupe/cooldown state isn't working.

## Resetting & backfilling safely

- To **reset** a loop, clear its `cursor`/`handled` — but keep `cooldowns` so a reset doesn't spam people who were recently contacted.
- On **first run** (no state yet), set the watermark to "now" rather than processing all history, or you'll blast every historical item. If you genuinely want a backfill, do a dry run first (log what it *would* do, act on nothing) and respect cooldowns.
- Never log raw PII in state or run logs — use IDs or hashes (see `loop-guardrails.md`).

## Session end: decisions and learnings

The state file stops a loop from repeating itself. It doesn't help the rest of the team, or the next drafting session, learn from what the loop found. Close every run that acted, and every manual working session on a loop, with a short session-end step:

1. **Write 1–3 decisions to the run log.** A decision is something that changes what happens next: "paused the competitor-term ad group pending a new landing page," "kept variant B as control," "dropped Reddit from the listening sources." Routine runs that changed nothing get no decision line; "no action" in the log is enough.
2. **Note open items** that carry to the next run (a test still collecting data, an approval still pending) in the state file's `in_flight`, so the next run picks them up instead of starting over.
3. **Propose learnings that will still hold next quarter.** If the run produced a lesson that should change future drafts or plans, propose a row for the **Learnings** table in `.agents/product-marketing.md` (format and promotion rules are in the **product-marketing** skill). Promote only lessons backed by a finished test or a pattern seen in two or more runs or campaigns. One-off results stay in the run log.
4. **Show proposals to the user.** Learnings are shared context every skill reads, so they're added on approval, never written silently by a scheduled run.
5. **Retire what the run contradicted.** If a run's result contradicts an active learning, propose marking it `retired` with the reason.

Example run-log line with decisions:

```
2026-10-15T09:00Z  checked=42  acted=3  note="2 fatigued ads refreshed; 1 learning proposed"
  decision: kept UGC testimonial as control (CTR 1.9% vs 1.1%, 6,800 impressions each)
  decision: paused static carousel concept (3 rounds, no winner)
  learning-proposed: "Testimonial hooks beat feature demos on Meta cold audiences" (2 campaigns)
```

The run log stays the full record. The Learnings table holds the short list of lessons that should shape the next piece of work.
