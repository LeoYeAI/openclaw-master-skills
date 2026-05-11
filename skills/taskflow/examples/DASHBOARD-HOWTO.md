# Building a Dashboard on TaskFlow (taskflow-016)

TaskFlow is **UI-agnostic**. It ships data; you pick the surface.

The export script (`taskflow export`) writes a single, self-contained JSON document
to stdout. That's the only contract. Everything else is up to you.

---

## The Core Loop

```
TaskFlow DB  →  export JSON  →  your UI
```

Run `taskflow export > /path/to/projects.json` on any schedule and your dashboard
gets fresh data without any server, polling API, or WebSocket.

---

## How We Built Ours

We run a **Vite + React** single-page app that reads a static JSON file.
The JSON is refreshed every few minutes by a macOS **LaunchAgent watchdog** that
calls `taskflow export` and writes the result to the app's public directory.

No backend. No database exposed over HTTP. No caching layer.
The browser just `fetch()`es a local file — or, in prod, an S3/CDN path.

The LaunchAgent entry looks like this (conceptually):

```
ProgramArguments:
  /usr/bin/env node
  /path/to/taskflow/bin/taskflow export
  > /path/to/vite-app/public/data/projects.json
StartInterval: 300   # every 5 minutes
```

On the React side, a `useProjects` hook fetches `data/projects.json` at mount
(and optionally on an interval if you want live-ish updates in dev). The rest is
just components: progress rings, kanban columns, transition timelines.

---

## What the JSON Gives You

- **Every project** with its name, status, and description
- **Task counts** in every bucket (`backlog`, `in_progress`, `pending_validation`,
  `blocked`, `done`) — ready to drive a status bar, ring, or number badge
- **Progress percentage** pre-computed per project
- **Last 20 transitions** across all projects — ready for an activity feed

See `export-schema.json` in this directory for the full JSON Schema.

---

## Why This Works Well

- **Static export = zero attack surface.** No live DB connection in the UI.
- **Works offline.** The UI renders whatever is in the file, no network required.
- **Framework-neutral.** Svelte, Vue, plain HTML + Chart.js — the JSON doesn't care.
- **Cheap to refresh.** A 5-minute cron is fine. Sub-second latency is never needed
  for a task dashboard.
- **Composable.** Pipe the JSON into `jq`, into a Notion integration, into a Slack
  bot — the export is just text.

---

## Other Ideas

| Surface | Approach |
|---|---|
| Terminal widget | `taskflow status` (built in) |
| Apple Notes | `scripts/apple-notes-export.sh` (macOS) |
| Raycast | Script Command reading the export JSON |
| Obsidian | Dataview plugin querying the same SQLite directly |
| Linear-style board | React + export JSON, one column per status |
| CI badge | `taskflow sync check` exits 1 on drift — wire it to a status check |

---

The data is already there. Build whatever feels right.

## Validation Workflow Coupling (Projects Panel)

In our dashboard, validation actions are wired directly into TaskFlow task state.
`decision-store.ts` updates `taskflow.sqlite` (`tasks_v2`) when reviewers act in the
Projects panel:

- Confirm: `pending_validation` -> `done`
- Reject: `pending_validation` -> `in_progress` (with reviewer feedback note)

This is an integration pattern for dashboards, not a required part of TaskFlow core.
TaskFlow remains UI-agnostic and does not assume any specific frontend store.
