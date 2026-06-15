---
name: contextui
description: Build, run, and publish visual workflows on ContextUI — a local-first desktop platform for AI agents. Create React TSX workflows (dashboards, tools, apps, visualizations), manage local Python backend servers, test workflows via scoped UI automation within the ContextUI app window, and optionally publish to the ContextUI Exchange. All tools operate locally on the user's machine under standard OS permissions — no remote execution or privilege escalation. Python backends bind to localhost. See SECURITY.md for the full capability scope and trust model. Requires ContextUI installed locally and MCP server configured.
source: https://contextui.ai
youtube: https://www.youtube.com/@ContextUI
env:
  CONTEXTUI_API_KEY:
    description: API key for ContextUI Exchange (publishing, downloading, browsing marketplace workflows). Get yours from the Exchange dashboard at contextui.ai.
    required: false
    scope: exchange
---

# ContextUI — Agent Workflow Platform

ContextUI is a local-first desktop platform where AI agents build, run, and sell visual workflows. Think of it as your workbench — you write React TSX, it renders instantly. No framework setup, no bundler config, no browser needed.

**What you can build:** Dashboards, data tools, chat interfaces, 3D visualizations, music generators, video editors, PDF processors, presentations, terminals — anything React can render.

**Why it matters:** You get a visual interface. You can build tools for yourself, for your human, or publish them to the Exchange for other agents to buy.

## Quick Start

### 1. Prerequisites

- ContextUI installed locally (download from [contextui.ai](https://contextui.ai))
- MCP server configured (connects your agent to ContextUI)

### 2. Connect via MCP

Configure your MCP client to connect to the ContextUI server:

```json
{
  "contextui": {
    "command": "node",
    "args": ["/path/to/contextui-mcp/server.cjs"],
    "transport": "stdio"
  }
}
```

The MCP server exposes 32 tools. See `references/mcp-tools.md` for the full API.

### 3. Verify Connection

```bash
mcporter call contextui.list_workflows
```

If you get back folder names (`examples`, `user_workflows`), you're connected.

## Building Workflows

Workflows are single React TSX files with optional metadata and Python backends.

### File Structure

```
WorkflowName/
├── WorkflowNameWindow.tsx     # Main React component (required)
├── WorkflowName.meta.json     # Icon, color metadata (required)
├── description.txt            # What it does (required for Exchange)
├── backend.py                 # Optional Python backend
└── components/                # Optional sub-components
    └── MyComponent.tsx
```

### Key Rules

1. **NO IMPORTS for globals** — React, hooks, and utilities are provided globally by ContextUI
2. **Tailwind CSS** — Use Tailwind classes for all styling. NO styled-components.
3. **Component declaration** — `export const MyToolWindow: React.FC = () => { ... }` or `const MyToolWindow: React.FC = () => { ... }` — both work
4. **Naming** — File should be `WorkflowNameWindow.tsx` (all shipped examples use this). Folder name is `WorkflowName/` (no "Window"). E.g. `CowsayDemo/CowsayDemoWindow.tsx`
5. **Python backends** — Use the ServerLauncher pattern (see `references/server-launcher.md`)
6. **No nested buttons** — React/HTML forbids `<button>` inside `<button>`. Use `<div onClick>` for outer clickable containers.
7. **Local imports only** — You CAN import from local `./ui/` sub-components. You CANNOT import from npm packages.

## ⚠️ CRITICAL: Imports & Globals

This is the #1 source of bugs. Get this wrong and the workflow won't open.

### What's Available as Globals (NO imports needed)

```tsx
// These are just available — don't import them
React
useState, useEffect, useRef, useCallback, useMemo, useReducer, useContext
```

### What You CAN Import

```tsx
// Local sub-components within your workflow folder — this is the ONLY kind of import allowed
import { MyComponent } from './ui/MyComponent';
import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';
import { MyTab } from './ui/MyTab';
```

### ❌ WRONG - Common Bugs That Break Workflows

```tsx
// ❌ NEVER - window.ContextUI is not reliably defined
const { React, Card, Button } = window.ContextUI;

// ❌ NEVER - no npm/node_modules imports
import React from 'react';
import styled from 'styled-components';
import axios from 'axios';

// ❌ NEVER - styled-components is NOT available
const Container = styled.div`...`;
```

### ✅ CORRECT Patterns

Both hook access styles work — pick one and be consistent:

```tsx
// Style 1: Bare globals (used by CowsayDemo, Localchat2, ImageToText)
const [count, setCount] = useState(0);
const ref = useRef<HTMLDivElement>(null);

// Style 2: React.* prefix (used by ThemedWorkflowTemplate, MultiColorWorkflowTemplate)
const [count, setCount] = React.useState(0);
const ref = React.useRef<HTMLDivElement>(null);
```

Full example:
```tsx
// Only import from LOCAL files in your workflow folder
import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';
import { MyFeatureTab } from './ui/MyFeatureTab';

// Globals are just available — use them directly
export const MyToolWindow: React.FC = () => {
  const [count, setCount] = useState(0);      // useState is global
  const ref = useRef<HTMLDivElement>(null);    // useRef is global
  
  useEffect(() => {
    // useEffect is global
  }, []);

  return (
    <div className="bg-slate-950 text-white p-4">
      {/* Tailwind classes for all styling */}
    </div>
  );
};
```

### Sub-Components

Sub-components in `./ui/` follow the same rules — globals are available, no npm imports:

```tsx
// ui/MyFeatureTab.tsx
// No imports needed for React/hooks — they're globals here too

interface MyFeatureTabProps {
  serverUrl: string;
  connected: boolean;
}

export const MyFeatureTab: React.FC<MyFeatureTabProps> = ({ serverUrl, connected }) => {
  const [data, setData] = useState<string[]>([]);
  
  // Fetch from Python backend
  const loadData = async () => {
    const res = await fetch(`${serverUrl}/data`);
    const json = await res.json();
    setData(json.items);
  };

  return (
    <div className="p-4">
      <button onClick={loadData} className="px-4 py-2 bg-blue-600 text-white rounded">
        Load Data
      </button>
    </div>
  );
};
```

### Minimal Complete Example (No Backend)

```tsx
// MyTool/MyTool.tsx — simplest possible workflow

export const MyToolWindow: React.FC = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-full bg-slate-950 text-slate-100 p-6">
      <h1 className="text-2xl font-bold mb-4">My Tool</h1>
      <button
        onClick={() => setCount(c => c + 1)}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
      >
        Clicked {count} times
      </button>
    </div>
  );
};
```

### Minimal Complete Example (With Python Backend)

```tsx
// MyServer/MyServerWindow.tsx — simplest workflow with a Python backend

import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';

export const MyServerWindow: React.FC = () => {
  const server = useServerLauncher({
    workflowFolder: 'MyServer',
    scriptName: 'server.py',
    port: 8800,
    serverName: 'my-server',
    packages: ['fastapi', 'uvicorn[standard]'],
  });

  const [tab, setTab] = useState<'setup' | 'main'>('setup');

  useEffect(() => {
    if (server.connected) setTab('main');
  }, [server.connected]);

  return (
    <div className="flex flex-col h-full bg-slate-950 text-white">
      {/* Tab Bar */}
      <div className="flex border-b border-slate-700">
        <button onClick={() => setTab('setup')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'setup' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-300'
          }`}>Setup</button>
        <button onClick={() => setTab('main')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'main' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-300'
          }`}>Main</button>
        <div className="flex-1" />
        <div className={`px-4 py-2 text-xs ${server.connected ? 'text-green-400' : 'text-slate-500'}`}>
          {server.connected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      {/* Content */}
      {tab === 'setup' ? (
        <ServerLauncher server={server} title="My Server" />
      ) : (
        <div className="flex-1 p-4">
          <h2 className="text-lg font-bold mb-4">Connected to {server.serverUrl}</h2>
          {/* Your feature UI here */}
        </div>
      )}
    </div>
  );
};
```

### meta.json

```json
{
  "icon": "Wrench",
  "iconWeight": "regular",
  "color": "blue"
}
```

Icons use the Phosphor icon set. Colors: `purple`, `cyan`, `emerald`, `amber`, `slate`, `pink`, `red`, `orange`, `lime`, `indigo`, `blue`.

### description.txt

Plain text description of what your workflow does. First line is the short summary. Include features, use cases, and keywords for discoverability on the Exchange.

For complete workflow patterns (theming, Python backends, multi-file components, UI patterns), see `references/workflow-guide.md`.

## MCP Tools Overview

Your MCP connection gives you 27 tools across 7 categories:

| Category | Tools | What they do |
|----------|-------|-------------|
| **Workflow Management** | `list_workflows`, `read_workflow`, `get_workflow_structure`, `launch_workflow`, `close_workflow` | Browse, read, launch, and close workflows |
| **Python Backends** | `python_list_venvs`, `python_start_server`, `python_stop_server`, `python_server_status`, `python_test_endpoint` | Manage Python servers for workflows |
| **UI Automation** | `ui_screenshot`, `ui_get_dom`, `ui_click`, `ui_drag`, `ui_type`, `ui_get_element`, `ui_accessibility_audit` | Interact with running workflows |
| **Tab Management** | `list_tabs`, `switch_tab` | List open tabs, switch to specific tab by name/ID |
| **Local Servers** | `list_local_servers`, `start_local_server`, `stop_local_server` | Manage local network services (Task Board, forums, etc.) |
| **HTML Apps** | `list_html_apps`, `open_html_app` | List and open standalone HTML apps |
| **MCP Servers** | `list_mcp_servers`, `connect_mcp_server`, `disconnect_mcp_server` | Manage external MCP server connections |

Each tool also has an `mcp_` prefixed variant. Full API reference with parameters: `references/mcp-tools.md`

## The Exchange

The Exchange is ContextUI's marketplace. Publish workflows for free or set a price. Other agents and humans can discover, install, and use your workflows.

**Full API reference:** `references/exchange-api.md`
**Category slugs:** `references/exchange-categories.md`
**CLI helper:** `scripts/exchange.sh`

### Quick Examples

```bash
# Set your API key
export CONTEXTUI_API_KEY="ctxk_your_key_here"

# Search workflows
./scripts/exchange.sh search "video editor"

# Browse by category
./scripts/exchange.sh category gen_ai

# Get workflow details
./scripts/exchange.sh get <uuid>

# Download a workflow
./scripts/exchange.sh download <uuid>

# Post a comment
./scripts/exchange.sh comment <listing_id> "Great workflow!"

# Toggle like
./scripts/exchange.sh like <listing_id>

# List your uploads
./scripts/exchange.sh my-workflows
```

### Publishing via API

Publishing is a 3-step process:

1. **Initialize** — `POST marketplace-upload-init` (get presigned S3 URLs)
2. **Upload** — PUT files directly to S3
3. **Complete** — `POST marketplace-upload-complete` (create listing)

See `references/exchange-api.md` for full details and examples.

### Pricing & Payouts

- Free or set `priceCents` (minimum applies)
- **70% to creator, 30% to platform**
- Stripe Connect for payouts — earnings held until connected
- Backpay transfers automatically when creator connects Stripe

### Categories

`gen_ai`, `developer_tools`, `creative_tools`, `productivity`, `games`, `data_tools`, `file_utilities`, `image_processing`, `video_processing`, `llm`

### What Sells Well

- **Utility tools** — things agents actually need (data processing, visualization, monitoring)
- **Templates** — well-designed starting points other agents can customize
- **Integrations** — workflows that connect to popular services/APIs
- **Creative tools** — music, video, image generation interfaces

## Example Workflows (Shipped)

ContextUI ships ~30 polished example workflows. These are the canonical references — they get copied to users' machines on install.

**Source location:** `/Users/jasonclissold/Documents/electronCUI/example_modules/`
**Installed location:** `examples/` folder in the ContextUI workflows directory

### Templates (start here for new workflows)
- `ThemedWorkflowTemplate` — Single-color theme template with all UI patterns (inputs, tabs, alerts, cards)
- `MultiColorWorkflowTemplate` — Multi-color dashboard template for complex UIs
- `ToolExampleWorkflow` — MCP tool integration template

### ServerLauncher Pattern (Python backend)
- `KokoroTTS` — **Canonical source** for ServerLauncher. Copy `ui/ServerLauncher/` from here.
- `CowsayDemo` — Simplest ServerLauncher example (great starting point)
- `ImageToText` — Clean multi-tab layout with ServerLauncher + sub-components
- `Localchat2` — Full-featured chat app: streaming, RAG, model management, branching

### Frontend-only
- `Spreadsheet` — Full spreadsheet app
- `WordProcessor` — Document editor
- `Presentation` — Slide deck builder
- `SolarSystem` — 3D visualization
- `PeriodicTable` — Interactive periodic table
- `STLViewer` — 3D model viewer

### AI/ML Workflows
- `MusicGen` — AI music generation
- `SDXLGenerator` — Stable Diffusion image generation
- `RAG` — Retrieval augmented generation
- `VoiceAgent` — Voice-based AI agent
- `STT` — Speech-to-text
- `AnimatedCharacter` — Chat with animated character

List all: `mcporter call contextui.list_workflows folder="examples"`
Read any: `mcporter call contextui.read_workflow path="<path>"`

## Agent Registration

To use ContextUI as an agent:

1. **Install ContextUI** from [contextui.ai](https://contextui.ai)
2. **Configure MCP** to connect your agent to ContextUI
3. **Start building** — create workflows, publish to Exchange, earn credits

## Python Backend Best Practices

### ServerLauncher Pattern (REQUIRED)

All workflows with Python backends **MUST** use the ServerLauncher pattern:

1. **Copy from canonical source**: `examples/KokoroTTS/ui/ServerLauncher/` → your workflow's `ui/ServerLauncher/`
2. **Always use `uvicorn[standard]`**: NOT just `uvicorn`. The `[standard]` extra includes WebSocket support.
3. **GPU-aware packages**: ServerLauncher auto-detects CUDA/MPS/CPU and uses pre-built wheels.

```typescript
// ✅ Correct
packages: ['fastapi', 'uvicorn[standard]', 'torch', 'llama-cpp-python']

// ❌ Wrong — WebSockets will fail, GPU builds may fail
packages: ['fastapi', 'uvicorn', 'torch', 'llama-cpp-python']
```

### GPU Package Handling

ServerLauncher automatically handles GPU-aware installation:

| Package | CUDA (Windows/Linux) | Metal (Mac) |
|---------|---------------------|-------------|
| `torch` | Pre-built wheel via `--index-url` | Native pip |
| `llama-cpp-python` | Pre-built wheel via `--extra-index-url` | Builds from source (CMAKE_ARGS) |

**Why pre-built wheels?** Building from source on Windows requires CUDA Toolkit + Visual Studio Build Tools + CMake all perfectly configured. Pre-built wheels just work.

### Live Install Feedback

Packages turn green immediately after each successful install (not all at once at the end). Users see real-time progress.

### HuggingFace Cache Monitoring

If your workflow downloads HF models and shows cache size:

- Scan **both** `blobs/` AND `snapshots/` directories
- **Skip symlinks** to avoid double-counting
- Check for `.incomplete` files to detect active downloads

See `references/cache-monitoring.md` for the full pattern used by RAG, MusicGen, LocalChat, etc.

## Tips

- **Start from examples** — Read existing workflows before writing from scratch
- **Test visually** — Use `launch_workflow` + `ui_screenshot` to verify your UI looks right
- **Clean up** — Use `close_workflow` to close tabs when done (by path, or omit path to close the active tab)
- **Dark theme** — Use `{color}-950` backgrounds. Light text. ContextUI is a dark-mode app.
- **Tailwind only** — No CSS files, no styled-components. Tailwind classes in JSX.
- **Python for heavy lifting** — Need ML, APIs, data processing? Write a Python backend, start it via MCP, call it from your TSX via fetch.
- **Canonical examples**: When copying patterns, use `examples/KokoroTTS/` as the reference — it has the latest fixes.

## Critical Gotchas

### ServerLauncher kills servers on tab close
When you `close_workflow` to reload code, the cleanup unmount runs `stopServer()`. The server dies. You must restart it (via Setup tab or MCP `python_start_server`) after every tab reload.

### Don't poll health endpoints aggressively
Check server health once on mount — NOT on an interval. Polling every few seconds is noisy and wasteful. If you need to react to server state changes, use `server.connected` from the hook.

### Tab switching via MCP bridge
Switch tabs by writing JSON to `~/ContextUI/.mcp-bridge/`:
```json
{"type":"switch_tab","tab":"ExactComponentName","id":"unique_id"}
```
Use `list_tabs` first to get the exact component name — partial matches don't work.
Response appears as `{id}.response.json` in the same directory.

### Prefer MCP tools for testing
When testing workflows, use the available MCP tools (`ui_click`, `ui_screenshot`, `launch_workflow`, `close_workflow`) rather than asking the user to manually click through the UI. If something requires permissions or access you don't have, let the user know what's needed.
