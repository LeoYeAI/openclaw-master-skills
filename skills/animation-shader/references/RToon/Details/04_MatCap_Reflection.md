# MatCap & Reflection (材质捕获与反射)

RToon 提供了强大的 MatCap 功能用于模拟金属光泽，以及一种伪造的环境反射（FReflection）用于风格化。

## 1. MatCap (Material Capture)

### Properties (参数)
*   `_MCap` ("MatCap", 2D): MatCap 纹理。
*   `_MCapIntensity` ("Intensity"): 强度。
*   `_MCapMask` ("Mask"): 遮罩贴图。
*   `_SPECMODE` ("Specular Mode"): **[关键]** 混合模式。
    *   **Off (Mult/Mix)**: MatCap 颜色与 MainColor 混合（正片叠底或加权）。适合模拟整体材质感。
    *   **On (Add)**: MatCap 颜色叠加（Add）。适合模拟高光。
*   `_SPECIN` ("Specular Power"): 仅在 `_SPECMODE` 开启时有效，控制叠加强度。
*   `_MCIALO` ("Main Color In Ambient Light Only"): **[特色]** MatCap 是否在暗部/环境光下也显示。
    *   如果开启，MatCap 不受光照方向产生的阴影遮蔽，始终发亮。适合金属、丝绸等高反射材质。

### Implementation (实现原理)

`RT_MCAP` 和 `RT_MCAP_SUB1` 函数 (`RT_URP_Core.hlsl`)。

```glsl
// 1. 采样 MatCap
half3 RT_MCAP(float2 uv, float3 normalDirection)
{
    // View Space Normal 映射 UV
    half2 MUV = (mul(UNITY_MATRIX_V, float4(normalDirection, 0.0)).xyz.rgb.rg * 0.5 + 0.5);
    half4 _MatCap_var = SAMPLE_TEXTURE2D(_MCap, sampler_MCap, TRANSFORM_TEX(MUV, _MCap));
    
    // 应用遮罩和强度
    // 这里代码逻辑有点绕，似乎还涉及 _SPECMODE 对输出的影响
    float3 MCapOutP = lerp(RT_SPECMO_OO, lerp(RT_SPECMO_OO, _MatCap_var.rgb, _MCapIntensity), _MCapMask_var.rgb);
    return MCapOutP;
}

// 2. 混合到主颜色 (RT_MCAP_SUB1)
half3 RT_MCAP_SUB1(half3 MCapOutP, half4 _MainTex_var, ...)
{
    // 如果 _SPECMODE 开启 (Add模式)
    // RT_SPECMO_OO = (_MainColor * _MaiColPo) + (MCapOutP * _SPECIN); // 叠加公式
    
    // 如果 _SPECMODE 关闭 (Mix模式)
    // RT_SPECMO_OO = (_MainColor * _MaiColPo) * MCapOutP; // 乘法公式
    
    // 最终输出 RTD_TEX_COL
    return RTD_TEX_COL;
}
```

---

## 2. Reflection (反射)

RToon 支持两种反射模式：标准 PBR 反射和伪造反射 (FReflection)。

### A. FReflection (Fake/Fast Reflection)
一种极低成本的风格化反射，不采样 Reflection Probe，而是直接将一张贴图映射到反射向量上。

*   **Properties**:
    *   `_FReflection` ("FReflection", 2D): 反射贴图（通常是全景图或环境图）。
    *   `_ReflectionIntensity`: 反射强度。
    *   `_ReflectionRoughtness`: 模糊度（采样 LOD）。
    *   `_MaskReflection`: 遮罩。

*   **Implementation**:
    ```glsl
    // 计算视线反射向量
    half2 ref_cal = reflect(viewDirection, normalDirection).rg;
    // 映射到 UV (球面映射近似)
    half2 ref_cal_out = (float2(ref_cal.r, (-1.0 * ref_cal.g)) * 0.5 + 0.5);
    // 采样贴图
    half4 _FReflection_var = SAMPLE_TEXTURE2D_LOD(_FReflection, sampler_FReflection, TRANSFORM_TEX(ref_cal_out, _FReflection), _ReflectionRoughtness);
    ```
*   **优点**: 无论场景如何，角色反射始终一致（适合动漫角色的固定画风），且性能极高。

### B. Standard Reflection
*   调用 `GlossyEnvironmentReflection`，采样 Unity 的 Reflection Probe。
*   受 `_RefMetallic` 控制。

---

## 3. Analysis (分析)

*   **二次元金属感**: 推荐使用 `_MCap` + `_MCIALO` (On) + `_SPECMODE` (On)。这样金属部分会有强烈的高光，且不受阴影影响，始终保持闪亮。
*   **固定风格**: `FReflection` 是非常实用的功能。二次元游戏往往希望角色身上的反射是受控的（比如永远反射蓝天白云），而不是反射真实的灰暗场景。
