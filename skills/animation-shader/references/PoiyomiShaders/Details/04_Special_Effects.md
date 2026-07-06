# Special Effects

Poiyomi Shader includes a vast array of special effects, many of which are integrated with AudioLink for music reactivity.

## 1. Emission
Poiyomi supports up to **4 independent Emission layers** (Emission, Emission1, Emission2, Emission3).

### Call Site
`Assets/_PoiyomiShaders/Shaders/8.1/Toon/Poiyomi.shader` (approx line 13356 in `applyEmission`).

### Properties
*   **Color**: `_EmissionColor`, `_EmissionMap`.
*   **Scrolling**:
    *   **`_ScrollingEmission`**: Toggle.
    *   **`_EmissiveScroll_Direction`**: Direction vector.
    *   **`_EmissiveScroll_Velocity`**: Speed.
*   **Blinking**:
    *   **`_EmissionBlinkingEnabled`**: Toggle.
    *   **`_EmissiveBlink_Min`** / **`_EmissiveBlink_Max`**: Bounds for blinking strength.
    *   **`_EmissiveBlink_Velocity`**: Speed of blink.

### Implementation
**Pseudo-Code:**
```hlsl
float3 applyEmission(...) {
    float3 emission = SampleTexture(_EmissionMap) * _EmissionColor;
    
    // 1. Scrolling
    if (_ScrollingEmission) {
        float2 scrollOffset = _Time.x * _EmissiveScroll_Velocity * _EmissiveScroll_Direction;
        emission = SampleTexture(_EmissionMap, uv + scrollOffset);
    }
    
    // 2. Blinking
    if (_EmissionBlinkingEnabled) {
        float blink = sin(_Time.y * _EmissiveBlink_Velocity);
        // Remap -1..1 to Min..Max
        blink = lerp(_EmissiveBlink_Min, _EmissiveBlink_Max, blink * 0.5 + 0.5);
        emission *= blink;
    }
    
    // 3. AudioLink Modulation (See below)
    
    return emission;
}
```

## 2. AudioLink Integration
Poiyomi has native support for [AudioLink](https://github.com/llealloo/vrc-udon-audio-link), a standard for music-reactive avatars in VRChat.

### Supported Features
*   **Emission**: `_EmissionAL0Enabled`. Modulates emission strength.
    ```hlsl
    if (_EmissionAL0Enabled) {
        float audioValue = AudioLinkData(Band).r;
        emissionStrength *= lerp(1.0, audioValue, _EmissionAL0StrengthMod);
    }
    ```
*   **Center Out**: `_AudioLinkEmission0CenterOut`. Pulses emission rings from the center.
*   **Vertex Manipulation**: Bounce/scale/jitter vertices to the beat.
*   **Decals**: Scale or rotate decals based on audio volume.

## 3. Dissolve
Advanced dissolve effects to hide parts of the mesh.

### Properties
*   **`_UVTileDissolveEnabled`**: Enables "pixelated" dissolve.
*   **`_DissolveTexture`**: The noise map driving the dissolve.
*   **`_DissolveAlpha`**: The cutoff value (0 to 1).
*   **`_DissolveEdgeWidth`**: Size of the glowing edge.
*   **`_DissolveEdgeColor`**: Color of the edge.

### Implementation
**Call Site**: `vert` shader (for vertex discard) and `frag` shader (for pixel discard/coloring).

**Pixel Logic:**
```hlsl
float noise = SampleTexture(_DissolveTexture, uv);
if (noise < _DissolveAlpha) discard;

// Edge Color
float edgeFactor = smoothstep(_DissolveAlpha, _DissolveAlpha + _DissolveEdgeWidth, noise);
finalColor += _DissolveEdgeColor * (1.0 - edgeFactor);
```

## 4. Flipbook
Frame-by-frame animation support for textures.
*   **`_FlipbookTotalFrames`**: Total number of frames in the sheet.
*   **`_FlipbookFPS`**: Speed of animation.
*   **Logic**: Calculates a UV offset based on time to step through the grid of sprites.

## 5. Glitching
Simulates digital artifacts and screen tearing.
*   **Vertex Glitch**: Displaces vertices (see Base Features).
*   **Texture Glitch**: Offsets UVs to create "tearing" in the texture lookup.
*   **AudioLink**: Glitch intensity can be driven by music volume.
