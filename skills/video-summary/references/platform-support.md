# Platform Support Details | 平台支持详情

Detailed information about subtitle extraction and transcription for each supported platform.

各平台字幕提取和转写的详细信息。

---

## YouTube

**Subtitle Extraction | 字幕提取**: ✅ Native CC + auto-generated

### How it works | 工作原理
- yt-dlp can download both manual and auto-generated subtitles | yt-dlp 可下载手动和自动生成字幕
- Supports 100+ languages | 支持 100+ 种语言
- Subtitle formats: VTT, SRT, TTML | 字幕格式

### Best practices | 最佳实践
- Use `--lang` to specify preferred language | 使用 `--lang` 指定首选语言
- Auto-generated subtitles are usually sufficient | 自动生成字幕通常足够
- For lectures/tutorials, manual CC is more accurate | 讲座/教程类视频，手动 CC 更准确

### URL Formats | URL 格式
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
```

### Example | 示例
```bash
# Get English subtitles | 获取英文字幕
video-summary "https://www.youtube.com/watch?v=xxxxx" --lang en

# Get auto-generated Chinese subtitles | 获取自动生成中文字幕
video-summary "https://www.youtube.com/watch?v=xxxxx" --lang zh-Hans
```

---

## Bilibili (B站)

**Subtitle Extraction | 字幕提取**: ✅ Native CC + backup methods

### How it works | 工作原理
- B站 has CC subtitles for many videos | B站许多视频有 CC 字幕
- yt-dlp can extract B站 subtitles | yt-dlp 可提取 B站字幕
- Backup: Download video and transcribe | 备用：下载视频并转写

### Limitations | 限制
- Not all videos have CC | 不是所有视频都有 CC
- Some videos require login for subtitle access | 部分视频需要登录才能访问字幕
- Live recordings rarely have subtitles | 录播视频很少有字幕

### URL Formats | URL 格式
```
https://www.bilibili.com/video/BVxxxxxxxx
https://www.bilibili.com/video/av123456
https://b23.tv/xxxxxxxx  (短链接)
```

### Best practices | 最佳实践
- For tech videos, CC availability is ~70% | 科技类视频 CC 可用率约 70%
- Use `--transcribe` for videos without CC | 无 CC 视频使用 `--transcribe`
- Short videos (<5min) work best | 短视频（<5分钟）效果最佳

### Example | 示例
```bash
# Standard extraction | 标准提取
video-summary "https://www.bilibili.com/video/BV1xx411c7mu"

# Force transcription | 强制转写
video-summary "https://www.bilibili.com/video/BV1xx411c7mu" --transcribe
```

---

## Xiaohongshu (小红书)

**Subtitle Extraction | 字幕提取**: ⚠️ Limited (requires transcription)

### Current Status | 当前状态
- No native subtitle API | 无原生字幕 API
- Platform uses embedded text in videos | 平台使用视频内嵌文字
- Requires transcription for most content | 大部分内容需要转写
- **风控严格** — May need cookies | Strict rate limiting, may need cookies

### URL Formats | URL 格式
```
https://www.xiaohongshu.com/explore/NOTE_ID
https://xhslink.com/xxxxxxxx  (短链接)
```

### How it works | 工作原理
1. Download video using yt-dlp | 使用 yt-dlp 下载视频
2. Extract audio | 提取音频
3. Transcribe with Whisper | 使用 Whisper 转写
4. Generate summary | 生成摘要

### Performance | 性能
| Whisper Model | Speed | Quality | Recommended |
|--------------|-------|---------|-------------|
| tiny | Fastest | Lowest | ❌ |
| base | Fast | Good | ✅ Recommended |
| small | Medium | Better | ✅ Better quality |
| medium | Slow | Great | ⚠️ Slow |

### Best practices | 最佳实践
- Use `--transcribe` flag explicitly | 显式使用 `--transcribe` 参数
- Use `--cookies` to avoid rate limiting | 使用 `--cookies` 避免频率限制
- For multiple videos, consider batch processing | 多视频考虑批量处理
- Short videos (<3min) work best | 短视频（<3分钟）效果最佳

### Getting Cookies | 获取 Cookies
1. Install browser extension: "Get cookies.txt LOCALLY"
2. Login to Xiaohongshu (登录小红书)
3. Export cookies to file (导出 cookies 到文件)

### Example | 示例
```bash
# With cookies for reliable access | 使用 cookies 确保可靠访问
video-summary "https://www.xiaohongshu.com/explore/xxxxx" --cookies cookies.txt --transcribe

# Explicit transcription | 显式转写
video-summary "https://www.xiaohongshu.com/explore/xxxxx" --transcribe
```

---

## Douyin (抖音)

**Subtitle Extraction | 字幕提取**: ⚠️ Limited (requires transcription)

### Current Status | 当前状态
- Similar to Xiaohongshu | 与小红书类似
- Short-form vertical videos | 竖版短视频
- No official subtitle API | 无官方字幕 API
- **风控严格** — May need cookies | Strict rate limiting, may need cookies

### URL Formats | URL 格式
```
https://www.douyin.com/video/VIDEO_ID
https://v.douyin.com/xxxxxxxx  (短链接)
```

### How it works | 工作原理
1. Extract video URL (may need redirection) | 提取视频 URL（可能需要重定向）
2. Download video | 下载视频
3. Transcribe with Whisper | 使用 Whisper 转写
4. Generate summary | 生成摘要

### Limitations | 限制
- Very short videos may not have enough content | 极短视频可能内容不足
- Background music can interfere with transcription | 背景音乐可能干扰转写
- Live streams not supported | 不支持直播

### Best practices | 最佳实践
- Focus on speech-heavy content | 聚焦语音内容为主的视频
- Filter out music-heavy videos | 过滤音乐为主的视频
- Use `--transcribe` explicitly | 显式使用 `--transcribe`
- Use `--cookies` for reliable access | 使用 `--cookies` 确保可靠访问

### Example | 示例
```bash
video-summary "https://v.douyin.com/xxxxx" --cookies cookies.txt --transcribe
```

---

## Local Files | 本地文件

**Subtitle Extraction | 字幕提取**: ✅ Whisper transcription

### Supported formats | 支持格式
- **Video | 视频**: mp4, mkv, webm, avi, mov
- **Audio | 音频**: mp3, wav, m4a, flac

### How it works | 工作原理
1. Detect file type | 检测文件类型
2. Extract audio if needed | 如需则提取音频
3. Transcribe with Whisper | 使用 Whisper 转写
4. Generate summary | 生成摘要

### Performance considerations | 性能考虑
| File Size | tiny | base | small |
|-----------|------|------|-------|
| 50MB | ~1m | ~2m | ~5m |
| 200MB | ~4m | ~8m | ~20m |
| 500MB | ~10m | ~20m | ~50m |

**GPU Acceleration | GPU 加速**:
- NVIDIA GPU with CUDA: 3-10x faster | NVIDIA GPU 配 CUDA 快 3-10 倍
- Apple Silicon: 2-5x faster | Apple Silicon 快 2-5 倍

### Best practices | 最佳实践
- Use appropriate Whisper model for your needs | 根据需求选择合适的 Whisper 模型
- For batch processing, consider `tiny` model | 批量处理考虑 `tiny` 模型
- GPU acceleration significantly speeds up transcription | GPU 加速显著提升转写速度

### Example | 示例
```bash
# Transcribe local video | 转写本地视频
video-summary ./meeting-recording.mp4

# With specific model | 使用特定模型
VIDEO_SUMMARY_WHISPER_MODEL=small video-summary ./lecture.mp4 --chapter

# Save output to file | 保存输出到文件
video-summary ./presentation.mp4 --output presentation-summary.md
```

---

## Whisper Model Comparison | Whisper 模型对比

| Model | Parameters | Speed | Accuracy | VRAM | Recommended |
|-------|-----------|-------|----------|------|-------------|
| tiny | 39M | Fastest | Lowest | ~1GB | ⚠️ Quick preview |
| base | 74M | Fast | Good | ~1GB | ✅ Recommended |
| small | 244M | Medium | Better | ~2GB | ✅ Better quality |
| medium | 769M | Slow | Great | ~5GB | ⚠️ Professional use |
| large | 1550M | Slowest | Best | ~10GB | ⚠️ Highest quality |

### Recommendations | 推荐

| Use Case | Recommended Model |
|----------|-------------------|
| Casual use / 快速预览 | `tiny` or `base` |
| Regular use / 日常使用 | `base` (default) |
| Professional use / 专业用途 | `small` or `medium` |
| Highest quality / 最高质量 | `large` (requires GPU) |

---

## Troubleshooting by Platform | 各平台故障排除

### YouTube
| Error | Cause | Solution |
|-------|-------|----------|
| "Sign in to confirm your age" | Age-restricted video | Not supported, use browser |
| "Video unavailable" | Region-locked or deleted | Try VPN or different video |
| "No subtitles found" | No CC available | Use `--transcribe` |

### Bilibili
| Error | Cause | Solution |
|-------|-------|----------|
| "No subtitles found" | Video doesn't have CC | Use `--transcribe` |
| "Login required" | Video requires B站 account | Try `--cookies` |
| "Video not found" | BV号 invalid or deleted | Check URL |

### Xiaohongshu
| Error | Cause | Solution |
|-------|-------|----------|
| "Could not extract content" | Video is private or deleted | Check if video is accessible |
| "Rate limited" | Too many requests | Use `--cookies` |
| Slow transcription | Normal for this platform | Consider `tiny` model |

### Douyin
| Error | Cause | Solution |
|-------|-------|----------|
| "Could not extract content" | Video may be private | Use `--cookies` |
| "URL redirection failed" | Short link expired | Get full URL |
| Slow transcription | Normal for this platform | Consider `tiny` model |

### Local Files
| Error | Cause | Solution |
|-------|-------|----------|
| "Unsupported format" | Unknown file type | Convert to mp4 or mp3 |
| "Out of memory" | File too large | Use smaller Whisper model |
| "No audio detected" | Corrupted or silent file | Check file integrity |

---

## Cookie Guide | Cookies 指南

### Why Cookies? | 为什么需要 Cookies?

Some platforms restrict content access:
- Age-restricted videos
- Login-required content
- Rate limiting avoidance

某些平台限制内容访问：
- 年龄限制视频
- 登录要求内容
- 避免频率限制

### How to Get Cookies | 如何获取 Cookies

**Method 1: Browser Extension | 方法 1：浏览器扩展**
1. Install "Get cookies.txt LOCALLY" extension
2. Login to the platform (登录平台)
3. Click extension and export (点击扩展导出)
4. Save as `cookies.txt`

**Method 2: Manual Export | 方法 2：手动导出**
1. Open DevTools (F12)
2. Go to Application → Cookies
3. Copy cookies in Netscape format

### Using Cookies | 使用 Cookies

```bash
# Method 1: Command line | 方法 1：命令行
video-summary "URL" --cookies cookies.txt

# Method 2: Environment variable | 方法 2：环境变量
export VIDEO_SUMMARY_COOKIES=/path/to/cookies.txt
video-summary "URL"
```

---

## Future Improvements | 未来改进

### Planned Features | 计划功能
- [ ] Batch processing for multiple URLs | 多 URL 批量处理
- [ ] Cloud transcription API integration (Deepgram, AssemblyAI) | 云转写 API 集成
- [ ] Real-time transcription for live streams | 直播实时转写
- [ ] Multi-language translation | 多语言翻译
- [ ] Speaker diarization (identify different speakers) | 说话人分离

### Platform Expansion | 平台扩展
- [ ] TikTok (international) | TikTok 国际版
- [ ] Twitter/X videos | Twitter/X 视频
- [ ] Instagram Reels | Instagram Reels
- [ ] Facebook videos | Facebook 视频

---

*Last updated: 2026-03-08*
