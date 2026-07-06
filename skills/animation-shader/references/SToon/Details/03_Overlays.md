# Overlay Features (覆盖特性)

SToon 提供了强大的屏幕空间/UV 空间纹理覆盖功能，主要分为 Halftone (网点) 和 Hatching (排线)。

## 1. Halftone (网点)

网点通常用于模拟漫画印刷效果。

### Logic
*   **UV Calculation**:
    *   **Screen Space**: 默认使用屏幕空间 UV ( `ase_grabScreenPosNorm` )。
    *   **Tiling Correct**: 修正屏幕长宽比，保证网点是圆的而不是拉伸的椭圆。
        ```glsl
        float2 appendResult1849 = (float2(( _OverlayUVTilling * ( _ScreenParams.x / _ScreenParams.y ) ) , _OverlayUVTilling));
        ```
    *   **Rotation**: 支持 UV 旋转。
*   **Application**:
    *   使用 `smoothstep` 根据光照强度和 `_HalftoneThreshold` 来决定网点的显示。
    *   `_HalftoneSmoothness` 控制网点边缘的抗锯齿程度。
    *   **Toon Affect**: `_HalftoneToonAffect` 参数控制网点颜色是使用 `_HalftoneColor` 还是混合主光源颜色。

## 2. Hatching (排线)

排线功能使用了两张贴图 (`_Hatch1`, `_Hatch2`) 来模拟素描的明暗层次。

### Constant Scale Hatching (恒定大小排线)

这是一个非常高级的特性。通常纹理贴在物体上，物体离远了纹理就会变小变密。但在手绘风格中，笔触的大小通常是相对于屏幕固定的（就像你在屏幕上画画一样），无论物体多远，线条粗细应该一致。

Shader 中实现了一个 `HatchingConstantScale491` 函数来解决这个问题：

```glsl
float3 HatchingConstantScale491( float2 _uv, ..., float _dist, float _MaxScaleDependingOnCamera )
{
    // 1. 计算距离的对数 (Log Distance)
    float log2_dist = log2(_dist) - 0.2;
    
    // 2. 计算两个相邻的 Mipmap 级别 (Floored Log)
    // 类似于手动实现 Texture Mipmapping 选择
    float2 floored_log_dist = floor( (log2_dist + float2(0.0, 1.0) ) * 0.5) * 2.0 - float2(0.0, 1.0);
    
    // 3. 计算 UV 缩放因子
    // 随着距离变远 (dist 变大)，uv_scale 变大，使得采样的纹理范围变大，
    // 从而抵消透视带来的缩小效应。
    float2 uv_scale = min(_MaxScaleDependingOnCamera, pow(2.0, floored_log_dist));
    
    // 4. 计算两个级别的混合权重
    float uv_blend = abs(frac(log2_dist * 0.5) * 2.0 - 1.0);
    
    // 5. 两次采样并混合
    // 采样级别 A
    float2 scaledUVA = _uv / uv_scale.x; 
    float3 hatch0A = tex2D(_Hatch0, scaledUVA).rgb;
    // ...
    // 采样级别 B
    float2 scaledUVB = _uv / uv_scale.y;
    float3 hatch0B = tex2D(_Hatch0, scaledUVB).rgb;
    // ...
    
    // 混合结果
    float3 hatch0 = lerp(hatch0A, hatch0B, uv_blend);
    // ...
}
```

*   **原理**: 它实际上是手动实现了一种类似于 Triplanar 或 Texture Streaming 的逻辑，根据摄像机距离动态调整 UV Tiling。
*   **效果**: 无论物体离摄像机多远，排线的密度和笔触大小在屏幕上看起来基本保持一致，非常符合 2D 手绘的视觉习惯。

## 3. Paper Texture (纸张纹理)

在最终输出前，Shader 还会叠加一层纸张纹理。
*   这层纹理通常也是屏幕空间的。
*   它让画面看起来像是画在粗糙的纸上，而不是光滑的显示器上。
