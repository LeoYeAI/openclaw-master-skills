# Core Shading (核心光照)

RToon 的核心光照模型主要由 "Self Shadow" (自阴影/二值化光照) 和 "Smooth Object Normal" (平滑法线) 组成。

## 1. Self Shadow (自阴影)

这是 RToon 实现赛璐璐风格（Cel-Shading）的基础。它不依赖贴图 Ramp，而是通过计算 NdotL 并进行阈值切割来生成硬边阴影。

### Properties (参数)
*   `_SelfShadowThreshold` ("Threshold", Range(0, 1)): 决定亮部和暗部的分界线。值越大，阴影区域越大。
*   `_SelfShadowHardness` ("Hardness", Range(0, 1)): 控制阴影边缘的软硬度。1.0 为绝对硬边，0.0 为非常柔和。
*   `_SelfShadowRealtimeShadowIntensity`: 控制实时投影（ShadowMap）对自阴影的影响程度。
*   `_SelfShadowAffectedByLightShadowStrength`: 自阴影是否受光源的 Shadow Strength 属性影响。
*   `_VertexColorGreenControlSelfShadowThreshold`: **[重要]** 使用顶点色的**绿色通道**来局部控制阴影阈值。
    *   *原理*: 绿色通道值会偏移全局的 Threshold。
    *   *应用*: 让某些部位（如脖子、腋下）更容易产生阴影，或让脸部更不容易产生阴影。

### Implementation (实现原理)

在 `RT_URP_Core.hlsl` 中的 `RT_SS` 函数实现：

```glsl
// RT_SS Function Analysis
half RT_SS(float4 vertexColor, float3 RTD_NDOTL, half attenuation, float dim_val)
{
    // 1. 硬度重映射: 将 0-1 的硬度参数映射到 smoothstep 的下限范围
    half RTD_SS_SSH_Sil = lerp(0.3, 1.0, _SelfShadowHardness);
    
    // 2. 阈值重映射: 将 0-1 的阈值参数映射到 -1 到 1 的范围 (用于偏移 NdotL)
    half RTD_SS_SSTH_Sli = lerp(-1.0, 1.0, _SelfShadowThreshold);

    // 3. 顶点色控制: 如果开启，顶点色绿色通道会改变阈值
    half RTD_SS_VCGCSSS_OO;
    if (!_VertexColorGreenControlSelfShadowThreshold) {
        RTD_SS_VCGCSSS_OO = RTD_SS_SSTH_Sli;
    } else {
        // 绿色通道值越小，阈值越低？这里逻辑是乘法混合
        RTD_SS_VCGCSSS_OO = RTD_SS_SSTH_Sli * (1.0 - vertexColor.g);
    }

    // 4. 核心计算: Smoothstep(min, 1.0, NdotL * ThresholdFactor)
    // 这里并没有直接比较 NdotL > Threshold，而是通过乘法缩放 NdotL 然后用 smoothstep 切割
    half RTD_SS_SST = smoothstep(RTD_SS_SSH_Sil, 1.0, ((float)RTD_NDOTL * lerp(7.0, RTD_SS_VCGCSSS_OO, RTD_SS_SSTH_Sli)));
    
    // 5. 结合光照衰减 (Attenuation / ShadowMap)
    // dim_val 通常来自 _MainLightShadowData.x
    half RTD_SS_SSABLSS_OO = lerp(RTD_SS_SST, lerp(RTD_SS_SST, 1.0, (1.0 - dim_val)), _SelfShadowAffectedByLightShadowStrength);
    
    // 6. 最终输出
    half RTD_SS_ON = lerp(1.0, (RTD_SS_SSABLSS_OO * attenuation), _SelfShadowRealtimeShadowIntensity);

    return RTD_SS_ON;
}
```

### Analysis (分析)
*   **非标准 Ramp**: RToon 没有使用传统的 `tex2D(_RampTex, NdotL)` 采样，而是使用数学公式计算。
*   **优点**: 省去了一张贴图采样，性能稍好，且参数调整更直观。
*   **缺点**: 无法做复杂的色彩渐变（如明暗交界处的红色散射线），只能做纯粹的明暗过渡。

---

## 2. Smooth Object Normal (平滑法线)

用于解决低模（Low Poly）角色面部或身体上的丑陋阴影块。

### Properties (参数)
*   `_SmoothObjectNormal` ("Smooth Object Normal", Range(0, 1)): 混合权重。0 为使用原始法线，1 为使用平滑法线。
*   `_VertexColorRedControlSmoothObjectNormal`: **[重要]** 使用顶点色的**红色通道**控制平滑程度。
*   `_XYZPosition`: 可以微调计算平滑法线时的中心点偏移。

### Implementation (实现原理)

RToon 在 Vertex Shader 中通过算法实时计算一个近似的平滑法线，或者通过混合法线来实现。

在 `RT_URP_Core.hlsl` 中的 `calcNorm` 函数（用于计算平滑法线）和 `RT_SON` 函数：

```glsl
// 1. 计算近似平滑法线 (在 Vertex Shader 中可能被调用)
// 这是一个非常简化的算法，实际上是基于位置的叉积，模拟球形法线
float3 calcNorm(float3 pos)
{
    float3 vecTan = normalize(cross(pos, float3(1.01, 1.0, 1.0)));
    float3 vecBitan = normalize(cross(vecTan, pos));
    return normalize(cross(vecTan, vecBitan));
}

// 2. 混合逻辑 (RT_SON)
float3 RT_SON(float4 vertexColor, float3 calNorm, float3 normalDirection, out float3 RTD_SON_CHE_1)
{
    // 计算混合权重
    float RTD_SON_VCBCSON_OO;
    if (!_VertexColorRedControlSmoothObjectNormal) {
        RTD_SON_VCBCSON_OO = _SmoothObjectNormal;
    } else {
        RTD_SON_VCBCSON_OO = _SmoothObjectNormal * (1.0 - vertexColor.r);
    }

    // 混合原始法线 (normalDirection) 和 计算出的/传入的平滑法线 (calNorm)
    // TransformObjectToWorldNormal(-calNorm) 说明 calNorm 可能是模型空间的
    float3 RTD_SON_ON_OTHERS = lerp(normalDirection, TransformObjectToWorldNormal(-calNorm), RTD_SON_VCBCSON_OO);

    // 返回最终用于光照计算的法线
    return RTD_SON_ON_OTHERS;
}
```

### Analysis (分析)
*   **用途**: 在不修改模型几何体的情况下，让角色的脸部阴影看起来像是一个圆润的球体，消除棱角分明的三角面阴影。
*   **限制**: `calcNorm` 算法是一种近似（基于位置向量），假设物体中心在原点或通过 `_XYZPosition` 修正。对于形状复杂的非球体物体，效果可能不理想。建议仅在脸部等接近球体的区域使用顶点色开启此功能。
