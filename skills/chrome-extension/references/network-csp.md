# Network Requests and CSP Bypass Reference

## Table of contents
1. CORS vs CSP in extensions
2. Where fetch() works freely
3. The relay pattern (CSP bypass)
4. declarativeNetRequest (header modification, blocking)
5. Offscreen documents for network + DOM
6. Host permissions and CORS
7. Fetch gotchas in service workers

## 1. CORS vs CSP in extensions

These are different mechanisms, often confused.

**CORS** (Cross-Origin Resource Sharing): server-side. Controls which origins can READ
responses. A server at api.com decides whether your extension origin can receive data.
- Content scripts follow the page's CORS rules (since Chrome 73)
- Service worker with host_permissions bypasses CORS for declared origins
- Popup/options pages (extension origin) also need host_permissions

**CSP** (Content Security Policy): page-side. Controls which resources a page can LOAD
or CONNECT to. A page with `connect-src 'self'` blocks ALL fetch() from content scripts
to external URLs, even your own API.
- Content scripts are bound by the page's `connect-src` directive
- Service worker is NOT subject to any page's CSP
- Extension pages have their own CSP (configured in manifest)

**The practical consequence**: a content script on a page with strict CSP cannot fetch
your API directly. You MUST relay through the service worker.

## 2. Where fetch() works freely

| Context | Subject to page CSP? | Subject to CORS? | Needs host_permissions? |
|---------|----------------------|-------------------|------------------------|
| Service worker | No | No (with host_permissions) | Yes |
| Popup / options / side panel | No (extension CSP) | No (with host_permissions) | Yes |
| Content script (isolated) | Yes (connect-src) | Yes (page origin rules) | Not sufficient alone |
| Content script (main world) | Yes (fully) | Yes | N/A (no chrome.* API) |
| Offscreen document | No (extension origin) | No (with host_permissions) | Yes |

## 3. The relay pattern (CSP bypass)

The standard, officially recommended approach. Content script sends a request to the
service worker, which performs the fetch and returns the result.

### Basic relay

```typescript
// === content-script.ts ===
async function relayFetch(url: string, init?: RequestInit): Promise<{
  ok: boolean; status: number; headers: Record<string, string>; body: string;
}> {
  // Serialize RequestInit (Headers/body may not be structured-cloneable)
  const serialized: Record<string, any> = {};
  if (init?.method) serialized.method = init.method;
  if (init?.headers) {
    serialized.headers = init.headers instanceof Headers
      ? Object.fromEntries(init.headers.entries())
      : init.headers;
  }
  if (init?.body) {
    serialized.body = typeof init.body === 'string' ? init.body : String(init.body);
  }

  const response = await chrome.runtime.sendMessage({
    type: '__RELAY_FETCH',
    url,
    init: serialized,
  });

  if (response?.error) throw new Error(response.error);
  return response;
}

// Usage in content script
const result = await relayFetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer token' },
  body: JSON.stringify({ query: 'test' }),
});
const data = JSON.parse(result.body);
```

```typescript
// === background.ts ===
const ALLOWED_ORIGINS = [
  'https://api.example.com',
  'https://cdn.example.com',
];

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== '__RELAY_FETCH') return false;

  // Security: validate sender is a content script in a tab
  if (!sender.tab?.id) {
    sendResponse({ error: 'Unauthorized: not from a tab' });
    return true;
  }

  // Security: validate URL against allowlist
  try {
    const url = new URL(message.url);
    const allowed = ALLOWED_ORIGINS.some(o => message.url.startsWith(o));
    if (!allowed) {
      sendResponse({ error: `URL not allowed: ${url.origin}` });
      return true;
    }
  } catch {
    sendResponse({ error: 'Invalid URL' });
    return true;
  }

  fetch(message.url, message.init || {})
    .then(async (res) => {
      const headers: Record<string, string> = {};
      res.headers.forEach((v, k) => { headers[k] = v; });
      const body = await res.text();
      sendResponse({ ok: res.ok, status: res.status, headers, body });
    })
    .catch((err) => sendResponse({ error: err.message }));

  return true;
});
```

### Relay with binary data (ArrayBuffer)

For binary responses (images, files), base64-encode through the relay:

```typescript
// background.ts handler for binary
if (message.responseType === 'arraybuffer') {
  fetch(message.url, message.init)
    .then(res => res.arrayBuffer())
    .then(buf => {
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
      sendResponse({ ok: true, base64, mimeType: 'application/octet-stream' });
    })
    .catch(err => sendResponse({ error: err.message }));
  return true;
}

// content script: decode
const result = await relayFetch(url, { responseType: 'arraybuffer' });
const binary = Uint8Array.from(atob(result.base64), c => c.charCodeAt(0));
```

## 4. declarativeNetRequest

Rule-based network modification. Replaces MV2's `webRequest` blocking.
Requires `"declarativeNetRequest"` permission.

### Static rules (manifest)

```json
{
  "declarative_net_request": {
    "rule_resources": [{
      "id": "main_rules",
      "enabled": true,
      "path": "rules.json"
    }]
  }
}
```

```json
// rules.json
[
  {
    "id": 1,
    "priority": 1,
    "action": { "type": "block" },
    "condition": {
      "urlFilter": "tracker.example.com",
      "resourceTypes": ["script", "image", "xmlhttprequest"]
    }
  },
  {
    "id": 2,
    "priority": 1,
    "action": {
      "type": "redirect",
      "redirect": { "extensionPath": "/blocked.html" }
    },
    "condition": {
      "urlFilter": "malware.example.com",
      "resourceTypes": ["main_frame"]
    }
  },
  {
    "id": 3,
    "priority": 2,
    "action": {
      "type": "modifyHeaders",
      "requestHeaders": [
        { "header": "cookie", "operation": "remove" }
      ],
      "responseHeaders": [
        { "header": "set-cookie", "operation": "remove" },
        { "header": "x-frame-options", "operation": "remove" },
        { "header": "content-security-policy", "operation": "remove" }
      ]
    },
    "condition": {
      "urlFilter": "*",
      "initiatorDomains": ["target-site.com"],
      "resourceTypes": ["main_frame", "sub_frame"]
    }
  }
]
```

### Dynamic rules (runtime)

```typescript
// Add/update rules at runtime
await chrome.declarativeNetRequest.updateDynamicRules({
  removeRuleIds: [1000],  // remove old rule if exists
  addRules: [{
    id: 1000,
    priority: 1,
    action: {
      type: chrome.declarativeNetRequest.RuleActionType.MODIFY_HEADERS,
      responseHeaders: [{
        header: 'content-security-policy',
        operation: chrome.declarativeNetRequest.HeaderOperation.REMOVE,
      }],
    },
    condition: {
      initiatorDomains: ['example.com'],
      resourceTypes: [chrome.declarativeNetRequest.ResourceType.MAIN_FRAME],
    },
  }],
});

// List current dynamic rules
const rules = await chrome.declarativeNetRequest.getDynamicRules();

// Session rules (cleared on browser restart)
await chrome.declarativeNetRequest.updateSessionRules({
  addRules: [/* same format */],
});
```

### Rule limits

| Rule type | Max count |
|-----------|-----------|
| Static rules (per ruleset) | 330,000 |
| Enabled static rulesets | 50 |
| Dynamic rules | 30,000 |
| Session rules | 5,000 |
| Regex rules (across all) | 2,000 |

### Important: CSP header removal caveats

- `append` operation on CSP headers does NOT relax the policy (CSP spec says additional
  headers can only be more restrictive)
- `remove` is the only way to relax CSP via declarativeNetRequest
- This removes the ENTIRE CSP header, not individual directives
- Use `initiatorDomains` or `urlFilter` to scope narrowly

## 5. Offscreen documents for network + DOM

When you need both fetch() and DOM APIs (DOMParser, Canvas, Audio).
See `service-worker.md` for full offscreen document setup.

Key facts:
- Runs in extension origin (not subject to page CSP)
- Has fetch() and full DOM
- Only chrome.runtime API available
- One offscreen document per extension
- Must specify a Reason enum value
- Created on demand, can be closed when done

## 6. Host permissions and CORS

The service worker needs `host_permissions` to fetch cross-origin URLs without CORS errors:

```json
{
  "host_permissions": [
    "https://api.example.com/*",
    "https://cdn.example.com/*"
  ]
}
```

With matching host_permissions, the service worker's fetch() ignores CORS entirely.
Without them, normal CORS rules apply (the server must send appropriate headers).

**Prefer optional_host_permissions** for URLs not needed at install time:

```json
{
  "optional_host_permissions": ["https://*/*"]
}
```

Then request at runtime (must be in a user gesture handler):

```typescript
const granted = await chrome.permissions.request({
  origins: ['https://new-api.example.com/*']
});
```

## 7. Fetch gotchas in service workers

### No XMLHttpRequest

Service workers only support `fetch()`. No `XMLHttpRequest`, no `$.ajax`.

### Request body types

Service workers support: string, Blob, ArrayBuffer, FormData, URLSearchParams.
NOT supported: ReadableStream as body (in some Chrome versions).

### Streaming responses

```typescript
// Streaming is supported in SW fetch
const response = await fetch(url);
const reader = response.body!.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Process chunk. BUT: can't stream to content script via sendMessage.
  // Use Ports for streaming to content scripts.
}
```

### Fetch and SW termination

If the SW terminates during a pending fetch, the fetch is cancelled. For long-running
downloads, use a keep-alive pattern or delegate to an offscreen document.
