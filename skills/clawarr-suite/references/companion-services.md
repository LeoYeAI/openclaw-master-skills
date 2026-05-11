# Companion Services Reference

Guide for *arr stack companion services: Prowlarr, Recyclarr, FlareSolverr, Unpackerr, Notifiarr, Maintainerr, and Kometa.

## Prowlarr — Indexer Management

### What It Does
Centralized indexer management. Add indexers once in Prowlarr, and they automatically sync to Sonarr, Radarr, Lidarr, and Readarr.

### Key API Endpoints
```
GET  /api/v1/indexer              # List indexers
POST /api/v1/indexer/test         # Test indexer
GET  /api/v1/applications         # List sync targets
POST /api/v1/applications         # Add sync target
POST /api/v1/applications/action/sync  # Trigger sync
GET  /api/v1/search?query=...     # Search across indexers
GET  /api/v1/health               # Health check
GET  /api/v1/system/status        # System info
GET  /api/v1/log                  # Logs
```

### Adding Sync Targets
After installing Prowlarr, add each *arr app as a sync target:
```json
{
  "name": "Sonarr",
  "implementation": "Sonarr",
  "configContract": "SonarrSettings",
  "syncLevel": "fullSync",
  "fields": [
    {"name": "prowlarrUrl", "value": "http://host:9696"},
    {"name": "baseUrl", "value": "http://host:8989"},
    {"name": "apiKey", "value": "sonarr-api-key"}
  ]
}
```

### Search Categories
- Movies: 2000
- TV: 5000
- Audio: 3000
- Books: 7000

---

## Recyclarr — Quality Profile Sync

### What It Does
Automatically syncs quality profiles from [TRaSH Guides](https://trash-guides.info/) to Sonarr and Radarr. Keeps your quality profiles optimized without manual tuning.

### Configuration (recyclarr.yml)
```yaml
sonarr:
  main:
    base_url: http://host:8989
    api_key: sonarr-key
    delete_old_custom_formats: true
    replace_existing_custom_formats: true
    quality_definition:
      type: series
    quality_profiles:
      - name: HD-1080p
        reset_unmatched_scores:
          enabled: true

radarr:
  main:
    base_url: http://host:7878
    api_key: radarr-key
    delete_old_custom_formats: true
    replace_existing_custom_formats: true
    quality_definition:
      type: movie
    quality_profiles:
      - name: HD-1080p
        reset_unmatched_scores:
          enabled: true
```

### Commands
```bash
recyclarr sync                    # Sync all
recyclarr sync --preview          # Dry run
recyclarr sync sonarr             # Sync only Sonarr
recyclarr list custom-formats radarr  # List available profiles
recyclarr list qualities radarr   # List quality definitions
recyclarr config create           # Generate template
```

---

## FlareSolverr — Cloudflare Bypass

### What It Does
Proxy that solves Cloudflare challenges. Some indexers use Cloudflare protection that blocks automated access. FlareSolverr sits between Prowlarr and these indexers.

### Setup
1. Run FlareSolverr container (port 8191)
2. In Prowlarr: Settings → Indexers → Add → FlareSolverr
3. Set URL: `http://host:8191`
4. Tag indexers that need Cloudflare bypass

### API
```
POST /v1 {"cmd": "request.get", "url": "..."}
GET  /health
```

No configuration needed beyond running the container. It auto-handles challenges.

---

## Unpackerr — Archive Extraction

### What It Does
Monitors Sonarr/Radarr/Lidarr download queues and automatically extracts compressed archives (.rar, .zip, etc.) so the *arr apps can import them.

### Configuration (Environment Variables)
```bash
# Sonarr integration
UN_SONARR_0_URL=http://host:8989
UN_SONARR_0_API_KEY=sonarr-key
UN_SONARR_0_PATHS_0=/downloads/tv

# Radarr integration
UN_RADARR_0_URL=http://host:7878
UN_RADARR_0_API_KEY=radarr-key
UN_RADARR_0_PATHS_0=/downloads/movies

# Optional: Lidarr
UN_LIDARR_0_URL=http://host:8686
UN_LIDARR_0_API_KEY=lidarr-key
```

### How It Works
1. Monitors *arr app queues via API
2. When a download completes with archives, extracts them
3. Notifies the *arr app to retry import
4. Cleans up extracted files after successful import

No manual intervention needed. Fully automated.

---

## Notifiarr — Unified Notifications

### What It Does
Routes notifications from all *arr services to Discord, Telegram, Slack, or other targets. Provides health monitoring, grab notifications, import confirmations.

### Setup
1. Run container (port 5454)
2. Open web UI at `http://host:5454`
3. Configure Discord webhook URL
4. Add *arr service URLs and API keys
5. Enable desired notification triggers

### Notification Types
- **Grabs**: When content is grabbed from indexer
- **Imports**: When content is imported to library
- **Health**: Service health alerts
- **Upgrades**: When quality upgrades happen
- **Failures**: Download/import failures

### Discord Webhook Setup
1. Discord Server Settings → Integrations → Webhooks
2. Create webhook in desired channel
3. Copy webhook URL
4. Paste in Notifiarr settings

---

## Maintainerr — Library Cleanup

### What It Does
Automated library cleanup based on configurable rules. Identifies media that matches criteria (unwatched, old, low-rated) and manages deletion.

### Common Rules
- Delete movies unwatched for 180+ days
- Delete shows with all episodes watched 90+ days ago
- Delete movies rated below 5.0 and unwatched for 60 days
- Keep movies in specific Plex collections regardless
- Delete content not in any Trakt list

### API Endpoints
```
GET  /api/rules                   # List rules
POST /api/rules/run               # Run all rules
POST /api/rules/:id/run           # Run specific rule
GET  /api/rules/:id/media         # Media matched by rule
POST /api/rules/:id/exclusion     # Exclude media from rule
GET  /api/collections             # Managed collections
GET  /api/logs                    # Activity log
```

### Workflow
1. Create rules in web UI (http://host:6246)
2. Rules evaluate periodically
3. Matched media moves to a collection
4. After configurable grace period, media is deleted
5. Exclusions override rules for specific items

---

## Kometa (Plex Meta Manager) — Collections & Overlays

### What It Does
Automatically creates/manages Plex collections, applies poster overlays (4K badge, Dolby Atmos icon), and maintains metadata from external sources.

### Configuration (config.yml)
```yaml
libraries:
  Movies:
    collection_files:
      - default: basic      # Genre collections
      - default: imdb        # IMDb Top 250, Popular
      - default: tmdb        # TMDb trending
      - default: trakt       # Trakt lists
    overlay_files:
      - default: resolution  # 4K/1080p badges
      - default: audio_codec # Atmos/DTS-X badges
      - default: ratings     # IMDb/RT ratings
  TV Shows:
    collection_files:
      - default: basic
      - default: imdb
    overlay_files:
      - default: resolution
      - default: status      # Returning/Ended/Canceled

plex:
  url: http://host:32400
  token: your-plex-token

tmdb:
  apikey: your-tmdb-key       # Optional, for TMDb collections
  language: en
```

### Available Defaults
**Collections:**
basic, imdb, tmdb, trakt, flixpatrol, anidb, myanimelist, oscars, golden, spirit, separator

**Overlays:**
resolution, audio_codec, video_format, streaming, ratings, ribbon, status

### Running
```bash
# One-shot run
docker run --rm -v /config:/config kometateam/kometa:latest --run

# Scheduled (daily at 5 AM)
docker run -v /config:/config kometateam/kometa:latest --run-schedule "05:00"

# Specific library only
docker run --rm -v /config:/config kometateam/kometa:latest --run --run-libraries "Movies"
```

---

## Service Dependencies

```
Prowlarr ──→ Sonarr, Radarr (indexer sync)
FlareSolverr ──→ Prowlarr (Cloudflare proxy)
Recyclarr ──→ Sonarr, Radarr (quality profiles)
Unpackerr ──→ Sonarr, Radarr (archive extraction)
Notifiarr ──→ All *arr apps (notifications)
Maintainerr ──→ Plex, Sonarr, Radarr (cleanup)
Kometa ──→ Plex (collections/overlays)
```

## Docker Images
```
lscr.io/linuxserver/prowlarr:latest
ghcr.io/flaresolverr/flaresolverr:latest
ghcr.io/recyclarr/recyclarr:latest
ghcr.io/unpackerr/unpackerr:latest
golift/notifiarr:latest
ghcr.io/jorenn92/maintainerr:latest
kometateam/kometa:latest
```
