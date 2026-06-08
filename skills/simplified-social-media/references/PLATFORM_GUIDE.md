# Platform Reference Guide

Detailed per-platform parameter reference for `createSocialMediaPost`. All settings go inside the `additional` object, grouped by platform name:

## Character Limits

Always respect these limits when composing post messages:

| Platform        | Message limit |
|-----------------|--------------|
| LinkedIn        | 3000 chars   |
| Facebook        | 2200 chars   |
| Instagram       | 2200 chars   |
| TikTok          | 2200 chars   |
| YouTube         | 2200 chars   |
| Pinterest       | 500 chars    |
| Threads         | 500 chars    |
| Google Business | 1500 chars   |
| Bluesky         | 300 chars    |

---


```json
"additional": {
  "instagram": {
    "postType": { "value": "story" },
    "channel":  { "value": "direct" }
  }
}
```

**Bold** = required field.

---

## Facebook

Required additionals: **`postType`**

### `facebook.postType` *(required)*

| Property  | Type   | Values                  | Default |
|-----------|--------|-------------------------|---------|
| **value** | string | `post`, `reel`, `story` | `post`  |

**Post type constraints:**

| Type    | Message  | Photos  | Videos                                      |
|---------|----------|---------|---------------------------------------------|
| `post`  | max 2200 | max 10  | max 1, up to 4h                             |
| `reel`  | max 2200 | ✗       | max 1, 4s–90s, 9:16, min 540×960 *(video required)* |
| `story` | ✗ (must be empty) | max 1 | max 1, 3s–60s, 9:16 *(media required)* |

---

## Instagram

Required additionals: **`postType`**, **`channel`**

### `instagram.postType` *(required)*

| Property  | Type   | Values                  | Default |
|-----------|--------|-------------------------|---------|
| **value** | string | `post`, `reel`, `story` | `post`  |

### `instagram.channel` *(required)*

| Property  | Type   | Values               | Default  |
|-----------|--------|----------------------|----------|
| **value** | string | `direct`, `reminder` | `direct` |

- **`direct`** — publish immediately
- **`reminder`** — send as a reminder notification instead of direct publish

### `instagram.postReel`

Only applies when `postType.value` is `reel`.

| Property      | Type    | Default | Description                         |
|---------------|---------|---------|-------------------------------------|
| `audioName`   | string  | —       | Audio track name (max 255 chars)    |
| `shareToFeed` | boolean | `true`  | Also show the reel in the main feed |

**Post type constraints:**

| Type    | Message | Photos | Videos                                      |
|---------|---------|--------|---------------------------------------------|
| `post`  | max 2200 | max 10 | max 10, 3s–15min                           |
| `reel`  | max 2200 | ✗      | max 1, 3s–60s *(video required)*           |
| `story` | ✗ (must be empty) | max 1 | max 1, 3s–60s            |

---

## TikTok

Required additionals: **`postType`**, **`channel`**, **`post`**

### `tiktok.postType` *(required)*

| Property  | Type   | Values          | Default |
|-----------|--------|-----------------|---------|
| **value** | string | `video`, `photo` | `video` |

### `tiktok.channel` *(required)*

| Property  | Type   | Values               | Default  |
|-----------|--------|----------------------|----------|
| **value** | string | `direct`, `reminder` | `direct` |

- **`direct`** — publish immediately
- **`reminder`** — send as a reminder notification instead of direct publish

### `tiktok.post` *(required for video)*

| Property        | Type    | Values / Default                                                         |
|-----------------|---------|--------------------------------------------------------------------------|
| **privacyStatus** | string | `PUBLIC_TO_EVERYONE`, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`, `SELF_ONLY` / `PUBLIC_TO_EVERYONE` |
| `brandContent`  | boolean | `false`                                                                  |
| `brandOrganic`  | boolean | `false`                                                                  |
| `duetDisabled`  | boolean | `true`                                                                   |
| `stitchDisabled`| boolean | `true`                                                                   |
| `commentDisabled`| boolean | `true`                                                                  |

### `tiktok.postPhoto` *(required for photo)*

Only when `postType.value` is `photo`.

| Property         | Type    | Default              |
|------------------|---------|----------------------|
| `title`          | string  | `""` (max 90 chars)  |
| **privacyStatus**| string  | `PUBLIC_TO_EVERYONE` |
| `commentDisabled`| boolean | `true`               |
| `autoAddMusic`   | boolean | `false`              |
| `brandContent`   | boolean | `false`              |
| `brandOrganic`   | boolean | `false`              |

---

## TikTok Business

Required additionals: **`postType`**, **`post`**

### `tiktokBusiness.postType` *(required)*

Same values as TikTok: `video`, `photo`.

### `tiktokBusiness.post` *(required)*

Same as `tiktok.post` plus:

| Property       | Type    | Default |
|----------------|---------|---------|
| `aiGenerated`  | boolean | `false` |
| `uploadToDraft`| boolean | `false` |

### `tiktokBusiness.postPhoto`

Same fields as `tiktok.postPhoto`.

---

## YouTube

Required additionals: **`postType`**

### `youtube.postType` *(required)*

| Property  | Type   | Values          | Default |
|-----------|--------|-----------------|---------|
| **value** | string | `video`, `short` | `video` |

- **`short`** constraints: max 60s, max ratio 1:1, min 600×600

### `youtube.post`

| Property                  | Type   | Values                                 | Default |
|---------------------------|--------|----------------------------------------|---------|
| **title**                 | string | max 100 chars (required)               | —       |
| **privacyStatus**         | string | `""`, `public`, `private`, `unlisted`  | `""`    |
| `license`                 | string | `""`, `youtube`, `creativeCommon`      | `""`    |
| `selfDeclaredMadeForKids` | string | `""`, `yes`, `no`                      | `""`    |
| `publishAt`               | string | datetime string                        | `""`    |

---

## LinkedIn

Required additionals: **`audience`**

### `linkedin.audience` *(required)*

| Property  | Type   | Values                          | Default  |
|-----------|--------|---------------------------------|----------|
| **value** | string | `PUBLIC`, `CONNECTIONS`, `LOGGED_IN` | `PUBLIC` |

**Message limit:** 3000 chars.

---

## Pinterest

Required additionals: **`post`**

### `pinterest.post` *(required)*

| Property   | Type   | Description                    |
|------------|--------|--------------------------------|
| `title`    | string | Pin title (max 100 chars)      |
| `link`     | string | Destination URL                |
| `imageAlt` | string | Alt text (max 500 chars)       |

Pinterest always requires at least one image in `media`.

---

## Threads

Required additionals: **`channel`**

### `threads.channel` *(required)*

| Property  | Type   | Values               | Default  |
|-----------|--------|----------------------|----------|
| **value** | string | `direct`, `reminder` | `direct` |

- **`direct`** — publish immediately
- **`reminder`** — send as a reminder notification instead of direct publish

---

## Google Business Profile

Required additionals: **`post`**

### `google.post` *(required)*

| Property           | Type   | Values / Description                                          |
|--------------------|--------|---------------------------------------------------------------|
| **topicType**      | string | `STANDARD`, `EVENT`, `OFFER` (default: `STANDARD`)           |
| `title`            | string | Post title (max 58 chars)                                     |
| `callToActionType` | string | `""`, `BOOK`, `ORDER`, `SHOP`, `LEARN_MORE`, `SIGN_UP`, `CALL` |
| `callToActionUrl`  | string | URL for CTA (required when CTA is not `CALL` or empty)        |
| `startDate`        | string | Required for `EVENT` and `OFFER`                              |
| `endDate`          | string | Required for `OFFER`                                          |
| `couponCode`       | string | Required for `OFFER`                                          |
| `redeemOnlineUrl`  | string | Required for `OFFER`                                          |
| `termsConditions`  | string | Required for `OFFER`                                          |

**Message limit:** 1500 chars. No videos allowed.

---

## Bluesky

No required additionals. No platform-specific `additional` settings.

**Message limit:** 300 chars. Max 4 photos or 1 video (max 60s).
