# Advanced Features (高级功能)

RToon 在 V5 版本中引入了一些针对现代 Unity 渲染管线的高级特性。

## 1. DOTS & GPU Skinning (ECS 支持)

RToon 显式支持 Unity 的 DOTS (Data-Oriented Technology Stack) 实例化和蒙皮，这在第三方 Toon Shader 中比较少见。

### Implementation Logic
在 `D_Default_URP.shader` 和 `RT_URP_Core.hlsl` 中：

```glsl
// 宏定义检查
#if defined(UNITY_DOTS_INSTANCING_ENABLED)
    // 定义 DOTS 所需的属性 (Weights, Indices)
    float4 weights : BLENDWEIGHTS;
    uint4 indices : BLENDINDICES;
#endif

// 顶点变换函数 (DOTS_LiBleSki)
void DOTS_LiBleSki(uint4 indices, float4 weights, float3 positionIn, float3 normalIn, float3 tangentIn, out float3 positionOut, out float3 normalOut, out float3 tangentOut)
{
    // 从 StructuredBuffer 读取骨骼矩阵
    // _SkinMatrices 是全局计算缓冲区
    for (int i = 0; i < 4; ++i)
    {
        float3x4 skinMatrix = _SkinMatrices[indices[i] + asint(UNITY_ACCESS_HYBRID_INSTANCED_PROP(_SkinMatrixIndex, float))];
        // ... 矩阵变换 ...
        positionOut += vtransformed * weights[i];
        // ...
    }
}
```
*   **意义**: 允许在大规模战斗场景中渲染成千上万个带动画的卡通角色，且保持高性能（GPU Skinning + Instancing）。

## 2. Triplanar Mapping (三向贴图)

通过开启 `N_F_TP_ON` 宏，所有主要贴图（MainTex, ShadowT, Mask, etc.）的采样方式会从 UV 采样变为 Triplanar 采样。

### Implementation
```glsl
half4 RT_Tripl_Default(TEXTURE2D_PARAM(tex, samp), float3 positionWS, float3 normalWS)
{
    float3 UV = positionWS * _TriPlaTile; // 世界坐标作为 UV
    float3 Blend = pow(abs(normalWS), _TriPlaBlend); // 基于法线计算混合权重
    Blend /= dot(Blend, 1.0); // 归一化
    
    // 三次采样
    float4 X = SAMPLE_TEXTURE2D_LOD(tex, samp, UV.zy, 0.0);
    float4 Y = SAMPLE_TEXTURE2D_LOD(tex, samp, UV.xz, 0.0);
    float4 Z = SAMPLE_TEXTURE2D_LOD(tex, samp, UV.xy, 0.0);

    return X * Blend.x + Y * Blend.y + Z * Blend.z;
}
```
*   **用途**: 适用于地形、甚至不需要展 UV 的程序化场景物体。但在角色渲染中较少使用（因为 UV 更好控制），除非是像史莱ム或元素生物这样的无定形物体。

## 3. Near Fade Dithering (近距离抖动消隐)

防止摄像机穿模时看到模型内部。当相机非常靠近物体时，使用 Dither Pattern 逐渐透明化物体。

### Properties
*   `_MinFadDistance`: 开始消隐的距离。
*   `_MaxFadDistance`: 完全消失的距离。

### Implementation (RT_NFD)
```glsl
void RT_NFD(float2 positionCS)
{
    float distanceFromCamera = distance(...);
    // 比较 Dither 矩阵值和距离系数
    clip(-(RT_Dither_Out(positionCS) - saturate((distanceFromCamera - _MinFadDistance) / _MaxFadDistance)));
}
```
*   **原理**: 利用 4x4 的 Bayer Dither 矩阵 (`RT_Dither_Out`) 生成有序噪点，在 clip 阶段丢弃像素。

## 4. Cutout Glow (辉光边缘)

为 Cutout (Alpha Test) 材质的边缘增加发光效果。

### Implementation
```glsl
// 计算边缘区域
half _Glow_Edge_Width_Add_Input_Value = ((1.0 - _Glow_Edge_Width) + RTD_CO); // RTD_CO 是 Alpha 值
// ... Remapping ...
half3 _Final_Output = (_Pre_Output * lerp(0.0, _Glow_Color.rgb, saturate(_Cutout * 200.0)));
```
*   **用途**: 科技感全息投影、被烧毁的纸张边缘、能量护盾等。
