# Outline

The Outline feature is a core component of the "toon" look, typically implemented using the **Inverted Hull** method (rendering the mesh inside-out and slightly larger).

## 1. Principles
The outline is rendered as a separate pass (or a specialized variant).

### Vertex Displacement
Vertices are pushed outward along their **Normals** in object space. To make the outline look consistent, lilToon also supports using a **Vector Map** (to smooth sharp edges) or **Vertex Colors** to control width.

### Inverted Hull (Pass Settings)
*   **Culling**: Set to `Front` (only backfaces are rendered).
*   **Offset**: Often adjusted to prevent Z-fighting with the main surface.

## 2. Properties
*   **_OutlineColor**: Color and transparency of the outline.
*   **_OutlineWidth**: Base width.
*   **_OutlineWidthMask**: Texture to scale the width (R channel).
*   **_OutlineFixWidth**: Controls how width changes with distance from camera (0 = 3D size, 1 = Screen size).
*   **_OutlineZBias**: Offsets the outline towards/away from the camera to fix depth issues.
*   **_OutlineVectorTex**: A normal map-like texture to define custom "push" directions.
*   **_OutlineLitColor**: Allows the outline to be affected by scene lights.

## 3. Implementation (Vertex Shader)
The vertex displacement logic is found in `lil_vert_outline.hlsl` and `lil_common_functions.hlsl`.

### Math Formula
1.  **Base Width**: $W_{base} = \text{Width} \times 0.01$
2.  **Masking**: $W_{mask} = W_{base} \times \text{Sample}(\text{WidthMask})$
3.  **Distance Scaling**:
    *   Makes the outline constant size on screen.
    *   $W_{final} = W_{mask} \times \text{lerp}(1.0, \text{DistanceToCamera}, \text{FixWidth})$
4.  **Displacement**: $Pos_{new} = Pos_{old} + Normal_{OS} \times W_{final}$

### Pseudo-Code (`lilCalcOutlinePosition`)
```hlsl
void lilCalcOutlinePosition(inout float3 positionOS, float3 normalOS, ...)
{
    // 1. Calculate the distance-fixed width
    float3 positionWS = TransformObjectToWorld(positionOS);
    float dist = length(CameraPosition - positionWS);
    
    float width = _OutlineWidth * 0.01;
    width *= Sample(WidthMask).r;
    
    // Scale width based on distance to keep it constant in screen-space
    width *= lerp(1.0, dist, _OutlineFixWidth);

    // 2. Select the extrusion vector
    float3 outlineN = normalOS;
    #if USE_VECTOR_TEX
        outlineN = UnpackNormal(Sample(OutlineVectorTex));
    #endif

    // 3. Extrude
    positionOS += outlineN * width;

    // 4. Apply Z-Bias (push away from camera to avoid clipping)
    float3 viewDirOS = normalize(CameraPosOS - positionOS);
    positionOS -= viewDirOS * _OutlineZBias;
}
```

## 4. Implementation (Fragment Shader)
The fragment shader handles the coloring and optional lighting of the outline.

```hlsl
#define OVERRIDE_OUTLINE_COLOR \
    // 1. Sample texture
    fd.col = Sample(_OutlineTex, uv);
    
    // 2. Adjust HSVG
    fd.col.rgb = lilToneCorrection(fd.col.rgb, _OutlineTexHSVG);
    
    // 3. Apply Lighting
    // Check dot product of Light and Normal
    float factor = saturate(NdotL * _LitScale + _LitOffset);
    fd.col.rgb = lerp(fd.col.rgb * _OutlineColor, _OutlineLitColor, factor);
```

## 5. Variants
*   **`lts_o.shader`**: Standard shader including an Outline pass.
*   **`lts_oo.shader`**: **Outline Only**. Contains ONLY the outline rendering pass.

```