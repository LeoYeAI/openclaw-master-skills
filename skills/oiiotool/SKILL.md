---
name: oiiotool
description: >
  Image processing with oiiotool CLI — format conversion (EXR, TIFF, DPX, PNG, JPEG, HDR),
  OCIO/ACES color management and display transforms, exposure adjustment, resize/crop,
  compositing, EXR sequence to video, texture baking, image comparison, and batch/sequence
  operations. Use when working with image files, EXR sequences, color spaces, or HDR content.
compatibility: Requires oiiotool (pip install openimageio). ffmpeg needed for video encoding.
metadata:
  author: oumad
  version: "1.0"
  clawdbot: '{"requires":{"bins":["oiiotool","python3"]}}'
---

# oiiotool Skill

Command-line image processing with [OpenImageIO's oiiotool](https://docs.openimageio.org). Industry-standard tool used across VFX, CGI, game dev, and photography for format conversion, color management, compositing, and batch image operations.

## Setup

```bash
pip install openimageio
```

This installs both the `oiiotool` CLI and the `OpenImageIO` Python module.

Verify:
```bash
oiiotool --version
oiiotool --list-formats
```

### OCIO / ACES Configuration

oiiotool uses OpenColorIO for color management. **Since OCIO 2.2+, built-in ACES configs are available — no file download needed:**

```bash
# Use built-in ACES CG config (recommended for most users)
export OCIO=ocio://cg-config-latest

# Or specify per-command
oiiotool --colorconfig ocio://cg-config-latest input.exr ...
```

Available built-in configs:
- `ocio://cg-config-latest` — CG-focused config (no camera color spaces, lean). Recommended.
- `ocio://studio-config-latest` — Full studio config (includes camera color spaces).
- `ocio://cg-config-v4.0.0_aces-v2.0_ocio-v2.5` — Pin to a specific version.

For production studios with a custom config:
```bash
export OCIO=/path/to/studio_config.ocio
```

Check what's available:
```bash
oiiotool --colorconfiginfo
```

## Core Concept: Stack-Based Processing

oiiotool processes commands **left to right** on a stack:
- Naming a file **pushes** it onto the stack
- Commands **pop** inputs, process, and **push** results
- `-o` writes the top of stack to a file

```bash
# Read -> process -> write
oiiotool input.exr --resize 1920x1080 -o output.png

# Two images -> composite -> write
oiiotool fg.exr bg.exr --over -o comp.exr
```

## File Info & Metadata

```bash
# Basic info (resolution, channels, format)
oiiotool --info input.exr

# Verbose info (all metadata)
oiiotool --info -v input.exr

# Pixel statistics (min, max, mean, stddev per channel)
oiiotool --stats input.exr

# Filter metadata with regex
oiiotool --info -v --metamatch "camera|lens" input.exr
```

## Format Conversion

Supported formats: EXR, TIFF, PNG, JPEG, DPX, HDR (Radiance), BMP, TGA, GIF, WebP, JPEG2000, PSD, ICO, FITS, and more.

```bash
# Simple conversion (format inferred from extension)
oiiotool input.exr -o output.png
oiiotool input.dpx -o output.tiff
oiiotool input.hdr -o output.exr

# Control output bit depth
oiiotool input.exr -d uint8 -o output.png       # 8-bit
oiiotool input.exr -d uint16 -o output.png       # 16-bit
oiiotool input.exr -d half -o output.exr         # 16-bit float (half)
oiiotool input.exr -d float -o output.tiff       # 32-bit float

# JPEG quality
oiiotool input.exr -d uint8 --compression jpeg:95 -o output.jpg

# EXR compression types
oiiotool input.exr --compression zip -o output.exr        # lossless, good general
oiiotool input.exr --compression piz -o output.exr        # lossless, best for noisy/CG
oiiotool input.exr --compression zips -o output.exr       # lossless, scanline
oiiotool input.exr --compression dwaa:45 -o output.exr    # lossy, very small files

# Tiled vs scanline EXR
oiiotool input.exr --tile 64 64 -o output.exr
oiiotool input.exr --scanline -o output.exr

# Add dither when going from high bit depth to 8-bit (reduces banding)
oiiotool input.exr -d uint8 --dither -o output.png
```

### Production Tip: Selective Channel Reading

For large multichannel EXRs (beauty + depth + normals + crypto), read only what you need to save memory and time:

```bash
# Read only R,G,B channels (skip depth, normals, cryptomatte, etc.)
oiiotool -i:ch=R,G,B input.exr -o output.png

# Combined with conversion and color management
oiiotool -i:ch=R,G,B input.exr --resize 1024x0 --colorconvert "ACES2065-1" "Rec.1886 Rec.709 - Display" --compression "jpeg:90" -o output.jpg
```

This is critical in production where EXRs can have 50+ channels and be hundreds of MB each.

## Color Management (OCIO)

### Color Space Conversion

```bash
# Convert between named color spaces
oiiotool input.exr --colorconvert ACEScg "sRGB - Texture" -o output.png
oiiotool input.exr --colorconvert linear srgb -o output.png
oiiotool input.exr --tocolorspace "sRGB - Texture" -o output.png

# Set the assumed input color space (without changing pixels)
oiiotool input.png --iscolorspace srgb --tocolorspace linear -o linear.exr
```

### ACES Display Transforms (Tone Mapping)

The proper way to view HDR content. Applies the ACES Reference Rendering Transform (RRT) + Output Device Transform (ODT) for correct highlight rolloff:

```bash
# sRGB monitor (most common for web/review)
oiiotool input.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png

# Rec.709 broadcast
oiiotool input.exr --ociodisplay "Rec.1886 Rec.709 - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png

# DCI-P3 cinema
oiiotool input.exr --ociodisplay "P3-D65 - Display" "ACES 1.0 - SDR Cinema" -d uint8 -o output.png

# HDR (1000 nits, PQ)
oiiotool input.exr --ociodisplay "Rec.2100-PQ - Display" "ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)" -d uint16 -o output.png

# Un-tone-mapped (linear to display, no RRT — useful for comparing raw values)
oiiotool input.exr --ociodisplay "sRGB - Display" "Un-tone-mapped" -d uint8 -o output.png
```

> **When to use display transforms vs colorconvert:** Use `--ociodisplay` when converting HDR scene-referred data to a display for viewing (applies tone mapping). Use `--colorconvert` when converting between working color spaces (no tone mapping, preserves linearity).

### OCIO Looks & File Transforms

```bash
# Apply an OCIO look (e.g., ACES gamut compression)
oiiotool input.exr --ociolook "ACES 1.3 Reference Gamut Compression" -o output.exr

# Apply a file-based transform (3D LUT, CDL, CLF)
oiiotool input.exr --ociofiletransform my_grade.cube -o output.exr

# Inverse
oiiotool input.exr --ociofiletransform:inverse=1 my_grade.cube -o output.exr
```

### Manual Matrix Color Conversion

When you don't have OCIO or need a specific 3x3 matrix:

```bash
# ACEScg to linear sRGB (comma-separated, row-major)
oiiotool input.exr --ccmatrix "1.70505,-0.62179,-0.08326,-0.13026,1.14080,-0.01055,-0.02400,-0.12897,1.15297" -o output.exr
```

## Exposure Adjustment

EXR stores linear light values. Exposure in stops is powers of 2:

```bash
# Lower exposure (darken) — reveal HDR highlights
oiiotool input.exr --mulc 0.0625 -o output.exr        # -4 stops
oiiotool input.exr --mulc 0.0078125 -o output.exr      # -7 stops

# Raise exposure (brighten) — reveal shadow detail
oiiotool input.exr --mulc 4 -o output.exr              # +2 stops
oiiotool input.exr --mulc 16 -o output.exr             # +4 stops

# Fractional stops
oiiotool input.exr --mulc 0.00407 -o output.exr        # -7.6 stops
```

**Exposure + ACES display transform** (most useful combo for HDR review):

```bash
oiiotool input.exr --mulc 0.0078125 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output_exp-7.png
```

### Exposure Reference Table

| Stops | Multiplier | Formula | Use Case |
|-------|-----------|---------|----------|
| +8    | 256       | 2^8     | Deep shadow recovery |
| +6    | 64        | 2^6     | Dark shadow detail |
| +4    | 16        | 2^4     | Shadow detail |
| +2    | 4         | 2^2     | Slight brighten |
| 0     | 1         | 2^0     | Native exposure |
| -2    | 0.25      | 2^-2    | Slight darken |
| -4    | 0.0625    | 2^-4    | Highlight recovery |
| -6    | 0.015625  | 2^-6    | Bright highlight detail |
| -8    | 0.00390625| 2^-8    | Extreme highlight recovery |

## Ready-Made Scripts

### Exposure Sweep

Generate a composite contact sheet of multiple exposures from an HDR EXR:

```bash
python scripts/exposure_sweep.py input.exr
python scripts/exposure_sweep.py input.exr --stops -8,-6,-4,-2,0,2,4,6,8
python scripts/exposure_sweep.py input.exr --display "sRGB - Display" --view "ACES 1.0 - SDR Video"
python scripts/exposure_sweep.py input.exr --cols 4 --output sweep.jpg
```

### EXR Sequence to Video

Convert an EXR image sequence to MP4:

```bash
python scripts/seq_to_video.py /path/to/sequence/
python scripts/seq_to_video.py /path/to/sequence/ --fps 24 --crf 18
python scripts/seq_to_video.py /path/to/sequence/ --display "sRGB - Display" --view "ACES 1.0 - SDR Video"
python scripts/seq_to_video.py /path/to/sequence/ --exposure -4 --output comp.mp4
```

Requires `ffmpeg` in PATH.

## Image Operations

### Resize & Fit

```bash
# Resize to exact dimensions
oiiotool input.exr --resize 1920x1080 -o output.exr

# Resize by percentage
oiiotool input.exr --resize 50% -o output.exr

# Resize width only, preserve aspect (height=0 means auto)
oiiotool input.exr --resize 1024x0 -o output.exr

# Fit within dimensions (preserves aspect ratio, no stretching)
oiiotool input.exr --fit 1920x1080 -o output.exr

# Fit and pad to exact dimensions
oiiotool input.exr --fit:pad=1 1920x1080 -o output.exr

# Choose resize filter
oiiotool input.exr --resize:filter=lanczos3 1920x1080 -o output.exr

# Fix pixel aspect ratio
oiiotool input.exr --pixelaspect 2.0 -o output.exr
```

Available filters: `box`, `triangle`, `gaussian`, `catmull-rom`, `blackman-harris`, `sinc`, `lanczos3`, `mitchell`, `bspline`, `cubic`. Default `lanczos3` is good for most uses.

### Crop & Cut

```bash
# Crop to region (WxH+X+Y — adjusts data window, keeps display window)
oiiotool input.exr --crop 1920x1080+100+50 -o output.exr

# Cut (crop + reposition to origin)
oiiotool input.exr --cut 1920x1080+100+50 -o output.exr

# Crop to full/display window
oiiotool input.exr --croptofull -o output.exr

# Auto-trim black borders
oiiotool input.exr --trim -o output.exr
```

### Rotate & Flip

```bash
oiiotool input.exr --rotate90 -o output.exr      # 90 CW
oiiotool input.exr --rotate180 -o output.exr
oiiotool input.exr --rotate270 -o output.exr      # 90 CCW
oiiotool input.exr --flip -o output.exr           # vertical mirror
oiiotool input.exr --flop -o output.exr           # horizontal mirror
oiiotool input.exr --transpose -o output.exr
oiiotool input.exr --rotate 45 -o output.exr      # arbitrary angle

# Auto-orient based on EXIF
oiiotool --autoorient input.jpg -o output.jpg
```

### Blur & Sharpen

```bash
# Gaussian blur
oiiotool input.exr --blur 5x5 -o output.exr
oiiotool input.exr --blur:kernel=gaussian 10x10 -o output.exr

# Median filter (salt-and-pepper noise removal)
oiiotool input.exr --median 3x3 -o output.exr

# Unsharp mask (sharpen)
oiiotool input.exr --unsharp:kernel=gaussian:width=3:contrast=1.5 -o output.exr

# Morphological ops
oiiotool input.exr --dilate 3x3 -o output.exr
oiiotool input.exr --erode 3x3 -o output.exr
```

## Channel Operations

```bash
# Select/reorder channels
oiiotool input.exr --ch R,G,B -o output.exr         # drop alpha
oiiotool input.exr --ch B,G,R -o output.exr         # BGR swap
oiiotool input.exr --ch R,G,B,A=1.0 -o output.exr   # add solid alpha
oiiotool input.exr --ch 0 -o output.exr             # first channel only

# Rename channels
oiiotool input.exr --chnames R,G,B -o output.exr

# Combine channels from multiple files
oiiotool rgb.exr alpha.exr --chappend -o rgba.exr

# Luminance (sum weighted channels)
oiiotool input.exr --chsum:weight=0.2126,0.7152,0.0722 -o luminance.exr

# Split layer-named channels into separate images
oiiotool multilayer.exr --layersplit -o layer.exr
```

## Compositing

```bash
# Alpha-over composite
oiiotool fg.exr bg.exr --over -o comp.exr

# Paste fg at position
oiiotool bg.exr fg.exr --paste +100+50 -o comp.exr

# Depth-based composite (Z channel)
oiiotool a.exr b.exr --zover -o comp.exr

# Mosaic/contact sheet
oiiotool img1.exr img2.exr img3.exr img4.exr --mosaic 2x2 -o grid.exr
oiiotool img*.exr --mosaic:pad=4 3x3 -o contact.exr

# Math operations between two images
oiiotool a.exr b.exr --add -o sum.exr
oiiotool a.exr b.exr --mul -o product.exr
oiiotool a.exr b.exr --absdiff -o diff.exr
oiiotool a.exr b.exr --max -o max.exr
oiiotool a.exr b.exr --min -o min.exr
```

## Color & Value Adjustments

```bash
# Multiply (exposure, tint)
oiiotool input.exr --mulc 2.0 -o output.exr              # all channels
oiiotool input.exr --mulc 1.1,1.0,0.9 -o output.exr      # per-channel warm tint

# Add offset
oiiotool input.exr --addc 0.1 -o output.exr

# Power/gamma
oiiotool input.exr --powc 2.2 -o output.exr              # apply gamma
oiiotool input.exr --powc 0.4545 -o output.exr            # remove gamma

# Invert colors
oiiotool input.exr --invert -o output.exr

# Clamp values
oiiotool input.exr --clamp:min=0:max=1 -o output.exr

# Contrast (S-curve)
oiiotool input.exr --contrast:black=0.1:white=0.9:scontrast=2.0 -o output.exr

# Saturation
oiiotool input.exr --saturate 1.5 -o output.exr          # boost
oiiotool input.exr --saturate 0 -o output.exr             # desaturate

# Range compress (HDR -> log preview)
oiiotool input.exr --rangecompress -o output.exr

# Fix NaN/Inf values
oiiotool input.exr --fixnan black -o output.exr
oiiotool input.exr --fixnan box3 -o output.exr            # interpolate neighbors

# False color visualization
oiiotool depth.exr --colormap inferno -o heatmap.png
oiiotool depth.exr --colormap viridis -o heatmap.png
oiiotool depth.exr --colormap turbo -o heatmap.png
```

## Drawing & Annotation

```bash
# Text overlay
oiiotool input.exr --text:x=20:y=40:size=24:color=1,1,1 "Frame 001" -o output.exr

# Draw box outline
oiiotool input.exr --box:color=1,0,0 100,100,500,400 -o output.exr

# Draw lines
oiiotool input.exr --line:color=0,1,0 0,0,100,100 -o output.exr

# Fill region with solid color
oiiotool input.exr --fill:color=0,0,1 100x100+50+50 -o output.exr

# Create solid color image from scratch
oiiotool --create 1920x1080 3 --fill:color=0.18,0.18,0.18 1920x1080+0+0 -o gray18.exr
```

## Sequence Processing

oiiotool supports frame number wildcards for batch operations:

```bash
# '#' expands to frame numbers (padded to match # count)
oiiotool --frames 1001-1100 input.####.exr --resize 50% -o output.####.exr

# printf-style patterns
oiiotool --frames 1001-1100 input.%04d.exr -o output.%04d.png

# Frame step (every other frame)
oiiotool --frames 1-100x2 input.####.exr -o output.####.exr

# Skip missing frames
oiiotool --frames 1001-1100 --skip-bad-frames input.####.exr -o output.####.png

# Parallel frame processing (use all cores)
oiiotool --frames 1001-1100 --parallel-frames input.####.exr --resize 1920x1080 -o output.####.exr

# ACES display transform on entire sequence
oiiotool --frames 1001-1100 input.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.####.png

# Exposure + display transform on sequence
oiiotool --frames 1001-1100 input.####.exr --mulc 0.0625 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.####.png

# Read only RGB channels for efficiency on multichannel sequences
oiiotool --frames 1001-1100 -i:ch=R,G,B input.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.####.png
```

### Sequence to Video (with ffmpeg)

Two-step process:

```bash
# Step 1: Convert EXR sequence to PNG
oiiotool --frames 1001-1100 --parallel-frames input.####.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o _tmp/output.####.png

# Step 2: Encode with ffmpeg
ffmpeg -framerate 24 -start_number 1001 -i _tmp/output.%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output.mp4
```

Or use the helper script: `python scripts/seq_to_video.py /path/to/sequence/`

## Texture Baking

```bash
# Tiled, mipmapped texture for rendering engines
oiiotool input.exr -otex output.tx

# Environment map (lat-long to cube)
oiiotool latlong.hdr -oenv environment.tx

# Bump map processing
oiiotool bump.exr -obump normals.tx
```

## Image Comparison

```bash
# Difference report
oiiotool a.exr b.exr --diff

# Perceptual difference
oiiotool a.exr b.exr --pdiff

# With thresholds
oiiotool a.exr b.exr --fail 0.001 --failpercent 1 --diff

# Visual difference (amplified)
oiiotool a.exr b.exr --absdiff --mulc 10 -o diff_amplified.exr

# Count pixels matching a color
oiiotool input.exr --colorcount "0,0,0"

# Count pixels outside a range
oiiotool input.exr --rangecheck 0,0,0 1,1,1
```

## Patterns & Test Images

```bash
# Black
oiiotool --create 1920x1080 3 -o black.exr

# Constant color
oiiotool --pattern constant:color=0.5,0.5,0.5 1920x1080 3 -o gray50.exr

# Checker
oiiotool --pattern checker:color1=0.2,0.2,0.2:color2=0.8,0.8,0.8:width=64:height=64 1920x1080 3 -o checker.exr

# Noise
oiiotool --pattern noise:type=gaussian:mean=0.5:stddev=0.1 1920x1080 3 -o noise.exr
```

## Metadata Manipulation

```bash
# Set metadata
oiiotool input.exr --attrib "Artist" "John Doe" -o output.exr
oiiotool input.exr --attrib:type=float "exposure" 1.5 -o output.exr

# Remove metadata by pattern
oiiotool input.exr --eraseattrib "camera.*" -o output.exr

# Copy metadata from one image to another
oiiotool source.exr target.exr --pastemeta -o output.exr

# Set caption
oiiotool input.exr --caption "Final comp v3" -o output.exr
```

## Deep Image Operations

```bash
# Flatten deep image to regular 2D
oiiotool deep.exr --flatten -o flat.exr

# Convert regular image to deep
oiiotool input.exr --deepen -o deep.exr

# Merge two deep images
oiiotool a_deep.exr b_deep.exr --deepmerge -o merged.exr

# Deep holdout
oiiotool fg_deep.exr holdout_deep.exr --deepholdout -o result.exr
```

## Cryptomatte Visualization

```bash
# Built-in cryptomatte to color matte
oiiotool input.exr --cryptomatte-colors crypto_material -o material_colors.exr
```

> For advanced cryptomatte extraction with custom palettes and batch processing, see the **exr** skill.

## Performance Tips

- `--threads N` — control parallelism (default: all cores)
- `--parallel-frames` — parallelize sequence processing
- `-i:ch=R,G,B` — read only needed channels from multichannel EXRs
- `--cache MB` — increase image cache for large files
- `--native` — bypass cache for one-shot operations
- `--autotile 64` — better cache performance with large scanline images
- `-u` — update mode: skip outputs newer than inputs

## Related Skills

- **exr** — Python-level EXR internals: channel inspection, cryptomatte extraction with custom palettes, beauty pass extraction with ACEScg matrix. Use when you need fine-grained channel access or cryptomatte decoding beyond what `--cryptomatte-colors` provides.
