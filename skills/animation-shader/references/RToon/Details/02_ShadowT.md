# ShadowT (Shadow Texture / 阴影纹理)

ShadowT 是 RToon 的特色功能，全称可能是 Shadow Texture 或 Shadow Tone。它允许在阴影区域叠加一层纹理，用于实现漫画网点（Halftone）、排线（Hatching）或特定的风格化纹理。

## 1. Properties (参数)

*   `_ShadowT` ("ShadowT", 2D): 阴影区域显示的纹理贴图。
*   `_ShadowTIntensity` ("Intensity", Range(0, 1)): 纹理的强度/不透明度。
*   `_ShadowTColor` ("Color", Color): 纹理的颜色叠加。
*   `_ShadowTLightThreshold` ("Light Threshold"): 控制纹理在光照过渡区域的显示范围。
*   `_ShadowTShadowThreshold` ("Shadow Threshold"): 控制纹理在阴影深处的显示范围。
*   `_ShadowTHardness` ("Hardness"): 纹理显示的边缘硬度。
*   `_ShowInAmbientLightShadowIntensity` ("Show In Ambient Light"): **[特色]** 允许纹理在环境光（非直射光）下依然可见。这对于保持角色身上的固有风格纹理（如布料纹理）非常重要。

## 2. Implementation (实现原理)

位于 `RT_URP_Core.hlsl` 中的 `RT_ST` 函数。

### 核心逻辑

ShadowT 的计算依赖于光照强度 (`attenuation`, `NdotL`) 和环境光。

```glsl
half RT_ST(float2 uv, float3 positionWS, float3 normalDirection, half RTD_NDOTL, half attenuation, ...)
{
    // 1. 采样贴图
    float4 _ShadowT_var = SAMPLE_TEXTURE2D(_ShadowT, sampler_ShadowT, TRANSFORM_TEX(uv, _ShadowT));
    
    // 2. 环境光下的显示逻辑
    // 如果开启 _ShowInAmbientLightShadowIntensity，即使没有直射光阴影，纹理也会基于环境光强度显示
    half RTD_ST_IS_ON = smoothstep(hardness, 0.22, (_ShowInAmbientLightShadowThreshold * _ShadowT_var.rgb));
    
    // 3. 阴影区域蒙版计算
    // 结合 NdotL 和 Attenuation (LightFalloff)
    half RT_LFOAST_OO = attenuation * RTD_NDOTL; // 光照强度因子
    
    // 核心公式: 根据光照强度决定纹理可见性
    // 这里的逻辑比较复杂，本质是：当光照变弱时，混合进 ShadowT 纹理
    half RTD_ST_In_Sli = lerp(1.0, 
        smoothstep(hardness, 0.22, 
            ((_ShadowT_var.r * (1.0 - _ShadowTShadowThreshold)) * (RT_LFOAST_OO * _ShadowTLightThreshold * 0.01))
        ), 
        _ShadowTIntensity);
        
    return RTD_ST_In_Sli;
}
```

## 3. Usage & Analysis (分析与用法)

### 典型用法
1.  **漫画网点 (Halftone)**: 
    *   将 `_ShadowT` 设为网点平铺贴图。
    *   调整 `_ShadowTLightThreshold` 使其仅在明暗交界处出现，或覆盖整个暗部。
2.  **手绘排线 (Hatching)**:
    *   使用排线纹理。
    *   配合 `_ShadowTHardness` 制作柔和的素描感。
3.  **暗部细节**:
    *   有些美术风格要求暗部不要死黑，而是有纹理细节（如衣服织物感）。
    *   通过 `_ShadowTColor` 提亮暗部并叠加纹理。

### 与 Self Shadow 的区别
*   **Self Shadow**: 决定了**哪里是阴影**（宏观的明暗形状）。
*   **ShadowT**: 决定了**阴影里长什么样**（微观的纹理填充）。
*   两者通常结合使用：Self Shadow 切出阴影块，ShadowT 填充阴影块。
