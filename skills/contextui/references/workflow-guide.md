# Workflow Building Guide

Complete guide to building ContextUI workflows. Read this when you're ready to build.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Available Globals](#available-globals)
3. [Color Theming](#color-theming)
4. [Python Backends](#python-backends)
5. [Multi-File Workflows](#multi-file-workflows)
6. [Common Patterns](#common-patterns)
7. [Testing Your Workflow](#testing-your-workflow)
8. [Publishing Checklist](#publishing-checklist)

---

## Core Concepts

### No Imports (except local files)
ContextUI dynamically loads your TSX. React and hooks are injected globally. You CAN import from local `./ui/` sub-components. You CANNOT import from npm packages.

### Available Globals
These are available without importing:
- `React` — Full React library
- `useState`, `useEffect`, `useRef`, `useMemo`, `useCallback`, `useReducer`, `useContext` — Available as bare globals
- `ReactDOM` — For portals if needed
- Tailwind CSS — All utility classes available in className
- `fetch` — For calling Python backends or external APIs

### File Naming Convention
- Main component: `WorkflowName.tsx` or `WorkflowNameWindow.tsx` — both work
- Must match folder name: `MyTool/MyTool.tsx` or `MyTool/MyToolWindow.tsx`
- Use named export: `export const MyToolWindow: React.FC = () => { ... }`

---

## Color Theming

Use a single Tailwind color family throughout your workflow for consistency.

### Color Scale (dark theme)
```
{color}-950  → Main background (darkest)
{color}-900  → Card/panel backgrounds
{color}-800  → Secondary backgrounds, hover states, tertiary buttons
{color}-700  → Borders, dividers
{color}-600  → Primary buttons, accents
{color}-500  → Button hover states, focus rings
{color}-400  → Muted text, placeholders, links
{color}-200  → Secondary text
{color}-100  → Primary text (lightest)
```

### Available Colors
`purple`, `cyan`, `emerald`, `amber`, `slate`, `pink`, `red`, `orange`, `lime`, `indigo`, `blue`

### Semantic Colors (always use these, regardless of theme)
- **Green** — Success states
- **Red** — Error/danger states
- **Yellow** — Warning states
- **Blue** — Info states

### Example: Themed Container
```tsx
<div className="min-h-full bg-purple-950 text-purple-100 p-6">
  <div className="bg-purple-900 rounded-lg border border-purple-700 p-4">
    <h2 className="text-purple-100 font-semibold">Panel Title</h2>
    <p className="text-purple-400 text-sm">Description text</p>
    <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg">
      Action
    </button>
  </div>
</div>
```

---

## Python Backends

For ML models, API calls, heavy data processing, or anything that shouldn't run in the browser.

**All Python-backed workflows use the ServerLauncher pattern.** See `references/server-launcher.md` for the complete guide, source code, and integration steps.

### Quick Summary

1. Copy `ui/ServerLauncher/` (2 files) from the `examples/KokoroTTS/` example (canonical source) into your workflow
2. Call `useServerLauncher()` with a simple config
3. Render `<ServerLauncher server={server} />` for the setup UI
4. Write your FastAPI backend

```tsx
import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';

const server = useServerLauncher({
  workflowFolder: 'MyWorkflow',
  scriptName: 'my_server.py',
  port: 8850,
  serverName: 'my-server',
  packages: ['fastapi', 'uvicorn[standard]'],
});

// Show setup UI until connected, then your workflow:
{server.connected ? <MyFeatureUI serverUrl={server.serverUrl} /> : <ServerLauncher server={server} />}
```

The ServerLauncher handles everything: Python detection, venv selection, package installation, port management, server start/stop, auto-start, and settings persistence. Cross-platform (Windows, macOS, Linux).

### Backend Pattern (FastAPI)
```python
# my_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DEFAULT_PORT = 8850

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/process")
async def process(data: dict):
    result = do_something(data)
    return {"result": result}

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    uvicorn.run(app, host="127.0.0.1", port=port)
```

**Important:** Always include a `/health` endpoint — the ServerLauncher uses it to detect when the server is ready.

### Calling from TSX
```tsx
const handleProcess = async () => {
  const res = await fetch(`${serverUrl}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input: 'data' }),
  });
  const data = await res.json();
  setResult(data.result);
};
```

### Python Venvs (via MCP)
ContextUI manages Python virtual environments. List available ones:
```bash
mcporter call contextui.python_list_venvs
```

---

## Multi-File Workflows

For complex workflows, split into multiple components in a `ui/` folder.

### Structure
```
MyWorkflow/
├── MyWorkflowWindow.tsx        # Main entry — imports from ./ui/
├── MyWorkflow.meta.json
├── description.txt
├── my_server.py                # Optional Python backend
└── ui/
    ├── MyFeatureTab.tsx         # Feature UI (imported by main)
    ├── SettingsPanel.tsx
    └── ServerLauncher/          # Copy from examples/KokoroTTS/ui/ServerLauncher/
        ├── useServerLauncher.ts
        └── ServerLauncher.tsx
```

### Sub-components
Sub-components use the same globals (React, hooks, etc.) and are imported by the main window:

```tsx
// ui/MyFeatureTab.tsx — exported as named export, imported by main window

interface MyFeatureTabProps {
  serverUrl: string;
  connected: boolean;
  addLog?: (msg: string) => void;
}

export const MyFeatureTab: React.FC<MyFeatureTabProps> = ({ serverUrl, connected, addLog }) => {
  const [result, setResult] = useState<string>('');

  const doWork = async () => {
    const res = await fetch(`${serverUrl}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: 'test' }),
    });
    const data = await res.json();
    setResult(data.result);
    addLog?.(`Got result: ${data.result}`);
  };

  return (
    <div className="flex-1 p-4">
      <button onClick={doWork} className="px-4 py-2 bg-blue-600 text-white rounded">
        Process
      </button>
      {result && <pre className="mt-4 text-sm text-slate-300">{result}</pre>}
    </div>
  );
};
```

### Main window imports sub-components:
```tsx
// MyWorkflowWindow.tsx
import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';
import { MyFeatureTab } from './ui/MyFeatureTab';
```

---

## Common Patterns

### TypeScript Interfaces
Define interfaces for your data structures at the top of the file:
```tsx
interface ServerStatus {
  model_ready: boolean;
  model_loading: boolean;
  error: string | null;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}
```

### Style Constants
For consistent styling, define a style object:
```tsx
const S = {
  section: 'bg-slate-900 p-3 rounded-md mb-2.5',
  btn: 'py-2 px-4 border-none rounded cursor-pointer bg-blue-500 text-white text-[13px]',
  btnDisabled: 'py-2 px-4 border-none rounded cursor-not-allowed bg-slate-600 text-white text-[13px] opacity-50',
  input: 'py-1.5 px-2.5 border border-slate-600 rounded bg-[#2a2a2a] text-white text-[13px] w-full',
};
```

### Platform Detection
For cross-platform package compatibility:
```tsx
const _isWindows = typeof navigator !== 'undefined'
  && (navigator.platform?.toLowerCase().includes('win') ?? false);

const IS_MAC = (typeof process !== 'undefined' && process.platform === 'darwin') ||
  (typeof navigator !== 'undefined' && /Mac/.test(navigator.userAgent));

// Use in packages array:
packages: [
  'fastapi',
  _isWindows ? 'uvicorn' : 'uvicorn[standard]',
  'torch',
  ...(IS_MAC ? ['mlx-lm'] : []),
]
```

### Connection Status Indicator
```tsx
<div className={`px-4 py-2 text-xs ${server.connected ? 'text-green-400' : 'text-slate-500'}`}>
  {server.connected ? '● Connected' : '○ Disconnected'}
</div>
```

### Data Fetching
```tsx
const [data, setData] = React.useState(null);
const [loading, setLoading] = React.useState(true);

React.useEffect(() => {
  fetch('http://127.0.0.1:8800/data')
    .then(res => res.json())
    .then(d => { setData(d); setLoading(false); })
    .catch(() => setLoading(false));
}, []);
```

### Tab Navigation
```tsx
const [tab, setTab] = React.useState(0);
const tabs = ['Overview', 'Settings', 'Output'];

<div className="flex gap-1 bg-slate-800/50 p-1 rounded-lg w-fit">
  {tabs.map((name, i) => (
    <button
      key={name}
      onClick={() => setTab(i)}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
        tab === i
          ? 'bg-blue-600 text-white shadow-lg'
          : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
      }`}
    >
      {name}
    </button>
  ))}
</div>
```

### Form Input
```tsx
<input
  type="text"
  value={value}
  onChange={(e) => setValue(e.target.value)}
  className="w-full bg-slate-900 border border-slate-700 text-slate-100 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
  placeholder="Enter text..."
/>
```

### Loading Spinner
```tsx
<div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
```

### Progress Bar
```tsx
<div className="w-full bg-slate-800 rounded-full h-2">
  <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${percent}%` }} />
</div>
```

### Alert Box
```tsx
<div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
  <div className="text-green-400 font-semibold mb-1">Success</div>
  <div className="text-green-300 text-sm">Operation completed.</div>
</div>
```

### Canvas / Three.js
ContextUI supports canvas rendering. Use a ref:
```tsx
const canvasRef = React.useRef<HTMLCanvasElement>(null);

React.useEffect(() => {
  const canvas = canvasRef.current;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  // Draw...
}, []);

<canvas ref={canvasRef} width={800} height={600} className="rounded-lg" />
```

For Three.js, load it via CDN in a script tag or use the global if available.

---

## Testing Your Workflow

### 1. Launch It
```bash
mcporter call contextui.launch_workflow path="/path/to/WorkflowWindow.tsx"
```

### 2. Screenshot It
```bash
mcporter call contextui.ui_screenshot
```

### 3. Interact With It
```bash
mcporter call contextui.ui_click text="Submit"
mcporter call contextui.ui_type selector="#input" text="test data"
```

### 4. Check Accessibility
```bash
mcporter call contextui.ui_accessibility_audit
```

### 5. Verify DOM
```bash
mcporter call contextui.ui_get_dom depth=4
```

---

## Publishing Checklist

Before publishing to the Exchange:

- [ ] Workflow launches without errors
- [ ] Screenshot looks professional (dark theme, good spacing)
- [ ] `description.txt` is clear and descriptive
- [ ] `meta.json` has appropriate icon and color
- [ ] All interactive elements work (buttons, inputs, etc.)
- [ ] Accessibility audit passes (or violations are addressed)
- [ ] Python backend (if any) starts cleanly and has error handling
- [ ] No hardcoded paths or credentials in the TSX
- [ ] Responsive layout (works at different window sizes)
- [ ] Performance is good (no unnecessary re-renders, no memory leaks)
