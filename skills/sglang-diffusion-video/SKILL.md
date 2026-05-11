---
name: sglang-diffusion-video
description: "Generate videos using a local SGLang-Diffusion server (Wan2.2, Hunyuan, FastWan, etc.). Use when: user asks to generate, create, or render a video with a locally running SGLang-Diffusion instance. NOT for: cloud-hosted video APIs or image generation (use sglang-diffusion for images). Requires a running SGLang-Diffusion server with a video model loaded."
homepage: https://github.com/sgl-project/sglang
metadata:
 {
   "openclaw":
     {
       "emoji": "🎬",
       "requires": { "bins": ["python3"] },
     },
 }
---

# SGLang-Diffusion Video Generation

Generate videos via a local SGLang-Diffusion server's OpenAI-compatible API.


Video generation is asynchronous and takes several minutes. The script handles
submission, polling, and download automatically.

## Prerequisites

- SGLang-Diffusion server running a video model (default: `http://127.0.0.1:30000`)
- Supported models: Wan2.2-T2V, Wan2.2-I2V, FastWan, Hunyuan
- If the server was started with `--api-key`, set `SGLANG_DIFFUSION_API_KEY` env var

## Generate a video

```bash
python3 {baseDir}/scripts/generate_video.py --prompt "a curious raccoon exploring a garden"
```

## Useful flags

```bash
python3 {baseDir}/scripts/generate_video.py --prompt "ocean waves at sunset" --size 1280x720
python3 {baseDir}/scripts/generate_video.py --prompt "city timelapse" --negative-prompt "blurry, low quality"
python3 {baseDir}/scripts/generate_video.py --prompt "dancing robot" --steps 50 --guidance-scale 7.5 --seed 42
python3 {baseDir}/scripts/generate_video.py --prompt "flying through clouds" --seconds 8 --fps 24 --out ./my-video.mp4
python3 {baseDir}/scripts/generate_video.py --prompt "flying through clouds" --server http://192.168.1.100:30000 --out ./my-video.mp4
python3 {baseDir}/scripts/generate_video.py --prompt "cat playing" --poll-interval 15 --timeout 1800
python3 {baseDir}/scripts/generate_video.py --prompt "animate this scene" --input-image /tmp/scene.png
```

## API key (optional)

Only needed if the SGLang-Diffusion server was started with `--api-key`.
Set `SGLANG_DIFFUSION_API_KEY`, or pass `--api-key` directly:

```bash
python3 {baseDir}/scripts/generate_video.py --prompt "hello" --api-key sk-my-key
```

Or configure in `~/.openclaw/openclaw.json`:


```json5
{
 skills: {
   "sglang-diffusion-video": {
     env: { SGLANG_DIFFUSION_API_KEY: "sk-my-key" },
   },
 },
}
```

## Notes

- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers.
- Output defaults to timestamped MP4 in `/tmp/`.
- Video generation typically takes 5-15 minutes depending on GPU and model size.
- Do not read the video back; report the saved path only.