# PonyFlash — Agent Skill

Generate images, videos, speech audio, and music through the [PonyFlash](https://ponyflash.com) Python SDK, and handle local media editing with FFmpeg.

Compatible with the [Agent Skills](https://agentskills.io/specification) open standard. Works with **Claude Code, OpenClaw, Cursor, Codex, Gemini CLI, Windsurf, Cline** and 40+ other AI agents.

## Quick Install

### Git (all agents)

```bash
git clone https://github.com/ponyflash/ponyflash-skill.git ponyflash
```

Then move the `ponyflash` folder into your agent's skills directory.

### OpenClaw

```bash
# From ClawHub (if published)
clawhub install ponyflash

# Or manually
git clone https://github.com/ponyflash/ponyflash-skill.git ~/.openclaw/skills/ponyflash
```

### Claude Code

```bash
git clone https://github.com/ponyflash/ponyflash-skill.git .claude/skills/ponyflash
```

### Cursor

```bash
git clone https://github.com/ponyflash/ponyflash-skill.git .cursor/skills/ponyflash
```

### Skills Directory by Agent

| Agent | Project-level | Global |
|-------|--------------|--------|
| Claude Code | `.claude/skills/ponyflash/` | `~/.claude/skills/ponyflash/` |
| OpenClaw | `skills/ponyflash/` | `~/.openclaw/skills/ponyflash/` |
| Cursor | `.cursor/skills/ponyflash/` | `~/.cursor/skills/ponyflash/` |
| Codex | `.codex/skills/ponyflash/` | `~/.codex/skills/ponyflash/` |
| Windsurf | `.windsurf/skills/ponyflash/` | `~/.codeium/windsurf/skills/ponyflash/` |
| Cline | `.cline/skills/ponyflash/` | `~/.cline/skills/ponyflash/` |

## What This Skill Does

This skill now combines **PonyFlash cloud generation** and **local FFmpeg media processing**.

| Capability | Description |
|---|---|
| Image generation | Text-to-image, image editing with mask/reference images |
| Video generation | Text-to-video, first-frame-to-video, OmniHuman, Motion Transfer |
| Speech synthesis | Text-to-speech with voice cloning, emotion & speed control |
| Music generation | Text-to-music with lyrics, style, instrumental mode, continuation |
| Model listing | List available models, get model details and supported modes |
| File management | Upload, list, get, delete files |
| Account | Check credit balance, get recharge link |
| Local media editing | Clip, concat, transcode, extract audio, and frame capture through `scripts/media_ops.sh` |
| FFmpeg capability checks | Detect `ffmpeg` / `ffprobe`, subtitle filters, and editing profile support |
| Subtitle burn-in | Burn subtitles with `scripts/media_ops.sh subtitle-burn` using the default workflow and on-demand fonts |
| Subtitle prep | Build adaptive ASS subtitles with `scripts/build_ass_subtitles.py` |

## Prerequisites

### PonyFlash cloud generation

```bash
pip install ponyflash
export PONYFLASH_API_KEY="rk_xxx"
```

### Local FFmpeg editing

Local editing does not require a PonyFlash API key, but it does require working `ffmpeg` / `ffprobe` binaries on the machine.

Check with:

```bash
bash scripts/check_ffmpeg.sh
```

If you also need subtitle burn-in:

```bash
bash scripts/check_ffmpeg.sh --require-subtitles-filter
```

The default `subtitle-burn` workflow prepares and removes its temporary subtitle font automatically. Only run this command when you explicitly want to keep a reusable local copy:

```bash
bash scripts/ensure_subtitle_fonts.sh
```

## Quick Examples

### PonyFlash SDK

```python
from ponyflash import PonyFlash

pony_flash = PonyFlash()

gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="A sunset over mountains",
    resolution="2K",
)
print(gen.url)
```

### FFmpeg editing

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
bash scripts/media_ops.sh clip --input "$taskDir/input.mp4" --output "$taskDir/clip.mp4" --start "00:00:05" --duration "8"
```

### Default subtitle burn-in

```bash
taskDir="$(mktemp -d "${TMPDIR:-/tmp}/ponyflash-task.XXXXXX")"
bash scripts/media_ops.sh subtitle-burn --input "$taskDir/input.mp4" --subtitle-file "$taskDir/subtitles.srt" --output "final-output.mp4"
```

See [SKILL.md](SKILL.md) for full usage instructions.

Useful references:

- [reference/operations.md](reference/operations.md)
- [reference/examples.md](reference/examples.md)
- [assets/subtitle-style.md](assets/subtitle-style.md)
- [assets/fonts.md](assets/fonts.md)

## Directory Structure

```text
ponyflash/
├── SKILL.md
├── README.md
├── LICENSE
├── assets/
│   ├── fonts.md
│   └── subtitle-style.md
├── examples/
│   ├── quickstart.py
│   └── advanced.md
├── playbooks/
│   ├── INDEX.md
│   └── crepal-director.md
├── reference/
│   ├── account.md
│   ├── examples.md
│   ├── files.md
│   ├── images.md
│   ├── models.md
│   ├── music.md
│   ├── operations.md
│   ├── speech.md
│   ├── video.md
│   └── models/
│       ├── INDEX.md
│       └── (per-model docs)
└── scripts/
    ├── build_ass_subtitles.py
    ├── check_ffmpeg.sh
    ├── ensure_subtitle_fonts.sh
    └── media_ops.sh
```

## Notes on Fonts

The default subtitle workflow downloads `Noto Sans CJK SC` into a temporary directory, burns the subtitles, and removes the temporary font files when the task finishes. Only `scripts/ensure_subtitle_fonts.sh` keeps a reusable local copy under `~/.cache/ponyflash/fonts/`. You can override that cache directory with `PONYFLASH_FONT_DIR` or pass explicit font file paths to `scripts/media_ops.sh subtitle-burn`.

## Cleanup Policy

- By default, clip, concat, transcode, audio extraction, frame capture, and subtitle burn-in write to temporary paths first and only keep the final `--output` file on success.
- Temporary concat lists, temporary ASS files, staged font directories, and partial outputs are removed automatically.
- If you explicitly pass a path such as `--output` or `--ass-output`, that path is treated as a user-requested deliverable and is kept.
- For multi-step editing workflows, create a temporary task directory first and keep staged downloads, subtitle files, and intermediate renders inside it. Delete that directory after confirming the final deliverable unless the user explicitly asked to keep intermediates.

## Contributing

1. Fork this repo
2. Add or update skill content
3. Follow the [Agent Skills specification](https://agentskills.io/specification)
4. Submit a PR

## License

[MIT](LICENSE)
