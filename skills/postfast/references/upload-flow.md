# Media Upload Flow

PostFast uses a 3-step media upload process. External URLs are NOT supported — all media must go through this flow.

## Step 1: Get Signed Upload URLs

```bash
curl -X POST https://api.postfa.st/file/get-signed-upload-urls \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentType": "image/png",
    "count": 1
  }'
```

**Response:**
```json
[
  {
    "key": "image/a1b2c3d4-e5f6-7890-1234-567890abcdef.png",
    "signedUrl": "https://postfast-media.s3.eu-central-1.amazonaws.com/image/a1b2c3d4..."
  }
]
```

For multiple files, set `count` to the number of files. All must share the same content type.

**Key prefix by type:**
- Images: `image/uuid.ext`
- Videos: `video/uuid.ext`
- Documents: `file/uuid.ext`

## Step 2: Upload File to S3

```bash
curl -X PUT "SIGNED_URL_FROM_STEP_1" \
  -H "Content-Type: image/png" \
  --data-binary @/path/to/file.png
```

**Critical:** The `Content-Type` header MUST match what you requested in Step 1. Mismatches cause upload failures.

**Response:** 200 OK with empty body on success.

## Step 3: Create Post with Media Key

Use the `key` from Step 1 in the `mediaItems` array:

```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "content": "Check out this photo!",
      "mediaItems": [
        {
          "key": "image/a1b2c3d4-e5f6-7890-1234-567890abcdef.png",
          "type": "IMAGE",
          "sortOrder": 0
        }
      ],
      "scheduledAt": "2026-06-15T10:00:00.000Z",
      "socialMediaId": "ACCOUNT_ID"
    }],
    "controls": {}
  }'
```

## Carousel Upload (Multiple Images)

For carousels (Instagram, Facebook, TikTok, Pinterest, LinkedIn):

1. Request multiple signed URLs: `{ "contentType": "image/png", "count": 5 }`
2. Upload each file to its respective signed URL
3. Include all keys in `mediaItems` with sequential `sortOrder`:

```json
{
  "mediaItems": [
    { "key": "image/uuid-1.png", "type": "IMAGE", "sortOrder": 0 },
    { "key": "image/uuid-2.png", "type": "IMAGE", "sortOrder": 1 },
    { "key": "image/uuid-3.png", "type": "IMAGE", "sortOrder": 2 }
  ]
}
```

## LinkedIn Document Upload

Documents use a different flow — `linkedinAttachmentKey` instead of `mediaItems`:

1. Get signed URL: `{ "contentType": "application/pdf", "count": 1 }`
2. Upload file to signed URL
3. Use the key in `controls`, NOT in `mediaItems`:

```json
{
  "posts": [{
    "content": "Our Q1 playbook in 12 slides",
    "mediaItems": [],
    "scheduledAt": "2026-06-15T10:00:00.000Z",
    "socialMediaId": "LINKEDIN_ACCOUNT_ID"
  }],
  "controls": {
    "linkedinAttachmentKey": "file/uuid.pdf",
    "linkedinAttachmentTitle": "Q1 Marketing Playbook"
  }
}
```

## TikTok Video Thumbnail

Set `coverTimestamp` in the media item to pick a frame as the thumbnail:

```json
{
  "mediaItems": [{
    "key": "video/uuid.mp4",
    "type": "VIDEO",
    "sortOrder": 0,
    "coverTimestamp": "3"
  }]
}
```

The value is in seconds (e.g., `"3"` = 3 seconds into the video).
