---
name: apple-music
version: 0.6.0
description: Apple Music integration via AppleScript (macOS) or MusicKit API
---

# Apple Music Integration

Guide for integrating with Apple Music. Covers AppleScript (macOS), MusicKit API (cross-platform), and the critical library-first requirement.

## When to Use

Invoke when users ask to:
- Manage playlists (create, add/remove tracks, list)
- Control playback (play, pause, skip, volume)
- Search catalog or library
- Add songs to library
- Access listening history or recommendations

## Critical Rule: Library-First Workflow

**You CANNOT add catalog songs directly to playlists.**

Songs must be in the user's library first:
- ❌ Catalog ID → Playlist (fails)
- ✅ Catalog ID → Library → Playlist (works)

**Why:** Playlists use library IDs (`i.abc123`), not catalog IDs (`1234567890`).

This applies to both AppleScript and API approaches.

## Platform Comparison

| Feature | AppleScript (macOS) | MusicKit API |
|---------|:-------------------:|:------------:|
| Setup required | None | Dev account + tokens |
| Playlist management | Full | API-created only |
| Playback control | Full | None |
| Catalog search | No | Yes |
| Library access | Instant | With tokens |
| Cross-platform | No | Yes |

---

# AppleScript (macOS)

Zero setup. Works immediately with the Music app.

**Run via Bash:**
```bash
osascript -e 'tell application "Music" to playpause'
osascript -e 'tell application "Music" to return name of current track'
```

**Multi-line scripts:**
```bash
osascript <<'EOF'
tell application "Music"
    set t to current track
    return {name of t, artist of t}
end tell
EOF
```

## Available Operations

| Category | Operations |
|----------|------------|
| **Playback** | play, pause, stop, resume, next track, previous track, fast forward, rewind |
| **Player State** | player position, player state, sound volume, mute, shuffle enabled/mode, song repeat |
| **Current Track** | name, artist, album, duration, time, rating, loved, disliked, genre, year, track number |
| **Library** | search, list tracks, get track properties, set ratings |
| **Playlists** | list, create, delete, rename, add tracks, remove tracks, get tracks |
| **AirPlay** | list devices, select device, current device |

## Track Properties (Read)

```applescript
tell application "Music"
    set t to current track
    -- Basic info
    name of t           -- "Hey Jude"
    artist of t         -- "The Beatles"
    album of t          -- "1 (Remastered)"
    album artist of t   -- "The Beatles"
    composer of t       -- "Lennon-McCartney"
    genre of t          -- "Rock"
    year of t           -- 1968

    -- Timing
    duration of t       -- 431.0 (seconds)
    time of t           -- "7:11" (formatted)
    start of t          -- start time in seconds
    finish of t         -- end time in seconds

    -- Track info
    track number of t   -- 21
    track count of t    -- 27
    disc number of t    -- 1
    disc count of t     -- 1

    -- Ratings
    rating of t         -- 0-100 (20 per star)
    loved of t          -- true/false
    disliked of t       -- true/false

    -- Playback
    played count of t   -- 42
    played date of t    -- date last played
    skipped count of t  -- 3
    skipped date of t   -- date last skipped

    -- IDs
    persistent ID of t  -- "ABC123DEF456"
    database ID of t    -- 12345
end tell
```

## Track Properties (Writable)

```applescript
tell application "Music"
    set t to current track
    set rating of t to 80          -- 4 stars
    set loved of t to true
    set disliked of t to false
    set name of t to "New Name"    -- rename track
    set genre of t to "Alternative"
    set year of t to 1995
end tell
```

## Player State Properties

```applescript
tell application "Music"
    player state          -- stopped, playing, paused, fast forwarding, rewinding
    player position       -- current position in seconds (read/write)
    sound volume          -- 0-100 (read/write)
    mute                  -- true/false (read/write)
    shuffle enabled       -- true/false (read/write)
    shuffle mode          -- songs, albums, groupings
    song repeat           -- off, one, all (read/write)
    current track         -- track object
    current playlist      -- playlist object
    current stream URL    -- URL if streaming
end tell
```

## Playback Commands

```applescript
tell application "Music"
    -- Play controls
    play                          -- play current selection
    pause
    stop
    resume
    playpause                     -- toggle play/pause
    next track
    previous track
    fast forward
    rewind

    -- Play specific content
    play (first track of library playlist 1 whose name contains "Hey Jude")
    play user playlist "Road Trip"

    -- Settings
    set player position to 60     -- seek to 1:00
    set sound volume to 50        -- 0-100
    set mute to true
    set shuffle enabled to true
    set song repeat to all        -- off, one, all
end tell
```

## Library Queries

```applescript
tell application "Music"
    -- All library tracks
    every track of library playlist 1

    -- Search by name
    tracks of library playlist 1 whose name contains "Beatles"

    -- Search by artist
    tracks of library playlist 1 whose artist contains "Beatles"

    -- Search by album
    tracks of library playlist 1 whose album contains "Abbey Road"

    -- Combined search
    tracks of library playlist 1 whose name contains "Hey" and artist contains "Beatles"

    -- By genre
    tracks of library playlist 1 whose genre is "Rock"

    -- By year
    tracks of library playlist 1 whose year is 1969

    -- By rating
    tracks of library playlist 1 whose rating > 60  -- 3+ stars

    -- Loved tracks
    tracks of library playlist 1 whose loved is true

    -- Recently played (sort by played date)
    tracks of library playlist 1 whose played date > (current date) - 7 * days
end tell
```

## Playlist Operations

```applescript
tell application "Music"
    -- List all playlists
    name of every user playlist

    -- Get playlist
    user playlist "Road Trip"
    first user playlist whose name contains "Road"

    -- Create playlist
    make new user playlist with properties {name:"New Playlist", description:"My playlist"}

    -- Delete playlist
    delete user playlist "Old Playlist"

    -- Rename playlist
    set name of user playlist "Old Name" to "New Name"

    -- Get playlist tracks
    every track of user playlist "Road Trip"
    name of every track of user playlist "Road Trip"

    -- Add track to playlist (must be library track)
    set targetPlaylist to user playlist "Road Trip"
    set targetTrack to first track of library playlist 1 whose name contains "Hey Jude"
    duplicate targetTrack to targetPlaylist

    -- Remove track from playlist
    delete (first track of user playlist "Road Trip" whose name contains "Hey Jude")

    -- Playlist properties
    duration of user playlist "Road Trip"   -- total duration
    time of user playlist "Road Trip"       -- formatted duration
    count of tracks of user playlist "Road Trip"
end tell
```

## AirPlay

```applescript
tell application "Music"
    -- List AirPlay devices
    name of every AirPlay device

    -- Get current device
    current AirPlay devices

    -- Set output device
    set current AirPlay devices to {AirPlay device "Living Room"}

    -- Multiple devices
    set current AirPlay devices to {AirPlay device "Living Room", AirPlay device "Kitchen"}

    -- Device properties
    set d to AirPlay device "Living Room"
    name of d
    kind of d           -- computer, AirPort Express, Apple TV, AirPlay device, Bluetooth device
    active of d         -- true if playing
    available of d      -- true if reachable
    selected of d       -- true if in current devices
    sound volume of d   -- 0-100
end tell
```

## String Escaping

Always escape user input:
```python
def escape_applescript(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

safe_name = escape_applescript(user_input)
script = f'tell application "Music" to play user playlist "{safe_name}"'
```

## Limitations

- **No catalog access** - only library content
- **macOS only** - no Windows/Linux

---

# MusicKit API

Cross-platform but requires Apple Developer account ($99/year) and token setup.

## Authentication

**Requirements:**
1. Apple Developer account
2. MusicKit key (.p8 file) from [developer portal](https://developer.apple.com/account/resources/authkeys/list)
3. Developer token (JWT, 180 day max)
4. User music token (browser OAuth)

**Generate developer token:**
```python
import jwt, datetime

with open('AuthKey_XXXXXXXXXX.p8') as f:
    private_key = f.read()

token = jwt.encode(
    {
        'iss': 'TEAM_ID',
        'iat': int(datetime.datetime.now().timestamp()),
        'exp': int((datetime.datetime.now() + datetime.timedelta(days=180)).timestamp())
    },
    private_key,
    algorithm='ES256',
    headers={'alg': 'ES256', 'kid': 'KEY_ID'}
)
```

**Get user token:** Browser OAuth to `https://authorize.music.apple.com/woa`

**Headers for all requests:**
```
Authorization: Bearer {developer_token}
Music-User-Token: {user_music_token}
```

**Base URL:** `https://api.music.apple.com/v1`

## Available Endpoints

### Catalog (Public - dev token only)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/catalog/{storefront}/search` | GET | Search songs, albums, artists, playlists |
| `/catalog/{storefront}/songs/{id}` | GET | Song details |
| `/catalog/{storefront}/albums/{id}` | GET | Album details |
| `/catalog/{storefront}/albums/{id}/tracks` | GET | Album tracks |
| `/catalog/{storefront}/artists/{id}` | GET | Artist details |
| `/catalog/{storefront}/artists/{id}/albums` | GET | Artist's albums |
| `/catalog/{storefront}/artists/{id}/songs` | GET | Artist's top songs |
| `/catalog/{storefront}/artists/{id}/related-artists` | GET | Similar artists |
| `/catalog/{storefront}/playlists/{id}` | GET | Playlist details |
| `/catalog/{storefront}/charts` | GET | Top charts |
| `/catalog/{storefront}/genres` | GET | All genres |
| `/catalog/{storefront}/search/suggestions` | GET | Search autocomplete |
| `/catalog/{storefront}/stations/{id}` | GET | Radio station |

### Library (Requires user token)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me/library/songs` | GET | All library songs |
| `/me/library/albums` | GET | All library albums |
| `/me/library/artists` | GET | All library artists |
| `/me/library/playlists` | GET | All library playlists |
| `/me/library/playlists/{id}` | GET | Playlist details |
| `/me/library/playlists/{id}/tracks` | GET | Playlist tracks |
| `/me/library/search` | GET | Search library |
| `/me/library` | POST | Add to library |
| `/catalog/{sf}/songs/{id}/library` | GET | Get library ID from catalog ID |

### Playlist Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me/library/playlists` | POST | Create playlist |
| `/me/library/playlists/{id}/tracks` | POST | Add tracks to playlist |

### Personalization

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me/recommendations` | GET | Personalized recommendations |
| `/me/history/heavy-rotation` | GET | Frequently played |
| `/me/recent/played` | GET | Recently played |
| `/me/recent/added` | GET | Recently added |

### Ratings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me/ratings/songs/{id}` | GET | Get song rating |
| `/me/ratings/songs/{id}` | PUT | Set song rating |
| `/me/ratings/songs/{id}` | DELETE | Remove rating |
| `/me/ratings/albums/{id}` | GET/PUT/DELETE | Album ratings |
| `/me/ratings/playlists/{id}` | GET/PUT/DELETE | Playlist ratings |

### Storefronts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/storefronts` | GET | All storefronts |
| `/storefronts/{id}` | GET | Storefront details |
| `/me/storefront` | GET | User's storefront |

## Common Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `term` | Search query | `term=beatles` |
| `types` | Resource types | `types=songs,albums` |
| `limit` | Results per page (max 25) | `limit=10` |
| `offset` | Pagination offset | `offset=25` |
| `include` | Related resources | `include=artists,albums` |
| `extend` | Additional attributes | `extend=editorialNotes` |
| `l` | Language code | `l=en-US` |

## Search Example

```bash
GET /v1/catalog/us/search?term=wonderwall&types=songs&limit=10

Response:
{
  "results": {
    "songs": {
      "data": [{
        "id": "1234567890",
        "type": "songs",
        "attributes": {
          "name": "Wonderwall",
          "artistName": "Oasis",
          "albumName": "(What's the Story) Morning Glory?",
          "durationInMillis": 258773,
          "releaseDate": "1995-10-02",
          "genreNames": ["Alternative", "Music"]
        }
      }]
    }
  }
}
```

## Library-First Workflow (Complete)

Adding a catalog song to a playlist requires 4 API calls:

```python
import requests

headers = {
    "Authorization": f"Bearer {dev_token}",
    "Music-User-Token": user_token
}

# 1. Search catalog
r = requests.get(
    "https://api.music.apple.com/v1/catalog/us/search",
    headers=headers,
    params={"term": "Wonderwall Oasis", "types": "songs", "limit": 1}
)
catalog_id = r.json()['results']['songs']['data'][0]['id']

# 2. Add to library
requests.post(
    "https://api.music.apple.com/v1/me/library",
    headers=headers,
    params={"ids[songs]": catalog_id}
)

# 3. Get library ID (catalog ID → library ID)
r = requests.get(
    f"https://api.music.apple.com/v1/catalog/us/songs/{catalog_id}/library",
    headers=headers
)
library_id = r.json()['data'][0]['id']

# 4. Add to playlist (library IDs only!)
requests.post(
    f"https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks",
    headers={**headers, "Content-Type": "application/json"},
    json={"data": [{"id": library_id, "type": "library-songs"}]}
)
```

## Create Playlist

```bash
POST /v1/me/library/playlists
Content-Type: application/json

{
  "attributes": {
    "name": "Road Trip",
    "description": "Summer vibes"
  },
  "relationships": {
    "tracks": {
      "data": []
    }
  }
}
```

## Ratings

```bash
# Love a song (value: 1 = love, -1 = dislike)
PUT /v1/me/ratings/songs/{id}
Content-Type: application/json

{"attributes": {"value": 1}}
```

## Limitations

- **No playback control** - API cannot play/pause/skip
- **Playlist editing** - can only modify API-created playlists
- **Token management** - dev tokens expire every 180 days
- **Rate limits** - Apple enforces request limits

---

# Common Mistakes

**❌ Using catalog IDs in playlists:**
```python
# WRONG
json={"data": [{"id": "1234567890", "type": "songs"}]}
```
**Fix:** Add to library first, get library ID, then add.

**❌ Playing catalog songs via AppleScript:**
```applescript
# WRONG
play track id "1234567890"
```
**Fix:** Song must be in library.

**❌ Unescaped AppleScript strings:**
```python
# WRONG
name = "Rock 'n Roll"
script = f'tell application "Music" to play playlist "{name}"'
```
**Fix:** Escape quotes.

**❌ Expired tokens:**
Dev tokens last 180 days max.
**Fix:** Check expiration, handle 401 errors.

---

# The Easy Way: mcp-applemusic

The [mcp-applemusic](https://github.com/epheterson/mcp-applemusic) MCP server handles all this complexity automatically: AppleScript escaping, token management, library-first workflow, ID conversions.

**Install:**
```bash
git clone https://github.com/epheterson/mcp-applemusic.git
cd mcp-applemusic && python3 -m venv venv && source venv/bin/activate
pip install -e .
```

**Configure Claude Desktop:**
```json
{
  "mcpServers": {
    "Apple Music": {
      "command": "/path/to/mcp-applemusic/venv/bin/python",
      "args": ["-m", "applemusic_mcp"]
    }
  }
}
```

On macOS, most features work immediately. For catalog features or Windows/Linux, see the repo README.

| Manual | mcp-applemusic |
|--------|----------------|
| 4 API calls to add song | `playlist(action="add", auto_search=True)` |
| AppleScript escaping | Automatic |
| Token management | Automatic with warnings |
