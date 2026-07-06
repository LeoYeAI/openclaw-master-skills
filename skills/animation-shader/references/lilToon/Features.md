# lilToon Shader Features

**Version:** 1.7.3  
**License:** MIT License

lilToon is a comprehensive shader developed for avatar services like VRChat, designed to be easy to use, beautiful (preventing overexposure, anti-aliased shading), and lightweight. It supports various Unity versions (2018-2023) and render pipelines (BRP, LWRP, URP, HDRP).

## 1. Base & Main Appearance
*   **Base Settings**: Culling, Z-Write, Z-Test, Stencil, Blending modes.
*   **Main Color**: Primary texture and color, HSV adjustment, Gradation Map.
*   **Layered Textures**: Main 2nd and 3rd layers with various blending modes, decal support, and animation.
*   **Alpha Mask**: Masking for transparency.
*   See `Details/01_Base_Main.md`

## 2. Lighting & Shadows
*   **Shadows**: 3-layer shadow system, Border control, Blur, Receive Shadow, Shadow Colors (1st, 2nd, 3rd).
*   **Backlight**: Simulates light coming from behind the object.
*   **Lighting Settings**: Min/Max brightness limits, Monochrome lighting.
*   See `Details/02_Lighting_Shadows.md`

## 3. Surface & Reflections
*   **Normal Map**: Primary and secondary normal maps.
*   **Anisotropy**: Anisotropic highlights (e.g., for hair).
*   **Reflection**: Smoothness, Metallic, Reflectance, Specular highlights, Environment reflections, MatCap (Sphere mapping).
*   **Rim Shade**: Darkening at the edges (ambient occlusion effect).
*   **Rim Light**: Highlighting at the edges.
*   See `Details/03_Surface_Reflections.md`

## 4. Special Effects
*   **Glitter**: Sparkling effect with shape and animation control.
*   **Emission**: Glowing parts with blinking, gradation, and scrolling.
*   **Parallax**: Parallax Occlusion Mapping (POM) for depth simulation.
*   **Distance Fade**: Fading effects based on camera distance.
*   **Dissolve**: Dissolve effect with noise mask and edge color.
*   See `Details/04_Special_Effects.md`

## 5. Advanced Features
*   **AudioLink**: Integration with AudioLink for music-reactive effects.
*   **ID Mask**: Masking parts of the mesh based on UVs or Vertex IDs.
*   **UDIM Discard**: Discarding fragments based on UDIM tiles.
*   **Encryption**: Texture encryption support.
*   See `Details/05_Advanced.md`

## 6. Outline
*   **Inverted Hull**: Vertex displacement logic for high-quality anime outlines.
*   **Masking**: Width control via textures or vertex colors.
*   **Z-Bias & Fix Width**: Techniques to prevent clipping and maintain screen-space size.
*   See `Details/08_Outline.md`

## 7. Shader Variants & Specialized Features
lilToon comes with multiple shader files optimized for specific use cases.
*   **Editions**: Standard (`lts`), Lite (`ltsl`), Multi (`ltsmulti`).
*   **Rendering Modes**: Cutout, Transparent, Two-Pass Transparent.
*   **Specialized Types**: Fur, Gem, Tessellation, Refraction.

See `Details/06_Variants.md` for file naming conventions.
See `Details/07_Variant_Features.md` for technical details on **Fur, Tessellation, Refraction, and Gem**.

## 8. Usage & Setup
*   **Supported Unity Versions**: 2018.1 - 2023.2.
*   **Render Pipelines**: Built-in, LWRP (4.0 - 6.9), URP (7.0 - 16.0), HDRP (4.0 - 16.0).
*   **Setup**: Select `lilToon` from the Shader dropdown in the Inspector.
*   **Transparency**: Change `Rendering Mode` to `Cutout` or `Transparent` in the material inspector if needed.

---

Detailed implementation notes can be found in the `Details` directory.
