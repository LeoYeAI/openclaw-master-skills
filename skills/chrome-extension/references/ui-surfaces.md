# UI Surfaces Reference

## Table of contents
1. Popup
2. Options page
3. Side panel
4. Context menus
5. Commands (keyboard shortcuts)
6. Notifications
7. Omnibox
8. DevTools panel
9. Choosing the right surface

## 1. Popup

The popup is an HTML page shown when the user clicks the extension icon. It is
**destroyed immediately** when it loses focus (clicking elsewhere, switching tabs).

### Manifest

```json
{
  "action": {
    "default_popup": "popup.html",
    "default_icon": { "16": "icon16.png", "48": "icon48.png" },
    "default_title": "My Extension"
  }
}
```

### Key behaviors

- Created fresh every time it opens. No state persists between opens.
- Has full access to all chrome.* APIs the extension has permission for.
- Max dimensions: 800x600 px. Set dimensions via CSS on `body`/`html`.
- Cannot be opened programmatically (only by user clicking the icon).
- `console.log` output appears in the popup's own DevTools (right-click icon → Inspect Popup).

### Popup with React (minimal)

```html
<!-- popup.html -->
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>body{width:350px;min-height:200px;margin:0;}</style></head>
<body><div id="root"></div><script src="popup.js" type="module"></script></body>
</html>
```

```typescript
// popup.tsx
import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';

function Popup() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    chrome.storage.local.get('cachedData').then(r => setData(r.cachedData));
  }, []);

  const handleAction = async () => {
    const result = await chrome.runtime.sendMessage({ type: 'DO_THING' });
    setData(result);
    await chrome.storage.local.set({ cachedData: result });
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>My Extension</h2>
      <button onClick={handleAction}>Do Thing</button>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<Popup />);
```

### Badge (icon overlay)

```typescript
// Set badge text and color (from service worker or popup)
chrome.action.setBadgeText({ text: '42' });
chrome.action.setBadgeBackgroundColor({ color: '#e53e3e' });
chrome.action.setBadgeTextColor({ color: '#ffffff' }); // Chrome 110+

// Per-tab badge
chrome.action.setBadgeText({ text: 'ON', tabId: tab.id });

// Clear badge
chrome.action.setBadgeText({ text: '' });
```

### Dynamic icon

```typescript
// Set icon per state
chrome.action.setIcon({
  path: { 16: 'icons/active-16.png', 48: 'icons/active-48.png' },
});

// Canvas-drawn icon (from offscreen doc, since SW has no Canvas)
chrome.action.setIcon({
  imageData: { 16: imageData16, 32: imageData32 },
});

// Disable/enable the action button
chrome.action.disable(tabId);
chrome.action.enable(tabId);
```

## 2. Options page

### Embedded in chrome://extensions

```json
{
  "options_ui": {
    "page": "options.html",
    "open_in_tab": false
  }
}
```

### Full-page options

```json
{
  "options_page": "options.html"
}
```

Open programmatically: `chrome.runtime.openOptionsPage()`.

Both have full chrome.* API access. Use `chrome.storage.sync` for settings
so they sync across devices.

## 3. Side panel (Chrome 114+)

Unlike popups, side panels **persist across tab switches** and don't close on
focus loss. Requires `"sidePanel"` permission.

### Manifest

```json
{
  "permissions": ["sidePanel"],
  "side_panel": { "default_path": "sidepanel.html" }
}
```

### Open on action click (instead of popup)

```typescript
// service worker
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
```

Cannot have both default_popup and openPanelOnActionClick. Choose one.

### Per-tab panel content

```typescript
chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!tab.url) return;
  const url = new URL(tab.url);

  if (url.hostname === 'github.com') {
    await chrome.sidePanel.setOptions({
      tabId,
      path: 'panels/github.html',
      enabled: true,
    });
  } else {
    await chrome.sidePanel.setOptions({
      tabId,
      path: 'panels/default.html',
      enabled: true,
    });
  }
});
```

### Open programmatically

```typescript
// Must be called from a user gesture handler
chrome.sidePanel.open({ windowId: chrome.windows.WINDOW_ID_CURRENT });
```

## 4. Context menus

Requires `"contextMenus"` permission.

```typescript
// Create menus in onInstalled (they persist, so don't recreate every SW wake)
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'lookup-selection',
    title: 'Look up "%s"',           // %s = selected text
    contexts: ['selection'],          // only shows when text is selected
  });

  chrome.contextMenus.create({
    id: 'save-image',
    title: 'Save to collection',
    contexts: ['image'],              // only on images
  });

  chrome.contextMenus.create({
    id: 'parent-menu',
    title: 'My Extension',
    contexts: ['page'],
  });

  chrome.contextMenus.create({
    id: 'child-action-1',
    parentId: 'parent-menu',
    title: 'Action 1',
    contexts: ['page'],
  });
});

// Handle clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  switch (info.menuItemId) {
    case 'lookup-selection':
      const query = info.selectionText;
      chrome.tabs.create({ url: `https://search.com?q=${encodeURIComponent(query!)}` });
      break;
    case 'save-image':
      saveImage(info.srcUrl!);
      break;
  }
});
```

Context types: `all`, `page`, `frame`, `selection`, `link`, `editable`, `image`,
`video`, `audio`, `launcher` (ChromeOS), `browser_action`, `page_action`, `action`.

## 5. Commands (keyboard shortcuts)

### Manifest

```json
{
  "commands": {
    "_execute_action": {
      "suggested_key": { "default": "Ctrl+Shift+Y", "mac": "Command+Shift+Y" },
      "description": "Open extension"
    },
    "toggle-feature": {
      "suggested_key": { "default": "Alt+T" },
      "description": "Toggle feature on/off"
    },
    "no-default-key": {
      "description": "User must set this shortcut manually in chrome://extensions/shortcuts"
    }
  }
}
```

### Handle in service worker

```typescript
chrome.commands.onCommand.addListener((command, tab) => {
  if (command === 'toggle-feature') {
    chrome.tabs.sendMessage(tab!.id!, { type: 'TOGGLE' });
  }
});
```

`_execute_action` triggers the popup or `action.onClicked` (if no popup). No need
to listen for it explicitly.

Users can remap shortcuts at `chrome://extensions/shortcuts`.

## 6. Notifications

Requires `"notifications"` permission.

```typescript
// Basic notification
chrome.notifications.create('notif-id', {
  type: 'basic',
  iconUrl: 'icons/icon128.png',
  title: 'Task Complete',
  message: 'Your export finished successfully.',
  priority: 2,              // -2 to 2
  requireInteraction: true, // don't auto-dismiss
  buttons: [
    { title: 'Open File' },
    { title: 'Dismiss' },
  ],
});

// Handle button clicks
chrome.notifications.onButtonClicked.addListener((notifId, buttonIndex) => {
  if (notifId === 'notif-id' && buttonIndex === 0) {
    chrome.tabs.create({ url: 'results.html' });
  }
  chrome.notifications.clear(notifId);
});

// Handle notification click (body click)
chrome.notifications.onClicked.addListener((notifId) => {
  chrome.notifications.clear(notifId);
});

// Image notification
chrome.notifications.create('image-notif', {
  type: 'image',
  iconUrl: 'icons/icon128.png',
  title: 'New Photo',
  message: 'Check out this image',
  imageUrl: 'path/to/image.png',
});
```

## 7. Omnibox

Register a keyword trigger in the address bar.

```json
{ "omnibox": { "keyword": "myext" } }
```

```typescript
// Provide suggestions as user types "myext <query>"
chrome.omnibox.onInputChanged.addListener((text, suggest) => {
  suggest([
    { content: `search ${text}`, description: `Search for: <match>${text}</match>` },
    { content: `lucky ${text}`, description: `I'm feeling lucky: <match>${text}</match>` },
  ]);
});

// Handle selection
chrome.omnibox.onInputEntered.addListener((text, disposition) => {
  const url = text.startsWith('search ')
    ? `https://search.com?q=${encodeURIComponent(text.slice(7))}`
    : `https://example.com/${encodeURIComponent(text)}`;

  switch (disposition) {
    case 'currentTab':
      chrome.tabs.update({ url });
      break;
    case 'newForegroundTab':
      chrome.tabs.create({ url });
      break;
    case 'newBackgroundTab':
      chrome.tabs.create({ url, active: false });
      break;
  }
});
```

## 8. DevTools panel

Extend Chrome DevTools with a custom panel.

```json
{ "devtools_page": "devtools.html" }
```

```html
<!-- devtools.html (invisible, just loads the script) -->
<!DOCTYPE html>
<html><body><script src="devtools.js"></script></body></html>
```

```javascript
// devtools.js
chrome.devtools.panels.create(
  'My Panel',          // title
  'icons/icon16.png',  // icon
  'panel.html'         // page
);
```

The panel page (panel.html) has access to `chrome.devtools` APIs:
- `chrome.devtools.inspectedWindow.eval()` - run JS in the inspected page
- `chrome.devtools.network` - network request monitoring
- `chrome.devtools.panels` - sidebar panes, element selection

## 9. Choosing the right surface

| Need | Surface | Why |
|------|---------|-----|
| Quick action, no persistent state | Popup | Simple, familiar UX |
| Persistent side content while browsing | Side panel | Survives tab switches |
| Extension configuration | Options page | Standard pattern |
| Right-click actions | Context menu | Contextual, discoverable |
| Power user shortcuts | Commands | Fast, keyboard-first |
| Background alerts | Notifications | Non-intrusive |
| Address bar integration | Omnibox | Search-like UX |
| Developer tooling | DevTools panel | Inspects page internals |
| In-page overlay/widget | Content script + Shadow DOM | Tight page integration |
