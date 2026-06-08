# Execution Contexts, Communication Flows, and Limits

## Table of contents

1. Communication flow diagrams
2. Communication methods matrix
3. Per-context reference cards

## 1. Communication flow diagrams

### Full picture: all contexts and channels

```
                        Extension Process
 ┌──────────────────────────────────────────────────────────────────┐
 │                                                                  │
 │  ┌─────────────────────┐    chrome.runtime.sendMessage()        │
 │  │   Service Worker     │◄──────────────────────────────────┐   │
 │  │   (background)       │───────────────────────────────┐   │   │
 │  └──────────┬───────────┘                               │   │   │
 │        ▲    │                                           │   │   │
 │        │    │ chrome.tabs.sendMessage(tabId, ...)       │   │   │
 │        │    │                                           ▼   │   │
 │        │    │    ┌────────┐  ┌─────────┐  ┌──────────┐     │   │
 │        │    │    │ Popup  │  │ Options  │  │ Side     │     │   │
 │        │    │    │        │  │  Page    │  │ Panel    │     │   │
 │        │    │    └───┬────┘  └────┬────┘  └────┬─────┘     │   │
 │        │    │        │            │             │            │   │
 │        │    │        └────────────┴─────────────┘            │   │
 │        │    │          chrome.runtime.sendMessage()          │   │
 │        │    │          chrome.runtime.connect()              │   │
 │        │    │                                                │   │
 │  chrome.storage.onChanged  ◄──── fires across ALL contexts ─┘   │
 │                                                                  │
 └──────────────────────────────────────────────────────────────────┘
              │
              │ chrome.tabs.sendMessage(tabId, ...)
              ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  Web Page (per tab)                                              │
 │                                                                  │
 │  ┌──────────────────────┐     ┌──────────────────────┐          │
 │  │  Content Script       │     │  Main World Script    │          │
 │  │  (isolated world)     │     │  (page context)       │          │
 │  │                       │◄───►│                       │          │
 │  │  chrome.runtime ──────┼──►  │  No chrome.* APIs     │          │
 │  │  chrome.storage       │     │  Full page JS access  │          │
 │  └──────────────────────┘     └──────────────────────┘          │
 │         ▲        │                    ▲        │                 │
 │         │        │                    │        │                 │
 │         │  window.postMessage()       │  window.postMessage()   │
 │         │  Custom DOM events          │  Custom DOM events      │
 │         │        │                    │        │                 │
 │         └────────┘                    └────────┘                 │
 │              Shared DOM (read/write by both worlds)              │
 └──────────────────────────────────────────────────────────────────┘
```

### Extension-internal messaging (popup/options/sidepanel to service worker)

All extension UI pages share the same origin and use the same API to reach the service worker.

```
  ┌────────┐  ┌─────────┐  ┌───────────┐
  │ Popup  │  │ Options │  │ Side Panel│
  └───┬────┘  └────┬────┘  └─────┬─────┘
      │            │              │
      │  chrome.runtime.sendMessage({ type, payload })
      │  chrome.runtime.connect({ name })
      ▼            ▼              ▼
  ┌──────────────────────────────────────┐
  │          Service Worker              │
  │  chrome.runtime.onMessage.addListener│
  │  chrome.runtime.onConnect.addListener│
  └──────────────────────────────────────┘
      │
      │  (cannot push to popup/options/sidepanel
      │   via tabs.sendMessage — they are not tabs)
      │
      │  Workaround: use chrome.storage.onChanged
      │  or long-lived port (chrome.runtime.connect)
      ▼
```

**Key point**: The service worker cannot initiate messages to popup/options/sidepanel with `sendMessage`. Use ports (bidirectional) or storage change events for SW-to-UI-page communication.

### Content script to service worker (and back)

```
  ┌──────────────────────┐                ┌─────────────────────┐
  │  Content Script       │                │  Service Worker      │
  │  (in tab)             │                │                      │
  │                       │  ──────────►   │                      │
  │  chrome.runtime       │  sendMessage() │  onMessage listener  │
  │    .sendMessage()     │                │                      │
  │                       │  ◄──────────   │                      │
  │  (receives response   │  sendResponse()│                      │
  │   via callback/await) │                │                      │
  │                       │                │                      │
  │  chrome.runtime       │  ◄──────────   │  chrome.tabs         │
  │    .onMessage listener│  tabs.send     │    .sendMessage()    │
  │                       │  Message()     │                      │
  └──────────────────────┘                └─────────────────────┘
```

The SW **must know the tabId** to push messages to a content script. It does not know which tabs have content scripts unless it tracks them (via `chrome.tabs.query` or by content scripts registering on load).

### Three-layer bridge: web page to extension

When the page's own JavaScript (no chrome.* access) needs to talk to the extension:

```
  ┌────────────────┐   window.postMessage    ┌────────────────┐   chrome.runtime     ┌───────────────┐
  │ Page JS         │  ────────────────────►  │ Content Script  │  ──────────────────► │ Service Worker │
  │ (main world)    │                         │ (isolated world)│                      │                │
  │                 │  ◄────────────────────  │ (bridge/relay)  │  ◄────────────────── │                │
  │ No chrome.* API │   window.postMessage    │ chrome.runtime  │   sendResponse()     │ Full chrome.*  │
  └────────────────┘                         └────────────────┘                      └───────────────┘

  Direction key:
    Page  ──► CS  : window.postMessage({ channel, direction: 'TO_EXT', ... })
    CS    ──► SW  : chrome.runtime.sendMessage({ type, payload })
    SW    ──► CS  : sendResponse() (reply) or chrome.tabs.sendMessage() (push)
    CS    ──► Page: window.postMessage({ channel, direction: 'FROM_EXT', ... })
```

Use a unique `channel` string and `direction` field to filter messages. Always validate `event.source === window` on the receiving side.

### Cross-extension messaging

```
  ┌────────────────────┐                      ┌────────────────────┐
  │ Extension A         │  chrome.runtime      │ Extension B         │
  │                     │  .sendMessage(        │                     │
  │ (sender)            │   extB_id, msg)      │ (receiver)          │
  │                     │  ──────────────────► │                     │
  │                     │                      │ onMessageExternal   │
  │                     │  ◄────────────────── │  .addListener()     │
  │                     │  sendResponse()      │                     │
  └────────────────────┘                      └────────────────────┘

  Requires in Extension B's manifest:
    "externally_connectable": { "ids": ["<ext-A-id>"] }
```

### Implicit communication via storage

```
  ┌────────┐  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌────────────────┐
  │ Popup  │  │ Options │  │ SW       │  │ Side Panel │  │ Content Script │
  └───┬────┘  └────┬────┘  └────┬─────┘  └─────┬──────┘  └───────┬────────┘
      │            │            │               │                 │
      │  chrome.storage.local.set({ theme: 'dark' })              │
      │            │            │               │                 │
      ▼            ▼            ▼               ▼                 ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  chrome.storage.onChanged fires in ALL contexts simultaneously      │
  │  No explicit messaging needed for settings/state propagation        │
  └──────────────────────────────────────────────────────────────────────┘
```

This is the simplest way to keep all contexts in sync. Any context writes, all others react.

## 2. Communication methods matrix

| Method | Direction | Use case | Response? | Keeps SW alive? | Size limit |
|--------|-----------|----------|-----------|-----------------|------------|
| `chrome.runtime.sendMessage` | Any ext context -> SW | One-shot request/response | Yes (via sendResponse) | Resets 30s timer | ~64 MB |
| `chrome.tabs.sendMessage` | SW -> content script (by tabId) | Push data to a specific tab | Yes (via sendResponse) | Resets 30s timer | ~64 MB |
| `chrome.runtime.connect` (Port) | Bidirectional, any ext context | Streaming, progress, real-time | Continuous | Yes, while active | ~64 MB/msg |
| `window.postMessage` | Between worlds on same page | Page JS <-> content script | No (use request IDs) | N/A | Structured clone |
| Custom DOM events | Between worlds on same page | Targeted, no cross-origin | No | N/A | JSON-serializable |
| `chrome.storage.onChanged` | Broadcast to all contexts | Settings sync, state propagation | No (fire-and-forget) | Wakes SW | Per storage area |
| `externally_connectable` | Extension <-> extension | Cross-extension RPC | Yes (via sendResponse) | Resets 30s timer | ~64 MB |
| Shared DOM | Content script <-> main world | Read/write DOM elements | N/A | N/A | DOM size |

### When to use which

- **Simple request/response**: `sendMessage` (one-shot, covers 90% of cases)
- **SW pushes to content script**: `tabs.sendMessage` (requires knowing tabId)
- **SW pushes to popup/sidepanel**: storage change events or ports
- **Streaming/progress**: ports (`chrome.runtime.connect`)
- **Page JS to extension**: three-layer bridge via `window.postMessage` + content script relay
- **Settings sync across all contexts**: `chrome.storage.onChanged` (no messaging code needed)

## 3. Per-context reference cards

### Service Worker (background)

| Capability | Status |
|------------|--------|
| DOM access | None |
| chrome.* APIs | All (full API surface) |
| `fetch()` | Yes, bypasses CORS with host_permissions |
| Subject to page CSP | No |
| `localStorage` / `sessionStorage` | Not available |
| `XMLHttpRequest` | Not available (fetch only) |
| Dynamic code generation | Forbidden by MV3 |
| IndexedDB | Yes |
| `chrome.storage.*` | All areas (local, sync, session) |

**Lifetime**: Ephemeral. Terminates after 30s of inactivity. Hard cap of 5 minutes for any single task.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| 30s idle termination | Global variables lost, timers cancelled | Persist state to `chrome.storage.session`; use `chrome.alarms` instead of setTimeout |
| 5-minute hard cap | Long tasks killed | Break into alarm-driven steps; delegate to offscreen document |
| No DOM | Cannot use DOMParser, Canvas, Audio | Create offscreen document with appropriate Reason |
| No localStorage/sessionStorage | Cannot use libraries that depend on them | Use `chrome.storage.session` (same purpose, survives SW restarts) |
| No dynamic code generation | Cannot load remote scripts | Bundle all code at build time |
| Event listeners must be top-level | Listeners inside callbacks are lost on restart | Always register synchronously at module scope; use static imports |
| Cannot push to popup/sidepanel | No tabs.sendMessage for extension pages | Use ports or chrome.storage.onChanged |

### Popup

| Capability | Status |
|------------|--------|
| DOM access | Full (own document) |
| chrome.* APIs | All |
| `fetch()` | Yes, same as SW (extension origin) |
| Subject to page CSP | No (extension CSP applies) |
| `localStorage` | Available but discouraged (not shared, lost on reinstall) |
| Dynamic code generation | Forbidden by MV3 extension CSP |
| `chrome.storage.*` | All areas |

**Lifetime**: Destroyed on blur (clicking outside the popup). No state survives between opens.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| Destroyed on blur | All JS state and DOM lost | Persist any important state to `chrome.storage` before/during interaction |
| Small viewport (800x600 max) | Limited UI real estate | Use side panel for complex UIs that need persistence |
| Cannot be opened programmatically | SW cannot show the popup | Use `chrome.action.openPopup()` (Chrome 127+, requires user gesture) or notifications |
| Extension CSP blocks inline scripts | No `<script>` tags in HTML, no inline event handlers | Use separate .js files; add listeners via addEventListener |

### Options Page

| Capability | Status |
|------------|--------|
| DOM access | Full (own document) |
| chrome.* APIs | All |
| `fetch()` | Yes (extension origin) |
| `localStorage` | Available but discouraged |
| `chrome.storage.*` | All areas |

**Lifetime**: Persistent while tab is open. Survives as long as the user keeps the tab.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| Extension CSP blocks inline scripts | Same as popup | Use separate .js files |
| Dynamic code generation forbidden | Same as popup | Bundle at build time |
| No special limits | Options page is a regular extension page | N/A |

### Side Panel

| Capability | Status |
|------------|--------|
| DOM access | Full (own document) |
| chrome.* APIs | All |
| `fetch()` | Yes (extension origin) |
| `chrome.storage.*` | All areas |

**Lifetime**: Persists while panel is open. Survives navigation in the main tab (unlike popup). Can be global or per-tab.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| One side panel per extension | Cannot show multiple panels | Use tabbed UI within the panel |
| Extension CSP blocks inline scripts | Same as popup | Use separate .js files |
| Chrome 114+ only | Not available on older browsers | Feature-detect with `chrome.sidePanel` check; fall back to popup |

### Content Script (Isolated World) — default

| Capability | Status |
|------------|--------|
| DOM access | Full (shared with page) |
| chrome.* APIs | Limited: `runtime`, `storage`, `i18n` only |
| `fetch()` | Subject to page's CSP `connect-src` and CORS |
| Page JS variables | Not accessible (separate JS scope) |
| `localStorage` | Page's localStorage (not extension's) |
| `chrome.storage.*` | local: yes, sync: yes, session: only if access level set |

**Lifetime**: Lives as long as the page. Orphaned on extension update (loses chrome.runtime).

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| Page CSP blocks fetch to external APIs | Cannot call your API directly | Relay through service worker (the standard pattern) |
| No chrome.tabs, chrome.scripting, etc. | Cannot manage tabs or inject into other pages | Send message to SW, let SW handle it |
| Orphaned on extension update | All chrome.runtime calls throw | Check `chrome.runtime?.id` before calls; show refresh banner |
| Cannot access page JS variables | Cannot read SPA state, intercept fetch | Inject a main-world script and bridge via postMessage |
| Page can't see content script variables | Page JS cannot call your functions | Use window.postMessage or custom DOM events |
| Subject to page CORS | Cross-origin fetch may fail even if CSP allows it | Relay through SW (SW with host_permissions bypasses CORS) |

### Content Script (Main World)

| Capability | Status |
|------------|--------|
| DOM access | Full (shared with page) |
| chrome.* APIs | None |
| `fetch()` | Subject to page's full CSP and CORS |
| Page JS variables | Full access (same scope as page) |
| `localStorage` | Page's localStorage |
| `chrome.storage.*` | Not available |

**Lifetime**: Same as page. Runs in the page's JS context.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| No chrome.* APIs at all | Cannot message SW, cannot use storage | Bridge through isolated-world content script via postMessage/DOM events |
| Subject to full page CSP | Cannot load external scripts, restricted fetch | All code must be bundled; relay network through content script -> SW |
| Page can tamper with your code | Page can override prototypes, intercept calls | Capture references to builtins at `document_start` before page runs |
| No direct extension storage | Cannot persist data | Send data to content script (isolated) via postMessage, which writes to chrome.storage |

### Offscreen Document

| Capability | Status |
|------------|--------|
| DOM access | Full (own document, not visible) |
| chrome.* APIs | `chrome.runtime` only |
| `fetch()` | Yes (extension origin, bypasses page CSP) |
| `localStorage` | Available (extension origin) |
| Canvas, Audio, DOMParser | All available |
| `chrome.storage.*` | Not directly (only via messaging to SW) |

**Lifetime**: Created on demand, persists until closed or browser restart. One per extension.

**Hard limits and workarounds**:

| Limit | Impact | Workaround |
|-------|--------|------------|
| Only chrome.runtime API | Cannot use tabs, scripting, etc. | Message the SW for anything beyond runtime |
| One per extension | Cannot run multiple offscreen tasks in parallel | Multiplex: use message types to route different tasks to the same document |
| Must specify a Reason enum | Chrome validates the reason matches usage | Pick the correct Reason (DOM_PARSER, AUDIO_PLAYBACK, CLIPBOARD, etc.) |
| Not visible to user | Cannot render UI | Only for background DOM work; use popup/sidepanel for UI |
