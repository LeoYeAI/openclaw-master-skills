# ServerLauncher — Python Backend Pattern (v3.0.0)

The standard pattern for any ContextUI workflow with a Python backend. Two files handle everything: Python detection → venv selection → GPU detection → package installation (GPU-aware) → server start/stop → connection polling. Cross-platform (Windows, macOS, Linux).

## Overview

Every Python-backed workflow follows the same structure:
1. Copy `ui/ServerLauncher/` (2 files) from **`examples/KokoroTTS/ui/ServerLauncher/`** (canonical source)
2. Call `useServerLauncher()` with a simple config object
3. Render `<ServerLauncher server={server} />` for the setup UI
4. Use `server.connected` and `server.serverUrl` in your workflow tabs

**User experience:** Open workflow → select venv → click "Install All" → click "Start Server" → use the workflow. Or enable auto-start and it handles everything automatically.

## ⚠️ Canonical Source

**Always copy from `examples/KokoroTTS/ui/ServerLauncher/`** — this is the canonical, tested version with all features:

- ✅ GPU detection (CUDA/MPS/CPU)
- ✅ GPU-aware PyTorch installation (auto wheel selection)
- ✅ GPU-aware llama-cpp-python (CMAKE_ARGS)
- ✅ Import validation (catches broken packages)
- ✅ Connection error feedback
- ✅ Download progress monitoring
- ✅ CreateVenvForm as separate component (prevents input focus loss)

Other examples may have older copies. When in doubt, sync from KokoroTTS.

## File Structure

```
YourWorkflow/
├── YourWorkflowWindow.tsx       # Main entry — hook init, tabs, connection check
├── YourWorkflow.meta.json       # Icon, color metadata
├── your_server.py               # FastAPI backend
└── ui/
    ├── YourFeatureTab.tsx        # Your main workflow UI
    └── ServerLauncher/           # Copy this directory (2 files)
        ├── useServerLauncher.ts  # Hook — all logic, zero external deps
        └── ServerLauncher.tsx    # UI component — drop-in setup panel
```

That's it. Two files in `ServerLauncher/`, your server script, your feature UI, and a main window.

## Quick Integration

### Step 1: Copy ServerLauncher

Copy `ui/ServerLauncher/` from **`examples/KokoroTTS/ui/ServerLauncher/`** into your workflow. This is the canonical source with GPU detection and all v3.0.0 features.

### Step 2: Write Your Python Server

Standard FastAPI server with a `/health` or root endpoint:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, sys

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Your endpoints here...

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Step 3: Hook + Component

```tsx
import { useServerLauncher } from './ui/ServerLauncher/useServerLauncher';
import { ServerLauncher } from './ui/ServerLauncher/ServerLauncher';

export const MyWorkflowWindow: React.FC = () => {
  const server = useServerLauncher({
    workflowFolder: 'MyWorkflow',
    scriptName: 'my_server.py',
    port: 8800,
    serverName: 'my-server',
    packages: ['fastapi', 'uvicorn[standard]', 'numpy'],
  });

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white">
      {server.connected ? (
        <MyFeatureUI serverUrl={server.serverUrl} />
      ) : (
        <ServerLauncher server={server} title="My Workflow" />
      )}
    </div>
  );
};
```

Done. That's the entire integration.

## Config Reference

```typescript
useServerLauncher({
  workflowFolder: string;   // Folder name (e.g., 'MyWorkflow')
  scriptName: string;        // Python script (e.g., 'server.py')
  port: number;              // Default port (e.g., 8800)
  serverName: string;        // Unique ID for IPC (e.g., 'my-server')
  packages?: string[];       // Pip packages (e.g., ['fastapi', 'torch'])
  preferredVenvs?: string[]; // Venv preference order (default: ['default'])
});
```

## ServerHandle (returned by hook)

### State
| Field | Type | Description |
|-------|------|-------------|
| `pythonInstalled` | `boolean \| null` | null = checking, true/false = result |
| `installingPython` | `boolean` | Currently installing Python |
| `availableVenvs` | `string[]` | Detected venvs |
| `selectedVenv` | `string` | Currently selected venv |
| `port` | `number` | Current port |
| `portFree` | `boolean \| null` | Port availability |
| `packages` | `string[]` | Required packages list |
| `depsStatus` | `DepsStatus` | Per-package install status |
| `checkingDeps` | `boolean` | Currently checking packages |
| `installingDeps` | `boolean` | Currently installing packages |
| `allDepsInstalled` | `boolean` | All packages installed |
| `serverRunning` | `boolean` | Server process started |
| `connected` | `boolean` | Server responding to HTTP |
| `connecting` | `boolean` | Waiting for connection |
| `serverUrl` | `string` | `http://127.0.0.1:{port}` |
| `autoStart` | `boolean` | Auto-start preference |
| `logs` | `string[]` | Activity log |
| `creatingVenv` | `boolean` | Currently creating venv |

### Actions
| Method | Description |
|--------|-------------|
| `setSelectedVenv(v)` | Select a venv |
| `setPort(p)` | Change port |
| `setAutoStart(v)` | Toggle auto-start |
| `installPython()` | Install Python 3.12 |
| `installDeps()` | Install missing packages |
| `startServer()` | Start the Python server |
| `stopServer()` | Stop the Python server |
| `createVenv(name)` | Create a new venv |
| `addLog(msg)` | Add a log entry |

## ServerLauncher Component Props

```tsx
<ServerLauncher
  server={server}           // Required: ServerHandle from hook
  title="My Workflow"       // Optional: header text (default: "Server Setup")
  launchLabel="Launch"      // Optional: button text (default: "Start Server")
  accentColor="bg-cyan-500 hover:bg-cyan-400"  // Optional: Tailwind classes
/>
```

The component renders everything: venv picker, port selector, package status, install button, start/stop button, and logs. All self-contained — manages its own venv creation UI state internally.

## Tab Pattern (optional)

If your workflow has Setup + Feature tabs:

```tsx
const [tab, setTab] = useState<'setup' | 'main'>('setup');

useEffect(() => {
  if (server.connected) setTab('main');
}, [server.connected]);

// In JSX:
{tab === 'setup' ? (
  <ServerLauncher server={server} title="My Workflow" />
) : (
  <MyFeatureTab serverUrl={server.serverUrl} />
)}
```

## What the Hook Handles Automatically

- **Python detection** — checks installed versions on mount
- **Venv loading** — lists available venvs, auto-selects preferred or last-used
- **Package checking** — re-checks when venv or packages change
- **Port checking** — tests availability when port changes
- **Connection polling** — polls server every 1s after start until connected
- **Settings persistence** — remembers port, venv, auto-start per workflow in localStorage
- **Auto-start** — starts server automatically when deps are ready (if enabled)
- **Cleanup** — stops server on unmount
- **Live install feedback** — packages turn green immediately after each successful install
- **GPU-aware installation** — auto-detects CUDA/MPS/CPU, uses pre-built wheels for torch and llama-cpp-python

## Common Package Sets

```typescript
// Web server (almost every workflow)
// ⚠️ ALWAYS use uvicorn[standard], not just uvicorn — includes websockets support!
packages: ['fastapi', 'uvicorn[standard]']

// Data science
packages: ['fastapi', 'uvicorn[standard]', 'numpy', 'pandas', 'matplotlib']

// Machine learning (GPU-aware: auto-detects CUDA/MPS/CPU)
packages: ['fastapi', 'uvicorn[standard]', 'torch', 'torchvision']

// LLM inference (llama-cpp-python uses pre-built CUDA wheels on Windows)
packages: ['fastapi', 'uvicorn[standard]', 'torch', 'llama-cpp-python']

// Audio processing
packages: ['fastapi', 'uvicorn[standard]', 'soundfile', 'scipy']
```

## ⚠️ Critical Requirements

### Always Use `uvicorn[standard]`
Do NOT use just `uvicorn` — use `uvicorn[standard]`. The `[standard]` extra includes `websockets` which is required for WebSocket endpoints. Without it, FastAPI WebSocket routes will fail silently.

### Copy ServerLauncher From Canonical Source
Always copy `ui/ServerLauncher/` from `examples/KokoroTTS/ui/ServerLauncher/`. This is the canonical, tested version. Other examples may have older copies.


## Source Code

The source code is maintained in the canonical location. **Do not embed copies in documentation** as they become outdated.

**Canonical source:** `examples/KokoroTTS/ui/ServerLauncher/`

Files:
- `useServerLauncher.ts` — Hook (~600 lines, v3.0.0)
- `ServerLauncher.tsx` — UI component (~200 lines, v3.0.0)

To view the current implementation:
```bash
mcporter call contextui.read_workflow path="examples/KokoroTTS/ui/ServerLauncher/useServerLauncher.ts"
mcporter call contextui.read_workflow path="examples/KokoroTTS/ui/ServerLauncher/ServerLauncher.tsx"
```
