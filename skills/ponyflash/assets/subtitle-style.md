# Default Subtitle Style

This style sheet serves as the default subtitle rendering reference for the skill, using a `1920x1080` landscape render as the baseline.

## Fonts

- Default subtitle font: `Noto Sans CJK SC`
- Default runtime behavior:
  - `scripts/media_ops.sh subtitle-burn` stages the font in a temporary directory and deletes it after export
- Explicit keep command:
  - `bash scripts/ensure_subtitle_fonts.sh`

## Baseline Style

The following values correspond to the approved default look for `1920x1080` output:

- font size: `60`
- text color: `#ffffff`
- outline color: `#000000`
- outline width: `1`
- outline join: `round`
- outline cap: `round`
- shadow offset: `1`
- `blur`: `1`
- shadow color: `rgba(0,0,0,0.25)`
- bottom margin: `104`
- left / right safe margin: `120`
- no background box by default

## Adaptive Rules

The default subtitle style should not rely on hardcoded pixel values. It should scale with the output dimensions:

- `shortEdge = min(videoWidth, videoHeight)`
- `fontSize = round(shortEdge * 0.0556)`
- `marginV = round(videoHeight * 0.0963)`
- `marginL = marginR = round(videoWidth * 0.0625)`
- `outline = max(1, round(fontSize * 0.0167))`
- `shadow = 1`
- `blur = 1`

Notes:

- These formulas are derived from the approved `1920x1080` baseline and keep visual density roughly consistent across resolutions.
- Tying font size to `shortEdge` works well across landscape, portrait, and square outputs.
- Tying bottom margin to `videoHeight` helps keep subtitles in the lower-middle area instead of too low on tall screens.
- Tying left / right margins to `videoWidth` helps prevent edge collisions on narrow frames.

## Wrapping and Layout

- For landscape or wide outputs (`videoWidth >= videoHeight`), keep max text width around `90%` of frame width
- For portrait or narrow outputs (`videoWidth < videoHeight`), keep max text width around `90%` of frame width
- Prefer explicit pre-wrapping for long lines instead of relying entirely on subtitle-engine auto-wrap
- Keep multiline subtitles center-aligned so that lines of different lengths still feel visually balanced

## Suggested ASS Mapping

- `PrimaryColour`: white
- `OutlineColour`: black
- `Outline`: `outline`
- `Shadow`: `shadow`
- `Blur`: `blur`
- `MarginV`: `marginV`
- `MarginL` / `MarginR`: `marginL` / `marginR`
- no background box

Notes:

- If you render subtitles with Canvas, Pillow, or a frontend renderer, you can implement the same baseline values and scaling formulas directly.
- If you render with `ffmpeg subtitles` / ASS, map to the closest ASS parameters and insert manual line breaks for long text when needed.

## Usage Notes

- This parameter set works well as a default subtitle reference, especially for light, warm, or medium-contrast video backgrounds.
- On high-contrast scenes, white text with a light outline is usually stable enough. Keep shadow subtle rather than heavy.
- For `9:16` short-video output, prefer reusing the same formulas instead of maintaining a separate fixed portrait preset.
