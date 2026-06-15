---
name: seerr-cli
description: >-
  CLI for the Seerr media request management API. Search movies and TV shows,
  create and manage media requests, manage users, track issues, and administer
  a self-hosted Seerr instance. Use when asked to find, request, or manage media
  content, check what is trending, look up actors or collections, manage users,
  or check system status.
metadata:
  author: electather
  repo: https://github.com/electather/seerr-cli
  install: >-
    Download the latest release archive from
    https://github.com/electather/seerr-cli/releases/latest, verify the
    SHA-256 checksum, and move the binary to a directory on PATH.
    A Docker image is also available at ghcr.io/electather/seerr-cli.
primary_credential: SEERR_API_KEY
env:
  # Core credentials — required for every command.
  - name: SEERR_SERVER
    description: Full URL of your Seerr instance (e.g. https://seerr.example.com)
    required: true
  - name: SEERR_API_KEY
    description: API key for authenticating with the Seerr server (primary credential)
    required: true
  # MCP transport — only relevant when running `seerr-cli mcp serve`.
  - name: SEERR_MCP_TRANSPORT
    description: MCP server transport mode; "stdio" (default) or "http"
    required: false
  - name: SEERR_MCP_ADDR
    description: Listen address for the MCP HTTP server (default ":8811")
    required: false
  - name: SEERR_MCP_AUTH_TOKEN
    description: >-
      Bearer token for MCP HTTP transport clients. When using HTTP transport,
      at least one of SEERR_MCP_AUTH_TOKEN, SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM,
      or SEERR_MCP_NO_AUTH=true must be set. Not used for stdio transport.
    required: false
  - name: SEERR_MCP_NO_AUTH
    description: >-
      Set to "true" to disable all MCP HTTP authentication. Only use in trusted
      environments where the endpoint is access-controlled by other means.
    required: false
  - name: SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM
    description: >-
      Set to "true" to accept the Seerr API key via the api_key query parameter
      in addition to the X-Api-Key header. Useful for clients that cannot send
      custom headers (e.g. claude.ai remote MCP). The MCP endpoint is always
      /mcp; append ?api_key=<key> to authenticate. HTTP transport only.
    required: false
  - name: SEERR_MCP_CORS
    description: Set to "true" to enable CORS headers for browser-based MCP clients (e.g. claude.ai)
    required: false
  - name: SEERR_MCP_TLS_CERT
    description: Path to a TLS certificate file for HTTPS on the MCP HTTP server
    required: false
  - name: SEERR_MCP_TLS_KEY
    description: Path to a TLS private-key file for HTTPS on the MCP HTTP server
    required: false
  - name: SEERR_MCP_LOG_FILE
    description: Path to a log file; required for stdio transport to capture logs without polluting stdout
    required: false
  - name: SEERR_MCP_LOG_LEVEL
    description: Log level for the MCP server; one of debug, info, warn, error (default "info")
    required: false
  - name: SEERR_MCP_LOG_FORMAT
    description: Log output format for the MCP server; "text" (default) or "json"
    required: false
---

# seerr-cli

CLI for interacting with a [Seer](https://github.com/seerr/app) media request management server.

## Installation

Download the latest release archive and checksum file from the [Releases page](https://github.com/electather/seerr-cli/releases/latest), verify, and install:

```bash
# Replace <os> and <arch> with your platform (linux/darwin, amd64/arm64)
curl -fsSL https://github.com/electather/seerr-cli/releases/latest/download/seerr-cli_<version>_<os>_<arch>.tar.gz -o seerr-cli.tar.gz
curl -fsSL https://github.com/electather/seerr-cli/releases/latest/download/seerr-cli_<version>_checksums.txt -o checksums.txt
grep seerr-cli_<version>_<os>_<arch>.tar.gz checksums.txt | sha256sum -c
tar -xzf seerr-cli.tar.gz
sudo mv seerr-cli /usr/local/bin/
```

Supports Linux and macOS (amd64 / arm64).

## Docker

Run the MCP HTTP server in a container next to your Seerr instance:

```bash
# With Bearer token auth
docker run --rm \
  -e SEERR_SERVER=http://your-seerr-instance:5055 \
  -e SEERR_API_KEY=your-api-key \
  -e SEERR_MCP_AUTH_TOKEN=your-secret-token \
  -p 8811:8811 \
  ghcr.io/electather/seerr-cli:latest
```

MCP endpoint: `http://localhost:8811/mcp` — set `Authorization: Bearer your-secret-token` in your MCP client.

For clients that cannot send custom headers (e.g. claude.ai remote MCP), use query parameter transport:

```bash
docker run --rm \
  -e SEERR_SERVER=http://your-seerr-instance:5055 \
  -e SEERR_API_KEY=your-api-key \
  -e SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM=true \
  -e SEERR_MCP_CORS=true \
  -p 8811:8811 \
  ghcr.io/electather/seerr-cli:latest
```

MCP endpoint: `http://localhost:8811/mcp?api_key=your-api-key` — no auth header required.

At least one of `SEERR_MCP_AUTH_TOKEN`, `SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM`, or `SEERR_MCP_NO_AUTH=true` must be set for HTTP transport.

### docker-compose deployment

Use the included `docker-compose.yml` to deploy alongside Seer:

```bash
SEERR_API_KEY=xxx SEERR_MCP_AUTH_TOKEN=secret docker compose up -d
```

The default `SEERR_SERVER` in the compose file points to `http://seer:5055` (the Seerr service name). Override it if your Seerr instance is elsewhere.

### Running CLI commands via Docker

Override the default CMD to run any CLI command:

```bash
docker run --rm \
  -e SEERR_SERVER=http://your-seerr-instance:5055 \
  -e SEERR_API_KEY=your-api-key \
  ghcr.io/electather/seerr-cli:latest \
  status system
```

## Setup

```bash
seerr-cli config set --server https://your-seerr-instance.com --api-key YOUR_KEY
seerr-cli config show   # verify
```

Environment variables also work: `SEERR_SERVER`, `SEERR_API_KEY`.

## Global Flags

- `-s, --server` — Seerr server URL
- `-k, --api-key` — API key
- `-v, --verbose` — show request URLs and HTTP status codes
- `--config` — path to config file (default `~/.seerr-cli.yaml`)

## Output

All commands return JSON. Pipe to `jq` for filtering. With `--verbose`, extra info (URL, HTTP status) is printed before the JSON.

## Commands

### Search & Discovery

Find movies, TV shows, and people:

```bash
seerr-cli search multi -q "The Matrix"              # search everything
seerr-cli search multi -q "Nolan" --page 2           # paginated results
seerr-cli search keyword -q "sci-fi"                 # TMDB keywords
seerr-cli search company -q "A24"                    # production companies
seerr-cli search trending                            # currently trending
seerr-cli search trending --time-window week          # weekly trending
seerr-cli search movies --genre 28                   # discover by genre
seerr-cli search movies --studio 7505                # by studio
seerr-cli search movies --sort-by popularity.desc    # custom sort
seerr-cli search tv --genre 18 --network 213         # TV by genre + network
```

Search results include a `mediaType` field (`movie`, `tv`, or `person`) and a TMDB `id` used by other commands.

If `mediaInfo` exists on a result, it's already tracked. `mediaInfo.status` values: 1=unknown, 2=pending, 3=processing, 4=partially available, 5=available.

### Movie Details

```bash
seerr-cli movies get 157336                  # details by TMDB ID
seerr-cli movies ratings 157336              # ratings
seerr-cli movies ratings-combined 157336     # combined RT/IMDB ratings
seerr-cli movies recommendations 157336      # recommended movies
seerr-cli movies similar 157336              # similar movies
```

### TV Show Details

```bash
seerr-cli tv get 72844                       # show details
seerr-cli tv ratings 72844                   # ratings
seerr-cli tv recommendations 72844           # recommendations
seerr-cli tv similar 72844                   # similar shows
seerr-cli tv season 72844 1                  # season details + episodes
```

### Requesting Media

Create requests for movies or TV shows using their TMDB ID:

```bash
# Request a movie
seerr-cli request create --media-type movie --media-id 157336

# Request a TV show (all seasons)
seerr-cli request create --media-type tv --media-id 72844 --seasons all

# Request specific seasons
seerr-cli request create --media-type tv --media-id 72844 --seasons 1,2

# Request 4K version
seerr-cli request create --media-type movie --media-id 157336 --is4k
```

Manage existing requests:

```bash
seerr-cli request list                       # list all requests
seerr-cli request get 5                      # get specific request
seerr-cli request count                      # counts by status
seerr-cli request approve 5                  # approve
seerr-cli request decline 5                  # decline
seerr-cli request retry 5                    # retry failed request
seerr-cli request delete 5                   # delete
```

### Media Management

```bash
seerr-cli media list                         # list all tracked media
seerr-cli media status 1 available           # update status
seerr-cli media watch-data 1                 # get watch data
seerr-cli media delete 1                     # remove from Seer
seerr-cli media delete-file 1                # delete file from Radarr/Sonarr
```

### Issues

Report and track problems with media:

```bash
seerr-cli issue list                         # list all issues
seerr-cli issue create                       # create new issue
seerr-cli issue get 3                        # get issue details
seerr-cli issue count                        # issue counts
seerr-cli issue comment 3                    # add comment
seerr-cli issue update-status 3 resolved     # resolve issue
seerr-cli issue delete 3                     # delete issue
```

### Watchlist

```bash
seerr-cli watchlist add --media-type movie --tmdb-id 157336
seerr-cli watchlist add --media-type tv --tmdb-id 72844
seerr-cli watchlist delete 1                 # remove by watchlist ID
```

### Blocklist

Prevent media from appearing in discovery:

```bash
seerr-cli blocklist list                     # list blocked items
seerr-cli blocklist get 157336               # get by TMDB ID
seerr-cli blocklist add --tmdb-id 157336     # add to blocklist
seerr-cli blocklist delete 1                 # remove by ID
```

### People

```bash
seerr-cli person get 525                     # person details
seerr-cli person combined-credits 525        # all movie + TV credits
```

### Collections

```bash
seerr-cli collection get 2344               # collection details (e.g., a film series)
```

### Users

```bash
seerr-cli users list                         # list all users
seerr-cli users get 1                        # user details
seerr-cli users create                       # create user
seerr-cli users update 1                     # update user
seerr-cli users delete 1                     # delete user
seerr-cli users requests 1                   # user's requests
seerr-cli users watchlist 1                  # user's watchlist
seerr-cli users watch-data 1                 # user's watch data
seerr-cli users quota 1                      # user's request quota
seerr-cli users import-from-plex             # import Plex users
seerr-cli users import-from-jellyfin         # import Jellyfin users
seerr-cli users bulk-update                  # bulk permission update
seerr-cli users settings get 1               # get user settings
seerr-cli users password reset 1             # reset password
```

### Services (Radarr / Sonarr)

```bash
seerr-cli service radarr-list                # list Radarr servers
seerr-cli service radarr-get 1               # profiles + root folders
seerr-cli service sonarr-list                # list Sonarr servers
seerr-cli service sonarr-get 1               # profiles + root folders
seerr-cli service sonarr-lookup 72844        # look up series in Sonarr
```

### TMDB Metadata

```bash
seerr-cli tmdb genres-movie                  # movie genre IDs
seerr-cli tmdb genres-tv                     # TV genre IDs
seerr-cli tmdb languages                     # supported languages
seerr-cli tmdb regions                       # supported regions
seerr-cli tmdb network 213                   # network details (e.g., Netflix)
seerr-cli tmdb studio 7505                   # studio details
seerr-cli tmdb backdrops                     # trending backdrops
```

### Other Lookups

```bash
seerr-cli other certifications-movie         # movie age ratings by country
seerr-cli other certifications-tv            # TV age ratings by country
seerr-cli other keyword 180547               # keyword details
seerr-cli other watchprovider-regions        # available streaming regions
seerr-cli other watchproviders-movies        # movie streaming providers
seerr-cli other watchproviders-tv            # TV streaming providers
```

### Override Rules

Custom rules for request routing:

```bash
seerr-cli overriderule list                  # list rules
seerr-cli overriderule create                # create rule
seerr-cli overriderule update 1              # update rule
seerr-cli overriderule delete 1              # delete rule
```

### System Status

```bash
seerr-cli status system                      # server version + status
seerr-cli status appdata                     # app data volume info
```

## MCP Server

`seerr-cli mcp serve` starts a Model Context Protocol server that exposes the Seerr API as tools. This lets AI agents (including Claude Desktop) use seerr-cli without invoking the CLI directly.

### stdio transport (Claude Desktop)

Claude Desktop spawns the process and communicates over stdin/stdout. No authentication or network configuration required.

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "seer": {
      "command": "/usr/local/bin/seerr-cli",
      "args": ["mcp", "serve"],
      "env": {
        "SEERR_SERVER": "https://your-seerr-instance.com",
        "SEERR_API_KEY": "your-api-key"
      }
    }
  }
}
```

### HTTP transport

For MCP clients that connect over HTTP with Bearer token auth:

```bash
seerr-cli mcp serve --transport http --addr :8811 --auth-token mysecrettoken
```

Endpoint: `http://localhost:8811/mcp` — set `Authorization: Bearer mysecrettoken` in your client.

For clients that cannot send custom headers (e.g. claude.ai remote MCP), use `--allow-api-key-query-param` (or `SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM`):

```bash
# Add --cors if connecting from a browser-based client (e.g. claude.ai)
seerr-cli mcp serve --transport http --addr :8811 --allow-api-key-query-param --cors
# Endpoint: http://localhost:8811/mcp?api_key=YOUR_SEERR_API_KEY
```

All flags are configurable via environment variables:

| Flag                          | Environment variable                  | Default |
| ----------------------------- | ------------------------------------- | ------- |
| `--transport`                 | `SEERR_MCP_TRANSPORT`                 | `stdio` |
| `--addr`                      | `SEERR_MCP_ADDR`                      | `:8811` |
| `--auth-token`                | `SEERR_MCP_AUTH_TOKEN`                | —       |
| `--no-auth`                   | `SEERR_MCP_NO_AUTH`                   | `false` |
| `--allow-api-key-query-param` | `SEERR_MCP_ALLOW_API_KEY_QUERY_PARAM` | `false` |
| `--cors`                      | `SEERR_MCP_CORS`                      | `false` |
| `--tls-cert`                  | `SEERR_MCP_TLS_CERT`                  | —       |
| `--tls-key`                   | `SEERR_MCP_TLS_KEY`                   | —       |

> Pass `--cors` (or `SEERR_MCP_CORS=true`) to enable CORS headers for browser-based clients (e.g. claude.ai). Disabled by default.

> The HTTP transport does not implement OAuth 2.0. Use stdio for Claude Desktop.

### MCP tools available

| Category              | Tools                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Search                | `search_multi`, `search_discover_movies`, `search_discover_tv`, `search_trending`                                        |
| Movies                | `movies_get`, `movies_recommendations`, `movies_similar`, `movies_ratings`                                               |
| TV                    | `tv_get`, `tv_season`, `tv_recommendations`, `tv_similar`, `tv_ratings`                                                  |
| Requests              | `request_list`, `request_get`, `request_create`, `request_approve`, `request_decline`, `request_delete`, `request_count` |
| Media                 | `media_list`, `media_status_update`                                                                                      |
| Issues                | `issue_list`, `issue_get`, `issue_create`, `issue_status_update`, `issue_count`                                          |
| Users                 | `users_list`, `users_get`, `users_quota`                                                                                 |
| People & Collections  | `person_get`, `person_credits`, `collection_get`                                                                         |
| Services              | `service_radarr_list`, `service_sonarr_list`                                                                             |
| Settings              | `settings_about`, `settings_jobs_list`, `settings_jobs_run`                                                              |
| Watchlist & Blocklist | `watchlist_add`, `watchlist_remove`, `blocklist_list`, `blocklist_add`, `blocklist_remove`                               |
| System                | `status_system`                                                                                                          |

## Common Workflows

### Find and request a movie

```bash
seerr-cli search multi -q "Interstellar"     # find TMDB ID
seerr-cli movies get 157336                  # confirm details
seerr-cli request create --media-type movie --media-id 157336
```

### Find and request a TV show

```bash
seerr-cli search multi -q "Breaking Bad"    # find TMDB ID
seerr-cli tv get 1396                        # confirm details
seerr-cli request create --media-type tv --media-id 1396 --seasons all
```

### Check what genre IDs mean

```bash
seerr-cli tmdb genres-movie                  # e.g., 28=Action, 18=Drama
seerr-cli tmdb genres-tv
```
