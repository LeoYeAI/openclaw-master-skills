---
name: code_flow_graph
description: >
  This skill generates interactive HTML node-graph diagrams to visualize codebase
  structure, class relationships, and function call chains. It should be used when
  the user asks to visualize, diagram, or map out code architecture, module
  dependencies, class hierarchies, or UI event flows. It also supports UI layout
  visualization — generating interactive nested widget hierarchy diagrams for Qt,
  React, or other UI frameworks (triggered by "UI layout", "widget hierarchy",
  "界面布局", "控件层级" keywords). The output is a standalone HTML+JS viewer with
  draggable nodes, bezier-curve connections, group boxes, sidebar navigation,
  global search (Ctrl+K), call-chain detail panel, localStorage position persistence,
  click-to-copy function name, Ctrl+Z undo layout moves, interactive widget-box
  tree with resize handles, and Catppuccin Mocha dark theme.
---

# Code Flow Graph

Generate interactive node-graph HTML diagrams that visualize code structure and call relationships.

## When to Use

- User requests code structure visualization, architecture diagrams, or call-chain mapping
- User wants to understand how classes/modules/functions relate to each other
- User wants to see UI event flows (button click → handler → business logic) — UI projects only
- User asks to "diagram", "visualize", "map out", or "graph" the code

## Architecture

The output consists of two files placed in a dedicated folder:

1. **`code_flow_graph.html`** — rendering engine (from this skill's `example/code_flow_graph.html` template)
2. **`code_flow_graph_data.js`** — diagram data (generated per-project)

The HTML loads the JS via `<script src="code_flow_graph_data.js">` and must be in the same directory.

> **Important**: The HTML template lives in **this skill's repository**, not in the user's project. See Step 3 for the correct procedure to locate and copy it.

## Workflow

> **Core principle**: Start fast, go deep on demand. Immediately generate an Overview diagram upon receiving a request — no upfront questions about scope or language. Offer deeper analysis options after the Overview is delivered.

### Step 1: Analyze Project & Determine Scope

Begin analysis **immediately** upon receiving the user's request. Do NOT ask any scoping or language questions.

#### Scope Rules

- If the user's request **explicitly names a module or directory** (e.g., "分析 core 模块", "visualize the auth/ package"), restrict analysis to that scope only.
- Otherwise, analyze the **entire project**.

#### Analysis Procedure

1. Read the project's top-level structure: README, entry scripts (`__main__.py`, `main.py`, `index.ts`, `app.py`), config files (`setup.py`, `pyproject.toml`, `package.json`, `Cargo.toml`), and directory layout
2. Determine whether the project has a **UI layer** (Qt, React, Web, etc.) or is **non-UI** (CLI, library, backend, pipeline, etc.)
3. Identify all major modules/packages and their purposes within the determined scope
4. Discover the **main execution entry points** within the scope:
   - **CLI entry points** — `if __name__ == '__main__'`, Click/Typer/argparse commands, `console_scripts`
   - **Public API functions** — exported functions in `__init__.py`, decorated endpoints (`@app.route`, `@api_view`)
   - **Pipeline/task entry points** — Celery tasks, Airflow DAGs, scheduled jobs
   - **Hook/plugin entry points** — registered callbacks, plugin `activate()` methods
   - **Class constructors + primary methods** — the main "do something" methods of core classes
   - **UI entry points** (UI projects only) — main window creation, app initialization, route/page registration
5. **Assess function importance** — For each function/method discovered, evaluate its importance based on how many **project-internal** functions it calls or is called by. This determines whether it appears in the diagram (see Function Importance Filtering below).

#### Function Importance Filtering

Determine which functions to **include** or **exclude** from the generated diagrams. The goal is to produce detailed yet noise-free graphs that show meaningful business logic.

**Include** a function if it meets ANY of these criteria:
- It is an entry point (CLI, API, pipeline, hook, UI init)
- It calls **2 or more** other project-internal functions (high fan-out = orchestration logic)
- It is called by **3 or more** different project-internal call sites (high fan-in = shared core logic)
- It contains branching/dispatch logic (if/match/switch that routes to different code paths)
- It performs state mutation, data transformation, or coordinates multi-step workflows

**Exclude** a function if it meets ALL of these criteria:
- It calls **0–1** project-internal functions (low fan-out)
- It is a simple accessor/getter/setter (e.g., `get_name()`, `set_value()`, `is_valid()`)
- It is a thin wrapper around a single external API call with no project-internal logic
- It is a utility/helper doing generic work not specific to the project's domain (e.g., `format_string()`, `ensure_dir()`, `clamp()`, `retry()`)
- It is a logging, validation, or type-checking function with no side effects on business state

**When in doubt**, include the function — it is better to show slightly more detail than to miss important logic. Excluded functions can still appear as `children` (collapsed sub-items) inside their caller's attr if they contribute to understanding the call flow.

#### Language Default

Use **Chinese (中文)** for all `desc`, `sig` hint text, `io` labels, section titles, and `navSub` in the generated data. Switch to another language only if the user explicitly requests it.

### Step 2: Create Output Folder

Create the visualization output inside the project's `docs/` directory:

1. Check if `<project>/docs/` exists. If not, create it.
2. Create the output folder at `<project>/docs/code_graph/`.
3. If the user specifies a custom location, use that instead.

The final output path is always `<project>/docs/code_graph/` unless overridden by the user.

### Step 3: Copy the HTML Engine

The HTML viewer template is located at `example/code_flow_graph.html` **relative to this skill's definition file (SKILL.md)**. It is NOT inside the user's project.

#### How to locate the template

1. Determine the **skill directory** — the folder containing this SKILL.md file. The skill loading mechanism provides this path; it is typically visible in the file paths used when the skill was loaded.
2. Construct the template path: `<skill_directory>/example/code_flow_graph.html`
3. Use `read_file` to read the template's complete content from that path.
4. Use `write_to_file` to write the content to `<output_folder>/code_flow_graph.html`.

**Do NOT modify the HTML content.** Copy it verbatim.

> **Common failure mode**: If you try to read `example/code_flow_graph.html` as a relative path, it resolves against the user's project root — where the file does not exist. You MUST use the absolute path based on the skill's installation directory.

#### Engine Features (built-in, code_flow_graph.html)

1. **Search** — Ctrl+K opens search box; fuzzy-matches function names across ALL diagrams; click to jump cross-diagram
2. **Collapsed Children Redirect** — When children are collapsed, connections redirect to the parent attr instead of disappearing
3. **Click Blank to Deselect** — Click any blank area in the viewport to clear all highlights and close the detail panel
4. **Enhanced Legend** — Node type badges (CLASS/MODULE/FUNC/ENTRY/DATA/UI CLASS) on header; `external: true` nodes get dashed border + EXT tag; connection color semantics (call/data/extern/signal) with gradient indicating direction
5. **Signature Tooltips** — Hover any function attr to see full signature; callChain attrs show "Click to view call chain →" hint
6. **Call Chain Detail Panel** — Click attrs with `callChain` to open right-side interactive call tree; each item shows a `desc` (description) explaining what the function does; clicking any item with a matching graph node highlights that node and pans the viewport to it
7. **Field Detail Panel** — Click attrs with `fieldDetail` (typically on `data` type nodes) to open right-side field computation panel; shows field name, type, summary, and all computation modes with ordered step lists. Function names in steps are auto-highlighted as `<code>` elements
8. **Position Persistence** — Node positions saved to localStorage per diagram; "Reset Layout" restores defaults
9. **Click to Copy** — Clicking any function attr automatically copies the function name to clipboard and shows a toast notification
10. **Undo Layout Moves** — Ctrl+Z undoes the last node/group drag operation (up to 50 steps); undo stack is cleared when switching diagrams
11. **Connection Anchor via offsetTop** — Connection line anchors use `offsetTop`/`offsetParent` chain (NOT `getBoundingClientRect`) to compute attr Y-offset within a node. This is critical because the canvas uses `CSS transform: scale()` for zoom — `getBoundingClientRect` returns screen-space coordinates that include the scale factor, causing connection lines to misalign at non-1x zoom levels

### Step 4: Generate Overview Diagram

Generate `code_flow_graph_data.js` containing **only the Overview diagram** as the first deliverable. This is the initial output — deep-dive diagrams are added incrementally in Step 6.

Refer to `references/data_format.md` for the complete data format specification including NODES, CONNECTIONS, GROUPS structure, color schemes, node types, and layout guidelines.

#### Overview Diagram Content

The Overview is a **module-level dependency graph** showing:

- One node per major module/class (NOT per function)
- All discovered entry points highlighted with `type: 'entry'`
- Cross-module dependency connections
- Package/folder groups
- For UI projects: a single node representing the UI layer with connections to business logic

Keep the Overview high-level. Do NOT trace individual function call chains at this stage.

#### Key Principles

- **Type-based colors** — Node color is automatically assigned by `type` (entry=yellow, class=blue, module=green, function=mauve, data=peach, widget=sapphire); no manual `cls` needed. Widget/UI class nodes use sapphire blue (`#74c7ec`), which is in the same blue family as `class` (`#89b4fa`) but visually distinct.
- **External dependencies** — Use the node's actual type (`module`/`class`) with `external: true` for third-party deps (renders dashed border + EXT tag)
- **Detailed but focused** — Generate comprehensive diagrams that show all important business logic functions. Apply the Function Importance Filtering rules from Step 1: include functions with high fan-out (calls ≥2 project functions) or high fan-in (called from ≥3 sites); exclude trivial accessors, thin API wrappers, generic utilities (`format_*`, `ensure_*`, `clamp`, `retry`), and pure logging/validation helpers. Excluded functions may still appear as collapsed `children` inside their caller's attr.
- **Rich tooltips** — Add `sig` field with HTML tooltip for every non-trivial function attr. Additionally, provide a `desc` (one-line summary) and `detail` (multi-line detailed description including: core processing steps, key called functions, side effects, error handling). The `detail` field appears below `desc` in the hover tooltip, giving developers a deeper understanding without needing to read source code.
- **Grid-aligned layout** — Arrange nodes on an implicit grid with consistent column x-coordinates and vertical spacing. Follow the Layout Guidelines in `references/data_format.md` to ensure nodes are neatly aligned in columns (left → right: callers → callees) with uniform gaps. Avoid overlapping or scattered placement. Groups should be tightly packed (INTER_GROUP_GAP=20px) — avoid excessive whitespace between groups.
- **Readable section headers** — Node-internal section titles (e.g., "PUBLIC METHODS") must be clearly legible: use color `#7f849c` and font-size `9.5px`. Keep them visually distinct from function names (uppercase + letter-spacing) but without glow or decorative effects.

### Step 5: Verify, Clean Up & Present Overview

After generating both files:

1. **Verify** the data file has valid JS syntax.
2. **Clean up** — Check the output folder (`docs/code_graph/`) and project root for any extra files generated during the process (e.g., temporary scripts, duplicate HTML files, stray data files, backup files). Delete any files that are NOT one of the two expected outputs (`code_flow_graph.html` and `code_flow_graph_data.js`). Also check for and remove any unintended files created outside the output folder.
3. **Present** — Open the HTML in the browser for the user.

### Step 6: Offer Deep-Dive Analysis Options

After the Overview is successfully generated and presented, inform the user that deeper analysis is available. Use the `ask_followup_question` tool to present **clickable option buttons** based on the actual entry points and data types discovered in Step 1.

#### Option Generation Rules

Analyze the discovered entry points and project characteristics to build a **dynamic** set of options. Do NOT use a fixed template — tailor the options to the actual codebase. Include the following categories as applicable:

1. **Function call chain analysis** — For each discovered entry point, offer an option like:
   - "分析 `ClassName.method_name()` 的完整调用链路"
   - "分析 `main()` 函数的调用链路"

2. **UI signal/event analysis** (UI projects ONLY) — If the project has a UI layer:
   - "分析 UI 信号与事件处理链路"
   - "分析 `MainWindow` 的事件绑定和分发逻辑"

3. **UI layout visualization** (UI projects ONLY) — If the project has a UI layer (Qt, React, Web, etc.):
   - "可视化 UI 界面布局层级"
   - "生成 `MainWindow` 的 Widget 层级布局图"
   - This generates `UI_LAYOUT_VIEWS` data in `code_flow_graph_data.js`, rendered as an interactive widget hierarchy tree in the left sidebar under "🖼️ UI 布局" section. Users can resize widget boxes by dragging edges and undo with Ctrl+Z.

4. **Data structure analysis** — If the project defines significant data types:
   - "分析数据结构的组成和传递链路"
   - "分析 `ConfigData` 的生成与变化链路"

5. **Custom analysis** — Always include a free-form option:
   - "自定义：分析其他函数或模块"

#### Example `ask_followup_question` Call

```
ask_followup_question({
  title: "Overview 已生成，还可以进行以下深度分析：",
  questions: [{
    id: "deep_dive",
    question: "选择要深入分析的内容：",
    options: [
      "分析 Pipeline.run() 的完整调用链路",
      "分析 Converter.convert() 的完整调用链路",
      "分析 CLI main() 的命令分发逻辑",
      "可视化 UI 界面布局层级",
      "分析数据结构的组成和传递链路",
      "自定义：分析其他函数或模块"
    ],
    multiSelect: true
  }]
})
```

**STOP and wait for the user's selection.** The user may pick one or more options, or type a custom request.

### Step 7: Generate Deep-Dive Diagrams (Incremental)

Based on the user's selection in Step 6, generate additional diagram pages and **append** them to the existing `code_flow_graph_data.js`. Do NOT regenerate the Overview or any previously created diagrams.

#### Incremental Append Procedure

1. Read the existing `code_flow_graph_data.js`
2. Add new `DIAGRAMS.<name>` entries for each requested deep-dive
3. Write the updated file back — preserving all existing diagram data

#### Deep-Dive Diagram Types

##### Call-Chain Diagram (per entry point)

Each diagram traces the **complete call chain** of one entry function:

1. Read the entry function's source code completely
2. For each function it calls, apply Function Importance Filtering:
   - **Include as a separate node** if the function has high fan-out/fan-in, contains branching logic, or performs significant state mutation
   - **Include as collapsed `children`** if the function is a simple helper but still relevant to understanding the flow
   - **Exclude entirely** if the function is a trivial accessor, thin API wrapper, or generic utility (e.g., `get_attr()`, `format_string()`, `retry()`)
3. For included functions, determine placement:
   - Is it an internal helper (same module)? → attr with `children` or separate node in same group
   - Is it a cross-module call? → separate node, different color, place in "External" group
   - Does it have sub-calls worth showing? → recurse and show as nested children or connected nodes
4. Organize nodes **left-to-right** following execution order (entry on left, deepest calls on right)
5. Each node should have a `sig` with a **one-line hint** explaining what the function does, plus a `detail` field with a **multi-line detailed description** covering core logic steps, key sub-calls, and side effects
6. Add `callChain` to the entry function attr for the interactive detail panel
7. Include `desc` for every `callChain` item explaining what the function does
8. Ensure `callChain[].id` exactly matches the target `attrs[].id` (format: `NodeId.method_name`)

##### UI Signal/Event Diagram (UI projects only)

1. Create a dedicated diagram entry per major UI view/window
2. Use `widget` type for widget nodes with sections: Widgets, Event Handlers, Slots
3. Draw dashed pink connections from event handlers to business logic

##### UI Layout Visualization (UI projects only)

Generate `UI_LAYOUT_VIEWS` data in `code_flow_graph_data.js` to create interactive widget hierarchy layout diagrams. These appear in the sidebar under a "🖼️ UI 布局" separator.

1. **Analyze UI source code** — Read the main window and page source files to understand the complete widget tree (parent-child relationships, layout types, sizing policies)
2. **Generate `UI_LAYOUT_VIEWS` object** — Append a `var UI_LAYOUT_VIEWS = {};` block to `code_flow_graph_data.js` (after the `DIAGRAMS` entries). Each view key maps to a view object:

```js
var UI_LAYOUT_VIEWS = {};
UI_LAYOUT_VIEWS.main_window = {
  title: 'MainWindow — 完整布局',
  sub: 'path/to/main_window.py — QMainWindow',
  navLabel: '🏠 MainWindow',
  navSub: '主窗口完整布局',
  legend: [ // optional custom legend
    { color: 'blue', label: '容器 / 框架' },
    { color: 'green', label: '功能页面' },
  ],
  root: { /* widget tree — see below */ }
};
```

3. **Widget tree node format**:

```js
{
  name: 'widget_name',          // Object name or display text (e.g., '"文件"')
  obj: 'QWidget',               // Qt class name / description
  color: 'blue',                // Catppuccin color key (blue/green/peach/mauve/red/pink/yellow/teal/flamingo/lavender/rosewater/sapphire/overlay)
  badge: 'FRAME',               // Short badge text on header (WINDOW/FRAME/PANEL/BTN/TAB/STACK/WIDGET/etc.)
  layout: 'v',                  // 'h' (horizontal), 'v' (vertical), 'hsplit' (QSplitter), 'stack' (QStackedWidget), 'tab' (QTabWidget)
  note: 'additional info',      // Shown in hover tooltip
  flex: 1,                      // CSS flex value
  w: 200,                       // Fixed width in px
  h: 40,                        // Fixed height in px
  splitWeight: 600,             // Weight for hsplit siblings
  leaf: true,                   // No children (terminal widget)
  placeholder: 'description',   // Placeholder text for stub pages
  spacer: true,                 // Stretch spacer element (use name: 'stretch')
  children: [ /* nested widgets */ ],
  // For layout: 'stack':
  stackTabs: [ { label: '[0] Page', key: 'p0', active: true } ],
  stackPages: { p0: { /* widget node */ } },
  // For layout: 'tab':
  tabTabs: [ { label: 'Tab 1', key: 't1', active: true } ],
  tabPages: { t1: { /* widget node */ } },
}
```

4. **Color coding** — Assign colors semantically:
   - `blue` / `sapphire` for containers and frameworks
   - `green` / `peach` / `pink` / `flamingo` / `mauve` for different functional areas
   - `yellow` for menus, toolbars, special controls
   - `lavender` for QStackedWidget
   - `teal` for functional widgets
   - `red` for overlays and floating layers
   - `overlay` for basic/leaf controls

5. **Literal `\n` in names** — For vertical button text (e.g., Chinese characters stacked vertically), use `\\n` in the name string. The renderer converts these to actual newlines via CSS `white-space: pre-line`.

6. **Resize & Undo** — Each rendered widget box has resize handles (right, bottom, corner) visible on hover. Users can drag to resize and press Ctrl+Z to undo.

##### Data Type Diagram

1. Create a dedicated "Data Types" diagram entry
2. Each dataclass / data model / state class → node with type `data`
3. List fields as attrs with type in the `val` field (e.g., `val: ': User[]'`)
4. **Add `fieldDetail` to every non-trivial field attr** — This is the key feature that enables the right-sidebar "field computation" panel when users click a data field. For each field, analyze the source code to determine:
   - **Where the field gets its initial value** (constructor, factory, default)
   - **What operations modify the field** (reducers, setters, event handlers, API callbacks)
   - **How the field is computed or derived** (selectors, computed properties, transformations)

   Structure the `fieldDetail` as:
   ```js
   fieldDetail: {
     field: 'fieldName',        // field name
     type: 'FieldType',         // type annotation
     summary: 'One-paragraph description of what this field represents and how it is managed.',
     sources: [
       {
         mode: 'INITIAL',       // mode label describing the scenario
         fn: 'constructor()',    // source function
         steps: [               // ordered computation steps
           'Step 1 — what happens',
           'Step 2 — call someFunction() to process',
           'Step 3 — assign result to field',
         ],
       },
       {
         mode: 'ON UPDATE',     // another scenario
         fn: 'reducer(state, action)',
         steps: [ ... ],
       },
     ],
   }
   ```
   Each `sources` entry represents a different **scenario** in which the field value changes. Common modes: `INITIAL`, `ON FETCH`, `ON UPDATE`, `ON DELETE`, `ON FILTER`, `COMPUTED`, `ON EVENT`.

5. Add connections between data nodes to show **data composition** (e.g., `AppState.users` → `UserState`) and **data flow** (e.g., Reducer → State field) using appropriate colors:
   - Blue `#89b4fa` — data composition / ownership (parent state → child state)
   - Green `#a6e3a1` — reducer / producer → state field (data creation)
   - Pink dashed `#f5c2e7` — signal / event dispatch → handler
   - Peach `#fab387` — external API dependency
6. Optionally add "Reducer" / "Service" / "Middleware" nodes (type `function` or `class`) to show the **data flow pipeline** — how data enters, transforms, and reaches each field

#### After Each Deep-Dive

After generating the requested deep-dive diagrams, repeat Step 6 — offer the remaining un-analyzed entry points and categories as new options. Continue this cycle until the user indicates they are done.

#### Diagram Organization (Sidebar Order)

As diagrams accumulate incrementally, the sidebar order follows this structure:

1. **Overview** (always first, generated in Step 4)
2. **Call-chain diagrams** — One per analyzed entry point, named after the entry function (e.g., "Pipeline.run()", "CLI — build")
3. **UI diagrams** (if applicable) — Widget hierarchy and event dispatch
4. **Data Types** (if applicable) — Dataclass field listings and data flow
5. **Config / Constants** (optional) — If central to understanding the code
6. **🖼️ UI 布局** (if applicable) — Separated by a visual divider in the sidebar; contains UI layout views generated via `UI_LAYOUT_VIEWS`. These render as interactive nested widget-box trees (not node graphs)

#### Element Mapping

| Code Concept | Graph Element |
|---|---|
| Entry function | NODE (type: `entry`) — ENTRY badge on header |
| Class / core object | NODE (type: `class`) — CLASS badge on header |
| Module / package | NODE (type: `module`) — MODULE badge on header |
| Function group / utility | NODE (type: `function`) — FUNC badge on header |
| Pipeline step / major called function | NODE with attrs for its sub-calls |
| Small helper called once | attr with `children` inside parent node |
| Cross-module dependency | NODE (type: `module`/`class`, `external: true`) — dashed border + EXT tag |
| Data type / dataclass | NODE (type: `data`) — DATA badge on header |
| UI widget / dialog | NODE (type: `widget`) — UI CLASS badge on header |
| Descriptive note | attr |
| Direct function call A→B | CONNECTION (solid, gradient toward callee) |
| Signal / event / callback | CONNECTION (dashed, gradient toward target) |

### Step 8: Verify & Clean Up

After each incremental update:

1. Verify the data file has valid JS syntax.
2. Check for and remove any extra/temporary files generated during the process. The output folder should only contain `code_flow_graph.html` and `code_flow_graph_data.js`.

## Handling Large Codebases

When the data JS file exceeds ~500 lines per diagram entry:

- Apply Function Importance Filtering more aggressively: raise fan-out threshold to ≥3 and fan-in threshold to ≥4
- Focus on the entry function's direct and second-level calls; collapse deeper calls into `children`
- Summarize repetitive patterns (e.g., "N similar UV operations") rather than listing every one
- Aggressively exclude all utility/helper functions — only show orchestration and domain-critical logic
- Cross-module calls should reference the target diagram by name in the `sig` hint

## Known Pitfalls

### Connection Anchor Calculation Must Use offsetTop

When calculating where bezier connection lines attach to attribute rows, **always use `offsetTop` / `offsetParent` chain** — never use `getBoundingClientRect()`.

**Why**: The canvas applies `CSS transform: translate() scale()` for pan & zoom. `getBoundingClientRect()` returns screen-space pixel coordinates that already include the scale factor. When computing `relY = attrRect.top - nodeRect.top`, the result is in scaled pixels, but the connection coordinates are drawn in the unscaled canvas coordinate system. This causes connection lines to progressively misalign as the user zooms in/out.

**Correct pattern** (used in `code_flow_graph.html`):
```js
var relY = el.offsetHeight / 2;
var cur = el;
while (cur && cur !== nodeEl) {
  relY += cur.offsetTop;
  cur = cur.offsetParent;
}
```

**Wrong pattern** (causes misaligned connections at non-1x zoom):
```js
var attrRect = el.getBoundingClientRect();
var nodeRect = nodeEl.getBoundingClientRect();
var relY = (attrRect.top - nodeRect.top) + attrRect.height / 2;
```

If you generate standalone HTML viewers outside this skill (e.g., `warp_card_diagram.html`, `node_diagram.html`), apply the same offsetTop pattern in their `getAttrAnchor()` function.

### Canvas Transform Must Be Synced Before Measuring

In `switchDiagram()`, after resetting `scale = 1; panX = 0; panY = 0;`, you **must call `applyTransform()`** before the `requestAnimationFrame` callback that runs `redrawConnections()`. Otherwise the canvas still has the **previous diagram's transform** (e.g., `scale(0.5)` from `fitToView`), and any coordinate measurement (even `offsetTop`) operates on a stale visual state.

**Correct pattern**:
```js
scale = 1; panX = 0; panY = 0;
applyTransform(); // flush transform to canvas BEFORE measuring
requestAnimationFrame(function() {
  updateGroupBounds(); redrawConnections(); fitToView();
});
```

**Wrong pattern** (stale transform during measurement):
```js
scale = 1; panX = 0; panY = 0;
// missing applyTransform()!
requestAnimationFrame(function() {
  updateGroupBounds(); redrawConnections(); fitToView();
});
```
