# Diffuse Shading (漫反射)

漫反射处理是卡通渲染的核心，主要目标是将传统的光照过渡进行离散化和风格化。

## 1. 基础漫反射 (Basic Diffuse)

### 梯度漫反射 (Banded Shading)
将传统的 `dot(N, L)` 结果通过 `floor` 或 `step` 函数进行分层。
*   **硬切**: 直接二分或多分，形成硬边。
    ```glsl
    // Banded Lighting
    float NL = saturate(dot(N, L));
    float BandedStep = 6;
    float BandedNL = floor(NL * BandedStep) / BandedStep;
    ```
*   **柔化 (Smooth)**: 使用 `smoothstep` 在明暗交界处产生一段过渡区域，避免完全的硬边锯齿，模拟赛璐璐动画中的笔触模糊。
    ```glsl
    // Smooth Banded
    float ramp = smoothstep(threshold - smooth, threshold + smooth, NL);
    ```
    *   **InverseLerp**: 也可使用线性插值代替 `smoothstep` 节省性能。

### Ramp 贴图映射 (Ramp Texture)
使用 `Half-Lambert` (0.5 * dot(N, L) + 0.5) 作为 UV 坐标对 Ramp 贴图进行采样。
*   **代码示例**:
    ```glsl
    fixed halfLambert = 0.5 * dot(lightDir, worldNormal) + 0.5;
    fixed3 diffuseColor = tex2D(_RampTex, fixed2(halfLambert, halfLambert)).rgb;
    ```
*   **优点**: 美术可自由控制明暗交界处的颜色变化（如在交界处加入高饱和度的“SS散射”色，模拟皮肤透光）。
*   **Wrap Mode**: 建议使用 `Clamp` 以防止采样错误。
*   **多维 Ramp (2D Ramp)**: 使用 Y 轴控制阴影软硬度或不同材质的阴影色调。例如，Y轴可以是曲率、厚度、或者视线角度（模拟菲涅尔）。

## 2. 暗部色彩设计 (Shadow Color Design)
*   **冷暖对比**: 遵循“亮暖暗冷”的美术规律。
*   **色调分离**:
    *   **Mask控制**: 使用 Mask 贴图或顶点色控制不同区域（皮肤、衣服）的暗部颜色倾向。
    *   **图层混合**: 不仅仅是正片叠底（Multiply），可以根据固有色的明度选择柔光（Soft Light）等混合模式，避免暗部死黑（参考《火影忍者究极风暴》方案）。
        ```glsl
        // Soft Light Blending Formula
        // Base: Texture Color, Blend: Shadow Tint
        float3 SoftLight(float3 base, float3 blend) {
            return (blend < 0.5) ? 
                (2.0 * base * blend + base * (1.0 - 2.0 * blend)) : 
                (sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend));
        }
        ```
*   **环境融合**: 将环境光颜色（Ambient）与漫反射结果混合。可以按漫反射色阶分别指定叠加的全局环境色，实现角色与场景的动态融合。

## 3. 面部漫反射 (Face Shading)

面部结构复杂，法线敏感，容易产生难看的阴影（如“三角区”问题）。

### A. 法线修正 (Normal Editing)
*   **原理**: 修改面部顶点法线，使其趋向平滑（如传递球体法线），或手动调整特定区域（眼下、鼻侧）的法线以形成完美的“伦勃朗光”三角区。
*   **球体传递**: 创建一个包裹头部的球体，将球体法线传递给面部顶点。
*   **缺点**: 表情动画可能导致修正后的法线崩坏。

### B. SDF 面部阴影 (Face SDF)
*   **原理**: 也就是《原神》方案。美术绘制不同光照角度下的理想阴影 Mask（如0°、45°、90°），生成 SDF（有向距离场）图。运行时根据水平光照角度插值采样 SDF 图。
*   **SDF 生成**:
    *   **帧间插值**: 绘制关键角度，算法生成中间过渡。
    *   **等高线填充**: 利用 CSP 等工具填充等高线生成 SDF。
    *   **Substance Designer**: 程序化生成。
*   **算法逻辑**:
    ```glsl
    // 简化逻辑
    float ctrl = 1 - clamp(0, 1, dot(Front, LightDir) * 0.5 + 0.5); // 计算水平光照角度
    float ilm = tex2D(_IlmTex, uv).r; // 采样SDF图
    float isShadow = step(ilm, ctrl); // 比较生成阴影
    ```
*   **优点**: 阴影形状完美可控，不受模型拓扑限制。
*   **缺点**: 制作流程复杂，通常只支持左右水平旋转的光照变化。

### C. 顶点色 / Mask 控制
利用顶点色通道作为 Mask，类似于 AO，控制面部阴影的阈值（如让鼻子区域更容易变暗，脸颊区域更不容易变暗，形成特定形状的阴影）。

### D. 其它技巧
*   **固定光照**: 在选人界面或特定情境下，固定光照方向相对于相机的位置（如始终偏向相机左上方），保证永远展示最好看的一面。
*   **MatCap**: 使用 MatCap 贴图直接映射光影（适用于固定视角的过场动画，如《七大罪》方案）。
