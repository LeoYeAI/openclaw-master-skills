# Installation

As of v2.0.0, the API Keys UI is built into OpenClaw as a core feature. No manual installation needed.

The tab is registered automatically via the Plugin UI architecture and appears under **Settings → API Keys** in the dashboard.

## What Changed

Previously, this skill required manually copying view/controller files and editing navigation. Now:
- Backend RPCs are in `src/gateway/server-methods/secrets.ts`
- UI files are at `ui/src/ui/controllers/apikeys.ts` and `ui/src/ui/views/apikeys.ts`
- Tab registration is in `src/gateway/server-methods/plugins-ui.ts` (builtin view)

## First-Time Vault Setup

No setup required. On first key save, the system automatically:
1. Creates `~/.openclaw/secrets.json` (mode 0600)
2. Configures the file secret provider in `openclaw.json`
3. Stores the key and creates a SecretRef

To migrate existing plaintext keys, click "🔒 Migrate to Vault" on the API Keys tab.
