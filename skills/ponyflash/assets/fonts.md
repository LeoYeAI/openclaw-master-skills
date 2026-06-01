# Subtitle Fonts

The repository no longer ships binary font files. Subtitle fonts are prepared on demand at runtime.

## Default Font Strategy

- Use `Noto Sans CJK SC` for both Latin text and Simplified Chinese subtitles.
- Keep a reusable downloaded font under `~/.cache/ponyflash/fonts/` only when the user explicitly runs the font preparation script.
- Allow overriding the cache directory with `PONYFLASH_FONT_DIR`.

## Explicit Keep Command

```bash
bash scripts/ensure_subtitle_fonts.sh
```

Quiet mode prints only the resolved font file path:

```bash
bash scripts/ensure_subtitle_fonts.sh --quiet
```

## Download Sources

The default script tries these sources in order:

1. `https://mirrors.aliyun.com/CTAN/fonts/notocjksc/NotoSansCJKsc-Regular.otf`
2. `https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf`

You can override the primary URL with `PONYFLASH_NOTO_FONT_URL`.

## Intended Usage

In the default workflow:

1. Run `scripts/media_ops.sh subtitle-burn`
2. Let the script create a temporary font directory automatically
3. Keep only the final requested output and remove temporary font files afterwards

## Notes

- `Noto Sans CJK SC` covers Simplified Chinese and common Latin text, which keeps the upload package text-only while preserving stable subtitle rendering.
- `scripts/ensure_subtitle_fonts.sh` is the opt-in path for keeping a reusable font copy on disk.
- `fontsdir` should point to a directory that contains only font files when possible.
- If you want to use custom fonts instead, pass `--latin-font-file` and `--cjk-font-file` explicitly.
