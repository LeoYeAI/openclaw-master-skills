---
name: ubtrippin
version: 2.0.0
description: Manages travel for your user via UBTRIPPIN — trips, items, loyalty programs, family, city guides, events, concerts, notifications, and more. Use when the user asks about their trips, upcoming travel, flights, hotels, train bookings, concert tickets, event tickets, loyalty numbers, family travel, or wants to manage their travel tracker. Requires a UBTRIPPIN API key from ubtrippin.xyz/settings.
---

# UBTRIPPIN Skill

**UBTRIPPIN** is a personal travel tracker that parses booking confirmation emails and organises them into trips. It also handles event tickets — concerts, theater, sports, festivals — from providers like Ticketmaster, AXS, Eventbrite, and more. As an agent, you can read and manage a user's trips, items (flights, hotels, trains, tickets/events, etc.), loyalty vault, family groups, city guides, and more via REST API.

---

## Setup (First Time)

1. Ask your user to visit **ubtrippin.xyz/settings** and generate an API key.
2. The key looks like: `ubt_k1_<40 hex chars>`. Store it securely.
3. Ask for their **registered sender email** — the email address they use to forward bookings (typically their personal inbox). This is their "allowed sender" in UBTRIPPIN.
4. You'll need both to operate: the API key for reads/writes, the email address for adding new bookings via forwarding.
5. After setup, call `GET /api/v1/me/profile` and offer to set the user's home airport, currency preference, and seat preference via `PATCH /api/v1/me/profile`.

---

## Authentication

All API calls use a Bearer token:

```
Authorization: Bearer ubt_k1_<your_key>
```

Base URL: `https://www.ubtrippin.xyz`

**Rate limit:** 100 requests/minute per API key. HTTP 429 if exceeded — back off 60 seconds.

---

## API Endpoints

### Trips

#### List All Trips
```
GET /api/v1/trips
```

Query params: `?status=upcoming` (optional filter)

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Tokyo Spring 2026",
      "start_date": "2026-04-01",
      "end_date": "2026-04-14",
      "primary_location": "Tokyo, Japan",
      "travelers": ["Ian Rogers"],
      "notes": null,
      "cover_image_url": "https://...",
      "share_enabled": false,
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-15T10:00:00Z"
    }
  ],
  "meta": { "count": 1 }
}
```

Ordered by start_date descending (soonest upcoming / most recent first).

#### Get Trip with All Items
```
GET /api/v1/trips/:id
```

Response includes full trip object with nested `items` array. Each item has: `id`, `trip_id`, `kind`, `provider`, `traveler_names`, `start_ts`, `end_ts`, `start_date`, `end_date`, `start_location`, `end_location`, `summary`, `details_json`, `status`, `confidence`, `needs_review`, timestamps.

**Item kinds:** `flight`, `hotel`, `train`, `car`, `ferry`, `activity`, `ticket`, `other`

#### Create Trip
```
POST /api/v1/trips
Content-Type: application/json

{ "title": "Summer in Provence", "start_date": "2026-07-01", "end_date": "2026-07-14" }
```

#### Update Trip
```
PATCH /api/v1/trips/:id
Content-Type: application/json

{ "title": "Updated Title", "notes": "Remember sunscreen" }
```

#### Delete Trip
```
DELETE /api/v1/trips/:id
```

#### Rename Trip
```
POST /api/v1/trips/:id/rename
Content-Type: application/json

{ "title": "New Trip Name" }
```

#### Merge Trips
```
POST /api/v1/trips/:id/merge
Content-Type: application/json

{ "source_trip_id": "uuid-of-trip-to-merge-in" }
```

Merges items from the source trip into the target trip.

#### Trip Status
```
GET /api/v1/trips/:id/status
```

Returns processing status for the trip.

#### Demo Trip
```
GET /api/v1/trips/demo
```

Returns a sample trip for onboarding — no auth required.

---

### Items

#### Get Single Item
```
GET /api/v1/items/:id
```

Response: `{ "data": <item> }` — full Item shape with `details_json` containing confirmation numbers, seat assignments, etc.

#### Update Item
```
PATCH /api/v1/items/:id
Content-Type: application/json

{ "summary": "Updated summary", "start_location": "Paris CDG" }
```

#### Delete Item
```
DELETE /api/v1/items/:id
```

#### Add Item to Trip
```
POST /api/v1/trips/:id/items
Content-Type: application/json
```

**Required fields:** `kind`, `start_date`

**All fields:**

| Field | Type | Description |
|-------|------|-------------|
| `kind` | string | **Required.** One of: `flight`, `hotel`, `car_rental`, `train`, `activity`, `restaurant`, `ticket`, `other` |
| `start_date` | string | **Required.** ISO date: `YYYY-MM-DD` |
| `end_date` | string | ISO date. For hotels = checkout, flights = arrival date if different |
| `start_ts` | string | ISO 8601 datetime with timezone: `2026-04-01T08:30:00Z` |
| `end_ts` | string | ISO 8601 datetime with timezone |
| `start_location` | string | Departure/origin. City, airport code, or address (max 300 chars) |
| `end_location` | string | Arrival/destination (max 300 chars) |
| `summary` | string | One-line summary, e.g. "AF276 CDG→NRT" (max 1000 chars) |
| `provider` | string | Airline, hotel chain, etc. e.g. "Air France" (max 200 chars) |
| `confirmation_code` | string | Booking reference (max 200 chars) |
| `traveler_names` | string[] | Array of traveler names (max 20, each max 200 chars) |
| `details_json` | object | Freeform metadata — gate, seat, room type, etc. (max 10KB) |
| `notes` | string | User notes |
| `status` | string | Item status |

**Example — Flight:**
```json
{
  "kind": "flight",
  "start_date": "2026-04-01",
  "start_ts": "2026-04-01T08:30:00+01:00",
  "end_ts": "2026-04-01T15:45:00+09:00",
  "start_location": "Paris CDG",
  "end_location": "Tokyo NRT",
  "summary": "AF276 CDG→NRT",
  "provider": "Air France",
  "confirmation_code": "XK7J3M",
  "traveler_names": ["Ian Rogers"],
  "details_json": { "flight_number": "AF276", "seat": "14A", "class": "Economy" }
}
```

**Example — Hotel:**
```json
{
  "kind": "hotel",
  "start_date": "2026-04-01",
  "end_date": "2026-04-05",
  "start_location": "Tokyo, Japan",
  "summary": "Park Hyatt Tokyo",
  "provider": "Hyatt",
  "confirmation_code": "HY-889923",
  "traveler_names": ["Ian Rogers", "Hedvig Rogers"],
  "details_json": { "room_type": "King Deluxe", "check_in": "15:00", "check_out": "11:00" }
}
```

**Example — Train:**
```json
{
  "kind": "train",
  "start_date": "2026-04-05",
  "start_ts": "2026-04-05T09:00:00+09:00",
  "end_ts": "2026-04-05T11:30:00+09:00",
  "start_location": "Tokyo Station",
  "end_location": "Kyoto Station",
  "summary": "Shinkansen Nozomi 7",
  "provider": "JR Central",
  "confirmation_code": "JR-44521",
  "details_json": { "car": "7", "seat": "3A", "class": "Green Car" }
}
```

**Example — Restaurant:**
```json
{
  "kind": "restaurant",
  "start_date": "2026-04-03",
  "start_ts": "2026-04-03T19:00:00+09:00",
  "start_location": "Sukiyabashi Jiro, Ginza, Tokyo",
  "summary": "Dinner at Sukiyabashi Jiro",
  "details_json": { "party_size": 2, "reservation_name": "Rogers" }
}
```

**Example — Ticket/Event (concert, sports, theater, festival, etc.):**
```json
{
  "kind": "ticket",
  "summary": "David Byrne at Théâtre du Châtelet",
  "start_date": "2026-05-15",
  "start_ts": "2026-05-15T20:00:00+02:00",
  "start_location": "Paris",
  "provider": "Ticketmaster",
  "details_json": {
    "event_name": "David Byrne: American Utopia",
    "venue": "Théâtre du Châtelet",
    "venue_address": "1 Place du Châtelet, 75001 Paris",
    "performer": "David Byrne",
    "event_time": "20:00",
    "door_time": "19:00",
    "section": "Orchestre",
    "seat": "12",
    "row": "G",
    "ticket_count": 2,
    "ticket_type": "Reserved",
    "event_category": "concert"
  }
}
```

**Ticket detail fields:**
| Field | Type | Description |
|-------|------|-------------|
| event_name | string | Name of the event/show |
| venue | string | Venue name |
| venue_address | string? | Full address |
| event_time | HH:MM | Show start time |
| door_time | HH:MM? | Door opening time |
| section | string? | Seating section |
| seat | string? | Seat number |
| row | string? | Row identifier |
| ticket_count | number | Number of tickets |
| ticket_type | string? | GA, Reserved, VIP, etc. |
| performer | string? | Artist/performer/team |
| event_category | enum | concert, theater, sports, museum, festival, other |

**Supported ticket providers:** Ticketmaster, AXS, Eventbrite, Dice, SeeTickets, StubHub, Viagogo, venue direct sales. Forward the confirmation email to trips@ubtrippin.xyz and the ticket is extracted automatically.

**Event-driven trips:** When a ticket email creates a new trip (no overlapping dates), the trip is named after the event/performer and the cover image is of the performer — not the city.

#### Batch Add Items
```
POST /api/v1/trips/:id/items/batch
Content-Type: application/json

{ "items": [ <item>, <item>, ... ] }
```

Up to 50 items per request. Same fields as single item creation above.

Response: `{ "data": [...items], "meta": { "count": N } }`

**Tip for agents:** When your user gives you a booking confirmation (email text, screenshot, pasted text), parse it yourself and use these endpoints to add structured items. You handle the extraction; UBTRIPPIN handles the storage, grouping, and display.

#### Item Status
```
GET /api/v1/items/:id/status
```

#### Refresh Item Status
```
POST /api/v1/items/:id/status/refresh
```

Re-checks live status (e.g. flight delays, gate changes).

---

### Loyalty Vault

#### List My Loyalty Programs
```
GET /api/v1/me/loyalty
```

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "provider_key": "delta_skymiles",
      "provider_name": "Delta SkyMiles",
      "member_number": "1234567890",
      "tier": "Gold",
      "notes": null
    }
  ]
}
```

#### Lookup by Provider
```
GET /api/v1/me/loyalty/lookup?provider_key=delta_skymiles
```

Returns matching loyalty entry for a specific provider.

#### Add Loyalty Program
```
POST /api/v1/me/loyalty
Content-Type: application/json

{ "provider_key": "delta_skymiles", "member_number": "1234567890", "tier": "Gold" }
```

#### Update Loyalty Program
```
PATCH /api/v1/me/loyalty/:id
Content-Type: application/json

{ "member_number": "9876543210", "tier": "Platinum" }
```

#### Delete Loyalty Program
```
DELETE /api/v1/me/loyalty/:id
```

#### Export Loyalty Data
```
GET /api/v1/me/loyalty/export
```

Returns all loyalty data in a downloadable format.

#### List Known Providers
```
GET /api/v1/loyalty/providers
```

Returns the full list of supported loyalty providers (no auth required).

---

### Profile

#### Get My Profile
```
GET /api/v1/me/profile
```

Response includes name, email, preferences, tier, and settings.

#### Update My Profile
```
PUT /api/v1/me/profile
Content-Type: application/json

{ "display_name": "Ian Rogers", "timezone": "Europe/Paris" }
```

Also accepts `POST` with the same body.

---

### Family

#### List My Families
```
GET /api/v1/families
```

#### Create Family
```
POST /api/v1/families
Content-Type: application/json

{ "name": "The Rogers Family" }
```

#### Get Family
```
GET /api/v1/families/:id
```

#### Update Family
```
PATCH /api/v1/families/:id
Content-Type: application/json

{ "name": "Updated Family Name" }
```

#### Delete Family
```
DELETE /api/v1/families/:id
```

#### Invite Member to Family
```
POST /api/v1/families/:id/members
Content-Type: application/json

{ "email": "partner@example.com", "role": "member" }
```

#### Remove Family Member
```
DELETE /api/v1/families/:id/members/:uid
```

#### Family Member Profiles
```
GET /api/v1/families/:id/profiles
```

#### Family Trips
```
GET /api/v1/families/:id/trips
```

Returns all trips visible to family members.

#### Family Loyalty Programs
```
GET /api/v1/families/:id/loyalty
```

#### Family Loyalty Lookup
```
GET /api/v1/families/:id/loyalty/lookup?provider_key=delta_skymiles
```

Look up a loyalty number across all family members.

#### Family City Guides
```
GET /api/v1/families/:id/guides
```

#### Family Invites
```
GET /api/v1/family-invites/:token
POST /api/v1/family-invites/:token/accept
```

View and accept family invite links.

---

### Collaborators (Trip Sharing)

#### List Collaborators
```
GET /api/v1/trips/:id/collaborators
```

#### Invite Collaborator
```
POST /api/v1/trips/:id/collaborators
Content-Type: application/json

{ "email": "friend@example.com", "role": "viewer" }
```

#### Update Collaborator Role
```
PATCH /api/v1/trips/:id/collaborators/:uid
Content-Type: application/json

{ "role": "editor" }
```

#### Remove Collaborator
```
DELETE /api/v1/trips/:id/collaborators/:uid
```

#### Trip Invites
```
GET /api/v1/invites/:token
POST /api/v1/invites/:token/accept
```

View and accept trip collaboration invite links.

---

### City Guides

#### List Guides
```
GET /api/v1/guides
```

Query params: `?family_id=uuid` (optional)

#### Create Guide
```
POST /api/v1/guides
Content-Type: application/json

{ "city": "Tokyo", "title": "Tokyo Eats" }
```

#### Get Guide
```
GET /api/v1/guides/:id
```

#### Update Guide
```
PATCH /api/v1/guides/:id
```

#### Delete Guide
```
DELETE /api/v1/guides/:id
```

#### List Guide Entries
```
GET /api/v1/guides/:id/entries
```

#### Add Guide Entry
```
POST /api/v1/guides/:id/entries
Content-Type: application/json

{ "name": "Tsukiji Outer Market", "category": "food", "notes": "Go early" }
```

#### Update Guide Entry
```
PATCH /api/v1/guides/:id/entries/:eid
```

#### Delete Guide Entry
```
DELETE /api/v1/guides/:id/entries/:eid
```

#### Nearby Guides
```
GET /api/v1/guides/nearby?lat=35.6762&lng=139.6503
```

Find guides near a location.

---

### Senders (Allowed Email Addresses)

#### List Senders
```
GET /api/v1/settings/senders
```

#### Add Sender
```
POST /api/v1/settings/senders
Content-Type: application/json

{ "email": "mywork@company.com" }
```

#### Remove Sender
```
DELETE /api/v1/settings/senders/:id
```

---

### Calendar

#### Get Calendar Token
```
GET /api/v1/calendar/token
```

Returns an iCal subscription URL for syncing trips to calendar apps.

#### Regenerate Calendar Token
```
POST /api/v1/calendar/token
```

Invalidates the old token and generates a new one.

---

### Notifications

#### List Notifications
```
GET /api/v1/notifications
```

Query params: `?unread=true` (optional)

#### Mark Notification Read
```
PATCH /api/v1/notifications/:id
Content-Type: application/json

{ "read": true }
```

---

### Webhooks

#### List Webhooks
```
GET /api/v1/webhooks
```

#### Create Webhook
```
POST /api/v1/webhooks
Content-Type: application/json

{ "url": "https://example.com/hook", "events": ["trip.created", "item.added"] }
```

#### Get Webhook
```
GET /api/v1/webhooks/:id
```

#### Update Webhook
```
PATCH /api/v1/webhooks/:id
Content-Type: application/json

{ "url": "https://example.com/new-hook", "active": true }
```

#### Delete Webhook
```
DELETE /api/v1/webhooks/:id
```

#### Test Webhook
```
POST /api/v1/webhooks/:id/test
```

Sends a test payload to verify the endpoint.

#### Webhook Deliveries
```
GET /api/v1/webhooks/:id/deliveries
```

Lists recent delivery attempts with status codes.

---

### Trains

#### Train Status
```
GET /api/v1/trains/:trainNumber/status
```

Returns real-time status for a train by number (delays, platform, etc.).

---

### Images

#### Search Images
```
GET /api/v1/images/search?q=tokyo+tower
```

Search for destination/cover images.

---

### Imports

#### List Imports
```
GET /api/v1/imports
```

#### Create Import
```
POST /api/v1/imports
```

Upload booking data for batch import.

#### Get Import
```
GET /api/v1/imports/:id
```

---

### Billing

#### Get Subscription
```
GET /api/v1/billing/subscription
```

Returns current plan, tier, and billing period.

#### Get Billing Portal URL
```
GET /api/v1/billing/portal
```

Returns a Stripe billing portal link for managing subscription.

#### Get Prices
```
GET /api/v1/billing/prices
```

Returns available plans and pricing.

#### Checkout
```
POST /api/v1/checkout
Content-Type: application/json

{ "price_id": "price_xxx" }
```

Creates a Stripe checkout session.

---

### Activation

#### Check Activation Status
```
GET /api/v1/activation/status
```

Returns whether the user's account is activated.

---

## Adding New Bookings (Email Forwarding)

The primary way to add bookings is **email forwarding**. When your user receives a booking confirmation:

1. Forward the email to: **trips@ubtrippin.xyz**
2. **Must forward from their registered sender address** — UBTRIPPIN rejects unknown senders.
3. UBTRIPPIN's AI parser extracts the booking details automatically (usually within 30 seconds).
4. The item appears in the relevant trip (or a new trip is created).

**How to do this as an agent:**
- Use your email sending capability to forward the email from the user's address to trips@ubtrippin.xyz.
- Or instruct the user to do it manually from their inbox.
- PDF attachments (e.g. eTickets) are supported — include them in the forward.

**Works with:** flights, hotels, trains (Eurostar, SNCF, Thalys, etc.), rental cars, ferry bookings, concert/event tickets (Ticketmaster, AXS, Eventbrite, Dice, SeeTickets, StubHub, Viagogo), and most major booking platforms (Booking.com, Expedia, Kayak, Trainline, etc.).

---

## Typical Agent Workflows

### "What trips do I have coming up?"
1. `GET /api/v1/trips`
2. Filter by start_date >= today
3. Format and present

### "What's my itinerary for Tokyo?"
1. `GET /api/v1/trips` — find the Tokyo trip ID
2. `GET /api/v1/trips/:id` — get full itinerary with all items
3. Format chronologically by start_ts

### "I just booked a hotel in Tokyo — add it"
1. Ask the user to forward the confirmation email from their registered address to trips@ubtrippin.xyz
2. Or if you have email access: forward it yourself
3. Wait ~30 seconds, then `GET /api/v1/trips/:id` to confirm it appeared

### "What's my Delta SkyMiles number?"
1. `GET /api/v1/me/loyalty/lookup?provider_key=delta_skymiles`
2. Return the `member_number` from the response

### "Add my Marriott Bonvoy membership"
1. `POST /api/v1/me/loyalty` with `{ "provider_key": "marriott_bonvoy", "member_number": "123456789" }`

### "What loyalty programs does my family have for Delta?"
1. Get the family ID: `GET /api/v1/families`
2. `GET /api/v1/families/:id/loyalty/lookup?provider_key=delta_skymiles`
3. Returns all family members' Delta numbers

### "Add my family members"
1. `POST /api/v1/families` to create a family group (if none exists)
2. `POST /api/v1/families/:id/members` with `{ "email": "partner@example.com" }` for each member
3. They'll receive an invite email to accept

### "Share my trip with a friend"
1. `POST /api/v1/trips/:id/collaborators` with `{ "email": "friend@example.com", "role": "viewer" }`

### "Is my train on time?"
1. `GET /api/v1/trains/:trainNumber/status`
2. Report delays, platform changes, etc.

### "Show me city guides near me"
1. `GET /api/v1/guides/nearby?lat=48.8566&lng=2.3522`

### "Set up a webhook for new bookings"
1. `POST /api/v1/webhooks` with `{ "url": "https://...", "events": ["item.added"] }`

### "Get me a calendar link for my trips"
1. `GET /api/v1/calendar/token`
2. Give the user the iCal URL to add to their calendar app

---

## Error Handling

| Status | Code | Meaning |
|--------|------|---------|
| 401 | `unauthorized` | Missing/invalid API key |
| 400 | `invalid_param` | Bad UUID or missing field |
| 404 | `not_found` | Trip/item not found or belongs to another user |
| 429 | _(body varies)_ | Rate limited — wait 60s |
| 500 | `internal_error` | Server error — retry once |

All errors return: `{ "error": { "code": "...", "message": "..." } }`

---

## Notes for Agents

- All IDs are UUIDs.
- Dates are ISO 8601 (`YYYY-MM-DD` for dates, `YYYY-MM-DDTHH:MM:SSZ` for timestamps).
- `details_json` contains raw parsed data — useful for confirmation numbers, seat assignments, loyalty numbers, etc.
- `confidence` (0–1): how confident the AI parser was. Items with `needs_review: true` may have errors.
- The API key is the user's — never share it, log it, or store it beyond the session unless the user explicitly asks.

---

## Managing API Keys

Users manage keys at **ubtrippin.xyz/settings**. Each key has a name and a masked preview. If a key is compromised, the user can revoke it from the settings page and generate a new one.
