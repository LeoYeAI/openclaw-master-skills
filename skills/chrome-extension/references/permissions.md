# Permissions Reference

## Table of contents
1. Permission types
2. All available permissions and their warnings
3. activeTab strategy
4. Optional permissions (runtime request)
5. Host permissions
6. Permission removal
7. CWS review impact

## 1. Permission types

| Manifest key | When granted | User prompt | CWS impact |
|-------------|-------------|-------------|------------|
| `permissions` | At install | Install dialog | Always reviewed |
| `optional_permissions` | At runtime | Prompt dialog | Less scrutiny |
| `host_permissions` | At install | Install dialog | Triggers manual review if broad |
| `optional_host_permissions` | At runtime | Prompt dialog | Minimal impact |

## 2. All available permissions and their warnings

### No warning (safe to use freely)

`activeTab`, `alarms`, `contextMenus`, `declarativeNetRequestFeedback`,
`dns`, `enterprise.deviceAttributes`, `enterprise.hardwarePlatform`,
`enterprise.networkingAttributes`, `enterprise.platformKeys`, `favicon`,
`fileBrowserHandler`, `fontSettings`, `gcm`, `idle`, `loginState`,
`offscreen`, `power`, `printing`, `printingMetrics`, `runtime`,
`scripting`, `search`, `sidePanel`, `storage`, `system.cpu`,
`system.display`, `system.memory`, `system.storage`, `ttsEngine`,
`unlimitedStorage`, `webAuthenticationProxy`

### Warning-generating permissions

| Permission | Warning message |
|-----------|----------------|
| `bookmarks` | Read and change your bookmarks |
| `clipboardRead` | Read data you copy and paste |
| `clipboardWrite` | Modify data you copy and paste |
| `contentSettings` | Change settings that control websites' access... |
| `cookies` | (combined with host permissions warning) |
| `debugger` | Access the page debugger backend |
| `declarativeNetRequest` | Block page content |
| `desktopCapture` | Capture content of your screen |
| `downloads` | Manage your downloads |
| `geolocation` | Detect your physical location |
| `history` | Read and change your browsing history |
| `identity` | Know your email address |
| `management` | Manage your apps, extensions, and themes |
| `nativeMessaging` | Communicate with cooperating native applications |
| `notifications` | Display notifications |
| `pageCapture` | Read and change all your data on all websites |
| `privacy` | Change privacy-related settings |
| `proxy` | Read and modify proxy settings |
| `tabCapture` | Read and change all your data on all websites |
| `tabs` | Read your browsing activity (URL, title, favicon) |
| `topSites` | Read a list of your most frequently visited sites |
| `tts` | N/A (generally no warning) |
| `webNavigation` | Read your browsing activity |
| `webRequest` | (varies, usually combined with host permissions) |

### Host permission warnings

| Pattern | Warning |
|---------|---------|
| `<all_urls>` | Read and change all your data on all websites |
| `https://*/*` | Read and change all your data on all websites |
| `https://*.google.com/*` | Read and change your data on all google.com sites |
| `https://example.com/*` | Read and change your data on example.com |

## 3. activeTab strategy

`activeTab` is the most important permission for CWS-friendly extensions. It grants
temporary access to the current tab ONLY when the user explicitly invokes the extension:

**Triggers that grant activeTab**:
- Clicking the extension icon (action)
- Using a keyboard shortcut (command)
- Selecting a context menu item
- Accepting a suggestion from the omnibox

**What it grants (temporarily)**:
- `chrome.scripting.executeScript` on that tab
- `chrome.scripting.insertCSS` on that tab
- Access to `tab.url`, `tab.title`, `tab.favIconUrl` for that tab
- Host permission for that tab's origin

**What it does NOT grant**:
- Persistent access (revoked on navigation or tab close)
- Access to other tabs
- Background injection without user gesture

**No install warning.** This is the key advantage.

```json
// Minimal, warning-free permission set
{
  "permissions": ["activeTab", "scripting", "storage"]
}
```

## 4. Optional permissions (runtime request)

Request permissions only when the user needs a specific feature:

```typescript
// Check if already granted
const hasPermission = await chrome.permissions.contains({
  permissions: ['bookmarks'],
  origins: ['https://api.example.com/*'],
});

if (hasPermission) {
  useFeature();
  return;
}

// Request (MUST be in a click/gesture handler)
document.getElementById('enable-btn')!.addEventListener('click', async () => {
  const granted = await chrome.permissions.request({
    permissions: ['bookmarks'],
    origins: ['https://api.example.com/*'],
  });

  if (granted) {
    useFeature();
  } else {
    showExplanation();
  }
});
```

### Best practices for runtime permission requests

1. **Explain before asking**: show why the permission is needed before calling request()
2. **Request just-in-time**: ask when the user activates the feature, not at startup
3. **Handle denial gracefully**: the feature should degrade, not crash
4. **Don't ask repeatedly**: if denied, show a manual enable path
5. **Combine permissions**: batch related permissions in one request dialog

### Permissions you CANNOT request at runtime

Some permissions can only be declared in manifest `permissions`:
`debugger`, `declarativeNetRequest`, `devtools`, `experimental`, `geolocation`,
`mdns`, `proxy`, `tts`, `ttsEngine`, `wallpaper`.

## 5. Host permissions deep dive

Host permissions control which origins the extension can interact with:
- `fetch()` from service worker/extension pages to that origin (bypasses CORS)
- `chrome.scripting.executeScript()` on pages from that origin
- `chrome.tabs.sendMessage()` to content scripts on that origin
- Access to `tab.url` for tabs on that origin (without `tabs` permission)

### Narrowing host permissions

```json
// ❌ BAD: triggers scary warning + manual CWS review
"host_permissions": ["<all_urls>"]

// ✅ BETTER: specific domains
"host_permissions": ["https://api.myservice.com/*"]

// ✅ BEST: optional, requested at runtime
"optional_host_permissions": ["https://*/*"]
```

### Host permission with activeTab

With `activeTab`, you don't need host_permissions for the current tab when the user
invokes the extension. You only need host_permissions for:
- Background fetches to your API
- Programmatic tab injection without user gesture
- Cross-origin requests from the service worker

## 6. Permission removal

Remove permissions you no longer need:

```typescript
await chrome.permissions.remove({
  permissions: ['bookmarks'],
  origins: ['https://old-api.example.com/*'],
});
```

Benefits:
- Reduces attack surface
- Improves user trust
- Reduces CWS review scope on next update

## 7. CWS review impact

| Permissions | Review type | Typical time |
|------------|------------|--------------|
| `activeTab` + `storage` + `scripting` | Automated | Hours to 1 day |
| + specific host_permissions (1-2 domains) | Automated | 1-3 days |
| + `tabs` or `webNavigation` | May trigger manual | 3-7 days |
| + `<all_urls>` or `https://*/*` | Manual review | 1-4 weeks |
| + `declarativeNetRequest` + broad hosts | Manual review | 1-4 weeks |
| + `debugger` or `nativeMessaging` | Deep manual review | 2-6 weeks |

**Every permission you declare must be used.** Unused permissions cause CWS rejection.
Justify each permission in your submission and privacy policy.
