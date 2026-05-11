# Extract Design

A Claude Code skill for extracting a webpage's design language into a reusable HTML style reference file. Perfect for learning design systems, creating AI-generated pages in a specific style, or building design token systems.

## What This Does

**Extract Web Style** analyzes any webpage and produces a universal style specimen HTML — not a clone, but an extraction of the underlying design system. It captures:

- **Primitive tokens** — raw colors, fonts, sizes, spacing
- **Semantic tokens** — `--color-text-primary`, `--color-bg-page`, etc.
- **Component archetypes** — buttons, cards, inputs, navigation patterns
- **Interaction rules** — hover states, transitions, animations
- **Theme variants** — light/dark mode behavior

The output is a self-contained HTML file that another AI can read and use to generate new pages in the same visual style.

## Key Features

- **Style System Extraction** — captures the design DNA, not just DOM copy
- **Semantic Token Naming** — abstracts raw values into meaningful roles
- **Dark Mode Support** — extracts and validates both light and dark themes
- **Component Archetypes** — compresses similar components into reusable patterns
- **Signature Animation Detection** — identifies brand-specific motion patterns
- **Machine-Readable Manifest** — JSON design manifest embedded for AI consumption

## Installation

### For Claude Code Users

```bash
git clone https://github.com/VintLin/extract-design.git ~/.claude/skills/extract-design
```

Then use it by typing `/extract-design` in Claude Code.

### Manual Copy

```bash
git clone https://github.com/VintLin/extract-design.git ~/.claude/skills/extract-design
```

## Usage

### Extract a Website's Design

```
/extract-design

> "Extract the design system from https://factory.ai"
```

The skill will:
1. Analyze the webpage's visual system
2. Extract typography, colors, spacing, motion
3. Identify component patterns and states
4. Generate a universal style specimen HTML
5. Save it to `assets/theme/<site-name>-style-specimen.html` inside the skill directory

### Create Pages in the Extracted Style

```
/extract-design

> "Use the factory.ai design system to create a landing page for my open-source project"
```

The skill will read the specimen file and generate new pages using the same design language.

## Output Structure

Each extraction produces:

| File | Purpose |
|------|---------|
| `SKILL.md` | The extraction skill itself |
| `scripts/extract-styles.py` | Built-in Playwright extraction script |
| `assets/theme/*-style-manifest.json` | Structured style manifest (JSON) |
| `assets/theme/*-style-specimen.html` | Universal style specimen HTML |
| `references/` | Supporting documentation and templates |

## Architecture

This skill follows a **progressive disclosure** design:

| File | Purpose | Loaded When |
|------|---------|-------------|
| `SKILL.md` | Core workflow and extraction rules | Always (skill invocation) |
| `assets/theme/*.html` | Extracted design references | When generating pages in that style |

The skill prioritizes:
- **Abstraction over fidelity** — same design language, not same page
- **Semantic naming** — `--color-text-primary` not `--color-base-900`
- **State completeness** — hover, focus, active, disabled states
- **Theme awareness** — proper dark mode token mapping

## Philosophy

1. **Extract the system, not the page.** A good extraction should let you recreate countless pages in the same style.

2. **Names should explain purpose.** Raw hex values mean nothing. `--color-accent` means everything.

3. **States matter as much as defaults.** A button without hover states isn't a complete component.

4. **Themes are first-class citizens.** Light and dark modes need equal attention.

5. **Signatures make it memorable.** Brand-specific animations (like Factory.ai's stripe overlay) are worth preserving.

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- Python 3.8+
- Playwright: `pip install playwright && playwright install chromium`
- Web access (for fetching target pages)

## Credits

Created with Claude Code.

## License

MIT — Use it, modify it, share it.
