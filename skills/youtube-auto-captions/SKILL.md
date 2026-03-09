# youtube-auto-captions - YouTube 自动字幕

## 描述
自动为 YouTube 视频生成字幕，支持多语言翻译、时间轴校准。提升视频可访问性和 SEO。

## 定价
- **按次收费**: ¥9/次
- 每视频最长 60 分钟
- 支持 50+ 语言

## 用法
```bash
# 生成字幕
/youtube-auto-captions --video <video_id> --lang zh

# 翻译字幕
/youtube-auto-captions --video <video_id> --translate en,ja,ko

# 批量处理
/youtube-auto-captions --playlist <playlist_id> --lang zh

# 导出字幕
/youtube-auto-captions --video <video_id> --export srt
```

## 技能目录
`~/.openclaw/workspace/skills/youtube-auto-captions/`

## 作者
张 sir

## 版本
1.0.0
