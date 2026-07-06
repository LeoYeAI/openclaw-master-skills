# Artistic Controls (艺术控制)

除了核心的光照和描边，SToon 还提供了一系列“破坏性”或“动态”的控制功能，用于打破计算机渲染的完美感，增添手绘或有机风格。

## 1. Diffuse Warp (漫反射扭曲)

这是一个非常有趣的功能，它不直接改变光照模型，而是通过扰动 NdotL 的计算结果来扭曲阴影边缘。

### Logic
*   **Source**: 使用一张噪点贴图 (`_DiffuseWarpNoise`)。
*   **Transform**: 支持独立的 UV Tiling (`_WarpTextureScale`) 和 Rotation (`_WarpTextureRotation`)，甚至支持屏幕空间 UV (`_UseScreenUvsWarp`)。
*   **Implementation**:
    ```glsl
    // 采样噪点
    float BNLightWarpVector250 = ( _UseDiffuseWarp == 1.0 ? ( tex2D( _DiffuseWarpNoise, rotator1489 ).r * _WarpStrength ) : 0.0 );
    
    // 扰动 NdotL
    // 公式: Warp * (1 + NdotL) ... 或类似的混合逻辑
    // 实际代码看起来像是：
    float3 temp_cast_7 = (( BNLightWarpVector250 + ( ( 1.0 - BNLightWarpVector250 ) * BNNDotL233 ) )).xxx;
    float3 temp_output_260_0 = ( max( temp_cast_7 , float3(0,0,0) ) * BNAttenuationColor244 );
    ```
*   **Effect**: 阴影边缘不再是平滑的曲线，而是呈现出被噪点侵蚀、扭曲的形状。这非常适合模拟水彩、油画或粗糙纸张上的颜料扩散效果。
*   **Impact on Shadows**: 可以选择 `_UseDiffuseWarpAsOverlay`，决定这个扭曲是仅影响漫反射本身，还是也影响接收到的阴影形状。

## 2. UV Animation (UV 动画)

Shader 为几乎所有主要的纹理层（Overlay, Specular Mask, Diffuse Warp）提供了统一的 UV 动画支持。

### Features
*   **Scroll (滚动)**: `_UVScrollSpeed`。简单的 `Time * Speed` 偏移。
*   **Rotation (旋转)**: `_UVSrcrollAngle`。通常结合时间变化。
*   **Frame Animation (帧动画)**: 代码中包含 `floor( ( Time % 2.0 ) * 0.5 )` 这样的逻辑，似乎支持简单的 2 帧切换或闪烁效果，模拟低帧率的手绘动画感。
    ```glsl
    float mulTime1278 = _TimeParameters.x * _UVAnimationSpeed;
    float temp_output_1281_0 = ( floor( ( mulTime1278 % 2.0 ) ) * 0.5 );
    ```

## 3. Occlusion (环境光遮蔽)

支持标准的 `_OcclusionMap`。

*   **Logic**:
    ```glsl
    float lerpResult1655 = lerp( 1.0 , tex2D( _OcclusionMap, uv_OcclusionMap ).r , _OcclusionStrength);
    float4 MainTexture364 = ( _Color * tex2DNode362 * appendResult1656 );
    ```
*   AO 直接乘在 Albedo 上（`MainTexture364`），这意味着它会变相加深漫反射颜色，也会影响后续的 Posterize 或 Ramp 计算（因为它改变了底色亮度）。这有助于强调模型凹陷处的结构感。

## 4. Adaptive Screen UVs (自适应屏幕 UV)

在处理屏幕空间纹理（如 Halftone, Hatching）时，Shader 提供了 `_UseAdaptiveScreenUvs` 选项。
*   **问题**: 屏幕空间纹理通常是“贴”在屏幕上的，当物体移动时，纹理就像投影仪一样投在物体上，产生“滑步”现象（Shower Door Effect）。
*   **解决**: 虽然完全解决需要复杂的 Object Space 映射，但 Adaptive UV 尝试通过修正 Tiling 和 Scale (`_MaxScaleDependingOnCamera`) 来缓解透视带来的纹理密度不一致问题。
