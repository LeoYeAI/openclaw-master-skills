---
name: youtube-music-cast
description: Download music from YouTube/YouTube Music and stream to Chromecast via Home Assistant. Complete CLI toolset with web server integration, configuration wizard, and playback controls.
version: "6.0.0"
author: Wobo
license: MIT
homepage: https://github.com/clawdbot/skills
repository: https://github.com/clawdbot/skills/tree/main/youtube-music-cast
user-invocable: true
triggers:
  - play music
  - cast to chromecast
  - youtube music
  - download music
  - cast music
keywords:
  - youtube
  - music
  - chromecast
  - home-assistant
  - cast
  - media-player
  - streaming
  - yt-dlp
  - google-cast
  - audio
  - mp3
  - free-music
category: media
requires:
  bins:
    - yt-dlp
    - python3
    - curl
    - jq
  env: []
config:
  stateDirs:
    - ~/.youtube-music-cast
metadata:
  clawdbot:
    emoji: "🎵"

---

# YouTube Music Cast

YouTube music → your Chromecast. Simple, free, works.

Download audio from YouTube or YouTube Music and stream it through Home Assistant to any Cast-enabled device. No subscriptions, no cloud services, just your local network.

## Features

- ✅ **Free forever** — No subscriptions, no premium accounts needed
- ✅ **High quality** — 320K MP3, crystal clear audio
- ✅ **Video mode** — Create MP4 videos with album art and text overlays
- ✅ **Radio mode** — Auto-discover and play related songs
- ✅ **Local storage** — Your music stays on your machine, no cloud
- ✅ **Multi-room** — Cast to any Chromecast device in your home
- ✅ **Batch download** — Download entire playlists, stream anytime
- ✅ **Simple CLI** — Fast commands, no browser required
- ✅ **Works offline** — Once downloaded, music is yours to keep

## Use Cases

### Daily Music
Download your favorite tracks in the morning, cast them throughout the day. No waiting, no buffering.

### Party Mode
Download a playlist before guests arrive, then queue up songs without fumbling with phones or apps.

### Background Audio
Play ambient music or podcasts while you work without worrying about ads or interruptions.

### Multi-Room Sync
Stream the same track to multiple Chromecasts simultaneously (bedroom + living room + kitchen).

## Why This Over Premium Services?

| Feature | YouTube Music Cast | Spotify Premium | YouTube Premium |
|---------|-------------------|------------------|------------------|
| Cost | Free forever | $10.99/month | $13.99/month |
| Quality | 320K MP3 | Up to 320K | Up to 1080p video |
| Offline | Yes, forever | Download limit | Download limit |
| Ads | None | None | None |
| Platforms | Any Chromecast | Spotify Connect devices | YouTube apps |
| Privacy | Local only | Cloud-based | Cloud-based |

## Quick Start

```bash
# 1. Setup (one time, takes 2 minutes)
cast-setup

# 2. Download your first song
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ

# 3. Start the web server
cast-server start

# 4. Cast it to your default device
cast-play never-gonna-give-you-up.mp3
```

That's it. Your music is playing through your Chromecast.

## What This Does

Three simple steps, one command each:

### 1. Download
`yt-dlp` grabs audio from YouTube or YouTube Music, extracts it as MP3 (320K quality).

### 2. Host
A lightweight Python HTTP server makes your downloaded files accessible over your local network. No setup required — just Python 3.

### 3. Cast
Home Assistant's `media_player.play_media` service sends the HTTP URL to your Chromecast, which streams the audio.

### Why a Web Server?

Home Assistant's `play_media` service requires a URL, not a file path. The web server bridges that gap.

```yaml
# ✅ This works — HA can fetch via HTTP
media_content_id: "http://192.168.1.81:8735/song.mp3"

# ❌ This fails — HA can't read file paths
media_content_id: "/tmp/youtube-music/song.mp3"
```

**Architecture:**
```
YouTube URL → yt-dlp → MP3 file → Python HTTP server → Home Assistant API → Chromecast
```

## Installation

### What You Need

- **Home Assistant** with Google Cast integration
- **Chromecast** or Cast-enabled device (Nest speakers, Google Home, TV)
- **System tools:** `yt-dlp`, Python 3, `curl`, `jq`

### Step 1: Install Scripts

```bash
# Clone or download the skill
cd youtube-music-cast

# Make all scripts executable
chmod +x scripts/*

# Install globally (recommended)
./install.sh --global

# Or install locally
./install.sh
```

### Step 2: Run Setup Wizard

```bash
cast-setup
```

The wizard will ask for:
- **Home Assistant URL** — e.g., `http://homeassistant.local:8123`
- **Long-Lived Access Token** — Generate in HA → Profile → Long-Lived Access Tokens
- **Server IP** — The machine running these scripts
- **Default media player** — e.g., `media_player.bedroom_display`

### Step 3: Test Your Setup

```bash
# Download a test song
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ

# Start the server
cast-server start

# Cast it
cast-play song.mp3
```

If music plays, you're ready!

## Commands

| Command | Description | Example |
|---------|-------------|----------|
| `cast-setup` | Run configuration wizard | `cast-setup` |
| `cast-download <URL> [options]` | Download from YouTube/YouTube Music | `cast-download https://youtube.com/watch?v=... --video` |
| `cast-radio <URL> [options]` | Start radio mode with related songs | `cast-radio https://youtube.com/watch?v=... --count 10` |
| `cast-server [start|stop|status]` | Manage HTTP server | `cast-server start` |
| `cast-play <file> [device]` | Cast music or video file to device | `cast-play song.mp4` |
| `cast-stop [device]` | Stop playback | `cast-stop` |
| `cast-status [device]` | Show player status | `cast-status` |
| `cast-devices` | List all available media players | `cast-devices` |
| `cast-list` | List downloaded files | `cast-list` |
| `cast-help` | Show help | `cast-help` |

## Usage Guide

### Your First Song

```bash
# Download from YouTube
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ

# Rename for cleaner URL (recommended)
mv "/tmp/youtube-music/Rick Astley - Never Gonna Give You Up.mp3" \
   "/tmp/youtube-music/never-gonna-give-you-up.mp3"

# Start the web server
cast-server start

# Cast to your default device
cast-play never-gonna-give-you-up.mp3
```

### Cast to Different Rooms

```bash
# Living room TV
cast-play song.mp3 media_player.living_room

# Kitchen speaker
cast-play song.mp3 media_player.kitchen_speaker

# Bedroom Chromecast
cast-play song.mp3 media_player.bedroom_display

# Multiple rooms at once (run multiple commands)
cast-play song.mp3 media_player.living_room & \
cast-play song.mp3 media_player.bedroom_display
```

### Check What's Playing

```bash
# Default device
cast-status

# Specific device
cast-status media_player.bedroom_display
```

Output:
```
📺 media_player.bedroom_display

State: playing
Friendly Name: Bedroom display
Volume: 22%

Now Playing:
  Title: Never Gonna Give You Up
  Artist: Rick Astley
  Duration: 3:32

App: Default Media Receiver
```

### Stop Playback

```bash
# Stop default device
cast-stop

# Stop specific device
cast-stop media_player.living_room
```

### See What You've Downloaded

```bash
# List all music files with sizes
cast-list
```

Output:
```
🎵 Downloaded Music

boneheads-bank-holiday.mp3                                    9.3M
never-gonna-give-you-up.mp3                                 8.2M
song-for-nary.mp3                                          7.8M

Total: 3 files
```

### See Available Devices

```bash
cast-devices
```

Output:
```
📺 Available Media Players

media_player.bedroom_display
  Name: Bedroom display
  State: idle
  Supported: play_media, volume_set, volume_mute, ...

media_player.living_room
  Name: Living room TV
  State: off
  Supported: play_media, volume_set, ...

Default device: media_player.bedroom_display
```

## New Features: Radio Mode & Video Mode

### 📻 Radio Mode

Radio mode automatically discovers and downloads related songs based on YouTube recommendations. After downloading a seed song, it searches for similar tracks and adds them to your queue.

**Start radio mode:**

```bash
# Basic radio (downloads seed + 3 related songs)
cast-radio https://youtube.com/watch?v=dQw4w9WgXcQ

# Custom number of related songs
cast-radio https://youtube.com/watch?v=dQw4w9WgXcQ --count 10

# Radio mode with video files
cast-radio https://youtube.com/watch?v=dQw4w9WgXcQ --video --count 5
```

**Or use cast-download with --radio flag:**

```bash
# Download with radio mode
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ --radio

# Download with custom count
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ --radio --radio-count 5

# Radio + video mode combined
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ --radio --video
```

**How it works:**
1. Downloads the seed song you specify
2. Extracts artist/title from metadata
3. Searches YouTube for similar videos
4. Downloads related songs (prefixed with `radio_`)
5. Related songs are ready to cast in sequence

**Play your radio queue:**

```bash
# Start server
cast-server start

# Play the first song
cast-play $(ls -t /tmp/youtube-music/*.mp3 | head -n 1 | xargs basename)

# Or play related songs sequentially
cast-play radio_some-song.mp3
cast-play radio_another-song.mp3
# ... etc
```

**Tips:**
- Related songs are prefixed with `radio_` for easy identification
- The radio mode searches based on the artist name from the seed song
- Use `--count` to control how many related songs to download
- Combine with `--video` flag for visual radio mode

### 🎬 Video Mode with Visuals

Video mode creates MP4 videos instead of plain MP3 files. Each video includes:
- The original audio track
- Album art thumbnail from YouTube
- Text overlay showing song title and artist
- Smooth, high-quality encoding

**Download a video:**

```bash
# Download as MP4 with album art and text
cast-download https://youtube.com/watch?v=dQw4w9WgXcQ --video

# Cast the MP4 file
cast-server start
cast-play "Never Gonna Give You Up.mp4"
```

**Radio mode with videos:**

```bash
# Download seed + related songs as videos
cast-radio https://youtube.com/watch?v=dQw4w9WgXcQ --video --count 5

# Cast videos
cast-play "Never Gonna Give You Up.mp4"
cast-play "radio_Together Forever.mp4"
# ... etc
```

**How it works:**
1. Downloads the audio track (320K MP3 quality)
2. Downloads the album art thumbnail from YouTube
3. Uses ffmpeg to create an MP4 video with:
   - Looping album art background
   - Audio track encoded as AAC
   - Text overlay (song title and artist name) at bottom
4. Cast the MP4 to your Chromecast (TVs with video support)

**Video output:**
- Codec: H.264 (libx264)
- Audio: AAC (192K)
- Resolution: Same as thumbnail (usually 480p or 720p)
- Text: White text with semi-transparent black box
- Compatible with all Chromecast devices with video support

**Notes:**
- Videos take more space than MP3s (~2-3x larger)
- Requires ffmpeg to be installed on your system
- Text overlay uses DejaVu Sans Bold font (included on most Linux systems)
- Chromecast audio devices (like Google Home Mini) will play audio only
- Chromecast with displays (TVs, Google Nest Hub) will show the full video

**Requirements for video mode:**
- `ffmpeg` must be installed on your system
  ```bash
  # Debian/Ubuntu
  sudo apt install ffmpeg

  # macOS
  brew install ffmpeg
  ```

### Mixed MP3 and MP4

`cast-play` automatically detects the file type:
- `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac` → music
- `.mp4`, `.mkv`, `.webm`, `.mov` → video

You can mix both formats in the same directory:
```bash
# Download some as MP3
cast-download https://youtube.com/watch?v=VIDEO_ID_1

# Download some as MP4
cast-download https://youtube.com/watch?v=VIDEO_ID_2 --video

# Play both - cast-play handles the difference
cast-play song.mp3
cast-play video.mp4
```

## Configuration

Config file: `~/.youtube-music-cast/config.sh`

```bash
# Home Assistant
HA_URL="http://homeassistant.local:8123"
HA_TOKEN="your-long-lived-access-token-here"

# Web Server
SERVER_IP="192.168.1.81"
SERVER_PORT="8735"

# Default Device (override per command)
DEFAULT_DEVICE="media_player.bedroom_display"

# Directories
DOWNLOAD_DIR="/tmp/youtube-music"
CAST_DIR="$HOME/.youtube-music-cast"
```

**Edit the file directly** or **re-run `cast-setup`** to update.

## File Naming Best Practices

Keep URLs clean. Simple filenames save you from headaches later.

### The Problem

❌ Bad filenames:
```
http://192.168.1.81:8735/Bonehead's%20Bank%20Holiday%20(Remastered).mp3
```
This URL is messy, hard to type, and prone to encoding errors.

### The Solution

✅ Good filenames:
```
http://192.168.1.81:8735/boneheads-bank-holiday.mp3
```
Clean, easy to type, no issues.

### Practical Tips

```bash
# After download, rename immediately
mv "Oasis - Bonehead's Bank Holiday (Remastered 1995).mp3" \
   "oasis-boneheads-bank-holiday.mp3"

# Use lowercase, hyphens only
mv "My Awesome Song.mp3" "my-awesome-song.mp3"

# No special characters
mv "song@remix#.mp3" "song-remix.mp3"
```

**Rule of thumb:**
- Lowercase
- Hyphens instead of spaces
- No special characters (@, #, ?, etc.)
- Keep it short

## Troubleshooting

### Chromecast Not in Home Assistant

**Problem:** `cast-devices` shows no Chromecast devices.

**Solution:** Add Google Cast integration
1. Home Assistant → Settings → Devices & Services
2. Click "+ Add Integration"
3. Search "Google Cast" → Select it
4. Follow the discovery wizard

**If discovery fails:**
- Ensure Chromecast and Home Assistant are on the same network
- Try adding manually with Chromecast IP address

### Server Won't Start

**Problem:** `cast-server start` fails or says "port in use".

**Solution:**
```bash
# Check if port 8735 is in use
netstat -tlnp | grep 8735
# or
ss -tlnp | grep 8735

# Stop any existing server
cast-server stop

# Try starting manually to see error
cd /tmp/youtube-music
python3 -m http.server 8735
```

**If port is in use by another process:**
Edit `~/.youtube-music-cast/config.sh`:
```bash
SERVER_PORT="8736"  # Change to something else
```

### "File Not Found" Error

**Problem:** `cast-play song.mp3` says file not found.

**Solution:**
```bash
# List what's actually there
cast-list

# Check exact spelling (case-sensitive!)
cast-play "Exact-Filename.mp3"  # Not "exact-filename.mp3"

# Verify server is running
cast-server status
```

**Common mistakes:**
- Wrong case: `Song.mp3` vs `song.mp3`
- Wrong extension: `song.MP3` vs `song.mp3`
- File in wrong directory: Check `DOWNLOAD_DIR` in config

### Download Fails

**Problem:** `cast-download` errors or hangs.

**Solution:**
```bash
# Update yt-dlp (YouTube changes often)
pip install --upgrade yt-dlp

# Check version
yt-dlp --version

# Try verbose output to see what's wrong
yt-dlp --verbose "URL"

# Try different URL format
# YouTube: https://youtube.com/watch?v=VIDEO_ID
# YouTube Music: https://music.youtube.com/watch?v=VIDEO_ID
```

**If it's a geo-blocked video:**
Use a VPN or find an alternative upload of the same track.

### Home Assistant Connection Error

**Problem:** `curl` errors when contacting HA.

**Solution:**
```bash
# Test your HA token manually
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     "http://homeassistant.local:8123/api/states"

# If you see JSON → token is good
# If 401 Unauthorized → token is wrong or expired
# If connection refused → URL is wrong or HA is down
```

**Regenerate token if needed:**
HA → Profile → Scroll down → Long-Lived Access Tokens → Generate new

### Video Mode Issues

**Problem:** `cast-download --video` fails with "ffmpeg not found" or similar error.

**Solution:**
```bash
# Check if ffmpeg is installed
ffmpeg -version

# If not found, install it
# Debian/Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**Problem:** Video creation is slow or takes too long.

**Solution:**
- Video encoding is CPU-intensive. First-time creation may take 10-30 seconds per song.
- Use MP3 mode (`cast-download` without `--video`) for faster downloads.
- Consider lowering video quality in the script (edit `cast-download` and change `-preset ultrafast` to `-preset fast` for better quality but slower encoding).

**Problem:** Text overlay doesn't appear or looks wrong.

**Solution:**
- The script uses DejaVu Sans Bold font. If it's not installed, text won't appear.
- Install the font:
  ```bash
  # Debian/Ubuntu
  sudo apt install fonts-dejavu

  # macOS (usually pre-installed)
  ```
- Or edit the script to use a different font path.

**Problem:** Chromecast audio device plays video without visuals.

**Solution:**
- This is expected behavior. Audio-only Chromecast devices (Google Home Mini, Chromecast Audio) will play the audio track from MP4 files but cannot display video.
- Use MP3 mode for audio-only devices to save bandwidth and storage.

**Problem:** MP4 files are too large.

**Solution:**
- Videos are larger than MP3s (typically 2-3x the size).
- Reduce video bitrate by editing `cast-download` and changing `-b:a 192k` to `-b:a 128k` for audio, or adjust video codec settings.
- Use MP3 mode if storage is a concern.

### Radio Mode Issues

**Problem:** Radio mode downloads unrelated songs.

**Solution:**
- Radio mode searches YouTube using the artist name from the seed song.
- Sometimes the search may return mixed results due to ambiguous artist names.
- Try using a different seed song with a clearer artist name.
- The `radio_` prefix makes it easy to identify and remove unwanted downloads.

**Problem:** Radio mode doesn't find any related songs.

**Solution:**
- Ensure you have a stable internet connection.
- Check that the seed song has proper metadata (title/uploader).
- Try a different seed song — some videos have limited search results.
- Increase the count with `--radio-count 10` to get more results.

**Problem:** Related songs don't play in sequence automatically.

**Solution:**
- Radio mode downloads the songs but doesn't auto-play them in sequence.
- You need to manually play each related song, or create a simple playlist script:
  ```bash
  # Play all radio songs in sequence
  for file in /tmp/youtube-music/radio_*.mp3; do
      cast-play "$(basename "$file")"
      sleep 5  # Wait between songs
  done
  ```

### Cast Commands Hang

**Problem:** `cast-play` doesn't return or music never starts.

**Common causes:**
1. **Media player is offline** — Check `cast-devices` for state
2. **Server isn't accessible from HA** — Verify `SERVER_IP` in config matches current IP
3. **Chromecast network issue** — Restart Chromecast
4. **Wrong device ID** — Copy exact ID from `cast-devices` output

**Quick fix:**
```bash
# Restart everything
cast-server stop
cast-server start
cast-play song.mp3

# Check device is online
cast-devices

# Try casting from HA UI to isolate issue
```

## Project Structure

```
youtube-music-cast/
├── scripts/
│   ├── cast-setup      # Configuration wizard (interactive)
│   ├── cast-download   # Download from YouTube (uses yt-dlp)
│   ├── cast-server     # HTTP server manager (start/stop/status)
│   ├── cast-play       # Cast to device (HA API)
│   ├── cast-stop       # Stop playback
│   ├── cast-status     # Player status query
│   ├── cast-devices    # List all HA media players
│   ├── cast-list       # List downloaded files
│   └── cast-help       # Help documentation
├── install.sh          # Installation script (--global, --help)
├── SKILL.md           # This file (ClawdHub skill definition)
├── README.md          # User-facing documentation
├── CHANGELOG.md       # Version history
├── LICENSE            # MIT license
├── .gitignore        # Protects secrets and state
└── .clawdhub/
    └── origin.json    # ClawdHub metadata

~/.youtube-music-cast/
└── config.sh         # Your configuration (don't commit to Git)

/tmp/youtube-music/
└── *.mp3            # Downloaded music files
```

## Requirements

### yt-dlp (YouTube downloader)

```bash
pip install yt-dlp
```

**Update regularly:** `pip install --upgrade yt-dlp`

### Python 3 (HTTP server)

```bash
# Check version (usually pre-installed)
python3 --version
```

### curl (HTTP client for HA API)

```bash
# Check version (usually pre-installed)
curl --version
```

### jq (JSON processor)

```bash
# Debian/Ubuntu
sudo apt install jq

# macOS
brew install jq
```

### ffmpeg (Video mode - optional)

Required for `--video` flag to create MP4 videos with album art and text overlays.

```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**Check installation:**
```bash
ffmpeg -version
```

**Note:** Video mode is optional. If you only download MP3s, you don't need ffmpeg.

## Performance Tips

### 1. Batch Downloads
Download multiple tracks or entire playlists at once:
```bash
# Download playlist
yt-dlp -x --audio-format mp3 --audio-quality 320K \
  -o "/tmp/youtube-music/%(playlist_index)s-%(title)s.%(ext)s" \
  "https://youtube.com/playlist?list=PLAYLIST_ID"

# Then cast them without waiting
cast-play 01-song.mp3
cast-play 02-song.mp3
cast-play 03-song.mp3
```

### 2. Keep Server Running
The HTTP server is lightweight (~5MB RAM). No need to stop/start between casts:
```bash
# Start once
cast-server start

# Cast as many songs as you want
cast-play song1.mp3
cast-play song2.mp3
# ... etc
```

### 3. Use Default Device
Set `DEFAULT_DEVICE` in config to avoid typing it every time:
```bash
# In ~/.youtube-music-cast/config.sh
DEFAULT_DEVICE="media_player.bedroom_display"

# Now just cast
cast-play song.mp3  # Automatically uses bedroom_display
```

### 4. Clean Up Occasionally
Files in `/tmp/` are cleared on reboot by design, but you can manually clean:
```bash
# List all files with sizes
cast-list

# Remove old files
rm /tmp/youtube-music/*.mp3
```

### 5. WiFi Matters
If streaming glitches:
- Move Chromecast to 5GHz WiFi
- Reduce distance between Chromecast and server
- Check for WiFi interference

### 6. Alias Commands
Add shell aliases for faster access:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias cs='cast-server'
alias cd='cast-download'
alias cp='cast-play'
alias cl='cast-list'
alias cst='cast-status'

# Now just type
cs      # Start server
cd URL   # Download
cp song  # Cast
cl       # List
```

## Notes

- Files are stored in `/tmp/youtube-music/` — cleared on reboot (by design)
- Web server runs in background, persists across sessions
- Keep filenames simple: lowercase, hyphens, no spaces/special chars
- Server and Chromecast must be on same network
- HA token is stored locally in `config.sh` — **don't commit to Git**
- Quality is 320K MP3 — good balance of quality and file size
- No cloud services, no subscriptions, no tracking

## Comparison: This vs Alternatives

| Feature | YouTube Music Cast | Spotify Free | YouTube Premium |
|---------|-------------------|----------------|-----------------|
| Cost | Free | Free (with ads) | $13.99/month |
| Ads | None | Yes, every few songs | None |
| Offline | Yes, forever | No (premium only) | Yes, with limit |
| Quality | 320K MP3 | 160K (variable) | Up to 1080p video |
| Privacy | Local only | Cloud-based | Cloud-based |
| Platform | Any Chromecast | Spotify Connect | YouTube apps |
| Queue management | Manual | Built-in | Built-in |
| Multi-room | Manual | Premium feature | No |

**Bottom line:** If you value privacy, want to own your music, and don't need cloud features, this is for you.

## License

MIT License — use it, modify it, share it.

---

**Version:** 6.0.0
**Author:** Wobo
**License:** MIT
