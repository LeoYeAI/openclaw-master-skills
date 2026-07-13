# Resy API Reference (Reverse-Engineered)

Resy has no official public API. All endpoints below are reverse-engineered from network traffic.

## Base URL

`https://api.resy.com`

## Authentication Headers

Every request requires:

```
Authorization: ResyAPI api_key="YOUR_RESY_API_KEY"
x-resy-auth-token: YOUR_RESY_AUTH_TOKEN
Accept: application/json
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
```

### How to Get the API Key

The API key is static and never expires. Extract it once:
1. Log into resy.com in a browser
2. Open Developer Tools → Network tab
3. Find any request to `api.resy.com`
4. `Authorization` header → the part after `ResyAPI api_key=` is the API key

### Token Management

Auth tokens are fetched automatically via `resy-auth.sh` using your email/password. Tokens are cached for 12 hours. On HTTP 419, the script automatically re-authenticates.

## Endpoints

### POST /3/auth/password — Login

Authenticate with email and password to obtain an auth token.

**Content-Type:** `application/x-www-form-urlencoded`

**Headers:**
```
Authorization: ResyAPI api_key="YOUR_RESY_API_KEY"
```

**Body (form-encoded):**
| Param | Type | Description |
|-------|------|-------------|
| `email` | string | Resy account email |
| `password` | string | Resy account password |

**Response:**
```json
{
  "token": "eyJhb...",
  "payment_methods": [
    { "id": 12345 }
  ]
}
```

The `token` value is used as the `x-resy-auth-token` header in subsequent requests.

### POST /4/find — Search Availability

Query available reservation slots for a venue.

**Content-Type:** `application/json`

**Request body:**
| Field | Type | Description |
|-------|------|-------------|
| `venue_id` | int | Restaurant identifier |
| `day` | string | Date in YYYY-MM-DD format |
| `party_size` | int | Number of guests |
| `lat` | float | Latitude (use 0 when venue_id is provided) |
| `long` | float | Longitude (use 0 when venue_id is provided) |

**Example request body:**
```json
{"lat": 0, "long": 0, "day": "2026-03-06", "party_size": 2, "venue_id": 6194}
```

**Response shape:**
```json
{
  "results": {
    "venues": [
      {
        "venue": {
          "id": { "resy": 5286 },
          "name": "Carbone",
          "slug": "carbone",
          "location": { "city": "New York", "neighborhood": "Greenwich Village" }
        },
        "slots": [
          {
            "date": { "start": "2026-03-15 19:30:00", "end": "2026-03-15 21:30:00" },
            "config": { "type": "Dining Room", "token": "..." }
          }
        ]
      }
    ]
  }
}
```

### GET /3/venuesearch/search — Search Venues

Search for restaurants by name.

**Parameters (query string):**
| Param | Type | Description |
|-------|------|-------------|
| `query` | string | Search term |
| `geo.lat` | float | Latitude |
| `geo.long` | float | Longitude |
| `per_page` | int | Results per page |
| `types` | string | Filter type (use `venue`) |

**Response shape:**
```json
{
  "search": {
    "hits": [
      {
        "id": { "resy": 5286 },
        "name": "Carbone",
        "url_slug": "carbone",
        "location": { "city": "New York" }
      }
    ]
  }
}
```

## Booking URLs

Direct link format: `https://resy.com/cities/<city>/<slug>?date=<YYYY-MM-DD>&seats=<party_size>`

Example: `https://resy.com/cities/ny/carbone?date=2026-03-15&seats=2`
