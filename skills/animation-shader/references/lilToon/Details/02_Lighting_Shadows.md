# Lighting & Shadows

## 1. Shadows & Toon Shading
lilToon employs a sophisticated 3-layer shadow system blended with a "Toon Stepping" function to create stylized shading.

### Properties
*   **_UseShadow**: Enable shadows.
*   **_ShadowStrength**: Overall shadow strength.
*   **_ShadowColor**, **_Shadow2ndColor**, **_Shadow3rdColor**: Colors for the shadow layers.
*   **_ShadowBorder**, **_ShadowBlur**: Control the edge sharpness and position of the shadow.
*   **_ShadowReceive**: Influence of received shadows (cast by other objects).
*   Masks: `_ShadowBorderMask`, `_ShadowBlurMask`, `_ShadowStrengthMask`.

### Implementation Call
The shadow logic is in `lilGetShading` (lil_common_frag.hlsl), called via `OVERRIDE_SHADOW`.

```hlsl
#define OVERRIDE_SHADOW \
    lilGetShading(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math

**Toon Stepping Function (`lilTooningScale`)**
Maps the input value (NdotL) through a step function controlled by a `Border` and `Blur` parameter.
$Value' = \frac{Value - (Border - Blur/2)}{Blur}$

```hlsl
float lilTooningScale(float aascale, float value, float border, float blur) {
    float borderMin = saturate(border - blur * 0.5);
    float borderMax = saturate(border + blur * 0.5);
    return saturate((value - borderMin) / (borderMax - borderMin));
}
```

**Shadow Logic (`lilGetShading` Pseudo-Code)**
1.  **Calculate NdotL**:
    ```hlsl
    // Can blend normal map with geometric normal per layer
    float3 N1 = lerp(fd.origN, fd.N, _ShadowNormalStrength);
    float NdotL = dot(LightDir, N1) * 0.5 + 0.5;
    ```
2.  **Apply Received Shadows**:
    ```hlsl
    float shadowAtten = saturate(LightAttenuation + distance(LightDir, OriginalLightDir));
    NdotL *= lerp(1.0, shadowAtten, _ShadowReceive);
    ```
3.  **Apply AO/Border Mask**:
    ```hlsl
    float mask = Sample(ShadowBorderMask);
    mask = mask * Shift + Offset;
    NdotL *= mask; 
    ```
4.  **Apply Toon Step**:
    ```hlsl
    float shadowMix = lilTooningScale(1.0, NdotL, _ShadowBorder, _ShadowBlur);
    ```
5.  **Final Color Blend**:
    ```hlsl
    FinalColor = lerp(ShadowColor, BaseColor, shadowMix);
    ```

## 2. Backlight
Simulates light coming from behind the object, creating a rim-like effect or subsurface scattering approximation.

### Properties
*   **_BacklightColor**: Color of the backlight.
*   **_BacklightMainStrength**: How much it blends with the main color.
*   **_BacklightDirectivity**: Focus of the light.
*   **_BacklightViewStrength**: Influence of view direction.
*   **_BacklightBorder**, **_BacklightBlur**: Toon stepping parameters.

### Implementation Call
Implemented in `lilBacklight` (lil_common_frag.hlsl), called via `OVERRIDE_BACKLIGHT`.

```hlsl
#define OVERRIDE_BACKLIGHT lilBacklight(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math
It combines the "Half Vector" (or view alignment) with the light alignment.

**Formula:**
1.  **Directivity Factor**: $Factor = saturate(-HalfVector \cdot Normal)^{Directivity}$
2.  **View & Light Alignment**: $LightNormal = dot(normalize(-ViewDir \cdot ViewStrength + LightDir), Normal)$

**Function (`lilBacklight` Pseudo-Code):**
```hlsl
void lilBacklight(...) {
    // 1. Calculate Backlight Intensity
    // fd.hl is the Half Vector (bisector of View and Light)
    float backlightFactor = pow(saturate(-dot(HalfVector, Normal) * 0.5 + 0.5), _BacklightDirectivity);
    
    // 2. Adjust based on View Strength
    float3 virtualLightDir = normalize(-ViewDir * _BacklightViewStrength + LightDir);
    float backlightLN = dot(virtualLightDir, Normal) * 0.5 + 0.5;
    
    // 3. Toon Step (Sharpen the effect)
    backlightLN = lilTooningScale(1.0, backlightLN, _BacklightBorder, _BacklightBlur);
    
    float finalBacklight = saturate(backlightFactor * backlightLN);

    // 4. Add to Color
    float3 resultColor = lerp(_BacklightColor, _BacklightColor * Albedo, _BacklightMainStrength);
    FinalColor += finalBacklight * resultColor * LightColor;
}
```
