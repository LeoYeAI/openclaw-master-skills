---
name: clipify
description: Find the funniest moments in a video, cut them as standalone clips, optionally reformat 16:9 to 9:16 (face-pan or split-screen), and burn opus-style word-by-word captions. Use when the user mentions "clipify," "cut clips from this video," "make shorts from this," "find funny moments," "reframe to 9:16," "vertical clips," or pastes a video file path and wants social-ready cuts.
tags: [video, clips, shorts, subtitles, whisper, ffmpeg, social-media]
---

# Clipify

Find the funniest moments in a video, cut them as standalone clips, optionally reformat 16:9 to 9:16 (face-pan or split-screen), and burn opus-style word-by-word captions.

## Prerequisites

- ffmpeg (verify with `ffmpeg -version`)
- openai-whisper (verify with `whisper --help`)
- numpy (verify with `python3 -c "import numpy"`)
- Scripts in `scripts/` directory (installed with skill)

## Inputs

- A video file path (ask if not provided)
- Optional: requested format (9:16, 16:9, 1:1) — ask after candidates are picked
- Optional: subtitle style preference — ask before captioning

## Workflow

### Step 1 — Find the funniest parts

```bash
mkdir -p /tmp/clipify
ffmpeg -y -i "$VIDEO" -vn -ac 1 -ar 16000 /tmp/clipify/audio.wav
whisper /tmp/clipify/audio.wav --model tiny.en --word_timestamps True --output_format json --output_dir /tmp/clipify --language en
```

For non-English: `--model base` (drop `--language`).

Read the resulting JSON and pick 3-5 candidate clips. Funny signals:
- Punchlines and reactions: "what", "wait", "no way", laughter, swearing
- Reversal moments: setup question then unexpected answer
- Awkward pauses: long gaps or fillers ("uh", "um")
- Self-roast / quotable one-liners
- Audio peaks: rapid back-and-forth alternating short segments

For each candidate, propose: `[start, end, why-it's-funny, suggested title]`. Aim for 10-25s clips. Show the list and let the user confirm/pick.

### Step 2 — Trim each chosen clip

```bash
ffmpeg -y -ss "$START" -t "$DURATION" -i "$VIDEO" -c copy /tmp/clipify/clip_$N.mp4
```

Use `-c copy` for instant trim. Re-encode only if cuts must be frame-accurate.

### Step 3 — Decide the output format

Ask the user (skip if already specified): "9:16 (TikTok/Reels), 16:9 (YouTube), or 1:1 (Insta feed)?"

### Step 4 — If 16:9 to 9:16: pan-between-faces vs split-screen

Detect source aspect with `ffprobe`. If source is 16:9 and target is 9:16, ask:

> "Two options: (a) hard-cut pan that follows whoever is speaking (single face on screen at a time), or (b) split-screen stack with both faces visible. Which do you want?"

Skip for single-talker clips — just center-crop.

#### Step 4a — Pan-between-faces (recommended for fast-cut talking-head dialogue)

1. **Locate the two face ROIs.** Sample one frame:

   ```bash
   ffmpeg -ss <middle> -i <clip> -frames:v 1 /tmp/clipify/probe.jpg
   ```

   Read the image. Identify each face's mouth+chin area as `x,y,w,h` in source pixel space. Verify by drawing boxes:

   ```bash
   ffmpeg -i probe.jpg -vf "drawbox=x=$LX:y=$LY:w=$LW:h=$LH:color=cyan@0.9:t=4,drawbox=x=$RX:y=$RY:w=$RW:h=$RH:color=magenta@0.9:t=4" verify.jpg
   ```

   Iterate at most twice. Boxes should cover mouth+chin and avoid hands/mics.

2. **Extract per-frame motion energy in each ROI:**

   ```bash
   ffmpeg -y -i clip.mp4 -filter_complex "
   [0:v]split=2[a][b];
   [a]crop=$LW:$LH:$LX:$LY,format=gray,tblend=all_mode=difference,signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=/tmp/clipify/L.txt[la];
   [b]crop=$RW:$RH:$RX:$RY,format=gray,tblend=all_mode=difference,signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=/tmp/clipify/R.txt[ra]
   " -map "[la]" -f null - -map "[ra]" -f null -
   ```

3. **Build speaker timeline** (min dwell 1.0s):

   ```bash
   python3 ~/.hermes/skills/media/clipify/scripts/analyze.py /tmp/clipify/L.txt /tmp/clipify/R.txt 1.0 > /tmp/clipify/segments.json
   ```

4. **Pick pan x-coordinates** for a 9:16 vertical strip. With source W=1920 and target W=1080, crop strip width = 608.
   - LEFT_X = face_left_center_x - 304 (clamp >= 0)
   - RIGHT_X = face_right_center_x - 304 (clamp <= source_W - 608)

5. **Generate the hard-cut x expression and render:**

   ```bash
   EXPR=$(python3 ~/.hermes/skills/media/clipify/scripts/build_pan.py /tmp/clipify/segments.json $LEFT_X $RIGHT_X)
   ffmpeg -y -i clip.mp4 -filter_complex \
     "[0:v]crop=608:1080:x='$EXPR':y=0,scale=1080:1920:flags=lanczos[v]" \
     -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
     -c:a aac -b:a 192k /tmp/clipify/clip_panned.mp4
   ```

   For 4K source: downscale first or double all coordinates.

#### Step 4b — Split-screen (both faces always visible)

Two stacked tiles, 1080x960 each. Active speaker's tile on top — overlay flips at speaker changes.

```
[0:v]split=2[a0][a1];
[a0]crop=Wcrop:Hcrop:LX_tile:LY_tile,scale=1080:960,split=2[lt0][lt1];
[a1]crop=Wcrop:Hcrop:RX_tile:RY_tile,scale=1080:960,split=2[rt0][rt1];
[lt0][rt0]vstack[layoutL];
[rt1][lt1]vstack[layoutR];
[layoutL][layoutR]overlay=0:0:enable='<RIGHT_SPEAKER_ENABLE>'[v]
```

Build `<RIGHT_SPEAKER_ENABLE>` from `segments.json` as `between(t,a,b)+between(t,a,b)+...` over the right-speaker segments.

### Step 5 — Add subtitles

Ask once if user hasn't specified a style:

> "Three subtitle styles: opus (big bold white, yellow active-word highlight), karaoke (4-word chunks, green highlight), minimal (clean Helvetica, no highlight). Or paste an example you like."

If they paste a reference image/example: match the font, size, weight, color, position, and animation as closely as possible — write a custom ASS or extend `build_ass.py`.

Else use the preset:

```bash
whisper /tmp/clipify/clip_panned.mp4 --model tiny.en --word_timestamps True --output_format json --output_dir /tmp/clipify --language en
python3 ~/.hermes/skills/media/clipify/scripts/build_ass.py /tmp/clipify/clip_panned.json /tmp/clipify/captions.ass opus
```

Burn captions:

```bash
ffmpeg -y -i /tmp/clipify/clip_panned.mp4 -vf "subtitles=/tmp/clipify/captions.ass" \
  -c:v libx264 -preset fast -crf 20 -c:a copy "$OUTPUT.mp4"
```

### Step 6 — Deliver

- Save each output to `<source_dir>/clipify_out/` (mkdir if missing)
- Print one line per clip: name, duration, what was funny, output path
- Offer to iterate (different style, different ROI, swap to split-screen, retime captions)

## Pitfalls

- **Don't over-tune ROIs.** Two iterations max. Motion-diff is forgiving — wider ROIs covering mouth+chin work fine.
- **Scene cuts inside a clip.** Run `ffmpeg -filter:v "select='gt(scene,0.3)',showinfo" -f null -` to count cuts. If many cuts, fixed face ROIs only work for the dominant scene; warn the user.
- **Source resolution matters.** 4K source: downscale to 1920x1080 first or multiply all ROI/pan coordinates by 2.
- **Burned-in subtitles in source.** If present, find the no-subs master via audio cross-correlation (`audio_align.py`) and trim from there.
- **Don't run whisper on full feature-length source if a short clip suffices.** Whisper the trimmed clip after Step 2; only whisper the full source in Step 1 if you need a transcript to find funny moments.
- **State the plan in one line, then act.** Don't narrate every iteration.

## Scripts

- `scripts/analyze.py` — Speaker timeline from two ROI motion files
- `scripts/build_pan.py` — ffmpeg crop x-expression with hard cuts
- `scripts/build_ass.py` — Opus-style ASS captions from whisper JSON
- `scripts/audio_align.py` — Find offset of a sub-clip in a longer source via FFT cross-correlation
