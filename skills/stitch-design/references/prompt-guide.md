# Stitch Prompt Guide

How to write prompts that get great results from Google Stitch.
This guide is loaded by the agent before every generate/edit/variants call.

---

## 1. How Stitch Thinks

**Stitch generates full screens, not components.**
Its strongest tendency is to build a complete application layout — sidebar, header, navigation, content — even when you only ask for a button. Every prompt must actively counteract this when you want isolated components.

**Stitch is an ideation tool, not a production tool.**
Use it to answer "What could this look like?" — not "Build me the final thing." Final polish, brand consistency, and integration into existing interfaces happen in Figma or the component library.

**Stitch interprets sketches well.**
Upload a hand-drawn wireframe or screenshot in the Stitch Web UI, then use `edit` via the skill to refine it. The skill finds the uploaded screen by title via `list_screens`.

---

## 2. The Prompt Framework

Every good Stitch prompt has four layers. If you leave one out, Stitch fills the gap with generic defaults — that's where "AI slop" comes from.

### Layer 1: Context (Who & What)
What kind of app/site? Who is the audience?

> "B2B estate management platform" triggers different design choices than "children's game."

- Industry/domain: SaaS, e-commerce, fintech, healthcare, portfolio site
- Audience: enterprise users, consumers, developers, creative professionals
- App reference shortcuts: "Like Linear's dashboard" or "Airbnb-style search cards"

### Layer 2: Structure (Layout & Components)
The spatial blueprint. Don't let Stitch guess — it will default to single-column stack.

**Page structure:** sidebar navigation, top navigation bar, split layout, bento grid, masonry layout, card grid, hero section with overlay, sticky header, full-bleed header

**Components:** metric card, KPI card with sparkline, data table, form with labels, multi-step form, tab navigation, breadcrumb, search bar, filter chips, progress bar, donut chart, avatar group, badge, status indicator, empty state with illustration

### Layer 3: Aesthetic (Visual Tone & Style)
The most powerful lever. Use precise design vocabulary — vague words produce vague results.

**Style keywords and what they trigger:**

| Keyword | What Stitch generates |
|---|---|
| `minimal` / `clean` | Lots of whitespace, restrained palette, simple geometry |
| `editorial` / `magazine-style` | Large typography, dramatic whitespace, museum-curatorial feel |
| `brutalist` / `neobrutalist` | Thick black borders, clashing colors, hard shadows, monospaced type |
| `glassmorphism` | Frosted translucent cards over colorful backgrounds, blur effects |
| `neumorphism` | Soft extruded surfaces, subtle inner/outer shadows |
| `dark mode` | Dark backgrounds with light text, often paired with accent colors |
| `premium` / `luxury` | Restrained palette, serif typography, generous spacing |
| `playful` / `consumer` | Rounded shapes, bright colors, friendly illustrations |

**Vintage vs. Retro** — these trigger different outputs:
- `vintage` → texture, paper grain, serif type, aged feel (19th-century cookbook)
- `retro` → modern homage to past era (80s synthwave, pixel art, neon)

**Color directions:** monochromatic, neutral with accent, vibrant on dark, pastel, muted/earthy, or specific: "indigo accent", "emerald green", "warm amber"

**Typography:** large headline, display typography, oversized numbers, compact/dense text, monospace data, tabular numbers

**Density:** generous whitespace / airy layout, compact / information-dense / tight spacing, centered with max-width, full-width fluid

### Layer 4: Constraints (Rules & Format)
What the output must look like and what it must NOT do.

**Always specify:**
- Device: desktop (1440px), mobile (375px), tablet (768–1024px)
- Output format: full screen vs. isolated component on neutral background
- Width if relevant for component isolation

**Always include when generating components:**
> "Design a single standalone UI component — do NOT generate a full application screen or layout. Show it isolated on a neutral background, like a component in a design system."

**Always include for text visibility:**
> "Make sure all text is fully visible — do not truncate any labels or text with ellipsis."

---

## 3. Patterns That Work

### Isolated component generation
Best results come from generating one component at a time on a neutral background. This avoids the full-screen tendency.

### Multiple states side by side
Show variants of the same component in one output:
> "Show 2 variants side by side: VARIANT A — collapsed state with summary only, VARIANT B — expanded state showing all details"

More efficient than separate prompts and makes comparison easy.

### 3-variant mode for exploration
Use `variants` when the visual direction is still open. Skip it when content is locked and variation adds no value.

### Sequential wizard steps
Generate each step individually, using the previous step as base:
> "Use the existing Step 2 screen as the base. The following elements must stay exactly identical: [header, sidebar, progress indicator, page title]. Change ONLY these elements: [form content, step number, CTA label]."

Without explicit constraints, Stitch will change headers, titles, and layout between steps.

### Sketch-to-design workflow
Upload a sketch or wireframe in the Stitch Web UI. Then tell the agent:
> "I uploaded a sketch called [title]. Edit it to [desired changes]."

The skill finds the screen by title and applies edits via the API.

---

## 4. Anti-Patterns — What NOT to Do

### ❌ Adding a component to an existing screenshot
Do NOT upload a screenshot and ask Stitch to add something to it. Stitch regenerates the entire screen, losing brand consistency and layout details.
→ **Instead:** Generate the component in isolation, integrate in Figma.

### ❌ Multi-screen in one prompt
Multiple screens in one prompt = broken theming, incomplete outputs, errors.
→ **Rule:** One prompt = one screen or one component.

### ❌ NanoBanana/Reimagine for small changes
Reimagine mode (`variants --range reimagine`) redesigns everything. It's a sledgehammer, not a scalpel.
→ **Use for:** Full visual overhauls
→ **Don't use for:** Adding features or adjusting individual components

### ❌ Trusting generated content blindly
Stitch invents copy, subtexts, badges, status labels that weren't requested. Always review generated content before using it.

### ❌ Long prompts (>5000 chars)
Stitch truncates or omits elements from very long prompts. Keep it focused — one component, clear constraints, iterate.

---

## 5. The Iteration Loop

Stitch works best with iterative refinement, not perfect-first-try prompts.

**Step 1 — Anchor:** Generate the base screen or component.
**Step 2 — Inject:** Add specific elements: "Add a bottom nav bar with icons for Home, Search, Profile."
**Step 3 — Tune:** Adjust visual details: "Make buttons fully rounded, switch to a warmer palette."
**Step 4 — Fix:** Correct drift: "The header changed — revert to the original. Keep the title 'Dashboard' exactly as it was."

### The Golden Rule of Iteration
**Define what must NOT change, not just what should change.**
Stitch aggressively reinterprets unchanged elements. List every element that must stay identical:
> "Keep the following EXACTLY as they are: sidebar width, header layout, color scheme, font family. Only change the main content area."

### Design system reinforcement
In longer sessions, Stitch drifts from established styles. Add to every prompt:
> "Use the existing design system established in this project. Do not create new styles."

---

## 6. Prompt Transformations

| Weak | Strong |
|---|---|
| "A login page" | "Minimal login page: centered card on dark charcoal background, email + password fields, 'Remember me' checkbox, purple gradient CTA, desktop" |
| "A dashboard" | "SaaS analytics dashboard: collapsible sidebar 240px, 4 KPI cards (revenue/MRR/users/churn) with sparklines, area chart main area, dark mode, desktop" |
| "Make it look better" | "Increase whitespace between cards, switch background to #0f0f0f, use teal accent (#0d9488), remove card borders, increase heading font size" |
| "A settings page" | "Settings page: grouped sections (Profile, Notifications, Security, Billing), vertical tab nav on left, form inputs with floating labels, light mode, desktop" |
| "Add a sidebar" | "Design a single standalone sidebar component: 240px wide, dark background, logo top, nav items with icons, active state highlighted, user avatar at bottom. Isolated on neutral background." |

---

## 7. Edit Prompts

Be **specific and surgical:**

✅ "Change sidebar background to #1a1a1a, add hover states to nav items"
✅ "Replace the data table with a card grid layout, keep the header unchanged"
✅ "Make the CTA button 48px height, use gradient from indigo-500 to violet-500"

❌ "Make it nicer" — too vague, Stitch reinterprets everything
❌ "Redesign everything" — use `generate` or `variants --range reimagine` instead

---

## 8. Variants Prompts

**Refine** (`--range refine`): Small targeted adjustments
> "Tighten card padding, reduce font size by one step, make the palette more muted"

**Explore** (`--range explore`): Direction shifts
> "Explore a light mode version with warm earth tones"
> "Try a more editorial layout with larger typography"

**Reimagine** (`--range reimagine`): Complete concept change
> "Reimagine as a terminal-style dark interface with monospace type"
> "Reimagine with a brutalist editorial aesthetic"

**Aspects** (combine with any range): `LAYOUT`, `COLOR_SCHEME`, `IMAGES`, `TEXT_FONT`, `TEXT_CONTENT`
> `variants --range explore --aspects COLOR_SCHEME,TEXT_FONT`

---

## 9. Model Selection

| Task | Model | Flag |
|---|---|---|
| Component generation | Gemini 3.1 Pro | `--model pro` |
| Iterative screen refinement | Gemini 3.1 Pro | `--model pro` |
| Full interface redesign | Reimagine mode | `variants --range reimagine` |
| Fast layout exploration | Gemini 3.0 Flash | `--model flash` |

---

## 10. Recommended Workflow

1. **Establish design system** — Define or extract colors, typography, component styles before generating.
2. **Generate components in isolation** — One component per prompt, neutral background.
3. **Use 3-variant mode** for components where visual direction is open.
4. **Review and select** — Evaluate hierarchy, tone, fit with existing interface.
5. **Export to Figma** — Paste the variant and integrate manually.
6. **Iterate on states** — Use the selected component as base for additional states (collapsed → expanded, empty → filled).
7. **Generate wizard steps sequentially** — Each step uses the previous as base, with explicit constraints on what stays unchanged.

---

## 11. Known Limitations

- **Image upload only via Web UI** — The SDK/API only accepts text prompts. Upload sketches in the Stitch Web UI first, then use the skill to edit/refine.
- **Full-screen bias** — Stitch defaults to generating complete layouts. Must be explicitly overridden for component work.
- **Content hallucination** — Stitch adds unrequested copy, labels, badges. Always review.
- **Theming drift** — Brand colors and typography can shift between sessions, even with a design system. Check every output.
- **Hanging generations** — Outputs sometimes hang indefinitely. The skill handles this with recovery polling, but timeouts can occur.
- **Max ~5 screens per project** — Stitch Web UI limits projects to approximately 5 screens.
