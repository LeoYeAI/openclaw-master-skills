# Operation Strategy

This document explains how an agent should make decisions when using this skill across different FFmpeg-related tasks.

## General Flow

1. Run `scripts/check_ffmpeg.sh` first.
2. If the task involves subtitles, run an additional subtitle capability check.
3. If dependencies or required filters are missing, explain what is missing, offer installation guidance, and rerun the checks after installation.
4. Confirm input files, output path, time parameters, and overwrite policy.
5. Prefer `scripts/media_ops.sh` over ad-hoc shell commands.
6. After execution, verify that the output file was actually created.
7. Unless the user explicitly asks to keep intermediate files, remove temporary files and caches after the task finishes.
8. For multi-step edits, create a temporary task directory first and keep every non-final file inside it.

Example:

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
```

## Capability Profiles

### `basic`

Used to guarantee that the basic editing path is available. Requires at least:

- `ffmpeg`
- `ffprobe`
- `libx264`
- `aac`

Recommended command:

```bash
bash scripts/check_ffmpeg.sh --profile basic
```

### `full`

Used to guarantee that both subtitle burn-in and basic editing are available. Requires:

- everything in `basic`
- the `subtitles` filter

Recommended command:

```bash
bash scripts/check_ffmpeg.sh --profile full
```

## Subtitle Capability Checks

### Basic check

If the user only asks whether FFmpeg is installed and usable, run:

```bash
bash scripts/check_ffmpeg.sh
```

### Subtitle-specific checks

If the user wants to burn in `.srt` or `.ass` subtitles, run:

```bash
bash scripts/check_ffmpeg.sh --require-subtitles-filter
```

If the user only needs basic editing support, run:

```bash
bash scripts/check_ffmpeg.sh --profile basic
```

If the user only needs simple text overlay support, run:

```bash
bash scripts/check_ffmpeg.sh --require-subtitle-support
```

### Result interpretation

- `subtitles_filter=available`: standard subtitle burn-in is supported
- `drawtext_filter=available`: plain text overlay is supported
- `basic_editing_support=available`: basic editing and common transcoding are supported
- `subtitle_support=full`: both subtitle burn-in and text overlay are available
- `subtitle_support=subtitles_only`: subtitle burn-in is available, but `drawtext` may not be
- `subtitle_support=drawtext_only`: plain text overlay is available, but direct `.srt` / `.ass` burn-in is not
- `subtitle_support=missing`: the current FFmpeg build lacks subtitle-related support

## Media Probe

Useful for:

- checking duration, codec, and resolution first
- deciding whether media is suitable for lossless concat
- confirming input parameters before transcoding

Recommended command:

```bash
bash scripts/media_ops.sh probe --input "input.mp4"
```

## Video Trimming

### Default strategy

Use `reencode` by default, because it is less sensitive to keyframe boundaries and produces more predictable results.

```bash
bash scripts/media_ops.sh clip --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

### When to use `copy`

Prefer `copy` only when the user explicitly wants:

- higher speed
- minimal or no re-encoding loss
- acceptance of keyframe-boundary inaccuracies

```bash
bash scripts/media_ops.sh clip --mode copy --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

## Video Concat

### Default strategy

If clips share the same codec, container, and resolution, prefer `concat + copy`.

```bash
bash scripts/media_ops.sh concat --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

### Fallback strategy

If lossless concat fails, the inputs usually differ in one of these ways:

- different video codec
- different audio codec
- different time base or container parameters

In that case, switch to re-encoding:

```bash
bash scripts/media_ops.sh concat --mode reencode --input "$taskDir/part1.mp4" --input "$taskDir/part2.mp4" --output "$taskDir/merged.mp4"
```

## Audio Extraction

### Default strategy

Use `aac` by default and prefer `.m4a` as the output format.

```bash
bash scripts/media_ops.sh extract-audio --input "$taskDir/input.mp4" --output "$taskDir/audio.m4a"
```

### When to use `copy`

Use `copy` only when the user explicitly wants to preserve the original audio codec and the target container supports it.

```bash
bash scripts/media_ops.sh extract-audio --input "$taskDir/input.mp4" --output "$taskDir/audio.aac" --audio-codec copy
```

## Transcoding

### Default strategy

Prefer broadly compatible Web / app output:

- container: `mp4`
- video codec: `libx264`
- audio codec: `aac`

```bash
bash scripts/media_ops.sh transcode --input "$taskDir/input.mov" --output "$taskDir/output.mp4"
```

### When to customize encoding

Override defaults only when the user explicitly asks for:

- a specific codec
- a specific compression level
- a target bitrate
- a delivery format for a downstream platform

## Frame Capture

Useful for cover images, screenshots at a specific timestamp, and preview frames.

```bash
bash scripts/media_ops.sh frame --input "$taskDir/input.mp4" --output "$taskDir/cover.jpg" --time "00:00:03"
```

## Subtitle Burn-in

### Default strategy

Check whether the current FFmpeg build supports the required filters first.

If subtitle style is unspecified, use the default subtitle workflow, which stages its runtime font in a temporary directory, keeps subtitle sources inside `taskDir`, and cleans them up afterwards.

Preferred stable entrypoint:

```bash
bash scripts/media_ops.sh subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

If the task has explicit requirements for long-line wrapping, portrait / landscape adaptation, or subtitle safe margins, generate `.ass` first and then burn it in with `ffmpeg subtitles`.

Recommended entry point:

```bash
python3 scripts/build_ass_subtitles.py --help
```

Default burn pattern:

1. Probe output dimensions with `ffprobe`
2. Stage the runtime font in a temporary directory
3. Build `.ass` with `scripts/build_ass_subtitles.py`
4. Burn it in with `ffmpeg subtitles=...:fontsdir=...`
5. Delete temporary font files and temporary subtitle files, keeping only explicit deliverables

The default subtitle style should use `1920x1080` as the reference baseline, but scale dynamically at runtime:

- `shortEdge = min(videoWidth, videoHeight)`
- `fontSize = round(shortEdge * 0.0556)`
- `marginV = round(videoHeight * 0.0963)`
- `marginL = marginR = round(videoWidth * 0.0625)`
- `outline = max(1, round(fontSize * 0.0167))`
- `shadow = 1`
- `blur = 1`

Wrapping rules:

- landscape or wide aspect ratio: keep max text width around `videoWidth * 0.90`
- portrait or narrow aspect ratio: keep max text width around `videoWidth * 0.90`
- pre-wrap `.ass` / `.srt` content before rendering whenever possible instead of relying fully on player or filter auto-wrapping
- `scripts/build_ass_subtitles.py` measures text width before deciding where to break lines

### Prerequisite for subtitle tasks

Standard subtitle burn-in requires the `subtitles` filter.

```bash
bash scripts/check_ffmpeg.sh --require-subtitles-filter
```

### Fallback when subtitle filters are missing

If `subtitles` is missing but `drawtext` is available:

- plain text overlays are still possible
- do not claim support for direct `.srt` / `.ass` burn-in

If both are missing:

- stop the subtitle task
- direct the user to install an FFmpeg build with `libass` / `freetype` support

## Overwrite Policy

Do not overwrite outputs by default. Only append `--overwrite` when the user explicitly allows it.

## Cleanup Policy

- Keep only the final deliverables the user explicitly requested, such as `--output` or `--ass-output`.
- Delete temporary concat lists, temporary ASS files, temporary font directories, and failed partial outputs automatically.
- Delete the temporary task directory after moving or confirming the final deliverable.
- If the user explicitly asks to keep reusable fonts, a local copy may be prepared with `scripts/ensure_subtitle_fonts.sh`.

## Out-of-Scope Tasks

The current stable script interface is not a good fit for:

- complex filter chains
- watermark compositing
- picture-in-picture
- multi-track audio/video rearrangement

Subtitle burn-in now has a stable default entrypoint through `media_ops.sh subtitle-burn`.
For more complex subtitle tasks beyond the default workflow, it is acceptable to fall back to raw `ffmpeg` commands after clearly explaining that they are outside the stable skill interface.
