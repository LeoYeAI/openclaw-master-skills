# Analytics Reference Guide

Detailed reference for the four analytics tools: `getSocialMediaAnalyticsRange`, `getSocialMediaAnalyticsPosts`, `getSocialMediaAnalyticsAggregated`, `getSocialMediaAnalyticsAudience`.

---

## General Rules

- **`date_to` must not be in the future** — analytics data does not exist for future dates. When a user asks for "this month" and today is March 10, set `date_to` to today (`2026-03-10`), not the end of the month.
- **LinkedIn account type** — check the `type` field from `getSocialMediaAccounts`: `"LinkedIn company"` = use Company metrics set, `"LinkedIn profile"` = use Personal metrics set.

---

## Relative Date Ranges

Translate common user expressions to concrete dates using today's date:

| User says | `date_from` | `date_to` |
|---|---|---|
| last 7 days | today − 7 days | today |
| last 30 days | today − 30 days | today |
| last 90 days | today − 90 days | today |
| this week | Monday of current week | today |
| last week | Monday of last week | Sunday of last week |
| this month | 1st of current month | today |
| last month | 1st of last month | last day of last month |
| this year | January 1 of current year | today |
| last year | January 1 of last year | December 31 of last year |

Always cap `date_to` at today — never use a future date.

---

## Timezone

Analytics day boundaries depend on timezone. UTC is the default but can produce misleading data for users in other timezones (e.g. a post published at 23:00 Warsaw time appears on the next day in UTC).

**Rules:**
- If the user mentions a timezone or location (e.g. "Warsaw", "New York", "CET"), pass it as `tz` using IANA format (e.g. `Europe/Warsaw`, `America/New_York`)
- If the user's timezone is known from context, always pass `tz` explicitly
- If timezone is unknown and the data is time-sensitive (daily breakdown), ask the user before proceeding
- For simple totals or aggregated KPIs, UTC is acceptable without asking

---

## Default Metrics per Network

Use these when the user does not specify metrics for `getSocialMediaAnalyticsRange`:

| Network | Default metrics |
|---|---|
| Facebook | `total_fans`, `total_follows`, `new_fan`, `page_reach`, `post_reach_total`, `post_reach_viral`, `post_impression_total`, `page_post_engagements`, `reactions`, `link_clicks`, `engaged_users` |
| Instagram | `follower_count`, `reach`, `accounts_engaged`, `total_interactions`, `saves`, `profile_views`, `profile_links_taps`, `website_clicks` |
| LinkedIn (Company) | `allFollowers`, `unique_impressions`, `engagement`, `clicks`, `shares`, `comments` |
| LinkedIn (Personal) | `memberFollowers`, `impressions`, `reactions`, `comments`, `shares` |
| TikTok Personal | `follower_count`, `likes_count`, `posts_count` |
| TikTok Business | `followers_count`, `video_views`, `profile_views`, `comments`, `shares` |
| YouTube | `views`, `estimatedMinutesWatched`, `averageViewDuration`, `likes`, `dislikes`, `comments` |
| Pinterest | `impression`, `save`, `save_rate`, `outbound_click`, `outbound_click_rate`, `pin_click_rate`, `video_avg_watch_time`, `engagement_rate` |
| Threads | `followers_count`, `views`, `reposts`, `quotes`, `replies`, `clicks` |
| Google | `queries_direct`, `queries_indirect`, `views_search`, `views_maps`, `actions_website`, `actions_phone`, `actions_driving_directions` |

> For TikTok Business audience demographics (gender, country breakdown) use `getSocialMediaAnalyticsAudience` instead of Range.

---

## Available Metrics by Network

Use these values in the `metrics` array for `getSocialMediaAnalyticsRange`. Unknown metrics are silently ignored by the API.

### Instagram

| Metric                | Description                           |
|-----------------------|---------------------------------------|
| `views`               | Video/content views                   |
| `reach`               | Unique accounts reached               |
| `profile_views`       | Profile page visits                   |
| `follower_count`      | Total followers                       |
| `text_message_clicks` | Clicks on text message button         |
| `website_clicks`      | Clicks on website link                |
| `email_contacts`      | Email button taps                     |
| `posts_count`         | Posts published                       |
| `accounts_engaged`    | Accounts that interacted with content |
| `profile_links_taps`  | Taps on profile links                 |
| `replies`             | Story/reel replies                    |
| `shares`              | Content shares                        |
| `saves`               | Content saves                         |
| `total_interactions`  | Sum of all interactions               |
| `impressions`         | *(deprecated)* Total impressions      |

### Facebook

| Metric                   | Description                              |
|--------------------------|------------------------------------------|
| `engaged_users`          | Users who engaged with page content      |
| `post_impression`        | Organic impressions                      |
| `post_impression_total`  | Total impressions (all sources)          |
| `post_reach_total`       | Total unique reach                       |
| `post_impression_paid`   | Paid impressions                         |
| `post_reach_paid`        | Paid unique reach                        |
| `post_reach`             | Organic unique reach                     |
| `page_post_engagements`  | Total page engagements                   |
| `new_fan`                | New page likes/follows                   |
| `reactions`              | Total reactions                          |
| `total_fans`             | Total page likes                         |
| `total_follows`          | Total page follows                       |
| `link_clicks`            | Link clicks in posts                     |
| `video_play`             | Video plays                              |
| `other_clicks`           | Other clicks (not link/photo)            |
| `photo_view`             | Photo views                              |
| `posts_count`            | Posts published                          |
| `post_reach_viral`       | Viral reach                              |
| `page_reach`             | Total page reach                         |

### LinkedIn (Company)

| Metric               | Description                    |
|----------------------|--------------------------------|
| `posts_count`        | Posts published                |
| `impressions`        | Total impressions              |
| `unique_impressions` | Unique impressions             |
| `comments`           | Total comments                 |
| `likes`              | Total likes                    |
| `clicks`             | Total clicks                   |
| `engagement`         | Engagement rate                |
| `shares`             | Total shares                   |
| `allFollowers`       | Total followers (all sources)  |
| `organicFollowers`   | Organic followers              |
| `paidFollowers`      | Paid/sponsored followers       |

### LinkedIn (Personal)

| Metric            | Description      |
|-------------------|------------------|
| `memberFollowers` | Total followers  |
| `impressions`     | Total impressions |
| `comments`        | Total comments   |
| `reactions`       | Total reactions  |
| `shares`          | Total shares     |

### Twitter / X

| Metric          | Description        |
|-----------------|--------------------|
| `posts_count`   | Posts published    |
| `retweetCount`  | Total retweets     |
| `replyCount`    | Total replies      |
| `likeCount`     | Total likes        |
| `quoteCount`    | Total quote tweets |

### YouTube

| Metric                    | Description                     |
|---------------------------|---------------------------------|
| `views`                   | Total video views               |
| `comments`                | Total comments                  |
| `likes`                   | Total likes                     |
| `dislikes`                | Total dislikes                  |
| `estimatedMinutesWatched` | Total minutes watched           |
| `averageViewDuration`     | Average view duration (seconds) |
| `posts_count`             | Videos published                |

### Pinterest

| Metric                     | Description                               |
|----------------------------|-------------------------------------------|
| `engagement_rate`          | Overall engagement rate                   |
| `save`                     | Total saves (repins)                      |
| `pin_click_rate`           | Pin click-through rate                    |
| `outbound_click`           | Clicks out to destination URLs            |
| `video_mrc_view`           | MRC views (2+ sec, 50% visible)           |
| `video_avg_watch_time`     | Average video watch time                  |
| `impression`               | Total impressions                         |
| `engagement`               | Total engagements                         |
| `video_v50_watch_time`     | Watch time at 50% completion              |
| `outbound_click_rate`      | Outbound click rate                       |
| `save_rate`                | Save rate                                 |
| `quartile_95_percent_view` | Views reaching 95% completion             |
| `video_start`              | Video starts                              |
| `video_10s_view`           | Views lasting 10+ seconds                 |
| `pin_click`                | Total pin clicks                          |
| `posts_count`              | Pins published                            |

### TikTok (Personal)

| Metric           | Description          |
|------------------|----------------------|
| `posts_count`    | Videos published     |
| `follower_count` | Total followers      |
| `likes_count`    | Total likes received |

### TikTok Business

| Metric               | Description                         |
|----------------------|-------------------------------------|
| `posts_count`        | Videos published                    |
| `audience_genders`   | Gender distribution of audience     |
| `audience_countries` | Audience distribution by country    |
| `comments`           | Total comments                      |
| `shares`             | Total shares                        |
| `audience_activity`  | Audience activity by time of day    |
| `profile_views`      | Profile page views                  |
| `followers_count`    | Total followers                     |
| `video_views`        | Total video views                   |

### Threads

| Metric           | Description          |
|------------------|----------------------|
| `views`          | Total views          |
| `followers_count`| Total followers      |
| `likes`          | Total likes          |
| `replies`        | Total replies        |
| `reposts`        | Total reposts        |
| `quotes`         | Total quote reposts  |
| `clicks`         | Total link clicks    |
| `posts_count`    | Posts published      |

### Google My Business

| Metric                                 | Description                          |
|----------------------------------------|--------------------------------------|
| `posts_count`                          | Posts published                      |
| `queries_indirect`                     | Discovery searches                   |
| `queries_direct`                       | Direct searches by business name     |
| `queries_chain`                        | Chain searches                       |
| `views_maps`                           | Views on Google Maps                 |
| `views_search`                         | Views on Google Search               |
| `actions_website`                      | Website clicks                       |
| `actions_phone`                        | Phone calls initiated                |
| `actions_driving_directions`           | Driving direction requests           |
| `business_impressions_desktop_maps`    | Desktop Maps impressions             |
| `business_impressions_mobile_maps`     | Mobile Maps impressions              |
| `business_impressions_mobile_search`   | Mobile Search impressions            |
| `business_impressions_desktop_search`  | Desktop Search impressions           |

---

## Response Structures

### AnalyticsMetric (shared schema)

All analytics tools return metrics using this unified shape:

```json
{
  "id": "reach",
  "value": 4500,
  "prevValue": 3800
}
```

| Field       | Type   | Description                                             |
|-------------|--------|---------------------------------------------------------|
| `id`        | string | Metric identifier (e.g. `reach`, `impressions`)         |
| `value`     | number | Value for the requested period                          |
| `prevValue` | number | Value for the equivalent previous period (for % change) |

---

### `getSocialMediaAnalyticsRange`

```json
{
  "data": [
    {
      "date": "2026-02-01",
      "metrics": [
        { "id": "reach",       "value": 1200, "prevValue": 980 },
        { "id": "impressions", "value": 3400, "prevValue": 2900 }
      ]
    },
    {
      "date": "2026-02-02",
      "metrics": [
        { "id": "reach",       "value": 1350, "prevValue": 1100 },
        { "id": "impressions", "value": 3800, "prevValue": 3100 }
      ]
    }
  ],
  "baseLine": {
    "reach":       { "id": "reach",       "value": 45000, "prevValue": 38000 },
    "impressions": { "id": "impressions", "value": 98000, "prevValue": 81000 }
  },
  "additional": {
    "reach": [
      { "id": "reach_28d", "value": 62000, "prevValue": 55000 }
    ]
  }
}
```

| Field        | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `data`       | Per-day time-series — one entry per day in the requested range           |
| `baseLine`   | Aggregated totals/averages for the whole period, keyed by metric ID      |
| `additional` | Extra metrics computed over different windows (e.g., 28-day reach); may be absent or empty |

---

### `getSocialMediaAnalyticsPosts`

```json
{
  "all_posts_count": 42,
  "current_page": 1,
  "pages_count": 3,
  "posts": [
    {
      "id": "post_abc123",
      "message": "Post caption text",
      "publishedDate": {
        "date": "2026-02-15 10:30:00.000000",
        "timezone_type": 3,
        "timezone": "UTC"
      },
      "postUrl": "https://www.instagram.com/p/abc123/",
      "postType": "IMAGE",
      "media": [
        { "type": "image", "url": "https://cdn.example.com/img.jpg" }
      ],
      "metrics": {
        "impressions": 4500,
        "reach": 3200,
        "likes": 120,
        "comments": 8
      }
    }
  ]
}
```

Per-post `metrics` fields vary by social network.

---

### `getSocialMediaAnalyticsAggregated`

```json
{
  "data": [
    {
      "date": "2026-02-01",
      "metrics": [
        { "id": "impressions_aggregated", "value": 1200, "prevValue": 980 }
      ]
    }
  ],
  "baseLine": {
    "impressions_aggregated": { "id": "impressions_aggregated", "value": 45000, "prevValue": 38000 },
    "engagement_aggregated":  { "id": "engagement_aggregated",  "value": 2300,  "prevValue": 1900 },
    "followers_aggregated":   { "id": "followers_aggregated",   "value": 12500, "prevValue": 11800 },
    "publishing_aggregated":  { "id": "publishing_aggregated",  "value": 28,    "prevValue": 24 }
  }
}
```

`baseLine` always contains these four KPIs:

| Key                       | Meaning                           |
|---------------------------|-----------------------------------|
| `impressions_aggregated`  | Total impressions for the period  |
| `engagement_aggregated`   | Total engagements for the period  |
| `followers_aggregated`    | Follower count / growth           |
| `publishing_aggregated`   | Number of posts published         |

---

### `getSocialMediaAnalyticsAudience`

```json
{
  "data": {
    "audience_page_fans_gender_age": {
      "M.18-24": 450,
      "F.25-34": 1200,
      "U.35-44": 80
    },
    "audience_page_fans_country": {
      "US": 5400,
      "PL": 1200,
      "DE": 800
    },
    "audience_page_fans_city": {
      "New York": 900,
      "Warsaw": 600
    }
  }
}
```

| Field                          | Description                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| `audience_page_fans_gender_age`| Keys are `{gender}.{age_range}` — gender: `M`, `F`, `U`                    |
| `audience_page_fans_country`   | Follower count by ISO country code                                          |
| `audience_page_fans_city`      | Follower count by city name                                                 |

Not all fields are available for every network. Missing fields may be an empty array `[]` or absent entirely.
