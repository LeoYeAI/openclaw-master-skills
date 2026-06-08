# Web Accessible Resources Reference

## What are web accessible resources?

Extension files (scripts, images, CSS, HTML) that web pages can access. By default,
extension resources are NOT accessible from web pages. You must explicitly declare them.

## MV3 declaration (scoped by origin)

```json
{
  "web_accessible_resources": [
    {
      "resources": ["inject.js", "styles/*.css", "images/logo.png"],
      "matches": ["https://example.com/*"]
    },
    {
      "resources": ["shared-widget.js"],
      "matches": ["<all_urls>"],
      "use_dynamic_url": true
    },
    {
      "resources": ["inter-ext-page.html"],
      "extension_ids": ["other_extension_id"]
    }
  ]
}
```

### Fields

- `resources`: glob patterns for files to expose
- `matches`: URL patterns of pages that can access these resources
- `extension_ids`: other extensions that can access (for cross-extension resources)
- `use_dynamic_url`: if `true`, URL changes each session (prevents fingerprinting)

## Accessing from web pages

```javascript
// From content script or main world script
const url = chrome.runtime.getURL('images/logo.png');
// Returns: chrome-extension://abcdef123456/images/logo.png

// Or with dynamic URL: chrome-extension://abcdef123456/dynamic-hash/images/logo.png
```

## Common use cases

### Injecting a script into the page's main world

```typescript
// content-script.ts
const script = document.createElement('script');
script.src = chrome.runtime.getURL('inject.js');
script.onload = () => script.remove(); // clean up
(document.head || document.documentElement).appendChild(script);
```

Requires `inject.js` in web_accessible_resources.

### Loading extension CSS into a page

```typescript
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = chrome.runtime.getURL('styles/content.css');
document.head.appendChild(link);
```

### Loading images in content script UI

```typescript
const img = document.createElement('img');
img.src = chrome.runtime.getURL('images/icon.png');
```

### Embedding extension HTML in an iframe

```typescript
const iframe = document.createElement('iframe');
iframe.src = chrome.runtime.getURL('widget.html');
iframe.style.cssText = 'width:400px;height:300px;border:none;position:fixed;z-index:999999;';
document.body.appendChild(iframe);
```

The iframe runs in the extension's origin and has access to chrome.* APIs.

## Security implications

**Fingerprinting risk**: any page matching the `matches` pattern can probe for your
extension by trying to load a web_accessible_resource. Use `use_dynamic_url: true`
to mitigate (URL changes each browser session).

**Scope narrowly**: only expose files that MUST be page-accessible. Never expose
your entire extension directory.

**No sensitive data**: never put API keys, tokens, or private logic in web-accessible
files. They're readable by any matching page.

**Content script injection vs web_accessible_resources**: for script injection into the
page, prefer `chrome.scripting.executeScript({ world: 'MAIN', func: ... })` over
loading a web_accessible_resource via `<script>` tag. The former doesn't require
the file to be web-accessible and is harder to fingerprint.
