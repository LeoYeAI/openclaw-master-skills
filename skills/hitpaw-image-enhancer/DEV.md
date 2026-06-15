# Development Guide

## Build

```bash
npm install
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## Test

### Images

```bash
export HITPAW_API_KEY=your_key
node dist/cli.js -u https://example.com/photo.jpg -o out.jpg -m general_2x
```

### Videos

```bash
export HITPAW_API_KEY=your_key
node dist/video-cli.js -u https://example.com/video.mp4 -o out.mp4 -m upscale_2x
```

## CLI Commands

- `enhance-image` - image enhancement (main entry)
- `enhance-video` - video enhancement

Options for both commands are similar; see `--help` for details.

## Publish to ClawHub

```bash
clawhub login
clawhub publish .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and ensure `npm run build` passes
4. Submit a Pull Request

---

## Notes

- Video API may not be fully documented; models listed based on HitPaw product pages.
- If API returns `Unsupported model`, check the official docs for latest model names.
- Video jobs can take a long time; adjust `--timeout` accordingly.
- Always test with a small video first to estimate coin consumption.

## Disclaimer

This skill integrates with HitPaw API. You must have a valid API key and comply with HitPaw's terms. The skill author is not responsible for any charges incurred.
