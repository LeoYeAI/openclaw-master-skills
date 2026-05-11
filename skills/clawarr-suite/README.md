# 🎬 ClawARR Suite

**Unified deep-integration control for self-hosted media automation stacks.**

ClawARR Suite is an [OpenClaw](https://openclaw.ai) agent skill that gives your AI assistant full operational control over your entire \*arr media stack — from library analytics to download management to Plex collection automation.

> **24 scripts · 8,500+ lines · 180+ subcommands · 8 reference docs**

---

## ✨ What Can It Do?

| Category | Capabilities |
|----------|-------------|
| 📊 **Library Analytics** | Stats, quality profiles, missing content, disk usage, genre/year distributions |
| 👀 **Viewing Analytics** | Current streams, watch history, most watched, peak hours, user stats |
| 🎬 **Content Management** | Add/remove movies & series, calendars, wanted lists, history |
| 📝 **Request Handling** | Overseerr approval workflows, stats, bulk actions |
| 💬 **Subtitles** | Bazarr wanted/search/history/languages |
| 🔍 **Indexer Management** | Prowlarr indexer control, testing, cross-app sync |
| ⬇️ **Downloads** | SABnzbd active/speed/queue/pause/resume |
| 🎯 **Quality Profiles** | Recyclarr TRaSH Guides sync, diff preview |
| 🧹 **Library Cleanup** | Maintainerr rules, collections, exclusions |
| 🔔 **Notifications** | Notifiarr status, triggers, service health |
| 🖼️ **Collections & Overlays** | Kometa/PMM automation for Plex |
| 📦 **Archive Extraction** | Unpackerr monitoring and error tracking |
| 📡 **Media Tracking** | Trakt.tv, Letterboxd, Simkl — sync, export, discovery |
| 📈 **Dashboards** | Self-contained HTML dashboard generation |
| 🔧 **Setup & Diagnostics** | Auto-discovery, guided setup, troubleshooting |

---

## 📦 Install

### From ClawHub (recommended)

```bash
clawhub install clawarr-suite
```

> ⚠️ **Note:** This skill is currently [flagged for review](https://github.com/openclaw/clawhub/issues/256) by ClawHub's automated security scanner. The flag is a false positive — the scanner detected standard patterns (bash `eval` for env vars, WebRTC for LAN discovery, Docker commands, API key handling) that are inherent to media server management. We've submitted a review request and are waiting for the flag to be lifted.
>
> **[View on ClawHub](https://clawhub.ai/skills/clawarr-suite)** · **[Review request →](https://github.com/openclaw/clawhub/issues/256)**

### From GitHub

```bash
git clone https://github.com/omiron33/clawarr-suite.git ~/.openclaw/skills/clawarr-suite
```

### Manual

Copy the `clawarr-suite` folder into your OpenClaw skills directory:

```
~/.openclaw/skills/clawarr-suite/
├── SKILL.md          # Agent documentation (OpenClaw reads this)
├── scripts/          # 24 bash scripts
└── references/       # 8 reference docs
```

### 2. Run setup

Tell your agent:
> "Set up ClawARR for my media server at 192.168.1.100"

Or run manually:
```bash
scripts/setup.sh 192.168.1.100
```

This auto-discovers services, extracts API keys, verifies connections, and outputs your config.

### 3. Start using it

Just talk to your agent naturally:

- *"Show me what's downloading right now"*
- *"What movies were added this week?"*
- *"Generate a dashboard of my media library"*
- *"Sync my Plex watch history to Trakt"*
- *"What are the most watched shows this month?"*
- *"Run Kometa to update my Plex collections"*
- *"Show cleanup rules and what's flagged for deletion"*

---

## 🛠️ Supported Services

### Core Stack
| Service | Port | Script |
|---------|------|--------|
| **Sonarr** | 8989 | `library.sh`, `manage.sh`, `search.sh` |
| **Radarr** | 7878 | `library.sh`, `manage.sh`, `search.sh` |
| **Lidarr** | 8686 | `library.sh` |
| **Readarr** | 8787 | `library.sh` |
| **Prowlarr** | 9696 | `prowlarr.sh` |
| **Bazarr** | 6767 | `subtitles.sh` |
| **Overseerr** | 5055 | `requests.sh` |
| **Plex** | 32400 | `analytics.sh` |
| **Tautulli** | 8181 | `analytics.sh` |
| **SABnzbd** | 38080 | `downloads.sh` |

### Companion Services
| Service | Port | Script | Purpose |
|---------|------|--------|---------|
| **Recyclarr** | — | `recyclarr.sh` | TRaSH Guides quality profile sync |
| **Unpackerr** | — | `unpackerr.sh` | Auto-extract archives from downloads |
| **Notifiarr** | 5454 | `notifiarr.sh` | Unified notification routing |
| **Maintainerr** | 6246 | `maintainerr.sh` | Automated library cleanup |
| **Kometa** | — | `kometa.sh` | Plex collections & overlays |
| **FlareSolverr** | 8191 | — | Cloudflare bypass for indexers |

### Media Trackers
| Service | Script | Features |
|---------|--------|----------|
| **Trakt.tv** | `trakt.sh` | Auth, history, ratings, watchlists, scrobbling, discovery, sync |
| **Letterboxd** | `letterboxd.sh` | CSV export/import, profile stats |
| **Simkl** | `simkl.sh` | Auth, sync, watchlist, stats |
| **Traktarr** | `trakt.sh` | Auto-add from Trakt lists → Radarr/Sonarr |
| **Retraktarr** | `trakt.sh` | Sync library → Trakt lists |

---

## ⚙️ Configuration

Set environment variables or use `setup.sh` to generate them:

```bash
# Required — your server's IP or hostname
export CLAWARR_HOST=192.168.1.100

# Core services (setup.sh auto-discovers these)
export SONARR_KEY=your_api_key
export RADARR_KEY=your_api_key
export PLEX_TOKEN=your_plex_token
export TAUTULLI_KEY=your_api_key
export SABNZBD_KEY=your_api_key

# Optional services
export PROWLARR_KEY=your_api_key
export BAZARR_KEY=your_api_key
export OVERSEERR_KEY=your_api_key
export NOTIFIARR_KEY=your_api_key

# Docker-based companions (SSH access to your server)
export RECYCLARR_SSH=mynas
export KOMETA_SSH=mynas
export UNPACKERR_SSH=mynas
export DOCKER_CONFIG_BASE=/opt/docker   # Default: /volume1/docker (Synology)

# Media trackers (register your own apps)
# Trakt: https://trakt.tv/oauth/applications/new
export TRAKT_CLIENT_ID=your_client_id
export TRAKT_CLIENT_SECRET=your_client_secret

# Simkl: https://simkl.com/settings/developer
export SIMKL_CLIENT_ID=your_client_id
export SIMKL_CLIENT_SECRET=your_client_secret
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[SKILL.md](SKILL.md)** | Full agent documentation — every command, workflow, and example. **This is what OpenClaw reads.** |
| `references/api-endpoints.md` | Complete API reference for all services |
| `references/setup-guide.md` | Platform-specific installation (Docker, Synology, Unraid, Linux) |
| `references/common-issues.md` | Troubleshooting guide with solutions |
| `references/companion-services.md` | Prowlarr, Recyclarr, FlareSolverr, Unpackerr, Notifiarr, Maintainerr, Kometa |
| `references/tracker-apis.md` | Media tracker API documentation |
| `references/traktarr-retraktarr.md` | Traktarr & Retraktarr automation guide |
| `references/prompts.md` | 50+ example natural-language prompts |
| `references/dashboard-templates.md` | HTML/CSS templates for dashboards |

> **For AI agents:** Read `SKILL.md` — it contains complete command references, environment variable documentation, workflows, and example prompts optimized for agent consumption.

---

## 📋 Requirements

- **bash** 3.2+ (macOS default is fine)
- **curl**, **jq**, **bc**, **sed** — standard on macOS and Linux
- SSH access for Docker-based companion services
- No Node.js, Python, or other runtimes required

---

## 🏗️ Supported Platforms

- **Docker** — any host
- **Synology NAS** — DSM 7+
- **Unraid** — Community Applications
- **Linux** — bare metal or VM
- **macOS** — client-side scripts (server runs elsewhere)

---

## 🗺️ Roadmap

- [ ] Torrent client support (qBittorrent, Transmission, Deluge)
- [ ] Jellyfin / Emby analytics
- [ ] Backup & restore workflows
- [ ] Native OpenClaw plugin (TypeScript, in progress)

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built for <a href="https://openclaw.ai">OpenClaw</a> · <a href="https://discord.com/invite/clawd">Community</a> · <a href="https://clawhub.com">More Skills</a>
</p>
