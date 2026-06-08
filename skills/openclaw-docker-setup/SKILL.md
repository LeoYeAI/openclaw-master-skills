---
name: openclaw-docker-setup
description: Install and configure a fully operational Dockerized OpenClaw instance on macOS from scratch. Includes browser pairing, Discord channel setup, and optional Gmail/Google Drive integration. Use when user asks to "install openclaw docker", "set up dockerized openclaw", "openclaw in docker", or "isolated openclaw instance".
triggers:
  - install openclaw docker
  - set up dockerized openclaw
  - openclaw in docker
  - isolated openclaw instance
  - dockerized openclaw
  - run openclaw in docker
metadata: {"openclaw": {"os": ["darwin"]}}
---

# openclaw-docker-setup

Install a fully isolated, production-ready OpenClaw instance inside Docker on macOS.
One session, zero to running. All common pitfalls are handled inline.

**Supports multiple instances on the same machine.** Each instance gets a unique name and port.

**What you end up with:**
- A named container running and auto-restarting
- Persistent data via named Docker volumes (survives container recreation)
- Dashboard accessible at http://127.0.0.1:YOUR_PORT/
- Discord channel configured and responding
- (Optional) Gmail working via Himalaya (supports attachments); Google Drive via gog

---

## Step 0: Pick Your Instance Name and Port

Run this auto-detect script. It scans existing OpenClaw containers, finds the next free port, and suggests a name. Confirm or override.

```bash
# Auto-detect existing instances and suggest next available name+port
python3 - << 'AUTODETECT'
import subprocess, re

# Find all running openclaw containers
result = subprocess.run(
    ["docker", "ps", "-a", "--format", "{{.Names}}	{{.Ports}}"],
    capture_output=True, text=True
)

existing = {}
for line in result.stdout.strip().splitlines():
    parts = line.split('	')
    name = parts[0]
    ports = parts[1] if len(parts) > 1 else ""
    if 'openclaw' in name.lower() or '18789' in ports:
        m = re.search(r'0\.0\.0\.0:(\d+)->18789', ports)
        port = int(m.group(1)) if m else None
        existing[name] = port

# Find next free port starting from 19002
used_ports = set(p for p in existing.values() if p)
port = 19002
while port in used_ports:
    port += 1

# Suggest name
count = len(existing) + 1
names = ["openclaw-main", "openclaw-work", "openclaw-demo", "openclaw-test", "openclaw-lab"]
suggested_name = names[min(count - 1, len(names) - 1)]

print("\n=== Existing OpenClaw instances ===")
if existing:
    for n, p in existing.items():
        print(f"  {n}  →  port {p}")
else:
    print("  (none found)")

print(f"\n=== Suggested for new instance ===")
print(f"  INSTANCE={suggested_name}")
print(f"  HOST_PORT={port}")
print(f"\nTo accept, run:")
print(f"  export INSTANCE={suggested_name}")
print(f"  export HOST_PORT={port}")
print(f"\nTo override, replace the values and run the export commands with your chosen values.")
AUTODETECT
```

Review the output, then set your variables:

```bash
# Accept suggestion (paste the export lines from the output above)
export INSTANCE=openclaw-main
export HOST_PORT=19002

# Or override with your own values:
export INSTANCE=openclaw-demo
export HOST_PORT=19003
```

**All subsequent commands in this guide use `$INSTANCE` and `$HOST_PORT`.** Keep this terminal session open, or re-export the variables if you open a new one.

**Multiple instances example:**

| Instance | Host port | Purpose |
|----------|-----------|---------|
| `openclaw-main` | 19002 | Primary personal assistant |
| `openclaw-demo` | 19003 | Public demo / lecture |
| `openclaw-work` | 19004 | Work projects |

Each instance has its own volumes (`$INSTANCE-data`, `$INSTANCE-home`) — data is fully isolated.

---

## Prerequisites

- macOS (Darwin) — Intel or Apple Silicon
- Docker Desktop installed and running (or Docker Engine + CLI)
- Claude Code CLI installed on the host if using a Claude Max/Pro subscription (`claude` command available). Skip if using a raw API key.

Verify Docker is running:

```bash
docker --version
docker ps
```

Both commands must succeed before continuing.

---

## Step 1: Pull the Image

The official image is on GitHub Container Registry (GHCR), **not Docker Hub**.

```bash
docker pull ghcr.io/openclaw/openclaw:latest
```

> **Pitfall:** `openclaw/openclaw` on Docker Hub does not exist. Always use `ghcr.io/openclaw/openclaw:latest`.

**Success:** Pull completes without error and `docker images | grep openclaw` shows the image.

---

## Step 2: Generate a Claude Setup Token

**Skip this step if you have a raw Anthropic API key** — you will pass it via `-e ANTHROPIC_API_KEY=sk-ant-api03-...` in Step 3 instead.

If you have a Claude Max or Pro subscription, generate a setup token on the host:

```bash
claude setup-token
```

Copy the token (format: `sk-ant-oat01-...`). You will paste it into the container in Step 5.

> **Pitfall:** This is a **setup token**, not an API key. The two are different. A setup token lets the container authenticate using your subscription. An API key charges per token.

---

## Step 3: Launch the Container

Use the `$INSTANCE` and `$HOST_PORT` variables you set in Step 0. Do not reduce the memory — 512 MB and 1024 MB are insufficient and cause crash loops.

```bash
docker run -d \
  --name $INSTANCE \
  --restart unless-stopped \
  -p $HOST_PORT:18789 \
  -m 2048m \
  --cpus=2 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  -v ${INSTANCE}-data:/app/data \
  -v ${INSTANCE}-home:/home/node \
  -e NODE_OPTIONS="--max-old-space-size=1024" \
  ghcr.io/openclaw/openclaw:latest
```

If using a raw API key instead of a setup token, add `-e ANTHROPIC_API_KEY=sk-ant-api03-...` before the image name.

Wait 10 seconds, then verify:

```bash
docker ps --filter name=$INSTANCE
```

**Success:** Status shows `Up X seconds` and the container is not restarting.

> **Pitfall — OOM crash loop:** If the container keeps restarting, check logs:
> `docker logs --tail 20 $INSTANCE`
> If you see `JavaScript heap out of memory`, the container needs `-m 2048m` AND `-e NODE_OPTIONS="--max-old-space-size=1024"`. Recreate with the full command above.

> **Pitfall — port conflict:** If the port is in use, you chose the wrong `HOST_PORT` in Step 0. Re-run the conflict check: `lsof -i :$HOST_PORT`. Pick a free port and relaunch.

---

## Step 4: Configure the Gateway

The gateway binds to `127.0.0.1` (loopback) inside the container by default. Docker port-forwarding sends traffic to the container's network interface, not its loopback. You must switch to LAN mode.

### 4a. Set bind to LAN

```bash
docker exec $INSTANCE node /app/openclaw.mjs config set gateway.bind lan
```

### 4b. Set allowed origins

Non-loopback bind requires explicitly allowed origins or the gateway refuses to start:

```bash
docker exec $INSTANCE node /app/openclaw.mjs config set \
  gateway.controlUi.allowedOrigins '["http://127.0.0.1:$HOST_PORT"]' --json
```

### 4c. Restart to apply

```bash
docker restart $INSTANCE
```

Wait 10 seconds, then verify:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$HOST_PORT/
```

**Success:** Returns `200`.

> **Pitfall — crash after setting LAN bind:** If you set `gateway.bind lan` but forget the `allowedOrigins` step, the container crash-loops with `non-loopback Control UI requires gateway.controlUi.allowedOrigins`. Run step 4b, then restart.

---

## Step 5: Register Authentication

> **Important:** Do NOT paste your token directly in the command line — it would be stored in shell history. The command below prompts interactively.

```bash
docker exec -it $INSTANCE node /app/openclaw.mjs models auth paste-token --provider anthropic
```

When prompted, paste the setup token from Step 2 (or your API key if using one).

**Success:**
```
Updated ~/.openclaw/openclaw.json
Auth profile: anthropic:manual (anthropic/token)
```

> **Pitfall — `openclaw` command not found:** The CLI binary is NOT installed as a global command in this image. Always use `node /app/openclaw.mjs` inside the container:
> ```bash
> docker exec $INSTANCE node /app/openclaw.mjs <command>
> ```
> For interactive commands (pasting tokens, TTY prompts), add `-it`:
> ```bash
> docker exec -it $INSTANCE node /app/openclaw.mjs <command>
> ```

---

## Step 6: Verify Authentication and Gateway

```bash
# Check model auth
docker exec $INSTANCE node /app/openclaw.mjs models status
```

**Success:** Output includes `Providers w/ OAuth/tokens (1): anthropic (1)`

```bash
# Check gateway
docker exec $INSTANCE node /app/openclaw.mjs gateway status
```

**Success:** Output includes `RPC probe: ok`

---

## Step 7: Access the Dashboard and Pair Your Browser

### Get the gateway auth token

The CLI redacts secrets in output. Read the raw config file instead:

```bash
docker exec $INSTANCE cat /home/node/.openclaw/openclaw.json
```

Find `gateway.auth.token` in the output. Copy it.

### Open the dashboard

Open http://127.0.0.1:$HOST_PORT/ in your browser. Enter the gateway token to log in.

The browser will show "Pairing required." This is expected on first access.

### Approve the pairing request

```bash
docker exec $INSTANCE node /app/openclaw.mjs devices list
```

Find the pending request ID, then approve it:

```bash
docker exec $INSTANCE node /app/openclaw.mjs devices approve <REQUEST_ID>
```

Refresh the browser.

**Success:** Dashboard loads and shows the OpenClaw interface.

---

## Step 8: Configure Discord

### Create a Discord bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** — name it (e.g. "OpenClaw Isolated")
3. Go to **Bot** → set a username → click **Reset Token** → copy the token
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent** (required)
   - **Server Members Intent** (recommended)
5. Go to **OAuth2 > URL Generator**:
   - Scopes: `bot` AND `applications.commands` (both required)
   - Bot Permissions: View Channels, Send Messages, Read Message History, Embed Links, Attach Files
6. Copy the generated URL, open it in a browser, and add the bot to your server

> **Pitfall — slash commands say "not authorized":** If you invite the bot without `applications.commands`, slash commands will not work. Re-authorize using this URL (replace `BOT_CLIENT_ID`):
> ```
> https://discord.com/oauth2/authorize?client_id=BOT_CLIENT_ID&scope=bot+applications.commands&permissions=274877991936
> ```

### Collect Discord IDs

Enable **Developer Mode**: Discord → User Settings → Advanced → Developer Mode.

- Right-click your server icon → **Copy Server ID**
- Right-click your own avatar → **Copy User ID**

### Configure Discord in the container

Replace `YOUR_DISCORD_BOT_TOKEN`, `YOUR_SERVER_ID`, and user IDs with real values.

```bash
# Enable Discord
docker exec $INSTANCE node /app/openclaw.mjs config set \
  channels.discord.enabled true --json

# Set bot token
docker exec $INSTANCE node /app/openclaw.mjs config set \
  channels.discord.token '"YOUR_DISCORD_BOT_TOKEN"' --json

# Set access policy to allowlist
docker exec $INSTANCE node /app/openclaw.mjs config set \
  channels.discord.groupPolicy '"allowlist"' --json

# Configure the guild with authorized users
docker exec $INSTANCE node /app/openclaw.mjs config set \
  channels.discord.guilds \
  '{"YOUR_SERVER_ID":{"requireMention":false,"users":["USER_ID_1","USER_ID_2"]}}' \
  --json

# Restart to apply
docker restart $INSTANCE
```

### Verify Discord is connected

```bash
docker exec $INSTANCE node /app/openclaw.mjs channels status --probe
```

**Success:** Output includes `Discord default: enabled, configured, running, ... works`

Confirm users resolved:
```bash
docker logs --tail 10 $INSTANCE
```

Look for: `[discord] channel users resolved: USER_ID_1→USER_ID_1`

> **Pitfall — guilds config fails with "expected record, received array":** Always set the full `guilds` object at once. Setting individual guild keys fails:
> ```bash
> # WRONG
> docker exec $INSTANCE node /app/openclaw.mjs config set \
>   'channels.discord.guilds.SERVER_ID' '{"requireMention":false}' --json
>
> # CORRECT
> docker exec $INSTANCE node /app/openclaw.mjs config set \
>   channels.discord.guilds '{"SERVER_ID":{"requireMention":false,"users":["UID"]}}' --json
> ```

> **Pitfall — adding users later:** `config set guilds` replaces the entire object. Always include ALL existing user IDs when adding new ones.

---

## Optional: Gmail Integration

**Skip this section if you do not need Gmail.** The rest of the setup works without it.

See `references/gmail-setup.md` for the complete guide (uses Himalaya — the only reliable option for attachment download).

The key insight: OAuth browser auth does NOT work inside Docker because the callback URL points to localhost inside the container, which the host browser cannot reach. The solution is to authenticate on the host Mac first, then copy tokens into the container.

---

## Optional: Google Drive Integration

**Skip this section if you do not need Google Drive.** Google Drive uses gog (gogcli) — independent of the Gmail/Himalaya setup. You can set up Drive without setting up Gmail.

See `references/google-drive-setup.md` for the complete guide.

---

## Maintenance Reference

### Daily operations

```bash
# Stop the container
docker stop $INSTANCE

# Start the container
docker start $INSTANCE

# View logs
docker logs --tail 50 $INSTANCE

# Monitor resource usage
docker stats --no-stream $INSTANCE
```

### Update OpenClaw to a new version

```bash
docker pull ghcr.io/openclaw/openclaw:latest
docker stop $INSTANCE
docker rm $INSTANCE

# Re-run the same launch command from Step 3
# Named volumes retain all config, auth, and workspace data
docker run -d \
  --name $INSTANCE \
  --restart unless-stopped \
  -p $HOST_PORT:18789 \
  -m 2048m \
  --cpus=2 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  -v ${INSTANCE}-data:/app/data \
  -v ${INSTANCE}-home:/home/node \
  -e NODE_OPTIONS="--max-old-space-size=1024" \
  ghcr.io/openclaw/openclaw:latest
```

### Transfer files

```bash
# Host to container
docker cp /path/to/local/file.txt $INSTANCE:/home/node/.openclaw/workspace/

# Container to host
docker cp $INSTANCE:/home/node/.openclaw/workspace/file.txt ~/Desktop/

# Backup entire .openclaw directory
docker exec $INSTANCE tar -czf - -C /home/node .openclaw \
  > ~/Desktop/${INSTANCE}-backup.tar.gz

# Restore from backup
cat ~/Desktop/${INSTANCE}-backup.tar.gz | \
  docker exec -i $INSTANCE tar -xzf - -C /home/node
```

### Completely remove everything

```bash
docker rm -f $INSTANCE
docker volume rm ${INSTANCE}-data ${INSTANCE}-home
```

**Warning:** This permanently deletes all config, auth, and workspace data. Backup first.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pull access denied for openclaw/openclaw` | Wrong image registry | Use `ghcr.io/openclaw/openclaw:latest` |
| Container keeps restarting | OOM crash | Use `-m 2048m` + `-e NODE_OPTIONS="--max-old-space-size=1024"` |
| `curl 127.0.0.1:$HOST_PORT` returns 000 or connection refused | Gateway on loopback | Set `gateway.bind lan` + `allowedOrigins`, restart |
| Container crash-loops after setting LAN bind | Missing `allowedOrigins` | Set `gateway.controlUi.allowedOrigins`, restart |
| `exec: "openclaw": executable file not found` | No global CLI binary | Use `node /app/openclaw.mjs` |
| Dashboard shows "Pairing required" | Browser not approved | `devices list` then `devices approve <ID>` |
| `config get gateway.auth.token` returns `__OPENCLAW_REDACTED__` | CLI redacts secrets | `cat /home/node/.openclaw/openclaw.json` |
| Discord slash commands say "not authorized" | Missing `applications.commands` scope or user not in allowlist | Re-authorize bot; check `guilds` config |
| Data gone after container recreation | Data on ephemeral overlay | Mount `/home/node` as named volume (the launch command above already does this) |

For full pitfall details, see `references/pitfalls.md`.

---

## Container Reference

| Setting | Value |
|---------|-------|
| Container name | `$INSTANCE` |
| Image | `ghcr.io/openclaw/openclaw:latest` |
| Host port | `19002` |
| Container port | `18789` |
| Dashboard URL | http://127.0.0.1:$HOST_PORT/ |
| Memory limit | 2048 MB |
| CPU limit | 1 core |
| Node.js heap | 1024 MB |
| Restart policy | `unless-stopped` |
| CLI prefix inside container | `node /app/openclaw.mjs` |

| Volume | Mounted at | Contains |
|--------|-----------|----------|
| `${INSTANCE}-home` | `/home/node` | Config, auth, workspace |
| `${INSTANCE}-data` | `/app/data` | App-level data |

---

## Do You Need to Be at Your Mac?

**Short answer: Yes for initial setup. No for ongoing use.**

### Why initial setup requires your Mac

Three steps require direct Mac access (physical or SSH with port forwarding):

| Step | Why Mac access is needed |
|------|--------------------------|
| **Step 2: Claude setup token** | `claude setup-token` opens a browser auth flow on `localhost`. Cannot be done remotely without a browser on the Mac. Skip if using a raw API key — that can be set from anywhere. |
| **Step 4: Browser pairing** | The OpenClaw dashboard runs at `http://127.0.0.1:$HOST_PORT/` — only reachable from the Mac. You must open a browser there to pair. |
| **Optional Gmail/Drive OAuth** | Google OAuth callback points to `localhost` on the Mac. Must authenticate from a browser running on the Mac. |

### Remote setup is possible via SSH port forwarding

If you SSH into your Mac from another machine, you can forward the container port to your local browser:

```bash
# From your remote machine — forward Mac's port 19002 to your local 19002
ssh -L 19002:localhost:19002 your-mac.local

# Then open http://127.0.0.1:19002/ in your local browser
```

This lets you complete the browser pairing step remotely.

### After setup is complete

Once the container is running and paired, you do **not** need to be at your Mac. OpenClaw runs as a background service (`--restart unless-stopped`). You interact with it entirely through your configured channel (Discord, Telegram, etc.) — from your phone, any browser, anywhere.


---

## Configuration

No persistent configuration required. All settings are chosen interactively in Step 0 and set as shell variables (`$INSTANCE`, `$HOST_PORT`).

**Optional integrations require additional setup:**

| Integration | Guide | Requires |
|-------------|-------|---------|
| Gmail (email + attachments) | `references/gmail-setup.md` | Gmail App Password |
| Google Drive / Docs / Sheets / Calendar | `references/google-drive-setup.md` | Google Cloud OAuth credentials |

**System dependencies:**

| Dependency | Purpose | Check |
|------------|---------|-------|
| Docker Desktop | Container runtime | `docker --version` |
| Python 3 | Auto-detect script in Step 0 | `python3 --version` |
| Claude Code CLI (`claude`) | Generate setup token (Claude Max/Pro only) | `claude --version` |
