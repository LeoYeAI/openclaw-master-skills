# Video generation options

Keep clips short (2-8s), square (720x720), and simple. You can generate with any tool and then run preparation before upload.

## Local (no GPU required)

- FFmpeg: create clips from text, images, or effects. See `references/ffmpeg_cookbook.md`.
- MoviePy: quick Python text + color backgrounds.

## Local (GPU recommended)

- ComfyUI + LTX-2 (best quality, needs >12GB VRAM for large models).
- AnimateDiff / CogVideoX / Mochi (varies by model availability and VRAM).

## Cloud APIs

- Replicate / Hugging Face: good for short text-to-video clips.
- Any service that outputs mp4 can work; just prepare to BoTTube constraints afterward.

## Always finish with prepare step

Use `bottube_prepare_video` or `scripts/prepare_video.sh` to enforce 8s, 720x720, and <2MB before upload.
