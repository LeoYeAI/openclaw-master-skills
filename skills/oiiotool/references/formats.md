# Image Format Reference

## Format Capabilities

| Format | Read | Write | Bit Depths | HDR | Alpha | Layers | Tiled | Metadata | Compression |
|--------|------|-------|-----------|-----|-------|--------|-------|----------|-------------|
| **EXR** | Y | Y | 16f, 32f | Y | Y | Y | Y | Rich | zip, piz, zips, dwaa, dwab, none |
| **TIFF** | Y | Y | 8, 16, 32, 32f | Y | Y | Y | Y | Rich | lzw, zip, none, jpeg |
| **PNG** | Y | Y | 8, 16 | N | Y | N | N | Basic | deflate |
| **JPEG** | Y | Y | 8 | N | N | N | N | EXIF | lossy (quality 1-100) |
| **DPX** | Y | Y | 8, 10, 12, 16 | N | Y | N | N | Film/TV | none, rle |
| **HDR** | Y | Y | 32f (RGBE) | Y | N | N | N | Minimal | RLE |
| **WebP** | Y | Y | 8 | N | Y | N | N | Basic | lossy/lossless |
| **BMP** | Y | Y | 8 | N | N | N | N | None | none, rle |
| **TGA** | Y | Y | 8 | N | Y | N | N | Minimal | none, rle |
| **GIF** | Y | Y | 8 (palette) | N | 1-bit | Anim | N | Minimal | lzw |
| **JPEG2000** | Y | Y | 8, 12, 16 | N | Y | N | Y | Basic | lossy/lossless |
| **PSD** | Y | N | 8, 16, 32f | Y | Y | Y | N | Rich | rle, zip |
| **ICO** | Y | Y | 8 | N | Y | Multi | N | None | none |
| **FITS** | Y | Y | 8, 16, 32, 32f | Y | N | N | N | Science | none |

## Common VFX/CGI Format Choices

### EXR — Rendering, Compositing, HDR
The standard for CGI and VFX. Use for:
- Render outputs (beauty, AOVs, cryptomatte)
- Compositing intermediates
- HDR photography / HDRI environment maps
- Any workflow needing >8-bit or floating point

Compression recommendations:
- **piz**: Best for CG renders with large flat areas and noise. Good compression ratio.
- **zip**: Good general purpose lossless. Slightly faster decode than piz.
- **zips**: Scanline zip. Good for streaming reads.
- **dwaa**: Lossy. Very small files (~10x smaller than zip). Quality level 45 is a good default. Excellent for dailies/review.
- **none**: No compression. Fastest I/O, largest files. Use for real-time playback.

```bash
# Recommended for final renders
oiiotool input.exr --compression piz -o output.exr

# Recommended for dailies/review
oiiotool input.exr --compression dwaa:45 -o output.exr

# Tiled for random access (Nuke, Mari)
oiiotool input.exr --tile 64 64 --compression zip -o output.exr
```

### DPX — Film Scanning, DI
Standard for digital intermediate (DI) and film scanning. 10-bit log is the classic format. Use when interfacing with film labs, DI facilities, or older pipelines.

```bash
# Convert EXR to 10-bit DPX
oiiotool input.exr --colorconvert ACEScg ACEScct -d uint10 -o output.dpx
```

### TIFF — Print, Matte Painting, Archival
Versatile format supporting many bit depths. Good for:
- Matte paintings and textures
- Print output
- Archival (lossless, widely supported)

```bash
# High quality 16-bit TIFF
oiiotool input.exr -d uint16 --compression zip -o output.tiff
```

### PNG — Web, UI, Review
Lossless 8/16-bit. Good for:
- Web delivery
- UI elements
- Quick review images
- Anything needing transparency (alpha)

```bash
# Standard 8-bit PNG
oiiotool input.exr -d uint8 -o output.png

# 16-bit PNG (for more precision)
oiiotool input.exr -d uint16 -o output.png
```

### JPEG — Web, Dailies, Thumbnails
Lossy 8-bit. Small files. Good for:
- Web delivery
- Email/Slack sharing
- Thumbnails and contact sheets

```bash
# High quality JPEG
oiiotool input.exr -d uint8 --compression jpeg:95 -o output.jpg

# With JPEG subsampling control
oiiotool input.exr -d uint8 --attrib "jpeg:subsampling" "4:4:4" --compression jpeg:95 -o output.jpg
```

### HDR (Radiance .hdr) — HDRI Environment Maps
RGBE format for HDR images. Limited to 32-bit float equivalent via mantissa+exponent encoding. Common for:
- HDRI environment maps for lighting
- Panoramic HDR captures

```bash
# Convert EXR to HDR
oiiotool input.exr -o output.hdr

# Convert HDR to EXR (for better precision)
oiiotool input.hdr -d half -o output.exr
```

## Bit Depth Selection Guide

| Bit Depth | Flag | Range | Use Case |
|-----------|------|-------|----------|
| uint8 | `-d uint8` | 0-255 | Web, review, final delivery |
| uint16 | `-d uint16` | 0-65535 | Print, archival, high quality |
| half (16f) | `-d half` | ~0.00006-65504 | EXR storage, textures (good balance of range and size) |
| float (32f) | `-d float` | Full IEEE 754 | Compositing intermediates, maximum precision |
| uint10 | `-d uint10` | 0-1023 | DPX film/DI |
| uint12 | `-d uint12` | 0-4095 | DPX, some cameras |
