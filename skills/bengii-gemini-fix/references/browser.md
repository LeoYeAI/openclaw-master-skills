# Browser Tool — Detailed Reference

Full browser automation via CDP (Chrome DevTools Protocol). OpenClaw manages a separate browser profile for the agent with deterministic tab control.

## What You Get

- A separate browser profile named `openclaw` (orange accent by default).
- Deterministic tab control (list/open/focus/close).
- Agent actions (click/type/drag/select), snapshots, screenshots, PDFs.
- Optional multi-profile support (`openclaw`, `work`, `remote`, …).

## Quick Start

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

## Profiles: `openclaw` vs `chrome`

- **`openclaw`**: Managed, isolated browser (no extension required).
- **`chrome`**: Extension relay to your system browser (requires the OpenClaw extension attached to a tab).

```json5
{ browser: { defaultProfile: "openclaw" } }
```

### Profile Types

- **openclaw-managed**: Dedicated Chromium instance with own user data dir + CDP port.
- **remote**: Explicit CDP URL (browser running elsewhere).
- **extension relay**: Existing Chrome tab(s) via relay + Chrome extension.

Notes:
- `openclaw` profile is auto-created if missing.
- `chrome` profile is built-in for the extension relay (points at `http://127.0.0.1:18792` by default).
- Local CDP ports allocate from 18800–18899 by default.
- Deleting a profile moves its local data directory to Trash.

## Configuration

```json5
{
  browser: {
    enabled: true,                    // default: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true,  // default trusted-network mode
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    remoteCdpTimeoutMs: 1500,        // remote CDP HTTP timeout
    remoteCdpHandshakeTimeoutMs: 3000, // remote CDP WebSocket timeout
    defaultProfile: "chrome",         // "openclaw" for managed browser
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,                // never launch; attach only
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work:     { cdpPort: 18801, color: "#0066CC" },
      remote:   { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

### Port Convention

- Browser control service: `gateway.port + 2` (default: 18791).
- Relay port: 18792.
- Per-profile CDP ports: 18800–18899.

If you override `gateway.port`, derived browser ports shift to the same "family".

## Use Brave (or Another Chromium Browser)

```json5
// macOS
{ browser: { executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" } }
// Windows
{ browser: { executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe" } }
// Linux
{ browser: { executablePath: "/usr/bin/brave-browser" } }
```

Or via CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

### Browser Auto-Detection Order

1. Chrome → 2. Brave → 3. Edge → 4. Chromium → 5. Chrome Canary

- macOS: checks `/Applications` and `~/Applications`.
- Linux: looks for `google-chrome`, `brave`, `microsoft-edge`, `chromium`, etc.
- Windows: checks common install locations.

## Local vs Remote Control

- **Local control** (default): Gateway starts loopback control service, can launch a local browser.
- **Remote control (node host)**: Run a node host on the browser machine; Gateway proxies browser actions.
- **Remote CDP**: Set `browser.profiles.<name>.cdpUrl` or `browser.cdpUrl` to attach to a remote Chromium browser. No local browser launched.

Auth for remote CDP:
- Query tokens: `https://provider.example?token=<token>`
- HTTP Basic auth: `https://user:pass@provider.example`

## Node Browser Proxy (Zero-Config Default)

- Node host exposes its local browser control server via proxy.
- Profiles come from the node's own `browser.profiles` config.
- Disable:
  - On the node: `nodeHost.browserProxy.enabled=false`
  - On the gateway: `gateway.nodes.browser.mode="off"`

## Browserless (Hosted Remote CDP)

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "https://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

## Chrome Extension Relay

[Chrome extension](https://docs.openclaw.ai/tools/chrome-extension):
- Gateway or node host runs locally (same machine).
- Local relay server listens at loopback `cdpUrl` (default: `http://127.0.0.1:18792`).
- You click the OpenClaw Browser Relay extension icon on a tab to attach.
- Agent controls that tab via the normal `browser` tool by selecting the right profile.

## Isolation Guarantees

- **Dedicated user data dir**: Never touches your personal browser profile.
- **Dedicated ports**: Avoids 9222 to prevent collisions with dev workflows.
- **Deterministic tab control**: Target tabs by `targetId`, not "last tab".

## Agent Tool API

The `browser` tool supports:

- `browser snapshot` — returns a stable UI tree (AI or ARIA mode).
- `browser act` — uses snapshot `ref` IDs to click/type/drag/select.
- `browser screenshot` — captures pixels (full page or element).

Parameters:
- `profile` — choose a named browser profile.
- `target` — `sandbox | host | node` to select where the browser lives.
  - Sandboxed sessions default to `sandbox`, non-sandbox to `host`.
  - `target: "host"` in sandbox requires `agents.defaults.sandbox.browser.allowHostControl=true`.
  - If a browser-capable node is connected, auto-routes unless you pin `target`.

## Control API (Optional)

HTTP endpoints (optional, for programmatic control):

| Endpoint | Description |
|---|---|
| `GET /`, `POST /start`, `POST /stop` | Status/start/stop |
| `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId` | Tab control |
| `GET /snapshot`, `POST /screenshot` | Snapshot/screenshot |
| `POST /navigate`, `POST /act` | Navigation and actions |
| `POST /hooks/file-chooser`, `POST /hooks/dialog` | Hooks |
| `POST /download`, `POST /wait/download` | Downloads |
| `GET /console`, `POST /pdf` | Debugging |
| `GET /errors`, `GET /requests` | Error/request logs |
| `POST /trace/start`, `POST /trace/stop`, `POST /highlight` | Tracing |
| `POST /response/body` | Network responses |
| `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear` | Cookie state |
| `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear` | Storage |
| `POST /set/offline`, `POST /set/headers`, `POST /set/credentials` | Settings |
| `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone` | Settings |
| `POST /set/locale`, `POST /set/device` | Settings |

Auth: `Authorization: Bearer <gateway token>` or `x-openclaw-password: <gateway password>`.

Profile selection: append `?profile=<name>` to any endpoint.

## Security & Privacy

- The `openclaw` browser profile may contain logged-in sessions; treat as sensitive.
- `browser act kind=evaluate` / `openclaw browser evaluate` and `wait --fn` execute arbitrary JavaScript. Disable with `browser.evaluateEnabled=false`.
- For logins and anti-bot notes (X/Twitter, etc.), see [Browser login](https://docs.openclaw.ai/tools/browser-login).
- Keep Gateway/node host private (loopback or tailnet-only).
- Remote CDP endpoints are powerful; tunnel and protect them.

### SSRF Policy

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,            // strict public-only
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

- `dangerouslyAllowPrivateNetwork` defaults to `true` (trusted-network model).
- Navigation is SSRF-guarded before navigation and re-checked on final URL.

## CLI Quick Reference

```bash
openclaw browser status                              # Browser status
openclaw browser start --browser-profile openclaw    # Start managed browser
openclaw browser profiles                             # List profiles
openclaw browser open <url>                           # Open URL
openclaw browser snapshot                             # Take snapshot
openclaw browser screenshot                           # Take screenshot
openclaw browser evaluate "<js>"                      # Run JavaScript
```

## Troubleshooting

See [Browser troubleshooting](https://docs.openclaw.ai/tools/browser-linux-troubleshooting) for Linux-specific issues.
