---
name: chrome-extension
description: "Comprehensive guide for building Chrome extensions with Manifest V3. Use this skill whenever the user mentions Chrome extension, browser extension, manifest.json, content script, service worker (in extension context), popup, side panel, chrome.runtime, chrome.tabs, chrome.storage, chrome.scripting, background script, MV3, Manifest V3, or any Chrome extension API. Also trigger when the user wants to inject scripts into web pages, communicate between page and background, bypass CSP from a content script, build an RPC layer over chrome messaging, or publish to the Chrome Web Store. Covers both new extension projects and adding features to existing ones. Do NOT use for framework-specific questions.
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents. Requires git, node.
metadata:
  author: samber
  version: "1.0.0"
  openclaw:
    emoji: "📝"
    homepage: https://github.com/samber/cc-skills
    requires:
      bins:
        - git
        - node
        - npm
allowed-tools: Read Edit Write Glob Grep Bash(git:*) Bash(gh:*) Bash(npm:*)
---

# Chrome Extension Development (Manifest V3)

This skill covers everything needed to build, debug, and publish Chrome extensions with MV3.
It is organized as a routing document: read this file first to understand the architecture and decision points, then load the relevant reference file for implementation details.

## Reference files

Read only the reference files relevant to the current task. Each file is self-contained.

| File                                     | When to read                                                                                      |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `references/manifest-v3.md`              | Setting up or modifying manifest.json, configuring icons, versioning                              |
| `references/service-worker.md`           | Background logic, lifecycle, state persistence, alarms, events                                    |
| `references/content-scripts.md`          | Injecting code into pages, isolated/main world, dynamic injection, SPA handling, orphaning        |
| `references/messaging-rpc.md`            | Communication between any contexts, typed protocols, RPC layer, async handler patterns            |
| `references/ui-surfaces.md`              | Popup, options page, side panel, context menus, commands, notifications, omnibox, devtools panel  |
| `references/storage.md`                  | chrome.storage (local/sync/session), quotas, reactive patterns, framework hooks                   |
| `references/network-csp.md`              | HTTP requests from content scripts, CSP bypass relay, declarativeNetRequest, offscreen docs, CORS |
| `references/permissions.md`              | Required/optional permissions, host permissions, activeTab, runtime request flow                  |
| `references/web-accessible-resources.md` | Exposing extension files to web pages, security implications                                      |
| `references/typescript-build.md`         | TypeScript setup, project structure, build tools comparison, bundling                             |
| `references/publishing.md`               | Chrome Web Store submission, review process, rejection reasons, updates, privacy policy           |
| `references/execution-contexts.md`       | Communication flow diagrams, per-context capabilities/limits, choosing the right messaging method |
| `references/debugging-mistakes.md`       | DevTools for extensions, testing SW termination, common gotchas, error patterns                   |

## Architecture overview

A Chrome extension has up to 5 execution contexts that communicate via message passing:

```
┌──────────────────────────────────────────────────────────┐
│ Extension Process                                        │
│  ┌─────────────────┐  ┌───────┐  ┌─────────┐  ┌──────┐ │
│  │ Service Worker   │  │ Popup │  │ Options │  │ Side │ │
│  │ (background)     │  │       │  │  Page   │  │Panel │ │
│  │ - No DOM         │  │ Full  │  │  Full   │  │ Full │ │
│  │ - Ephemeral      │  │ DOM   │  │  DOM    │  │ DOM  │ │
│  │ - All chrome.*   │  │ All   │  │  All    │  │ All  │ │
│  │   APIs           │  │ APIs  │  │  APIs   │  │ APIs │ │
│  └────────┬─────────┘  └───┬───┘  └────┬────┘  └──┬───┘ │
│           │ chrome.runtime.sendMessage / connect   │     │
└───────────┼────────────────┼───────────┼──────────┼──────┘
            │                │           │          │
    chrome.tabs.sendMessage  │           │          │
            │                │           │          │
┌───────────┼────────────────┼───────────┼──────────┼──────┐
│ Web Page  ▼                                              │
│  ┌──────────────────┐    ┌──────────────────┐            │
│  │ Content Script    │    │ Main World Script │            │
│  │ (isolated world)  │◄──►│ (page context)    │            │
│  │ - Shared DOM      │    │ - Shared DOM      │            │
│  │ - Own JS scope    │    │ - Page JS scope   │            │
│  │ - chrome.runtime  │    │ - No chrome.* API │            │
│  │ - chrome.storage  │    │ - Full page access│            │
│  │ - Subject to CSP  │    │ - Subject to CSP  │            │
│  │   (network only)  │    │   (fully)         │            │
│  └──────────────────┘    └──────────────────┘            │
│           ▲ window.postMessage                           │
│           │ (through shared DOM)                         │
└──────────────────────────────────────────────────────────┘
```

### Communication flows (labeled channels)

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Extension Process                                                         │
│                                                                           │
│  ┌─────────────────┐  chrome.runtime   ┌───────┐  ┌─────────┐  ┌──────┐ │
│  │ Service Worker   │◄─.sendMessage()──│ Popup │  │ Options │  │ Side │ │
│  │ (background)     │◄─.connect()──────│       │  │  Page   │  │Panel │ │
│  │                  │                  └───────┘  └─────────┘  └──────┘ │
│  │ - No DOM         │  ┌────────────────────────────────────────────┐   │
│  │ - Ephemeral 30s  │  │ SW cannot push to these pages.             │   │
│  │ - All chrome.*   │  │ Use: ports (.connect) or storage.onChanged │   │
│  └────────┬─────────┘  └────────────────────────────────────────────┘   │
│           │                                                              │
│  chrome.storage.onChanged ◄── fires across ALL contexts simultaneously  │
│                                                                           │
└───────────┼──────────────────────────────────────────────────────────────┘
            │ chrome.tabs.sendMessage(tabId, ...) [SW must know tabId]
            │
┌───────────┼──────────────────────────────────────────────────────────────┐
│ Web Page  ▼                                                              │
│  ┌──────────────────┐  window.postMessage  ┌──────────────────┐         │
│  │ Content Script    │◄───────────────────►│ Main World Script │         │
│  │ (isolated world)  │  Custom DOM events  │ (page context)    │         │
│  │                   │                     │                   │         │
│  │ chrome.runtime ───┼── to/from SW        │ No chrome.* APIs  │         │
│  │ chrome.storage    │                     │ Full page JS      │         │
│  │ Shared DOM        │                     │ Shared DOM        │         │
│  │ Page CSP (network)│                     │ Page CSP (full)   │         │
│  └──────────────────┘                     └──────────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
```

For detailed flow diagrams (three-layer bridge, cross-extension, storage broadcast) and a per-context breakdown of permissions, limits, and workarounds:
→ Read `references/execution-contexts.md`

### Communication methods at a glance

| Method | Direction | Best for |
|--------|-----------|----------|
| `chrome.runtime.sendMessage` | Any ext context → SW | One-shot request/response (90% of cases) |
| `chrome.tabs.sendMessage` | SW → content script (by tabId) | Pushing data to a specific tab |
| `chrome.runtime.connect` (Port) | Bidirectional | Streaming, progress, SW ↔ popup |
| `window.postMessage` | Between worlds on same page | Page JS ↔ content script bridge |
| `chrome.storage.onChanged` | Broadcast to all contexts | Settings sync, no messaging needed |

→ Full matrix with limits and edge cases: `references/execution-contexts.md`
→ Implementation patterns, typed protocols, RPC layer: `references/messaging-rpc.md`

### Key architectural rules

1. **Service worker is ephemeral.** It terminates after 30s of inactivity. All state must be persisted to chrome.storage. All event listeners must be registered synchronously at the top level. Never use setTimeout/setInterval for anything beyond a few seconds.
   → Read `references/service-worker.md`

2. **Content scripts run in the page's origin.** Network requests from content scripts are subject to the page's CSP and CORS. To bypass, relay through the service worker.
   → Read `references/network-csp.md`

3. **Messaging is the backbone.** Every cross-context interaction uses chrome.runtime messaging.
   The #1 bug: forgetting to `return true` from async message listeners.
   → Read `references/messaging-rpc.md`

4. **Permissions determine CWS review speed.** Broad host_permissions trigger manual review (weeks). activeTab + optional permissions = fast automated review.
   → Read `references/permissions.md`

5. **Popup is destroyed on blur.** Side panel persists. Choose based on interaction duration.
   → Read `references/ui-surfaces.md`

## Decision tree: which context handles what?

### "I need to run code when the user visits a page"
→ Content script. Static (manifest) for known URL patterns, dynamic (chrome.scripting) for user-triggered injection. Default to isolated world unless you need page JS access.
→ Read `references/content-scripts.md`

### "I need to make an HTTP request to my API"
- From popup/options/side panel: direct fetch() works (extension origin, no CSP issues)
- From content script on a page with restrictive CSP: relay through service worker
- From service worker: direct fetch() works (requires host_permissions for the target domain)
→ Read `references/network-csp.md`

### "I need to store user settings"
- Settings that sync across devices: chrome.storage.sync (100KB limit)
- Large data or caches: chrome.storage.local (10MB, or unlimited with permission)
- Ephemeral state surviving SW restarts: chrome.storage.session
→ Read `references/storage.md`

### "I need to modify HTTP headers or block requests"
→ declarativeNetRequest (NOT webRequest, which lost blocking in MV3)
→ Read `references/network-csp.md`

### "I need the page's JavaScript to talk to my extension"
→ Three-layer bridge: page (window.postMessage) → content script → service worker
→ Read `references/messaging-rpc.md`

### "I need to understand what each context can and cannot do"
→ Read `references/execution-contexts.md` — per-context cards listing chrome.* access, DOM, network, storage, lifetime, hard limits, and practical workarounds.

### "I need periodic background tasks"
→ chrome.alarms (minimum 30s interval). NOT setTimeout.
→ Read `references/service-worker.md`

### "I need DOM APIs in the background" (DOMParser, Canvas, Audio)
→ Offscreen document. One per extension, only chrome.runtime available.
→ Read `references/network-csp.md`

### "I need to authenticate with OAuth"
→ chrome.identity.launchWebAuthFlow() or chrome.identity.getAuthToken() (Google only)
→ Read `references/service-worker.md` (identity section)

## Workflow: new extension from scratch

1. **Define the manifest** with minimum permissions. Start with `activeTab` + `scripting`.
   → Read `references/manifest-v3.md`

2. **Set up TypeScript and build tooling** (or use CRXJS for Vite-based dev).
   → Read `references/typescript-build.md`

3. **Implement the service worker** with all event listeners at the top level.
   → Read `references/service-worker.md`

4. **Add content scripts** if you need page interaction.
   → Read `references/content-scripts.md`

5. **Build UI surfaces** (popup, options, side panel) as needed.
   → Read `references/ui-surfaces.md`

6. **Wire up messaging** between all contexts.
   → Read `references/messaging-rpc.md`

7. **Test with DevTools**, specifically test service worker termination.
   → Read `references/debugging-mistakes.md`

8. **Publish to Chrome Web Store.**
   → Read `references/publishing.md`

## Workflow: adding a feature to an existing extension

1. Identify which context the feature belongs to (see decision tree above).
2. Read the relevant reference file(s) for that context.
3. Check if new permissions are needed. Prefer optional_permissions for new capabilities.
   → Read `references/permissions.md`
4. Update the manifest if adding new content scripts, UI surfaces, or permissions.
5. Handle extension updates gracefully (content script orphaning).
   → Read `references/content-scripts.md` (orphaning section)

## Minimal manifest.json template

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "What it does in one sentence",
  "permissions": ["storage", "activeTab", "scripting"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

→ For the full manifest reference with all fields: `references/manifest-v3.md`

## Code patterns quick reference

### Async message handler (the safe pattern)

```typescript
// Wrap async handlers to avoid the return-true trap
function asyncHandler(fn: (msg: any, sender: chrome.runtime.MessageSender) => Promise<any>) {
  return (message: any, sender: chrome.runtime.MessageSender, sendResponse: (r: any) => void) => {
    fn(message, sender)
      .then(sendResponse)
      .catch(e => sendResponse({ __error: true, message: e.message }));
    return true; // literal true, not Promise<true>
  };
}

chrome.runtime.onMessage.addListener(asyncHandler(async (msg, sender) => {
  if (msg.type === 'FETCH') {
    const res = await fetch(msg.url);
    return { ok: res.ok, data: await res.text() };
  }
}));
```

### CSP bypass relay (content script → service worker → API)

```typescript
// content-script.ts
async function apiCall(endpoint: string, options?: RequestInit) {
  return chrome.runtime.sendMessage({ type: 'API_RELAY', endpoint, options });
}

// background.ts
const ALLOWED_ENDPOINTS = ['https://api.example.com'];
chrome.runtime.onMessage.addListener(asyncHandler(async (msg) => {
  if (msg.type !== 'API_RELAY') return;
  if (!ALLOWED_ENDPOINTS.some(e => msg.endpoint.startsWith(e))) {
    throw new Error('Blocked endpoint');
  }
  const res = await fetch(msg.endpoint, msg.options);
  return { ok: res.ok, status: res.status, data: await res.text() };
}));
```

### Persist state across SW restarts

```typescript
// Use chrome.storage.session for ephemeral state
chrome.storage.session.setAccessLevel({ accessLevel: 'TRUSTED_AND_UNTRUSTED_CONTEXTS' });

async function getState<T>(key: string, fallback: T): Promise<T> {
  const result = await chrome.storage.session.get(key);
  return result[key] ?? fallback;
}
async function setState<T>(key: string, value: T): Promise<void> {
  await chrome.storage.session.set({ [key]: value });
}
```

### Orphaned content script detection

```typescript
function isExtensionContextValid(): boolean {
  try { return !!chrome.runtime?.id; }
  catch { return false; }
}

// Before any chrome.runtime call
if (!isExtensionContextValid()) {
  showRefreshBanner();
  return;
}
```

## What NOT to do

- Do NOT use `eval()`, `new Function()`, or load remote scripts. MV3 forbids it.
- Do NOT use `setTimeout`/`setInterval` for anything > 5s in service workers.
- Do NOT register event listeners inside callbacks or async functions.
- Do NOT use `<all_urls>` host permission unless absolutely necessary.
- Do NOT rely on DevTools keeping the service worker alive during testing.
- Do NOT forget `return true` in async message listeners.
- Do NOT use `localStorage` or `sessionStorage` in service workers (they don't exist there).
- Do NOT assume content scripts survive extension updates.
- Do NOT use `webRequest` blocking (removed in MV3). Use `declarativeNetRequest`.
- Do NOT use `chrome.extension.getBackgroundPage()` (removed in MV3).
