# Shader Variants

lilToon includes many shader files to cover different rendering needs and optimization levels. This document explains the naming conventions and the purpose of specific variants found in the `Assets/lilToon/Shader` directory.

## Naming Convention

The shader filenames generally follow this pattern:
`[Prefix]_[Feature]_[RenderingMode]_[OutlineMode].shader`

### 1. Prefixes (Editions)
*   **`lts`**: **Standard**. The full-featured lilToon shader. Use this for most characters and objects.
*   **`ltsl`**: **Lite**. A lightweight version with reduced features for better performance. Useful for background objects or crowds.
*   **`ltsmulti`**: **Multi**. Optimized for multi-material setups or specific specialized rendering.

### 2. Rendering Modes
*   **(None)**: **Opaque**. Solid objects with no transparency.
*   **`cutout`**: **Cutout**. Alpha testing (hard edges). Pixels are either fully visible or discarded. Good for fences, grates, or hair.
*   **`trans` / `transparent`**: **Transparent**. Alpha blending. For glass, semi-transparent fabrics, etc.
*   **`onetrans`**: **One-Pass Transparent**. Standard transparency.
*   **`twotrans`**: **Two-Pass Transparent**. Renders backfaces first, then frontfaces. Improves sorting for double-sided transparent objects (like hollow glass spheres).

### 3. Features
*   **`tess`**: **Tessellation**. Uses DX11 Tessellation to subdivide geometry for smoother curves and displacement. Expensive but high quality.
*   **`fur`**: **Fur**. Uses multi-pass rendering (shells) to simulate volumetric fur or grass.
*   **`gem`**: **Gem**. Specialized for gemstones, featuring internal reflection and refraction approximations.
*   **`ref`**: **Refraction**. Fetches the screen buffer to simulate distortion (glass/water).
*   **`fakeshadow`**: **Fake Shadow**. Likely a projector or specialized shadow receiver/caster variant.

### 4. Outline Modes
*   **`o`**: **Outline**. The shader includes an outline pass (Inverted Hull method).
*   **`oo`**: **Outline Only**. Renders *only* the outline. Useful for multi-pass setups where the main mesh is rendered by a different shader.

## Detailed Variant Explanations

### Fur Shaders (`lts_fur*`)
These shaders render the mesh multiple times (shells) to create the illusion of volume.
*   **`lts_fur`**: Standard opaque fur.
*   **`lts_fur_cutout`**: Fur with cutout transparency for strands.
*   **`lts_fur_two`**: Likely two-pass fur or specialized layering.
*   **`lts_furonly`**: Renders only the fur fins/shells, not the base surface.

### Tessellation Shaders (`lts_tess*`)
Includes the `Tessellation` hull and domain shaders to smooth geometry.
*   **`lts_tess`**: Standard opaque tessellation.
*   **`lts_tess_cutout`**: Tessellated cutout.
*   **`lts_tess_trans`**: Tessellated transparent.

### Helper & Hidden Shaders
*   **`ltspass_*`**: Internal pass definitions included by other shaders via `UsePass`. not meant to be selected directly.
*   **`ltspass_baker`**: Used for texture baking tools included with lilToon.

## Choosing the Right Variant

| Goal | Recommended Variant |
| :--- | :--- |
| **Character Body/Clothes** | `lts` (Standard) or `lts_cutout` |
| **Glass / Ice** | `lts_trans` or `lts_ref` (if distortion needed) |
| **Double-sided Glass** | `lts_twotrans` |
| **Furry Ears/Tail** | `lts_fur` or `lts_fur_cutout` |
| **Jewelry** | `lts_gem` |
| **Performance** | `ltsl` (Lite versions) |
| **High Quality Closeups** | `lts_tess` (Tessellation) |
