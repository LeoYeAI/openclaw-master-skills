# Traktarr & Retraktarr Guide

## Overview

**Traktarr** and **Retraktarr** are automation tools that bridge Trakt.tv with Radarr/Sonarr, creating a two-way sync system for your media library and watchlists.

### Traktarr (Trakt → Radarr/Sonarr)

**Purpose:** Automatically add content from Trakt lists to your *arr apps for download.

**Use Cases:**
- Auto-add trending/popular movies and shows
- Monitor custom Trakt lists (e.g., "Must Watch 2024")
- Import watchlist items automatically
- Add content from public curated lists
- Scheduled automation via cron

**Example Workflow:**
1. You add movies to your Trakt watchlist
2. Traktarr runs every 6 hours (via cron)
3. New watchlist items are added to Radarr
4. Radarr downloads them automatically
5. You never manually add content again

### Retraktarr (Radarr/Sonarr → Trakt)

**Purpose:** Sync your Radarr/Sonarr library to Trakt as public or private lists.

**Use Cases:**
- Share your library as a public Trakt list
- Keep Trakt lists in sync with your collection
- Create backup lists of your library
- Share recommendations with friends
- Track library size over time

**Example Workflow:**
1. You add movies to Radarr
2. Retraktarr runs daily (via cron)
3. New library items appear in your Trakt list
4. Friends can see/follow your public list
5. Your Trakt profile reflects your actual library

## Installation

### Method 1: pip (Recommended)

```bash
# Install traktarr
pip3 install --user traktarr

# Install retraktarr
pip3 install --user retraktarr

# Verify installation
traktarr --version
retraktarr --version
```

### Method 2: Git Clone (Development)

**Traktarr:**
```bash
git clone https://github.com/l3uddz/traktarr.git
cd traktarr
pip3 install -r requirements.txt
python3 traktarr.py --version
```

**Retraktarr:**
```bash
git clone https://github.com/l3uddz/retraktarr.git
cd retraktarr
pip3 install -r requirements.txt
python3 retraktarr.py --version
```

### Installation Locations

When installed via pip with `--user`:
- **Linux/macOS:** `~/.local/bin/traktarr`, `~/.local/bin/retraktarr`
- **Add to PATH:** `export PATH="$HOME/.local/bin:$PATH"`

When cloned from git:
- Scripts run from their directory: `python3 traktarr.py` or `python3 retraktarr.py`

## Configuration

### Traktarr Config

**Location:** `~/.config/traktarr/config.json`

**Minimal Config:**
```json
{
  "core": {
    "debug": false
  },
  "trakt": {
    "client_id": "YOUR_TRAKT_CLIENT_ID",
    "client_secret": "YOUR_TRAKT_CLIENT_SECRET"
  },
  "radarr": {
    "url": "http://localhost:7878",
    "api_key": "YOUR_RADARR_KEY",
    "root_folder": "/movies",
    "quality_profile": "HD-1080p",
    "minimum_availability": "released"
  },
  "sonarr": {
    "url": "http://localhost:8989",
    "api_key": "YOUR_SONARR_KEY",
    "root_folder": "/tv",
    "quality_profile": "HD-1080p",
    "language_profile": "English"
  },
  "filters": {
    "movies": {
      "allowed_countries": ["us", "gb", "ca"],
      "allowed_languages": ["en"],
      "blacklisted_genres": ["anime"],
      "blacklisted_min_year": 1990,
      "rating_limit": 5.0
    },
    "shows": {
      "allowed_countries": ["us", "gb", "ca"],
      "allowed_languages": ["en"],
      "blacklisted_genres": ["anime"],
      "blacklisted_networks": [],
      "rating_limit": 5.0
    }
  },
  "automatic": {
    "movies": {
      "anticipated": 10,
      "trending": 5,
      "popular": 5,
      "boxoffice": 5
    },
    "shows": {
      "anticipated": 10,
      "trending": 5,
      "popular": 5
    }
  }
}
```

**Key Settings:**

- **`root_folder`** - Where media is stored (must match Radarr/Sonarr root folder)
- **`quality_profile`** - Quality to download (must exist in Radarr/Sonarr)
- **`minimum_availability`** - When to download movies: `announced`, `in_cinemas`, `released`, `predb`
- **`filters`** - Prevent unwanted content from being added
- **`automatic`** - How many items to add from each list type

**Common Filter Options:**

```json
"filters": {
  "movies": {
    "allowed_countries": ["us", "gb", "ca", "au"],
    "allowed_languages": ["en"],
    "blacklisted_genres": ["anime", "documentary"],
    "blacklisted_min_year": 2000,
    "blacklisted_max_year": 2025,
    "rating_limit": 6.0,
    "blacklisted_tmdb_ids": [12345, 67890],
    "runtime_limit": 30
  }
}
```

### Retraktarr Config

**Location:** `~/.config/retraktarr/config.json`

**Minimal Config:**
```json
{
  "core": {
    "debug": false
  },
  "trakt": {
    "client_id": "YOUR_TRAKT_CLIENT_ID",
    "client_secret": "YOUR_TRAKT_CLIENT_SECRET"
  },
  "radarr": {
    "url": "http://localhost:7878",
    "api_key": "YOUR_RADARR_KEY",
    "list_name": "radarr-library",
    "list_privacy": "private"
  },
  "sonarr": {
    "url": "http://localhost:8989",
    "api_key": "YOUR_SONARR_KEY",
    "list_name": "sonarr-library",
    "list_privacy": "private"
  },
  "sync": {
    "interval_hours": 24,
    "remove_from_trakt": false
  }
}
```

**Key Settings:**

- **`list_name`** - Name of Trakt list to create/update
- **`list_privacy`** - `public`, `private`, or `friends`
- **`interval_hours`** - How often to sync (for automatic mode)
- **`remove_from_trakt`** - Remove items from Trakt list if deleted from *arr

**Privacy Options:**

- **`public`** - Anyone can see the list
- **`private`** - Only you can see it
- **`friends`** - Only Trakt friends can see it

## Usage

### Traktarr Commands

**Manual Add from Trakt Lists:**

```bash
# Add 10 anticipated movies to Radarr
traktarr movies -t anticipated --add-limit 10

# Add 5 trending shows to Sonarr
traktarr shows -t trending --add-limit 5

# Add from popular list
traktarr movies -t popular --add-limit 20

# Add from box office
traktarr movies -t boxoffice --add-limit 10

# Add from your personal watchlist
traktarr movies -t watchlist --add-limit 50

# Add from custom Trakt list
traktarr movies -l username/list-name --add-limit 10
```

**List Types:**
- `anticipated` - Most anticipated upcoming releases
- `trending` - Currently trending
- `popular` - Most popular overall
- `boxoffice` - Top box office (movies only)
- `watched` - Most watched this week
- `played` - Most played this week
- `watchlist` - Your personal Trakt watchlist

**Automatic Mode (run via cron):**

```bash
# Run automatic sync based on config.json settings
traktarr run

# This will add content from all enabled lists in config
```

**Using ClawARR Script:**

```bash
# Check status
./trakt.sh traktarr-status

# Add content
./trakt.sh traktarr-add movies trending 10
./trakt.sh traktarr-add shows popular 5

# Configure
./trakt.sh traktarr-config
```

### Retraktarr Commands

**Manual Sync:**

```bash
# Sync movies only
retraktarr sync --movies

# Sync shows only
retraktarr sync --shows

# Sync both
retraktarr sync
```

**Using ClawARR Script:**

```bash
# Check status
./trakt.sh retraktarr-status

# Sync library
./trakt.sh retraktarr-sync all
./trakt.sh retraktarr-sync movies
./trakt.sh retraktarr-sync shows

# Configure
./trakt.sh retraktarr-config
```

## Automation with Cron

### Traktarr Cron Schedule

**Every 6 hours (recommended for automatic mode):**

```bash
# Edit crontab
crontab -e

# Add line:
0 */6 * * * /home/user/.local/bin/traktarr run >> /var/log/traktarr.log 2>&1
```

**Daily at 2am:**

```bash
0 2 * * * /home/user/.local/bin/traktarr run >> /var/log/traktarr.log 2>&1
```

**Multiple targeted runs:**

```bash
# Trending movies every 12 hours
0 */12 * * * /home/user/.local/bin/traktarr movies -t trending --add-limit 5

# Anticipated shows daily
0 3 * * * /home/user/.local/bin/traktarr shows -t anticipated --add-limit 10

# Personal watchlist every 4 hours
0 */4 * * * /home/user/.local/bin/traktarr movies -t watchlist --add-limit 20
```

### Retraktarr Cron Schedule

**Daily sync at 3am:**

```bash
# Edit crontab
crontab -e

# Add line:
0 3 * * * /home/user/.local/bin/retraktarr sync >> /var/log/retraktarr.log 2>&1
```

**Every 12 hours:**

```bash
0 */12 * * * /home/user/.local/bin/retraktarr sync >> /var/log/retraktarr.log 2>&1
```

**Weekly (Sundays at 4am):**

```bash
0 4 * * 0 /home/user/.local/bin/retraktarr sync >> /var/log/retraktarr.log 2>&1
```

## Common Patterns

### Pattern 1: Curated Auto-Add

**Goal:** Automatically add high-quality content from multiple sources

**Traktarr Config:**
```json
"automatic": {
  "movies": {
    "anticipated": 15,
    "trending": 10,
    "popular": 5,
    "boxoffice": 5
  },
  "shows": {
    "anticipated": 10,
    "trending": 5,
    "popular": 3
  }
}
```

**Cron:** Every 12 hours
```bash
0 */12 * * * traktarr run
```

### Pattern 2: Watchlist-Only

**Goal:** Only add items you manually curate in your Trakt watchlist

**Traktarr Config:**
```json
"automatic": {
  "movies": {
    "watchlist": 100
  },
  "shows": {
    "watchlist": 50
  }
}
```

**Cron:** Every 4 hours (near real-time)
```bash
0 */4 * * * traktarr run
```

### Pattern 3: Custom List Following

**Goal:** Follow curated public lists from trusted users

**Command:**
```bash
# Add from specific user's list
traktarr movies -l username/best-movies-2024 --add-limit 50
```

**Cron:** Daily
```bash
0 2 * * * traktarr movies -l username/best-movies-2024 --add-limit 10
```

### Pattern 4: Quality-First

**Goal:** Only add highly-rated recent content

**Filters:**
```json
"filters": {
  "movies": {
    "rating_limit": 7.5,
    "blacklisted_min_year": 2020,
    "allowed_countries": ["us", "gb"]
  }
}
```

### Pattern 5: Two-Way Sync

**Goal:** Keep Trakt and Radarr/Sonarr perfectly in sync

**Setup:**
1. Traktarr runs every 6 hours (adds from Trakt → Arr)
2. Retraktarr runs daily (syncs Arr → Trakt)
3. Result: Both stay in sync

**Cron:**
```bash
# Traktarr every 6 hours
0 */6 * * * traktarr run

# Retraktarr daily at 3am
0 3 * * * retraktarr sync
```

## Troubleshooting

### Traktarr Issues

**Problem:** Traktarr adds content I don't want

**Solution:** Tighten filters in config.json
```json
"filters": {
  "movies": {
    "rating_limit": 7.0,
    "blacklisted_genres": ["horror", "anime"],
    "allowed_languages": ["en"]
  }
}
```

**Problem:** Traktarr not adding anything

**Solutions:**
1. Check filters aren't too strict
2. Verify Radarr/Sonarr API keys
3. Check root folder exists and is writable
4. Verify quality profile exists in Radarr/Sonarr
5. Run with `--debug` flag for verbose logging

**Problem:** "Quality profile not found"

**Solution:** Get exact profile name from Radarr/Sonarr:
```bash
# List Radarr quality profiles
curl -H "X-Api-Key: KEY" http://HOST:7878/api/v3/qualityprofile | jq '.[] | .name'

# Update config.json with exact match
```

**Problem:** Items added but not downloading

**Issue:** This is Radarr/Sonarr behavior, not Traktarr
**Check:**
1. Indexers are working
2. Quality profile allows downloads
3. Content is available
4. Disk space available

### Retraktarr Issues

**Problem:** List not appearing on Trakt

**Solutions:**
1. Check authentication (re-auth if needed)
2. Verify list privacy setting
3. Check Trakt API rate limits
4. Run with `--debug` for errors

**Problem:** Duplicate items in list

**Solution:** Delete and recreate list, or manually clean via Trakt web UI

**Problem:** Items not removed from Trakt when deleted from Arr

**Setting:** Enable in config:
```json
"sync": {
  "remove_from_trakt": true
}
```

## Best Practices

### 1. Start Conservative

Begin with small limits and strict filters:
```json
"automatic": {
  "movies": {
    "trending": 5,
    "popular": 3
  }
}
```

### 2. Use Appropriate Intervals

- **Trending lists:** Check every 6-12 hours
- **Watchlist:** Check every 2-4 hours (if actively managing)
- **Anticipated:** Once daily is enough
- **Retraktarr sync:** Once daily is sufficient

### 3. Monitor Disk Usage

Traktarr can add a LOT of content. Set limits to avoid filling your drives:
```json
"automatic": {
  "movies": {
    "trending": 5,  // Not 50!
    "popular": 3
  }
}
```

### 4. Test Filters First

Before automating, test filter combinations manually:
```bash
# Dry run (if supported)
traktarr movies -t trending --add-limit 10 --dry-run
```

### 5. Separate Quality Profiles

Create separate Radarr/Sonarr quality profiles for Traktarr-added content if you want different quality for auto-added items vs manual adds.

### 6. Review Periodically

Check what Traktarr is adding:
```bash
# View recent Radarr additions
curl -H "X-Api-Key: KEY" http://HOST:7878/api/v3/movie | jq '.[] | select(.added > "2024-01-01") | .title'
```

### 7. Backup Configs

Keep backups of working configurations:
```bash
cp ~/.config/traktarr/config.json ~/traktarr-config-backup.json
cp ~/.config/retraktarr/config.json ~/retraktarr-config-backup.json
```

## Integration with ClawARR Scripts

The ClawARR suite provides convenient wrappers:

### Quick Setup
```bash
./trackers.sh setup
# Choose option 5 (Traktarr) or 6 (Retraktarr)
```

### Status Checks
```bash
./trakt.sh traktarr-status
./trakt.sh retraktarr-status
./trackers.sh status  # Shows all tracker statuses
```

### Adding Content
```bash
./trakt.sh traktarr-add movies trending 10
./trakt.sh traktarr-add shows anticipated 5
```

### Syncing
```bash
./trakt.sh retraktarr-sync all
```

### Configuration
```bash
./trakt.sh traktarr-config
./trakt.sh retraktarr-config
```

## Example Complete Setup

### Step 1: Install Tools
```bash
pip3 install --user traktarr retraktarr
export PATH="$HOME/.local/bin:$PATH"
```

### Step 2: Configure via ClawARR
```bash
cd /path/to/clawarr-suite/scripts
./trackers.sh setup  # Option 1 (Trakt auth)
./trackers.sh setup  # Option 5 (Traktarr config)
./trackers.sh setup  # Option 6 (Retraktarr config)
```

### Step 3: Test Manually
```bash
./trakt.sh traktarr-add movies trending 3
./trakt.sh retraktarr-sync movies
```

### Step 4: Verify in Radarr/Sonarr
Check that movies were added to Radarr

### Step 5: Set Up Automation
```bash
crontab -e

# Add:
0 */6 * * * $HOME/.local/bin/traktarr run >> /var/log/traktarr.log 2>&1
0 3 * * * $HOME/.local/bin/retraktarr sync >> /var/log/retraktarr.log 2>&1
```

### Step 6: Monitor Logs
```bash
tail -f /var/log/traktarr.log
tail -f /var/log/retraktarr.log
```

## Resources

### Official Documentation
- **Traktarr:** https://github.com/l3uddz/traktarr
- **Retraktarr:** https://github.com/l3uddz/retraktarr
- **Trakt API:** https://trakt.docs.apiary.io/

### Community
- Reddit: r/radarr, r/sonarr, r/trakt
- Discord: Radarr/Sonarr official servers

### Related Tools
- **Plex-Trakt-Sync:** Sync Plex watch history to Trakt
- **Tautulli:** Plex monitoring and notifications
- **Overseerr:** Request management

## Summary

**Traktarr** and **Retraktarr** create a powerful automation loop:

1. You curate content on Trakt (or let Trakt's algorithms help)
2. Traktarr pulls from Trakt → adds to Radarr/Sonarr
3. Radarr/Sonarr download the content
4. Retraktarr pushes your library back to Trakt as lists
5. Friends can follow your lists and discover your collection

**Key Benefits:**
- Hands-off content discovery and addition
- Share your library publicly without exposing your server
- Keep Trakt as the "source of truth" for what you want
- Automate 90% of content management

**Key Risks:**
- Can add too much content (use filters!)
- May add low-quality content (set rating limits)
- Requires monitoring initially to dial in settings

Start small, monitor closely, and gradually expand as you find the right balance for your setup.
