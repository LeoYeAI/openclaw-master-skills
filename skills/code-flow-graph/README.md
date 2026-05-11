# Code Flow Graph

An interactive HTML node-graph viewer skill that visualizes codebase structure, entry-point call chains, and data type flows.

![Catppuccin Mocha Theme](https://img.shields.io/badge/theme-Catppuccin%20Mocha-b4befe?style=flat-square) ![Standalone HTML](https://img.shields.io/badge/output-standalone%20HTML-a6e3a1?style=flat-square) ![No Dependencies](https://img.shields.io/badge/dependencies-none-89b4fa?style=flat-square)

## Example — [AuroraView](https://github.com/loonghao/auroraview) Analysis

Below are screenshots from analyzing the [AuroraView](https://github.com/loonghao/auroraview) Rust WebView project:

### Full Call Chain Overview

![AuroraView Full Call Chain](images/auroraview_full_call_chain.jpg)

*Complete `AuroraView::new()` call chain with all modules, IPC handlers, lifecycle management, and WebView builder — right-side panel shows the interactive call chain detail.*

### Function Signature Tooltips

![AuroraView Signature Tooltip](images/auroraview_signature_tooltip.jpg)

*Hover over any function to see its full signature and source location. Click to highlight all connected relationships.*

### Entry Point Tracing

![AuroraView Entry Point Tracing](images/auroraview_entry_tracing.jpg)

*Click `show_embedded()` to trace the DCC embedded entry flow — the viewer highlights the active path and dims unrelated nodes.*

### UI Layout Visualization

![UI Layout Visualization](images/example_ui.jpg)

*Interactive widget hierarchy viewer — nested layout boxes with color-coded widget types, resize handles on hover, stack/tab switching, and Ctrl+Z undo. Sidebar shows "🖼️ UI 布局" section for layout views.*

## Features

- **Interactive Node Graph** — Draggable nodes with bezier-curve connections, pan & zoom
- **UI Layout Visualization** — Interactive widget hierarchy viewer for UI projects (Qt, React, etc.); nested layout boxes with resize handles, Ctrl+Z undo, and hover tooltips showing widget class/properties
- **Call Chain Detail Panel** — Click entry-point functions to explore the complete call tree in a right-side panel; each item shows a description explaining what the function does
- **Global Search (Ctrl+K)** — Fuzzy search across ALL diagram pages with cross-diagram navigation
- **Multi-Diagram Support** — Organize views by entry-point call chains, UI layers, data types, and overview
- **Smart Highlighting** — Click any function to highlight its node + all connected relationships; dim everything else
- **Collapsible Children** — Sub-functions collapse/expand with connection redirect to parent
- **Signature Tooltips** — Hover functions to see full signatures, descriptions, detailed explanations, and I/O
- **Click to Copy** — Click any function attr to copy the function name to clipboard with toast notification
- **Undo Layout Moves (Ctrl+Z)** — Undo the last node/group drag operation (up to 50 steps)
- **Position Persistence** — Node positions saved to localStorage per diagram; "Reset Layout" restores defaults
- **Catppuccin Mocha Dark Theme** — Beautiful dark color scheme with type-based semantic colors
- **Group Boxes** — Dashed-border groups with auto-sizing to enclose member nodes; draggable as a unit

## How It Works

The viewer renders two files together:

| File | Purpose |
|------|---------|
| `code_flow_graph.html` | Rendering engine (do not modify) |
| `code_flow_graph_data.js` | Diagram data (generated per-project by your AI assistant) |

Simply place both files in the same directory and open the HTML in a browser.

## Installation

### As an Agent Skill

Copy the entire repository into your AI agent's skills directory:

```
<project>/.skills/code_flow_graph/
  SKILL.md
  example/
    code_flow_graph.html
    code_flow_graph_data.js
  references/
    data_format.md
```

Then ask your AI: *"Visualize the code architecture of this project"* or *"Generate a code graph for this module"*.

The AI will:
1. Analyze the project structure and discover entry points
2. Generate an Overview diagram immediately (no scoping questions)
3. Offer deep-dive options for specific call chains, UI layers, or data types
4. Incrementally append new diagram pages as you select options

### Standalone Usage

You can also use the viewer independently:

1. Copy `example/code_flow_graph.html` to your project
2. Create a `code_flow_graph_data.js` file following the format in `references/data_format.md`
3. Open the HTML file in a browser

## Data Format

See [`references/data_format.md`](references/data_format.md) for the complete data format specification.

## Diagram Types

### Overview Diagram

A **module-level dependency graph** showing one node per major module/class, entry points highlighted with `type: 'entry'`, cross-module connections, and package groups. Always generated first.

### Call-Chain Diagram

Traces the **complete call chain** of one entry function. Nodes are organized left-to-right following execution order. Each function attr includes `sig` (signature tooltip), `desc` (one-line summary), and `detail` (multi-line explanation). The entry function attr includes a `callChain` array for the interactive detail panel.

### UI Signal/Event Diagram

For UI projects (Qt, React, Web, etc.). Uses `widget` type nodes with sections for Widgets, Event Handlers, and Slots. Dashed pink connections link event handlers to business logic.

### Data Type Diagram

Each dataclass/type definition → node with `type: 'data'` (peach color). Fields listed as attrs with type in the `val` field. Connections show how data flows between components:

| Connection Color | Meaning |
|-----------------|---------|
| 🔵 Blue | Data passed as input / output between functions |
| 🟢 Green | Data constructed or returned by a function |
| 🟠 Peach | Data consumed by an external dependency |

## Color Scheme

Uses [Catppuccin Mocha](https://github.com/catppuccin/catppuccin) palette. Color is **automatically assigned by node type**:

| Type | Color | Badge |
|------|-------|-------|
| `entry` | 🟡 Yellow (`#f9e2af`) | ENTRY |
| `class` | 🔵 Blue (`#89b4fa`) | CLASS |
| `module` | 🟢 Green (`#a6e3a1`) | MODULE |
| `function` | 🟣 Mauve (`#cba6f7`) | FUNC |
| `data` | 🟠 Peach (`#fab387`) | DATA |
| `widget` / `QDialog` | 💎 Sapphire (`#74c7ec`) | UI CLASS |
| `slots` | 🩷 Pink (`#f5c2e7`) | SLOTS |

> Nodes with `external: true` are rendered with dashed borders and an `EXT` tag to indicate third-party dependencies.

## Connection Types

All connections render with a **gradient stroke** from transparent at source to full opacity at target, indicating flow direction.

| Color | Style | Meaning |
|-------|-------|---------|
| 🟢 Green (`#a6e3a1`) | Solid | Direct function call |
| 🔴 Red (`#f38ba8`) | Solid | Inheritance / override |
| 🔵 Blue (`#89b4fa`) | Solid | Data flow / return value |
| 🩷 Pink (`#f5c2e7`) | Dashed | Signal / event / callback |
| 🟠 Peach (`#fab387`) | Solid | External dependency call |
| ⚫ Overlay (`#6c7086`) | Solid | Weak reference / optional |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+K` | Open global search |
| `Ctrl+Z` | Undo last layout move (up to 50 steps) |
| `Space + Drag` | Pan the viewport |
| `Scroll` | Zoom in / out |
| `Escape` | Close search / detail panel |
| Click function | Copy function name + highlight connections |
| Click blank area | Clear all highlights |

## Element Mapping

| Code Concept | Graph Element |
|---|---|
| Entry function | NODE (`type: 'entry'`) — ENTRY badge |
| Class / core object | NODE (`type: 'class'`) — CLASS badge |
| Module / package | NODE (`type: 'module'`) — MODULE badge |
| Function group / utility | NODE (`type: 'function'`) — FUNC badge |
| Data type / dataclass | NODE (`type: 'data'`) — DATA badge |
| UI widget / dialog | NODE (`type: 'widget'`) — UI CLASS badge |
| Small helper called once | attr with `children` inside parent node |
| Third-party dependency | NODE with `external: true` — dashed border + EXT tag |
| Direct function call | CONNECTION (solid, gradient toward callee) |
| Signal / event / callback | CONNECTION (dashed, gradient toward target) |

## License

MIT
