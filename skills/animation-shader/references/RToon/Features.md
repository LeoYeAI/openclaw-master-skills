# RToon Shader Features

RToon v5 (URP) is a comprehensive Anime/Toon shader suite designed for versatility. It combines traditional cel-shading techniques with advanced features like DOTS support, Triplanar mapping, and specialized stylization options (ShadowT, PTexture).

## 1. Core Shading & Lighting

RToon uses a custom lighting model centered around "Self Shadow" (Stylized Shading) and "ShadowT" (Texture Overlay).

### A. Self Shadow (Main Cel-Shading)
*   **Threshold Control**: Defines the lit/shaded boundary using `_SelfShadowThreshold`.
*   **Hardness**: Controls the softness of the terminator line via `_SelfShadowHardness`.
*   **Vertex Color Control**: The **Green Channel** of vertex colors can be used to locally adjust the Shadow Threshold (e.g., to force shadows on specific areas).
*   **Smooth Normals**: `_SmoothObjectNormal` (controlled by **Red Channel**) allows using smoothed normals for shading calculations to avoid ugly artifacts on low-poly faces, while keeping the original normals for outlines.

### B. ShadowT (Shadow Texture)
A secondary shadow layer often used for stylized effects like Halftones, Hatching, or specific patterns in the shadow area.
*   **Overlay Logic**: Can replace or blend with the standard shadow color.
*   **Ambient Light**: `_ShowInAmbientLightShadowIntensity` allows the pattern to appear even in ambient lighting, useful for "always-on" stylistic textures.
*   **Hardness & Threshold**: Independent control from the main shadow.

### C. MatCap (Material Capture)
*   **Modes**: Supports both additive (Specular-like) and mix modes (`_SPECMODE`).
*   **Ambient Influence**: `_MCIALO` (Main Color In Ambient Light Only) allows MatCap to be visible even without direct light.
*   **Masking**: Dedicated `_MCapMask`.

## 2. Outline (Geometry-Based)

RToon uses the "Inverted Hull" (Back-face Extrusion) method for outlines.

*   **Extrusion Methods**:
    *   **Normal**: Extrudes along vertex normal.
    *   **Origin**: Extrudes from object center (useful for some hard-surface styles).
*   **Distance Scaling**: `_OutlineWidthAffectedByViewDistance` keeps lines consistent or scales them based on camera distance (`_FarDistanceMaxWidth`).
*   **Dynamic Noise**: `_DynamicNoisyOutline` adds animated noise to the outline width, creating a "hand-drawn" or "sketchy" look.
*   **Vertex Color Control**: **Blue Channel** controls outline width per vertex.
*   **Lighting Influence**: `_LightAffectOutlineColor` allows outlines to be tinted by the light color.

## 3. Special Effects & Textures

### A. Gloss (Specular)
*   **Texture-Based Gloss**: `_GlossTexture` can generate stylized highlights.
*   **Rotation Modes**:
    *   **Follow Light**: Highlight moves with the light source.
    *   **Follow Object**: Highlight is "stuck" to the object rotation (like a painted highlight).
    *   **Rotate**: The gloss texture itself can rotate.

### B. Reflection
*   **Faked Reflection (`_FReflection`)**: Uses a texture mapped to the reflection vector instead of sampling the scene's reflection probe. Cheaper and more stylized.
*   **Standard Reflection**: Supports standard PBR reflection probes with roughness control.

### C. Rim Light
*   **Unfill**: `_RimLightUnfill` controls the spread of the rim light (Fresnel power).
*   **In Light**: `_RimLightInLight` determines if rim light appears on the lit side, shadowed side, or both.

### D. PTexture (Pattern Texture)
*   **Screen Space / View Space**: Maps a texture based on view direction/screen position. Useful for static screen-overlays (like a paper texture effect applied to the character).

## 4. Advanced Features

*   **Triplanar Mapping**: `N_F_TP_ON` enables triplanar mapping for MainTex, Shadows, etc., allowing texturing without UVs.
*   **DOTS / ECS Support**: Includes logic (`DOTS_LiBleSki`, `DOTS_CompDef`) for Unity's Data-Oriented Technology Stack, supporting GPU skinning and instancing.
*   **Glow Edge**: `_N_F_COEDGL` adds a glowing emissive rim to Cutout materials (dissolve edge effect).
*   **Near Fade Dithering**: `_N_F_NFD` fades out the object when close to the camera using dithering pattern.

## 5. Vertex Color Usage Summary
*   **Red**: Smooth Object Normal control.
*   **Green**: Self Shadow Threshold control.
*   **Blue**: Outline Width control.
