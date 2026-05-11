# Suggested Agent Prompts

Natural-language prompts that users can give their AI agent to leverage the ClawARR Suite skill.

## Library Exploration

**"Show me what's downloading right now"**
- Use: `scripts/queue.sh` or `scripts/downloads.sh active`
- Returns current download queue across Radarr/Sonarr and SABnzbd status

**"What movies were added this week?"**
- Use: `scripts/library.sh recent radarr 7`
- Shows recently added movies (last 7 days)

**"What TV shows were added in the last 30 days?"**
- Use: `scripts/library.sh recent sonarr 30`

**"Find all 720p movies that could be upgraded to 4K"**
- Use: `scripts/library.sh quality radarr`
- Shows quality profile breakdown; cross-reference with wanted list

**"Show missing episodes for all monitored shows"**
- Use: `scripts/library.sh missing sonarr`
- Lists all missing/wanted episodes

**"What's coming out this week?"**
- Use: `scripts/manage.sh calendar all 7`
- Shows upcoming releases (movies + TV) for next 7 days

**"How much disk space am I using per library?"**
- Use: `scripts/library.sh disk all`
- Disk usage breakdown by root folder for all *arr apps

**"Show me my genre distribution"**
- Use: `scripts/library.sh genres radarr` or `scripts/library.sh genres sonarr`
- Top genres in your library

**"What content am I monitoring but haven't downloaded?"**
- Use: `scripts/library.sh nofiles radarr` or `scripts/library.sh nofiles sonarr`
- Monitored content with no files on disk

**"Give me library stats for everything"**
- Use: `scripts/library.sh stats all`
- Complete statistics across Radarr, Sonarr, Lidarr

## Analytics & Viewing

**"What are the most watched shows this month?"**
- Use: `scripts/analytics.sh most-watched month`
- Top movies and TV shows by play count (last 30 days)

**"Show my Plex viewing stats for the last 30 days"**
- Use: `scripts/analytics.sh user-stats` or `scripts/analytics.sh most-watched month`

**"Who's watching right now?"**
- Use: `scripts/analytics.sh activity`
- Current active Plex streams

**"What were my peak watching hours this month?"**
- Use: `scripts/analytics.sh peak-hours`
- Hourly breakdown of viewing activity

**"What did [user] watch recently?"**
- Use: `scripts/analytics.sh history 20` (then filter by user)
- Recent watch history

**"What genres are most popular?"**
- Use: `scripts/analytics.sh popular-genres month`
- Genre popularity based on play counts

**"What was recently added to Plex?"**
- Use: `scripts/analytics.sh recent-added 20`

## Request Management

**"Approve all pending Overseerr requests"**
- Use: `scripts/requests.sh list pending` then loop `scripts/requests.sh approve <id>`

**"Show pending media requests"**
- Use: `scripts/requests.sh list pending`

**"Deny request 123 because quality is too low"**
- Use: `scripts/requests.sh deny 123 "Quality too low, please search for better release"`

**"What's the status of request 456?"**
- Use: `scripts/requests.sh info 456`

**"How many requests do we have total?"**
- Use: `scripts/requests.sh stats`
- Complete request statistics

## Content Management

**"Add Dune Part Two in 4K to Radarr"**
- Use: `scripts/manage.sh add-movie "Dune Part Two" 4` (where 4 is quality profile ID)
- Or interactive: `scripts/manage.sh add-movie "Dune Part Two"` and select profile

**"Add Foundation TV series to Sonarr"**
- Use: `scripts/manage.sh add-series "Foundation"`

**"Remove movie ID 123 from Radarr"**
- Use: `scripts/manage.sh remove radarr 123`

**"Show all wanted content"**
- Use: `scripts/manage.sh wanted all`
- Missing movies and episodes

**"What's the download history for the last week?"**
- Use: `scripts/manage.sh history radarr 50`
- Recent downloads/imports

**"Refresh metadata for Radarr"**
- Use: `scripts/manage.sh refresh radarr`

**"Trigger rename for movie ID 789"**
- Use: `scripts/manage.sh rename radarr 789`

## Subtitles

**"What subtitles are missing?"**
- Use: `scripts/subtitles.sh wanted`
- Missing subtitles for both movies and TV

**"Show recent subtitle downloads"**
- Use: `scripts/subtitles.sh history 20`

**"Search for subtitles for series ID 456"**
- Use: `scripts/subtitles.sh search series 456`

**"What languages are configured for subtitles?"**
- Use: `scripts/subtitles.sh languages`

## Indexers & Downloads

**"Test all my indexers"**
- Use: `scripts/indexers.sh test`
- Tests connectivity for all Prowlarr indexers

**"Show indexer performance stats"**
- Use: `scripts/indexers.sh stats`
- Query counts, success rates

**"List all configured indexers"**
- Use: `scripts/indexers.sh list`

**"What's the current download speed?"**
- Use: `scripts/downloads.sh speed`
- SABnzbd current speed

**"Pause downloads"**
- Use: `scripts/downloads.sh pause`

**"Resume downloads"**
- Use: `scripts/downloads.sh resume`

**"Show SABnzbd download history"**
- Use: `scripts/downloads.sh history 30`

## Dashboard & Reporting

**"Generate a dashboard of my media library"**
- Use: `scripts/dashboard.sh`
- Creates self-contained HTML dashboard with all stats

**"Show me the health of all services"**
- Use: `scripts/status.sh`
- Health check across all configured *arr apps

**"Run diagnostics on my stack"**
- Use: `scripts/diagnose.sh`
- Automated troubleshooting and health checks

**"Discover what services are running on my media server"**
- Use: `scripts/discover.sh <host-ip>`

## Bulk Operations

**"Find and upgrade all 720p content to 1080p"**
1. `scripts/library.sh quality radarr` — identify 720p content
2. Manually update quality profiles in Radarr UI or via API
3. `scripts/manage.sh wanted radarr` — trigger searches

**"Add all items from Overseerr pending queue to Radarr/Sonarr"**
1. `scripts/requests.sh list pending`
2. Loop through and approve: `scripts/requests.sh approve <id>`

**"Clean up unmonitored content"**
1. `scripts/library.sh unmonitored radarr`
2. Review list, then remove via `scripts/manage.sh remove radarr <id>`

## Maintenance

**"Check for stale Docker mounts"**
- Use: `scripts/diagnose.sh`
- Detects containers with stale mount points after host reboot

**"Show disk usage warnings"**
- Use: `scripts/library.sh disk all`

**"Verify all services are healthy"**
- Use: `scripts/status.sh`

## Setup & Configuration

**"Set up ClawARR Suite for the first time"**
- Use: `scripts/setup.sh <host-ip>`
- Guided setup wizard

**"Discover services on my NAS at 192.168.1.100"**
- Use: `scripts/discover.sh 192.168.1.100`

## Advanced Workflows

**"Show me sci-fi movies added this year that are missing"**
1. `scripts/library.sh genres radarr` — confirm sci-fi genre exists
2. Combine with API calls to filter by year and missing status
3. Or use `scripts/manage.sh wanted radarr` and manually filter

**"Generate weekly viewing report"**
1. `scripts/analytics.sh most-watched week`
2. `scripts/analytics.sh user-stats`
3. Combine into formatted report

**"Auto-approve requests from trusted users"**
1. `scripts/requests.sh list pending`
2. Parse JSON output, filter by user
3. Approve matching requests

## Tips for Natural Prompts

- Be specific about time ranges: "last week", "last 30 days", "this month"
- Mention app names when relevant: "Radarr", "Sonarr", "Tautulli"
- Use domain language: "movies", "series", "episodes", "subtitles"
- Combine operations: "Show missing 4K movies added in the last month"

The agent should translate natural language to the appropriate script + arguments.
