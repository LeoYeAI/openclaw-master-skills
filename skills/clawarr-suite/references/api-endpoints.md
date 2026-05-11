# API Endpoints Reference

Complete API reference for all *arr services. All endpoints use JSON for request/response bodies.

## Authentication

All requests require authentication:

**Sonarr/Radarr/Lidarr/Readarr/Prowlarr/Bazarr:**
```
Header: X-Api-Key: <api-key>
```

**Plex:**
```
Header: X-Plex-Token: <token>
```

**Tautulli/Overseerr:**
```
Query param: ?apikey=<key>
Or Header: X-Api-Key: <key>
```

## Sonarr (API v3)

Base URL: `http://host:8989/api/v3`

### System
- `GET /system/status` - System information
- `GET /health` - Health checks
- `GET /log/file` - Log file contents

### Series
- `GET /series` - All series
- `GET /series/{id}` - Single series
- `GET /series/lookup?term=<query>` - Search for series
- `POST /series` - Add series
- `PUT /series/{id}` - Update series
- `DELETE /series/{id}` - Delete series

### Episodes
- `GET /episode` - All episodes
- `GET /episode/{id}` - Single episode
- `GET /episode?seriesId={id}` - Episodes for series

### Queue
- `GET /queue` - Download queue
- `GET /queue/{id}` - Queue item details
- `DELETE /queue/{id}?removeFromClient=true` - Remove from queue

### History
- `GET /history?pageSize=20&sortKey=date&sortDirection=descending` - History
- `GET /history/series?seriesId={id}` - Series history

### Quality Profiles
- `GET /qualityprofile` - All quality profiles
- `GET /qualityprofile/{id}` - Single profile

### Root Folders
- `GET /rootfolder` - All root folders
- `POST /rootfolder` - Add root folder

### Download Clients
- `GET /downloadclient` - All download clients
- `GET /downloadclient/{id}` - Single client
- `POST /downloadclient/test` - Test connection

### Indexers
- `GET /indexer` - All indexers
- `POST /indexer/test` - Test indexer

### Commands
- `POST /command` - Execute command
  - `{"name": "SeriesSearch", "seriesId": 1}`
  - `{"name": "EpisodeSearch", "episodeIds": [1,2,3]}`
  - `{"name": "MissingEpisodeSearch"}`
  - `{"name": "RssSync"}`

## Radarr (API v3)

Base URL: `http://host:7878/api/v3`

### System
- `GET /system/status` - System information
- `GET /health` - Health checks

### Movies
- `GET /movie` - All movies
- `GET /movie/{id}` - Single movie
- `GET /movie/lookup?term=<query>` - Search for movies
- `GET /movie/lookup/tmdb?tmdbId=<id>` - Lookup by TMDB ID
- `POST /movie` - Add movie
- `PUT /movie/{id}` - Update movie
- `DELETE /movie/{id}` - Delete movie

### Queue
- `GET /queue` - Download queue
- `DELETE /queue/{id}?removeFromClient=true` - Remove from queue

### History
- `GET /history?pageSize=20&sortKey=date&sortDirection=descending` - History
- `GET /history/movie?movieId={id}` - Movie history

### Quality Profiles
- `GET /qualityprofile` - All quality profiles

### Root Folders
- `GET /rootfolder` - All root folders

### Download Clients
- `GET /downloadclient` - All download clients
- `POST /downloadclient/test` - Test connection

### Commands
- `POST /command`
  - `{"name": "MoviesSearch", "movieIds": [1,2,3]}`
  - `{"name": "MissingMoviesSearch"}`
  - `{"name": "RssSync"}`
  - `{"name": "RefreshMovie", "movieId": 1}`

## Lidarr (API v1)

Base URL: `http://host:8686/api/v1`

### Artists
- `GET /artist` - All artists
- `GET /artist/{id}` - Single artist
- `GET /search?term=<query>` - Search
- `POST /artist` - Add artist
- `DELETE /artist/{id}` - Delete artist

### Albums
- `GET /album` - All albums
- `GET /album/{id}` - Single album
- `GET /album?artistId={id}` - Albums by artist

### Queue
- `GET /queue` - Download queue
- `DELETE /queue/{id}` - Remove from queue

### Quality Profiles
- `GET /qualityprofile` - All quality profiles

### Root Folders
- `GET /rootfolder` - All root folders

## Readarr (API v1)

Base URL: `http://host:8787/api/v1`

### Authors
- `GET /author` - All authors
- `GET /author/{id}` - Single author
- `GET /author/lookup?term=<query>` - Search authors
- `POST /author` - Add author
- `DELETE /author/{id}` - Delete author

### Books
- `GET /book` - All books
- `GET /book/{id}` - Single book
- `GET /book/lookup?term=<query>` - Search books
- `POST /book` - Add book

### Queue
- `GET /queue` - Download queue
- `DELETE /queue/{id}` - Remove from queue

## Prowlarr (API v1)

Base URL: `http://host:9696/api/v1`

### Indexers
- `GET /indexer` - All indexers
- `GET /indexer/{id}` - Single indexer
- `POST /indexer` - Add indexer
- `PUT /indexer/{id}` - Update indexer
- `DELETE /indexer/{id}` - Delete indexer
- `POST /indexer/test` - Test indexer
- `POST /indexer/testall` - Test all indexers

### Applications
- `GET /applications` - All applications (Sonarr/Radarr/etc)
- `POST /applications` - Add application

### Search
- `GET /search?query=<term>&indexerIds=<id>` - Search indexers

### System
- `GET /system/status` - System information
- `GET /health` - Health checks

## Bazarr (API v1)

Base URL: `http://host:6767/api`

### System
- `GET /system/status` - System status
- `GET /system/health` - Health checks

### Episodes
- `GET /episodes` - All episodes
- `GET /episodes/wanted` - Episodes missing subtitles
- `POST /episodes/search` - Search subtitles for episode

### Movies
- `GET /movies` - All movies
- `GET /movies/wanted` - Movies missing subtitles
- `POST /movies/search` - Search subtitles for movie

### Providers
- `GET /providers` - All subtitle providers
- `POST /providers/test` - Test provider

## Overseerr (API v1)

Base URL: `http://host:5055/api/v1`

### System
- `GET /status` - System status
- `GET /settings/public` - Public settings

### Requests
- `GET /request` - All requests
- `GET /request/{id}` - Single request
- `POST /request` - Create request
- `POST /request/{id}/approve` - Approve request
- `POST /request/{id}/decline` - Decline request
- `DELETE /request/{id}` - Delete request

### Search
- `GET /search?query=<term>` - Multi-search (movies + TV)
- `GET /search/movie?query=<term>` - Movie search
- `GET /search/tv?query=<term>` - TV search

### Media
- `GET /media` - All media
- `GET /media/{id}` - Single media item

### Users
- `GET /user` - All users
- `GET /user/me` - Current user

## Plex Media Server

Base URL: `http://host:32400`

### System
- `GET /identity` - Server identity
- `GET /` - Server capabilities

### Library
- `GET /library/sections` - All library sections
- `GET /library/sections/{id}/all` - All items in section
- `GET /library/sections/{id}/refresh` - Refresh library section
- `GET /library/recentlyAdded` - Recently added items

### Metadata
- `GET /library/metadata/{id}` - Item metadata
- `GET /library/metadata/{id}/children` - Children (seasons/episodes)

### Playback
- `GET /status/sessions` - Current playback sessions

## Tautulli (API v2)

Base URL: `http://host:8181/api/v2`

All requests: `?apikey=<key>&cmd=<command>`

### Common Commands
- `cmd=status` - Server status
- `cmd=get_activity` - Current activity
- `cmd=get_history&length=10` - Watch history
- `cmd=get_home_stats` - Homepage statistics
- `cmd=get_library_names` - Library sections
- `cmd=get_library_media_info&section_id=1` - Library contents
- `cmd=get_recently_added&count=10` - Recently added
- `cmd=get_user_names` - All users
- `cmd=get_user_watch_time_stats&user_id=1` - User stats

## Common Patterns

### Search and Add Workflow

1. **Search:**
   ```bash
   GET /movie/lookup?term=dune
   ```

2. **Get quality profiles and root folders:**
   ```bash
   GET /qualityprofile
   GET /rootfolder
   ```

3. **Add with search:**
   ```bash
   POST /movie
   {
     "title": "Dune",
     "tmdbId": 438631,
     "qualityProfileId": 1,
     "rootFolderPath": "/movies",
     "monitored": true,
     "addOptions": {
       "searchForMovie": true
     }
   }
   ```

### Queue Management

1. **Get queue:**
   ```bash
   GET /queue
   ```

2. **Remove stuck item:**
   ```bash
   DELETE /queue/{id}?removeFromClient=true&blocklist=false
   ```

### Health Monitoring

```bash
# Check all services
GET /health  # Returns array of issues

# Empty array = healthy
# Non-empty = issues to address
```

## SABnzbd (API)

Base URL: `http://host:38080/api`

All requests: `?apikey=<key>&mode=<mode>&output=json`

### Common Modes
- `mode=queue` - Download queue
- `mode=history&limit=<count>` - Download history
- `mode=pause` - Pause downloads
- `mode=resume` - Resume downloads
- `mode=speedlimit&value=<kbps>` - Set speed limit
- `mode=status` - Server status
- `mode=get_cats` - Categories
- `mode=version` - Version info

### Queue Response
```json
{
  "queue": {
    "status": "Downloading",
    "speed": "10.2 MB/s",
    "kbpersec": "10445.23",
    "size": "15.2 GB",
    "sizeleft": "5.3 GB",
    "timeleft": "0:08:42",
    "paused": false,
    "slots": [
      {
        "nzo_id": "SABnzbd_nzo_abc123",
        "filename": "Movie.Name.2024.1080p.mkv",
        "mb": "5234.2",
        "size": "10.2 GB",
        "percentage": "51",
        "timeleft": "0:08:42",
        "cat": "movies",
        "priority": "Normal"
      }
    ]
  }
}
```

## Homarr

Note: Homarr is primarily a frontend dashboard aggregator. It does not expose a comprehensive REST API for querying data. Instead, it integrates with *arr apps and other services using their APIs.

For Homarr automation:
- Use individual service APIs (Radarr, Sonarr, etc.)
- Homarr stores config in SQLite database
- Direct database access possible but not recommended
- Future versions may expose REST API

## Advanced Tautulli Endpoints

### Watch Statistics
- `cmd=get_user_watch_time_stats&user_id=<id>&query_days=<days>` - User watch time
- `cmd=get_plays_by_date&time_range=<days>` - Plays by date
- `cmd=get_plays_by_hour_of_day&time_range=<days>` - Hourly breakdown
- `cmd=get_plays_by_dayofweek&time_range=<days>` - Day of week breakdown

### Library Operations
- `cmd=get_library&section_id=<id>` - Library details
- `cmd=get_library_media_info&section_id=<id>&length=<count>` - Media in library
- `cmd=refresh_libraries_list` - Refresh library cache
- `cmd=get_sync_item&sync_id=<id>` - Synced item details

### User Management
- `cmd=get_user&user_id=<id>` - User details
- `cmd=get_user_player_stats&user_id=<id>` - Player statistics
- `cmd=get_user_ips&user_id=<id>` - User IP history

### Notifications
- `cmd=notify&notifier_id=<id>&subject=<text>&body=<text>` - Send notification
- `cmd=get_notifier_config&notifier_id=<id>` - Notifier settings

## Advanced Plex Endpoints

### Playback Control
- `POST /player/playback/playMedia?...` - Start playback
- `POST /player/playback/pause` - Pause
- `POST /player/playback/play` - Resume
- `POST /player/playback/stop` - Stop
- `POST /player/playback/skipNext` - Next track
- `POST /player/playback/skipPrevious` - Previous track

### Search
- `GET /hubs/search?query=<term>` - Universal search
- `GET /library/sections/<id>/search?title=<term>` - Library search

### Playlists
- `GET /playlists` - All playlists
- `GET /playlists/<id>/items` - Playlist items
- `POST /playlists` - Create playlist
- `PUT /playlists/<id>/items` - Add to playlist

### Users
- `GET /accounts` - Managed users (home users)
- `GET /myplex/account` - Current account info

## Advanced Overseerr Endpoints

### Issue Tracking
- `GET /issue` - All issues
- `POST /issue` - Create issue
- `POST /issue/<id>/comment` - Add comment
- `PUT /issue/<id>/resolved` - Mark resolved

### Webhooks
- `GET /settings/notifications/webhook` - Webhook settings
- `POST /settings/notifications/webhook/test` - Test webhook

### Collections
- `GET /collection/<id>` - Collection details
- `POST /collection/<id>/request` - Request entire collection

## Error Responses

All APIs return similar error formats:

```json
{
  "error": "Error message",
  "message": "Detailed error description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `401` - Unauthorized (invalid API key)
- `404` - Not found
- `500` - Internal server error
