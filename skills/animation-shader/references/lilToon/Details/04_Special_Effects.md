# Special Effects

## 1. Glitter
Simulates a multi-faceted sparkling surface.

### Properties
*   **_UseGlitter**: Enable Glitter.
*   **_GlitterColor**: Base color.
*   **_GlitterParams1**, **_GlitterParams2**: Parameters controlling particle size, tiling, contrast, etc.
*   **_GlitterShapeTex**: Optional texture for particle shape.
*   **_GlitterSensitivity**: Sensitivity to light/view angle.

### Implementation Call
Implemented in `lilGlitter` (lil_common_frag.hlsl), called via `OVERRIDE_GLITTER`.

```hlsl
#define OVERRIDE_GLITTER \
    lilGlitter(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math
1.  **Grid Generation**: Divide UV space into a grid.
2.  **Randomization (Voronoi)**: Assign a random seed to each cell.
3.  **Sparkle Calculation**: Compare view/light angle with a random normal.

**Function (`lilCalcGlitter` Pseudo-Code):**
```hlsl
float3 lilCalcGlitter(float2 uv, float3 N, float3 V, float3 L, ...) {
    float2 pos = uv * Tiling;
    // Voronoi Noise: Get random cell center & seed
    float4 near = lilVoronoi(pos, ...); 
    
    // Random Facet Normal from seed
    float3 sparkleNormal = abs(frac(near.xyz * 14.27 + Time * Speed) * 2.0 - 1.0);
    sparkleNormal = normalize(sparkleNormal * 2.0 - 1.0);
    
    // View Alignment
    float glitter = dot(sparkleNormal, CameraDir);
    glitter = abs(frac(glitter * Sensitivity) - 0.5) * 4.0 - 1.0; // Peak function
    glitter = pow(saturate(glitter), Contrast);
    
    // Lighting Influence
    float3 H = normalize(V + L);
    glitter *= saturate(dot(N, H)); // Mask by specular highlight area

    return Color * glitter;
}
```

## 2. Emission (Blinking & Gradation)
Adds glowing effects with animation.

### Properties
*   **_UseEmission**: Enable Emission.
*   **_EmissionColor**: Color and intensity.
*   **_EmissionMap**: Emission texture.
*   **_EmissionBlink**: Blinking settings (speed, offset, etc.).
*   **_EmissionGradTex**: Gradation texture for animated color changes.

### Implementation Call
Implemented in `lilEmission`, called via `OVERRIDE_EMISSION_1ST`.

```hlsl
#define OVERRIDE_EMISSION_1ST \
    lilEmission(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math
**Blinking (`lilCalcBlink`)**
Uses a sine wave: $Blink = \sin(Time \times Speed + Offset) \times 0.5 + 0.5$

```hlsl
float lilCalcBlink(float4 blinkParams) {
    float outBlink = sin(Time * blinkParams.z + blinkParams.w) * 0.5 + 0.5;
    if(blinkParams.y > 0.5) outBlink = round(outBlink); // Hard Blink
    return lerp(1.0, outBlink, blinkParams.x); // Blend by strength
}
```

**Gradation**
Samples a 1D gradient texture based on time.
```hlsl
float gradUV = Speed * Time;
EmissionColor *= Sample(GradationTex, gradUV);
```

## 3. Dissolve
Erodes the object based on a mask and a threshold value.

### Properties
*   **_DissolveParams**: Controls mode (Texture, Point, Line), threshold, and edge width.
*   **_DissolveMask**: Texture mask.
*   **_DissolveNoiseMask**: Noise texture to randomize the edge.

### Implementation Call
Implemented in `lilCalcDissolveWithNoise`, called via `OVERRIDE_DISSOLVE`.

```hlsl
#define OVERRIDE_DISSOLVE \
    lilCalcDissolveWithNoise(...);
```

### Principles & Math
Compare Mask vs Threshold.
*   If $Mask < Threshold$, discard pixel.
*   Create border where $Mask \approx Threshold$.

**Pseudo-Code:**
```hlsl
void lilCalcDissolveWithNoise(...) {
    float mask = Sample(DissolveMask, uv);
    float noise = Sample(NoiseMask, uv) - 0.5;
    float combinedMask = mask + noise * Strength;
    
    // Visibility Check
    float visibility = combinedMask > Threshold ? 1.0 : 0.0;
    
    // Border Alpha (Glowing Edge)
    float borderAlpha = 1.0 - saturate(abs(combinedMask - Threshold) / BorderWidth);
    
    FinalAlpha *= visibility;
    OutBorderAlpha = borderAlpha;
}
```

## 4. Parallax Occlusion Mapping (POM)
Simulates depth by raymarching into the height map.

### Properties
*   **_UseParallax**: Enable Parallax.
*   **_UsePOM**: Enable POM.
*   **_ParallaxMap**: Height map.
*   **_Parallax**: Scale.

### Implementation Call
Called via `OVERRIDE_PARALLAX`.

### Principles & Math
Iteratively steps UV coordinates along the view vector projected onto the surface.

**Pseudo-Code (`lilPOM`):**
```hlsl
void lilPOM(...) {
    float3 rayDir = normalize(ViewDirTangentSpace);
    rayDir.z *= -1.0; // Invert Z (looking down)
    
    float stepSize = 1.0 / Steps;
    float currentHeight = 1.0;
    float2 currentUV = originalUV;
    
    for(int i=0; i < Steps; i++) {
        float heightFromMap = Sample(HeightMap, currentUV).r;
        if(currentHeight < heightFromMap) break; // Hit surface
        
        currentUV += rayDir.xy * stepSize * Scale;
        currentHeight -= stepSize;
    }
    modifiedUV = currentUV;
}
```
