# Chrome Web Store Publishing Reference

## Table of contents
1. Submission checklist
2. Required assets
3. Privacy policy requirements
4. Common rejection reasons and fixes
5. Update process
6. Enterprise distribution (alternative)

## 1. Submission checklist

Before submitting to the Chrome Web Store:

- [ ] `manifest.json` has `name`, `version`, `description`, correct `manifest_version: 3`
- [ ] Icons: 16, 48, 128px PNGs included and referenced in manifest
- [ ] Every declared permission is actually used in code
- [ ] No unused permissions (causes rejection)
- [ ] No `eval()`, `new Function()`, `document.write()` with dynamic strings
- [ ] No remote code loading (all JS bundled locally)
- [ ] Code is not obfuscated (minified is OK)
- [ ] Privacy policy URL ready (if you collect ANY data)
- [ ] Store listing screenshots (1280x800 or 640x400)
- [ ] Store description (up to 132 chars for short, detailed for long)
- [ ] Category selected
- [ ] Single purpose clearly defined
- [ ] Tested in Chrome stable (not just Canary/Dev)
- [ ] `host_permissions` are as narrow as possible

## 2. Required assets

### Store listing images

| Asset | Size | Required |
|-------|------|----------|
| Icon | 128x128 PNG | Yes |
| Screenshots | 1280x800 or 640x400 | Yes (1-5) |
| Small promo tile | 440x280 | No but recommended |
| Large promo tile | 920x680 | No |
| Marquee promo tile | 1400x560 | No |

### Store listing text

- **Name**: max 75 chars (45 recommended for display)
- **Short description**: max 132 chars (shows in search results)
- **Detailed description**: no hard limit, supports basic formatting
- **Category**: choose the most specific match
- **Language**: primary language + translations

## 3. Privacy policy requirements

Required if your extension:
- Collects, transmits, or stores user data
- Uses any personal or sensitive data
- Has `host_permissions` or `tabs` permission
- Uses `cookies`, `history`, `bookmarks`, `identity`

The privacy policy must disclose:
- What data is collected
- How data is used
- Whether data is shared with third parties
- How users can request data deletion
- Data retention period

Host it on a publicly accessible URL (your website, GitHub page, Notion page).

**Even for extensions that don't collect data**, consider adding a simple policy:
"This extension does not collect, store, or transmit any user data."

## 4. Common rejection reasons and fixes

### Excessive permissions (~36% of rejections)

**Problem**: requesting permissions you don't use or requesting broad permissions
when narrow ones suffice.

**Fix**:
- Remove every permission not actively used in code
- Replace `<all_urls>` with specific domains
- Replace `tabs` with `activeTab` if you only need the current tab
- Move non-essential permissions to `optional_permissions`
- Add justification in the "Permission justification" field

### Missing or inadequate privacy policy (~29%)

**Problem**: no privacy policy, or policy doesn't match actual data practices.

**Fix**: create a privacy policy page that specifically addresses your extension's
data handling. Update it when you add features.

### Single purpose violation

**Problem**: extension does too many unrelated things.

**Fix**: each extension should have ONE clear purpose. If you have multiple features,
they should all serve the same core purpose. Example: "Tab manager" is OK. "Tab manager
+ ad blocker + screenshot tool" is not.

### Remote code execution

**Problem**: loading JS from external servers, using `eval()`, or using `document.write()`
with dynamic content.

**Fix**: bundle ALL code locally. If you need dynamic behavior, use `chrome.storage`
for configuration, not remote scripts. For template engines, use sandbox pages.

### Obfuscated code

**Problem**: code is intentionally made unreadable (not just minified).

**Fix**: submit readable or minified (not obfuscated) code. Reviewers must be able
to understand what your code does. Source maps are not a substitute.

### Deceptive functionality

**Problem**: extension does something different than described, or has hidden features.

**Fix**: store listing must accurately describe ALL extension behavior. No hidden
data collection, no undisclosed network requests.

### Keyword spam in listing

**Problem**: stuffing description with competitor names or unrelated keywords.

**Fix**: describe your extension's actual features. Don't mention competitors by name
in the description.

## 5. Update process

### Publishing an update

1. Increment `version` in manifest.json (must be higher than current CWS version)
2. Create a new zip of the extension
3. Upload to CWS dashboard (same listing)
4. Fill in changelog (optional but recommended)
5. Submit for review

### Auto-update timeline

- Chrome checks for updates every few hours
- Users receive updates automatically (no action required)
- The old version continues running until Chrome restarts or the update is applied
- Content scripts from the old version become orphaned (see content-scripts.md)

### Breaking changes in updates

When updating, handle data migration in `chrome.runtime.onInstalled`:

```typescript
chrome.runtime.onInstalled.addListener(async ({ reason, previousVersion }) => {
  if (reason === 'update') {
    // Migrate data, re-inject content scripts, etc.
  }
});
```

### Staged rollout

CWS supports percentage-based rollout (5%, 10%, 50%, 100%). Use this for risky
updates to catch issues early.

## 6. Enterprise distribution

For internal/corporate extensions not on the CWS:

### Self-hosted

Host a `.crx` file and an `update_url` XML file:

```json
// manifest.json
{ "update_url": "https://yourserver.com/updates.xml" }
```

```xml
<!-- updates.xml -->
<?xml version='1.0' encoding='UTF-8'?>
<gupdate xmlns='http://www.google.com/update2/response' protocol='2.0'>
  <app appid='YOUR_EXTENSION_ID'>
    <updatecheck crid='YOUR_EXTENSION_ID' version='1.0.0'
                 prodversionmin='116'
                 hash_sha256='...'
                 url='https://yourserver.com/extension.crx'/>
  </app>
</gupdate>
```

Requires enterprise policy to allowlist the extension ID.

### Developer mode (testing only)

Load unpacked at `chrome://extensions` with Developer Mode enabled.
Not suitable for distribution. Extension ID changes between machines.
