# Core Shading Logic (核心光照逻辑)

SToon 的光照模型构建在 URP 的标准光照流程之上，但对光照衰减（Attenuation）和漫反射（Diffuse）部分进行了大量的风格化处理。

## 1. Light Ramp Modes (光照渐变模式)

Shader 提供了三种主要的光照模式，通过关键字 `_USELIGHTRAMP_STEP`, `_USELIGHTRAMP_DIFFUSERAMP`, `_USELIGHTRAMP_POSTERIZE` 切换。

### A. Step (硬切割)
这是最简单的 Toon Shading 形式。
*   **逻辑**: 使用 `smoothstep` 对 NdotL (结合 ShadowAttenuation) 进行二值化或硬过渡处理。
*   **代码片段**:
    ```glsl
    // temp_output_1188_0 是 NdotL * Attenuation
    float smoothstepResult444 = smoothstep( ( _StepOffset + 0.5 - 0.009 ) , ( _StepOffset + 0.5 ) , temp_output_1188_0);
    float4 lerpResult1619 = lerp( _ShadowColor , _MainLightColor , saturate( smoothstepResult444 ));
    ```
*   **参数**:
    *   `_StepOffset`: 调整明暗交界线的位置。

### B. Diffuse Ramp (渐变贴图)
使用一张 1D 纹理（通常是 Gradient）来映射光照强度。
*   **逻辑**: 将 NdotL 映射到纹理 UV 的 x 轴。
*   **代码片段**:
    ```glsl
    // appendResult356.x = _LightRampOffset + NdotL
    // clamp 防止采样越界
    float2 clampResult358 = clamp( appendResult356 , 0.01 , 0.98 );
    // 采样 Ramp 贴图
    float4 lerpResult1617 = lerp( tex2D( _LightRampTexture, float2( 0.02,0 ) ) , ( tex2D( _LightRampTexture, clampResult358 ) * _MainLightColor ) , staticSwitch1470);
    ```
*   **优点**: 可以制作丰富多彩的阴影过渡（例如皮肤阴影带点红色）。

### C. Posterize (色调分离)
通过数学计算将连续的光照强度离散化为几个阶梯。
*   **逻辑**:
    ```glsl
    float Posterize1331( float In, float Steps ) {
        return floor(In / (1 / Steps)) * (1 / Steps);
    }
    // ...
    float In1331 = pow( saturate( ( NdotL + ( _DiffusePosterizeOffset * -1.0 ) ) ) , _DiffusePosterizePower );
    float localPosterize1331 = Posterize1331( In1331 , round( _DiffusePosterizeSteps ) );
    ```
*   **参数**:
    *   `_DiffusePosterizeSteps`: 色阶数量（如 3 阶、4 阶）。
    *   `_DiffusePosterizePower`: 伽马校正，控制色阶的分布密度。

## 2. Additional Lights (多光源处理)

额外的点光源/聚光灯也经过了特殊的风格化处理，特别是它们的衰减（Falloff）也可以被 Posterize。

### Implementation
```glsl
float3 AdditionalLight( ... )
{
    // ... 遍历光源 ...
    // 计算 NdotL
    float3 DotVector = dot(light.direction, WorldNormal);
    
    // 计算最大通道强度 (Max Component)
    float maxColor = max(colout.r,max(colout.g,colout.b));
    
    // 平滑阶梯化 (Smoothstep based banding)
    float3 outColor = smoothstep(SMin, SMax, maxColor) * light.color;
    Color += outColor;
}
```
*   这确保了即使是额外的点光源，投射在物体上也不会产生写实的柔和衰减，而是保持卡通的硬边风格。

## 3. Shadows (阴影)

*   **Shadow Color**: 阴影颜色是显式定义的 `_ShadowColor`，而不是简单的变黑。
*   **混合逻辑**:
    ```glsl
    // staticSwitch1470 包含了 ShadowMap 的采样结果和 ShadowStrength
    float4 lerpResult1626 = lerp( _ShadowColor , lerpResult1619 , staticSwitch1470);
    ```
*   这意味着受阴影遮蔽的区域会直接显示 `_ShadowColor`，而不是 `BaseColor * ShadowColor`。这允许美术完全控制阴影区的色相（例如冷暖对比）。
