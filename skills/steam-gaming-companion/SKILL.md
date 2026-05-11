---
name: steam-gaming-companion
description: >
  Steam & PC Gaming Companion — full Steam Web API integration for library management,
  play recommendations, wishlist sale monitoring, achievement tracking, and game info lookup.
  The first real Steam API skill on ClawHub.
version: 1.0.0
tags:
  - gaming
  - steam
  - pc-gaming
  - library-management
  - achievements
  - wishlist
  - backlog
  - recommendations
author: steam-companion
requires:
  - STEAM_API_KEY
  - STEAM_ID
optional_env:
  - IGDB_CLIENT_ID
  - IGDB_ACCESS_TOKEN
---

# Steam & PC Gaming Companion

A complete Steam Web API integration skill. Manages your library, tracks achievements, monitors wishlist sales, recommends what to play next, and looks up any game — all from natural language.

---

## Setup

### Step 1: Get Your Steam API Key (required, 30 seconds)

1. Go to https://steamcommunity.com/dev/apikey
2. Sign in with your Steam account
3. Enter any domain name (e.g. `localhost`) — it doesn't matter for personal use
4. Click **Register** and copy the key
5. Set it: `STEAM_API_KEY=<your-key>`

### Step 2: Get Your 64-bit Steam ID (required, 15 seconds)

Your Steam ID is NOT your vanity URL or display name. It's a 17-digit number.

1. Go to https://steamid.io
2. Paste your Steam profile URL (e.g. `https://steamcommunity.com/id/yourname`)
3. Copy the **steamID64** value (looks like `76561198012345678`)
4. Set it: `STEAM_ID=<your-steam-id-64>`

### Step 3: Get IGDB Credentials (optional, 2 minutes)

IGDB provides richer game metadata (ratings, genres, descriptions) than the Steam store API. It's free via Twitch.

1. Go to https://dev.twitch.tv/console/apps and log in with your Twitch account (create one if needed)
2. Click **Register Your Application**
3. Name: anything (e.g. `steam-companion`), OAuth Redirect: `http://localhost`, Category: **Application Integration**
4. Click **Manage** on your new app, copy the **Client ID**
5. Generate a **Client Secret** and copy it
6. Get an access token by running:
   ```
   curl -X POST 'https://id.twitch.tv/oauth2/token' \
     -d 'client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=client_credentials'
   ```
7. Copy the `access_token` from the response
8. Set both:
   ```
   IGDB_CLIENT_ID=<your-client-id>
   IGDB_ACCESS_TOKEN=<your-access-token>
   ```

Note: IGDB tokens expire after ~60 days. If game lookups start failing with 401, regenerate the token using step 6.

### Step 4: Verify Setup

Tell the agent: **"verify my steam setup"** — it will confirm your credentials work and show your account name and library size.

---

## Trigger Conditions

| User Says (examples) | Feature Triggered |
|---|---|
| "show my steam library", "how many games do I own", "what's in my backlog" | Library Overview + Backlog Manager |
| "what should I play", "recommend something chill for an hour", "I have all night, what's good" | Play Recommender |
| "any wishlist sales", "check my wishlist", "are any of my wishlisted games on sale" | Wishlist Sale Monitor |
| "show my achievements for Hades", "how far am I in Elden Ring", "achievement progress" | Achievement Tracker |
| "most played games", "what do I play the most", "top 10 games by hours" | Most Played Rankings |
| "tell me about Hollow Knight", "look up Baldur's Gate 3", "game info for Celeste" | Game Info Lookup |
| "verify my steam setup", "test steam connection", "are my steam credentials working" | Setup Verification |

---

## Feature 1: Library Overview + Backlog Manager

### API Call

```
GET https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/
```

**Query parameters:**
| Parameter | Value |
|---|---|
| `key` | `{STEAM_API_KEY}` |
| `steamid` | `{STEAM_ID}` |
| `include_appinfo` | `1` |
| `include_played_free_games` | `1` |
| `format` | `json` |

### Response Fields Used

```json
{
  "response": {
    "game_count": 247,
    "games": [
      {
        "appid": 570,
        "name": "Dota 2",
        "playtime_forever": 14523,
        "playtime_2weeks": 120,
        "img_icon_url": "hash",
        "has_community_visible_stats": true
      }
    ]
  }
}
```

- `playtime_forever` is in **minutes**
- `playtime_2weeks` is present only if the game was played in the last 2 weeks

### Logic Rules

Categorize every game by `playtime_forever`:

| Category | Rule | Label |
|---|---|---|
| **Unplayed** | `playtime_forever < 60` | Never really touched |
| **Abandoned** | `60 <= playtime_forever < 300` | Tried but didn't stick |
| **Played** | `playtime_forever >= 300` | Actually played |

### Response Format

```
🎮 Steam Library Overview

📊 Total Games: {game_count}
✅ Played (5+ hrs): {played_count} ({played_pct}%)
⚠️ Abandoned (1-5 hrs): {abandoned_count} ({abandoned_pct}%)
🆕 Unplayed (<1 hr): {unplayed_count} ({unplayed_pct}%)
⏱️ Total Lifetime Hours: {total_hours}

📦 Your Backlog ({unplayed_count} games)
{for each unplayed game, sorted alphabetically:}
  • {name} — {playtime_forever} min logged
{end}

⚠️ Abandoned Games ({abandoned_count})
{for each abandoned game, sorted by playtime_forever ascending:}
  • {name} — {hours}h {minutes}m
{end}
```

If `game_count` is 0 or the `games` array is missing, the profile is likely private. See Error Handling.

---

## Feature 2: Play Recommender

### Prerequisites

Fetch the full library using the same API call as Feature 1.

### Interaction Flow

1. Ask the user two questions (or extract from their message if already stated):
   - **Mood**: chill / intense / story-driven / competitive
   - **Time available**: under 1 hour / 1-2 hours / all night (3+ hours)

2. Filter the user's library to games with `playtime_forever < 60` (unplayed) OR `60 <= playtime_forever < 300` (abandoned — gave it a short try).

3. For each candidate game, look up genre data. Use one of these methods:
   - **If IGDB credentials exist**: POST to `https://api.igdb.com/v4/games` with body `search "{game_name}"; fields genres.name, themes.name, total_rating; limit 1;` and headers `Client-ID: {IGDB_CLIENT_ID}`, `Authorization: Bearer {IGDB_ACCESS_TOKEN}`
   - **If no IGDB**: GET `https://store.steampowered.com/api/appdetails?appids={appid}` and extract `data.genres[].description` and `data.short_description`

4. Match games to mood using these genre mappings:

| Mood | Matching Genres / Themes |
|---|---|
| **Chill** | Simulation, Puzzle, Casual, Farming, Sandbox, Walking Simulator, Indie (non-horror) |
| **Intense** | Action, Shooter, Roguelike, Roguelite, Survival Horror, Souls-like, Bullet Hell |
| **Story-driven** | RPG, Adventure, Visual Novel, Interactive Fiction, Narrative, Point & Click |
| **Competitive** | Multiplayer, PvP, Fighting, Sports, Racing, Battle Royale, MOBA |

5. Match games to time available:

| Time Slot | Rule |
|---|---|
| Under 1 hour | Prefer games with short play sessions — roguelites, puzzle games, platformers, arcade. Avoid open-world RPGs or grand strategy. |
| 1-2 hours | Any genre works. Prefer games with moderate session lengths. |
| All night | Prefer RPGs, open-world, strategy, survival, sandbox — games that reward long sessions. |

6. Select the top 3 matches. If fewer than 3 match, relax the playtime filter to include games up to 600 minutes.

### Response Format

```
🎯 Play Recommendations — {mood}, {time_available}

1. 🎮 {game_name}
   Genre: {genres}
   Why: {1-2 sentence reason based on mood + time fit}
   Playtime so far: {minutes} min

2. 🎮 {game_name}
   Genre: {genres}
   Why: {reason}
   Playtime so far: {minutes} min

3. 🎮 {game_name}
   Genre: {genres}
   Why: {reason}
   Playtime so far: {minutes} min

💡 None of these click? Tell me more about what you're in the mood for.
```

If no games match at all:

```
😅 Couldn't find a great match in your unplayed library for "{mood}" + "{time}".

Your unplayed games are mostly: {top 3 genres in unplayed list}.

Want me to check your full library instead, or look up something new?
```

---

## Feature 3: Wishlist Sale Monitor

### API Call

```
GET https://store.steampowered.com/wishlist/profiles/{STEAM_ID}/wishlistdata/
```

No API key needed — uses the Steam store API directly. Requires the user's wishlist to be **public**.

**Note:** This endpoint may paginate. If the response contains exactly 50 items, make additional requests:
```
GET https://store.steampowered.com/wishlist/profiles/{STEAM_ID}/wishlistdata/?p=1
GET https://store.steampowered.com/wishlist/profiles/{STEAM_ID}/wishlistdata/?p=2
```
Continue incrementing `p` until the response is empty or contains fewer than 50 items. Page 0 is the default.

### Response Fields Used

Each entry is keyed by `appid`:

```json
{
  "730": {
    "name": "Counter-Strike 2",
    "capsule": "url-to-image",
    "review_score": 7,
    "review_desc": "Very Positive",
    "reviews_total": "7,456,123",
    "reviews_percent": 86,
    "release_date": "1694649600",
    "release_string": "Sep 27, 2023",
    "priority": 0,
    "added": 1680000000,
    "background": "url",
    "rank": 14,
    "tags": ["FPS", "Shooter"],
    "is_free_game": false,
    "subs": [
      {
        "id": 54029,
        "discount_block": "<div ...>-75%</div>",
        "discount_pct": 75,
        "price": "749"
      }
    ]
  }
}
```

### Logic Rules

1. Iterate over all wishlist entries
2. For each entry, check `subs` array. A game is on sale if any sub has `discount_pct > 0`
3. The `price` field is the **current (discounted) price** in **cents** (e.g. `749` = `$7.49`). If `price` is a string, parse it as an integer first.
4. Calculate original price: `original_price = price / (1 - discount_pct / 100)`
5. Sort results by `discount_pct` descending (biggest discounts first)

### Response Format

**If sales found:**

```
🏷️ Wishlist Sales — {count} game(s) on sale!

{for each discounted game, sorted by discount_pct desc:}
🔥 {name} — {discount_pct}% OFF
   💰 ${sale_price} (was ${original_price})
   ⭐ {review_desc} ({reviews_percent}% positive)
   🔗 https://store.steampowered.com/app/{appid}
{end}

💡 Prices are current as of this check. Steam sales change without notice.
```

**If no sales:**

```
🏷️ Wishlist Sales

No games on your wishlist are currently discounted.

📋 You have {total_wishlist_count} games wishlisted.
Top 3 by priority:
  1. {name} — {review_desc}
  2. {name} — {review_desc}
  3. {name} — {review_desc}

💡 Major Steam sales happen in June (Summer Sale) and December (Winter Sale).
```

**If wishlist is empty or inaccessible:**

```
⚠️ Couldn't access your wishlist.

This usually means your wishlist is set to private. To fix:
1. Go to your Steam profile → Edit Profile → Privacy Settings
2. Set "Game details" to Public
3. Try again

If it's already public, Steam's wishlist API may be temporarily down. Try again in a few minutes.
```

---

## Feature 4: Achievement Tracker

### Step 1: Get Player Achievements

```
GET https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/
```

**Query parameters:**
| Parameter | Value |
|---|---|
| `key` | `{STEAM_API_KEY}` |
| `steamid` | `{STEAM_ID}` |
| `appid` | `{appid}` |
| `l` | `english` |

**Response fields:**
```json
{
  "playerstats": {
    "steamID": "76561198012345678",
    "gameName": "Hades",
    "success": true,
    "achievements": [
      {
        "apiname": "AchUnlockAll",
        "achieved": 1,
        "unlocktime": 1695000000
      }
    ]
  }
}
```

- `achieved`: `1` = unlocked, `0` = locked
- `unlocktime`: Unix timestamp (0 if locked)

### Step 2: Get Achievement Schema (for human-readable names + descriptions)

```
GET https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/
```

**Query parameters:**
| Parameter | Value |
|---|---|
| `key` | `{STEAM_API_KEY}` |
| `appid` | `{appid}` |
| `l` | `english` |

**Response fields:**
```json
{
  "game": {
    "gameName": "Hades",
    "availableGameStats": {
      "achievements": [
        {
          "name": "AchUnlockAll",
          "defaultvalue": 0,
          "displayName": "Everything in its Place",
          "hidden": 0,
          "description": "Unlock all other achievements.",
          "icon": "url-to-achieved-icon",
          "icongray": "url-to-locked-icon"
        }
      ]
    }
  }
}
```

### Step 3: Resolve Game Name to AppID

If the user says a game name instead of an AppID, resolve it:

```
GET https://api.steampowered.com/ISteamApps/GetAppList/v2/
```

This returns ALL Steam apps (~180,000). To avoid fetching this every time:
1. First try the store search API: `GET https://store.steampowered.com/api/storesearch/?term={game_name}&l=english&cc=US`
2. Use the first result's `id` as the `appid`
3. If no results, tell the user the game wasn't found and ask them to check the name

### Logic Rules

1. Fetch both player achievements and schema for the given appid
2. Match achievements by `apiname` (player data) to `name` (schema data)
3. Replace API names with `displayName` from the schema
4. Sort unlocked achievements by `unlocktime` descending (most recent first)
5. Calculate: `unlocked_count`, `total_count`, `completion_pct`
6. Build a visual progress bar: use `█` for filled and `░` for empty, 20 characters wide
7. Show the 5 most recently unlocked achievements
8. Show up to 5 locked achievements (non-hidden ones only; for `hidden: 1`, show as "🔒 Hidden Achievement")

### Response Format

```
🏆 Achievements — {game_name}

Progress: {unlocked_count}/{total_count} ({completion_pct}%)
[████████████░░░░░░░░] {completion_pct}%

🔓 Recently Unlocked
{for each of the 5 most recent, by unlocktime desc:}
  ✅ {displayName} — {description}
     Unlocked: {formatted_date}
{end}

🔒 Up Next ({remaining_count} remaining)
{for up to 5 non-hidden locked achievements:}
  ⬜ {displayName} — {description}
{end}
{if hidden locked achievements exist:}
  🔒 +{hidden_count} hidden achievement(s)
{end}

{if completion_pct == 100:}
🎉 Completionist! You've unlocked every achievement in {game_name}!
{end}
```

### Error: Game Has No Achievements

If `GetSchemaForGame` returns no achievements array or it's empty:

```
ℹ️ {game_name} doesn't have Steam achievements.
```

### Error: Achievement Data Private

If `GetPlayerAchievements` returns `success: false`:

```
⚠️ Can't access achievement data for {game_name}.

This usually means your game details are set to private. To fix:
1. Go to Steam → Profile → Edit Profile → Privacy Settings
2. Set "Game details" to Public
3. Try again
```

---

## Feature 5: Most Played Rankings

### API Call

Same as Feature 1 — `IPlayerService/GetOwnedGames/v1` with `include_appinfo=1`.

### Logic Rules

1. Sort all games by `playtime_forever` descending
2. Take the top 10
3. Convert minutes to hours and minutes: `hours = playtime_forever // 60`, `minutes = playtime_forever % 60`
4. Calculate total lifetime hours across ALL games: `sum(playtime_forever for all games) / 60`
5. If `playtime_2weeks` exists on any game, also show "Recently Active" section

### Response Format

```
⏱️ Most Played Games — Top 10

 # │ Game                          │ Playtime
───┼───────────────────────────────┼──────────
 1 │ {name}                        │ {hours}h {minutes}m
 2 │ {name}                        │ {hours}h {minutes}m
 3 │ {name}                        │ {hours}h {minutes}m
 4 │ {name}                        │ {hours}h {minutes}m
 5 │ {name}                        │ {hours}h {minutes}m
 6 │ {name}                        │ {hours}h {minutes}m
 7 │ {name}                        │ {hours}h {minutes}m
 8 │ {name}                        │ {hours}h {minutes}m
 9 │ {name}                        │ {hours}h {minutes}m
10 │ {name}                        │ {hours}h {minutes}m

📊 Total Lifetime Gaming: {total_hours} hours across {game_count} games
   That's {total_days} days of gaming!

{if any game has playtime_2weeks:}
🕹️ Active This Week
{for each game with playtime_2weeks > 0, sorted desc:}
  • {name} — {hours}h {minutes}m in the last 2 weeks
{end}
{end}
```

---

## Feature 6: Game Info Lookup

### Method A: IGDB (preferred, if credentials exist)

```
POST https://api.igdb.com/v4/games
```

**Headers:**
| Header | Value |
|---|---|
| `Client-ID` | `{IGDB_CLIENT_ID}` |
| `Authorization` | `Bearer {IGDB_ACCESS_TOKEN}` |
| `Content-Type` | `text/plain` |

**Body (Apicalypse query language):**
```
search "{game_name}";
fields name, summary, total_rating, genres.name, themes.name,
       involved_companies.company.name, involved_companies.developer,
       involved_companies.publisher, first_release_date, platforms.name,
       aggregated_rating, aggregated_rating_count, cover.url;
limit 1;
```

**Response fields:**
```json
[
  {
    "id": 119171,
    "name": "Hades",
    "summary": "A rogue-like dungeon crawler...",
    "total_rating": 91.234,
    "aggregated_rating": 93.0,
    "aggregated_rating_count": 24,
    "genres": [{"id": 12, "name": "Role-playing (RPG)"}, {"id": 31, "name": "Adventure"}],
    "themes": [{"id": 17, "name": "Fantasy"}],
    "involved_companies": [
      {"company": {"name": "Supergiant Games"}, "developer": true, "publisher": true}
    ],
    "first_release_date": 1600300800,
    "platforms": [{"name": "PC (Microsoft Windows)"}, {"name": "Nintendo Switch"}],
    "cover": {"url": "//images.igdb.com/igdb/image/upload/t_cover_big/co1234.jpg"}
  }
]
```

- `total_rating` is 0-100 (community + critic average)
- `first_release_date` is Unix timestamp
- Filter `involved_companies` where `developer: true` for developer, `publisher: true` for publisher

### Method B: Steam Store API (fallback)

```
GET https://store.steampowered.com/api/appdetails?appids={appid}
```

To get the `appid` from a game name, use the store search:
```
GET https://store.steampowered.com/api/storesearch/?term={game_name}&l=english&cc=US
```

**Response fields (from appdetails):**
```json
{
  "{appid}": {
    "success": true,
    "data": {
      "name": "Hades",
      "steam_appid": 1145360,
      "short_description": "Defy the god of the dead...",
      "detailed_description": "...",
      "developers": ["Supergiant Games"],
      "publishers": ["Supergiant Games"],
      "genres": [{"id": "3", "description": "RPG"}, {"id": "25", "description": "Adventure"}],
      "release_date": {"coming_soon": false, "date": "Sep 17, 2020"},
      "metacritic": {"score": 93, "url": "..."},
      "categories": [{"id": 2, "description": "Single-player"}],
      "platforms": {"windows": true, "mac": true, "linux": true},
      "price_overview": {"final_formatted": "$24.99", "discount_percent": 0}
    }
  }
}
```

### Response Format

```
🎮 {name}

📝 {summary or short_description — first 2 sentences max}

📊 Rating: {total_rating or metacritic score}/100
🎭 Genre: {genres, comma-separated}
🏢 Developer: {developer name(s)}
📦 Publisher: {publisher name(s)}
📅 Released: {formatted release date}
🖥️ Platforms: {platform list}

{if price_overview exists and source is Steam:}
💰 Price: {final_formatted} {if discount > 0: "(🔥 {discount}% off!)"}
{end}

{if the user owns this game (check library):}
📂 In your library — {playtime_forever} min played
{end}
```

### Error: Game Not Found

```
❌ Couldn't find "{game_name}".

Tips:
• Check the spelling
• Use the full official name (e.g. "Counter-Strike 2" not "CS2")
• For DLC, include the base game name
```

---

## Feature 7: Setup Verification

### API Call

```
GET https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/
```

**Query parameters:**
| Parameter | Value |
|---|---|
| `key` | `{STEAM_API_KEY}` |
| `steamids` | `{STEAM_ID}` |

**Response fields:**
```json
{
  "response": {
    "players": [
      {
        "steamid": "76561198012345678",
        "personaname": "PlayerName",
        "profileurl": "https://steamcommunity.com/id/...",
        "avatar": "url",
        "avatarfull": "url",
        "personastate": 1,
        "communityvisibilitystate": 3,
        "profilestate": 1,
        "lastlogoff": 1695000000,
        "timecreated": 1300000000
      }
    ]
  }
}
```

- `communityvisibilitystate`: `1` = private, `3` = public
- `personastate`: `0` = Offline, `1` = Online, `2` = Busy, `3` = Away, `4` = Snooze, `5` = Looking to trade, `6` = Looking to play

Then also call `IPlayerService/GetOwnedGames/v1` to get `game_count`.

### Response Format

**Success:**

```
✅ Steam Companion — Setup Verified

👤 Account: {personaname}
🔗 Profile: {profileurl}
🌐 Status: {personastate_label}
🔓 Profile Visibility: {Public or Private}
📅 Member Since: {formatted timecreated}
🎮 Games Owned: {game_count}

{if communityvisibilitystate != 3:}
⚠️ Your profile is set to Private. Some features (wishlist sales, achievements)
   require a public profile. Go to Edit Profile → Privacy Settings → set to Public.
{end}

{if IGDB_CLIENT_ID and IGDB_ACCESS_TOKEN are set:}
🎮 IGDB: ✅ Connected (richer game lookups enabled)
{else:}
🎮 IGDB: ❌ Not configured (game lookups will use Steam store data)
   Optional: Set IGDB_CLIENT_ID and IGDB_ACCESS_TOKEN for better game info.
{end}

All systems go. Try: "show my library" or "what should I play tonight?"
```

**Failure — bad API key:**

If the API returns `403` or the response is empty:

```
❌ Setup Failed — Invalid API Key

Your STEAM_API_KEY was rejected by Steam.

To fix:
1. Go to https://steamcommunity.com/dev/apikey
2. Make sure you're logged into the correct Steam account
3. If you see a key, copy it exactly (no spaces)
4. If you don't see a key, register a new one with any domain
5. Update your STEAM_API_KEY env var
```

**Failure — bad Steam ID:**

If `players` array is empty:

```
❌ Setup Failed — Steam ID Not Found

No account found for Steam ID: {STEAM_ID}

To fix:
1. Go to https://steamid.io
2. Paste your Steam profile URL
3. Copy the steamID64 (17-digit number like 76561198012345678)
4. Update your STEAM_ID env var

Common mistakes:
• Using your vanity URL name instead of the 64-bit ID
• Using a 32-bit Steam ID (shorter number) instead of 64-bit
• Extra spaces or characters in the value
```

**Failure — missing env vars:**

```
❌ Setup Failed — Missing Credentials

{if STEAM_API_KEY not set:}
• STEAM_API_KEY is not set — get one at https://steamcommunity.com/dev/apikey
{end}
{if STEAM_ID not set:}
• STEAM_ID is not set — find yours at https://steamid.io
{end}

Both are required. See the setup instructions above.
```

---

## Error Handling (Global)

### Private Profile

**Detection:** `IPlayerService/GetOwnedGames/v1` returns `{"response": {}}` (empty, no `game_count` or `games` key).

**Response:**
```
🔒 Your Steam profile or game details are set to private.

To use this skill, your profile needs to be public:
1. Open Steam → click your name → Profile
2. Click Edit Profile → Privacy Settings
3. Set "My profile" to Public
4. Set "Game details" to Public
5. Wait 1-2 minutes for Steam's cache to update
6. Try again

Note: You can set it back to private after you're done.
```

### API Rate Limiting

Steam's Web API has a rate limit of approximately **100,000 calls per day** and **1 request per second** per key. In practice, you will not hit this unless you're scripting bulk requests.

If you receive HTTP `429` or `503`:

```
⏳ Steam's API is temporarily rate-limiting requests. Wait a minute and try again.
```

### Network / Server Errors

If any API call returns HTTP `500`, `502`, `503`, or times out:

```
⚠️ Steam's API returned an error ({status_code}). This is on Steam's end, not yours.

Try again in a minute. If it persists, check https://steamstat.us for outages.
```

### Missing Environment Variables

Before making any API call, check that the required env vars are set. If missing:

```
⚠️ Missing required configuration.

{if STEAM_API_KEY not set:}
• STEAM_API_KEY — Get one at https://steamcommunity.com/dev/apikey
{end}
{if STEAM_ID not set:}
• STEAM_ID — Find yours at https://steamid.io
{end}

Run "verify my steam setup" after setting them.
```

### IGDB Token Expired

IGDB access tokens expire after approximately 60 days. If any IGDB API call returns HTTP `401`:

```
⚠️ Your IGDB access token has expired.

To regenerate it:
1. Run this command (replace with your credentials):
   curl -X POST 'https://id.twitch.tv/oauth2/token' \
     -d 'client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=client_credentials'
2. Copy the new access_token from the response
3. Update your IGDB_ACCESS_TOKEN env var

Falling back to Steam store API for this lookup.
```

After showing this message, fall back to Steam store API (Method B) for the current request so the user still gets a result.

### Store API Region Issues

`store.steampowered.com/api/appdetails` may return different prices based on region. Prices shown are for the US store by default. Add `&cc=US` to force USD, or `&cc={country_code}` if the user requests a different region.

---

## Example Conversations

### Example 1: Library Check

**User:** How many games do I own on Steam?

**Agent:** Calls `IPlayerService/GetOwnedGames/v1` → gets library → categorizes → responds with full library overview showing total count, backlog breakdown, and the unplayed/abandoned lists.

### Example 2: Play Recommendation

**User:** I've got about 2 hours tonight and want something chill. What should I play?

**Agent:** Fetches library → filters unplayed/abandoned games → looks up genres for each via IGDB or Steam store → matches to "chill" + "1-2 hours" → picks 3 best matches → responds with names, genres, and personalized reasons.

### Example 3: Wishlist Check

**User:** Any games on my wishlist on sale?

**Agent:** Calls wishlist API → checks all subs for `discount_pct > 0` → calculates original prices → sorts by discount → responds with formatted sale list or "no sales" message with upcoming sale dates.

### Example 4: Achievement Progress

**User:** Show my achievements for Hades

**Agent:** Searches store for "Hades" → gets appid 1145360 → calls `GetPlayerAchievements` and `GetSchemaForGame` → matches by apiname → calculates completion → builds progress bar → shows recent unlocks and remaining achievements.

### Example 5: Quick Stats

**User:** What are my most played games?

**Agent:** Fetches library → sorts by playtime_forever desc → takes top 10 → formats table with hours/minutes → calculates total lifetime hours → shows recently active games if any.

### Example 6: Game Lookup

**User:** Tell me about Baldur's Gate 3

**Agent:** If IGDB configured, POSTs search query → gets name, summary, rating, genres, developer, release date. If not, searches Steam store → gets appdetails. Also checks if user owns it and shows playtime.

---

## Notes for Agent Implementors

- All Steam Web API calls use HTTPS GET with query parameters. No POST requests needed for Steam.
- IGDB uses POST with a plain-text body in Apicalypse query language. Content-Type must be `text/plain`.
- The wishlist endpoint (`store.steampowered.com`) does not require an API key but does require the wishlist to be public.
- Steam's `playtime_forever` is always in minutes. Always convert to hours/minutes for display.
- Unix timestamps from Steam and IGDB should be formatted as human-readable dates (e.g., "Sep 17, 2020").
- The store search API (`storesearch`) is the fastest way to resolve a game name to an appid. Do not fetch the full app list unless store search fails.
- When making multiple API calls for a single feature (e.g., achievements need 2 calls), make them concurrently where possible.
- IGDB access tokens expire. If a 401 is returned, tell the user to regenerate the token.

---

## Changelog

### v1.0.0 — Initial Release
- Library overview with backlog categorization (unplayed / abandoned / played)
- Mood + time-based play recommender from user's actual library
- Wishlist sale monitor with price calculations and pagination
- Achievement tracker with progress bars and human-readable names
- Most played rankings with lifetime hour totals
- Game info lookup via IGDB (preferred) or Steam store API (fallback)
- Setup verification with specific error diagnostics
- Comprehensive error handling for private profiles, missing credentials, API failures
