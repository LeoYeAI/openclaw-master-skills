# Meta Ads CLI Commands Reference

Complete reference for all `lanbow-ads` subcommands. All commands follow the pattern: `lanbow-ads <group> <action> [options]`.

## Table of Contents

- [auth](#auth) - Authentication management
- [config](#config) - Configuration management
- [accounts](#accounts) - Ad account management
- [campaigns](#campaigns) - Campaign management
- [adsets](#adsets) - Ad set management
- [ads](#ads) - Ad management
- [creatives](#creatives) - Ad creative management
- [images](#images) - Image management
- [videos](#videos) - Video management
- [insights](#insights) - Performance analytics
- [pages](#pages) - Facebook Page discovery
- [targeting](#targeting) - Targeting research and estimation

---

## auth

Authentication management. These commands do NOT require prior authentication.

### auth login

Login via OAuth browser flow.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--force` | boolean | No | Force re-login even if already authenticated |

### auth logout

Clear cached authentication token. No flags.

### auth status

Show current authentication status. No flags.

---

## config

Configuration management. These commands do NOT require prior authentication.

### config set

Set configuration values.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--app-id <id>` | string | No | Meta App ID |
| `--app-secret <secret>` | string | No | Meta App Secret |
| `--account <id>` | string | No | Default ad account ID (act_XXXXX) |
| `--key <key>` | string | No | Arbitrary config key |
| `--value <value>` | string | If --key | Value for arbitrary config key |

At least one config value must be provided.

### config get

Get a configuration value.

```
lanbow-ads config get <key>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<key>` | string | Yes | Config key to retrieve |

### config list

List all configuration values. No flags.

### config unset

Remove a configuration value.

```
lanbow-ads config unset <key>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<key>` | string | Yes | Config key to remove |

### config accounts list

List all account aliases. No flags.

### config accounts add

Add or update an account alias. Alias cannot look like an account ID (`act_*` or numeric).

```
lanbow-ads config accounts add <alias> <account-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<alias>` | string | Yes | Friendly name (e.g. "main", "client-a") |
| `<account-id>` | string | Yes | Ad account ID (act_XXXXX or numeric) |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--label <text>` | string | No | Optional descriptive label |

### config accounts remove

Remove an account alias.

```
lanbow-ads config accounts remove <alias>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<alias>` | string | Yes | Alias to remove |

---

## accounts

Ad account management.

### accounts list

List accessible ad accounts.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### accounts info

Get ad account details.

```
lanbow-ads accounts info <account-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<account-id>` | string | Yes | Ad account ID (act_XXXXX) |

---

## campaigns

Campaign management.

### campaigns list

List campaigns.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--status <status...>` | string[] | No | Filter: ACTIVE, PAUSED, ARCHIVED (variadic) |
| `--objective <objective>` | string | No | Filter by ODAX objective |
| `--fields <fields...>` | string[] | No | Custom fields to return (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### campaigns get

Get campaign details.

```
lanbow-ads campaigns get <campaign-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<campaign-id>` | string | Yes | Campaign ID |

### campaigns create

Create a new campaign.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | Yes | Campaign name |
| `--objective <objective>` | string | Yes | ODAX objective |
| `--status <status>` | string | No | PAUSED or ACTIVE (default: PAUSED) |
| `--daily-budget <cents>` | int | No | Daily budget in cents (CBO only) |
| `--lifetime-budget <cents>` | int | No | Lifetime budget in cents (CBO only) |
| `--bid-strategy <strategy>` | string | No | Bid strategy |
| `--bid-cap <cents>` | int | No | Bid cap in cents |
| `--special-ad-categories <cats...>` | string[] | No | e.g. HOUSING CREDIT (variadic) |
| `--use-adset-level-budgets` | boolean | No | Enable ABO mode (budget at ad set level) |

**ODAX Objectives:** OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT, OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_APP_PROMOTION

### campaigns update

Update a campaign.

```
lanbow-ads campaigns update <campaign-id> [options]
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<campaign-id>` | string | Yes | Campaign ID |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | No | New name |
| `--status <status>` | string | No | ACTIVE, PAUSED, ARCHIVED |
| `--daily-budget <cents>` | int | No | New daily budget in cents |
| `--lifetime-budget <cents>` | int | No | New lifetime budget in cents |
| `--bid-strategy <strategy>` | string | No | New bid strategy |
| `--bid-cap <cents>` | int | No | New bid cap in cents |

---

## adsets

Ad set management.

### adsets list

List ad sets.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--campaign <id>` | string | No | Filter by campaign |
| `--status <status...>` | string[] | No | Filter: ACTIVE, PAUSED, ARCHIVED (variadic) |
| `--fields <fields...>` | string[] | No | Custom fields to return (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### adsets get

Get ad set details.

```
lanbow-ads adsets get <adset-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<adset-id>` | string | Yes | Ad set ID |

### adsets create

Create a new ad set.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--campaign-id <id>` | string | Yes | Parent campaign ID |
| `--name <name>` | string | Yes | Ad set name |
| `--optimization-goal <goal>` | string | Yes | e.g. LINK_CLICKS, REACH, OFFSITE_CONVERSIONS |
| `--billing-event <event>` | string | Yes | e.g. IMPRESSIONS |
| `--status <status>` | string | No | PAUSED or ACTIVE (default: PAUSED) |
| `--daily-budget <cents>` | int | No | Daily budget in cents |
| `--lifetime-budget <cents>` | int | No | Lifetime budget in cents |
| `--bid-amount <cents>` | int | No | Bid cap in cents |
| `--bid-strategy <strategy>` | string | No | Bid strategy |
| `--targeting <json>` | JSON | No | Targeting spec object |
| `--start-time <iso>` | string | No | ISO 8601 start time |
| `--end-time <iso>` | string | No | ISO 8601 end time |
| `--destination-type <type>` | string | No | WEBSITE, APP, MESSENGER, WHATSAPP, etc. |
| `--promoted-object <json>` | JSON | No | Required for OUTCOME_SALES. e.g. `'{"pixel_id":"123","custom_event_type":"PURCHASE"}'` |

**Optimization goals:** LINK_CLICKS, REACH, CONVERSIONS, APP_INSTALLS, VALUE, LEAD_GENERATION, IMPRESSIONS, LANDING_PAGE_VIEWS, OFFSITE_CONVERSIONS, QUALITY_LEAD

**Billing events:** IMPRESSIONS, LINK_CLICKS, OFFER_CLAIMS, PAGE_LIKES, POST_ENGAGEMENT

**Bid strategies:** LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, COST_CAP, LOWEST_COST_WITH_MIN_ROAS

**Destination types:** WEBSITE, WHATSAPP, MESSENGER, INSTAGRAM_DIRECT, ON_AD, APP, FACEBOOK, SHOP_AUTOMATIC, MESSAGING_MESSENGER_WHATSAPP

### adsets update

Update an ad set.

```
lanbow-ads adsets update <adset-id> [options]
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<adset-id>` | string | Yes | Ad set ID |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | No | New name |
| `--status <status>` | string | No | ACTIVE, PAUSED, ARCHIVED |
| `--daily-budget <cents>` | int | No | New daily budget in cents |
| `--lifetime-budget <cents>` | int | No | New lifetime budget in cents |
| `--bid-amount <cents>` | int | No | New bid amount in cents |
| `--bid-strategy <strategy>` | string | No | New bid strategy |
| `--targeting <json>` | JSON | No | Updated targeting spec |
| `--start-time <iso>` | string | No | New start time |
| `--end-time <iso>` | string | No | New end time |
| `--frequency-cap <json>` | JSON | No | Frequency cap spec |
| `--frequency-control-specs <json>` | JSON | No | Alternative to --frequency-cap |

---

## ads

Ad management.

### ads list

List ads.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--adset <id>` | string | No | Filter by ad set |
| `--campaign <id>` | string | No | Filter by campaign |
| `--status <status...>` | string[] | No | Filter: ACTIVE, PAUSED, ARCHIVED (variadic) |
| `--fields <fields...>` | string[] | No | Custom fields to return (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### ads get

Get ad details.

```
lanbow-ads ads get <ad-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<ad-id>` | string | Yes | Ad ID |

### ads create

Create a new ad.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | Yes | Ad name |
| `--adset-id <id>` | string | Yes | Parent ad set ID |
| `--status <status>` | string | No | PAUSED or ACTIVE (default: PAUSED) |
| `--creative-id <id>` | string | No | Creative ID to use |
| `--bid-amount <cents>` | int | No | Bid amount in cents |
| `--tracking-specs <json>` | JSON | No | Tracking specifications |
| `--conversion-domain <domain>` | string | No | Conversion domain |

### ads update

Update an ad.

```
lanbow-ads ads update <ad-id> [options]
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<ad-id>` | string | Yes | Ad ID |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | No | New name |
| `--status <status>` | string | No | ACTIVE, PAUSED, ARCHIVED |
| `--creative-id <id>` | string | No | New creative ID |
| `--bid-amount <cents>` | int | No | New bid amount in cents |

---

## creatives

Ad creative management.

### creatives list

List ad creatives.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--ad <id>` | string | No | Filter by ad |
| `--fields <fields...>` | string[] | No | Custom fields to return (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### creatives get

Get creative details.

```
lanbow-ads creatives get <creative-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<creative-id>` | string | Yes | Creative ID |

### creatives create

Create an ad creative.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | Yes | Creative name |
| `--page-id <id>` | string | No | Facebook Page ID |
| `--image-hash <hash>` | string | No | Image hash from upload |
| `--video-id <id>` | string | No | Video ID from upload; switches simple mode to `video_data` |
| `--link <url>` | string | No | Destination URL |
| `--message <text>` | string | No | Primary text |
| `--headline <text>` | string | No | Headline |
| `--description <text>` | string | No | Description text |
| `--call-to-action <type>` | string | No | CTA: LEARN_MORE, SHOP_NOW, SIGN_UP, etc. |
| `--instagram-actor-id <id>` | string | No | Instagram account ID |
| `--object-story-spec <json>` | JSON | No | Full object story spec |
| `--asset-feed-spec <json>` | JSON | No | Dynamic creative spec (for automated ads) |

Simple modes:
- Image: `--page-id` + `--image-hash` + `--link`
- Video: `--page-id` + `--video-id` + `--link` (`--image-hash` optional but recommended for thumbnail reliability)

### creatives update

Update a creative (name only).

```
lanbow-ads creatives update <creative-id> --name <name>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<creative-id>` | string | Yes | Creative ID |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--name <name>` | string | Yes | New name |

---

## images

Image management.

### images upload

Upload an image to an ad account.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--file <path>` | string | Yes | Local path to image file |
| `--name <name>` | string | No | Image name (defaults to filename) |

---

## videos

Ad video management. Supports files up to 4 GB. Files <= 20 MB use single-request upload; larger files use chunked (resumable) upload automatically.

### videos upload

Upload a video to an ad account. Optionally attach a thumbnail.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--file <path>` | string | Yes | Local path to video file |
| `--title <text>` | string | No | Video title |
| `--name <name>` | string | No | Video name (defaults to filename) |
| `--thumbnail <path>` | string | No | Local image to use as thumbnail |
| `--auto-thumbnail` | boolean | No | Auto-extract thumbnail from Meta (waits for processing) |

`--thumbnail` and `--auto-thumbnail` are mutually exclusive. Thumbnail extraction is best-effort and will never hide a successful video upload.

**Supported formats:** MP4 (recommended), MOV, AVI, MKV, WEBM, GIF

---

## insights

Performance analytics.

### insights get

Get performance insights with breakdowns and date filtering.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--campaign <id>` | string | No | Campaign ID |
| `--adset <id>` | string | No | Ad set ID |
| `--ad <id>` | string | No | Ad ID |
| `--level <level>` | string | No | account, campaign, adset, ad |
| `--date-preset <preset>` | string | No | Time preset (see below) |
| `--since <date>` | string | No | Custom start date (YYYY-MM-DD) |
| `--until <date>` | string | No | Custom end date (YYYY-MM-DD) |
| `--breakdowns <dims...>` | string[] | No | Breakdown dimensions (variadic) |
| `--fields <fields...>` | string[] | No | Custom metrics fields (variadic) |
| `--time-increment <n>` | string | No | Time granularity: number of days, "monthly", or "all_days" |
| `--sort <fields...>` | string[] | No | Sort fields, prefix `-` for descending (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |

At least one of `--campaign`, `--adset`, or `--ad` should be provided. If none provided, uses default account.

**Date presets:** today, yesterday, last_3d, last_7d, last_14d, last_30d, last_90d, this_month, last_month

**Breakdown dimensions:** age, gender, country, region, device_platform, publisher_platform, platform_position, impression_device

**Default metrics:** impressions, clicks, spend, cpc, cpm, ctr, reach, frequency, actions, conversions

---

## pages

Facebook Page discovery.

### pages list

List Pages accessible to the current user.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--fields <fields...>` | string[] | No | Custom fields to return (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |
| `--after <cursor>` | string | No | Pagination cursor |
| `--all` | boolean | No | Fetch all pages |

### pages instagram

Get the Instagram account linked to a Facebook Page.

```
lanbow-ads pages instagram <page-id>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<page-id>` | string | Yes | Facebook Page ID |

---

## targeting

Targeting research and audience estimation.

### targeting interests

Search interest targeting options.

```
lanbow-ads targeting interests <query>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<query>` | string | Yes | Search keyword |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--limit <n>` | string | No | Max results (default: 25) |

### targeting suggestions

Get interest suggestions from existing interests.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--interests <names...>` | string[] | Yes | Interest names (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |

### targeting locations

Search geographic locations.

```
lanbow-ads targeting locations <query>
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<query>` | string | Yes | Location search query |

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--type <types...>` | string[] | No | country, region, city, zip, geo_market (variadic) |
| `--limit <n>` | string | No | Max results (default: 25) |

### targeting behaviors

List behavior targeting options.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--limit <n>` | string | No | Max results (default: 50) |

### targeting demographics

List demographic targeting options.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--class <class>` | string | No | Category: demographics, life_events, industries, income, family_statuses, user_device, user_os (default: demographics) |
| `--limit <n>` | string | No | Max results (default: 50) |

### targeting estimate

Estimate audience size for a targeting spec.

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--targeting <json>` | JSON | Yes | Targeting spec object (same format as adsets create) |
