---
name: clawarr-suite
description: >
  Comprehensive management for self-hosted media stacks (Sonarr, Radarr, Lidarr, Readarr,
  Prowlarr, Bazarr, Overseerr, Plex, Tautulli, SABnzbd, Recyclarr, Unpackerr, Notifiarr,
  Maintainerr, Kometa, FlareSolverr). Deep library exploration, analytics, dashboard generation,
  content management, request handling, subtitle management, indexer control, download monitoring,
  quality profile sync, library cleanup automation, notification routing, collection/overlay
  management, and media tracker integration (Trakt, Letterboxd, Simkl).
homepage: https://github.com/omiron33/clawarr-suite
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["bash", "curl", "jq", "bc", "sed"] },
        "security":
          {
            "networkScope": "local-lan-and-user-configured-hosts",
            "secretsPolicy": "api keys loaded from env/user config only; never hardcoded",
            "destructiveActions": "none by default; explicit command required for delete/remove actions"
          },
        "capabilities":
          [
            "arr-api-management",
            "docker-service-observability",
            "dashboard-generation",
            "media-tracker-sync"
          ]
      }
  }
---

# ClawARR Suite

Unified deep-integration control for self-hosted media automation stacks. This skill provides comprehensive agent-executable operations across the entire *arr ecosystem with rich analytics, dashboard generation, and advanced library exploration.

## Security & Scanner Clarity

- Local-first operations: all API calls target user-provided local hosts (typically LAN/NAS).
- No embedded secrets: API keys/tokens are sourced from environment variables or user-owned config files.
- No telemetry/exfiltration paths: scripts do not transmit credentials or library data to third-party endpoints.
- Destructive behavior is opt-in: delete/remove actions require explicit command invocation by the user/agent.
- Setup logic avoids dynamic `eval` and uses explicit variable mapping for scanner-friendly shell behavior.

## Quick Start

**First time setup (recommended):**
```bash
scripts/setup.sh <host-ip-or-hostname>
```
Discovers services, grabs API keys, verifies connections, and outputs your config.

**Common operations:**
```bash
scripts/status.sh              # Health check all services
scripts/library.sh stats all   # Library statistics
scripts/analytics.sh activity  # Current Plex streams
scripts/dashboard.sh           # Generate HTML dashboard
scripts/manage.sh wanted all   # Show missing content
scripts/requests.sh list       # Overseerr requests
```

## Scripts Overview

### Core Operations
- **`setup.sh`** — Guided setup wizard with auto-discovery
- **`discover.sh`** — Scan host for *arr services
- **`status.sh`** — Health check all configured services
- **`diagnose.sh`** — Automated troubleshooting

### Library Exploration (`library.sh`)
Deep statistics and exploration for Radarr/Sonarr/Lidarr:
```bash
library.sh stats [app]          # Overall library stats
library.sh quality [app]        # Quality profile breakdown
library.sh missing [app]        # Missing/wanted content
library.sh unmonitored [app]    # Unmonitored items
library.sh recent [app] [days]  # Recently added (default: 7)
library.sh genres [app]         # Genre distribution
library.sh years [app]          # Year distribution
library.sh studios [app]        # Studio/network breakdown
library.sh nofiles [app]        # Monitored but no files
library.sh disk [app]           # Disk usage by root folder
```

### Analytics (`analytics.sh`)
Rich viewing analytics from Tautulli/Plex:
```bash
analytics.sh activity                 # Currently watching
analytics.sh history [count]          # Watch history
analytics.sh most-watched [period]    # Most watched (week/month/year)
analytics.sh popular-genres [period]  # Popular genres
analytics.sh peak-hours               # Peak watching hours
analytics.sh user-stats [user]        # User activity
analytics.sh library-stats            # Plex library stats
analytics.sh recent-added [count]     # Recently added to Plex
analytics.sh play-totals              # Total play statistics
```

### Content Management (`manage.sh`)
Add, remove, and manage content:
```bash
manage.sh add-movie "<title>" [quality] [root]
manage.sh add-series "<title>" [quality] [root]
manage.sh remove <app> <id>
manage.sh wanted [app]
manage.sh calendar [app] [days]
manage.sh history [app] [count]
manage.sh rename <app> <id>
manage.sh refresh <app> [id]
```

### Request Management (`requests.sh`)
Overseerr request handling:
```bash
requests.sh list [pending|approved|available|all]
requests.sh approve <id>
requests.sh deny <id> [reason]
requests.sh info <id>
requests.sh stats
```

### Subtitle Management (`subtitles.sh`)
Bazarr operations:
```bash
subtitles.sh wanted
subtitles.sh history [count]
subtitles.sh search <series|movie> <id>
subtitles.sh languages
```

### Indexer Management (`indexers.sh`)
Prowlarr operations:
```bash
indexers.sh list
indexers.sh test [id]
indexers.sh stats
```

### Download Client (`downloads.sh`)
SABnzbd operations:
```bash
downloads.sh active
downloads.sh speed
downloads.sh history [count]
downloads.sh pause
downloads.sh resume
downloads.sh queue
```

### Dashboard Generation (`dashboard.sh`)
Generate self-contained HTML dashboard:
```bash
dashboard.sh [output_file]
```
Creates beautiful dark-themed dashboard with:
- System health
- Download activity
- Library statistics
- Recent activity
- Viewing analytics
- Disk usage

Output defaults to `clawarr-dashboard.html` (open in any browser).

### Media Tracker Integration (`trakt.sh`, `trackers.sh`, `letterboxd.sh`, `simkl.sh`)

Track and sync what you watch across services like Trakt.tv, Letterboxd, Simkl, and more.

**Unified Interface (`trackers.sh`):**
```bash
trackers.sh setup              # Interactive setup wizard
trackers.sh status             # Show configured trackers
trackers.sh sync plex trakt    # Sync Plex → Trakt
trackers.sh export trakt json  # Export watch history
trackers.sh import letterboxd file.csv
trackers.sh compare trakt simkl
```

**Trakt.tv Integration (`trakt.sh`):**

*Authentication:*
```bash
trakt.sh auth                  # Device code OAuth flow
trakt.sh auth-status           # Check authentication
```

*Profile & Stats:*
```bash
trakt.sh profile [username]    # Show profile
trakt.sh stats [username]      # Detailed statistics
```

*Watching & History:*
```bash
trakt.sh watching              # Currently watching
trakt.sh history [movies|shows|episodes] [limit]
trakt.sh sync-history export file.json
trakt.sh sync-history import file.json
```

*Scrobbling:*
```bash
trakt.sh scrobble start movie 12345
trakt.sh scrobble stop movie 12345 100
trakt.sh checkin movie "Inception"
```

*Lists & Collections:*
```bash
trakt.sh watchlist [movies|shows]
trakt.sh watchlist-add movie "Dune Part Two"
trakt.sh collection movies
trakt.sh collection-add movie 12345
trakt.sh lists                 # Custom lists
trakt.sh list-items my-favorites
```

*Ratings:*
```bash
trakt.sh ratings movies 8      # Movies rated 8+
trakt.sh rate movie "Inception" 10
```

*Discovery:*
```bash
trakt.sh recommendations movies
trakt.sh trending shows
trakt.sh popular movies
trakt.sh calendar all 7        # Next 7 days
```

*Search:*
```bash
trakt.sh search "Breaking Bad" show
```

*Sync:*
```bash
trakt.sh sync-plex             # Sync Plex watch history to Trakt
```

**Letterboxd Integration (`letterboxd.sh`):**
```bash
letterboxd.sh export           # Export from Plex as Letterboxd CSV
letterboxd.sh import diary.csv # Import Letterboxd diary
letterboxd.sh profile username # View public profile
letterboxd.sh diary username 2024
```

**Simkl Integration (`simkl.sh`):**
```bash
simkl.sh auth                  # OAuth authentication
simkl.sh profile               # Show profile
simkl.sh stats                 # Viewing statistics
simkl.sh history movies        # Watch history
simkl.sh watchlist all         # View watchlist
simkl.sh sync                  # Sync with Plex
```

### Traktarr & Retraktarr Integration

Automate content discovery and library syncing with Trakt lists.

**Traktarr (Trakt → Radarr/Sonarr):**
```bash
# Status and configuration
trakt.sh traktarr-status       # Check if installed
trakt.sh traktarr-config       # Configure Traktarr

# Add content from Trakt lists
trakt.sh traktarr-add movies trending 10
trakt.sh traktarr-add movies anticipated 15
trakt.sh traktarr-add movies popular 5
trakt.sh traktarr-add shows trending 5
trakt.sh traktarr-add movies watchlist 50
```

**Retraktarr (Radarr/Sonarr → Trakt):**
```bash
# Status and configuration
trakt.sh retraktarr-status     # Check if installed
trakt.sh retraktarr-config     # Configure Retraktarr

# Sync library to Trakt lists
trakt.sh retraktarr-sync all   # Sync movies and shows
trakt.sh retraktarr-sync movies
trakt.sh retraktarr-sync shows
```

**Installation via Setup Wizard:**
```bash
trackers.sh setup
# Choose option 5 for Traktarr
# Choose option 6 for Retraktarr
# Offers to install via pip if not found
```

**What They Do:**
- **Traktarr:** Automatically adds content from Trakt lists (trending, anticipated, watchlist, custom) to Radarr/Sonarr for download
- **Retraktarr:** Syncs your Radarr/Sonarr library back to Trakt as public/private lists

See `references/traktarr-retraktarr.md` for complete setup, cron scheduling, and usage patterns.

### Prowlarr Indexer Management (`prowlarr.sh`)
Centralized indexer management across all *arr apps:
```bash
prowlarr.sh indexers              # List all indexers
prowlarr.sh test [id]             # Test indexer(s)
prowlarr.sh stats                 # Indexer & app sync statistics
prowlarr.sh search <query> [type] # Search across all indexers (type: movie|tv|audio|book)
prowlarr.sh apps                  # List sync targets (Sonarr/Radarr/etc)
prowlarr.sh add-app <type> <url> <key>  # Add app sync target
prowlarr.sh sync                  # Trigger sync to all apps
prowlarr.sh status                # Health check
prowlarr.sh logs [count]          # Recent logs
```

### Recyclarr Quality Profiles (`recyclarr.sh`)
Sync TRaSH Guides quality profiles to Sonarr/Radarr:
```bash
recyclarr.sh status               # Check status & config
recyclarr.sh sync [instance]      # Sync profiles (all or specific)
recyclarr.sh diff [instance]      # Preview changes without applying
recyclarr.sh profiles             # List available TRaSH profiles
recyclarr.sh qualities [app]      # List quality definitions
recyclarr.sh config               # Show current config
recyclarr.sh create-config        # Generate config template
recyclarr.sh logs [count]         # View recent logs
```

### Maintainerr Library Cleanup (`maintainerr.sh`)
Automated library cleanup based on rules:
```bash
maintainerr.sh status             # Check status
maintainerr.sh rules              # List cleanup rules
maintainerr.sh collections        # List managed collections
maintainerr.sh run [rule_id]      # Trigger rules (all or specific)
maintainerr.sh media <rule_id>    # Show media matched by a rule
maintainerr.sh exclude <media_id> <rule_id>  # Exclude media from rule
maintainerr.sh logs               # View activity log
```

### Notifiarr Notifications (`notifiarr.sh`)
Unified notification management across *arr services:
```bash
notifiarr.sh status               # Check status & integrations
notifiarr.sh triggers             # List notification triggers
notifiarr.sh services             # Show connected services
notifiarr.sh test [channel]       # Send test notification
notifiarr.sh config               # Configuration summary
notifiarr.sh logs                 # Recent notification log
```

### Kometa Collection Manager (`kometa.sh`)
Plex collection, overlay, and metadata automation:
```bash
kometa.sh status                  # Check container status
kometa.sh run [library]           # Run Kometa (all or specific library)
kometa.sh collections             # Show Plex collections
kometa.sh overlays                # Check overlay config
kometa.sh config                  # Show Kometa config
kometa.sh templates               # List available default collections/overlays
kometa.sh logs [count]            # View recent logs
```

### Unpackerr Archive Extraction (`unpackerr.sh`)
Automatic archive extraction for download clients:
```bash
unpackerr.sh status               # Check status & config
unpackerr.sh activity             # Recent extraction activity
unpackerr.sh errors               # Recent errors/warnings
unpackerr.sh config               # Show configuration
unpackerr.sh logs [count]         # View recent logs
unpackerr.sh restart              # Restart container
```

### Legacy Scripts
- **`queue.sh`** — View download queues (use `manage.sh wanted` or `downloads.sh active` for more detail)
- **`search.sh`** — Search content (use `manage.sh add-*` for full workflow)

## Configuration

### Environment Variables

**Core Services:**
```bash
export CLAWARR_HOST=192.168.1.100
export SONARR_KEY=abc123...
export RADARR_KEY=def456...
export LIDARR_KEY=ghi789...
export READARR_KEY=jkl012...
export PROWLARR_KEY=mno345...
export BAZARR_KEY=pqr678...
export OVERSEERR_KEY=stu901...
export PLEX_TOKEN=vwx234...
export TAUTULLI_KEY=yz567...
export SABNZBD_KEY=abc890...
export NOTIFIARR_KEY=xyz123...

# Companion services (auto-detected, keys optional)
export PROWLARR_KEY=abc123...   # Required for prowlarr.sh

# Docker-based services (SSH access for remote management)
export RECYCLARR_SSH=mynas       # SSH host for recyclarr container
export KOMETA_SSH=mynas          # SSH host for kometa container
export UNPACKERR_SSH=mynas       # SSH host for unpackerr container
export DOCKER_CONFIG_BASE=/opt/docker  # Docker config root (default: /volume1/docker for Synology)
```

**Media Trackers (optional):**
```bash
# Trakt.tv (register app at https://trakt.tv/oauth/applications/new)
export TRAKT_CLIENT_ID=your_client_id
export TRAKT_CLIENT_SECRET=your_client_secret

# Simkl (register at https://simkl.com/settings/developer)
export SIMKL_CLIENT_ID=your_client_id
export SIMKL_CLIENT_SECRET=your_client_secret

# Letterboxd (requires API approval)
export LETTERBOXD_API_KEY=your_api_key  # Optional, uses CSV export if not set
```

**Token Storage:**
- Tokens are automatically saved to `~/.config/clawarr/`
- Files: `trakt_tokens.json`, `simkl_tokens.json`
- Permissions: 600 (user read/write only)

Store in `.env` file and source before running scripts.

### Standard Ports
- Sonarr: 8989
- Radarr: 7878
- Lidarr: 8686
- Readarr: 8787
- Prowlarr: 9696
- Bazarr: 6767
- Overseerr: 5055
- Plex: 32400
- Tautulli: 8181
- SABnzbd: 38080
- Notifiarr: 5454
- Maintainerr: 6246
- FlareSolverr: 8191
- Homarr: 7575

## API Key Discovery

### Method 1: /initialize.json (Easiest)
Most *arr apps expose API key at public endpoint:
```bash
curl -s http://HOST:7878/initialize.json | jq -r '.apiKey'
```

For older versions (v3):
```bash
curl -s http://HOST:7878/initialize.js | grep -o "apiKey: '[^']*'" | cut -d"'" -f2
```

### Method 2: Config Files
**Docker/Unraid/Synology:** `/config/config.xml` (inside container)
```bash
grep '<ApiKey>' /path/to/config.xml | sed 's/.*<ApiKey>\(.*\)<\/ApiKey>.*/\1/'
```

### Method 3: Web UI
Settings → General → Security → API Key

### Plex Token
From Plex Web UI:
1. Open any media item
2. "Get Info" → "View XML"
3. URL contains `X-Plex-Token=...`

Or use:
```bash
curl -u "username:password" -X POST \
  'https://plex.tv/users/sign_in.json' \
  -H "X-Plex-Client-Identifier: <unique-id>"
```

### Tautulli API Key
Settings → Web Interface → API → API Key

### SABnzbd API Key
Config → General → Security → API Key

## Common Workflows

### Library Analysis
```bash
# Get complete library overview
scripts/library.sh stats all

# Find quality upgrade candidates
scripts/library.sh quality radarr

# Show missing content
scripts/library.sh missing all

# Check disk usage
scripts/library.sh disk all
```

### Viewing Analytics
```bash
# Current activity
scripts/analytics.sh activity

# Most watched this month
scripts/analytics.sh most-watched month

# User statistics
scripts/analytics.sh user-stats

# Peak hours
scripts/analytics.sh peak-hours
```

### Request Management
```bash
# Show pending requests
scripts/requests.sh list pending

# Approve request
scripts/requests.sh approve 123

# Request statistics
scripts/requests.sh stats
```

### Content Management
```bash
# Add movie
scripts/manage.sh add-movie "Dune Part Two"

# Show calendar
scripts/manage.sh calendar all 7

# View history
scripts/manage.sh history radarr 30

# Show wanted/missing
scripts/manage.sh wanted all
```

### Indexer Management (Prowlarr)
```bash
# List and test all indexers
scripts/prowlarr.sh indexers
scripts/prowlarr.sh test

# Search across all indexers
scripts/prowlarr.sh search "Dune" movie

# Add Sonarr/Radarr as sync targets
scripts/prowlarr.sh add-app sonarr http://host:8989 <sonarr_key>
scripts/prowlarr.sh add-app radarr http://host:7878 <radarr_key>

# Trigger indexer sync to all apps
scripts/prowlarr.sh sync
```

### Quality Profiles (Recyclarr)
```bash
# Preview changes
scripts/recyclarr.sh diff

# Sync TRaSH Guides profiles
scripts/recyclarr.sh sync

# Check status
scripts/recyclarr.sh status
```

### Library Cleanup (Maintainerr)
```bash
# View rules and matched media
scripts/maintainerr.sh rules
scripts/maintainerr.sh media 1

# Run cleanup
scripts/maintainerr.sh run

# Exclude something from cleanup
scripts/maintainerr.sh exclude 12345 1
```

### Collections & Overlays (Kometa)
```bash
# Run collection/overlay generation
scripts/kometa.sh run

# View existing collections
scripts/kometa.sh collections

# See available templates
scripts/kometa.sh templates
```

### Dashboard
```bash
# Generate dashboard
scripts/dashboard.sh my-dashboard.html

# Open in browser
open my-dashboard.html
```

### Media Tracking Workflows

**Initial Setup:**
```bash
# Set up Trakt.tv
scripts/trackers.sh setup
# Select option 1 (Trakt.tv)
# Follow device auth flow

# Check status
scripts/trackers.sh status
```

**Sync Plex to Trakt:**
```bash
# One-time sync of watch history
scripts/trakt.sh sync-plex

# Or use unified interface
scripts/trackers.sh sync plex trakt
```

**Export for Letterboxd:**
```bash
# Generate Letterboxd-compatible CSV
scripts/letterboxd.sh export

# Upload at letterboxd.com/import/
```

**Cross-Tracker Sync:**
```bash
# Export from Trakt, convert for Letterboxd
scripts/trackers.sh sync trakt letterboxd

# Compare two services
scripts/trackers.sh compare trakt simkl
```

**Discovery & Recommendations:**
```bash
# Get personalized recommendations
scripts/trakt.sh recommendations movies

# See what's trending
scripts/trakt.sh trending shows

# Check upcoming releases
scripts/trakt.sh calendar all 7
```

**Track Viewing:**
```bash
# See what you're currently watching
scripts/trakt.sh watching

# View watch history
scripts/trakt.sh history movies 50

# Rate something you watched
scripts/trakt.sh rate movie "Inception" 10
```

**Automation with Traktarr/Retraktarr:**
```bash
# Set up Traktarr (Trakt → Arr)
scripts/trackers.sh setup  # Option 5

# Add trending movies to Radarr
scripts/trakt.sh traktarr-add movies trending 10

# Add anticipated shows to Sonarr
scripts/trakt.sh traktarr-add shows anticipated 5

# Set up Retraktarr (Arr → Trakt)
scripts/trackers.sh setup  # Option 6

# Sync library to Trakt lists
scripts/trakt.sh retraktarr-sync all

# Schedule automation (cron):
# Traktarr every 6 hours: 0 */6 * * * traktarr run
# Retraktarr daily at 3am: 0 3 * * * retraktarr sync
```

## Troubleshooting

### No Files Eligible for Import

**Diagnosis:**
```bash
scripts/diagnose.sh
```

Common causes:
1. **Stale Docker mounts** — Container restarted but host didn't
2. **Path mapping** — Download client and *arr app see different paths
3. **Permissions** — *arr app can't read download directory
4. **Category mismatch** — Download in wrong category

**Solutions:**
```bash
# Restart containers (fixes stale mounts)
docker restart radarr sonarr

# Check path mappings
# Settings → Download Clients → Remote Path Mappings
```

### Queue Stuck

**Check download client:**
```bash
scripts/downloads.sh active
scripts/downloads.sh speed
```

**Check *arr queues:**
```bash
scripts/manage.sh wanted all
```

**Check indexers:**
```bash
scripts/indexers.sh test
scripts/indexers.sh stats
```

### Missing Subtitles

```bash
scripts/subtitles.sh wanted
scripts/subtitles.sh search series <id>
```

## Reference Documentation

- **`references/api-endpoints.md`** — Complete API reference for all services
- **`references/tracker-apis.md`** — Media tracker API documentation (Trakt, Simkl, Letterboxd)
- **`references/traktarr-retraktarr.md`** — Complete guide to Traktarr & Retraktarr automation
- **`references/companion-services.md`** — Prowlarr, Recyclarr, FlareSolverr, Unpackerr, Notifiarr, Maintainerr, Kometa reference
- **`references/common-issues.md`** — Troubleshooting guide with solutions
- **`references/setup-guide.md`** — Platform-specific installation
- **`references/prompts.md`** — Suggested natural-language prompts for agents
- **`references/dashboard-templates.md`** — HTML/CSS templates for dashboards

## Example Agent Prompts

See `references/prompts.md` for complete list. Examples:

**Library & Downloads:**
- "Show me what's downloading right now"
- "What movies were added this week?"
- "Generate a dashboard of my media library"
- "What are the most watched shows this month?"
- "Find all 720p movies that could be upgraded to 4K"
- "Show missing episodes for all monitored shows"
- "What's coming out this week?"
- "Approve all pending Overseerr requests"
- "How much disk space am I using per library?"
- "Show my Plex viewing stats for the last 30 days"
- "What subtitles are missing?"
- "Test all my indexers"

**Media Tracking:**
- "Set up Trakt tracking for my Plex library"
- "Sync my Plex watch history to Trakt"
- "What am I currently watching on Trakt?"
- "Show my Trakt watch history from this month"
- "Get movie recommendations based on my Trakt ratings"
- "What's trending on Trakt right now?"
- "Export my library for Letterboxd"
- "Compare my Trakt and Simkl watch histories"
- "Show me upcoming movie releases I'm tracking"
- "Rate Inception 10/10 on Trakt"
- "Add Dune Part Two to my Trakt watchlist"
- "Show my Letterboxd profile stats"
- "What are my top-rated movies on Trakt?"

**Prowlarr & Indexers:**
- "Show all my indexers and test them"
- "Search across all indexers for Breaking Bad"
- "Sync Prowlarr indexers to Sonarr and Radarr"
- "Add Sonarr as a sync target in Prowlarr"

**Quality Profiles (Recyclarr):**
- "Sync TRaSH Guides quality profiles"
- "Preview what Recyclarr would change"
- "Show available quality profiles for Radarr"
- "What quality definitions does Sonarr have?"

**Library Cleanup (Maintainerr):**
- "Show my library cleanup rules"
- "What movies are flagged for deletion?"
- "Run all cleanup rules now"
- "Exclude this movie from the cleanup rule"

**Collections & Overlays (Kometa):**
- "Run Kometa to update collections"
- "Show all my Plex collections"
- "What overlay templates are available?"
- "Add IMDb Top 250 collection to my movie library"

**Notifications (Notifiarr):**
- "Check Notifiarr status and integrations"
- "Send a test notification"
- "Show recent notifications"

**Archive Extraction (Unpackerr):**
- "Check Unpackerr status"
- "Show recent extraction activity"
- "Any extraction errors?"

**Traktarr/Retraktarr Automation:**
- "Set up Traktarr to auto-add trending movies"
- "Add the top 10 anticipated movies from Trakt to Radarr"
- "Configure Traktarr to monitor my Trakt watchlist"
- "Sync my Radarr library to a public Trakt list"
- "Show Traktarr status and configuration"
- "Add trending shows to Sonarr via Traktarr"
- "Set up automatic syncing between Trakt and my *arr apps"
- "What's Retraktarr doing? Is it synced?"

## Technical Notes

### Bash 3.2 Compatibility
All scripts are compatible with macOS bash 3.2:
- No associative arrays (`declare -A`)
- No uppercase parameter expansion (`${var^^}`)
- Use `$(echo "$var" | tr '[:lower:]' '[:upper:]')` for case conversion
- No `|&` (pipe stderr), use `2>&1` instead

### Dependencies
- **curl** — HTTP requests
- **jq** — JSON parsing
- **bc** — Math calculations (for percentages, GB conversions)
- **sed** — Text processing

All standard on macOS/Linux.

### Security
- Never log API keys
- Confirm destructive actions (delete, remove)
- Rate limiting for bulk operations
- Use HTTPS for remote access

### Performance
- Scripts cache API responses where possible
- Dashboard generation pulls data once per run
- Bulk operations use batch APIs when available

## Version Compatibility

Tested with:
- Sonarr v4.x (API v3)
- Radarr v5.x (API v3)
- Lidarr v2.x (API v1)
- Readarr v0.3.x (API v1)
- Prowlarr v1.x (API v1)
- Bazarr v1.4.x
- Overseerr v1.33.x (API v1)
- Plex Media Server (all recent versions)
- Tautulli v2.x (API v2)
- SABnzbd v4.x
- Recyclarr v7.x
- Unpackerr v0.14.x
- Notifiarr v0.8.x
- Maintainerr v2.x
- Kometa v2.x (Plex Meta Manager successor)
- FlareSolverr v3.x

## Contributing

Report issues or suggest features via GitHub. Include:
- Script name and command run
- Error output (sanitize API keys!)
- Service versions
- Platform (Docker/Unraid/Synology/etc)

## License

MIT License - See repository for details.
