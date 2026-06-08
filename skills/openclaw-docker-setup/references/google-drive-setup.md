# Google Drive Setup via gog (OPTIONAL)

Connect Google Drive, Docs, Sheets, and Calendar to a Dockerized OpenClaw instance using **gog** (gogcli).

---

## Why gog for Drive, Not Himalaya?

**gog is the right tool for Google Drive, Docs, Sheets, and Calendar.** It uses the Google REST API natively and supports the full breadth of Google Workspace operations.

**Himalaya handles email only** (IMAP/SMTP). It has no Google Drive support.

**Rule:** Email → Himalaya. Google Drive/Docs/Sheets/Calendar → gog. See `gmail-setup.md` for the email side.

| Task | Use |
|------|-----|
| Read/send emails | Himalaya |
| Download attachments | Himalaya |
| List/search Drive files | **gog** |
| Read/write Google Docs | **gog** |
| Google Sheets | **gog** |
| Calendar events | **gog** |

**This guide is standalone.** You do NOT need to complete gmail-setup.md first. gog uses OAuth (not IMAP), so it is a completely separate auth flow.

---

## Prerequisites

- Running `openclaw-isolated` container (see SKILL.md)
- A Google account for the bot (same account used for Gmail if you set that up, or a fresh one)

---

## Step 1: Create a Google Cloud OAuth Client

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g. "OpenClaw Bot")
3. Go to **APIs & Services > Library** and enable:
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Calendar API
4. Go to **APIs & Services > OAuth consent screen**
   - Choose **External**
   - Fill in app name and support email
   - Add the bot Google account as a **test user**
5. Go to **Credentials > Create Credentials > OAuth Client ID**
   - Application type: **Desktop app**
   - Click Create
   - **Download the JSON file** — save to `~/Downloads/`

The file will be named something like:
`client_secret_XXXX-YYYY.apps.googleusercontent.com.json`

---

## Step 2: Install gog on the Host Mac

```bash
brew install steipete/tap/gogcli
```

Verify:

```bash
gog --version
```

---

## Step 3: Authenticate on the Host Mac

**OAuth browser flow must happen on the host Mac — not inside Docker.** The browser callback URL points to localhost, which the container cannot serve.

```bash
gog auth credentials ~/Downloads/client_secret_XXXX*.json --client isolated
```

Authorize the bot account:

```bash
gog auth add <YOUR_BOT_EMAIL> --client isolated --services drive,docs,sheets,calendar --force-consent
```

Replace `<YOUR_BOT_EMAIL>` with the bot Google account email.

This opens your browser. Sign in with the bot account and grant the requested permissions. The callback completes on your Mac.

Verify:

```bash
gog auth list --client isolated
```

**Success:** The bot email appears with services: `drive,docs,sheets,calendar`

---

## Step 4: Install gog Inside the Container

### Apple Silicon (M1/M2/M3/M4):

```bash
docker exec openclaw-isolated sh -c \
  'mkdir -p /home/node/.local/bin && \
  curl -L https://github.com/steipete/gogcli/releases/latest/download/gogcli_linux_arm64.tar.gz \
  | tar -xz -C /home/node/.local/bin/'
```

### Intel Mac:

```bash
docker exec openclaw-isolated sh -c \
  'mkdir -p /home/node/.local/bin && \
  curl -L https://github.com/steipete/gogcli/releases/latest/download/gogcli_linux_amd64.tar.gz \
  | tar -xz -C /home/node/.local/bin/'
```

Verify:

```bash
docker exec openclaw-isolated /home/node/.local/bin/gog --version
```

---

## Step 5: Copy Credentials into the Container

**Do NOT use `docker cp`** — it creates files owned by host UID 501, causing permission errors with `--cap-drop=ALL`. Pipe instead:

```bash
cat "$HOME/Library/Application Support/gogcli/credentials-isolated.json" | \
  docker exec -i openclaw-isolated sh -c \
  'mkdir -p /home/node/.config/gogcli && cat > /home/node/.config/gogcli/credentials-isolated.json'
```

Verify ownership (must show `node node`):

```bash
docker exec openclaw-isolated ls -la /home/node/.config/gogcli/credentials-isolated.json
```

---

## Step 6: Export and Import Auth Token

The OAuth token is stored in macOS Keychain on the host. Export it and pipe it into the container's file-based keyring.

### Export from host:

```bash
gog auth tokens export <YOUR_BOT_EMAIL> \
  --client isolated \
  --out /tmp/gog-token-export.json \
  --overwrite
```

### Pipe into container (do NOT use docker cp):

```bash
cat /tmp/gog-token-export.json | \
  docker exec -i -e GOG_KEYRING_PASSWORD=openclaw-isolated \
  openclaw-isolated /home/node/.local/bin/gog auth tokens import /dev/stdin
```

### Clean up:

```bash
rm /tmp/gog-token-export.json
```

### Verify inside container:

```bash
docker exec -e GOG_KEYRING_PASSWORD=openclaw-isolated \
  openclaw-isolated /home/node/.local/bin/gog auth list --client isolated
```

**Success:** Bot email appears with `drive,docs,sheets,calendar` listed.

---

## Step 7: Recreate Container with Environment Variables

gog requires three environment variables at runtime. These must be set via `docker run -e`:

```bash
docker rm -f openclaw-isolated

docker run -d \
  --name openclaw-isolated \
  --restart unless-stopped \
  -p 19002:18789 \
  -m 2048m \
  --cpus=1 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  -v openclaw-isolated-data:/app/data \
  -v openclaw-isolated-home:/home/node \
  -e NODE_OPTIONS="--max-old-space-size=1024" \
  -e GOG_KEYRING_PASSWORD=openclaw-isolated \
  -e GOG_CLIENT=isolated \
  -e GOG_ACCOUNT=<YOUR_BOT_EMAIL> \
  ghcr.io/openclaw/openclaw:latest
```

Replace `<YOUR_BOT_EMAIL>` with the bot account email.

---

## Step 8: Update TOOLS.md

```bash
docker exec openclaw-isolated sh -c 'cat >> /home/node/.openclaw/workspace/TOOLS.md << '"'"'EOF'"'"'

### Google Drive / Docs / Sheets / Calendar (gog)

- Account: <YOUR_BOT_EMAIL>
- Binary: /home/node/.local/bin/gog
- Capabilities: Drive files, Docs, Sheets, Calendar (NOT email — use Himalaya for email)
- Examples:
  - List Drive files: `gog drive ls`
  - Search Drive: `gog drive search "name contains '"'"'report'"'"'"`
  - Create Doc: `gog docs create --title "My Doc"`
  - List calendar events: `gog calendar events --days 7`
  - List Sheets: `gog sheets list`
- NOTE: gog does NOT support email attachments. Use Himalaya for all email operations.
EOF'
```

Restart:

```bash
docker restart openclaw-isolated
```

---

## Step 9: Verify

```bash
# List Drive files from inside container
docker exec -e GOG_KEYRING_PASSWORD=openclaw-isolated \
  -e GOG_CLIENT=isolated \
  openclaw-isolated /home/node/.local/bin/gog drive ls
```

**Success:** List of files in the bot account's Google Drive.

Test via Discord: "List my Google Drive files"

---

## Maintenance

### Refresh expired tokens

```bash
# Re-authorize on host
gog auth add <YOUR_BOT_EMAIL> --client isolated --services drive,docs,sheets,calendar --force-consent

# Export and re-import
gog auth tokens export <YOUR_BOT_EMAIL> --client isolated --out /tmp/gog-token-export.json --overwrite
cat /tmp/gog-token-export.json | \
  docker exec -i -e GOG_KEYRING_PASSWORD=openclaw-isolated \
  openclaw-isolated /home/node/.local/bin/gog auth tokens import /dev/stdin
rm /tmp/gog-token-export.json
```

---

## What NOT to Do

### Do NOT use gog for email attachments

gog cannot download Gmail attachments. Use Himalaya for all email operations including attachment handling.

### Do NOT use `docker cp` for credentials

Always pipe credentials using `docker exec -i`. `docker cp` creates wrong file ownership that cannot be fixed with `--cap-drop=ALL` active.
