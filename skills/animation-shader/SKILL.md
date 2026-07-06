---
name: animation-shader
description: READ this skill when implementing or configuring animation-style shaders (Toon/Cel Shaders) — including outlines, rim lighting, toon shading, MatCap, emission, dissolve, hatching, or any stylized rendering effect. Contains preset styles and feature-to-reference mappings for lilToon, Poiyomi, UTS2, RToon, SToon, and ToonShadingCollection. Works as a domain knowledge plugin alongside workflow skills (OpenSpec, SpecKit) or plan mode of an agent.
metadata:
  short-description: Implement and configure Animation-Style Shaders
---

# Animation Shader Skill

Domain knowledge reference for animation-style shaders (Toon Shaders). Contains preset styles, feature lists, and reference mappings for popular shader libraries.

> [!NOTE]
> This skill contains **domain knowledge only**, not a workflow. Pair it with a workflow skill (e.g., OpenSpec, SpecKit) or an agent's plan mode for structured design flow.

## Usage Modes

### With Workflow Skill (Recommended)

When used with a workflow skill (e.g., OpenSpec, SpecKit) or in the plan mode of an agent, this skill serves as a domain knowledge plugin:

- **During requirements/spec phases**: Use the Presents section to identify the target style and map user requests to concrete feature sets
- **During design/planning phases**: Use the Feature List to look up all relevant `references/` documents for each feature
- **Key rule**: For each identified feature, read ALL reference files listed — do not select just one

### Standalone

A lightweight `workflow-standalone.md` is also available as a self-contained design pipeline if needed.

### Knowledge Mode (Query)

When user requests to query knowledge for animation shaders, this skill provides preset styles and feature-to-reference mappings based on the task.

## Presents

Use these presets when the user is unsure about specific features or wants a quick starting point for a specific style.

### 1. Basic Anime
*   **Description**: The standard, clean anime look. Efficient, readable, and widely used.
*   **Features**: Base Color / Main Texture, 3-Tone Shading (Double Shade), Outline (Inverted Hull).
*   **Use Case**: General avatars, NPCs, standard anime characters, performance-critical scenes.

### 2. Advanced Illustration
*   **Description**: A high-quality, detailed look with rich lighting, material definition, and depth.
*   **Features**: Base Color / Main Texture, Layered Textures, 3-Tone Shading (Double Shade), Alpha Mask,Outline (Inverted Hull), Rim Light, MatCap (Material Capture), Specular / HighColor, Shadow Ramp.
*   **Use Case**: Main characters, close-ups, high-fidelity VRChat avatars, cinematic cutscenes.

### 3. Stylized Sketch
*   **Description**: Mimics hand-drawn art, manga, or pencil sketches with a rougher, artistic feel.
*   **Features**: Color Adjustments (Desaturated), Sketchy Outline, Hatching, Halftone Overlay, Sketch / Paper Overlay.
*   **Use Case**: Flashbacks, artistic indie games, unique aesthetic styles, manga adaptations.

### 4. Cyber / VFX
*   **Description**: High-tech, glowing, and dynamic style with motion and reactivity.
*   **Features**: Base Color / Main Texture (Dark), Emission / Glow, AudioLink, Dissolve, Vertex Manipulation (Glitch), Rim Light.
*   **Use Case**: Sci-fi characters, powered-up states, music visualizers, holographic effects.

### 5. Semi-Realistic Toon
*   **Description**: Blends anime aesthetics with realistic material properties for a modern, high-fidelity look.
*   **Features**: PBR (Metallic/Smoothness), Normal Map, Shadow Ramp, Subsurface Scattering (SSS), Outline (Inverted Hull).
*   **Use Case**: Modern action RPGs, high-end cinematic characters, "Genshin-like" but more detailed.

### 6. Retro 90s Anime
*   **Description**: Recreates the look of classic cel animation from the 90s.
*   **Features**: Color Adjustments (High Saturation, Posterization), 3-Tone Shading (Double Shade), Outline (Inverted Hull), Film Grain.
*   **Use Case**: Nostalgic projects, retro-style games, lo-fi aesthetics.

### 7. Oil Painting / Artistic
*   **Description**: Simulates traditional media like oil painting or watercolor.
*   **Features**: Brush Stroke Textures, Distorted UVs, Sketch / Paper Overlay, Smudged Shadows, Sketchy Outline.
*   **Use Case**: Storybook visuals, artistic showcases, dream sequences.

### 8. Flat Pop Art
*   **Description**: A bold, graphic style with minimal shading and vibrant colors.
*   **Features**: Base Color / Main Texture (Unlit), Outline (Inverted Hull), Halftone Overlay, Stencil Patterns.
*   **Use Case**: UI characters, music videos, stylized indie games.

## Feature List

A comprehensive list of features available across the supported shaders, organized by category.

### 1. Core Shading & Coloring
*   **Base Color / Main Texture**: The primary color and texture of the model. (All)
    *   `references/lilToon/Details/01_Base_Main.md`
    *   `references/PoiyomiShaders/Details/01_Base_Main.md`
    *   `references/ToonShadingCollection/Details/03_Diffuse.md`
*   **Color Adjustments**: Adjusts Hue, Saturation, Brightness, or applies Posterization to the final color. (Poiyomi, SToon, lilToon)
    *   `references/lilToon/Details/01_Base_Main.md`
    *   `references/PoiyomiShaders/Details/01_Base_Main.md`
*   **3-Tone Shading (Double Shade)**: Defines shadows using two distinct shades (1st and 2nd) for a traditional anime look. (lilToon, Poiyomi, UTS2)
    *   `references/lilToon/Details/02_Lighting_Shadows.md`
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
    *   `references/UnityChanToonShaderVer2/Details/01_DoubleShade.md`
    *   `references/ToonShadingCollection/Details/09_Lighting_Shadows.md`
*   **Shadow Ramp**: Uses a gradient texture to control the falloff and color of shadows, allowing for soft or stylized transitions. (SToon, Poiyomi, RToon)
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
*   **Shadow Texture (ShadowT)**: Applies a pattern (like hatching or halftone) specifically within the shadowed areas. (RToon, SToon)
    *   `references/RToon/Details/02_ShadowT.md`
*   **Shading Grade Map**: Controls the shadow threshold per-pixel using a grayscale map, allowing for organic shadow shapes. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/02_ShadingGradeMap.md`
*   **Position Maps**: Fixes shadows to specific areas (e.g., under the chin) regardless of lighting direction. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/01_DoubleShade.md`
*   **Ambient Occlusion (AO)**: Adds soft shadows in crevices and corners to increase depth. (Poiyomi, SToon, lilToon)
    *   `references/lilToon/Details/02_Lighting_Shadows.md`
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
*   **Cell Shading / Hard Shading**: Uses hard cutoffs for shadows to create a cel-shaded look. (RToon, SToon)
    *   `references/RToon/Details/01_Core_Shading.md`
    *   `references/SToon/Details/01_Core_Shading.md`
*   **Diffuse Warp**: Distorts the shading terminator for irregular, hand-drawn shadow edges. (SToon)
    *   `references/SToon/Details/05_Artistic_Controls.md`
*   **Normal Map**: Adds surface detail and depth without changing geometry. (All)
    *   `references/PoiyomiShaders/Details/01_Base_Main.md`
*   **Detail Maps**: Adds high-frequency surface details using secondary textures. (Poiyomi, lilToon)
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
*   **Layered Textures**: Allows stacking multiple texture layers with blending modes for complex surface details. (lilToon, Poiyomi)
    *   `references/lilToon/Details/01_Base_Main.md`
*   **Decals**: Applies sticker-like textures on top of the main surface with independent transforms. (Poiyomi, lilToon)
    *   `references/lilToon/Details/01_Base_Main.md`
*   **Alpha Mask**: Controls transparency or restricts features to specific areas using a mask texture. (lilToon, Poiyomi)
    *   `references/lilToon/Details/01_Base_Main.md`
*   **RGB Masking**: Re-colors specific parts of the mesh using RGBA masks. (Poiyomi)
    *   `references/PoiyomiShaders/Details/01_Base_Main.md`
*   **Triplanar Mapping**: Applies textures based on world space, useful for models without proper UVs. (RToon, SToon)
    *   `references/RToon/Details/06_Advanced_Features.md`

### 2. Surface & Reflections
*   **Specular / HighColor**: Adds stylized highlights to the surface, often with masking or cartoon shapes. (All)
    *   `references/lilToon/Details/03_Surface_Reflections.md`
    *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
    *   `references/ToonShadingCollection/Details/04_Specular.md`
    *   `references/SToon/Details/04_Specular_Rim.md`
    *   `references/RToon/Details/05_Gloss_Rim.md`
*   **MatCap (Material Capture)**: Simulates complex lighting and reflections (like metal or hair sheen) using a sphere texture. (All)
    *   `references/RToon/Details/04_MatCap_Reflection.md`
    *   `references/lilToon/Details/03_Surface_Reflections.md`
    *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Camera Rolling Stabilizer**: Keeps MatCap reflections upright even when the camera tilts. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Rim Light**: Adds a highlight to the edges of the model based on the viewing angle (Fresnel effect). (All)
    *   `references/RToon/Details/05_Gloss_Rim.md`
    *   `references/SToon/Details/04_Specular_Rim.md`
    *   `references/lilToon/Details/03_Surface_Reflections.md`
    *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
*   **Backlight**: Simulates light coming from behind the object, enhancing the silhouette or adding a rim on the shadowed side. (lilToon, SToon, UTS2)
    *   `references/lilToon/Details/02_Lighting_Shadows.md`
    *   `references/SToon/Details/04_Specular_Rim.md`
*   **Shadow Rim / Antipodean Rim**: Adds a rim light specifically to the shadowed side of the object. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Side Shine**: Adds a specific highlight on the side of the object to increase volume. (SToon)
    *   `references/SToon/Details/04_Specular_Rim.md`
*   **Anisotropy**: Specialized highlights for hair or brushed metal surfaces. (lilToon, Poiyomi, SToon)
    *   `references/lilToon/Details/03_Surface_Reflections.md`
    *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
    *   `references/ToonShadingCollection/Details/04_Specular.md`
*   **Clear Coat**: Adds an extra glossy layer on top of the material for a varnished look. (Poiyomi)
    *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
*   **Faked Reflection**: Uses a static texture for reflections instead of a probe for stylized control. (RToon)
    *   `references/RToon/Details/04_MatCap_Reflection.md`
*   **Environment / Reflections**: Configures environment reflections using Cubemaps or Reflection Probes. (All)
    *   `references/ToonShadingCollection/Details/05_Environment.md`
*   **Iridescence / Color Shift**: Changes color based on viewing angle or time. (UTS2, Poiyomi)
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Subsurface Scattering (SSS)**: Simulates light penetrating translucent surfaces like skin. (Poiyomi)
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`

### 3. Outline & Edge Detection
*   **Outline (Inverted Hull)**: Creates outlines by extruding back-facing vertices; widely used for character outlines. (All)
    *   `references/lilToon/Details/08_Outline.md`
    *   `references/PoiyomiShaders/Details/05_Outline.md`
    *   `references/RToon/Details/03_Outline.md`
    *   `references/UnityChanToonShaderVer2/Details/03_Outline.md`
    *   `references/ToonShadingCollection/Details/02_Outline.md`
*   **Stylized Outline**: Noise, Sketchy, Hand-drawn look.
    *   `references/SToon/Details/02_Outline.md`
    *   `references/RToon/Details/03_Outline.md`
*   **Baked Normal Outline**: Uses a smooth normal map for outlines to prevent breaks on hard edges. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/03_Outline.md`

### 4. Special Effects & VFX
*   **Emission / Glow**: Makes specific parts of the model glow, often with animation support. (lilToon, Poiyomi, UTS2)
    *   `references/lilToon/Details/04_Special_Effects.md`
    *   `references/PoiyomiShaders/Details/04_Special_Effects.md`
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Dissolve**: Gradually makes the model transparent using a noise pattern, often with a glowing edge. (lilToon, Poiyomi)
    *   `references/PoiyomiShaders/Details/04_Special_Effects.md`
    *   `references/lilToon/Details/04_Special_Effects.md`
*   **Halftone Overlay**: Applies a comic-book style dot pattern over the model. (SToon)
    *   `references/SToon/Details/03_Overlays.md`
    *   `references/ToonShadingCollection/Details/08_PostProcessing.md`
*   **Hatching**: Uses line patterns for shading instead of solid colors, often with multiple layers. (SToon, RToon)
    *   `references/SToon/Details/03_Overlays.md`
*   **Sketch / Paper Overlay**: Applies paper textures or sketch lines for a hand-drawn look. (SToon)
    *   `references/SToon/Details/03_Overlays.md`
*   **Glitter**: Adds procedural sparkling effects to the surface. (lilToon)
    *   `references/lilToon/Details/04_Special_Effects.md`
*   **AudioLink**: Reacts to music/audio for dynamic effects like pulsing emission, color shifts, or vertex glitching. (lilToon, Poiyomi)
    *   `references/lilToon/Details/05_Advanced.md`
    *   `references/PoiyomiShaders/Details/04_Special_Effects.md`
*   **Parallax Occlusion**: Simulates depth in textures by offsetting UVs based on view angle. (lilToon)
    *   `references/lilToon/Details/04_Special_Effects.md`
*   **Vertex Manipulation**: Deforms the mesh geometry (e.g., glitching, rounding, scaling). (Poiyomi, SToon)
    *   `references/PoiyomiShaders/Details/01_Base_Main.md`
*   **Animation & Motion**: Techniques for UV animation, vertex animation, and smear frames. (ToonShadingCollection)
    *   `references/ToonShadingCollection/Details/10_Animation_VFX.md`
*   **Refraction / Gem**: Simulates light bending through transparent materials like gems or eyes. (lilToon)
    *   `references/lilToon/Details/07_Variant_Features.md`
*   **UV Animation**: Scrolls or rotates textures for effects like flowing water or tech interfaces. (SToon, lilToon, UTS2)
    *   `references/lilToon/Details/01_Base_Main.md`
    *   `references/SToon/Details/05_Artistic_Controls.md`

### 5. Advanced & Pipeline
*   **Culling / Stencil / Clipping**: Controls face culling and stencil buffer operations for advanced rendering effects. (lilToon, UTS2)
    *   `references/lilToon/Details/05_Advanced.md`
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Stencil Masking**: Uses the stencil buffer for effects like "eyebrows visible through hair". (lilToon, UTS2)
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Back Face Rendering**: Dedicated settings for rendering the back side of polygons. (Poiyomi)
    *   `references/lilToon/Details/01_Base_Main.md`
*   **Distance Fade / Near Fade**: Fades the object or outline based on camera distance to prevent view blocking. (lilToon, RToon, UTS2)
    *   `references/RToon/Details/06_Advanced_Features.md`
*   **Tessellation**: Dynamically subdivides geometry for smoother curves. (lilToon)
    *   `references/lilToon/Details/07_Variant_Features.md`
*   **Variants & Optimization**: Guidelines for using shader variants (Lite, Multi) and optimizing models. (lilToon, ToonShadingCollection)
    *   `references/lilToon/Details/06_Variants.md`
    *   `references/ToonShadingCollection/Details/11_Modeling_Pipeline.md`
*   **Art Styles & Theory**: Analysis of different art styles and PBR stylization techniques. (ToonShadingCollection)
    *   `references/ToonShadingCollection/Details/01_ArtStyles.md`
    *   `references/ToonShadingCollection/Details/06_PBR_Stylization.md`

### 6. Special Objects (Material Specific)
*   **Hair (Angel Ring)**: Creates a fixed highlight halo on hair. (UTS2)
    *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
    *   `references/ToonShadingCollection/Details/04_Specular.md`
*   **Eyes**: Specialized rendering for eyes including parallax, refraction, and stencil masking. (lilToon, UTS2)
    *   `references/lilToon/Details/07_Variant_Features.md`
    *   `references/ToonShadingCollection/Details/07_Stylized_Features.md`
*   **Skin**: Simulates subsurface scattering and soft shading for skin. (Poiyomi, UTS2)
    *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
    *   `references/ToonShadingCollection/Details/07_Stylized_Features.md`
*   **Fur**: Simulates fur using multi-layer rendering. (lilToon)
    *   `references/lilToon/Details/07_Variant_Features.md`

## Details Features Document

*   `references/lilToon/Features.md`
*   `references/PoiyomiShaders/Features.md`
*   `references/SToon/Features.md`
*   `references/RToon/Features.md`
*   `references/UnityChanToonShaderVer2/Features.md`
*   `references/ToonShadingCollection/Features.md`
