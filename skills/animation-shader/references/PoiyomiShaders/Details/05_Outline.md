# Outline

Poiyomi uses an Inverted Hull method for outlines, implemented in a separate shader pass or variant (`Poiyomi Outline.shader`).

## 1. Vertex Displacement
Vertices are extruded along their normals to create the outline shell.

### Call Site
`Assets/_PoiyomiShaders/Shaders/8.1/Toon/Poiyomi Outline.shader` (approx line 9300 in `vert`).

### Properties
*   **Width**:
    *   **`_LineWidth`**: Base width of the outline.
    *   **`_OutlineFixedSize`**: Toggle for screen-space constant size.
    *   **`_OutlineFixWidth`**: Factor for fixed size scaling.
*   **Masking**:
    *   **`_OutlineMask`**: Texture mask.
    *   **`_OutlineVertexColorMask`**: Channel of vertex color to use as mask.
*   **Color**:
    *   **`_OutlineColor`**: Base color.
    *   **`_OutlineLit`**: Toggle to enable lighting on outlines.

### Logic (Pseudo-code)
```hlsl
// 1. Calculate Mask
float mask = SampleTexture(_OutlineMask);
if (_OutlineVertexColorMask > 0) {
    // 1=R, 2=G, 3=B, 4=A
    mask *= v.color[_OutlineVertexColorMask - 1]; 
}

// 2. Select Normal
// Can use mesh normals or custom normals baked into vertex colors
float3 normal = _OutlineSpace ? worldNormal : objectNormal;
if (_OutlineUseVertexColorNormals) {
    // Decode custom normal from vertex color (0..1 -> -1..1)
    float3 customNormal = v.color.rgb * 2.0 - 1.0;
    normal = TransformToWorld(customNormal);
}

// 3. Distance Scaling (Fixed Size)
// Keeps outlines visible even at a distance
float dist = distance(CameraPos, WorldPos);
float sizeFactor = 1.0;
if (_OutlineFixedSize) {
    sizeFactor = lerp(1.0, clamp(dist, 0, _OutlinesMaxDistance), _OutlineFixWidth);
}

// 4. AudioLink Modulation
float width = _LineWidth;
if (_AudioLinkAnimToggle) {
    // Modulate width by audio band volume
    width += lerp(_AudioLinkOutlineSize.x, _AudioLinkOutlineSize.y, AudioLinkData(Band));
}

// 5. Extrude
// Base extrusion formula
float3 offset = normal * (width / 100.0) * mask * sizeFactor;
v.vertex.xyz += offset;
```

## 2. Rendering Features
*   **Lighting**: Outlines can be Lit (affected by shadows) or Unlit.
    *   If `_OutlineLit` is enabled, the fragment shader calculates standard lighting.
*   **Coloring**: Texture mode, Color tint, or Screen-space texture.
*   **Culling**: Front-face culling is used to render the backfaces of the extruded shell.
*   **Z-Bias**: Offsets depth to prevent Z-fighting or to make lines appear "on top".

## 3. AudioLink
Outlines can react to music:
*   **Width**: Pulse thickness to the beat (logic in Vertex Shader).
*   **Color**: Shift hue or emission brightness based on audio bands (logic in Fragment Shader).
