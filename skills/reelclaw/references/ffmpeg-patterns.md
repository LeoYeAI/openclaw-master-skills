# FFmpeg Patterns for ReelClaw

All commands include `-y` (overwrite) and `-hide_banner` for cleaner output.

## Standard Video Filter (1080x1920 vertical)

```bash
VF="scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30"
```

## Trim / Cut

```bash
ffmpeg -y -hide_banner -loglevel error \
  -i "INPUT" -ss START_TIME -to END_TIME \
  -c copy "OUTPUT"
```

## Landscape to Vertical (center crop)

```bash
ffmpeg -y -hide_banner -loglevel error \
  -i "INPUT" \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30" \
  -an -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

## Landscape to Vertical (blur background)

```bash
ffmpeg -y -hide_banner -loglevel error -i "INPUT" \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];\
    [0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0[fg];\
    [bg][fg]overlay=0:0" \
  -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 128k -movflags +faststart \
  "OUTPUT"
```

## Vertical Scale + Pad

```bash
ffmpeg -y -hide_banner -loglevel error \
  -i "INPUT" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30" \
  -an -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

## Speed Up (two-pass — REQUIRED)

Never combine `-ss`/`-to` with `setpts` in a single pass. Always use two-pass.

```bash
# Pass 1: Trim segment
ffmpeg -y -hide_banner -loglevel error \
  -i "INPUT" -ss START -to END \
  -c copy "/tmp/segment.mp4"

# Pass 2: Speed up + scale
# Speed = source_duration / target_duration
# PTS multiplier = 1 / speed (e.g., 3x speed = 0.333*PTS)
ffmpeg -y -hide_banner -loglevel error \
  -i "/tmp/segment.mp4" \
  -vf "setpts=PTS_MULTIPLIER*PTS,$VF" -an \
  -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

**Speed factor reference:**

| Source | Target | PTS Multiplier | Speed |
|--------|--------|----------------|-------|
| 21s | 7s | 0.333*PTS | 3.0x |
| 24s | 8s | 0.333*PTS | 3.0x |
| 28s | 8s | 0.286*PTS | 3.5x |
| 30s | 8.5s | 0.283*PTS | 3.53x |
| 32s | 8s | 0.250*PTS | 4.0x |

## Concatenate Clips

**Concat demuxer (same codec, fastest):**
```bash
cat > /tmp/concat.txt << EOF
file '/path/to/clip-01.mp4'
file '/path/to/clip-02.mp4'
EOF

ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i /tmp/concat.txt \
  -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

**Filter concat (different codecs/resolutions):**
```bash
ffmpeg -y -hide_banner -loglevel error \
  -i clip-01.mp4 -i clip-02.mp4 \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];\
    [1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];\
    [v0][v1]concat=n=2:v=1:a=0[outv]" \
  -map "[outv]" -an \
  -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

## Text Overlays (drawtext)

**Inline text (no apostrophes):**
```bash
ffmpeg -y -hide_banner -loglevel error -i "INPUT" \
  -vf "drawtext=text='Your text here':\
    fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:\
    fontsize=64:fontcolor=white:borderw=4:bordercolor=black:\
    x=(60+(900-text_w)/2):y=310:\
    enable='between(t,0,4.5)'" \
  -c:v libx264 -preset fast -crf 18 -c:a copy -movflags +faststart \
  "OUTPUT"
```

**Textfile approach (for apostrophes):**
```bash
printf "When nothing's wrong" > /tmp/line1.txt

ffmpeg -y -hide_banner -loglevel error -i "INPUT" \
  -vf "drawtext=textfile=/tmp/line1.txt:\
    fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:\
    fontsize=64:fontcolor=white:borderw=4:bordercolor=black:\
    x=(60+(900-text_w)/2):y=310:\
    enable='between(t,0,4.5)'" \
  -c:v libx264 -preset fast -crf 18 -c:a copy -movflags +faststart \
  "OUTPUT"
```

**Multi-line text:**
```bash
ffmpeg -y -hide_banner -loglevel error -i "INPUT" \
  -vf "drawtext=text='Line one':\
    fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:\
    fontsize=64:fontcolor=white:borderw=4:bordercolor=black:\
    x=(60+(900-text_w)/2):y=310:\
    enable='between(t,0,4.5)',\
  drawtext=text='Line two':\
    fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:\
    fontsize=64:fontcolor=white:borderw=4:bordercolor=black:\
    x=(60+(900-text_w)/2):y=390:\
    enable='between(t,0,4.5)'" \
  -c:v libx264 -preset fast -crf 18 -c:a copy -movflags +faststart \
  "OUTPUT"
```

**Text with background box:**
```bash
drawtext=text='YOUR TEXT':\
  fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:\
  fontsize=64:fontcolor=white:\
  box=1:boxcolor=black@0.6:boxborderw=20:\
  x=(60+(900-text_w)/2):y=310:\
  enable='between(t,0,4.5)'
```

**Escape colons:** Use `\\:` (e.g., `10\\:00 AM`)

## Add Music

```bash
# Analyze volume to find peak energy
ffmpeg -i "track.mp3" -af volumedetect -f null /dev/null 2>&1 | grep volume

# Overlay music with fade in/out
ffmpeg -y -hide_banner -loglevel error \
  -i "video.mp4" -i "track.mp3" \
  -map 0:v -map 1:a \
  -af "afade=t=in:st=0:d=0.5,afade=t=out:st=14:d=1,volume=0.8" \
  -c:v copy -c:a aac -b:a 128k \
  -shortest -movflags +faststart \
  "OUTPUT"
```

## Validate Duration

```bash
ffprobe -v quiet -print_format json -show_entries format=duration "OUTPUT" | \
  python3 -c "import sys,json; d=float(json.load(sys.stdin)['format']['duration']); \
  print(f'Duration: {d:.1f}s — {\"OK\" if d <= 15.0 else \"TOO LONG\"}')"
```

## Upload to tmpfiles.org

```bash
url=$(curl -s -F "file=@video.mp4" https://tmpfiles.org/api/v1/upload | \
  python3 -c "import sys,json; u=json.load(sys.stdin)['data']['url']; \
  print(u.replace('tmpfiles.org/', 'tmpfiles.org/dl/'))")
echo "Public URL: $url"
```

## Probe Video Info

```bash
ffprobe -v quiet -print_format json -show_format -show_streams "INPUT"
```

## Final Export (high quality)

```bash
ffmpeg -y -hide_banner -loglevel error -i "INPUT" \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -ar 44100 \
  -pix_fmt yuv420p -movflags +faststart -r 30 \
  "FINAL_OUTPUT"
```

## Transitions (xfade)

```bash
ffmpeg -y -hide_banner -loglevel error \
  -i clip-01.mp4 -i clip-02.mp4 \
  -filter_complex "\
    [0:v]scale=1080:1920:...,fps=30[v0];\
    [1:v]scale=1080:1920:...,fps=30[v1];\
    [v0][v1]xfade=transition=fade:duration=0.5:offset=CLIP1_DUR_MINUS_0.5[outv]" \
  -map "[outv]" -an \
  -c:v libx264 -preset fast -crf 18 -movflags +faststart \
  "OUTPUT"
```

Available transitions: `fade`, `dissolve`, `wipeleft`, `wiperight`, `slideup`, `slidedown`, `circlecrop`, `fadeblack`, `fadewhite`, `radial`, `smoothleft`, `smoothright`
