# Base & Main Appearance

## 1. Base Settings
These properties control the fundamental rendering behavior of the shader.

### Properties
*   **_Invisible**: Makes the object invisible.
*   **_AsUnlit**: Mixes the lighting result to appear unlit (0 = lit, 1 = unlit).
*   **_Cutoff**: Alpha cutoff threshold for Cutout rendering.
*   **_Cull**: Culling mode (Off, Front, Back).
*   **_ZWrite**: Depth writing (On, Off).
*   **_ZTest**: Depth testing comparison function.
*   **Blending Modes**: `_SrcBlend`, `_DstBlend`, etc.

### Principles & Logic
*   **Culling (`_Cull`)**: Determines which side of the polygons to draw (Front, Back, or Off/Both).
*   **Z-Test (`_ZTest`)**: Controls how the depth buffer is checked (e.g., LessEqual means draw if closer or equal).
*   **Z-Write (`_ZWrite`)**: Controls whether the object writes to the depth buffer.
*   **Blending**: Standard alpha blending logic: `FinalColor = SrcColor * SrcFactor + DstColor * DstFactor`.

## 2. Main Color & Tone Correction
The main color calculation includes texture sampling, tone correction (HSVG), and gradation mapping.

### Properties
*   **_Color**: Main color tint.
*   **_MainTex**: Primary texture.
*   **_MainTexHSVG**: Hue, Saturation, Value, Gamma adjustment.
*   **_MainGradationStrength**: Strength of the gradation map application.
*   **_MainGradationTex**: Texture used for gradation mapping.

### Implementation Call
The main color logic is encapsulated in the `OVERRIDE_MAIN` macro in `lil_common_frag.hlsl`.

```hlsl
#define OVERRIDE_MAIN \
    LIL_GET_MAIN_TEX \
    LIL_APPLY_MAIN_TONECORRECTION \
    fd.col *= _Color;
```

*   `LIL_GET_MAIN_TEX`: Samples the main texture using `LIL_SAMPLE_2D_POM`.
*   `LIL_APPLY_MAIN_TONECORRECTION`: Applies HSVG and Gradation Map.

### Principles & Math
**Tone Correction (HSVG)**
Allows real-time color adjustment without modifying the texture.
1.  **Gamma**: $RGB = RGB^{Gamma}$
2.  **RGB to HSV**: Convert standard RGB to Hue-Saturation-Value.
3.  **Shift**: $H += Shift_H$, $S *= Shift_S$, $V *= Shift_V$.
4.  **HSV to RGB**: Convert back to RGB.

**Gradation Map**
Replaces the brightness (luminance) of the texture with a color sampled from a gradation texture.
$Color_{new} = lerp(Color_{original}, Sample(GradMap, Color_{original}.r), Strength)$

**Function (`lilToneCorrection` Pseudo-code):**
```hlsl
float3 lilToneCorrection(float3 c, float4 hsvg) {
    c = pow(abs(c), hsvg.w); // Gamma
    // ... RGB to HSV conversion ...
    hsv.x += hsvg.x; // Hue
    hsv.y = saturate(hsv.y * hsvg.y); // Saturation
    hsv.z = saturate(hsv.z * hsvg.z); // Value
    // ... HSV to RGB conversion ...
    return rgb;
}
```

## 3. UV Animation & Calculation
Handles scrolling, rotating, and tiling of UV coordinates.

### Properties
*   **_MainTex_ScrollRotate**: Vector controlling scrolling (XY) and rotation (Z).

### Implementation Call
Usually called via macros like `OVERRIDE_ANIMATE_MAIN_UV`.

### Principles & Math
1.  **Scale & Offset**: $UV_{new} = UV \times Tiling + Offset$
2.  **Scroll**: Add time-based offset.
3.  **Rotation**: Multiply by 2D rotation matrix.

**Function (`lilCalcUV` Pseudo-code):**
```hlsl
float2 lilCalcUV(float2 uv, float4 uv_st, float4 uv_sr) {
    float2 outuv = uv * uv_st.xy + uv_st.zw; // Tiling
    float angle = uv_sr.z + uv_sr.w * Time; // Rotation
    // ... Apply Rotation Matrix ...
    outuv += frac(uv_sr.xy * Time); // Scroll
    return outuv;
}
```

## 4. Main 2nd & 3rd Layers
Additional texture layers that can be blended over the main color.

### Properties
*   **_UseMain2ndTex** / **_UseMain3rdTex**: Toggles.
*   **_Main2ndTex** / **_Main3rdTex**: Textures.
*   **_Main2ndTexBlendMode**: Blending mode (Normal, Add, Multiply, etc.).
*   **_Main2ndTexDecalAnimation**: Support for decal animation (grid-based).

### Implementation Call
Implemented via `OVERRIDE_MAIN2ND` and `OVERRIDE_MAIN3RD`. They use `lilBlendColor` to mix with the base `fd.col`.

### Principles & Math
Blends additional texture layers using standard Photoshop-style blend modes.

**Function (`lilBlendColor` Pseudo-code):**
```hlsl
float3 lilBlendColor(float3 dstCol, float3 srcCol, float srcA, int blendMode) {
    float3 outCol;
    if (blendMode == 0) outCol = srcCol;        // Normal
    else if (blendMode == 1) outCol = dstCol + srcCol; // Add
    else if (blendMode == 2) outCol = max(dstCol + srcCol - dstCol * srcCol, dstCol); // Screen
    else if (blendMode == 3) outCol = dstCol * srcCol; // Multiply
    return lerp(dstCol, outCol, srcA);
}
```

## 5. Alpha Mask
Allows masking parts of the mesh to make them transparent.

### Properties
*   **_AlphaMaskMode**: Mode of operation.
*   **_AlphaMask**: The mask texture.
*   **_AlphaMaskScale**: Scale factor for the mask value.
*   **_AlphaMaskValue**: Offset/Bias.

### Implementation Call
The `OVERRIDE_ALPHAMASK` macro applies the mask to `fd.col.a`.