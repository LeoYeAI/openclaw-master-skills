# Content Scripts Reference

## Table of contents
1. Isolated world vs main world
2. Static declaration (manifest)
3. Dynamic/programmatic injection
4. Injection timing (run_at)
5. SPA navigation handling
6. Content script orphaning on extension update
7. CSS injection
8. Communication between worlds

## 1. Isolated world vs main world

Content scripts default to the **isolated world**: a separate JavaScript execution
environment that shares the page's DOM but not its JavaScript objects.

| Capability | Isolated world | Main world |
|-----------|---------------|------------|
| Read/modify DOM | Yes | Yes |
| Access page JS variables (`window.myApp`) | No | Yes |
| Intercept page `fetch`/`XMLHttpRequest` | No | Yes |
| Access `chrome.runtime` | Yes | No |
| Access `chrome.storage` | Yes | No |
| Access `chrome.i18n` | Yes | No |
| Subject to page CSP (scripts) | No | Yes |
| Subject to page CSP (network) | Yes | Yes |
| Page can see script variables | No | Yes |
| Can modify `window` prototypes | No | Yes |

### When to use main world

- Intercepting/monkey-patching page functions (`fetch`, `XMLHttpRequest`, custom APIs)
- Reading page JavaScript state (SPA router state, React fiber tree)
- Setting `window` globals for page scripts to consume
- Overriding built-in APIs for instrumentation

### When to use isolated world (default)

- Everything else. It's safer: the page can't tamper with your code, and you retain
  chrome.* API access.

## 2. Static declaration (manifest)

```json
{
  "content_scripts": [
    {
      "matches": ["https://*.example.com/*"],
      "exclude_matches": ["https://example.com/admin/*"],
      "js": ["content/main.js", "content/utils.js"],
      "css": ["content/styles.css"],
      "run_at": "document_idle",
      "all_frames": false,
      "match_about_blank": false,
      "world": "ISOLATED"
    }
  ]
}
```

Scripts in `js` array execute in order. CSS in `css` array is injected before any DOM.

## 3. Dynamic/programmatic injection

Use `chrome.scripting` (requires `"scripting"` permission) for on-demand injection.
This is preferred over static when injection depends on user action or runtime conditions.

### Execute a function

```typescript
// Inject a function directly (serialized, no closure access)
chrome.scripting.executeScript({
  target: { tabId, allFrames: false },
  func: (color: string) => {
    document.body.style.backgroundColor = color;
  },
  args: ['yellow'],
  world: 'ISOLATED',       // or 'MAIN'
});
```

### Execute a file

```typescript
chrome.scripting.executeScript({
  target: { tabId },
  files: ['content/injected.js'],
});
```

### Register persistent dynamic content scripts

Dynamic content scripts persist across browser restarts (unlike executeScript):

```typescript
// Register (persists until explicitly removed)
await chrome.scripting.registerContentScripts([{
  id: 'my-dynamic-script',
  matches: ['https://example.com/*'],
  js: ['content/dynamic.js'],
  runAt: 'document_idle',
  persistAcrossSessions: true,    // default true
}]);

// Update
await chrome.scripting.updateContentScripts([{
  id: 'my-dynamic-script',
  excludeMatches: ['https://example.com/admin/*'],
}]);

// List registered
const scripts = await chrome.scripting.getRegisteredContentScripts();

// Remove
await chrome.scripting.unregisterContentScripts({ ids: ['my-dynamic-script'] });
```

### CSS injection

```typescript
// Insert CSS
await chrome.scripting.insertCSS({
  target: { tabId },
  css: 'body { border: 2px solid red !important; }',
});

// Or from file
await chrome.scripting.insertCSS({
  target: { tabId },
  files: ['styles/highlight.css'],
});

// Remove CSS (same parameters as insert)
await chrome.scripting.removeCSS({
  target: { tabId },
  css: 'body { border: 2px solid red !important; }',
});
```

## 4. Injection timing (run_at)

| Value | When | DOM state | Use case |
|-------|------|-----------|----------|
| `document_start` | Before any page scripts or DOM | Only `<html>` exists, no `<body>` | Monkey-patching APIs before page runs, blocking early scripts |
| `document_end` | After DOM parsed, before subresources | Full DOM, images/iframes may still load | Most content modifications |
| `document_idle` | After load event or small idle period | Everything loaded | Default. Safest. Use unless you need earlier access |

### document_start gotchas

- `document.body` does not exist yet. Use `document.documentElement` or wait:
  ```javascript
  // At document_start, wait for body
  const observer = new MutationObserver(() => {
    if (document.body) {
      observer.disconnect();
      injectUI();
    }
  });
  observer.observe(document.documentElement, { childList: true });
  ```

- Script injection at document_start with `world: "MAIN"` runs before ANY page scripts,
  making it ideal for API interception:
  ```javascript
  // main-world-early.js (run_at: document_start, world: MAIN)
  const originalFetch = window.fetch;
  window.fetch = async function(...args) {
    console.log('Intercepted fetch:', args[0]);
    return originalFetch.apply(this, args);
  };
  ```

## 5. SPA navigation handling

Single-page applications (YouTube, Gmail, Twitter) use History API for navigation.
Content scripts only inject on **full page loads**, not SPA navigations.

### Detection from service worker

```typescript
// Detect SPA navigations
chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
  if (details.frameId !== 0) return; // main frame only
  chrome.tabs.sendMessage(details.tabId, {
    type: 'SPA_NAVIGATION',
    url: details.url,
  }).catch(() => {}); // Content script may not be ready
});

// Also handle hash changes
chrome.webNavigation.onReferenceFragmentUpdated.addListener((details) => {
  if (details.frameId !== 0) return;
  chrome.tabs.sendMessage(details.tabId, {
    type: 'SPA_NAVIGATION',
    url: details.url,
  }).catch(() => {});
});
```

### Detection from content script

```typescript
// MutationObserver for DOM changes (SPA route transitions)
const observer = new MutationObserver((mutations) => {
  // Check if significant content changed
  for (const mutation of mutations) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      onContentChanged();
      break;
    }
  }
});
observer.observe(document.body, { childList: true, subtree: true });

// URL change detection
let lastUrl = location.href;
new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    onUrlChanged(lastUrl);
  }
}).observe(document.body, { childList: true, subtree: true });

// Navigation API (Chrome 102+, more reliable)
if ('navigation' in window) {
  navigation.addEventListener('navigatesuccess', () => {
    onUrlChanged(location.href);
  });
}
```

## 6. Content script orphaning on extension update

When an extension updates, existing content scripts become **orphaned**: they continue
running but lose access to `chrome.runtime`. All messaging throws errors.

### Detection

```typescript
function isExtensionAlive(): boolean {
  try {
    return !!chrome.runtime?.id;
  } catch {
    return false;
  }
}

// Wrap every chrome.runtime call
function safeSendMessage(message: any): Promise<any> {
  return new Promise((resolve, reject) => {
    if (!isExtensionAlive()) {
      reject(new Error('Extension context invalidated'));
      showRefreshBanner();
      return;
    }
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
      } else {
        resolve(response);
      }
    });
  });
}
```

### Show refresh banner

```typescript
function showRefreshBanner() {
  if (document.getElementById('ext-refresh-banner')) return;
  const banner = document.createElement('div');
  banner.id = 'ext-refresh-banner';
  banner.innerHTML = `
    <div style="position:fixed;top:0;left:0;right:0;z-index:999999;
                background:#f59e0b;color:#000;padding:8px 16px;text-align:center;
                font-family:system-ui;font-size:14px;">
      Extension updated. Please <a href="#" style="color:#000;font-weight:bold;
      text-decoration:underline;">refresh this page</a> to continue using it.
    </div>
  `;
  banner.querySelector('a')!.addEventListener('click', (e) => {
    e.preventDefault();
    location.reload();
  });
  document.body.appendChild(banner);
}
```

### Re-inject on update (from service worker)

```typescript
chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason !== 'update') return;
  const manifest = chrome.runtime.getManifest();
  const tabs = await chrome.tabs.query({});
  for (const cs of manifest.content_scripts ?? []) {
    for (const tab of tabs) {
      if (!tab.id || !tab.url) continue;
      const matches = cs.matches?.some(pattern => matchesPattern(tab.url!, pattern));
      if (!matches) continue;
      try {
        if (cs.js) {
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: cs.js,
          });
        }
        if (cs.css) {
          await chrome.scripting.insertCSS({
            target: { tabId: tab.id },
            files: cs.css,
          });
        }
      } catch { /* chrome:// pages, permission denied, etc. */ }
    }
  }
});
```

### Prevent double-injection

```typescript
// content-script.ts (idempotent entry point)
(() => {
  const MARKER = '__myext_v2_injected';
  if ((window as any)[MARKER]) {
    // Old instance exists; clean it up
    (window as any).__myext_cleanup?.();
  }
  (window as any)[MARKER] = true;

  const observer = new MutationObserver(/* ... */);
  const ui = createUI();

  (window as any).__myext_cleanup = () => {
    observer.disconnect();
    ui.remove();
    delete (window as any)[MARKER];
  };
})();
```

## 7. CSS injection patterns

### Shadow DOM for isolated UI

Inject UI that won't be affected by the page's CSS and vice versa:

```typescript
function createIsolatedUI() {
  const host = document.createElement('div');
  host.id = 'myext-root';
  const shadow = host.attachShadow({ mode: 'closed' });

  shadow.innerHTML = `
    <style>
      :host { all: initial; }
      .panel { position: fixed; bottom: 20px; right: 20px; z-index: 2147483647;
               background: white; border-radius: 8px; padding: 16px;
               box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-family: system-ui; }
      button { padding: 8px 16px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; }
    </style>
    <div class="panel">
      <p>My Extension</p>
      <button id="action-btn">Do thing</button>
    </div>
  `;

  shadow.getElementById('action-btn')!.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'ACTION' });
  });

  document.body.appendChild(host);
  return { host, shadow };
}
```

### Using extension CSS files

```typescript
// Load CSS from extension bundle
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = chrome.runtime.getURL('styles/content.css');
document.head.appendChild(link);
```

Requires the CSS file to be listed in `web_accessible_resources`.

## 8. Communication between worlds

Content scripts in isolated world and main world scripts on the same page communicate
through the shared DOM via `window.postMessage` or custom DOM events.

### window.postMessage (bidirectional)

```typescript
// Main world script
window.postMessage({ source: 'MY_EXT_PAGE', type: 'DATA', payload: window.appState }, '*');

// Content script (isolated world)
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (event.data?.source !== 'MY_EXT_PAGE') return;
  chrome.runtime.sendMessage(event.data);
});
```

### Custom DOM events (more targeted)

```typescript
// Main world: dispatch custom event
document.dispatchEvent(new CustomEvent('myext-data', {
  detail: JSON.parse(JSON.stringify(window.appState)) // must be cloneable
}));

// Content script: listen
document.addEventListener('myext-data', (event: CustomEvent) => {
  chrome.runtime.sendMessage({ type: 'PAGE_DATA', data: event.detail });
});
```

Custom events are slightly more targeted than postMessage (no cross-origin concerns)
but require serializable data via `JSON.parse(JSON.stringify(...))`.
