# Outline

UTS2 uses the **Inverted Hull** method for outlines, where a second pass renders the mesh inside-out and slightly larger than the original.

## 1. Core Properties
*   **`_Outline_Width`**: The base thickness of the outline.
*   **`_Outline_Color`**: The color of the line.
*   **`_Is_BlendBaseColor`**: If enabled, the outline color blends with the underlying texture color. This is useful for creating softer, colored outlines (e.g., skin-colored outlines on skin) rather than harsh black lines.
*   **`_Outline_Sampler`**: Texture mask to control outline width per-pixel.

## 2. Vertex Extrusion
The vertex shader moves vertices along their normals.

**Call Site**: `vert` function in `UniversalToonOutline.hlsl`.

**Pseudo-Code:**
```hlsl
VertexOutput vert (VertexInput v) {
    // 1. Calculate Distance Scaling
    // Prevents clutter at a distance
    float dist = distance(ObjectPos, CameraPos);
    float distScale = smoothstep(_Farthest_Distance, _Nearest_Distance, dist);
    
    // 2. Determine Normal
    // Use Baked Normal if enabled (smoother lines on hard edges)
    float3 normal = v.normal;
    if (_Is_BakedNormal) {
        float3 baked = UnpackNormal(tex2D(_BakedNormal, uv));
        normal = baked;
    }
    
    // 3. Calculate Width
    float width = _Outline_Width * 0.001 * distScale;
    width *= SampleTexture(_Outline_Sampler, uv).r; // Apply mask
    
    // 4. Extrude
    // Move vertex along normal
    float4 pos = v.vertex;
    pos.xyz += normal * width;
    
    // 5. Apply Z-Offset
    // Push outline deeper to prevent z-fighting
    o.pos = UnityObjectToClipPos(pos);
    
    // Adjust Z based on camera clip space
    o.pos.z += _Offset_Z * ClipCameraPos.z; 
    
    return o;
}
```

### Distance Scaling
To prevent outlines from becoming a messy blob when the character is far away, UTS2 scales the width based on distance.

*   **`_Farthest_Distance`**: Distance at which outlines are thinnest (0 width).
*   **`_Nearest_Distance`**: Distance at which outlines are thickest (Max width).

### Baked Normals (`_BakedNormal`)
Standard smooth normals can cause outlines to "break" or look disjointed at hard edges (like boxy hair or clothes). Splitting vertices fixes shading but breaks outlines (gaps appear).

UTS2 allows using a **Baked Normal Map** for the outline pass.
*   The mesh uses split vertices for hard shading edges.
*   The Outline pass ignores the mesh normals and instead reads a "smooth" normal from a texture (UV mapped).
*   This results in a continuous outline even on a mesh with hard edges.

## 3. Z-Offset
*   **`_Offset_Z`**: Pushes the outline deeper into the Z-buffer. This helps prevent "Z-fighting" where the outline flickers on top of the mesh, ensuring it stays behind the main geometry.
