# Platform-Specific Controls Reference

All controls are passed in the `controls` object of `POST /social-posts`.

## TikTok

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tiktokPrivacy` | string | `PUBLIC` | `PUBLIC`, `MUTUAL_FRIENDS`, `ONLY_ME` |
| `tiktokAllowComments` | boolean | `true` | Allow comments |
| `tiktokAllowDuet` | boolean | `true` | Allow duets |
| `tiktokAllowStitch` | boolean | `true` | Allow stitches |
| `tiktokBrandOrganic` | boolean | `false` | Self-promotional content |
| `tiktokBrandContent` | boolean | `false` | Sponsored/partnership content |
| `tiktokAutoAddMusic` | boolean | `false` | Auto-add background music |
| `tiktokIsDraft` | boolean | `false` | Save as draft (appears in TikTok app only) |

**Media notes:**
- Video: MP4/MOV, H.264, ≤250MB, 3s-10min. Best: 15-30s, 1080×1920 (9:16)
- Carousels: 2-35 images (photo slideshows)
- `coverTimestamp` in mediaItems: seconds into video for thumbnail (e.g., `"3"`)
- Caption: max 2,200 characters

## Instagram

| Parameter | Type | Default | Description |
|---|---|---|---|
| `instagramPublishType` | string | `TIMELINE` | `TIMELINE`, `STORY`, `REEL` |
| `instagramPostToGrid` | boolean | `true` | Show Reel on profile grid |
| `instagramCollaborators` | string[] | `[]` | Usernames (without @), max 3 |

**Content types:**
- **TIMELINE**: Feed posts. Single image, carousel (up to 10), or video
- **STORY**: 24-hour temporary content. Image or video
- **REEL**: Short-form video, 3-90 seconds, 9:16 recommended. Gets algorithm boost (2-3x reach vs feed)

**Media notes:**
- Video: ≤1GB for Reels
- Carousels: up to 10 images or videos

## Facebook

| Parameter | Type | Default | Description |
|---|---|---|---|
| `facebookContentType` | string | `POST` | `POST`, `REEL`, `STORY` |
| `facebookReelsCollaborators` | string[] | `[]` | Facebook usernames for Reel collaboration |

**Content types:**
- **POST**: Permanent feed content. Up to 10 images OR 1 video (not mixed). Text limit: 63,206 chars
- **REEL**: Short-form vertical video, 1 video only
- **STORY**: 24-hour temporary content, 1 image or 1 video

**Media notes:**
- Images: JPG/PNG, ≤30MB each, up to 10 per post
- Cannot mix images and videos in same post

## YouTube

| Parameter | Type | Default | Description |
|---|---|---|---|
| `youtubeIsShort` | boolean | `true` | Publish as YouTube Short |
| `youtubeTitle` | string | — | Video title (max 100 chars). Falls back to first 100 chars of content |
| `youtubePrivacy` | string | `PUBLIC` | `PUBLIC`, `UNLISTED`, `PRIVATE` |
| `youtubePlaylistId` | string | — | Add to playlist after publishing. Get IDs from `GET /social-media/{id}/youtube-playlists` |
| `youtubeMadeForKids` | boolean | `false` | COPPA compliance flag |
| `youtubeTags` | string[] | `[]` | Video tags |
| `youtubeCategoryId` | string | — | YouTube category ID |

**Media notes:**
- Shorts: up to 3 minutes, 9:16 or 1:1
- Copyrighted music limits Shorts to 60 seconds
- H.264 video codec with AAC audio recommended

## LinkedIn

| Parameter | Type | Default | Description |
|---|---|---|---|
| `linkedinAttachmentKey` | string | — | S3 key for document post (from `/file/get-signed-upload-urls`). Format: `file/{uuid}.{ext}` |
| `linkedinAttachmentTitle` | string | `Document` | Display title for document |

**Content types:**
- Regular posts: text + images (up to 9) or video (up to 10 min)
- Document posts: PDF, PPTX, DOCX (display as swipeable carousels). Use `linkedinAttachmentKey` instead of `mediaItems`. ≤60MB
- Cannot mix documents with regular media

**Tips:**
- Character limit: 3,000 (under 1,300 performs better)
- Put links in comments, not post body (LinkedIn deprioritizes external links)
- 3-5 hashtags max

## X (Twitter)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `xQuoteTweetUrl` | string | — | URL of tweet to quote with your own commentary. Supports content and media attachments |
| `xRetweetUrl` | string | — | URL of tweet to retweet without changes. Content and media are ignored |
| `xCommunityId` | string | — | Community ID for posting to an X Community |

**URL formats accepted:** `x.com`, `twitter.com`, `mobile.twitter.com`. Example: `https://x.com/username/status/1234567890`

**Important:**
- Cannot use `xQuoteTweetUrl` and `xRetweetUrl` together — pick one
- Quote tweets support your own content + media attachments
- Retweets share the original tweet — any content/media provided will be ignored
- Character limit: 280
- Up to 4 images per post
- **API limit: 5 posts per account per day** — exceeding risks account restrictions

## Pinterest

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pinterestBoardId` | string | **required** | Board to pin to. Get IDs from `GET /social-media/{id}/pinterest-boards` |
| `pinterestLink` | string | — | Destination URL when pin is clicked |

**Content parsing:**
- First line of `content` → pin title (max 100 chars)
- Remaining lines → pin description (max 800 chars)

**Media notes:**
- Ideal aspect ratio: 2:3 (1000×1500)
- Carousels: 2-5 static images only (no video in carousels)

## Bluesky

No platform-specific controls.

**Notes:**
- Character limit: 300
- Up to 4 images
- No video support via API
- URLs auto-generate link cards
- No edit after publishing

## Threads

No platform-specific controls.

**Notes:**
- Text + images + video supported
- Carousels: up to 10 images

## Telegram

No platform-specific controls.

**Notes:**
- Character limit: 4,096
- Up to 10 images, videos, or mixed media per post
- Supports channels and groups
