# UnityChan Toon Shader Ver 2 (UTS2) - Universal Render Pipeline

**UnityChan Toon Shader Ver 2 (UTS2)** is a highly versatile uber shader designed for anime-style characters in the Universal Render Pipeline (URP). It excels in creating controllable, high-quality cel-shaded looks with support for standard URP lighting features while allowing for non-photorealistic artistic control.

## Core Architecture
*   **Uber Shader**: All features are integrated into a single shader (`Universal Render Pipeline/Toon`). You switch between workflows and enable features via the Inspector, rather than swapping shader files.
*   **Legacy Compatibility**: Material property names match the legacy pipeline version, allowing for easy migration of values.
*   **Real-time Adjustment**: Almost all features, including shadow thresholds and feathering, can be tweaked in real-time.

## 1. Shading Workflows
UTS2 offers two primary workflows for calculating shadows.

### A. Double Shade with Feather
The standard mode simulating anime production steps: **Base Color** -> **1st Shade** -> **2nd Shade**.
*   **Position Maps**: Two separate textures (`_Set_1st_ShadePosition`, `_Set_2nd_ShadePosition`) allow you to "fix" shadows to specific parts of the mesh (e.g., under the nose or chin) regardless of lighting.
*   **Feathering**: Adjustable softness (`_BaseShade_Feather`, `_1st2nd_Shades_Feather`) allows transition from hard cel-edges to soft gradient shading.

### B. Shading Grade Map
An advanced mode for more organic control.
*   **Concept**: Uses a single grayscale map (`_ShadingGradeMap`) to define the "shading threshold" per pixel.
    *   **Black (0.0)**: Shadows form easily (creases, deep areas).
    *   **White (1.0)**: Shadows form with difficulty (highlights, tips).
*   **Result**: Shadows flow continuously based on the map's gradient, allowing for complex shapes that still react to light direction.

## 2. Basic Color & Texture Setup
*   **Three Step Color**: Defines `BaseMap`, `1st_ShadeMap`, and `2nd_ShadeMap`. Textures can be shared (e.g., BaseMap used for 1st Shade) to simplify setup.
*   **Normal Map**:
    *   Used for **shading gradation**, not just surface bumps.
    *   Can be selectively applied to HighColor, RimLight, or the Base colors (`_Is_NormalMapToBase`).

## 3. Advanced Feature Modules

### Outline (Inverted Hull)
*   **Method**: Renders the mesh inside-out, slightly larger.
*   **Distance Scaling**: `_Farthest_Distance` / `_Nearest_Distance` scaling prevents clutter at a distance.
*   **Baked Normal Support**: `_BakedNormal` allows hard-edged meshes (split vertices) to have smooth, continuous outlines by reading a smooth normal map.
*   **Blending**: `_Is_BlendBaseColor` blends the outline color with the texture color for softer looks.
*   **Z-Offset**: `_Offset_Z` pushes the outline back to prevent Z-fighting.

### HighColor (Specular)
*   **Customization**: Supports textures for complex highlights.
*   **Specular Mode**: Can render as realistic gloss (`_Is_SpecularToHighColor`) or stylized vector circles.
*   **Masking**: `_Set_HighColorMask` allows masking highlights on specific areas (like skin).

### RimLight
*   **Directional**: Standard rim lighting based on view angle.
*   **Antipodean (Ap) RimLight**: Adds rim lighting to the **shadowed side** (opposite to light source), useful for backlighting effects.
*   **LightDirection Mask**: Can restrict rim lights to only appear in the direction of the main light.

### MatCap (Material Capture)
*   **Camera Rolling Stabilizer**: A unique feature (`_CameraRolling_Stabilizer`) that counter-rotates the MatCap UVs when the camera tilts, keeping reflections upright (horizon-stable).
*   **Normal Map**: Dedicated `_NormalMapForMatCap` allows adding surface detail (like brushed metal) specifically to the reflection without affecting the base shading.
*   **Masking**: `_Set_MatcapMask` controls where the MatCap is applied.

### Angel Ring
*   **Purpose**: Fixed "halo" highlights on hair that slide horizontally but stay vertically fixed relative to the camera.
*   **Requirement**: Uses **UV2** coordinates (projected orthographically from the front) to map the highlight texture.

### Emissive (Self-Illumination)
*   **Animation**: Supports `Scroll`, `Rotate`, and `PingPong` (blinking) animations.
*   **Color Shift**: Can shift colors over time or based on **View Angle** (iridescence).
*   **Masking**: Alpha channel of the Emissive texture acts as a mask.

## 4. System Integration & Lighting

### Environmental Lighting
*   **GI Intensity**: Controls how much Light Probe/Ambient data affects the material (`_GI_Intensity`).
*   **Unlit Intensity**: Boosts ambient blending when no directional light is present (`_Unlit_Intensity`).
*   **SceneLights Hi-Cut Filter**: Intelligent filter to prevent overexposure when multiple bright lights or intense Bloom are present (`_Is_Filter_LightColor`).

### Light Color Contribution
*   **Fine Control**: Individual toggles (`_Is_LightColor_Base`, `_Is_LightColor_1st_Shade`, etc.) to determine if specific layers react to the *color* of real-time lights or strictly use their set colors.

### System Shadows
*   **Receive Shadows**: Full support for receiving shadows from other objects (`_Set_SystemShadowsToBase`).
*   **Raytraced Hard Shadows**: Support for RTHS if the environment supports DXR.

## 5. Utility Features
*   **Clipping / Stencil**:
    *   **Clipping**: Alpha cutout support (`_ClippingMask`), including "TransClipping" (alpha-weighted clipping).
    *   **Stencil**: Standard Stencil Buffer support (`StencilMask` / `StencilOut`) for effects like "eyebrows visible through hair".
*   **Culling Options**: Configurable `Culling Mode` (Off, Front, Back).