# Changelog

## v1.1.0 (2026-02-12)

### New Features

- **Feishu Video Sending Guide**: Added `how_to_send_video_via_feishu_app.md` with a complete guide on how to send generated videos to Feishu (Lark) chats using OpenClaw.
  - End-to-end workflow: Generate video → Save locally → Send via message tool → Feishu API upload → Feishu delivery
  - Includes message tool usage examples
  - Feishu Open API details (upload credentials, CDN upload, message sending)
  - Authentication & permissions guide (ARK_API_KEY, Feishu app_access_token)
  - Key technical notes (file size limits, supported formats, timeout handling, rate limits)

## v1.0.0 (2026-02-12)

- Initial release
- Supports Seedance 1.5 Pro, 1.0 Pro, 1.0 Pro Fast, and 1.0 Lite models
- Text-to-video, Image-to-video (first frame, first+last frame, reference images)
- Python CLI tool (`seedance_byteplus.py`)
- Full curl command examples
- All documentation in English
