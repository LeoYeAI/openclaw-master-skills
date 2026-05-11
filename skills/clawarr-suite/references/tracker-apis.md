# Media Tracker API Reference

## Trakt.tv API

**Base URL:** `https://api.trakt.tv`
**API Version:** 2
**Authentication:** OAuth 2.0 (device code flow)
**Rate Limits:** 1000 requests per 5 minutes (generous)

### Authentication Flow

1. **Generate Device Code**
   - POST `/oauth/device/code`
   - Body: `{"client_id": "YOUR_CLIENT_ID"}`
   - Returns: `device_code`, `user_code`, `verification_url`

2. **User Authorization**
   - User visits `verification_url` and enters `user_code`

3. **Poll for Token**
   - POST `/oauth/device/token`
   - Body: `{"code": "DEVICE_CODE", "client_id": "...", "client_secret": "..."}`
   - Returns: `access_token`, `refresh_token`, `expires_in`

4. **Refresh Token**
   - POST `/oauth/token`
   - Body: `{"refresh_token": "...", "client_id": "...", "client_secret": "...", "grant_type": "refresh_token"}`

### Common Endpoints

**User Profile & Stats:**
- GET `/users/settings` - Current user settings (authenticated)
- GET `/users/{username}` - Public user profile
- GET `/users/{username}/stats` - User statistics

**History & Watching:**
- GET `/users/me/watching` - Currently watching
- GET `/users/me/history` - Watch history (supports filtering by type)
- GET `/users/me/history/movies?limit=20` - Movie history
- GET `/users/me/history/shows?limit=20` - Show history

**Scrobbling:**
- POST `/scrobble/start` - Start watching
- POST `/scrobble/pause` - Pause playback
- POST `/scrobble/stop` - Finish watching
- Body: `{"movie": {"ids": {"trakt": 123}}, "progress": 75}`

**Check-in:**
- POST `/checkin` - Check in to something
- Body: `{"movie": {"ids": {"trakt": 123}}}`

**Lists:**
- GET `/users/me/watchlist` - Watchlist
- GET `/users/me/collection` - Collection
- POST `/sync/watchlist` - Add to watchlist
- POST `/sync/collection` - Add to collection
- Body: `{"movies": [{"ids": {"trakt": 123}}]}`

**Ratings:**
- GET `/users/me/ratings` - All ratings
- GET `/users/me/ratings/movies` - Movie ratings
- POST `/sync/ratings` - Add ratings
- Body: `{"movies": [{"ids": {"trakt": 123}, "rating": 8}]}`

**Discovery:**
- GET `/recommendations/movies?limit=20` - Personalized recommendations
- GET `/movies/trending?limit=20` - Trending movies
- GET `/movies/popular?limit=20` - Popular movies
- GET `/calendars/my/movies/{start_date}/{days}` - Movie calendar

**Search:**
- GET `/search/movie?query=inception&year=2010` - Search movies
- GET `/search/show?query=breaking+bad` - Search shows

**Sync:**
- POST `/sync/history` - Add watch history
- Body: `{"movies": [{"ids": {"trakt": 123}, "watched_at": "2024-01-01T12:00:00.000Z"}]}`

### Headers Required

```
Content-Type: application/json
Authorization: Bearer {access_token}
trakt-api-version: 2
trakt-api-key: {client_id}
```

### ID Types Supported

- `trakt` - Trakt ID (integer)
- `imdb` - IMDb ID (tt#######)
- `tmdb` - TMDb ID
- `slug` - Trakt slug (url-friendly-title)

## Simkl API

**Base URL:** `https://api.simkl.com`
**Authentication:** OAuth 2.0 (authorization code flow)
**Rate Limits:** Varies by endpoint

### Authentication Flow

1. **Generate Authorization URL**
   - User visits: `https://simkl.com/oauth/authorize?response_type=code&client_id=...&redirect_uri=...`

2. **Exchange Code for Token**
   - POST `/oauth/token`
   - Body: `{"code": "...", "client_id": "...", "client_secret": "...", "grant_type": "authorization_code"}`

### Common Endpoints

**User:**
- GET `/users/settings` - Current user settings

**History:**
- GET `/sync/all-items/movies/watched` - Watched movies
- GET `/sync/all-items/shows/watched` - Watched shows
- GET `/sync/all-items/anime/watched` - Watched anime

**Watchlist:**
- GET `/sync/watchlist/movies` - Movie watchlist
- GET `/sync/watchlist/shows` - Show watchlist

**Sync:**
- POST `/sync/history` - Add watch history
- POST `/sync/watched` - Mark as watched

### Headers Required

```
Content-Type: application/json
Authorization: Bearer {access_token}
simkl-api-key: {client_id}
```

## Letterboxd API

**Base URL:** `https://api.letterboxd.com/api/v0`
**Authentication:** OAuth 2.0 (requires API application approval)
**Status:** Requires approved API access

### CSV Import/Export Format

Letterboxd supports CSV import/export for diary entries:

**CSV Header:**
```
Date,Letterboxd URI,Name,Year,Directors,Rating,Rewatch,Tags,Watched Date
```

**Example Row:**
```
2024-01-15,,Inception,2010,Christopher Nolan,5,No,mind-bending,2024-01-15
```

**Rating Scale:** 0.5 to 5 stars (in 0.5 increments)

### Public Profile Scraping

Public profiles are accessible at:
- `https://letterboxd.com/{username}/`
- `https://letterboxd.com/{username}/films/diary/`

Note: Web scraping is fragile and subject to change. Official API preferred.

## TV Time

**Status:** No public API available

### Export Format

TV Time provides CSV export at:
- `https://www.tvtime.com/export`

Export contains:
- Show name
- Episode watched
- Date watched

## Plex + Tautulli Integration

### Tautulli History Endpoint

**Get Watch History:**
```
GET http://{host}:8181/api/v2?apikey={key}&cmd=get_history&length=500
```

Returns:
```json
{
  "response": {
    "data": {
      "data": [
        {
          "date": 1704470400,
          "full_title": "Inception (2010)",
          "media_type": "movie",
          "watched_status": 1,
          "year": 2010,
          "title": "Inception"
        }
      ]
    }
  }
}
```

### Mapping Strategy

**Movies:**
1. Extract title + year from Tautulli
2. Search Trakt/Simkl by title + year
3. Match best result
4. Sync using matched ID

**TV Shows:**
1. Extract show title + season + episode
2. Search tracker by show title
3. Match episode by season/episode number
4. Sync episode watch status

### Rate Limiting Best Practices

When syncing large libraries:
- Batch API calls where possible
- Add 0.5-1 second delay between searches
- Cache matched IDs to avoid re-searching
- Use bulk sync endpoints when available

## Error Handling

### Common HTTP Status Codes

- **200** - Success
- **201** - Created
- **204** - Success (no content)
- **400** - Bad request (invalid data)
- **401** - Unauthorized (invalid/expired token)
- **404** - Not found
- **409** - Conflict (already exists)
- **420** - Account limit exceeded
- **422** - Validation error
- **429** - Rate limit exceeded
- **500** - Server error
- **502** - Bad gateway
- **503** - Service unavailable

### Retry Strategy

1. **401 Unauthorized** - Refresh token, retry once
2. **429 Rate Limit** - Wait and exponentially backoff
3. **5xx Server Error** - Retry with backoff (max 3 attempts)
4. **Other errors** - Report and skip item

## Best Practices

### Token Management

- Store tokens in `~/.config/clawarr/` with 600 permissions
- Auto-refresh tokens before expiry
- Include created_at and expires_at timestamps

### ID Caching

For sync operations, maintain a local cache:
```json
{
  "inception_2010": {
    "trakt": 16662,
    "simkl": 5,
    "tmdb": 27205,
    "imdb": "tt1375666"
  }
}
```

### Sync State

Track last sync time to avoid re-syncing:
```json
{
  "last_sync": {
    "plex_to_trakt": 1704470400,
    "trakt_to_letterboxd": 1704380400
  }
}
```

### Rate Limit Compliance

- Respect `X-RateLimit-*` headers
- Implement exponential backoff
- Use bulk endpoints for large operations
- Cache results where possible

## Testing Endpoints

### Public Test Endpoints (no auth required)

**Trakt:**
- GET `/movies/trending?limit=5`
- GET `/search/movie?query=inception`

**Simkl:**
- Requires API key but no user auth for search

### Development Tips

1. Use `curl -v` to inspect headers
2. Save sample responses for offline testing
3. Test with small datasets first
4. Validate JSON payloads before sending
5. Log all API errors for debugging
