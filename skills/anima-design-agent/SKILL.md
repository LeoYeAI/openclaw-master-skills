---
name: anima
description: "Turns ideas into live, full-stack web applications with editable code, built-in database, user authentication, and hosting. Anima is the design agent in the AI swarm, giving agents design awareness and brand consistency when building interfaces. Three input paths: describe what you want (prompt to code), clone any website (link to code), or implement a Figma design (Figma to code). Also generates design-aware code from Figma directly into existing codebases. Triggers when the user provides Figma URLs, website URLs, Anima Playground URLs, asks to design, create, build, or prototype something, or wants to publish or deploy."
mcpServers:
  - anima
compatibility: "Works via MCP server (HTTP transport) or Anima CLI. For headless environments, requires an ANIMA_API_KEY."
homepage: "https://github.com/AnimaApp/mcp-server-guide"
metadata: {"clawdbot":{"emoji":"🎨","requires":{"env":["ANIMA_API_KEY"]},"primaryEnv":"ANIMA_API_KEY"},"author":"animaapp","version":"1.1.0"}
---

# Design and Build with Anima

## Overview

Anima is the design agent in your AI coding swarm. This skill gives agents design awareness and the ability to turn visual ideas into production-ready code.

There are **two distinct paths** depending on what you're trying to do:

### Path A: Create & Publish (Full App Creation)

Build complete applications from scratch. No local codebase needed. Anima handles everything: design, code generation, scalable database, and hosting. You go from idea to live URL in minutes.

This path is powerful for **parallel variant creation**. Generate multiple versions of the same idea with different prompts, all at the same time. Pick the best one, then open the playground URL to keep refining. All without writing a line of code or managing infrastructure.

**Create Anima Playgrounds by:** Prompt, Clone URL, Figma URL

**What you get:**
- A fully working application in an Anima Playground
- The ability to generate multiple variants in parallel and compare them
- No tokens wasted on file scanning, dependency resolution, or build tooling
- Scalable database already connected
- Scalable hosting when you publish

### Path B: Integrate into Codebase (Design-Aware Code Generation)

Pull design elements and experiences from Anima into your existing project. Use this when you have a codebase and want to implement specific components or pages from a Figma design url or an existing Anima Playground.

**Flows:** Figma URL to Code (codegen), Anima Playground to Code

**What you get:**
- Generated code from Anima playgrounds designs adapted to your stack
- Precise design tokens, assets, and implementation guidelines

---

## Prerequisites

- Anima MCP server must be connected and accessible — or use the Anima CLI as an alternative
- User must have an Anima account (free tier available)
- For Figma flows: Figma account connected during Anima authentication

## Important: Timeouts

Anima's `playground-create` tool generates full applications from scratch. This takes time:

- **p2c (prompt to code):** Typically 3-7 minutes
- **l2c (link to code):** Typically 3-7 minutes
- **f2c (Figma to code):** Typically 2-5 minutes
- **playground-publish:** Typically 1-3 minutes

**Always use a 10-minute timeout** (600000ms) for `playground-create`, `playground-publish`, and CLI calls. Default timeouts will fail.

## Setup

Use the Anima CLI (`npx @animaapp/cli`) for all operations. CLI examples are shown throughout this guide. See the [CLI documentation](https://github.com/AnimaApp/anima-cli) for authentication setup.

If the Anima MCP server is connected, MCP tools can also be used. See the [MCP setup guide](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima-skill-references/setup.md) for details.

---

## Choosing the Right Path

Before diving into tools and parameters, decide which path fits the user's goal.

### When to use Path A (Create & Publish)

- User wants to **build something new** from a description, reference site, or Figma design
- User wants a **live URL** they can share immediately
- No existing codebase to integrate into
- Goal is prototyping, exploring visual directions, or shipping a standalone app

### When to use Path B (Integrate into Codebase)

- User has an **existing project** and wants to add a component or page from Figma
- User wants **generated code files** to drop into their repo, not a hosted app
- User already built something in an Anima Playground and wants to pull the code locally

### Ambiguous cases

| User says | Likely path | Why |
|---|---|---|
| "Implement this Figma design" | **Path B** | "Implement" implies code in their project |
| "Turn this Figma into a live site" | **Path A** (f2c) | "Live site" means they want hosting |
| "Build me an app like this" + URL | **Path A** (l2c) | Clone and rebuild from scratch |
| "Add this Figma component to my project" | **Path B** | "Add to my project" = codebase integration |
| "Clone this website" | **Path A** (l2c) | Clone = capture and rebuild from scratch |
| "Download the playground code" | **Path B** | Wants files locally |

When still unclear, ask: "Do you want a live hosted app, or code files to add to your project?"

---

## From Request to Prompt

Before calling any tool, the agent needs to decide: is this request ready to build, or does it need clarification? And if it's ready, how do you write a prompt that lets Anima shine?

### When to ask vs when to build

**Threshold rule:** Can you write a prompt that includes **purpose**, **audience**, and **3-5 key features**? Yes = build. No = ask.

**Signals to just build:**
- "Build a recipe sharing app where users can upload photos and rate each other's dishes" (clear purpose, audience implied, features named)
- "Clone stripe.com" (unambiguous)
- "Turn this into a live site" + Figma URL (clear intent and input)

**Signals to ask:**
- "Build me a website" (what kind? for whom?)
- "Make something for my business" (what does the business do?)
- "Create an app" (what should it do?)

When you ask, ask everything in **one message**. Don't drip-feed questions. If the user is vague and doesn't want to answer, skip clarification and use [Explore Mode](#explore-mode-parallel-variants) to generate 3 variants instead. Showing beats asking.

### Crafting the prompt

Anima is a design-aware AI. Treat it like a creative collaborator, not a code compiler. Describe the *feel* of what you want, not the pixel-level implementation. Over-specifying with code and hex values **overrides Anima's design intelligence** and produces generic results.

**Include in prompts:** purpose, audience, mood/style, 3-5 key features, content tone.

**Leave out of prompts:** code snippets, CSS values, hex colors, pixel dimensions, font sizes, component library names (use the `uiLibrary` parameter instead), implementation details, file structure.

**Bad (over-specified):**
```
Create a dashboard. Use #1a1a2e background, #16213e sidebar at 280px width,
#0f3460 cards with 16px padding, border-radius 12px. Header height 64px with
a flex row, justify-between. Font: Inter 14px for body, 24px bold for headings.
```

**Good (descriptive):**
```
SaaS analytics dashboard for a B2B product team. Clean, minimal feel.
Sidebar navigation, KPI cards for key metrics, a usage trend chart, and a
recent activity feed. Professional but approachable. Think Linear meets Stripe.
```

## Path A: Create & Publish

### Step A1: Identify the Flow

Determine which flow to use based on what the user provides and what they want.

**User has a text description or idea → p2c**

The most flexible path. Anima designs everything from your description. Best for new apps, prototypes, and creative exploration.

**User has a website URL → l2c**

Use l2c to clone the site. Anima recreates the full site into an editable playground.

**User has a Figma URL → f2c (Path A) or codegen (Path B)**

Two sub-cases:
- **"Turn this into a live app"** or **"Make this a working site"** → f2c (Path A). Creates a full playground from the Figma design
- **"Implement this in my project"** or **"Add this component to my codebase"** → codegen (Path B). Generates code files for integration

**Quick reference:**

| User provides | Intent | Flow | Tool |
|---|---|---|---|
| Text description | Build something new | p2c | `playground-create` type="p2c" |
| Website URL | Clone it | l2c | `playground-create` type="l2c" |
| Figma URL | Make it a live app | f2c | `playground-create` type="f2c" |
| Figma URL | Implement in my project | codegen | `codegen-figma_to_code` (Path B) |

### Step A2: Create

#### Prompt to Code (p2c)

Describe what you want in plain language. Anima designs and generates a complete playground with brand-aware visuals.

**CLI:**
```bash
anima create -t p2c -p "SaaS analytics dashboard for a B2B product team. Clean, minimal feel. Sidebar navigation, KPI cards for key metrics, a usage trend chart, and a recent activity feed. Professional but approachable." --guidelines "Dark mode, accessible contrast ratios"
```

**MCP:**
```
playground-create(
  type: "p2c",
  prompt: "SaaS analytics dashboard for a B2B product team. Clean, minimal feel. Sidebar navigation, KPI cards for key metrics, a usage trend chart, and a recent activity feed. Professional but approachable.",
  framework: "react",
  styling: "tailwind",
  guidelines: "Dark mode, accessible contrast ratios"
)
```

Only `-t` and `-p` are required. Defaults: `--framework react`, `--styling tailwind`, `--language typescript`.

**Parameters specific to p2c:**

| Parameter | Required | Description |
|---|---|---|
| `prompt` | Yes | Text description of what to build |
| `guidelines` | No | Additional coding guidelines or constraints |

**Styling options:** `tailwind`, `css`, `inline_styles`

#### Link to Code (l2c)

Provide a website URL. Anima recreates it as an editable playground with production-ready code.

**CLI:**
```bash
anima create -t l2c -u https://stripe.com/payments --ui-library shadcn
```

**MCP:**
```
playground-create(
  type: "l2c",
  url: "https://stripe.com/payments",
  framework: "react",
  styling: "tailwind",
  language: "typescript",
  uiLibrary: "shadcn"
)
```

Only `-t` and `-u` are required. Defaults: `--framework react`, `--styling tailwind`, `--language typescript`.

**Parameters specific to l2c:**

| Parameter | Required | Description |
|---|---|---|
| `url` | Yes | Website URL to clone |

**Styling options:** `tailwind`, `inline_styles`

**UI Library options:** `shadcn` only

**Language:** Always `typescript` for l2c

#### Figma to Playground (f2c)

Provide a Figma URL. Anima implements the design into a full playground you can preview and iterate on.

**URL format:** `https://figma.com/design/:fileKey/:fileName?node-id=1-2`

**Extract:**
- **File key:** The segment after `/design/` (e.g., `kL9xQn2VwM8pYrTb4ZcHjF`)
- **Node ID:** The `node-id` query parameter value, replacing `-` with `:` (e.g., `42-15` becomes `42:15`)

**CLI** (accepts full Figma URL — extracts file key and node IDs automatically):
```bash
anima create -t f2c --file-key "https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/My-File?node-id=42-15" --ui-library shadcn
```

**MCP:**
```
playground-create(
  type: "f2c",
  fileKey: "kL9xQn2VwM8pYrTb4ZcHjF",
  nodesId: ["42:15"],
  framework: "react",
  styling: "tailwind",
  language: "typescript",
  uiLibrary: "shadcn"
)
```

Only `-t` and `--file-key` are required. The CLI parses Figma URLs and normalizes node IDs automatically. Defaults: `--framework react`, `--styling tailwind`, `--language typescript`.

**Parameters specific to f2c:**

| Parameter | Required | Description |
|---|---|---|
| `fileKey` | Yes | Figma file key from URL |
| `nodesId` | Yes | Array of Figma node IDs (use `:` not `-`) |

**Styling options:** `tailwind`, `plain_css`, `css_modules`, `inline_styles`

**UI Library options:** `mui`, `antd`, `shadcn`, `clean_react`

### Step A3: Publish

After creating a playground, deploy it to a live URL.

**CLI:**
```bash
anima publish abc123xyz
```

**MCP:**
```
playground-publish(
  sessionId: "abc123xyz",
  mode: "webapp"
)
```

The response includes the live URL for the published app.

### Explore Mode: Parallel Variants

This is Path A's secret weapon. When a user says "build me X" or "prototype X", generate multiple interpretations in parallel, publish all of them, and return live URLs for comparison.

**Workflow:**

1. **Generate 3 prompt variants** from the user's idea. Each takes a different creative angle:
   - Variant 1: Faithful, straightforward interpretation
   - Variant 2: A more creative or opinionated take
   - Variant 3: A different visual style or layout approach

2. **Launch all 3 `playground-create` calls in parallel** (one per variant, type p2c)

3. **As each one completes**, immediately call `playground-publish` (mode webapp)

4. **Return all 3 live URLs** so the user can pick a favorite or ask for refinements. Optionally, if you have a screenshot tool available, capture each page to show in the chat.

**Timing:** All 3 variants generate in parallel, so total wall time is roughly the same as one (~5-7 minutes creation + 1-3 minutes publishing). Expect results within ~10 minutes.

**Tips for good variant prompts:**
- Keep the core idea identical across all three
- Vary the visual approach: e.g., "minimal and clean", "bold and colorful", "enterprise and professional"
- Add specific guidelines to each variant to differentiate them
- If the user mentioned a reference site or style, incorporate it into one variant
- Follow the [prompt crafting principles](#crafting-the-prompt) above: describe mood and purpose, not implementation details

---

## Path B: Integrate into Codebase

### Step B1: Identify the Flow

| User provides | Flow | Tool |
|---|---|---|
| Figma URL + wants code in their project | Figma to Code | `codegen-figma_to_code` |
| Anima Playground URL + wants code locally | Download | `project-download_from_playground` |

### Step B2: Match Project Stack to Tool Parameters

| Project stack | Parameter | Value |
|---|---|---|
| React | `framework` | `"react"` |
| No React | `framework` | `"html"` |
| Tailwind | `styling` | `"tailwind"` |
| CSS Modules | `styling` | `"css_modules"` |
| Plain CSS | `styling` | `"plain_css"` |
| TypeScript | `language` | `"typescript"` |
| MUI | `uiLibrary` | `"mui"` |
| Ant Design | `uiLibrary` | `"antd"` |
| shadcn | `uiLibrary` | `"shadcn"` |

### Step B3: Generate Code

#### Figma to Code (direct implementation)

**CLI** (writes files directly to disk):
```bash
anima codegen --file-key "https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/My-File?node-id=42-15" -o ./components --ui-library shadcn
```

**MCP:**
```
codegen-figma_to_code(
  fileKey: "kL9xQn2VwM8pYrTb4ZcHjF",
  nodesId: ["42:15"],
  framework: "react",
  styling: "tailwind",
  language: "typescript",
  uiLibrary: "shadcn",
  assetsBaseUrl: "./assets"
)
```

**CLI** (writes files directly to disk):
```bash
anima codegen --file-key "https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/My-File?node-id=42-15" -o ./components --ui-library shadcn
```

Only `--file-key` is required. Defaults: `--framework react`, `--styling tailwind`, `--language typescript`, `-o ./anima-codegen-output`.

Use the response fields (snapshots, assets, guidelines) as design reference when implementing.

#### Download Playground to Local Files

**CLI:**
```bash
anima download https://dev.animaapp.com/chat/abc123xyz -o ./my-project
```

**MCP:**
```
project-download_from_playground(sessionId: "abc123xyz")
```

The CLI accepts playground URLs directly and extracts the session ID automatically.

---

## CLI & MCP Quick Reference

| Action | CLI Command | MCP Tool |
|--------|-------------|----------|
| Prompt to Code | `anima create -t p2c -p "..."` | `playground-create` type="p2c" |
| Link to Code | `anima create -t l2c -u <url>` | `playground-create` type="l2c" |
| Figma to Playground | `anima create -t f2c --file-key <key>` | `playground-create` type="f2c" |
| Publish | `anima publish <sessionId>` | `playground-publish` |
| Figma to Code | `anima codegen --file-key <key> -o ./out` | `codegen-figma_to_code` |
| Download | `anima download <url> -o ./out` | `project-download_from_playground` |

**When to use CLI vs MCP:**
- **CLI**: Preferred — lightweight, no MCP setup needed, works in headless environments
- **MCP**: Alternative when Anima MCP server is already connected

**CLI defaults** (all optional): `--framework react`, `--styling tailwind`, `--language typescript` (when react). Only the type flag and the type-specific input (prompt, url, or file-key) are required.

---

## Additional References

- [Setup guide](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima-skill-references/setup.md)
- [MCP Tools Reference](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima-skill-references/mcp-tools.md)
- [Examples](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima-skill-references/examples.md)
- [Troubleshooting](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima-skill-references/troubleshooting.md)
- [Anima MCP Documentation](https://docs.animaapp.com/docs/integrations/anima-mcp)
