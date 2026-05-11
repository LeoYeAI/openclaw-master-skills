# Code Flow Graph Data Format Reference

## Overview

The data file `code_flow_graph_data.js` defines a global `var DIAGRAMS = {};` object. Each key in `DIAGRAMS` is a diagram identifier (sidebar entry). A special `_projectTitle` key can set the sidebar header.

## Top-level Structure

```js
var DIAGRAMS = {};
DIAGRAMS._projectTitle = 'My Project'; // optional sidebar header

DIAGRAMS.module_name = {
  title: 'Module Name — Class Diagram',        // header title
  sub: 'path/to/module.py — description',       // subtitle
  navLabel: 'Module Name',                       // sidebar label
  navSub: 'path/to/module.py',                   // sidebar sublabel
  NODES: [ ... ],
  CONNECTIONS: [ ... ],
  GROUPS: [ ... ],
};
```

## NODES Array

Each node represents a **class**, **module**, **function group**, or **UI component**. Each node object:

```js
{
  id: 'className',                    // unique string, used in CONNECTIONS
  label: 'ClassName',                 // display name (header text)
  type: 'class | module | function | entry | data | QDialog | widget | slots',
  // type determines the badge label on the header (all nodes share 6px rounded shape):
  //   class      → CLASS badge
  //   module     → MODULE badge
  //   function/functions → FUNC badge
  //   entry      → ENTRY badge
  //   data       → DATA badge
  //   QDialog/widget/slots → UI CLASS / SLOTS badge
  // External dependencies use the appropriate type (module/class) with `external: true`.
  external: false,                    // optional — true for third-party dependencies (dashed border + EXT tag)
  // Visual differentiation is via color auto-assigned by type.
  x: 30, y: 60,                       // default position (pixels)
  w: 280,                             // node width (pixels)
  sections: [                         // method/attribute groups
    {
      title: 'Public Methods',        // section header (optional)
      code: 'some code snippet',      // code block (optional, mutually exclusive with attrs)
      attrs: [
        {
          id: 'cls.method_name',      // unique, format: nodeId.attrName — used in CONNECTIONS
          name: 'method_name()',       // display text
          val: '→ returns X',          // right-side value text (optional)
          sig: '<span class="sig-name">method_name</span>(<span class="sig-params">param1, param2=default</span>)\n<span class="sig-return">→ ReturnType</span>',  // optional: hover tooltip HTML showing full signature
          // For typed parameters, use: <span class="sig-type">Type</span> in sig
          desc: '函数功能的一行中文描述',  // optional: Chinese description shown in tooltip and call chain
          detail: '更详细的函数说明，包括：核心处理逻辑、关键步骤、调用的重要函数、副作用、异常处理等。支持多行文本。',  // optional: detailed description shown below desc in tooltip
          io: { input: 'param1: Type — 说明', output: 'ReturnType — 说明' },  // optional: input/output shown in tooltip
          children: [                 // optional: sub-functions called by this function (same file)
            {                         // children are COLLAPSIBLE by default, user can expand via ▶ toggle
              id: 'cls.sub_func',     // same format as parent attr
              name: 'sub_func()',
              sig: '...',             // optional tooltip for child too
            },
          ],
          childrenCollapsed: true,    // optional: default collapsed state (true by default)
          callChain: [                // optional: complete call chain data for detail panel
            {
              id: 'cls.method_name',  // MUST exactly match the target attr's id in the graph (format: NodeId.method_name)
                                      // The viewer uses this id to highlight the corresponding node/attr when clicked.
                                      // If this id doesn't match any attr in the current diagram, click-to-highlight won't work.
              name: 'method_name()',  // display name
              module: 'module.py',    // source module (optional)
              desc: 'One-line description of what the function does',  // description text shown below function name
              sig: 'method_name(param1, param2) → ReturnType',  // plain text signature (legacy, prefer desc)
              external: false,        // true if from external module
              calls: [                // recursive sub-calls
                { id: '...', name: '...', module: '...', desc: '...', calls: [...] },
              ],
            },
          ],
          fieldDetail: {              // optional: field computation detail for data-type attrs
            field: 'field_name',      // field name displayed in the detail panel header
            type: 'FieldType',        // type annotation shown next to field name
            summary: 'One-paragraph description of the field purpose and how it is managed.',
            sources: [                // array of computation/assignment modes (how the field gets its value)
              {
                mode: 'INITIAL',      // mode label (e.g., INITIAL, ON FETCH, ON UPDATE, ON FILTER)
                fn: 'createStore()',   // source function or expression
                steps: [              // ordered list of computation steps
                  'Step 1: describe what happens first',
                  'Step 2: describe the next operation (function names like foo() are auto-highlighted)',
                  'Step 3: final result assignment',
                ],
              },
            ],
          },
        },
      ],
    },
  ],
}
```

### Node CSS Classes (Unified Color Scheme)

### Node Type Visual Styles

All node types share the same **unified shape** (6px rounded corners, 1.5px solid border). Types are distinguished by **color** (auto-assigned by type) and the **badge** on the header bar. Nodes with `external: true` get dashed borders and an `EXT` tag.

| type value | Header Badge |
|-----------|-------------|
| class | CLASS |
| module | MODULE |
| function/functions | FUNC |
| entry | ENTRY |
| data | DATA |
| QDialog/widget | UI CLASS |
| slots | SLOTS |


## CONNECTIONS Array

Each connection is a 4-element or 5-element array:

```js
['sourceAttrId', 'targetAttrId', '#color', dashed]
// or with optional label:
['sourceAttrId', 'targetAttrId', '#color', dashed, 'label text']
```

- `sourceAttrId` / `targetAttrId`: attribute `id` values from NODES (format: `nodeId.attrName`)
- `color`: hex color string for the bezier curve
- `dashed`: `true` for dashed lines (signals/events), `false` for solid (direct calls)
- `label` (optional): text shown at the midpoint of the connection

### Connection Color Conventions

All connections render with a **gradient stroke** that transitions from light (transparent) at the source to full opacity at the target, indicating flow direction (caller → callee, emitter → handler). This provides a clear, static visual indication of data/call direction without arrows or animations.

- `#a6e3a1` (green) — direct function call
- `#f38ba8` (red) — inheritance / override
- `#89b4fa` (blue) — data flow / return value
- `#f5c2e7` (pink) — signal / event / callback
- `#fab387` (peach) — external dependency call
- `#6c7086` (overlay) — weak reference / optional

## GROUPS Array

Each group represents a **folder / module / package**:

```js
{
  id: 'grp-module',                           // unique group id
  label: 'module_name/ (Package)',            // display label
  nodes: ['class1', 'class2'],                // array of node ids in this group
  color: '#89b4fa',                           // border/label color
  bg: 'rgba(137,180,250,0.04)',               // background fill
}
```

## Layout Guidelines

### Positioning — Grid-Aligned Layout

Arrange nodes on an **implicit grid** for a clean, organized appearance:

- **Column-based layout**: Organize nodes into vertical columns following execution flow (left → right: callers → callees). Align all nodes in the same column to the **same x coordinate**.
- **Grid spacing**: Use consistent column width of **320px** (center-to-center) and row spacing of **40px** between node bottom edges and the next node top edge.
- **Starting position**: First column at `x: 30`, first row at `y: 60`.
- **Column assignment**:
  - Column 0 (x: 30): Entry points / root callers
  - Column 1 (x: 350): Direct callees of entry points
  - Column 2 (x: 670): Second-level callees
  - Column 3+ (x: 990, 1310, ...): Deeper calls
- **Vertical alignment within a column**: Stack nodes top-to-bottom with consistent gap. Estimate node height as `80 + (attrCount × 22)` px. Place the next node at `y_previous + estimatedHeight + 40`.
- **External/utility nodes**: Place in the rightmost column or a separate row below (y > 800) to avoid cluttering the main flow.
- **Group-aware placement**: Nodes within the same GROUP should be placed adjacent to each other (same column or adjacent columns) so the group's dashed border stays compact.

### Group Spacing

The auto-layout engine uses the following spacing parameters for groups. When manually placing nodes, follow these values to ensure consistent, compact spacing:

- **INTER_GROUP_GAP**: `20px` — minimum gap between different groups' bounding boxes. Keep this tight to avoid large empty areas between groups.
- **INTRA_GROUP_GAP**: `24px` — vertical gap between nodes within the same group.
- **GROUP_PAD**: `18px` — padding inside the group's dashed border around its member nodes.

Groups should appear tightly packed with uniform spacing. Avoid excessive whitespace between groups — the layout should feel compact and organized rather than scattered.

### Node Sizing

- Standard class: `w: 260-320`
- Small utility: `w: 200-240`
- Large class with many methods: `w: 300-350`

### Node Internal Styling

Section headers inside nodes (e.g., "PUBLIC METHODS", "PRIVATE METHODS") use the `.attr-section` style:

- **Font size**: `9.5px` — large enough to be readable at default zoom
- **Color**: `#7f849c` — a visible mid-gray that stands out from the dark node background while remaining visually subordinate to function names
- **Text transform**: uppercase with `1px` letter-spacing — distinguishes section headers from function attr rows
- Do NOT add glow (`text-shadow`) or other decorative effects to section headers; keep them clean and understated

### For UI-Related Code

When the codebase has a graphical UI (Qt, Web, etc.):

1. Create a dedicated diagram entry for the UI layer
2. Use `widget` type for UI widget/component nodes (renders with `UI CLASS` badge and sapphire blue color — same family as `class` blue but visually distinct)
3. Each UI node's sections should list:
   - Widget structure (buttons, layouts)
   - Event handlers / slots
   - Connected business logic methods (as connections to other class nodes)
4. Connections from UI event handlers to business logic should use dashed pink lines
5. The sidebar entry `navLabel` should indicate it's a UI view (e.g., "UI — MainWindow")

## Complete Minimal Example

```js
var DIAGRAMS = {};
DIAGRAMS._projectTitle = 'MyApp';

DIAGRAMS.core = {
  title: 'Core Module',
  sub: 'src/core/ — business logic',
  navLabel: 'Core',
  navSub: 'src/core/',
  NODES: [
    { id: 'Engine', label: 'Engine', type: 'class', x: 30, y: 60, w: 280, sections: [
      { title: 'Public', attrs: [
        { id: 'Engine.start', name: 'start()' },
        { id: 'Engine.stop', name: 'stop()' },
      ]},
      { title: 'Private', attrs: [
        { id: 'Engine._init', name: '_init_subsystems()' },
      ]},
    ]},
    { id: 'Logger', label: 'Logger', type: 'class', x: 400, y: 60, w: 240, sections: [
      { title: 'Methods', attrs: [
        { id: 'Logger.log', name: 'log(msg)' },
      ]},
    ]},
  ],
  CONNECTIONS: [
    ['Engine._init', 'Logger.log', '#a6e3a1', false],
  ],
  GROUPS: [
    { id: 'g-core', label: 'Core', nodes: ['Engine', 'Logger'], color: '#89b4fa', bg: 'rgba(137,180,250,0.04)' },
  ],
};
```

---

## UI_LAYOUT_VIEWS (Widget Hierarchy Visualization)

An optional global variable that enables the **UI Layout Viewer** mode. When defined in `code_flow_graph_data.js`, the sidebar gains a "🖼️ UI 布局" separator followed by nav items for each layout view. Clicking a layout view switches from the node-graph mode to an interactive nested widget-box tree.

### Top-level Structure

```js
var UI_LAYOUT_VIEWS = {};

UI_LAYOUT_VIEWS.main_window = {
  title: 'MainWindow — 完整布局',              // header title
  sub: 'path/to/main_window.py — QMainWindow', // subtitle
  navLabel: '🏠 MainWindow',                   // sidebar label
  navSub: '主窗口完整布局',                      // sidebar sublabel
  legend: [                                     // optional custom legend items
    { color: 'blue', label: '容器 / 框架' },
    { color: 'green', label: '功能页面' },
  ],
  root: { /* widget tree root node — see below */ },
};
```

### Widget Tree Node Format

Each node in the widget tree represents a UI widget/component:

```js
{
  name: 'widget_name',       // Object name or display text (e.g., '"文件"')
  obj: 'QWidget',            // Qt class name or framework component type
  color: 'blue',             // Catppuccin color key (see Color Keys below)
  badge: 'FRAME',            // Short badge text on header (WINDOW/FRAME/PANEL/BTN/TAB/STACK/WIDGET/LIST/ITEM/MENU/BAR/etc.)
  layout: 'v',               // Layout type: 'h' | 'v' | 'hsplit' | 'stack' | 'tab'
  note: 'additional info',   // Shown in hover tooltip (supports \\n for newlines)
  flex: 1,                   // CSS flex value for proportional sizing
  w: 200,                    // Fixed width in pixels
  h: 40,                     // Fixed height in pixels
  splitWeight: 600,          // Weight for hsplit siblings (QSplitter stretch factor)
  leaf: true,                // Terminal widget, no children
  placeholder: 'description',// Placeholder text for stub/empty pages
  spacer: true,              // Stretch spacer element (use with name: 'stretch')
  children: [ /* nested widget nodes */ ],

  // For layout: 'stack' (QStackedWidget):
  stackTabs: [
    { label: '[0] Page Name', key: 'page_key', active: true },
    { label: '[1] Other Page', key: 'other_key' },
  ],
  stackPages: {
    page_key: { /* widget tree node for this page */ },
    other_key: { /* widget tree node for this page */ },
  },

  // For layout: 'tab' (QTabWidget / MTabWidget):
  tabTabs: [
    { label: 'Tab 1', key: 't1', active: true },
    { label: 'Tab 2', key: 't2' },
  ],
  tabPages: {
    t1: { /* widget tree node for this tab */ },
    t2: { /* widget tree node for this tab */ },
  },
}
```

### Layout Types

| Value | Widget | Behavior |
|-------|--------|----------|
| `'v'` | QVBoxLayout | Children stacked vertically |
| `'h'` | QHBoxLayout | Children placed horizontally |
| `'hsplit'` | QSplitter (horizontal) | Children placed horizontally with draggable splitter handles between them |
| `'stack'` | QStackedWidget | One page visible at a time, controlled by `stackTabs` buttons |
| `'tab'` | QTabWidget | Tab bar at top, one page visible per tab |

### Color Keys

Assign colors semantically based on widget purpose:

| Color Key | Hex | Recommended Usage |
|-----------|-----|-------------------|
| `blue` | `#89b4fa` | Main containers, frames, windows |
| `sapphire` | `#74c7ec` | Tab widgets, secondary containers |
| `green` | `#a6e3a1` | Functional area A (e.g., face sculpting) |
| `peach` | `#fab387` | Functional area B (e.g., body workshop) |
| `mauve` | `#cba6f7` | Lists, sidebars |
| `red` | `#f38ba8` | Floating overlays, error states |
| `pink` | `#f5c2e7` | Functional area C (e.g., material lab) |
| `yellow` | `#f9e2af` | Menus, toolbars, special controls |
| `teal` | `#94e2d5` | Functional widgets, utility panels |
| `flamingo` | `#f2cdcd` | Functional area D (e.g., hair studio) |
| `lavender` | `#b4befe` | QStackedWidget containers |
| `rosewater` | `#f5e0dc` | Decorative, soft accent |
| `overlay` | `#313244` | Basic/leaf controls, minimal widgets |

### Special Features

- **Resize handles** — Each rendered widget box has three resize handles (right edge, bottom edge, bottom-right corner) that appear on hover. Users can drag to resize any widget box.
- **Ctrl+Z undo** — Resize operations are pushed to an undo stack. Press Ctrl+Z to revert the last resize. The undo stack is separate from the node-graph undo stack and is cleared when switching views.
- **Hover tooltips** — Hovering a widget box shows: badge type, object class (`obj`), name, note (if any), and size constraints (`w`, `h`, `splitWeight`).
- **`\\n` in names** — For vertical button text (e.g., Chinese characters stacked vertically), use `\\n` in the name string. The renderer converts these to actual newlines via CSS `white-space: pre-line`.
- **Spacer elements** — Use `{ spacer: true, name: 'stretch' }` to insert a flexible stretch spacer in horizontal or vertical layouts.
- **Splitter handles** — In `hsplit` layout, visual splitter handles (8px vertical bars with repeating pattern) are automatically inserted between children.

### Minimal Example

```js
var UI_LAYOUT_VIEWS = {};

UI_LAYOUT_VIEWS.main_window = {
  title: 'MainWindow — Layout',
  sub: 'main_window.py — QMainWindow',
  navLabel: '🏠 MainWindow',
  navSub: 'Main window layout',
  root: {
    name: 'MainWindow', obj: 'QMainWindow', color: 'blue',
    badge: 'WINDOW', layout: 'v',
    children: [
      {
        name: 'menu_bar', obj: 'QMenuBar', color: 'yellow', badge: 'MENU',
        layout: 'h', h: 30,
        children: [
          { name: '"File"', obj: 'QMenu', color: 'overlay', badge: 'MENU', leaf: true },
          { name: '"Edit"', obj: 'QMenu', color: 'overlay', badge: 'MENU', leaf: true },
        ]
      },
      {
        name: 'central', obj: 'QWidget', color: 'blue', badge: 'FRAME',
        layout: 'h', flex: 1,
        children: [
          {
            name: 'sidebar', obj: 'QListWidget', color: 'mauve', badge: 'LIST',
            w: 200, layout: 'v',
            children: [
              { name: '"Item 1"', obj: 'QListWidgetItem', color: 'overlay', badge: 'ITEM', leaf: true },
              { name: '"Item 2"', obj: 'QListWidgetItem', color: 'overlay', badge: 'ITEM', leaf: true },
            ]
          },
          {
            name: 'content', obj: 'QStackedWidget', color: 'lavender', badge: 'STACK',
            layout: 'stack', flex: 1,
            stackTabs: [
              { label: '[0] Page A', key: 'a', active: true },
              { label: '[1] Page B', key: 'b' },
            ],
            stackPages: {
              a: { name: 'page_a', obj: 'QWidget', color: 'green', badge: 'VIEW', placeholder: 'Page A content' },
              b: { name: 'page_b', obj: 'QWidget', color: 'peach', badge: 'VIEW', placeholder: 'Page B content' },
            },
          },
        ]
      },
      { name: 'status_bar', obj: 'QStatusBar', color: 'overlay', badge: 'BAR', leaf: true, h: 24 },
    ]
  }
};
```