---
name: widget
description: Create, update, hide, show, list, and delete Übersicht desktop widgets on macOS. Use this skill whenever the user asks for desktop widgets, desktop gadgets, or widgets.
argument-hint: "[operation, e.g. add a clock / hide the pomodoro / list all widgets]"
allowed-tools: Bash(bash *), Bash(cp *), Bash(mv *), Bash(rm *), Bash(ls *), Write, Edit
---

# WidgetDesk Skill

## Environment
- Widget directory: `~/Library/Application Support/Übersicht/widgets/`
- Template directory: `~/.claude/skills/widget/templates/` after install, or `.claude/skills/widget/templates/` inside this repo
- Host requirement: Übersicht is installed and available at `/Applications/Übersicht.app` or `/Applications/Uebersicht.app`

## First Step
- When working inside a WidgetDesk repo clone, run `bash scripts/setup.sh` first
- `scripts/setup.sh` is the default entrypoint: it installs missing host dependencies, starts Übersicht, prepares the widget directory, installs the skill, and verifies the result
- Use `bash scripts/setup.sh --check` only when the user explicitly wants a dry-run check or when you are diagnosing an installation problem
- Use `bash ~/.claude/skills/widget/scripts/doctor.sh` only for a fast post-install health check
- After setup, use the installed skill path under `~/.claude/skills/widget/`

## Reference Files
- Reusable implementation patterns: [patterns.md](patterns.md)
- Host management scripts: `scripts/` for setup, starting Übersicht, checking the environment, installing widgets, and listing widgets

---

## Hard Constraints

### 1. Layout
- All widgets should default to `position: fixed`
- Any bottom-aligned widget must keep `bottom >= 90px`
- Default edge spacing is `40px`
- Default width should stay within `140px` to `360px`
- Default height should stay within `48px` to `220px`
- Only exceed these dimensions when the user explicitly asks for a large widget

### 2. Interaction
- Display-only widgets should default to `pointer-events: none`
- Only enable interaction when the widget truly needs clicking, dragging, or text input
- Interactive controls must stay easy to hit
- Avoid complex multi-step desktop interactions by default

### 3. Refresh
- Command-driven widgets should normally refresh between `1000ms` and `600000ms`
- Refresh below `1000ms` only for clocks or clearly time-sensitive UI
- Pure frontend widgets should use `refreshFrequency = false`
- Avoid high-frequency network requests

### 4. Implementation
- Use lowercase kebab-case filenames
- Prefer existing templates and `patterns.md` before inventing new structure
- Prefer built-in macOS capabilities over extra dependencies
- Do not hardcode secrets
- Keep widgets single-file by default unless the user explicitly asks for more complexity

### 5. Visual Style
- Keep the style consistent, restrained, and macOS-like
- Default to dark translucent cards
- Recommended corner radius: `14px` to `20px`
- Prefer `SF Pro Display` and `SF Mono`
- Keep motion short, light, and purposeful
- Do not invent a brand-new visual language for every widget

---

## Operations

```bash
# First-time setup inside this repo
bash scripts/setup.sh
bash scripts/setup.sh --check

# Fast post-install health check
bash ~/.claude/skills/widget/scripts/doctor.sh

# Start Übersicht
bash ~/.claude/skills/widget/scripts/start-uebersicht.sh

# Install or update a template widget
bash ~/.claude/skills/widget/scripts/install-widget.sh \
  ~/.claude/skills/widget/templates/clock.jsx

# List installed widgets
bash ~/.claude/skills/widget/scripts/list-widgets.sh

# Write a brand-new custom widget
cat > ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx << 'EOF'
{widget_code}
EOF

# Hide a widget without deleting it
mv ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx \
   ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx.disabled

# Show a hidden widget
mv ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx.disabled \
   ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx

# Delete a widget
rm ~/Library/Application\ Support/Übersicht/widgets/{name}.jsx
```

Prefer the `scripts/` helpers for host operations. Only write raw widget files directly when creating or replacing actual JSX content.

When the user asks for a standard widget that already exists as a built-in template, do not rewrite it from scratch. Run `scripts/setup.sh` if needed, then install the matching template.
Do not install or copy any widget file until `scripts/setup.sh` has completed successfully and the host app is available.

---

## Widget Format

```jsx
// Optional shell command. stdout is passed into render as output.
export const command = "date '+%H:%M:%S'"

// Refresh frequency in milliseconds. Pure frontend widgets should use false.
export const refreshFrequency = 1000

// CSS positioning. Use position: fixed.
export const className = `
  position: fixed;
  bottom: 90px;
  right: 40px;
`

// render receives { output, error }
export const render = ({ output }) => {
  return <div>{output?.trim()}</div>
}
```

---

## Required Rules

### Rule 1: Never import React from `react`
```jsx
// Bad
import { useState } from 'react'

// Good
import { React } from 'uebersicht'
```

### Rule 2: Never call hooks directly inside `render`
```jsx
// Bad
export const render = () => {
  const [n, setN] = React.useState(0)
}

// Good
const Widget = () => {
  const { useState } = React
  const [n, setN] = useState(0)
  return <div>{n}</div>
}

export const render = () => <Widget />
```

### Rule 3: Never return a function from a state updater
```jsx
// Bad
setRemaining(r => {
  if (r <= 1) return p => p === 'work' ? BREAK : WORK
})

// Good
useEffect(() => {
  if (remaining !== 0) return
  setPhase(p => p === 'work' ? 'break' : 'work')
  setRemaining(p => p === 'work' ? BREAK : WORK)
}, [remaining])
```

---

## Position Cheatsheet

| Position | CSS |
|----------|-----|
| Bottom right | `bottom: 90px; right: 40px;` |
| Bottom left | `bottom: 90px; left: 40px;` |
| Top right | `top: 40px; right: 40px;` |
| Top left | `top: 40px; left: 40px;` |

---

## Built-In Templates

| File | Purpose | Default Position |
|------|---------|------------------|
| `clock.jsx` | Clock and date | Bottom right |
| `horizon-clock.jsx` | Alternate horizontal clock | Bottom right |
| `pomodoro.jsx` | Pomodoro timer | Bottom left |
| `now-playing.jsx` | Apple Music now playing | Bottom center |
| `system-stats.jsx` | CPU, memory, battery | Top right |
| `weather-canvas.jsx` | Animated weather card | Top left |
| `git-pulse.jsx` | Local Git activity heatmap | Top right |
| `memo-capsule.jsx` | Local quick-note capsule | Top center |
| `volume-knob.jsx` | System volume control knob | Right side |
| `tap-counter.jsx` | Simple interactive counter with persisted local state | Bottom right |

Copy a template directly when it already matches the request, or use it as the starting point for a custom widget.

---

## Style Baseline

```css
background: rgba(8, 12, 20, 0.72);
backdrop-filter: blur(24px);
-webkit-backdrop-filter: blur(24px);
border-radius: 18px;
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35);
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
color: rgba(255, 255, 255, 0.92);
```

Add this for display-only widgets:

```css
pointer-events: none;
```

---

## Useful macOS Shell Commands

```bash
date '+%H:%M:%S'
date '+%Y年%-m月%-d日 %A'
pmset -g batt | grep -o '[0-9]*%' | head -1
top -l 1 | grep "CPU usage" | awk '{print $3}'
curl -s "wttr.in/?format=%t+%C"
```

Remember to `.trim()` command output before rendering it.
