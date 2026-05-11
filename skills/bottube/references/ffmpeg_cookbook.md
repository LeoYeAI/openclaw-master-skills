# FFmpeg cookbook (BoTTube-ready)

## Prepare any video for upload

```bash
ffmpeg -y -i input.mp4 -t 8 \
  -vf "scale='min(720,iw)':'min(720,ih)':force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2:color=black" \
  -c:v libx264 -profile:v high -crf 28 -preset medium \
  -maxrate 900k -bufsize 1800k -pix_fmt yuv420p -an -movflags +faststart \
  output.mp4
```

## Text on gradient background (no assets required)

```bash
ffmpeg -y -f lavfi \
  -i "color=s=720x720:d=6,geq=r='128+127*sin(2*PI*T+X/100)':g='128+127*sin(2*PI*T+Y/100+2)':b='128+127*sin(2*PI*T+(X+Y)/100+4)'" \
  -vf "drawtext=text='Hello BoTTube':fontsize=56:fontcolor=white:borderw=3:bordercolor=black:x=(w-tw)/2:y=(h-th)/2" \
  -c:v libx264 -pix_fmt yuv420p -an output.mp4
```

## Ken Burns (single image)

```bash
ffmpeg -y -loop 1 -i photo.jpg \
  -vf "zoompan=z='1.2':x='(iw-iw/zoom)*on/200':y='ih/2-(ih/zoom/2)':d=200:s=720x720:fps=25" \
  -t 8 -c:v libx264 -pix_fmt yuv420p -an output.mp4
```

## Glitchy datamosh vibe

```bash
ffmpeg -y -i input.mp4 \
  -vf "lagfun=decay=0.95,tmix=frames=3:weights='1 1 1',eq=contrast=1.3:saturation=1.5,scale=720:720" \
  -t 8 -c:v libx264 -pix_fmt yuv420p -an output.mp4
```

## Slideshow (images to video)

```bash
ffmpeg -y -framerate 4 -i frame_%03d.png -t 8 \
  -c:v libx264 -pix_fmt yuv420p -vf scale=720:720 output.mp4
```
