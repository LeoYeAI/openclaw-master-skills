---
name: lanbow-ads
description: Manage Meta (Facebook/Instagram) advertising campaigns via the lanbow-ads CLI. Use when the user wants to create, analyze, optimize, or manage Meta Ads campaigns, ad sets, ads, creatives, targeting, or performance insights. Triggers on tasks like "show my active campaigns", "create a campaign", "get ad performance", "search interests for targeting", "upload an ad image", "upload an ad video", "manage account aliases", or any Meta/Facebook/Instagram advertising management task. IMPORTANT - always follow the invocation instructions in this skill instead of exploring the CLI yourself.
---

# Lanbow Ads CLI

Manage Meta advertising campaigns using the `lanbow-ads` CLI. Commands are organized as hierarchical subcommands: `lanbow-ads <group> <action> [options]`.

**IMPORTANT: Follow the invocation patterns documented in this skill. If you are unsure about a command's usage or available options, run `lanbow-ads <command> --help` to get up-to-date help directly from the CLI. Avoid unnecessary exploration via `--version`, inspecting `package.json`, or `npm show`.**

## Prerequisites

Ensure lanbow-ads is installed and authenticated. For a full step-by-step guide, see [meta-account-setup.md](meta-account-setup.md).

```bash
npm install -g lanbow-ads           # install CLI globally
```

**Authentication — try in this order:**

1. **Environment variables or platform secret fields (best):** If `META_ACCESS_TOKEN`, `META_APP_ID`, `META_AD_ACCOUNT_ID` are set, configure automatically:
   ```bash
   lanbow-ads config set --app-id "$META_APP_ID"
   lanbow-ads auth set-token "$META_ACCESS_TOKEN"
   lanbow-ads config set --account "$META_AD_ACCOUNT_ID"
   # Only if META_APP_SECRET is set (optional — for token exchange only):
   [ -n "$META_APP_SECRET" ] && lanbow-ads config set --app-secret "$META_APP_SECRET"
   ```

2. **User provides credentials directly:** Ask the user for their Access Token, App ID, and Ad Account ID (minimum needed). Only request App Secret if the user needs token exchange. Recommend the user provide credentials via env vars or platform secret fields rather than pasting into chat. The user gets tokens from Meta's web interface (Graph API Explorer or Business Settings).

3. **`lanbow-ads auth login` (rarely works):** This opens a local browser for OAuth. It only works when you and the user are on the **same machine**. Do NOT attempt this by default — if the user can't open the auth URL, it means you're on different machines. Fall back to method 2 immediately instead of sending auth URLs the user cannot use.

```bash
lanbow-ads config list              # verify authentication
```

## CLI Invocation Pattern

```bash
lanbow-ads <group> <action> [options]
lanbow-ads campaigns list --status ACTIVE --limit 10
lanbow-ads insights get --campaign 123456 --date-preset last_7d
```

**Global options** (apply to any command):

| Flag                     | Description                                |
| ------------------------ | ------------------------------------------ |
| `--json`                 | Output as JSON                             |
| `--format <format>`      | Output format: `table` or `json`           |
| `--verbose`              | Enable verbose logging                     |
| `--account <id>`         | Ad account ID or alias (overrides default) |
| `--access-token <token>` | Access token (overrides stored token)      |

Default account is auto-injected when configured via `lanbow-ads config set --account act_XXXXX`.

## Workflow Decision Tree

**Exploring accounts?** -> Account Discovery
**Managing account aliases?** -> Configuration (account aliases)
**Creating a campaign from scratch?** -> Full Campaign Creation (Campaign -> Ad Set -> Creative -> Ad)
**Uploading video creatives?** -> Pages, Images & Videos
**Checking performance?** -> Insights & Analysis
**Researching targeting?** -> Targeting Research
**Modifying existing ads?** -> Listing & Updating

---

## Account Discovery

```bash
lanbow-ads accounts list
lanbow-ads accounts info act_123456789
```

## Full Campaign Creation

### 1. Create Campaign

**CBO (Campaign Budget Optimization)** - budget at campaign level:

```bash
lanbow-ads campaigns create \
  --name "Q1 Awareness" \
  --objective OUTCOME_AWARENESS \
  --status PAUSED \
  --daily-budget 5000
```

**ABO (Ad Set Budget Optimization)** - budget at ad set level:

```bash
lanbow-ads campaigns create \
  --name "Q1 Sales ABO" \
  --objective OUTCOME_SALES \
  --status PAUSED \
  --use-adset-level-budgets
```

> **IMPORTANT:** For ABO campaigns, pass `--use-adset-level-budgets`. Do NOT simply omit `--daily-budget` - Meta API v24+ requires explicit configuration, and this flag handles it automatically.

**ODAX objectives** (required for new campaigns):
- `OUTCOME_AWARENESS` - Brand awareness, reach
- `OUTCOME_TRAFFIC` - Website visits, link clicks
- `OUTCOME_ENGAGEMENT` - Post engagement, page likes
- `OUTCOME_LEADS` - Lead generation forms
- `OUTCOME_SALES` - Conversions, catalog sales
- `OUTCOME_APP_PROMOTION` - App installs

Budgets are in **cents** (5000 = $50.00).

### 2. Create Ad Set with Targeting

**Basic example (traffic/clicks):**

```bash
lanbow-ads adsets create \
  --campaign-id CAMPAIGN_ID \
  --name "US 25-45 Mobile" \
  --optimization-goal LINK_CLICKS \
  --billing-event IMPRESSIONS \
  --daily-budget 2000 \
  --bid-strategy LOWEST_COST_WITHOUT_CAP \
  --targeting '{"age_min":25,"age_max":45,"geo_locations":{"countries":["US"]},"interests":[{"id":"6003392754754","name":"Nike, Inc."}],"device_platforms":["mobile"]}' \
  --status PAUSED
```

**Conversion/Sales example (with pixel):**

```bash
lanbow-ads adsets create \
  --campaign-id CAMPAIGN_ID \
  --name "US Purchase Conversions" \
  --optimization-goal OFFSITE_CONVERSIONS \
  --billing-event IMPRESSIONS \
  --daily-budget 100 \
  --bid-strategy LOWEST_COST_WITHOUT_CAP \
  --promoted-object '{"pixel_id":"YOUR_PIXEL_ID","custom_event_type":"PURCHASE"}' \
  --destination-type WEBSITE \
  --targeting '{"age_min":25,"genders":[2],"geo_locations":{"countries":["US","GB"]}}' \
  --status PAUSED
```

> **IMPORTANT:** For `OUTCOME_SALES` campaigns, pass `--promoted-object` with `pixel_id` and `custom_event_type`, set `--optimization-goal OFFSITE_CONVERSIONS`, and add `--destination-type WEBSITE` for web conversions.

**Bid strategies:** `LOWEST_COST_WITHOUT_CAP`, `LOWEST_COST_WITH_BID_CAP`, `COST_CAP`, `LOWEST_COST_WITH_MIN_ROAS`

### 3. Upload Media & Create Creative

```bash
# Upload image -> returns image_hash
lanbow-ads images upload --file /path/to/image.jpg

# Upload video -> returns video_id (+ optional thumbnail image_hash)
lanbow-ads videos upload --file /path/to/video.mp4 --name "Q1 Video"
lanbow-ads videos upload --file /path/to/video.mp4 --thumbnail /path/to/thumb.jpg
lanbow-ads videos upload --file /path/to/video.mp4 --auto-thumbnail

# Create creative (simple spec - image)
lanbow-ads creatives create \
  --name "Q1 Creative v1" \
  --page-id PAGE_ID \
  --image-hash IMAGE_HASH \
  --message "Discover our new collection" \
  --headline "Shop Now" \
  --description "Limited time offer" \
  --link "https://example.com/shop" \
  --call-to-action SHOP_NOW

# Create creative (simple spec - video)
# --image-hash is optional but recommended for thumbnail reliability
lanbow-ads creatives create \
  --name "Q1 Video Creative" \
  --page-id PAGE_ID \
  --video-id VIDEO_ID \
  --image-hash THUMBNAIL_HASH \
  --message "Discover our new collection" \
  --headline "Watch Now" \
  --link "https://example.com/shop" \
  --call-to-action SHOP_NOW
```

### 4. Create Ad

```bash
lanbow-ads ads create \
  --name "Q1 Ad v1" \
  --adset-id ADSET_ID \
  --creative-id CREATIVE_ID \
  --status PAUSED
```

## Insights & Analysis

```bash
# Campaign performance last 7 days
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d

# Breakdown by age at adset level
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_30d --breakdowns age --level adset

# Custom date range
lanbow-ads insights get \
  --campaign CAMPAIGN_ID \
  --since 2025-01-01 --until 2025-01-31 \
  --breakdowns country \
  --level campaign
```

**Date presets:** today, yesterday, last_3d, last_7d, last_14d, last_30d, last_90d, this_month, last_month

**Breakdowns:** age, gender, country, region, device_platform, publisher_platform, impression_device

**Levels:** account, campaign, adset, ad

## Targeting Research

```bash
lanbow-ads targeting interests basketball --limit 10
lanbow-ads targeting suggestions --interests "Movies" "Music"
lanbow-ads targeting locations "New York" --type city
lanbow-ads targeting behaviors
lanbow-ads targeting demographics --class demographics
lanbow-ads targeting estimate --targeting '{"age_min":25,"age_max":45,"geo_locations":{"countries":["US"]}}'
```

## Listing & Updating

```bash
# List active campaigns
lanbow-ads campaigns list --status ACTIVE --limit 20

# List ad sets for a campaign
lanbow-ads adsets list --campaign CAMPAIGN_ID

# List ads in an ad set
lanbow-ads ads list --adset ADSET_ID

# Get details
lanbow-ads campaigns get CAMPAIGN_ID
lanbow-ads adsets get ADSET_ID
lanbow-ads ads get AD_ID

# Update status
lanbow-ads campaigns update CAMPAIGN_ID --status PAUSED
lanbow-ads adsets update ADSET_ID --daily-budget 3000
lanbow-ads ads update AD_ID --status ACTIVE

# List and get creatives
lanbow-ads creatives list --limit 10
lanbow-ads creatives get CREATIVE_ID
```

## Pages, Images & Videos

```bash
# List Facebook Pages accessible to user
lanbow-ads pages list

# Get Instagram account linked to a Page
lanbow-ads pages instagram PAGE_ID

# Upload image
lanbow-ads images upload --file /path/to/image.jpg --name "My Ad Image"

# Upload video (supports up to 4 GB; files > 20 MB use chunked upload)
lanbow-ads videos upload --file ./ad-video.mp4 --name "Q1 Video Ad"

# Upload video with local thumbnail image
lanbow-ads videos upload --file ./ad-video.mp4 --thumbnail ./thumb.jpg

# Upload video with auto-extracted thumbnail (waits for Meta processing)
lanbow-ads videos upload --file ./ad-video.mp4 --auto-thumbnail
```

> **Note:** `--thumbnail` and `--auto-thumbnail` are mutually exclusive. Thumbnail extraction is best-effort — a failed thumbnail never hides the video upload result.

## Configuration

```bash
lanbow-ads config set --app-id 123456 --app-secret SECRET
lanbow-ads config set --account act_111
lanbow-ads config get meta_app_id
lanbow-ads config list
lanbow-ads config unset meta_app_secret

# Account aliases — use friendly names instead of act_XXXXX
lanbow-ads config accounts list
lanbow-ads config accounts add main act_111222333
lanbow-ads config accounts add client-a act_444555666 --label "Client A (production)"
lanbow-ads config accounts remove client-a

# Then use alias with any command:
lanbow-ads campaigns list --account main
```

## Pagination

List commands support pagination with `--limit`, `--after` (cursor), and `--all` (fetch all pages):

```bash
lanbow-ads campaigns list --limit 50
lanbow-ads campaigns list --all
lanbow-ads ads list --after CURSOR_VALUE
```

## Targeting Spec Format

The `--targeting` flag accepts a JSON object:

```json
{
  "age_min": 25,
  "age_max": 45,
  "genders": [1],
  "geo_locations": {
    "countries": ["US", "CA"],
    "regions": [{"key": "4081"}],
    "cities": [{"key": "2420605"}]
  },
  "interests": [{"id": "6003392754754", "name": "Nike, Inc."}],
  "behaviors": [{"id": "6002714895372", "name": "Frequent Travelers"}],
  "device_platforms": ["mobile", "desktop"],
  "publisher_platforms": ["facebook", "instagram"]
}
```

`genders`: 1 = male, 2 = female. Omit for all genders.

## Resources

### references/

- **[ad-delivery-commands.md](ad-delivery-commands.md)** - Complete command reference with all flags, types, and descriptions for every subcommand. Consult when exact parameter names, types, or optional fields are needed.
