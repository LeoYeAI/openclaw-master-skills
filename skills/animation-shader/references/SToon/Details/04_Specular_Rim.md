# Specular & Rim Light (高光与边缘光)

## 1. Stylized Specular (风格化高光)

SToon 的高光不仅仅是简单的 Blinn-Phong，它增加了数个控制项来实现卡通感。

### Logic
1.  **Standard Specular Calculation**:
    *   使用 `LightingSpecular` (URP函数) 或手动计算 Blinn-Phong (N dot H)。
    *   `Smoothness` (Glossiness) 控制高光范围。
2.  **Posterized Falloff (阶梯衰减)**:
    *   为了防止高光边缘过于柔和（写实），Shader 对高光强度进行了 Posterize 处理。
    *   函数 `FaloffPosterize`：
        ```glsl
        float FaloffPosterize( float IN, float SpecFaloff, float Steps )
        {
            // 先做一个平滑映射
            float minOut = 0.5 * SpecFaloff - 0.005;
            float faloff = lerp(IN, smoothstep(minOut, 0.5, IN), SpecFaloff);
            
            // 然后进行阶梯化
            if(Steps < 1) return faloff;
            else return floor(faloff / (1 / Steps)) * (1 / Steps);
        }
        ```
    *   **效果**: 高光可以变成一个个同心圆环，或者硬边的光斑。

3.  **Specular Mask (高光遮罩)**:
    *   **Texture**: `_SpecularMaskTexture`。
    *   **Animation**: 支持 UV 旋转 (`_SpecularMaskRotation`) 和滚动。
    *   **Halftone Interaction**: 遮罩本身也可以应用 Halftone 逻辑 (`_HaltonePatternSize`)，让高光内部呈现网点状。

## 2. Rim Light (边缘光)

边缘光用于勾勒物体轮廓，使其从背景中分离出来。

### Split Color Modes (分裂颜色模式)
这是该 Shader 的一个特色，由 `_RimSplitColor` 控制：
1.  **NoSplit**: 使用单一的 `_RimColor`。
2.  **MultiplyWithDiffuse**: `_RimColor * DiffuseColor`。边缘光颜色会受到底色影响，看起来更自然，像透光（Subsurface Scattering）效果。
3.  **UseSecondColor**: 使用 `_RimColor` 和 `_RimShadowColor` 进行混合。
    *   **逻辑**: 根据物体的亮度 (`Luminance(Diffuse)`) 来决定使用哪个颜色。
    *   **应用**: 在亮部边缘显示白色 Rim，在暗部边缘显示蓝色 Rim，增强冷暖对比。

### Backlight & Side Shine
除了标准的 Fresnel Rim，还模拟了特定方向的光照效果：
*   **Backlight**: 模拟光源在物体正后方产生的轮廓光（类似于日食效果）。
*   **Side Shine**: 模拟侧侧光的掠射效果，通常用于增强金属或光滑物体的体积感。
*   **代码**:
    ```glsl
    // 计算视线反方向与主光方向的点积
    float dotResult745 = dot( ( ase_worldViewDir * -1.0 ) , _MainLightPosition.xyz );
    // 结合 Fresnel 使用
    float smoothstepResult759 = smoothstep( _SideShineHardness , 0.5 , ( clampResult753 * FresnelValue738 ));
    ```
