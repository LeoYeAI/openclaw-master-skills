# ACES Display Transforms Reference

## OCIO Configuration

oiiotool uses OpenColorIO (OCIO) for color management. Since OCIO 2.2+, built-in ACES configs ship with the library — no external files needed.

### Built-in Configs (OCIO 2.2+)

Set via `$OCIO` env var or `--colorconfig`:

| URI | Description |
|-----|-------------|
| `ocio://cg-config-latest` | Latest CG config. No camera spaces, lean. Recommended for most users. |
| `ocio://studio-config-latest` | Latest Studio config. Includes camera spaces (ARRI, RED, Sony, etc.). |
| `ocio://cg-config-v4.0.0_aces-v2.0_ocio-v2.5` | Pinned CG config with ACES 2.0. |
| `ocio://studio-config-v4.0.0_aces-v2.0_ocio-v2.5` | Pinned Studio config with ACES 2.0. |
| `ocio://cg-config-v2.0.0_aces-v1.3_ocio-v2.1` | Older CG config, ACES 1.3. |

### CG Config vs Studio Config

- **CG Config**: Minimalist. Color spaces for CGI rendering: ACEScg, ACES2065-1, ACEScct, sRGB, Rec.709, P3, Rec.2020. No camera IDTs. Best for artists who work primarily with rendered imagery.
- **Studio Config**: Full. Adds camera input transforms for ARRI (LogC3, LogC4), RED (Log3G10), Sony (S-Log3/S-Gamut3.Cine), Canon, Panasonic, etc. Needed when working with live-action footage.

### Custom Studio Config

Productions often customize configs to add show-specific LUTs, looks, or file rules:

```bash
export OCIO=/path/to/studio_config.ocio
```

The config file is a YAML `.ocio` file. Key customizations include:
- Custom `file_rules` for auto-detecting color spaces from filenames
- Additional `looks` (CDL grades, show LUTs)
- Modified `displays` and `views`

## Display/View Combinations

### SDR Output (most common)

| Display | View | Use Case |
|---------|------|----------|
| `sRGB - Display` | `ACES 1.0 - SDR Video` | sRGB monitors, web, review. **Most common.** |
| `Rec.1886 Rec.709 - Display` | `ACES 1.0 - SDR Video` | HD broadcast (Rec.709 with 2.4 gamma). |
| `P3-D65 - Display` | `ACES 1.0 - SDR Cinema` | DCI-P3 cinema projection. |

### HDR Output

| Display | View | Use Case |
|---------|------|----------|
| `Rec.2100-PQ - Display` | `ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)` | HDR TV (PQ, Rec.2020 gamut, 1000 nit). |
| `ST2084-P3-D65 - Display` | `ACES 1.1 - HDR Video (1000 nits & P3 lim)` | HDR cinema (PQ, P3 gamut, 1000 nit). |

### Utility Views

| Display | View | Use Case |
|---------|------|----------|
| Any | `Un-tone-mapped` | Linear to display, no RRT. For comparing raw values. |
| Any | `Raw` | No transform at all. For data passes (depth, normals, IDs). |

## oiiotool Syntax

```bash
# SDR sRGB (most common)
oiiotool input.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png

# With explicit config (if $OCIO is not set)
oiiotool --colorconfig ocio://cg-config-latest input.exr --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png

# HDR PQ output (use 16-bit for HDR)
oiiotool input.exr --ociodisplay "Rec.2100-PQ - Display" "ACES 1.1 - HDR Video (1000 nits & Rec.2020 lim)" -d uint16 -o output.png

# With exposure adjustment
oiiotool input.exr --mulc 0.0625 --ociodisplay "sRGB - Display" "ACES 1.0 - SDR Video" -d uint8 -o output.png
```

## Common Working Color Spaces

| Name | Aliases | Description |
|------|---------|-------------|
| `ACEScg` | `lin_ap1` | AP1 primaries, linear. The standard CGI working space. |
| `ACES2065-1` | `lin_ap0` | AP0 primaries, linear. The ACES interchange/archival space. |
| `ACEScct` | `acescct_ap1` | AP1 primaries, log encoding. For grading. |
| `ACEScc` | `acescc_ap1` | AP1 primaries, log encoding. Older grading space. |
| `Linear Rec.709 (sRGB)` | `lin_srgb`, `lin_rec709` | Rec.709/sRGB primaries, linear. |
| `sRGB - Texture` | `srgb_tx` | sRGB gamma + Rec.709 primaries. For 8-bit textures. |
| `Raw` | — | No transform. For data (depth, normals, IDs). |

## colorconvert vs ociodisplay

- **`--colorconvert SRC DST`**: Converts between working color spaces. No tone mapping. Preserves linearity. Use for pipeline conversions (e.g., ACEScg to linear sRGB for a compositing tool).

- **`--ociodisplay DISPLAY VIEW`**: Applies the full ACES Output Transform (RRT + ODT). Includes tone mapping with proper highlight rolloff and shadow lift. Use when preparing images for human viewing on a specific display type.

## ACES Version History (Brief)

| Version | Key Changes |
|---------|-------------|
| ACES 1.0 | Original SDR output transforms (Rec.709, sRGB, P3, DCDM). |
| ACES 1.1 | Added HDR output transforms (PQ 1000/2000/4000 nit). |
| ACES 1.3 | Added Reference Gamut Compression (LMT) to handle out-of-gamut colors. |
| ACES 2.0 | New output transform with improved highlight rendering, better skin tones, reduced hue shifts. Major update. |
