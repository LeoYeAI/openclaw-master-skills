# Service Worker Reference

## Table of contents
1. Lifecycle and termination rules
2. Event listener registration rules
3. State management patterns
4. Alarms (replacing setTimeout/setInterval)
5. Startup and install events
6. Keep-alive patterns (when absolutely needed)
7. Identity and OAuth
8. Offscreen documents

## 1. Lifecycle and termination rules

The service worker is Chrome's replacement for MV2's persistent background page. It is
**event-driven and ephemeral**.

### Termination timeline

| Condition | Timeout |
|-----------|---------|
| No pending events or API calls | **30 seconds** |
| Single long-running task | **5 minutes** hard cap |
| Active fetch() request | **30 seconds** from last network activity |
| Active chrome.* API call | Resets the 30s idle timer |
| DevTools open on SW | **Never terminates** (masks bugs!) |

### What resets the 30s idle timer (Chrome 110+)

Any chrome.* API call or event: `onMessage`, `onAlarm`, `onClicked`, `tabs.onUpdated`,
`webNavigation.*`, etc. Also: active `fetch()`, WebSocket messages (Chrome 116+),
native messaging host communication (Chrome 105+).

### What does NOT keep it alive

- `setTimeout`/`setInterval` - these are **cancelled** on termination
- Global variables - reset to `undefined` on restart
- Promises that haven't resolved - **lost**
- `localStorage`/`sessionStorage` - **do not exist** in service workers

### What's lost on termination

```javascript
// ALL of these vanish:
let cache = {};           // gone
let counter = 0;          // gone
const ws = new WebSocket(url);  // disconnected
setTimeout(fn, 60000);    // cancelled
const pending = fetch(url); // if SW terminates before response, lost
```

## 2. Event listener registration rules

**CRITICAL**: All event listeners MUST be registered synchronously at the top level of the
service worker file. Chrome records which events a SW listens to. If a listener isn't
registered synchronously on startup, Chrome won't wake the SW for that event.

```javascript
// ✅ CORRECT: top-level, synchronous
chrome.runtime.onMessage.addListener(handleMessage);
chrome.tabs.onUpdated.addListener(handleTabUpdate);
chrome.alarms.onAlarm.addListener(handleAlarm);
chrome.runtime.onInstalled.addListener(handleInstall);
chrome.action.onClicked.addListener(handleClick);

// ✅ CORRECT: conditional logic inside the handler is fine
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'A') handleA(msg, sendResponse);
  if (msg.type === 'B') handleB(msg, sendResponse);
  return true;
});

// ❌ BROKEN: listener inside async/callback
chrome.storage.local.get('config', (config) => {
  if (config.enableFeature) {
    chrome.tabs.onUpdated.addListener(handleTabUpdate); // LOST after restart
  }
});

// ❌ BROKEN: listener inside import().then()
import('./handlers.js').then(module => {
  chrome.runtime.onMessage.addListener(module.handler); // LOST after restart
});

// ✅ WORKAROUND for dynamic imports: register first, delegate later
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  import('./handlers.js').then(m => m.handler(msg, sender, sendResponse));
  return true;
});
```

With `"type": "module"` in manifest, **static** `import` statements are fine:

```javascript
// background.js with "type": "module"
import { handleMessage } from './handlers.js';  // ✅ static import is OK
chrome.runtime.onMessage.addListener(handleMessage);
```

## 3. State management patterns

### Use chrome.storage.session for ephemeral state

`chrome.storage.session` persists across SW restarts but clears on browser close.
Perfect for auth tokens, computed caches, in-progress operations.

```typescript
// Initialize access for content scripts (call once at top level)
chrome.storage.session.setAccessLevel({
  accessLevel: 'TRUSTED_AND_UNTRUSTED_CONTEXTS'
});

// State helpers
async function getState<T>(key: string, fallback: T): Promise<T> {
  const result = await chrome.storage.session.get(key);
  return (result[key] as T) ?? fallback;
}

async function setState(key: string, value: unknown): Promise<void> {
  await chrome.storage.session.set({ [key]: value });
}

async function updateState<T>(key: string, fallback: T, updater: (prev: T) => T): Promise<T> {
  const current = await getState(key, fallback);
  const next = updater(current);
  await setState(key, next);
  return next;
}

// Usage
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'INCREMENT') {
    updateState('counter', 0, n => n + 1).then(sendResponse);
    return true;
  }
});
```

### Use chrome.storage.local for persistent state

```typescript
// Batch reads for performance
const { token, settings, cache } = await chrome.storage.local.get([
  'token', 'settings', 'cache'
]);

// Atomic batch writes
await chrome.storage.local.set({
  token: newToken,
  settings: { ...settings, theme: 'dark' },
  lastUpdated: Date.now(),
});
```

## 4. Alarms: replacing setTimeout/setInterval

`chrome.alarms` survives SW termination. Requires `"alarms"` permission.
Minimum interval: **30 seconds** (Chrome 120+, was 1 minute before).

```typescript
// Create alarms
chrome.alarms.create('periodic-sync', { periodInMinutes: 1 });           // recurring
chrome.alarms.create('delayed-task', { delayInMinutes: 0.5 });           // one-shot (30s)
chrome.alarms.create('daily-check', { periodInMinutes: 1440 });          // daily
chrome.alarms.create('specific-time', { when: Date.now() + 60000 });     // absolute time

// Handle alarms (TOP LEVEL)
chrome.runtime.onMessage.addListener(handleMessage); // other listeners...

chrome.alarms.onAlarm.addListener(async (alarm) => {
  switch (alarm.name) {
    case 'periodic-sync':
      await syncData();
      break;
    case 'delayed-task':
      await processQueue();
      break;
  }
});

// Idempotent alarm creation (don't duplicate on every SW wake)
async function ensureAlarms() {
  const existing = await chrome.alarms.getAll();
  const names = existing.map(a => a.name);
  if (!names.includes('periodic-sync')) {
    chrome.alarms.create('periodic-sync', { periodInMinutes: 1 });
  }
}
ensureAlarms();
```

## 5. Startup and install events

```typescript
// Runs on install, update, and Chrome update
chrome.runtime.onInstalled.addListener((details) => {
  switch (details.reason) {
    case 'install':
      // First install: set defaults, open onboarding tab
      chrome.storage.sync.set({ theme: 'light', enabled: true });
      chrome.tabs.create({ url: 'onboarding.html' });
      break;
    case 'update':
      // Extension updated: migrate data, re-inject content scripts
      const prev = details.previousVersion;
      console.log(`Updated from ${prev} to ${chrome.runtime.getManifest().version}`);
      reInjectContentScripts();
      break;
    case 'chrome_update':
      // Chrome browser itself updated
      break;
  }
});

// Runs every time the SW starts (install, update, wake from idle, browser start)
chrome.runtime.onStartup.addListener(() => {
  // Good place to ensure alarms exist, warm caches, etc.
  ensureAlarms();
});
```

## 6. Keep-alive patterns (use sparingly)

Sometimes you need the SW alive for longer operations (e.g., streaming responses).
These patterns extend lifetime but should be last resorts.

### Periodic chrome.* API call

```typescript
// Keep alive for up to 5 minutes during a long operation
let keepAliveInterval: ReturnType<typeof setInterval> | null = null;

function startKeepAlive() {
  keepAliveInterval = setInterval(() => {
    chrome.runtime.getPlatformInfo(() => {}); // resets 30s timer
  }, 25000);
}

function stopKeepAlive() {
  if (keepAliveInterval) {
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

// Usage during long operation
async function longRunningTask() {
  startKeepAlive();
  try {
    // ... work that takes > 30s ...
  } finally {
    stopKeepAlive();
  }
}
```

### Port-based keep-alive (offscreen document keeps SW alive)

An open port from an offscreen document keeps the SW alive indefinitely. This is the
nuclear option and should only be used for genuinely persistent requirements (e.g.,
real-time WebSocket proxy). Even then, implement cleanup.

## 7. Identity and OAuth

### Google account (simplest)

```typescript
// manifest.json: "permissions": ["identity"]
// Also needs "oauth2": { "client_id": "...", "scopes": ["..."] }

const token = await chrome.identity.getAuthToken({ interactive: true });
const response = await fetch('https://www.googleapis.com/userinfo/v2/me', {
  headers: { Authorization: `Bearer ${token.token}` }
});
```

### Generic OAuth (non-Google)

```typescript
const redirectUrl = chrome.identity.getRedirectURL(); // https://<ext-id>.chromiumapp.org/
const authUrl = new URL('https://provider.com/oauth/authorize');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', redirectUrl);
authUrl.searchParams.set('response_type', 'token');
authUrl.searchParams.set('scope', 'read write');

const responseUrl = await chrome.identity.launchWebAuthFlow({
  url: authUrl.toString(),
  interactive: true,
});

const url = new URL(responseUrl);
const token = url.hash.split('&').find(p => p.startsWith('access_token='))?.split('=')[1];
await chrome.storage.session.set({ accessToken: token });
```

## 8. Offscreen documents

When you need DOM APIs unavailable in service workers (DOMParser, Canvas, Audio, Clipboard):

```typescript
// background.ts
async function ensureOffscreen() {
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT'],
    documentUrls: [chrome.runtime.getURL('offscreen.html')],
  });
  if (contexts.length > 0) return;
  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: [chrome.offscreen.Reason.DOM_PARSER],
    justification: 'Parse HTML responses',
  });
}

// Delegate work to offscreen doc
async function parseHTML(html: string) {
  await ensureOffscreen();
  return chrome.runtime.sendMessage({ target: 'offscreen', type: 'PARSE', html });
}
```

```html
<!-- offscreen.html -->
<script src="offscreen.js"></script>
```

```javascript
// offscreen.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.target !== 'offscreen') return;
  if (msg.type === 'PARSE') {
    const doc = new DOMParser().parseFromString(msg.html, 'text/html');
    const title = doc.querySelector('title')?.textContent;
    const links = [...doc.querySelectorAll('a')].map(a => a.href);
    sendResponse({ title, links });
    return true;
  }
});
```

**Limitations**: only one offscreen document per extension, only `chrome.runtime` API
available, must specify a `Reason` enum value. Available reasons: `TESTING`, `AUDIO_PLAYBACK`,
`IFRAME_SCRIPTING`, `DOM_SCRAPING`, `DOM_PARSER`, `BLOBS`, `CLIPBOARD`, `LOCAL_STORAGE`,
`WORKERS`, `BATTERY_STATUS`, `MATCH_MEDIA`, `GEOLOCATION`, `USER_MEDIA`, `DISPLAY_MEDIA`.
