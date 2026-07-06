# Base & Main Features

This document details the base appearance and geometry manipulation features of the Poiyomi Toon Shader.

## 1. Main Appearance
The core visual settings found in the "Main" section.

### Properties
*   **Color & Texture**:
    *   `_Color`: Base color tint.
    *   **`_MainTex`**: Base Albedo texture.
    *   **`_BumpMap`**: Normal map.
    *   **`_BumpScale`**: Normal map intensity.
    *   **`_Cutoff`**: Alpha cutoff threshold (for Cutout mode).
    *   **`_AlphaMod`**: Global alpha modifier.
*   **Color Adjust**:
    *   **`_MainHueShift`**: Hue shift amount (0-1).
    *   **`_Saturation`**: Saturation adjustment (-1 to 1).
    *   **`_MainBrightness`**: Brightness multiplier.

### Implementation Call
**Fragment Shader**: `frag` function in `Poiyomi.shader`.
The base color is sampled and adjusted early in the fragment pipeline.

**Pseudo-Code:**
```hlsl
float4 mainTexture = SampleTexture(_MainTex, uv);
float3 baseColor = mainTexture.rgb * _Color.rgb;

// Hue Shift
baseColor = HueShift(baseColor, _MainHueShift);

// Saturation/Brightness
baseColor = AdjustSaturation(baseColor, _Saturation);
baseColor *= _MainBrightness;
```

## 2. Vertex Manipulation
Geometric deformations applied in the Vertex Shader. This allows for animating the mesh without changing the actual model data.

### Properties
*   **Translation**: `_VertexManipulationLocalTranslation`, `_VertexManipulationWorldTranslation`.
*   **Rotation**: `_VertexManipulationLocalRotation` (Euler angles), `_VertexManipulationLocalRotationSpeed`.
*   **Scale**: `_VertexManipulationLocalScale`.
*   **Rounding**: `_VertexRoundingEnabled`, `_VertexRoundingDivision` (Grid size for retro effect).
*   **Distortion**: `_VertexBarrelMode`, `_VertexSphereMode`.

### Implementation Call
**Vertex Shader**: `vert` function in `Poiyomi.shader` (approx line 8920).

**Core Logic (Pseudo-code):**
```hlsl
VertexOut vert(appdata v) {
    // 1. AudioLink Data Retrieval
    float4 bands = GetAudioLinkBands();
    
    // 2. Calculate Offsets
    float3 translation = _VertexManipulationLocalTranslation;
    float3 rotation = _VertexManipulationLocalRotation;
    
    if (_VertexAudioLinkEnabled) {
        // AudioLink modifies the base transformation values
        translation += lerp(_VertexLocalTranslationALMin, _VertexLocalTranslationALMax, bands[BandIndex]);
        rotation += bands[RotBand] * _VertexLocalRotationAL;
    }
    
    // 3. Apply Rotation & Translation
    // Rotate around pivot (usually object center)
    v.vertex = Rotate(v.vertex, rotation);
    v.vertex.xyz += translation;
    
    // 4. Barrel/Sphere Distortion
    if (_VertexBarrelMode) {
        // Distort XZ based on height or distance
        v.vertex.xz = DistortBarrel(v.vertex.xz, _VertexBarrelWidth);
    }
    
    // 5. Rounding (Retro Effect)
    if (_VertexRoundingEnabled) {
        float grid = _VertexRoundingDivision;
        // Snap vertex positions to the nearest grid point
        v.vertex.xyz = ceil(v.vertex.xyz / grid) * grid;
    }
    
    return o;
}
```

## 3. Vertex Glitching
Simulates digital artifacts by displacing vertices randomly or based on a texture.

### Properties
*   **`_VertexGlitchStrength`**: Intensity of the glitch displacement.
*   **`_VertexGlitchFrequency`**: Speed of the jitter animation.
*   **`_VertexGlitchThreshold`**: Cutoff value to make glitching intermittent.
*   **`_VertexGlitchMap`**: Optional texture to mask where glitches happen.

### Principles & Math
Uses a noise function based on time and vertex position (`_Time.y` and `worldPos.y`) to generate a random offset vector.

### Implementation
**Pseudo-Code:**
```hlsl
if (_VertexGlitchingEnabled) {
    // Generate noise based on time and position
    float time = _Time.y * _VertexGlitchFrequency;
    float noise = sin(dot(worldPos.y, 12.9898)) + sin(time);
    
    // Threshold check
    if (noise > _VertexGlitchThreshold) {
        // Calculate offset direction (orthogonal to view)
        float3 direction = normalize(cross(ViewDir, Up));
        
        // Apply offset
        float3 offset = direction * _VertexGlitchStrength;
        
        // AudioLink Modulation
        if (_VertexAudioLinkEnabled) {
            offset *= AudioLinkData(Band).r;
        }
        
        v.vertex.xyz += offset;
    }
}
```

## 4. Dissolve
Poiyomi supports advanced dissolve effects, including "UV Tile Dissolve".

### Properties
*   **`_UVTileDissolveEnabled`**: Toggle for tile-based dissolve.
*   **`_DissolveAlpha`**: Progress of the dissolve.

### Implementation
**Vertex Discard Logic:**
```hlsl
if (_UVTileDissolveEnabled) {
    // Quantize UVs to create "tiles"
    float2 tileUV = floor(v.uv * GridSize);
    
    // Sample noise for this tile
    float noise = SampleNoise(tileUV);
    
    // Discard entire tile if below threshold
    if (noise < _DissolveAlpha) {
        return NAN; // Discard vertex by returning NaN position
    }
}
```
