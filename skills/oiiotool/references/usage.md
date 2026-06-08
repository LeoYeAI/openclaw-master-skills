# oiiotool Usage Examples

## Quick Start

### Convert EXR to viewable PNG
```bash
# Simple (linear to sRGB)
oiiotool input.exr --colorconvert linear srgb -d uint8 -o output.png

# With ACES tone mapping (better for HDR content)
oiiotool input.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png
```

### Check what's in an image
```bash
oiiotool --info -v input.exr
```

## HDR Review Workflows

### Exposure sweep from a single HDR frame
```bash
# Generate multiple exposures to review dynamic range
for ev in -8 -6 -4 -2 0 2 4 6 8; do
  mul=$(python -c "print(2**($ev))")
  oiiotool input.exr --mulc $mul --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o "output_exp${ev}.png"
done

# Or use the helper script
python exposure_sweep.py input.exr --stops -8,-6,-4,-2,0,2,4,6,8
```

### Review a specific exposure level
```bash
# See what's in the highlights (darken by 7 stops)
oiiotool input.exr --mulc 0.0078125 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o highlights.png

# See what's in the shadows (brighten by 4 stops)
oiiotool input.exr --mulc 16 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o shadows.png
```

## Production EXR Workflows

### Efficient multichannel EXR processing
```bash
# Only read RGB from a 50+ channel EXR (saves memory and time)
oiiotool -i:ch=R,G,B heavy_render.exr --resize 1024x0 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o thumbnail.jpg

# Extract just the depth channel
oiiotool -i:ch=depth.Z heavy_render.exr --colormap turbo -d uint8 -o depth_vis.png
```

### EXR sequence to MP4
```bash
# Step 1: Convert EXRs to PNGs
oiiotool --frames 1001-1100 --parallel-frames -i:ch=R,G,B input.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o _tmp/output.####.png

# Step 2: Encode to MP4
ffmpeg -framerate 24 -start_number 1001 -i _tmp/output.%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output.mp4

# Or use the helper script (auto-detects fps, frame range, naming)
python seq_to_video.py /path/to/exr_sequence/
```

### Batch convert a directory
```bash
# Convert all EXRs in a directory to PNGs
oiiotool --frames 1-100 render.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.####.png

# With update mode (skip already-converted frames)
oiiotool -u --frames 1-100 render.####.exr -d uint8 -o output.####.png
```

## Format Conversion

### EXR to delivery formats
```bash
# High quality JPEG for review
oiiotool -i:ch=R,G,B input.exr --colorconvert ACEScg "sRGB - Texture" --attrib "jpeg:subsampling" "4:2:0" --compression "jpeg:90" -d uint8 -o output.jpg

# 16-bit TIFF for print
oiiotool input.exr --colorconvert ACEScg "sRGB - Texture" -d uint16 --compression zip -o output.tiff

# DPX for DI
oiiotool input.exr --colorconvert ACEScg ACEScct -d uint10 -o output.dpx
```

### Re-compress EXR (e.g., for smaller dailies)
```bash
# Lossless to lossy (much smaller files)
oiiotool input.exr --compression dwaa:45 -o output_small.exr

# Scanline to tiled (better for Nuke/Mari)
oiiotool input.exr --tile 64 64 --compression zip -o output_tiled.exr
```

### HDR format conversion
```bash
# HDRI panorama: HDR to EXR
oiiotool panorama.hdr -d half -o panorama.exr

# EXR to HDR
oiiotool input.exr -o output.hdr
```

## Color Space Workflows

### ACEScg render to sRGB PNG
```bash
# Option 1: Simple colorconvert (clips highlights at 1.0)
oiiotool input.exr --colorconvert ACEScg "sRGB - Texture" -d uint8 -o output.png

# Option 2: ACES display transform (tone maps highlights gracefully)
oiiotool input.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png
```

### Apply a show LUT
```bash
# Apply a 3D LUT file
oiiotool input.exr --ociofiletransform show_grade.cube -o output.exr

# Apply and convert to sRGB
oiiotool input.exr --ociofiletransform show_grade.cube --colorconvert ACEScg "sRGB - Texture" -d uint8 -o output.png
```

### Convert between working spaces
```bash
# ACEScg to ACES2065-1 (for archival)
oiiotool input.exr --colorconvert ACEScg ACES2065-1 -o output_aces.exr

# Linear sRGB to ACEScg
oiiotool input.exr --colorconvert "Linear Rec.709 (sRGB)" ACEScg -o output_acescg.exr
```

## Image Manipulation

### Create a contact sheet
```bash
# 3x3 grid of images
oiiotool img_01.exr img_02.exr img_03.exr img_04.exr img_05.exr img_06.exr img_07.exr img_08.exr img_09.exr --mosaic:pad=4 3x3 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o contact.jpg
```

### Resize for dailies
```bash
# Half res
oiiotool input.exr --resize 50% -o half.exr

# Fit to HD (preserves aspect)
oiiotool input.exr --fit 1920x1080 -o hd.exr

# Width only (auto height)
oiiotool input.exr --resize 1024x0 -o thumb.exr
```

### Compare two images
```bash
# Pixel difference report
oiiotool a.exr b.exr --diff

# Visual difference (amplified 10x)
oiiotool a.exr b.exr --absdiff --mulc 10 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o diff.png
```

### Composite foreground over background
```bash
# Standard alpha-over
oiiotool fg.exr bg.exr --over -o comp.exr

# With premultiplication handling
oiiotool fg.exr --unpremult bg.exr --over --premult -o comp.exr
```

### Add text overlay (burn-in)
```bash
# Frame number burn-in on a sequence
oiiotool --frames 1001-1100 input.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" --text:x=50:y=50:size=36:color=1,1,1 "Frame {FRAME_NUMBER}" -d uint8 -o output.####.png
```

## Texture Preparation

### Create mipmapped texture for rendering
```bash
# Standard texture conversion
oiiotool diffuse.exr -otex diffuse.tx

# With specific tile size
oiiotool diffuse.exr --tile 64 64 -otex diffuse.tx

# HDRI environment map
oiiotool panorama.hdr -oenv environment.tx
```

## Data Visualization

### Depth pass to heatmap
```bash
# Using built-in color maps
oiiotool render.exr --ch depth.Z --colormap turbo -d uint8 -o depth_turbo.png
oiiotool render.exr --ch depth.Z --colormap inferno -d uint8 -o depth_inferno.png
oiiotool render.exr --ch depth.Z --colormap viridis -d uint8 -o depth_viridis.png
```

### Normals to RGB visualization
```bash
# World-space normals (remap -1..1 to 0..1)
oiiotool render.exr --ch N.X,N.Y,N.Z --mulc 0.5 --addc 0.5 -d uint8 -o normals.png
```
