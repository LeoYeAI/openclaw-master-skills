# Messaging and RPC Reference

## Table of contents
1. One-shot messaging (sendMessage)
2. The async handler trap and fix
3. Port-based long-lived connections
4. Service worker → content script
5. Full three-layer bridge: page ↔ content script ↔ service worker
6. Typed message protocol with discriminated unions
7. Full RPC layer (simulate HTTP through messaging)
8. Cross-extension messaging
9. Common messaging bugs

## 1. One-shot messaging (sendMessage)

The simplest pattern: send a message, get one response.

```typescript
// Content script or popup → service worker
const response = await chrome.runtime.sendMessage({ type: 'GET_DATA', key: 'user' });

// Service worker → specific tab's content script
await chrome.tabs.sendMessage(tabId, { type: 'HIGHLIGHT', selector: '.target' });

// Service worker handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // sender.tab exists if message came from a content script
  // sender.url is the page URL or extension page URL
  // sender.id is the extension ID

  if (message.type === 'GET_DATA') {
    chrome.storage.local.get(message.key).then(sendResponse);
    return true; // CRITICAL for async responses
  }
});
```

### Response rules

- **Synchronous response**: return value doesn't matter, call `sendResponse()` before listener returns
- **Async response**: MUST `return true` from the listener (literal boolean, not a Promise)
- **No response needed**: return `undefined` or `false` (channel closes immediately)
- **Multiple listeners**: only the FIRST listener to call `sendResponse` or `return true` wins.
  Other listeners are ignored.

## 2. The async handler trap and fix

This is the #1 messaging bug in Chrome extension development.

### The problem

`async` functions always return a Promise. Chrome checks for literal `true`, not `Promise<true>`.

```typescript
// ❌ BROKEN: async returns Promise, Chrome closes channel immediately
chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
  const data = await fetch('https://api.example.com/data');
  const json = await data.json();
  sendResponse(json);     // NEVER REACHES the sender
  return true;            // Wrapped in Promise<true>, Chrome doesn't see it
});
```

### The fix: non-async wrapper

```typescript
// ✅ CORRECT: synchronous wrapper returns literal true
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'FETCH_DATA') {
    fetchData(msg.url)
      .then(data => sendResponse({ ok: true, data }))
      .catch(err => sendResponse({ ok: false, error: err.message }));
    return true; // literal boolean true
  }
});
```

### Reusable async handler utility

```typescript
type AsyncMessageHandler = (
  message: any,
  sender: chrome.runtime.MessageSender
) => Promise<any>;

function asyncHandler(fn: AsyncMessageHandler) {
  return (
    message: any,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response: any) => void
  ): true => {
    fn(message, sender)
      .then(result => sendResponse({ __ok: true, result }))
      .catch(err => sendResponse({ __ok: false, error: err.message, stack: err.stack }));
    return true;
  };
}

// Usage
chrome.runtime.onMessage.addListener(asyncHandler(async (msg, sender) => {
  if (msg.type === 'FETCH') {
    const res = await fetch(msg.url);
    return await res.json();
  }
  if (msg.type === 'STORAGE_GET') {
    return await chrome.storage.local.get(msg.keys);
  }
}));
```

### Client-side unwrapper

```typescript
async function sendMessage<T>(message: any): Promise<T> {
  const response = await chrome.runtime.sendMessage(message);
  if (response?.__ok === false) throw new Error(response.error);
  return response?.__ok ? response.result : response;
}
```

## 3. Port-based long-lived connections

For ongoing bidirectional communication: streaming data, real-time updates, progress
reporting. Ports keep the service worker alive as long as messages are being sent.

```typescript
// === Content script: open connection ===
const port = chrome.runtime.connect({ name: 'data-stream' });

port.postMessage({ action: 'subscribe', topics: ['prices', 'news'] });

port.onMessage.addListener((msg) => {
  if (msg.type === 'update') updateUI(msg.data);
  if (msg.type === 'error') showError(msg.error);
});

port.onDisconnect.addListener(() => {
  if (chrome.runtime.lastError) {
    console.error('Port error:', chrome.runtime.lastError.message);
  }
  // Auto-reconnect with backoff
  setTimeout(() => reconnect(), 1000);
});

// === Service worker: handle connections ===
const activePorts = new Map<number, chrome.runtime.Port>();

chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== 'data-stream') return;

  const tabId = port.sender?.tab?.id;
  if (tabId) activePorts.set(tabId, port);

  port.onMessage.addListener((msg) => {
    if (msg.action === 'subscribe') {
      startStreaming(port, msg.topics);
    }
  });

  port.onDisconnect.addListener(() => {
    if (tabId) activePorts.delete(tabId);
    cleanupSubscriptions(port);
  });
});

// Broadcast to all connected tabs
function broadcast(message: any) {
  for (const [tabId, port] of activePorts) {
    try { port.postMessage(message); }
    catch { activePorts.delete(tabId); }
  }
}
```

### Port vs sendMessage: when to use which

| Use case | sendMessage | Port |
|----------|-------------|------|
| Single request/response | ✅ | Overkill |
| Multiple messages over time | Inefficient | ✅ |
| Progress reporting | Awkward | ✅ |
| Streaming data | Impossible | ✅ |
| Simple one-off query | ✅ | Overkill |
| Need to detect disconnect | Manual | ✅ Built-in |

## 4. Service worker → content script

The service worker initiates communication using `chrome.tabs.sendMessage`:

```typescript
// Send to a specific tab
async function sendToTab(tabId: number, message: any) {
  try {
    return await chrome.tabs.sendMessage(tabId, message);
  } catch (err) {
    // Common: tab doesn't have content script, or script is orphaned
    console.warn(`Tab ${tabId} unreachable:`, err);
    return null;
  }
}

// Send to the active tab
async function sendToActiveTab(message: any) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return null;
  return sendToTab(tab.id, message);
}

// Send to all tabs matching a URL pattern
async function sendToMatchingTabs(urlPattern: string, message: any) {
  const tabs = await chrome.tabs.query({ url: urlPattern });
  return Promise.allSettled(
    tabs.filter(t => t.id).map(t => sendToTab(t.id!, message))
  );
}
```

Content script must have a listener:

```typescript
// content-script.ts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'HIGHLIGHT') {
    const el = document.querySelector(message.selector);
    if (el) el.style.outline = '3px solid red';
    sendResponse({ found: !!el });
  }
  return true;
});
```

## 5. Full three-layer bridge: page ↔ content script ↔ service worker

This pattern enables web page JavaScript (with no chrome.* API access) to communicate
with the extension's service worker through the content script as a relay.

```
┌─────────────────┐  window.postMessage  ┌──────────────────┐  chrome.runtime  ┌─────────────────┐
│ Page (main world)│ ◄──────────────────► │ Content Script    │ ◄──────────────► │ Service Worker   │
│ No chrome.* API  │                      │ (isolated world)  │                  │ Full chrome.* API│
│ Full page access │                      │ Bridge/relay      │                  │ No DOM           │
└─────────────────┘                      └──────────────────┘                  └─────────────────┘
```

### Page-side client (injected as main world script)

```typescript
// page-client.ts (world: "MAIN" or injected via web_accessible_resources)
const EXTENSION_CHANNEL = 'MY_EXT_BRIDGE';
const pendingRequests = new Map<string, { resolve: Function; reject: Function }>();

// Send request to extension, get response back
function requestFromExtension(type: string, payload?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    pendingRequests.set(requestId, { resolve, reject });

    // Timeout after 30s
    setTimeout(() => {
      if (pendingRequests.has(requestId)) {
        pendingRequests.delete(requestId);
        reject(new Error('Extension request timeout'));
      }
    }, 30000);

    window.postMessage({
      channel: EXTENSION_CHANNEL,
      direction: 'TO_EXTENSION',
      requestId,
      type,
      payload,
    }, window.location.origin); // NEVER use '*'
  });
}

// Listen for responses from extension
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (event.data?.channel !== EXTENSION_CHANNEL) return;
  if (event.data?.direction !== 'FROM_EXTENSION') return;

  const { requestId, response, error } = event.data;
  const pending = pendingRequests.get(requestId);
  if (!pending) return;

  pendingRequests.delete(requestId);
  if (error) pending.reject(new Error(error));
  else pending.resolve(response);
});

// Usage from page JS:
// const user = await requestFromExtension('GET_USER', { id: '123' });
```

### Content script bridge

```typescript
// bridge.ts (content script, isolated world)
const EXTENSION_CHANNEL = 'MY_EXT_BRIDGE';

// Page → Extension
window.addEventListener('message', async (event) => {
  if (event.source !== window) return;
  if (event.data?.channel !== EXTENSION_CHANNEL) return;
  if (event.data?.direction !== 'TO_EXTENSION') return;

  const { requestId, type, payload } = event.data;

  try {
    const response = await chrome.runtime.sendMessage({ type, payload });
    window.postMessage({
      channel: EXTENSION_CHANNEL,
      direction: 'FROM_EXTENSION',
      requestId,
      response,
    }, window.location.origin);
  } catch (err: any) {
    window.postMessage({
      channel: EXTENSION_CHANNEL,
      direction: 'FROM_EXTENSION',
      requestId,
      error: err.message,
    }, window.location.origin);
  }
});

// Extension → Page (forward service worker events to page)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.direction === 'TO_PAGE') {
    window.postMessage({
      channel: EXTENSION_CHANNEL,
      direction: 'FROM_EXTENSION_PUSH',
      type: message.type,
      payload: message.payload,
    }, window.location.origin);
    sendResponse({ received: true });
  }
  return true;
});
```

## 6. Typed message protocol with discriminated unions

Type-safe messaging eliminates string matching bugs:

```typescript
// === messages.ts (shared types) ===

// Define all messages as a discriminated union
type ContentToBackground =
  | { type: 'FETCH_API'; url: string; method?: string; body?: string }
  | { type: 'GET_SETTINGS' }
  | { type: 'SET_SETTINGS'; settings: Partial<Settings> }
  | { type: 'LOG_EVENT'; event: string; data?: Record<string, unknown> };

type BackgroundToContent =
  | { type: 'SETTINGS_CHANGED'; settings: Settings }
  | { type: 'TOGGLE_UI'; visible: boolean }
  | { type: 'NOTIFICATION'; title: string; body: string };

// Response types mapped to request types
interface ResponseMap {
  FETCH_API: { ok: boolean; status: number; data: string };
  GET_SETTINGS: Settings;
  SET_SETTINGS: { success: boolean };
  LOG_EVENT: void;
  SETTINGS_CHANGED: void;
  TOGGLE_UI: { wasVisible: boolean };
  NOTIFICATION: void;
}

interface Settings {
  theme: 'light' | 'dark';
  enabled: boolean;
  apiKey: string;
}

// === Type-safe sender ===
async function sendTyped<T extends ContentToBackground>(
  message: T
): Promise<ResponseMap[T['type']]> {
  return chrome.runtime.sendMessage(message);
}

// Usage (fully typed):
const settings = await sendTyped({ type: 'GET_SETTINGS' });
//    ^ Settings
const result = await sendTyped({ type: 'FETCH_API', url: 'https://api.com/data' });
//    ^ { ok: boolean; status: number; data: string }
```

## 7. Full RPC layer (simulate HTTP through messaging)

For extensions that need HTTP-like semantics (methods, status codes, errors) over
chrome.runtime messaging:

```typescript
// === rpc-types.ts ===
interface RPCMethods {
  'user.get':      { params: { id: string };              result: User };
  'user.update':   { params: { id: string; data: Partial<User> }; result: User };
  'user.delete':   { params: { id: string };              result: void };
  'tabs.list':     { params: void;                        result: TabInfo[] };
  'settings.get':  { params: { key: string };             result: unknown };
  'settings.set':  { params: { key: string; value: unknown }; result: void };
  'fetch.relay':   { params: FetchParams;                 result: FetchResult };
}

interface FetchParams {
  url: string;
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

interface FetchResult {
  ok: boolean;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  body: string;
}

interface RPCRequest<M extends keyof RPCMethods = keyof RPCMethods> {
  __rpc: true;
  id: string;
  method: M;
  params: RPCMethods[M]['params'];
}

interface RPCResponseOk<M extends keyof RPCMethods = keyof RPCMethods> {
  __rpc: true;
  id: string;
  result: RPCMethods[M]['result'];
  error?: never;
}

interface RPCResponseError {
  __rpc: true;
  id: string;
  result?: never;
  error: { code: number; message: string; data?: unknown };
}

type RPCResponse<M extends keyof RPCMethods = keyof RPCMethods> =
  RPCResponseOk<M> | RPCResponseError;

// === rpc-client.ts (content script or popup) ===
let rpcCounter = 0;

function createRPC() {
  return new Proxy({} as {
    [M in keyof RPCMethods]: RPCMethods[M]['params'] extends void
      ? () => Promise<RPCMethods[M]['result']>
      : (params: RPCMethods[M]['params']) => Promise<RPCMethods[M]['result']>
  }, {
    get(_, method: string) {
      return async (params?: unknown) => {
        const id = `rpc_${++rpcCounter}_${Date.now()}`;
        const response: RPCResponse = await chrome.runtime.sendMessage({
          __rpc: true, id, method, params: params ?? null,
        });
        if (!response?.__rpc) throw new Error('Invalid RPC response');
        if (response.error) {
          const err = new Error(response.error.message);
          (err as any).code = response.error.code;
          (err as any).data = response.error.data;
          throw err;
        }
        return response.result;
      };
    },
  });
}

const rpc = createRPC();

// Usage: fully typed, looks like function calls
const user = await rpc['user.get']({ id: '123' });
const tabs = await rpc['tabs.list']();
await rpc['settings.set']({ key: 'theme', value: 'dark' });

// CSP bypass: relay fetch through service worker
const apiResponse = await rpc['fetch.relay']({
  url: 'https://api.example.com/data',
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'test' }),
});

// === rpc-server.ts (service worker) ===
type Handler<M extends keyof RPCMethods> = (
  params: RPCMethods[M]['params'],
  sender: chrome.runtime.MessageSender
) => Promise<RPCMethods[M]['result']>;

const handlers = new Map<string, Handler<any>>();

function registerHandler<M extends keyof RPCMethods>(method: M, handler: Handler<M>) {
  handlers.set(method, handler);
}

// Register handlers
registerHandler('user.get', async (params) => {
  const res = await fetch(`https://api.example.com/users/${params.id}`);
  if (!res.ok) throw { code: res.status, message: res.statusText };
  return res.json();
});

registerHandler('tabs.list', async () => {
  const tabs = await chrome.tabs.query({});
  return tabs.map(t => ({ id: t.id, title: t.title, url: t.url }));
});

registerHandler('settings.get', async (params) => {
  const result = await chrome.storage.sync.get(params.key);
  return result[params.key];
});

registerHandler('settings.set', async (params) => {
  await chrome.storage.sync.set({ [params.key]: params.value });
});

registerHandler('fetch.relay', async (params, sender) => {
  // Security: validate URL against allowlist
  const allowed = ['https://api.example.com', 'https://cdn.example.com'];
  if (!allowed.some(base => params.url.startsWith(base))) {
    throw { code: 403, message: 'URL not in allowlist' };
  }

  const res = await fetch(params.url, {
    method: params.method ?? 'GET',
    headers: params.headers,
    body: params.body,
  });

  const headers: Record<string, string> = {};
  res.headers.forEach((v, k) => { headers[k] = v; });

  return {
    ok: res.ok,
    status: res.status,
    statusText: res.statusText,
    headers,
    body: await res.text(),
  };
});

// Main listener (top level, synchronous registration)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message?.__rpc) return false; // not an RPC message, let other listeners handle

  const handler = handlers.get(message.method);
  if (!handler) {
    sendResponse({
      __rpc: true, id: message.id,
      error: { code: -32601, message: `Method not found: ${message.method}` },
    });
    return true;
  }

  handler(message.params, sender)
    .then(result => sendResponse({ __rpc: true, id: message.id, result }))
    .catch(err => {
      const error = typeof err === 'object' && err.code
        ? err
        : { code: -32000, message: err?.message ?? String(err) };
      sendResponse({ __rpc: true, id: message.id, error });
    });

  return true; // async
});
```

## 8. Cross-extension messaging

Extensions can communicate with each other via `externally_connectable`:

```json
// manifest.json of receiving extension
{
  "externally_connectable": {
    "ids": ["sender_extension_id_here"],
    "matches": ["https://your-website.com/*"]
  }
}
```

```typescript
// Sending extension
chrome.runtime.sendMessage('target_extension_id', { type: 'HELLO' }, (response) => {
  console.log('Response from other extension:', response);
});

// Receiving extension
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  console.log('From extension:', sender.id);
  sendResponse({ ok: true });
});
```

## 9. Common messaging bugs

### Bug: "Could not establish connection. Receiving end does not exist."

Causes:
1. No content script injected in the target tab
2. Content script orphaned after extension update
3. Sending to a chrome://, edge://, or other restricted page
4. Service worker terminated and listener not registered synchronously

Fix: always wrap `sendMessage`/`tabs.sendMessage` in try/catch.

### Bug: sendResponse called but sender never receives

Cause: `return true` missing or wrapped in a Promise (async function).
Fix: use the `asyncHandler` wrapper from section 2.

### Bug: message received by wrong listener

Cause: multiple listeners registered, first one to `return true` wins.
Fix: use message type discrimination. Return `false` or `undefined` from
listeners that don't handle the message type.

### Bug: Port disconnected unexpectedly

Causes:
1. Service worker terminated (no messages sent within 30s)
2. Tab closed or navigated away
3. Extension updated/reloaded

Fix: always handle `port.onDisconnect`, implement reconnection logic.

### Bug: message payload too large

Chrome has an undocumented limit of ~64MB per message. For large data,
consider using `chrome.storage` as a shared buffer or chunking.
