# Surface & Reflections

Poiyomi Shader offers a layered approach to surface properties, allowing mixing of stylized (MatCap, Toon Rim) and realistic (PBR, Cubemap) effects.

## 1. Reflections & Specular
The shader supports a standard PBR workflow as well as stylized specular.

### PBR (Mochie BRDF)
*   **Properties**:
    *   **`_MochieMetallicMultiplier`**: Global metallic value.
    *   **`_MochieRoughnessMultiplier`**: Global smoothness/roughness.
    *   **`_MochieMetallicMaps`**: Packed map (Metallic, Roughness, Occlusion).
*   **Implementation**: Calculates standard Unity PBR or a modified BRDF.
*   **GSAA (`_MochieGSAAEnabled`)**: Geometric Specular Aliasing Approximation. Reduces shimmering on high-frequency normal maps by adjusting roughness based on screen-space derivatives.

### Stylized Specular
*   **Multi-Layer**: Support for primary and secondary specular highlights.
*   **Masking**: High granular control over where highlights appear.
*   **Toon Ramp**: Specular falloff can be controlled via a ramp for hard-edged anime highlights.

## 2. MatCap (Material Capture)
Poiyomi allows up to **4 MatCap layers** (0-3).

### Properties
*   **`_Matcap`**: The MatCap texture (sphere map).
*   **`_MatcapColor`**: Tint color.
*   **`_MatcapBorder`**: Controls the edge falloff/size of the MatCap.
*   **`_MatcapBlendMode`**: Selects the blending equation (0=Add, 1=Replace, etc.).
*   **`_MatcapMask`**: Texture to mask the effect.

### Implementation
**Call Site**: `applyMatcap` function (called in `frag` approx line 12417).

**Logic (Pseudo-code):**
```hlsl
// 1. Calculate MatCap UVs based on View-Space Normals
float3 worldViewUp = normalize(float3(0, 1, 0) - viewDir * dot(viewDir, float3(0, 1, 0)));
float3 worldViewRight = normalize(cross(viewDir, worldViewUp));
float2 matcapUV = float2(dot(worldViewRight, normal), dot(worldViewUp, normal)) * _MatcapBorder + 0.5;

// 2. Sample Texture
float4 matcapColor = tex2D(_Matcap, matcapUV) * _MatcapColor;

// 3. Apply Masking
matcapColor *= tex2D(_MatcapMask, uv);

// 4. Blending (Simplified)
switch(_MatcapBlendMode) {
    case REPLACE:  baseColor = lerp(baseColor, matcapColor, mask); break;
    case ADD:      baseColor += matcapColor * mask; break;
    case MULTIPLY: baseColor *= matcapColor * mask; break;
    case SCREEN:   baseColor = 1 - (1 - baseColor) * (1 - matcapColor * mask); break;
}
```

## 3. Rim Lighting
Three distinct Rim Lighting styles are supported:

### 1. Poiyomi Style (`_RIMSTYLE_POIYOMI`)
Standard rim light based on NdotV.
*   **Properties**: `_RimWidth`, `_RimSharpness`, `_RimPower`, `_RimLightColor`.
*   **Logic**:
    ```hlsl
    // Fresnel-like calculation
    float rim = 1.0 - saturate(dot(viewDir, normal));
    // Sharpening
    rim = smoothstep(_RimWidth, _RimWidth + _RimSharpness, rim);
    rim = pow(rim, _RimPower);
    ```

### 2. UTS2 Style (`_RIMSTYLE_UTS2`)
Emulates Unity-Chan Toon Shader. Blends rim light based on light direction (Antipodean Rim).
*   **Feature**: `_Add_Antipodean_RimLight` adds a second rim opposite to the light.

### 3. lilToon Style (`_RIMSTYLE_LILTOON`)
Emulates lilToon rim lighting.
*   **Backface Mask**: `_RimBackfaceMask` prevents rim light on backfaces.
*   **Indirection**: Includes logic for indirect light contribution.

**Depth Rim**: A special rim light calculated based on scene depth, useful for highlighting edges intersecting with other geometry (e.g., force fields).

## 4. CubeMap
Environment reflections using a Unity CubeMap.
*   **Properties**: `_CubeMap`, `_CubeMapIntensity`, `_CubeMapRotation`.
*   **Logic**: Samples the CubeMap using the reflection vector (`reflect(-viewDir, normal)`).

## 5. Anisotropy
Simulates hair-like highlights.
*   **Properties**: `_AnisoColorMap`, `_Aniso0Strength`, `_Aniso0Offset`.
*   **Tangent Space**: Uses `dot(tangent, halfDir)` instead of `dot(normal, halfDir)` for highlight calculation.
*   **Bi-Directional**: Can have highlights in two directions (e.g., hair strand sheen).
