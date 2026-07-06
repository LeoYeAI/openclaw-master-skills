# Poiyomi Toon Shader Features

**Version:** 8.1.167 (as seen in shader file)
**License:** MIT (Check `ThirdPartyLicenses` folder for specifics)

Poiyomi Toon Shader is a highly feature-rich shader designed for VRChat avatars, known for its extensive configurability and "monolithic" single-file structure for stability.

## 1. Base & Appearance
*   **Main Color**: Texture, Color, Normal Map, Alpha Cutoff.
*   **Color Adjust**: Hue Shift (Standard & AudioLink), Saturation, Brightness.
*   **Back Face**: Dedicated settings for backface rendering (Color, Emission, Texture).
*   **Details**: Secondary textures and normals for high-frequency details.
*   **RGB Masking**: Re-color parts of the mesh using RGBA masks.

## 2. Geometry & Vertex Options
*   **Vertex Manipulation**: Local/World translation, rotation, and scaling.
*   **Rounding**: Quantize vertex positions for retro effects.
*   **Glitching**: Vertex-based glitch effects with noise and AudioLink integration.
*   **Decals**: Up to 4 layers of decals with independent transform and blending.

## 3. Lighting & Shadows
*   **Shading Models**: Toon, Realistic, Skin, Cloth, etc.
*   **Shadows**: Multilayer math-based shadows, Ramp textures, Shadow Strength.
*   **AO**: Ambient Occlusion maps and strength control.
*   **Subsurface Scattering (SSS)**: Simulated light scattering through skin/thin objects.
*   **Rim Lighting**: Two independent Rim Light layers plus Depth Rim.

## 4. Reflections & Specular
*   **Metallic/Smoothness**: PBR-based reflection workflow.
*   **MatCap**: Up to 4 MatCap layers with various blending modes and masking.
*   **CubeMap**: Environment reflections.
*   **Anisotropy**: Hair-like highlights.
*   **Clear Coat**: Additional glossy layer on top.

## 5. Special Effects
*   **Dissolve**: Alpha transparency effects.
*   **AudioLink**: Deep integration for music-reactive effects on almost every property (Hue, Vertex, Decals, etc.).
*   **Outline**: (In `Poiyomi Outline.shader`) Inverted hull outline with width masking and distance scaling.

---

Detailed implementation notes can be found in the `Details` directory.
