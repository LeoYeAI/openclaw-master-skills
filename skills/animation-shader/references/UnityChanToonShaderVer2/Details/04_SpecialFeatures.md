# Special Features

## 1. Angel Ring
The "Angel Ring" (or "Tenshi no Wa") is a stylized highlight often seen on anime hair.

*   **Behavior**: Unlike a static texture, the Angel Ring stays "fixed" relative to the camera view vertically, simulating a specular highlight on a anisotropic surface (like hair strands).
*   **Properties**:
    *   **`_AngelRing_Sampler`**: The texture of the highlight.
    *   **`_AngelRing_Color`**: Tint color.
    *   **`_AR_OffsetU` / `_AR_OffsetV`**: Adjusts the position.
    *   **`_ARSampler_AlphaOn`**: Uses texture alpha for blending.

### Implementation Logic
**Pseudo-Code:**
```hlsl
// 1. Calculate View-Space Normal
float3 viewNormal = mul(UNITY_MATRIX_V, float4(normal, 0)).xyz;

// 2. Project UVs
// X is standard view-normal X (horizontal movement)
// Y is fixed (vertical movement ignored, or offset manually)
float2 arUV = float2(viewNormal.x * 0.5 + 0.5, _AR_OffsetV);

// 3. Apply Offset
arUV.x += _AR_OffsetU;

// 4. Sample & Blend
float4 arColor = tex2D(_AngelRing_Sampler, arUV) * _AngelRing_Color;
finalColor = lerp(finalColor, finalColor + arColor.rgb, arColor.a);
```

## 2. MatCap (Material Capture)
Used for shiny surfaces (metal, latex, gold).

*   **Camera Rolling Stabilizer**: A unique UTS2 feature. Standard MatCaps rotate when you tilt the camera (roll). UTS2 calculates the camera roll angle and counter-rotates the MatCap UVs, keeping the reflection "upright" relative to the horizon.
*   **Properties**:
    *   **`_MatCap_Sampler`**: Sphere map texture.
    *   **`_BlurLevelMatcap`**: Blur level (LOD).
    *   **`_CameraRolling_Stabilizer`**: Toggle for the counter-rotation feature.
    *   **`_Tweak_MatCapUV`**: Zoom/Scale of the MatCap.

### Implementation Logic
**Pseudo-Code (Camera Roll):**
```hlsl
// Calculate Camera Roll
float3 camRight = UNITY_MATRIX_V[0].xyz;
float3 camFront = UNITY_MATRIX_V[2].xyz;
float3 up = float3(0,1,0);
float3 rightHorizon = cross(camFront, up);

// Calculate Angle between Camera Right and Horizon Right
float rollCos = dot(rightHorizon, camRight);
float rollAngle = acos(rollCos);

// Counter-Rotate UVs
if (_CameraRolling_Stabilizer) {
    matCapUV = RotateUV(matCapUV, -rollAngle);
}
```

## 3. Emission
Supports standard emission plus animation.

*   **Keyword**: `_EMISSIVE_ANIMATION`.
*   **Scrolling**: `_Scroll_EmissiveU`, `_Scroll_EmissiveV`.
*   **Blinking**: `_Is_PingPong_Base` enables a sin-wave pulsing.
*   **Color Shift**: `_Is_ColorShift` changes color over time.
*   **View Shift**: `_Is_ViewShift` changes color based on viewing angle (iridescence).

**Pseudo-Code:**
```hlsl
// Scrolling
float2 scroll = float2(_Scroll_EmissiveU, _Scroll_EmissiveV) * _Time.y;
float2 uv = input.uv + scroll;

// Blinking (PingPong)
if (_Is_PingPong_Base) {
    float wave = sin(_Time.y * _Base_Speed);
    uv += wave * scrollDir; // Oscillate back and forth
}

float3 emission = tex2D(_Emissive_Tex, uv).rgb * _Emissive_Color;
```

## 4. Clipping & Stencil
Used for advanced rendering techniques, like seeing eyebrows through hair.

*   **Clipping Mask**: `_ClippingMask` allows discarding pixels based on a texture.
*   **Stencil**:
    *   **`_StencilMode`**: Can be set to `StencilMask` (write to buffer) or `StencilOut` (read and discard).
    *   **Use Case**:
        1.  Render Eyebrows with `StencilMask` (ID=1).
        2.  Render Hair.
        3.  Where Hair overlaps Eyebrows (Stencil Test), discard the Hair pixels, revealing the eyebrows "on top".

**Logic:**
```hlsl
// In Fragment Shader
float clipVal = tex2D(_ClippingMask, uv).r;
// _Inverse_Clipping flips the logic
if (_Inverse_Clipping) clipVal = 1.0 - clipVal;

// Apply Level Threshold
clip(clipVal - _Clipping_Level);
```
