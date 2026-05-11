<p align="center">
  <img src="public/logo-text.png" alt="Glance" width="120" />
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://github.com/acfranzen/glance"><img src="https://img.shields.io/badge/Open%20Source-100%25-brightgreen.svg" alt="Open Source" /></a>
</p>

<p align="center">
  <strong>The Dashboard Skill for OpenClaw</strong><br/>
  Stop configuring dashboards. Just tell OpenClaw what you want to see.
</p>

---

Glance is a **free and open source** dashboard that OpenClaw builds and manages for you. Not another app to configure — a skill that gives OpenClaw a visual command center.

Tell OpenClaw _"show me my GitHub PRs"_ and watch it build the widget. Ask _"what needs my attention?"_ and OpenClaw reads your dashboard and tells you. No manual setup. No YAML files. No `.env` hell.

![Glance Dashboard](glance.png)

---

## 🤖 AI Agents: Start Here

If you're an AI agent (OpenClaw, Cursor, Claude, etc.), read these files:

| File                                         | Purpose                                                                    |
| -------------------------------------------- | -------------------------------------------------------------------------- |
| **[SKILL.md](SKILL.md)**                     | Quick reference (~200 lines) — API workflow, code patterns, essential info |
| **[docs/widget-sdk.md](docs/widget-sdk.md)** | Full documentation — components, hooks, examples, error handling           |

**TL;DR workflow:**

1. `POST /api/credentials` — Store API keys (provider, name, value)
2. `POST /api/widgets` — Create widget definition (source_code, server_code)
3. `POST /api/widgets/instances` — Add widget instance to dashboard

---

## 🚀 Quick Start with OpenClaw

### 1. Install Glance

#### Option A: One-Line Install (Recommended)

```bash
curl -fsSL https://openglance.dev/install.sh | bash
```

This will:

- Clone the repository to `~/.glance`
- Install dependencies via pnpm
- Offer to install as a background service (launchd on macOS, systemd on Linux)
- Open the dashboard in your browser

#### Option B: Docker

```bash
git clone https://github.com/acfranzen/glance.git && cd glance && docker compose up
```

#### Option C: Manual Install

```bash
git clone https://github.com/acfranzen/glance.git
cd glance
npm install
npm run dev
```

Open [http://localhost:3333](http://localhost:3333).

> **Note**: On first run, Glance auto-generates a secure encryption key. Your data is stored locally in `./data/glance.db`.

### Running as a Background Service

Keep Glance running 24/7 without keeping a terminal open.

#### macOS (launchd)

```bash
cd ~/.glance  # or your Glance directory
./scripts/install-launchd.sh
```

Benefits:

- ✅ Starts automatically on login
- ✅ Restarts on crash
- ✅ Logs to `~/Library/Logs/glance/`
- ✅ Survives terminal closes

Commands:

```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.glance.dashboard.plist

# Start service
launchctl load ~/Library/LaunchAgents/com.glance.dashboard.plist

# View logs
tail -f ~/Library/Logs/glance/glance.log

# Uninstall service
./scripts/uninstall-launchd.sh
```

#### Linux (systemd)

```bash
cd ~/.glance  # or your Glance directory
./scripts/install-systemd.sh
```

Benefits:

- ✅ Starts automatically on login
- ✅ Restarts on crash
- ✅ Integrates with journald
- ✅ Survives terminal closes

Commands:

```bash
# Stop service
systemctl --user stop glance

# Start service
systemctl --user start glance

# View logs
journalctl --user -u glance -f

# Service status
systemctl --user status glance

# Uninstall service
./scripts/uninstall-systemd.sh
```

### 2. Configure OpenClaw Integration

Add to your OpenClaw workspace (TOOLS.md or memory):

```markdown
### Glance Dashboard

- URL: http://localhost:3333
- Auth: Bearer <your-token>
- API: POST /api/widgets to create widget definitions
- API: POST /api/widgets/instances to add widgets to dashboard
- API: POST /api/credentials to store API keys
```

#### Instant Refresh Notifications (Optional)

For agent_refresh widgets, Glance can ping OpenClaw immediately when a user clicks refresh (instead of waiting for heartbeat polls).

Add to your `.env.local`:

```bash
OPENCLAW_WEBHOOK_URL=http://localhost:18789/tools/invoke
OPENCLAW_WEBHOOK_TOKEN=your-openclaw-token
```

When configured, clicking refresh on any `agent_refresh` widget will instantly wake OpenClaw to process the request. If the webhook fails, the request still queues normally for the next heartbeat.

### 3. Start Using It

```
You: "OpenClaw, add a widget showing my GitHub PRs"
OpenClaw: *creates the widget, stores your GitHub token, adds it to the dashboard*

You: "What needs my attention?"
OpenClaw: "You have 3 PRs waiting for review. One has failing CI."
```

That's it. OpenClaw handles the rest.

---

## 🧠 How It Works

### OpenClaw Builds Widgets

```
You: "Add a widget showing my Claude Max usage"
OpenClaw: *creates the widget, wires up the PTY capture, adds it to your dashboard*
```

No templates to browse. No documentation to read. Just describe what you want.

### OpenClaw Reads Your Dashboard

```
You: "What's on my dashboard?"
OpenClaw: "You have 3 open PRs that need review, your Claude usage is at 72%,
          and the weather looks good for that outdoor meeting at 2pm."
```

OpenClaw interprets your widgets and surfaces what matters. You don't even need to look at the dashboard — OpenClaw does it for you.

### OpenClaw Already Has Your Credentials

Here's the magic: **OpenClaw already knows your API keys.** Your GitHub token, Anthropic key, Vercel token — they're already in OpenClaw's memory.

When you ask for a GitHub widget, OpenClaw doesn't ask you to configure anything. It just stores your existing credentials in Glance's encrypted database and wires everything up.

No `.env` files. No copy-pasting tokens. No configuration circus. It just works.

---

## 💬 Example Conversations

```
"OpenClaw, create a weather widget for NYC"
"Show me my open PRs across all repos"
"Add a widget tracking my Anthropic API spend"
"What's the status of my dashboard?"
"Move the GitHub widget to the top right"
"Delete the clock widget, I don't need it"
"Import this widget: !GW1!eJyrVkrOz..."
```

### Sharing Widgets

Export any widget as a shareable string and import widgets others have shared:

```
You: "Export my Claude usage widget"
OpenClaw: *generates a !GW1!... package string*
         "Here's your widget package. Share this string and anyone can import it."

You: "Import this widget: !GW1!eJyrVkrOz0nVUbJS..."
OpenClaw: *validates, checks credentials, imports*
         "Done! The widget needs a GitHub token. Want me to set that up?"
```

---

## ✨ Features

- 🤖 **100% OpenClaw-Managed** — OpenClaw builds, updates, and interprets widgets
- 💬 **Natural Language Widgets** — Describe what you want, get a working widget
- 📦 **Widget Package Sharing** — Share widgets via compressed strings (WeakAuras-style)
- 🔐 **Encrypted Credential Store** — No `.env` files, no plaintext secrets
- 🏠 **Local-First** — Runs on your machine, your data stays yours
- 🎨 **Drag & Drop** — Rearrange and resize widgets freely
- 🌓 **Dark Mode** — Beautiful light and dark themes
- ⚡ **Fast** — Next.js 16 + Turbopack

### Built-in Widgets

- ⏰ **Clock** — Time and date
- 🌤️ **Weather** — Real-time conditions
- 📝 **Quick Notes** — Persistent notes
- 🔖 **Bookmarks** — Quick links

### OpenClaw-Created Widgets (Examples)

- 📊 **Claude Max Usage** — Track your API consumption
- 🔀 **GitHub PRs** — Open pull requests across repos
- 📧 **Email Summary** — Unread count and priorities
- 📅 **Calendar Glance** — Today's schedule
- _...whatever you can describe_

---

## 🔧 API Reference (For OpenClaw)

### Custom Widget Definition API

| Method   | Endpoint                     | Description                 |
| -------- | ---------------------------- | --------------------------- |
| `POST`   | `/api/widgets`               | Create widget definition    |
| `GET`    | `/api/widgets`               | List all widget definitions |
| `GET`    | `/api/widgets/:slug`         | Get widget definition       |
| `PATCH`  | `/api/widgets/:slug`         | Update widget definition    |
| `DELETE` | `/api/widgets/:slug`         | Delete widget definition    |
| `POST`   | `/api/widgets/:slug/execute` | Execute server code         |

### Credential API

| Method   | Endpoint               | Description                    |
| -------- | ---------------------- | ------------------------------ |
| `POST`   | `/api/credentials`     | Store a credential (encrypted) |
| `GET`    | `/api/credentials`     | List credentials + status      |
| `GET`    | `/api/credentials/:id` | Get credential metadata        |
| `DELETE` | `/api/credentials/:id` | Delete a credential            |

### Dashboard API

| Method   | Endpoint                     | Description                  |
| -------- | ---------------------------- | ---------------------------- |
| `GET`    | `/api/widgets/instances`     | List widgets on dashboard    |
| `POST`   | `/api/widgets/instances`     | Add widget to dashboard      |
| `PATCH`  | `/api/widgets/instances/:id` | Update widget instance       |
| `DELETE` | `/api/widgets/instances/:id` | Remove widget from dashboard |
| `GET`    | `/api/layout`                | Get layout and theme         |
| `PUT`    | `/api/layout`                | Save layout/theme            |
| `GET`    | `/api/snapshot`              | Dashboard snapshot for AI    |

### Widget Package API

| Method | Endpoint                    | Description                       |
| ------ | --------------------------- | --------------------------------- |
| `GET`  | `/api/widgets/:slug/export` | Export widget as package string   |
| `POST` | `/api/widgets/import`       | Import widget from package string |

### Widget Data API

| Method | Endpoint                     | Description                          |
| ------ | ---------------------------- | ------------------------------------ |
| `POST` | `/api/widgets/proxy`         | Proxy API calls with credentials     |
| `POST` | `/api/widgets/:slug/refresh` | Request data refresh (webhook/agent) |
| `GET`  | `/api/widgets/:slug/cache`   | Get cached widget data               |

### Widget SDK Components

OpenClaw can use these components when creating widgets:

`Card`, `Badge`, `Progress`, `Stat`, `List`, `Avatar`, `Button`, `Input`, `Switch`, `Tabs`, `Tooltip`, `Separator`

📖 **[Full Widget SDK Documentation →](docs/widget-sdk.md)**

---

## 🏠 Why Local-First?

Your dashboard shows sensitive data — API usage, emails, calendar, code activity. That data shouldn't live on someone else's server.

Glance runs entirely on your machine:

- **SQLite database** — Everything stored locally
- **No cloud sync** — Your data never leaves your device
- **No accounts** — No sign-ups, no telemetry, no tracking
- **Full control** — Export, backup, or delete anytime

---

## 🌍 Access Your Dashboard Anywhere

Glance runs locally, but you can securely access it from anywhere using a private network or tunnel.

### Option A: Tailscale (Recommended)

[Tailscale](https://tailscale.com) creates a private network between your devices — no port forwarding, no configuration.

1. **Install Tailscale** on your Glance server and your phone/laptop
2. **Start Glance** with network binding:
   ```bash
   npm run dev -- -H 0.0.0.0
   ```
3. **Access via Tailscale IP**: `http://100.x.x.x:3333`

Find your Tailscale IP with `tailscale ip -4`. Add it to your bookmarks and you're done.

> **Tip**: Tailscale is free for personal use (up to 100 devices).

### Option B: Cloudflare Tunnel

[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) exposes your dashboard via a custom domain with automatic HTTPS.

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Authenticate and create tunnel
cloudflared tunnel login
cloudflared tunnel create glance

# Run the tunnel
cloudflared tunnel route dns glance glance.yourdomain.com
cloudflared tunnel run --url http://localhost:3333 glance
```

Access at `https://glance.yourdomain.com`. Cloudflare handles SSL and DDoS protection.

### Option C: SSH Tunnel (Quick & Dirty)

If you just need temporary access from another machine:

```bash
# On your laptop/remote machine
ssh -L 3333:localhost:3333 user@your-server

# Then open http://localhost:3333 in your browser
```

### Security Notes

- **Always use AUTH_TOKEN** when exposing Glance to a network:
  ```bash
  AUTH_TOKEN=your-secret-token npm run dev -- -H 0.0.0.0
  ```
- **Never expose port 3333 directly to the internet** without authentication
- Tailscale and Cloudflare Tunnel both provide secure access without opening firewall ports

---

## 🌐 OpenClaw Community

Glance is built for the [OpenClaw](https://openclaw.ai) community. Find more skills at [clawhub.com](https://clawhub.com).

**Want to share widget ideas?** Tweet at me @AlexFranzen, Glance Discord coming soon!

---

## 🤝 Contributing

Want to improve Glance? Contributions welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

📖 **[Contributing Guide →](CONTRIBUTING.md)**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Stop configuring dashboards. Just tell OpenClaw what you want to see.</strong>
</p>
