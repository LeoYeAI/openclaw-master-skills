# Gloss & Rim Light (高光与边缘光)

## 1. Gloss (高光/Specular)

RToon 提供了传统的高光计算和基于纹理的艺术化高光。

### Properties (参数)
*   `_GlossIntensity` ("Intensity"): 整体强度。
*   `_Glossiness` ("Glossiness"): 高光范围/聚焦度（类似 Smoothness）。
*   `_GlossSoftness` ("Softness"): 高光边缘的柔和度（0=硬边）。
*   `_GlossColor`: 高光颜色。
*   `_MaskGloss`: 高光遮罩。

### Texture Based Gloss (纹理高光)
当开启 `_GlossTexture` 时，高光不再只是光斑，而是一个纹理图案。
*   `_GlossTextureSoftness`: 纹理采样的 LOD 偏移（模糊）。
*   **三种模式**:
    1.  **Follow Light (`_GlossTextureFollowLight`)**:
        *   纹理基于 `HalfDirection` (半角向量) 采样。
        *   效果：高光纹理会随着光照移动，类似传统高光，但形状是自定义的（如窗户倒影、特殊的星星形状）。
    2.  **Follow Object (`_GlossTextureFollowObjectRotation`)**:
        *   纹理基于 `mul(unity_WorldToObject, reflectDir)`。
        *   效果：高光像是“画”在物体表面的，随物体旋转，类似 MatCap 但只在高光区出现。
    3.  **Rotate (`_GlossTextureRotate`)**:
        *   纹理自身旋转。适合做魔法效果或流动的光泽。

### Implementation (RT_GLO)
```glsl
// 传统高光 (Blinn-Phong 变体)
half RTD_NDOTH = saturate(dot(halfDirection, normalDirection));
// 使用 smoothstep 切割高光边缘，实现卡通硬高光
half RTD_GLO_MAIN = smoothstep(0.1, RTD_GLO_MAIN_Sof_Sli, pow(RTD_NDOTH, exp2(lerp(-2.0, 15.0, _Glossiness))));

// 纹理高光逻辑
half3 RTD_GT_FL_Sli;
if (!_GlossTextureFollowLight) {
    RTD_GT_FL_Sli = viewDirection; // ? 这里的逻辑似乎是 ViewReflect
} else {
    RTD_GT_FL_Sli = halfDirection;
}
half3 RefGlo = reflect(RTD_GT_FL_Sli, normalDirection);
// ... 采样贴图 ...
```

---

## 2. Rim Light (边缘光)

### Properties (参数)
*   `_RimLigInt` ("Intensity"): 强度。
*   `_RimLightUnfill` ("Unfill"): **[特色]** 控制 Rim Light 向内填充的程度（Fresnel 指数的倒数或类似）。值越大，边缘光越窄。
*   `_RimLightSoftness` ("Softness"): 边缘光的羽化程度。
*   `_RimLightInLight` ("In Light"): 是否允许边缘光出现在受光面。
    *   **Off**: 仅在暗部出现（常用做法，模拟逆光）。
    *   **On**: 亮部暗部都有（类似光环）。
*   `_LightAffectRimLightColor`: 是否受主光颜色影响。

### Implementation (RT_RL)
```glsl
half RT_RL(..., out half RTD_RL_MAIN)
{
    // 计算 Fresnel: 1 - dot(N, V)
    // pow(abs(...), (1.0 - _RimLightUnfill)) : 控制宽窄
    // smoothstep(..., softness, ...) : 控制硬边
    RTD_RL_MAIN = lerp(0.0, 1.0, smoothstep(1.71, RTD_RL_S_Sli, pow(abs(1.0 - max(0, dot(normalDirection, viewDirection))), (1.0 - _RimLightUnfill))));
    
    return RTD_RL_MAIN;
}
```

### Analysis (分析)
*   **硬边边缘光**: 通过 `smoothstep` 处理 Fresnel 结果，RToon 可以产生非常锐利的边缘光，符合赛璐璐风格。
*   **Unfill 参数**: 这个命名比较独特，实际上调节的是 Fresnel 曲线的指数，决定了边缘光是仅仅只有一条细线，还是覆盖到了模型表面。
