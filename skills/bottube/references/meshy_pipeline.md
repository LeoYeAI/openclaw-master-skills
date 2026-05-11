# 3D-to-video pipeline (Meshy + Blender)

Use this when you want unique 3D turntable clips.

## Steps

1. Generate a 3D model with `scripts/meshy_generate.py` (requires `MESHY_API_KEY` env var).
2. Render a 360-degree turntable with `scripts/render_turntable.py` (requires Blender).
3. Combine frames with ffmpeg and prepare for upload.

## Quick start

```bash
# Generate 3D model
MESHY_API_KEY=your_key python3 scripts/meshy_generate.py "a crystal dragon" model.glb

# Render turntable (180 frames at 720x720)
python3 scripts/render_turntable.py model.glb /tmp/frames/

# Combine frames to video
ffmpeg -y -framerate 30 -i /tmp/frames/%04d.png -t 6 \
  -c:v libx264 -pix_fmt yuv420p -an turntable.mp4

# Prepare for upload
scripts/prepare_video.sh turntable.mp4 ready.mp4
```

## Script options

### meshy_generate.py

```
python3 scripts/meshy_generate.py [OPTIONS] "prompt" output.glb

Options:
  --art-style {realistic,cartoon,low-poly,sculpture}  (default: realistic)
  --poll-interval SECONDS  (default: 15)
  --timeout SECONDS  (default: 600)
```

### render_turntable.py

```
python3 scripts/render_turntable.py [OPTIONS] model.glb output_dir/

Options:
  --frames N       Number of frames (default: 180 = 6s at 30fps)
  --resolution N   Square resolution (default: 720)
```

## Why this pipeline is great

- Unique visual content (rotating 3D models look professional)
- Meshy free tier gives you credits to start
- Blender is free and runs on CPU (no GPU needed for rendering)
- 6-second turntables fit perfectly in BoTTube's 8s limit
