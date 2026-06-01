# Examples

These examples help an agent map user requests to the stable script entrypoints.

## Example 1: Check whether FFmpeg is available

User intent:

> Check whether this machine can run ffmpeg directly

Recommended command:

```bash
bash scripts/check_ffmpeg.sh
```

If only basic editing support is required:

```bash
bash scripts/check_ffmpeg.sh --profile basic
```

If dependencies are missing, explain what is missing, offer installation guidance, and rerun the check after installation.

If subtitle burn-in may be needed later, run an extra check:

```bash
bash scripts/check_ffmpeg.sh --require-subtitles-filter
```

## Example 2: Keep 8 seconds starting at 00:00:05

User intent:

> Cut an 8-second clip starting from 00:00:05 in `input.mp4`

Recommended command:

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
bash scripts/media_ops.sh clip --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

## Example 3: Fast near-lossless trimming

User intent:

> I only care about speed and I can tolerate keyframe-boundary inaccuracies

Recommended command:

```bash
bash scripts/media_ops.sh clip --mode copy --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

## Example 4: Concatenate two clips

User intent:

> Merge `part1.mp4` and `part2.mp4` into one output file

Recommended command:

```bash
bash scripts/media_ops.sh concat --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

If that fails, retry with re-encoding:

```bash
bash scripts/media_ops.sh concat --mode reencode --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

## Example 5: Extract audio

User intent:

> Export the audio track from the video

Recommended command:

```bash
bash scripts/media_ops.sh extract-audio --input "$taskDir/input.mp4" --output "$taskDir/audio.m4a"
```

## Example 6: Convert MOV to a more compatible MP4

User intent:

> Convert this MOV file into a more standard MP4

Recommended command:

```bash
bash scripts/media_ops.sh transcode --input "$taskDir/input.mov" --output "$taskDir/output.mp4"
```

## Example 7: Export a cover frame

User intent:

> Grab a cover image at the 3-second mark

Recommended command:

```bash
bash scripts/media_ops.sh frame --input "$taskDir/input.mp4" --output "$taskDir/cover.jpg" --time "00:00:03"
```

## Example 8: Inspect media before deciding what to do

User intent:

> Check the codec and duration of this video first

Recommended command:

```bash
bash scripts/media_ops.sh probe --input "input.mp4"
```

## Example 9: Allow overwriting existing output

User intent:

> Overwrite the existing output file directly

Add:

```bash
--overwrite
```

For example:

```bash
bash scripts/media_ops.sh transcode --input "input.mov" --output "output.mp4" --overwrite
```

## Example 10: Verify whether subtitle burn-in is supported

User intent:

> Confirm whether this machine can burn in SRT subtitles directly with ffmpeg

Recommended command:

```bash
bash scripts/check_ffmpeg.sh --require-subtitles-filter
```

If that fails, explain that a full FFmpeg build with `libass` support is required and ask the user to install it manually.

## Example 11: Check whether simple text overlays are possible

User intent:

> I do not necessarily need SRT support. I just need to place a few lines of text at the bottom.

Recommended command:

```bash
bash scripts/check_ffmpeg.sh --require-subtitle-support
```

## Example 12: Prepare the default subtitle font

User intent:

> Keep a reusable local copy of the default subtitle font

Recommended command:

```bash
bash scripts/ensure_subtitle_fonts.sh
```

## Example 13: Use a custom subtitle font cache directory

User intent:

> Download the default subtitle font into a project-specific cache directory

Recommended command:

```bash
bash scripts/ensure_subtitle_fonts.sh --font-dir "./.cache/subtitle-fonts"
```

## Example 14: Generate adaptive ASS subtitles for 9:16 output

User intent:

> Burn subtitles into a portrait video and keep long lines from overflowing the frame

Recommended command:

```bash
bash scripts/ensure_subtitle_fonts.sh

python3 scripts/build_ass_subtitles.py \
  --events-json "events.json" \
  --output-ass "subtitles.ass" \
  --video-width 1080 \
  --video-height 1920 \
  --latin-font-file "$HOME/.cache/ponyflash/fonts/NotoSansCJKsc-Regular.otf" \
  --cjk-font-file "$HOME/.cache/ponyflash/fonts/NotoSansCJKsc-Regular.otf"
```

## Example 15: Burn subtitles with the default workflow

User intent:

> Add subtitles to this video. Use the default style.

Recommended command:

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
bash scripts/media_ops.sh subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

What it does by default:

- probes the input video width and height with `ffprobe`
- builds an adaptive `.ass` file with `scripts/build_ass_subtitles.py`
- prepares the default runtime font in a temporary directory
- burns subtitles with `ffmpeg subtitles=...:fontsdir=...`
- removes temporary subtitle and font files after the final output is written
- deletes `taskDir` afterwards unless you explicitly asked to keep staged files

## Example 16: Expanded default subtitle burn pattern

User intent:

> Show me the full default subtitle burn flow

Recommended workflow:

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$taskDir/input.mp4"
```

```bash
bash scripts/media_ops.sh subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

Notes:

- the command stages fonts and temporary subtitle files automatically
- only the final `final-output.mp4` is kept unless you explicitly request another deliverable such as `--ass-output`
- staged downloads, subtitle sources, and intermediate renders should stay inside `taskDir`
