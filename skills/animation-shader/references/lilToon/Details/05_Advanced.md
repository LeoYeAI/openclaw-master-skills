# Advanced Features

## 1. AudioLink
Integrates with the AudioLink system to make materials react to music.

### Properties
*   **_UseAudioLink**: Enable AudioLink.
*   **_AudioLinkUVParams**: Selects the frequency band (Bass, Low Mid, High Mid, Treble) and maps it to UVs or effects.
*   **_AudioLink2Emission**, **_AudioLink2Vertex**, etc.: Toggles for specific effects.

### Implementation Call
Implemented in `lilAudioLinkFrag` (lil_common_frag.hlsl), called via `OVERRIDE_AUDIOLINK`.

```hlsl
#define OVERRIDE_AUDIOLINK \
    lilAudioLinkFrag(fd LIL_SAMP_IN(sampler_MainTex));
```

### Principles & Math
AudioLink writes audio amplitude data into a 128x4 texture.
*   **X**: Frequency bins.
*   **Y**: 4 rows (Bass, LowMid, HighMid, Treble) + History.

**Function (`lilAudioLinkFrag` Pseudo-Code):**

```hlsl
void lilAudioLinkFrag(inout lilFragData fd, ...) {
    // 1. Calculate UV
    float2 alUV = float2(0, 0);
    // Select Band Row (0-3)
    alUV.y = (float(_AudioLinkBand) + 0.5) / 4.0; 
    
    // 2. Sample Texture (Global AudioLink Texture)
    float4 audioData = Sample(_AudioLinkTexture, alUV);
    float amplitude = audioData.r; // Red channel typically holds amplitude
    
    // 3. Store
    fd.audioLinkValue = amplitude;
    
    // Example: Modulate Emission
    // Emission *= fd.audioLinkValue * Strength;
}
```

## 2. Outline (Inverted Hull)
Renders a colored outline around the object.

### Properties
*   **_OutlineColor**: Color of the outline.
*   **_OutlineWidth**: Width of the outline.
*   **_OutlineWidthMask**: Mask to control width per-vertex/pixel.
*   **_OutlineLitColor**: Interaction with lighting.

### Implementation Call
**Pass**: `FORWARD_OUTLINE` in `ltspass_opaque.shader`.
**Fragment**: `OVERRIDE_OUTLINE_COLOR` in `lil_common_frag.hlsl`.

```hlsl
#define OVERRIDE_OUTLINE_COLOR \
    LIL_GET_OUTLINE_TEX \
    LIL_APPLY_OUTLINE_TONECORRECTION \
    LIL_APPLY_OUTLINE_COLOR
```

### Principles & Math
**Vertex Shader (Extrusion)**
1.  Render mesh with Front Face Culling (Inside out).
2.  Move vertices along normal: $Pos_{new} = Pos + Normal \times Width$.

**Function (`lilCalcOutlinePosition` Pseudo-Code):**

```hlsl
void lilCalcOutlinePosition(...) {
    float width = _OutlineWidth * Sample(WidthMask, uv).r;
    
    // Distance scaling (Fixed Width in screen space)
    float dist = distance(CameraPos, positionWS);
    width *= lerp(1.0, dist, _OutlineFixWidth);
    
    positionOS += normalOS * width;
}
```

## 3. ID Mask
Efficiently hides parts of a mesh using a mask map or vertex IDs.

### Properties
*   **_IDMaskCompile**: Compile-time switch.
*   **_IDMask1** to **_IDMask8**: Toggles for specific ID ranges.
*   **_IDMaskIndex...**: The value to match.

### Principles & Math
*   **Vertex ID**: Checks `SV_VertexID` against a range $[Min, Max)$.
*   **Texture**: Checks pixel value against threshold.

**Function (`IDMask` Pseudo-Code):**

```hlsl
bool IDMask(uint vertexID, int indices[8], float flags[8]) {
    // Check if ID is in a disabled range
    if (vertexID >= indices[0] && vertexID < indices[1] && flags[0] == 1) return true; // Hide
    // ... check other ranges ...
    return false; // Show
}
```
If true, vertex is collapsed (moved to NaN or infinity) or pixel is discarded.

## 4. UDIM Discard
Optimized texture atlas usage. Discards pixels based on UV tile coordinates.

### Properties
*   **_UDIMDiscardMode**: Vertex or Pixel discard.
*   **_UDIMDiscardRow...**: Toggles for specific UV tiles.

### Implementation Call
Called via `OVERRIDE_UDIMDISCARD`.

```hlsl
#define OVERRIDE_UDIMDISCARD \
    if(_UDIMDiscardMode == 1 && LIL_CHECK_UDIMDISCARD(fd)) discard;
```

### Principles & Math
Tile Index = $(\text{floor}(u), \text{floor}(v))$.

**Function (`lilUDIMDiscard` Pseudo-Code):**

```hlsl
bool lilUDIMDiscard(float2 uv) {
    int u = (int)floor(uv.x);
    int v = (int)floor(uv.y);
    
    // Check against enabled tiles
    if (u == 0 && v == 0 && _UDIMDiscardRow0_0) return true; // Discard
    // ...
    return false;
}
```
