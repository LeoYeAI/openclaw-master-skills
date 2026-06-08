# PostFast Skill Examples

Ready-to-use request bodies for common social media scheduling scenarios.

## Examples Index

| File | Description |
|------|-------------|
| [cross-platform-post.json](cross-platform-post.json) | Post same content to LinkedIn, X, and Threads |
| [tiktok-video.json](tiktok-video.json) | TikTok video with privacy and brand settings |
| [tiktok-carousel.json](tiktok-carousel.json) | TikTok image carousel (2-35 images) |
| [tiktok-draft.json](tiktok-draft.json) | TikTok video saved as draft |
| [instagram-reel.json](instagram-reel.json) | Instagram Reel with collaborators |
| [instagram-story.json](instagram-story.json) | Instagram Story (video) |
| [instagram-carousel.json](instagram-carousel.json) | Instagram carousel (up to 10 images) |
| [facebook-reel.json](facebook-reel.json) | Facebook Reel with cover timestamp |
| [facebook-story.json](facebook-story.json) | Facebook Story (image) |
| [youtube-short.json](youtube-short.json) | YouTube Short with tags and playlist |
| [pinterest-pin.json](pinterest-pin.json) | Pinterest pin with board and destination link |
| [linkedin-document.json](linkedin-document.json) | LinkedIn document/carousel post (PDF) |
| [x-quote-tweet.json](x-quote-tweet.json) | X quote tweet with commentary and image |
| [x-retweet.json](x-retweet.json) | X scheduled retweet (content ignored) |
| [x-first-comment.json](x-first-comment.json) | X post with automatic first comment |
| [threads-carousel.json](threads-carousel.json) | Threads image carousel (up to 10) |
| [batch-scheduling.json](batch-scheduling.json) | Schedule 5 posts across a week |
| [telegram-mixed-media.json](telegram-mixed-media.json) | Telegram post with mixed media |
| [post-analytics.json](post-analytics.json) | Fetch published post metrics (impressions, likes, etc.) |

## Usage

Each JSON file is a complete request body for `POST /social-posts`. Replace placeholder IDs with real values from `GET /social-media/my-social-accounts`.

For examples with media, complete the 3-step upload flow first (see [references/upload-flow.md](../references/upload-flow.md)) and replace the `key` values with your actual upload keys.
