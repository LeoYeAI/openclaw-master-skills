---
name: stitch-design
description: Official Google Stitch SDK wrapper for OpenClaw. Requires only STITCH_API_KEY. Generate UI screens from text, apply targeted edits, branch variants, export HTML/images, and track design lineage with screen aliases plus append-only event history. Stores local artifacts under the skill folder and talks only to Google Stitch endpoints needed for generation and screenshot delivery.
metadata: {"openclaw": {"requires": {"anyBins": ["node", "node18", "node20", "node22"], "env": ["STITCH_API_KEY"]}, "primaryEnv": "STITCH_API_KEY", "homepage": "https://github.com/rasimme/stitch-design"}}
---

# Stitch Design

AI-powered UI design with Google Stitch — generate, iterate, export.

## Setup

**Required:** Node.js 18+ and `STITCH_API_KEY` env var.
Get a key at: https://stitch.withgoogle.com → Profile → API Keys
Configure the key in your OpenClaw skill env settings or in the shell used to run the CLI.

```bash
# Install dependencies (one-time, from skill root)
cd scripts && npm install
```

Install scope: this installs the Node dependency declared in `scripts/package.json` (`@google/stitch-sdk`) plus its npm transitive dependencies.

**Troubleshooting:**
- `STITCH_API_KEY not set` → ensure the env var is configured in OpenClaw skill settings or shell
- `ECONNRESET` / timeouts → Stitch API calls take 1-5 min; the CLI retries automatically
- `Corrupt names.json` → run `node scripts/stitch.mjs rebuild --project <id>` to reconstruct from event log

## Usage

## Runtime Scope

- Network: Google Stitch API and Google-hosted screenshot URLs returned by Stitch
- Credentials: `STITCH_API_KEY` only
- Local writes: `runs/`, `state/`, `latest-screen.json`
- No extra services, daemons, browser automation, or unrelated credentials required


The CLI is at `scripts/stitch.mjs`. All output is JSON on stdout.

```bash
node scripts/stitch.mjs <command> [args] [--flags]
```

---

## Workflow: New Design

Use when user wants to design something from scratch.

**Step 1 — Shape the prompt** (see `references/prompt-guide.md` for keywords)

Transform the user's brief into a richer prompt:
- Add layout terms (sidebar, card grid, hero section...)
- Add visual tone (minimal, dark mode, editorial...)
- Specify device explicitly

**Step 2 — Generate**

```bash
node scripts/stitch.mjs generate <project-id> "shaped prompt" --device desktop
```

Typical time: 1–5 minutes. The CLI downloads HTML + PNG automatically.

**Step 3 — Preview**

Show the hi-res screenshot: run `show <alias>` → display via `MEDIA:<screenshotUrl>` (see Image Delivery).

**Step 4 — Iterate** (edit or variants)

---

## Workflow: Edit Design

Use when user wants targeted changes to an existing screen.

```bash
node scripts/stitch.mjs edit <screen-id> "change the header to blue, add a search bar"
# --project auto-detected from latest-screen.json
```

Focused edits work better than vague ones. Be specific: colors, layout, components.

---

## Workflow: Design Variants

Use when user wants to explore directions before committing.

```bash
# 3 variants, exploring freely
node scripts/stitch.mjs variants <screen-id> "make it feel more premium" --count 3 --range explore

# More conservative: refine only
node scripts/stitch.mjs variants <screen-id> "tighten the spacing" --count 2 --range refine

# Target specific aspects
node scripts/stitch.mjs variants <screen-id> "new color direction" --aspects color_scheme,text_font
```

**Creative ranges:**
- `refine` — small changes, stays close to original
- `explore` — moderate exploration (default)
- `reimagine` — radical redesign

**Aspects** (comma-separated): `layout`, `color_scheme`, `images`, `text_font`, `text_content`

---

## Workflow: Visual Review (Browse & Pick)

Use when user wants to see existing designs and decide which to work on.

**Step 1 — Get project overview**

```bash
node scripts/stitch.mjs info <project-id>
```

This returns all screen IDs + titles.

**Step 2 — Export screenshots for each screen**

```bash
node scripts/stitch.mjs image <screen-id> --project <project-id>
```

Do this for each screen (or a selection). Each call saves a local thumbnail + `result.json` with the `screenshotUrl`.

**Step 3 — Send images to user**

For each screen: get the `screenshotUrl` from the `image` command's `result.json`, append `=w780`, and display via `MEDIA:<url>`.
Include screen ID + title as caption so user can reference them.

**Step 4 — User picks a screen**

User says "take screen 3" or "the dark one" → match to screen ID.

**Step 5 — Continue with edit/variants**

Use the picked screen ID for `edit` or `variants` workflows.

---

## Workflow: Export

Download HTML + screenshot from an existing screen.

```bash
node scripts/stitch.mjs export <screen-id> --project <project-id>
# or just HTML:
node scripts/stitch.mjs html <screen-id>
# or just screenshot:
node scripts/stitch.mjs image <screen-id>
```

---

## Multi-Screen Consistency

### Rule: Always start with a Hub Screen

Related screens of a concept need a shared hub screen as their visual basis. Generate is generative — layout, colors, spacing, and typography are all invented from scratch. Edit takes the source screen as the visual basis and changes only what you describe — navigation, typography, and color palette stay consistent.

**generate vs edit — the key difference:**
- `generate` = brand-new screen. Everything is up for grabs.
- `edit` = visual continuation of the source screen. Only the described delta changes.

### Recommended Workflow

1. Generate the hub screen → review it carefully
2. All further screens of the same concept → `edit` from the hub, not fresh `generate`
3. Max 1-2 changes per edit prompt — Stitch regenerates generatively, not surgically. Too many changes = unpredictable results
4. Even elements you did NOT mention can change in an edit. Fewer changes = more stable output.

**Core Rule:** For multi-screen concepts, always define a hub screen first, then derive further screens via edit — never fresh generate.

### Reduce to Core (Concept Phase)

During the concept phase, 3-4 consistent core screens are enough. Full screen coverage only after the concept is approved. Stitch excels at rapid exploration, not exhaustive elaboration.

---

## Screen Review Loop

A systematic loop for deciding when to keep editing in Stitch vs. when to note something for post-export fixing.

### 4-Step Loop

**Step 1 — Run generate or edit**

**Step 2 — Analyze the screenshot** (vision model)

Check against this list:
- Layout structure — sections in right order, correct hierarchy
- Colors — matches design system / brief
- Content — no hallucinated labels, avatars, or copy that doesn't belong
- Navigation — correct tabs, back buttons, menu items
- Design System Compliance — spacing, typography, component patterns

**Step 3 — Categorize issues**

| Category | Examples |
|---|---|
| **Stitch-fixable** | Missing section, wrong layout order, major color error, wrong navigation structure |
| **Post-Export Fix** | Exact pixel spacing, icon details, typography fine-tuning, persistent content hallucinations (avatars, labels) |

**Step 4 — Decide**

- Fix in Stitch → write a focused edit prompt (max 1-2 changes), go back to Step 1
- Post-export fix → note it, move on to next screen

### Decision Tree

- **Stitch didn't fix it after 2 edits** → note as post-export fix, move on
- **Detail work** (shadows, exact radii, pixel spacing) → directly note as post-export fix, don't waste edit budget
- **Structural issue** (section missing, navigation wrong) → Stitch edit

The user decides which external tool to use for post-export fixes — Figma, Framer, code, or any other tool. Do not prescribe a tool.

---

## Planning — Feature Coverage

Before generating anything, create a feature matrix: which features appear on which screen. Only start generating once the coverage is clear. This way every subsequent generate/edit call is a deliberate execution step, not a discovery — no surprises, no forgotten features. Keep this matrix short; a simple table or bullet list per screen is enough. Three focused screens you've thought through are worth more than ten screens you discover issues with during generation.

---

## Project Management

```bash
# List all projects
node scripts/stitch.mjs projects

# Create a new project
node scripts/stitch.mjs create "App Name"

# Show project screens
node scripts/stitch.mjs info <project-id>
```

---

## State Tracking

`latest-screen.json` (in skill root) tracks the last generated/edited screen.

- `edit`, `variants`, `html`, `image`, `export` auto-detect project from `latest-screen.json`
- Override with `--project <id>` when needed

---

## Screen Names (Alias Registry)

Screens get auto-generated IDs like `bcde81e368e24edbabd6213d9dc17b3b`. Use **screen names** to give them memorable aliases that persist across sessions.

### Naming screens

```bash
# Name during generation (recommended — naming in the flow)
node scripts/stitch.mjs generate <project-id> "prompt" --name concept-a

# Name during editing (alias follows the new screen)
node scripts/stitch.mjs edit <screen-id> "changes" --name concept-a --force

# Name an existing screen manually
node scripts/stitch.mjs name concept-a <screen-id> --project <id>

# Add a note
node scripts/stitch.mjs name concept-a <screen-id> --note "Karte als Fenster, Bottom Sheet"
```

### Looking up screens

```bash
# Show screen details via alias or screen ID (fetches live data from Stitch API)
node scripts/stitch.mjs show concept-a
node scripts/stitch.mjs show bcde81e368e24edbabd6213d9dc17b3b

# Resolve alias to screen ID only
node scripts/stitch.mjs resolve concept-a

# List all named screens in a project
node scripts/stitch.mjs names

# List + verify against Stitch API (checks for deleted screens)
node scripts/stitch.mjs names --verify
```

### Managing names

```bash
# Rename
node scripts/stitch.mjs rename concept-a map-startscreen

# Remove
node scripts/stitch.mjs unname old-concept
```

### Naming rules
- **Slugs only:** lowercase `a-z`, `0-9`, hyphens. Case-insensitive.
- **Examples:** `concept-a`, `home-v2`, `onboarding-flow`, `dark-variant-3`
- **Not allowed:** spaces, uppercase, special characters
- Aliases are **unique per project** — the same alias can exist in different projects
- Use `--force` to overwrite an existing alias

### How it works
- Names are stored in `state/projects/<projectId>/names.json` (rebuildable snapshot)
- Every operation is recorded in `state/projects/<projectId>/events.jsonl` (append-only, immutable)
- The Stitch API remains the source of truth for screen data — local state only stores mappings and history
- If a screen is deleted in Stitch, `show` will report it as broken; `names --verify` checks all at once
- If `names.json` gets corrupted, run `rebuild` to reconstruct from the event log (pre-log aliases require a backup or manual re-naming)

### Event Log & History

Every generate/edit/variants operation and every alias change is recorded as an append-only event.

```bash
# Show all events for an alias (creates, edits, rebinds)
node scripts/stitch.mjs history concept-b

# Show a specific alias revision (Nth time it was bound to a screen)
node scripts/stitch.mjs history concept-b --rev 2

# Walk the edit/variant lineage DAG backwards from a screen
node scripts/stitch.mjs lineage concept-b
node scripts/stitch.mjs lineage abc123def456

# Rebuild names.json from event log (recovery)
node scripts/stitch.mjs rebuild --project <id>
```

**Event types:**
- `generate` / `edit` / `variants` — screen operations (with parentScreenId, promptPreview, runDir)
- `alias_set` / `alias_renamed` / `alias_removed` — alias pointer changes
- Variants include a `variantGroupId` to group related screens

### Agent workflow (MANDATORY)
When generating or editing screens for the user:
1. **Always use `--name`** when the user has a clear concept name or purpose for the screen
2. If the user refers to a screen by name (e.g. "show me Concept A"), use `show <alias>` first
3. When editing a named screen, use `--name <same-alias> --force` to keep the alias pointing to the latest version
4. **After every generate/edit/variants:** run `show <alias|screenId>`, extract `screenshotUrl`, display via `MEDIA:<url>` (see Image Delivery section)
5. Use `names` at session start to see what screens already exist

---

## Artifacts

Every operation saves to `runs/<YYYYMMDD-HHmmss>-<operation>-<slug>/`:

| File | Content |
|---|---|
| `screen.html` | Full HTML/CSS/JS of the screen |
| `screen.png` | Screenshot (desktop/mobile) |
| `result.json` | Metadata (screenId, projectId, prompt, timestamps) |
| `variant-N.html/.png` | For variants commands |

---

## Architecture

The skill uses a 3-layer local state model. The Stitch API is always the source of truth for screen content (HTML, screenshots).

| Layer | Storage | Purpose |
|---|---|---|
| **Artifacts** | `runs/<timestamp>/` | Immutable per-operation receipts: thumbnail, HTML, result.json |
| **Event Log** | `state/projects/<id>/events.jsonl` | Append-only chronological record of all operations |
| **Alias Pointers** | `state/projects/<id>/names.json` | Current named references — rebuildable from event log |

**Key principles:**
- `runs/` are artifacts (never mutated, never deleted)
- `state/` is the mutable layer (names.json is a snapshot, events.jsonl is append-only)
- `names.json` can be rebuilt from `events.jsonl` via `rebuild` (complete for all alias changes recorded in the log; pre-log aliases are preserved from existing snapshot if available)
- Local thumbnails (`screen.png`) are low-res; always use `screenshotUrl` + `=w780` for display
- `state/` and `runs/` are gitignored — they are local working state, not source code

---

## Core Rules

1. **MANDATORY: Read `references/prompt-guide.md` before your first generate/edit/variants call in a session.** It contains critical prompting principles that determine output quality. For SDK details (methods, types, enums), see `references/sdk-api.md`.
2. **Always shape prompts** — Never pass the user's raw text directly to Stitch. Enrich it using the Prompt Framework (Context → Structure → Aesthetic → Constraints) from the prompt guide. Transform weak prompts into strong ones.
3. **Component isolation by default** — When the user asks for a component (not a full page), always add: "Design a single standalone UI component — do NOT generate a full application screen. Show it isolated on a neutral background."
4. **Preview first** — Show the hi-res screenshot to user before offering export
5. **Visual feedback (MANDATORY)** — After every generate/edit/variants, display the hi-res screenshot inline via `show <alias|screenId>` → `MEDIA:<screenshotUrl>`. See "Image Delivery" section.
6. **Iteration > perfection** — Follow the Anchor → Inject → Tune → Fix loop. Define what must NOT change in every edit prompt.
7. **One prompt = one thing** — Never combine multiple components or screens in one prompt.
8. **Default values:** `generate` defaults to `--device desktop`. `--model` uses SDK default (pro). Explicit: `--count 3`, `--range explore`. `edit` and `variants` inherit device from the source screen.
9. **State awareness** — Before asking the user for screen or project IDs, ALWAYS read `latest-screen.json` first. If it has a recent entry, use that projectId/screenId. Only ask if no state exists or the user explicitly switches context.
10. **Figma export** — Manual: open Stitch UI → "Copy to Figma" → paste in Figma. CLI can export HTML which also pastes into Figma
11. **Hub-first for multi-screen concepts** — For multi-screen concepts, always define a hub screen first, then derive further screens via edit — never fresh generate.

---

## Image Delivery (MANDATORY after every generate/edit/variants)

The local `screen.png` in `runs/` is only a low-res thumbnail (~168×512px). Full-resolution images come from the Stitch API via `screenshotUrl`.

### How it works

The `show` command accepts an alias OR a raw screen ID and returns live API data with a hi-res screenshot URL (`=w780` suffix appended):

```bash
# By alias
node scripts/stitch.mjs show concept-a
# By screen ID (no alias needed)
node scripts/stitch.mjs show bcde81e368e24edbabd6213d9dc17b3b
# → { "screenshotUrl": "https://lh3.googleusercontent.com/...=w780", ... }
```

### Agent workflow for image display

After every generate/edit/variants:
1. **With alias** (preferred): run `show <alias>` → extract `screenshotUrl` from JSON → `MEDIA:<url>`
2. **Without alias**: run `show <screenId>` (accepts raw screen IDs too) → same flow
3. **Last resort**: get `screenshotUrl` from `runs/<dir>/result.json`, append `=w780`, display via `MEDIA:<url>`

```
MEDIA:https://lh3.googleusercontent.com/...=w780
```

### URL size suffixes

Google's `lh3.googleusercontent.com` URLs support size parameters:
- `=w780` — full mobile design width (default from `show`)
- `=w1440` — full desktop design width
- `=s2000` — max 2000px on longest side
- No suffix → thumbnail only (~168px wide)

## Sketch-to-Design Workflow

Stitch interprets hand-drawn sketches and wireframes well. The SDK has no image upload — but the workflow is:
1. User uploads sketch in Stitch Web UI (stitch.withgoogle.com)
2. User tells the agent: "I uploaded a sketch called [title]" (or just "the sketch I just uploaded")
3. Agent runs `info <project-id>` → finds the screen by title in `list_screens`
4. Agent uses `edit` or `variants` on that screen to refine it

## Limitations

- **No image upload via SDK** — Sketches/screenshots must be uploaded in Stitch Web UI first, then refined via the skill
- **Models:** `pro` (Gemini 3.1 Pro) and `flash` (Gemini 3.0 Flash). "Redesign/NanoBanana" from the Web UI = `variants --range reimagine`
- **Full-screen bias** — Stitch defaults to generating complete layouts. Must be explicitly overridden for component work (see Core Rules).
- **Content hallucination** — Stitch adds unrequested copy, labels, badges. Always have the user review generated content.
- **Long operations** — generate/edit/variants take 1-5 minutes. Connection drops are handled automatically via recovery polling (generate/edit retry via `list_screens` newest; variants use delta-based recovery by comparing screen lists before and after the call)

## Flags Reference

| Flag | Commands | Values | Default |
|---|---|---|---|
| `--device` | `generate`, `edit`, `variants` | `desktop`, `mobile`, `tablet`, `agnostic` | `desktop` for `generate`; inherited from source for `edit`/`variants` |
| `--model` | `generate`, `edit`, `variants` | `pro`, `flash` | SDK default (pro) |
| `--count` | `variants` | `1`–`5` | `3` |
| `--range` | `variants` | `refine`, `explore`, `reimagine` | `explore` |
| `--aspects` | `variants` | `layout`, `color_scheme`, `images`, `text_font`, `text_content` | all |
| `--project` | all | project ID | from `latest-screen.json` |
| `--design-system` | `generate`, `edit`, `variants` | design system name/slug | — |

**Note on `--design-system`:** Stitch supports native Design Systems (`create_design_system`), but the SDK does not yet allow linking them to generate/edit calls. `--design-system` is a workaround that loads `design-systems/<name>.md` from this skill folder and appends that content to your prompt. It does not accept arbitrary file paths. Once the SDK supports `design_system_id` in generate/edit, this flag will become obsolete.
