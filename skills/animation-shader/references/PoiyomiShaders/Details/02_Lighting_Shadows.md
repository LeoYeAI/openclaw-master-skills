# Lighting & Shadows

Poiyomi Shader uses a custom lighting pipeline that supports multiple lighting models (Standard, Toon, UTS2) and extensive configuration.

## 1. Light Data Pipeline
The shader calculates light data in the fragment shader before applying shading.

### Call Site
`Assets/_PoiyomiShaders/Shaders/8.1/Toon/Poiyomi.shader` (approx line 15941 in `frag`, actual calculation in `calculateShading` or inline).

### Lighting Modes (`_LightingColorMode`)
*   **0: Poi Custom**: Calculates Direct/Indirect color using Spherical Harmonics (SH) with luminance balancing to prevent overexposure while maintaining rich ambient light.
*   **1: Standard**: Uses Unity's standard `_LightColor0` and SH.
*   **2: UTS2**: Unity-Chan Toon Shader style (Max of SH and LightColor).
*   **3: OpenLit**: Matches OpenLit/lilToon lighting response.

### Light Direction (`_LightingDirectionMode`)
*   **0: Standard**: Uses `_WorldSpaceLightPos0`.
*   **1/2: Forced**: Uses a custom vector (`_LightngForcedDirection`) in Local or World space. Useful for stylized scenes or UI characters.
*   **3: UTS2**: Interpolates between Camera Up and Light Direction.

## 2. Shadow Calculation
Poiyomi calculates a "Light Map" value (0 to 1) representing how lit a pixel is.

### Properties
*   **`_ShadowStrength`**: Global multiplier for shadow intensity.
*   **`_LightingMapMode`**: How NdotL is treated (Normalized vs Saturated).
*   **`_LightingMinLightBrightness`**: Minimum brightness floor.

### Principles & Math (Pseudo-code)
The "Poi Custom" mode uses a unique algorithm to balance direct light and spherical harmonics.

```hlsl
// Calculate NdotL (Normal dot Light Direction)
float nDotL = dot(normal, lightDir);

// Attenuation (Shadows from other objects/Point light falloff)
float attenuation = UNITY_LIGHT_ATTENUATION(i, worldPos);

// Calculate Base LightMap
if (_LightingMapMode == 0) { // Poi Custom
    // 1. Get Spherical Harmonics (Ambient Light)
    float3 magic = BetterSH9(normalize(unity_SHAr + ...));
    float3 normalLight = _LightColor0.rgb + BetterSH9(0,0,0);
    
    // 2. Luminance Balancing
    // Ensures the light doesn't become too bright or washed out
    float magiLumi = calculateLuminance(magic);
    float normaLumi = calculateLuminance(normalLight);
    float target = calculateLuminance(magic * ratio + normalLight * ratio);
    
    // 3. Compute Direct/Indirect Color
    poiLight.directColor = properLightColor * (target / properLuminance);
    
    // 4. Ramp Calculation
    // Calculates a smooth ramp based on the difference between direct and indirect light
    float bw_direct = ((nDotL * 0.5 + 0.5) * lightColor * attenuation);
    float lightDifference = (topIndirect + lightColor) - bottomIndirect;
    
    // Final Light Map (0-1 value)
    lightMap = smoothstep(0, lightDifference, bw_direct - bottomIndirect);
} 
else if (_LightingMapMode == 1) { // Normalized
    // Maps NdotL from [-1, 1] to [0, 1]
    lightMap = (nDotL * 0.5 + 0.5) * attenuation;
}
else { // Saturated
    // Clamps negative NdotL to 0
    lightMap = saturate(nDotL) * attenuation;
}

// Apply Detail Shadows & AO
// _LightDataAOStrengthR controls blending
lightMap *= lerp(1, detailShadow, _LightingDetailShadowStrengthR);
lightMap *= lerp(1, occlusion, _LightDataAOStrengthR);
```

## 3. Shading Models
Once the `lightMap` is calculated, it's used to blend between Lit and Shadow colors.

### Multilayer Math (`_LightingMode == 1`)
Defines shadows using math gradients rather than a texture ramp.
*   **Layers**: Up to 3 shadow layers (Primary, Secondary, Tertiary).
*   **Properties**:
    *   `_ShadowBorder`: Position of the shadow edge (0-1).
    *   `_ShadowBlur`: Softness of the edge.
    *   `_ShadowColor`: Color of the shadow.
*   **Logic**:
    ```hlsl
    // Smoothstep creates a soft transition based on Border and Blur
    float shadow1 = smoothstep(_ShadowBorder - _ShadowBlur, _ShadowBorder + _ShadowBlur, lightMap);
    
    // Blend final color
    finalColor = lerp(_ShadowColor, LitColor, shadow1);
    ```

### Texture Ramp (`_LightingMode == 0`)
Uses a 1D gradient texture sampled by `lightMap`.
*   **`_ToonRamp`**: The gradient texture.
*   **`_ShadowOffset`**: Offsets the lookup value (animatable).
*   **Logic**:
    ```hlsl
    // Sample texture using lightMap as the U coordinate
    float4 rampColor = tex2D(_ToonRamp, float2(lightMap + _ShadowOffset, 0.5));
    finalColor *= rampColor;
    ```

## 4. Additional Features
*   **AO Maps (`_LightingAOMaps`)**: Separate Ambient Occlusion texture with RGBA channel support.
*   **Shadow Masks (`_LightingShadowMasks`)**: Texture to force areas to be permanently in shadow or lit (useful for fixing ugly face shadows).
*   **Subsurface Scattering (SSS)**: Simulated by blurring the lighting or using thickness maps to allow light through thin areas.
    *   **`_SSSThicknessMap`**: Defines thin areas (ears, fingers).
    *   **`_SSSColor`**: Color of the light passing through.
