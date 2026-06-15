# ContextUI MCP Tools — Full API Reference

27 tools available via MCP server (each also has an `mcp_` prefixed variant).

---

## Workflow Management

### list_workflows

List workflow folders and their contents.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `folder` | string | No | Subfolder to list (e.g., `"examples/MusicGen"`). Omit for top-level folders. |

```bash
mcporter call contextui.list_workflows
mcporter call contextui.list_workflows folder="examples"
mcporter call contextui.list_workflows folder="user_workflows/BBAvatar"
```

### read_workflow

Read workflow source code.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Absolute path to workflow file |

```bash
mcporter call contextui.read_workflow path="/path/to/WorkflowWindow.tsx"
```

### get_workflow_structure

Get complete directory tree of all workflows. No parameters.

```bash
mcporter call contextui.get_workflow_structure
```

### launch_workflow

Launch a workflow in the ContextUI app (opens as a docked tab).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Absolute path to the `.tsx` or `.jsx` file |

```bash
mcporter call contextui.launch_workflow path="/path/to/WorkflowWindow.tsx"
```

### close_workflow

Close a workflow tab in the ContextUI app. If no path is provided, closes the currently active tab.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | No | Absolute path to the `.tsx` or `.jsx` file to close. Omit to close the active tab. |

```bash
# Close a specific workflow
mcporter call contextui.close_workflow path="/path/to/WorkflowWindow.tsx"

# Close the active tab
mcporter call contextui.close_workflow
```

---

## Python Backend Management

### python_list_venvs

List available Python virtual environments. No parameters.

```bash
mcporter call contextui.python_list_venvs
```

### python_start_server

Start a local Python backend server (FastAPI/Flask) for a workflow. Runs an existing local script using a pre-configured virtual environment. Server binds to localhost (127.0.0.1) only — not externally accessible.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `venvName` | string | Yes | Python venv name (from `python_list_venvs`) |
| `scriptPath` | string | Yes | Absolute path to existing local Python script |
| `port` | number | Yes | Port number (localhost-bound) |
| `serverName` | string | Yes | Unique server identifier |

```bash
mcporter call contextui.python_start_server venvName="myenv" scriptPath="/path/to/server.py" port=8800 serverName="my-backend"
```

### python_stop_server

Stop a running Python server.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `serverName` | string | Yes | Server identifier used when starting |

```bash
mcporter call contextui.python_stop_server serverName="my-backend"
```

### python_server_status

Get status of running Python servers.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `serverName` | string | No | Specific server name. Omit for all servers. |

```bash
mcporter call contextui.python_server_status
mcporter call contextui.python_server_status serverName="my-backend"
```

### python_test_endpoint

Make an HTTP request to test a Python server endpoint.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Full URL (e.g., `http://127.0.0.1:8800/status`) |
| `method` | string | No | HTTP method (GET, POST, PUT, DELETE). Default: GET |
| `body` | object | No | Request body for POST/PUT |
| `headers` | object | No | Additional HTTP headers |

```bash
mcporter call contextui.python_test_endpoint url="http://127.0.0.1:8800/status"
mcporter call contextui.python_test_endpoint url="http://127.0.0.1:8800/generate" method="POST" body='{"text":"hello"}'
```

---

## UI Automation

### ui_screenshot

Capture a screenshot of the current workflow or app window.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | string | No | `"active_tab"` (default) or `"full_window"` |
| `selector` | string | No | CSS selector to capture specific element |

```bash
mcporter call contextui.ui_screenshot
mcporter call contextui.ui_screenshot target="full_window"
mcporter call contextui.ui_screenshot selector=".my-chart"
```

### ui_get_dom

Get the DOM tree structure of the current workflow.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `depth` | number | No | Max traversal depth (default: 3) |
| `includeStyles` | boolean | No | Include computed styles (default: false) |
| `selector` | string | No | CSS selector to scope query |
| `includeHidden` | boolean | No | Include hidden elements (default: false) |
| `maxElements` | number | No | Max elements to return (default: 50) |

```bash
mcporter call contextui.ui_get_dom
mcporter call contextui.ui_get_dom depth=5 selector=".data-table"
```

### ui_click

Click on an element by selector, text, or coordinates.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `selector` | string | No | CSS selector |
| `text` | string | No | Text content to find (buttons, links, labels) |
| `coordinates` | object | No | `{x, y}` relative to workflow container |
| `button` | string | No | `"left"` (default), `"right"`, `"middle"` |
| `doubleClick` | boolean | No | Double-click instead of single |

```bash
mcporter call contextui.ui_click text="Submit"
mcporter call contextui.ui_click selector="#save-btn"
mcporter call contextui.ui_click coordinates='{"x":100,"y":200}'
```

### ui_drag

Drag from one point to another. For sliders, use selector + value.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `selector` | string | No | CSS selector (preferred for sliders) |
| `value` | number | No | For range inputs: set slider to this value |
| `startCoordinates` | object | No | `{x, y}` start point |
| `endCoordinates` | object | No | `{x, y}` end point |
| `steps` | number | No | Intermediate mousemove events (default: 10) |

```bash
mcporter call contextui.ui_drag selector="input[type=range]" value=75
mcporter call contextui.ui_drag startCoordinates='{"x":100,"y":200}' endCoordinates='{"x":300,"y":200}'
```

### ui_type

Type text into an input field.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `selector` | string | No | CSS selector. Omit to use focused/first input. |
| `text` | string | Yes | Text to type |
| `clear` | boolean | No | Clear existing value first (default: true) |
| `pressEnter` | boolean | No | Press Enter after typing |
| `delay` | number | No | Delay between keystrokes in ms |

```bash
mcporter call contextui.ui_type text="Hello, world!"
mcporter call contextui.ui_type selector="#search" text="query" pressEnter=true
```

### ui_get_element

Get properties of an element (visibility, enabled state, text, bounds).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `selector` | string | No | CSS selector |
| `text` | string | No | Find element by text content |

```bash
mcporter call contextui.ui_get_element text="Submit"
mcporter call contextui.ui_get_element selector=".status-indicator"
```

### ui_accessibility_audit

Run an axe-core accessibility audit.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `selector` | string | No | CSS selector to scope audit |
| `rules` | string[] | No | Specific rule IDs to run |
| `tags` | string[] | No | Filter by tags (e.g., `wcag2a`, `wcag2aa`) |

```bash
mcporter call contextui.ui_accessibility_audit
mcporter call contextui.ui_accessibility_audit tags='["wcag2aa"]'
```

---

## Tab Management

### list_tabs

List all open tabs in the ContextUI layout. Returns array of tab objects with `id`, `name`, `component`, and `visible` status.

```bash
mcporter call contextui.list_tabs
```

### switch_tab

Switch to a specific tab by name or ID. Use `list_tabs` first to get exact names.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `tab` | string | Yes | Exact tab/component name to switch to |
| `id` | string | No | FlexLayout node ID for disambiguation |

```bash
mcporter call contextui.switch_tab tab="MCPServersWindow"
mcporter call contextui.switch_tab tab="MyWorkflow" id="node-123"
```

---

## Local Server Management

Servers are auto-discovered from `~/ContextUI/<profile>/local_servers/*/server.json`.

### list_local_servers

List all configured local servers with running status (health check on their port).

```bash
mcporter call contextui.list_local_servers
```

### start_local_server

Start a local server by ID, name, or port.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | Server folder ID |
| `name` | string | No | Server name (from server.json) |
| `port` | number | No | Server port number |

```bash
mcporter call contextui.start_local_server id="task-board"
mcporter call contextui.start_local_server name="Office Forum"
mcporter call contextui.start_local_server port=8850
```

### stop_local_server

Stop a running local server by ID, name, or port.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | Server folder ID |
| `name` | string | No | Server name (from server.json) |
| `port` | number | No | Server port number |

```bash
mcporter call contextui.stop_local_server id="task-board"
mcporter call contextui.stop_local_server port=8860
```

---

## HTML Apps

Apps are auto-discovered from `~/ContextUI/<profile>/html_apps/*/app.json`.

### list_html_apps

List all configured HTML apps.

```bash
mcporter call contextui.list_html_apps
```

### open_html_app

Open an HTML app by ID or name (opens in system default app).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | App folder ID |
| `name` | string | No | App name (from app.json) |

```bash
mcporter call contextui.open_html_app id="my-dashboard"
mcporter call contextui.open_html_app name="My Dashboard"
```

---

## MCP Server Management

Manage external MCP server connections (the same servers shown in MCPServersWindow).

### list_mcp_servers

List all configured external MCP servers with connection status and tool counts.

```bash
mcporter call contextui.list_mcp_servers
```

### connect_mcp_server

Connect to a local MCP (Model Context Protocol) server for tool integration — similar to configuring extensions in an IDE. Transport is auto-detected. All connections are persisted in a visible config file and shown in the ContextUI UI, so the user can review and disconnect at any time.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name for the server |
| `command` | string | Yes | Stdio command or HTTP URL for an MCP server |

```bash
# Stdio server
mcporter call contextui.connect_mcp_server name="Filesystem" command="npx -y @modelcontextprotocol/server-filesystem /tmp"

# HTTP server
mcporter call contextui.connect_mcp_server name="Remote" command="http://localhost:3000/mcp"
```

### disconnect_mcp_server

Disconnect from an external MCP server by ID or name.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | Server ID |
| `name` | string | No | Server name |

```bash
mcporter call contextui.disconnect_mcp_server name="Filesystem"
```

Server configs are persisted in `~/ContextUI/.mcp-servers.json`.
