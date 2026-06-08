# Manifest V3 Complete Reference

## Table of contents
1. Required fields
2. All manifest fields
3. Icons
4. Versioning
5. Content Security Policy
6. Web accessible resources
7. Minimal vs full manifest examples

## 1. Required fields

Every MV3 extension must declare these three fields:

```json
{
  "manifest_version": 3,
  "name": "Extension Name (max 45 chars)",
  "version": "1.0.0"
}
```

`version` must be 1-4 dot-separated integers (e.g., `1.0.0.1`). Use `version_name` for
human-readable display (e.g., `"1.0 beta"`).

## 2. All manifest fields

```json
{
  // === REQUIRED ===
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",

  // === RECOMMENDED ===
  "description": "One sentence, max 132 chars for CWS",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },

  // === BACKGROUND ===
  "background": {
    "service_worker": "background.js",
    "type": "module"                    // enables ES import/export
  },

  // === CONTENT SCRIPTS ===
  "content_scripts": [
    {
      "matches": ["https://*.example.com/*"],
      "js": ["content.js"],
      "css": ["content.css"],
      "run_at": "document_idle",        // document_start | document_end | document_idle
      "all_frames": false,              // inject into iframes too?
      "match_about_blank": false,       // inject into about:blank frames?
      "match_origin_as_fallback": false, // inject into blob:/data: frames?
      "world": "ISOLATED",             // ISOLATED | MAIN
      "exclude_matches": ["*://example.com/admin/*"],
      "include_globs": [],
      "exclude_globs": []
    }
  ],

  // === UI SURFACES ===
  "action": {
    "default_popup": "popup.html",
    "default_icon": { "16": "icon16.png", "48": "icon48.png" },
    "default_title": "Click to open"
  },
  "options_page": "options.html",       // full-page options
  "options_ui": {                       // embedded in chrome://extensions
    "page": "options.html",
    "open_in_tab": false
  },
  "side_panel": {
    "default_path": "sidepanel.html"
  },
  "devtools_page": "devtools.html",

  // === PERMISSIONS ===
  "permissions": [
    "storage",          // chrome.storage
    "activeTab",        // temporary access to current tab on user gesture
    "scripting",        // chrome.scripting.executeScript
    "alarms",           // chrome.alarms
    "contextMenus",     // chrome.contextMenus
    "notifications",    // chrome.notifications
    "sidePanel",        // chrome.sidePanel
    "offscreen",        // chrome.offscreen
    "tabs",             // chrome.tabs (url, title, favIconUrl access)
    "identity",         // chrome.identity (OAuth)
    "cookies",          // chrome.cookies
    "webNavigation",    // chrome.webNavigation
    "declarativeNetRequest",           // Rule-based network modification
    "declarativeNetRequestWithHostAccess" // Same + host permission check
  ],
  "optional_permissions": ["bookmarks", "history", "downloads"],
  "host_permissions": ["https://api.example.com/*"],
  "optional_host_permissions": ["https://*/*"],

  // === NETWORK RULES ===
  "declarative_net_request": {
    "rule_resources": [
      {
        "id": "ruleset_1",
        "enabled": true,
        "path": "rules.json"
      }
    ]
  },

  // === WEB ACCESSIBLE RESOURCES ===
  "web_accessible_resources": [
    {
      "resources": ["images/*.png", "styles/injected.css"],
      "matches": ["https://*.example.com/*"]
    },
    {
      "resources": ["worker.js"],
      "matches": ["<all_urls>"],
      "use_dynamic_url": true           // randomized URL, prevents fingerprinting
    }
  ],

  // === COMMANDS (keyboard shortcuts) ===
  "commands": {
    "_execute_action": {                // built-in: triggers action click
      "suggested_key": { "default": "Ctrl+Shift+Y", "mac": "Command+Shift+Y" },
      "description": "Open popup"
    },
    "toggle-feature": {
      "suggested_key": { "default": "Ctrl+Shift+F" },
      "description": "Toggle the feature"
    }
  },

  // === INTERNATIONALIZATION ===
  "default_locale": "en",              // required if _locales/ exists

  // === CONTENT SECURITY POLICY ===
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'",
    "sandbox": "sandbox allow-scripts; script-src 'self' 'unsafe-eval'"
  },

  // === OTHER ===
  "homepage_url": "https://example.com",
  "short_name": "Ext",                 // max 12 chars, used when space is limited
  "author": "Your Name",
  "version_name": "1.0 beta",          // human-readable, not used for updates
  "minimum_chrome_version": "116",
  "incognito": "spanning",             // spanning | split | not_allowed
  "sandbox": {
    "pages": ["sandbox.html"]           // pages with relaxed CSP (allow eval)
  },
  "externally_connectable": {
    "matches": ["https://*.example.com/*"],
    "ids": ["other_extension_id"]       // allow cross-extension messaging
  },
  "chrome_url_overrides": {
    "newtab": "newtab.html"            // or "bookmarks" or "history"
  },
  "omnibox": { "keyword": "myext" },
  "update_url": "https://example.com/updates.xml"  // enterprise self-hosting
}
```

## 3. Icons

Provide at least 16, 48, and 128px PNG icons. Chrome uses them in different contexts:

| Size | Used in |
|------|---------|
| 16px | Toolbar, favicon, context menus |
| 32px | Windows taskbar (2x of 16) |
| 48px | Extensions management page |
| 128px | Chrome Web Store, installation dialog |

SVG is NOT supported in manifest icon fields. Use PNG with transparency.

For the action icon specifically, provide 16 and 32 (or 19 and 38 for exact toolbar sizing).
Chrome auto-scales, but crisp icons at native sizes look best.

## 4. Versioning

- `version`: 1-4 integers separated by dots. `1.0` < `1.1` < `2.0`. Used for auto-updates.
- Published version must always be higher than the previous CWS version.
- CWS compares numerically: `1.10.0` > `1.9.0`.
- `version_name` is cosmetic only (display in chrome://extensions).

## 5. Content Security Policy (extension pages)

MV3 extensions cannot use `unsafe-eval` or `unsafe-inline` in extension_pages CSP.
The default is already restrictive:

```
script-src 'self'; object-src 'self'
```

You can tighten it but not relax it (no remote scripts, no inline scripts, no eval).

For sandbox pages, `unsafe-eval` IS allowed (useful for template engines):

```json
"content_security_policy": {
  "sandbox": "sandbox allow-scripts allow-forms; script-src 'self' 'unsafe-eval'"
}
```

Sandbox pages have no access to chrome.* APIs.

## 6. Web accessible resources (MV3 changes)

In MV3, web_accessible_resources require explicit match patterns. No more global access:

```json
"web_accessible_resources": [{
  "resources": ["inject.js", "styles.css"],
  "matches": ["https://example.com/*"]    // only this origin can access
}]
```

Access via: `chrome.runtime.getURL('inject.js')` returns `chrome-extension://<id>/inject.js`.

Set `use_dynamic_url: true` to prevent fingerprinting (URL changes each session).

## 7. Match patterns syntax

```
<scheme>://<host><path>

Scheme:  http | https | file | ftp | * (http+https) | chrome-extension
Host:    *.example.com | example.com | * (any host)
Path:    /* | /path/* | /specific/page.html

Special: <all_urls> = matches everything (avoid for CWS approval)
```

Examples:
- `https://*.google.com/*` - all Google subdomains over HTTPS
- `*://example.com/api/*` - HTTP or HTTPS, specific path
- `file:///*` - local files (requires user opt-in)
- `http://localhost:*/*` - localhost any port
