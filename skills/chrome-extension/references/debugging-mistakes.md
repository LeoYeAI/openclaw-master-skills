# Debugging and Common Mistakes Reference

## Table of contents
1. DevTools for each extension context
2. Testing service worker termination
3. Common error messages and fixes
4. The top 10 MV3 mistakes
5. Performance pitfalls
6. Testing strategies

## 1. DevTools for each extension context

Each extension context has its own DevTools instance:

| Context | How to open DevTools |
|---------|---------------------|
| Service worker | chrome://extensions → click "Inspect views: service worker" |
| Popup | Right-click extension icon → "Inspect popup" |
| Options page | Right-click in options page → "Inspect" |
| Side panel | Right-click in side panel → "Inspect" |
| Content script | Normal page DevTools (F12), check Sources → Content scripts |
| Offscreen document | chrome://extensions → "Inspect views: offscreen.html" |

### Content script debugging tips

Content script console logs appear in the PAGE's DevTools console, not the extension's.
Filter by your extension name or use `console.log('[MyExt]', ...)` prefix.

In Sources panel: look under "Content scripts" folder to set breakpoints.

### Service worker debugging

The service worker console is separate. Use `chrome://extensions` → Inspect to open it.
Warning: **keeping DevTools open on the SW prevents it from terminating**, masking
lifecycle bugs.

## 2. Testing service worker termination

### Manual termination

1. Open chrome://extensions
2. Find your extension
3. Click the "service worker" link to open DevTools (optional)
4. Click the "Stop" button next to the service worker link
5. Trigger your extension's functionality
6. Verify it works after the SW restarts

### Programmatic self-termination for testing

```typescript
// Add a test-only handler
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === '__TEST_TERMINATE_SW') {
    // Force terminate by not returning true and doing nothing
    // The SW will idle out in 30 seconds
    // OR: more aggressively, just stop doing anything
  }
});
```

### Chrome flag for testing

`chrome://flags/#enable-extension-service-worker-test-flag` (if available in your
Chrome version) can help with automated testing of SW suspension.

### Automated test pattern

```typescript
// In a test (e.g., Puppeteer/Playwright)
// 1. Load extension
// 2. Interact with it (verify functionality)
// 3. Wait 35 seconds (or stop the SW via chrome://extensions)
// 4. Interact again (verify it recovers)
// 5. Check that all state was preserved
```

## 3. Common error messages and fixes

### "Extension context invalidated"

**Cause**: Content script trying to use chrome.runtime after extension was updated/reloaded.
**Fix**: Check `chrome.runtime?.id` before any chrome.runtime call. Show refresh banner.

### "Could not establish connection. Receiving end does not exist."

**Causes**:
1. No content script in the target tab
2. Content script orphaned
3. Sending to chrome:// or other restricted page
4. Service worker terminated and listener not registered

**Fix**: Wrap in try/catch. Check tab URL before sending. Verify content script injection.

### "The message port closed before a response was received."

**Cause**: Message listener didn't call sendResponse and didn't return true.
**Fix**: return `true` from the listener if response is async.

### "Unchecked runtime.lastError: ..."

**Cause**: chrome.* API callback error not checked.
**Fix**: always check `chrome.runtime.lastError` in callbacks, or use Promise-based
APIs and catch rejections:

```typescript
// Callback style
chrome.tabs.sendMessage(tabId, msg, (response) => {
  if (chrome.runtime.lastError) {
    console.warn(chrome.runtime.lastError.message);
    return;
  }
  // use response
});

// Promise style (preferred)
try {
  const response = await chrome.tabs.sendMessage(tabId, msg);
} catch (err) {
  console.warn('Tab unreachable:', err);
}
```

### "Cannot access contents of url ... Extension manifest must request permission."

**Cause**: missing host_permissions for the target URL.
**Fix**: add the origin to `host_permissions` or `optional_host_permissions`.

### "Service worker registration failed."

**Causes**:
1. Syntax error in the service worker file
2. Import of a nonexistent module
3. Top-level await with incorrect module config
4. Missing `"type": "module"` when using `import` statements

**Fix**: check the error details in chrome://extensions. Fix syntax errors.
Ensure `"type": "module"` is set if using ES imports.

## 4. The top 10 MV3 mistakes

### 1. Storing state in global variables
Global variables reset when SW terminates. Use chrome.storage.session instead.

### 2. Using setTimeout/setInterval in the service worker
Cancelled on termination. Use chrome.alarms (30s minimum interval).

### 3. Forgetting `return true` in async message listeners
The channel closes before sendResponse fires. Use the asyncHandler wrapper.

### 4. Using `async` directly on message listeners
Async functions return Promise, not literal true. Wrap in synchronous function.

### 5. Registering listeners inside callbacks
Chrome records listener registrations at SW startup. Listeners registered inside
callbacks, promises, or dynamic imports are missed after restart.

### 6. Testing with DevTools open (hides SW termination)
DevTools keeps the SW alive indefinitely. Always test with DevTools closed.

### 7. Requesting excessive permissions
Slows CWS review, scares users. Use activeTab + optional_permissions.

### 8. Not handling content script orphaning
After extension update, old content scripts lose chrome.runtime. Always check
`chrome.runtime?.id` and show a refresh prompt.

### 9. Confusing CORS and CSP
CORS is server-side (who can read responses). CSP is page-side (what can connect).
Content scripts are subject to both. Service worker bypasses both with host_permissions.

### 10. Using eval() or loading remote code
Forbidden in MV3. All code must be bundled locally. Use chrome.scripting.executeScript
with `func` parameter instead of `code` string.

## 5. Performance pitfalls

### Memory leaks in content scripts

Content scripts persist as long as the page is open. Common leaks:

```typescript
// ❌ LEAK: never cleaned up
document.addEventListener('scroll', onScroll);
const observer = new MutationObserver(callback);
observer.observe(document.body, { childList: true, subtree: true });

// ✅ CLEAN UP
function destroy() {
  document.removeEventListener('scroll', onScroll);
  observer.disconnect();
  ui?.remove();
}

// Clean up on extension update
chrome.runtime.onConnect.addListener(() => {});
// If this throws, extension was updated
try { chrome.runtime.id; } catch { destroy(); }
```

### Storage performance

```typescript
// ❌ SLOW: many small reads
for (const key of keys) {
  const value = await chrome.storage.local.get(key);
}

// ✅ FAST: batch read
const values = await chrome.storage.local.get(keys);
```

### Service worker startup time

Keep the service worker entry point lean. Heavy initialization blocks event handling:

```typescript
// ❌ SLOW: heavy computation at startup
const bigLookupTable = computeExpensiveTable(); // blocks all events
chrome.runtime.onMessage.addListener(handleMessage);

// ✅ FAST: lazy initialization
let lookupTable: Map<string, any> | null = null;
async function getTable() {
  if (!lookupTable) {
    const cached = await chrome.storage.session.get('lookupTable');
    lookupTable = cached.lookupTable ? new Map(cached.lookupTable) : await computeTable();
  }
  return lookupTable;
}
chrome.runtime.onMessage.addListener(handleMessage);
```

## 6. Testing strategies

### Manual testing checklist

1. Load unpacked at chrome://extensions
2. Test all user flows with DevTools CLOSED
3. Stop the service worker manually, then test again
4. Update the extension (increment version, reload), verify content scripts recover
5. Test on restricted pages (chrome://, chrome-extension://, about:blank)
6. Test with permissions revoked (chrome://settings → Privacy → Site Settings)
7. Test incognito mode (if incognito: "spanning" in manifest)

### Automated testing with Puppeteer

```typescript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  headless: false,
  args: [
    `--disable-extensions-except=/path/to/extension`,
    `--load-extension=/path/to/extension`,
  ],
});

// Get extension ID
const targets = await browser.targets();
const extensionTarget = targets.find(t => t.type() === 'service_worker');
const extensionUrl = extensionTarget?.url() ?? '';
const extensionId = extensionUrl.split('/')[2];

// Test popup
const popupPage = await browser.newPage();
await popupPage.goto(`chrome-extension://${extensionId}/popup.html`);
// ... assert popup content
```

### Unit testing shared code

Shared utilities (message types, storage helpers, pure functions) can be tested with
any standard test runner (Vitest, Jest) without a browser:

```typescript
// shared/utils.test.ts
import { debounce, formatTimestamp } from './utils';
test('debounce delays execution', async () => { /* ... */ });
```

Mock chrome.* APIs for integration tests:

```typescript
// test/mocks/chrome.ts
globalThis.chrome = {
  storage: {
    local: {
      get: vi.fn().mockResolvedValue({}),
      set: vi.fn().mockResolvedValue(undefined),
    },
  },
  runtime: {
    sendMessage: vi.fn(),
    onMessage: { addListener: vi.fn() },
  },
} as any;
```
