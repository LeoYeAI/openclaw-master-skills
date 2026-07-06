# Surface & Reflections

## 1. Reflection (Specular & Environment)
lilToon combines traditional PBR-like specular highlights with environment mapping.

### Properties
*   **_Smoothness**: Surface smoothness (inverse of roughness).
*   **_Metallic**: Metalness workflow.
*   **_Reflectance**: Specular reflectance for dielectrics.
*   **_ApplySpecular**: Enable specular highlights from lights.
*   **_ApplyReflection**: Enable environment map reflections.
*   **_ReflectionColor**: Tint for the reflection.

### Implementation Call
Implemented in `lilReflection` (lil_common_frag.hlsl), called via `OVERRIDE_REFLECTION`.

```hlsl
#define OVERRIDE_REFLECTION \
    lilReflection(fd LIL_SAMP_IN(sampler_MainTex) LIL_HDRP_POSITION_INPUT_VAR);
```

### Principles & Math
**Specular (Blinn-Phong / GGX style)**
Calculates the reflection of direct light sources off the surface.
Typically involves the Half Vector ($H = \frac{L + V}{|L + V|}$) and Roughness.
lilToon uses a modified look-up or calculation for toon specular.

**Environment Reflection (Indirect Light)**
Samples the reflection probe or environment map based on the reflected view vector.
$ReflectVector = reflect(-ViewDir, Normal)$

**Function (`lilReflection` Pseudo-Code):**

```hlsl
// 1. Surface Data
fd.smoothness = _Smoothness * Sample(_SmoothnessTex);
GSAAForSmoothness(fd.smoothness, fd.N, _GSAAStrength); // Anti-aliasing
float metallic = _Metallic * Sample(_MetallicGlossMap);

// 2. Specular (Direct Light)
float3 H = normalize(LightDir + ViewDir);
float NdotH = saturate(dot(Normal, H));
// ... Calculate Specular Term ...
float3 specularColor = LightColor * specularTerm * SpecularStrength;
FinalColor = lilBlendColor(FinalColor, specularColor, ...);

// 3. Environment Reflection
float3 envReflectionColor = LIL_GET_ENVIRONMENT_REFLECTION(fd.V, N, fd.perceptualRoughness, ...);
float3 fresnel = lilFresnelLerp(specular, grazingTerm, NdotV);
FinalColor += surfaceReduction * envReflectionColor * fresnel;
```

**Fresnel Function (`lilFresnelLerp`):**
Schlick's approximation: $F(\theta) = F_0 + (F_{90} - F_0) (1 - \cos\theta)^5$

## 2. MatCap (Sphere Mapping)
MatCap projects a texture onto the object based on the view-space normal.

### Properties
*   **_UseMatCap**: Enable MatCap.
*   **_MatCapTex**: The sphere map texture.
*   **_MatCapBlend**: Blend strength.
*   **_MatCapEnableLighting**: Interaction with scene lighting.

### Implementation Call
Implemented in `lilGetMatCap`, called via `OVERRIDE_MATCAP`.

```hlsl
#define OVERRIDE_MATCAP \
    lilGetMatCap(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math
The UV coordinates are derived from the Normal vector transformed into View Space.
$UV = Normal_{ViewSpace}.xy \times 0.5 + 0.5$

**Function (`lilCalcMatCapUV`):**

```hlsl
float2 lilCalcMatCapUV(...) {
    // Get Normal in View Space
    float3 normalVS = mul(ViewMatrix, normalWS);
    // Map to 0-1 range
    float2 uv = normalVS.xy * 0.5 + 0.5;
    // Apply Tiling/Offset
    return uv * Tiling + Offset;
}
```

## 3. Rim Shade (Ambient Occlusion style)
Darkens the edges of the object to simulate occlusion or thickness.

### Properties
*   **_UseRimShade**: Enable Rim Shade.
*   **_RimShadeColor**: Color (usually dark).
*   **_RimShadeBorder**, **_RimShadeBlur**: Control edge sharpness.

### Implementation Call
Implemented in `lilGetRimShade`, called via `OVERRIDE_RIMSHADE`.

### Principles & Math
Based on the dot product of Normal and View Direction (NdotV).
$Rim = (1 - |N \cdot V|)^{Power}$

**Function (`lilGetRimShade` Pseudo-Code):**

```hlsl
void lilGetRimShade(...) {
    float NdotV = abs(dot(Normal, ViewDir));
    float rimBase = pow(saturate(1.0 - NdotV), _RimShadeFresnelPower);
    
    // Toon Step
    float rimFactor = lilTooningScale(1.0, rimBase, _RimShadeBorder, _RimShadeBlur);
    rimFactor *= Sample(_RimShadeMask);
    
    // Blend (Darken)
    FinalColor = lerp(FinalColor, FinalColor * _RimShadeColor, rimFactor);
}
```

## 4. Rim Light
Similar to Rim Shade, but blends light (additive or mixed) at the edges.

### Properties
*   **_UseRim**: Enable Rim Light.
*   **_RimColor**: Color of the light.
*   **_RimFresnelPower**: Controls width.

### Implementation Call
Implemented in `lilGetRimLight`, called via `OVERRIDE_RIMLIGHT`.

```