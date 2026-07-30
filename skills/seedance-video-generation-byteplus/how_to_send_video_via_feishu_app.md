## Sending Videos via Feishu App (OpenClaw)

In OpenClaw, after generating a video with this skill, you can send it to a Feishu (Lark) chat using the built-in `message` tool.

### Complete Workflow Overview

Generate video → Save locally → Send via message tool → Feishu API processing → Upload to Feishu CDN → Deliver to chat

### Step 1: Generate the Video File

Use the `seedance-video-byteplus` skill to generate a video:

```bash
python3 /root/.openclaw/workspace/skills/seedance-video-generation/seedance.py \
  create \
  --prompt "New Year celebration scene..." \
  --ratio 9:16 \
  --duration 5 \
  --resolution 1080p \
  --generate-audio true \
  --wait \
  --download /root/.openclaw/workspace
```

Output: local video file path, e.g.:
`/root/.openclaw/workspace/seedance_cgt-20260212104701-nqcr7_1770864513.mp4`

### Step 2: Send the Video Using the message Tool

Call OpenClaw's `message` tool:

```python
message(
  action="send",           # Action: send message
  channel="feishu",        # Target channel: Feishu
  filePath="/root/.openclaw/workspace/seedance_cgt-20260212104701-nqcr7_1770864513.mp4",  # Local video path
  message="Video description text"    # Optional caption
)
```

### Step 3: Internal Processing by the message Tool

After receiving the request, the `message` tool performs the following operations:

#### 3.1 Read the Local File

```python
with open(filePath, 'rb') as f:
    file_content = f.read()
```

#### 3.2 Call Feishu Open API

The tool calls the Feishu Open Platform API with the following steps:

**a) Obtain Upload Credentials**

```
POST https://open.feishu.cn/open-apis/drive/v1/medias/upload_all
```

Request parameters:
- `file_type`: video/mp4
- `file_name`: seedance_cgt-xxx.mp4
- `file_size`: [file size]

Response:
```json
{
  "code": 0,
  "data": {
    "upload_token": "xxxxx",
    "upload_url": "https://xxx.com/upload..."
  }
}
```

**b) Upload File to Feishu CDN**

```
PUT {upload_url}
Content-Type: video/mp4
Authorization: Bearer {upload_token}

[Video binary data]
```

**c) Send Message to Feishu Chat**

```
POST https://open.feishu.cn/open-apis/im/v1/messages/send
```

Request parameters:
```json
{
  "receive_id_type": "open_id",
  "receive_id": "ou_f323dd2c97951b029f7c43505c4b7566",
  "msg_type": "file",
  "content": "{\"file_key\":\"xxx\",\"file_name\":\"video.mp4\"}"
}
```

### Authentication & Permissions

The following permissions are required throughout the workflow:

| Step | Required Permission | Configuration Location |
|------|-------------------|----------------------|
| Video generation | BytePlus ARK_API_KEY | Environment variable |
| Read local file | File system read access | `/root/.openclaw/workspace/` |
| Feishu API calls | Feishu app_access_token | OpenClaw Feishu settings |

To obtain the Feishu app_access_token:

```
POST https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal
```

Use the `feishu.app_id` and `feishu.app_secret` configured in OpenClaw.

### Feishu Processing & Delivery

After Feishu receives the message:
1. **Store video**: The video file is uploaded to Feishu CDN storage
2. **Generate resource key**: A unique `file_key` is assigned to the video
3. **Deliver to client**: The Feishu client receives the message, downloads the video preview from CDN, and displays a video player in the chat window

### Complete Workflow Diagram

```
┌──────────────────┐
│   User Request    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Seedance Generate │ → BytePlus Ark API call
│     Video         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Save to Local     │ → /root/.openclaw/workspace/
│     File          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ message Tool Call │ → Read local file
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Feishu API Upload │ → 1. Get upload_token
│                   │ → 2. Upload to Feishu CDN
│                   │ → 3. Send message
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Feishu Delivers   │
│   to Client       │
└──────────────────┘
```

### Key Technical Details

1. **File size limit**: Feishu supports video files up to 100MB. Files exceeding this limit require chunked upload.
2. **Supported video formats**: MP4 (recommended), MOV, AVI, WebM
3. **Upload timeout**: Large file uploads may time out. It is recommended to keep videos under 10MB.
4. **API rate limits**: Feishu API has QPS limits. Be mindful of throttling when sending frequently.

### Summary

The core workflow is: 1. Generate locally → 2. Save locally → 3. Tool packaging → 4. API upload → 5. Feishu delivery

OpenClaw's `message` tool already encapsulates steps 3-5. You only need to provide the local file path!
