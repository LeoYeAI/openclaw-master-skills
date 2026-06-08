# Pitfalls and Solutions

All known pitfalls extracted from installation logs and documentation.

---

## Pitfall 1: Wrong Docker image name

**Symptom:**
```
Error: pull access denied for openclaw/openclaw, repository does not exist
```

**Cause:** The image `openclaw/openclaw` on Docker Hub does not exist.

**Fix:** Use the official GHCR image:
```bash
docker pull ghcr.io/openclaw/openclaw:latest
```

---

## Pitfall 2: Out of memory crash loop

**Symptom:** Container keeps restarting. Logs show:
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Cause:** Insufficient memory limit. The Node.js process uses 200-300 MB at idle and can spike to 400-600 MB under load. Additionally, the default V8 heap limit inside the container is too low regardless of container memory.

**Fix:** Use at least 2048 MB AND set the Node.js heap limit explicitly:
```bash
-m 2048m -e NODE_OPTIONS="--max-old-space-size=1024"
```

512 MB and 1024 MB for the container are both insufficient.

---

## Pitfall 3: Dashboard unreachable (port mapping doesn't work)

**Symptom:** `curl http://127.0.0.1:19002/` returns connection refused or code 000.

**Cause:** The gateway binds to `127.0.0.1` (loopback) inside the container by default. Docker port-forwarding sends traffic to the container's network interface (`eth0`), not its loopback. The gateway never receives the request.

**Fix:**
```bash
docker exec openclaw-isolated node /app/openclaw.mjs config set gateway.bind lan
# Then also set allowedOrigins (see Pitfall 4) before restarting
docker restart openclaw-isolated
```

---

## Pitfall 4: Gateway crash after setting bind to LAN

**Symptom:** After setting `gateway.bind` to `lan`, the container crash-loops with:
```
Gateway failed to start: Error: non-loopback Control UI requires gateway.controlUi.allowedOrigins
```

**Cause:** Non-loopback bind mode requires an explicit allowlist of origins for the Control UI, otherwise the gateway refuses to start as a security measure.

**Fix:** Set allowed origins before restarting:
```bash
docker exec openclaw-isolated node /app/openclaw.mjs config set \
  gateway.controlUi.allowedOrigins '["http://127.0.0.1:19002"]' --json
docker restart openclaw-isolated
```

Always run steps 4a and 4b together before restarting.

---

## Pitfall 5: `openclaw` command not found inside container

**Symptom:**
```
exec: "openclaw": executable file not found in $PATH
```

**Cause:** The OpenClaw CLI is not installed as a global binary in this Docker image. There is no `openclaw` command in `$PATH`.

**Fix:** Use the full path to the Node.js entry point:
```bash
docker exec openclaw-isolated node /app/openclaw.mjs <command>
```

For interactive commands (paste-token, TTY prompts), add `-it`:
```bash
docker exec -it openclaw-isolated node /app/openclaw.mjs <command>
```

---

## Pitfall 6: Data lost after container recreation

**Symptom:** After `docker rm` and `docker run`, all config and workspace files are gone. Auth token is missing. Discord config is missing.

**Cause:** The `.openclaw` directory at `/home/node/.openclaw/` was on the container's ephemeral overlay filesystem, not a persistent named volume.

**Fix:** Mount `/home/node` as a named volume:
```bash
-v openclaw-isolated-home:/home/node
```

This ensures config, auth tokens, and workspace files survive container recreation. The launch command in SKILL.md already includes this flag.

---

## Pitfall 7: `config get gateway.auth.token` returns `__OPENCLAW_REDACTED__`

**Symptom:** Running `docker exec openclaw-isolated node /app/openclaw.mjs config get gateway.auth.token` outputs `__OPENCLAW_REDACTED__`.

**Cause:** The CLI redacts secret values in output.

**Fix:** Read the raw JSON config file instead:
```bash
docker exec openclaw-isolated cat /home/node/.openclaw/openclaw.json
```

Find `gateway.auth.token` in the JSON output.

---

## Pitfall 8: Discord slash commands say "not authorized"

**Symptom:** The bot responds to regular messages but slash commands like `/status` show "You are not authorized to use this command."

**Cause 1:** Bot was invited without the `applications.commands` OAuth2 scope.

**Fix:** Re-authorize the bot (replace `BOT_CLIENT_ID`):
```
https://discord.com/oauth2/authorize?client_id=BOT_CLIENT_ID&scope=bot+applications.commands&permissions=274877991936
```
Then: `docker restart openclaw-isolated`

**Cause 2:** The Discord user ID is not listed in the `users` array for the guild.

**Fix:** Add the user ID to the guild config:
```bash
docker exec openclaw-isolated node /app/openclaw.mjs config set \
  channels.discord.guilds \
  '{"YOUR_SERVER_ID":{"requireMention":false,"users":["USER_ID_1","USER_ID_2","NEW_USER_ID"]}}' \
  --json
docker restart openclaw-isolated
```

---

## Pitfall 9: Discord `config set guilds` fails with type error

**Symptom:** Setting individual guild keys fails:
```
expected record, received array
```

**Cause:** The `guilds` config key expects the entire object to be set at once, not individual nested keys.

**Fix:** Always set the full `guilds` object:
```bash
# WRONG
docker exec openclaw-isolated node /app/openclaw.mjs config set \
  'channels.discord.guilds.SERVER_ID' '{"requireMention":false}' --json

# CORRECT
docker exec openclaw-isolated node /app/openclaw.mjs config set \
  channels.discord.guilds '{"SERVER_ID":{"requireMention":false,"users":["UID"]}}' --json
```

Also: when adding a new user, include ALL existing users in the `users` array — the set operation replaces the entire object.

---

## Pitfall 10: Browser OAuth auth fails inside container (Google/gog)

**Symptom:** Running `gog auth add` inside the container opens a browser URL, but after authorizing, the redirect to `localhost` fails. Safari shows "can't connect to the server."

**Cause:** The OAuth callback URL points to `127.0.0.1:PORT` inside the container. The host browser cannot reach ports that are only listening inside Docker.

**Fix:** Authenticate on the host Mac, then export/import the token into the container. Never attempt OAuth browser auth inside Docker. See `references/gmail-setup.md`.

---

## Pitfall 11: `gog` auth `--remote` two-step flow fails inside Docker

**Symptom:** Running `gog auth add <YOUR_BOT_EMAIL> --remote --services all` succeeds in step 1, but step 2 fails with `manual auth state missing; run remote step 1 again`.

**Cause:** Each `docker exec` call spawns a new process. The in-memory state from the remote auth step 1 is lost by the time step 2 runs.

**Fix:** Same as Pitfall 10. Authenticate on the host Mac, then copy tokens into the container.

---

## Pitfall 12: File ownership errors after `docker cp`

**Symptom:** Permission denied errors when the container process tries to read files that were copied in with `docker cp`.

**Cause:** `docker cp` copies files with the host user's UID (typically 501 on macOS). The container runs as `node` (UID 1000). `chown` is not available because `--cap-drop=ALL` removes `CHOWN`.

**Fix:** Pipe file content instead of using `docker cp`:
```bash
# WRONG — creates file owned by UID 501
docker cp localfile.json container:/path/file.json

# CORRECT — creates file owned by the container user
cat localfile.json | docker exec -i container sh -c 'cat > /path/file.json'
```

---

## Pitfall 13: Container uses wrong AI model provider

**Symptom:** Agent fails with `No API key found for provider github-copilot` or similar.

**Cause:** The container's config (on the persistent volume) has `agents.defaults.model` set to a provider other than `anthropic`. This can happen if the container was previously configured with a different provider and the volume was reused.

**Fix:**
```bash
docker exec openclaw-isolated node /app/openclaw.mjs config set \
  agents.defaults.model '"anthropic/claude-sonnet-4-6"' --json
docker restart openclaw-isolated
```

Verify:
```bash
docker exec openclaw-isolated node /app/openclaw.mjs models status | head -4
```

Expected: `Default : anthropic/claude-sonnet-4-6`

---

## Pitfall 14: Agent says "no email integration configured" despite gog being set up

**Symptom:** Everything is installed correctly (`gog` binary, credentials, token) but the agent replies "no email integration is configured."

**Cause:** The OpenClaw agent reads `TOOLS.md` in its workspace to discover available tools. Without a Google Workspace entry in `TOOLS.md`, the agent does not know `gog` exists.

**Fix:** Add the Google Workspace section to `TOOLS.md`:
```bash
docker exec openclaw-isolated sh -c 'cat >> /home/node/.openclaw/workspace/TOOLS.md << '"'"'EOF'"'"'

### Google Workspace (gog)

- Account: <YOUR_BOT_EMAIL>
- Services: Gmail, Drive, Docs, Sheets, Calendar, Contacts, Tasks
- Use the `gog` CLI for all Google operations
EOF'
docker restart openclaw-isolated
```
