# SToon Features

SToon 是一个由 Amplify Shader Editor 生成的 URP 卡通渲染着色器，专注于提供高度风格化的渲染效果，如手绘素描、漫画网点、以及动态描边。

## 1. Core Shading (核心光照)
*   **Light Ramp Modes**:
    *   **Step**: 经典的硬切割色阶。
    *   **Diffuse Ramp**: 使用渐变贴图 (`_LightRampTexture`) 控制明暗过渡。
    *   **Posterize**: 动态色调分离，通过参数控制色阶数量。
*   **Additional Lights**: 支持多光源，且光照计算也是风格化的（Posterized Falloff）。
*   **Shadows**: 支持接收阴影，并可自定义阴影颜色 (`_ShadowColor`)。

## 2. Outline (描边)
*   **Dynamic Sketch Outline**: 独特的动态噪点描边，模拟手绘时线条的抖动感。
*   **Outline Type**: 支持 Normal (法线外扩), Position (顶点位移), UVBaked (烘焙UV) 三种挤出方式。
*   **Noise Control**: 可调节噪点缩放、强度和动画速度 (`_OutlineDynamicSpeed`)。
*   **Adaptive Thickness**: 基于距离的自适应宽度调整。

## 3. Stylized Overlays (风格化覆盖)
*   **Halftone (网点)**:
    *   屏幕空间或 UV 空间的网点覆盖。
    *   支持平滑度 (`_HalftoneSmoothness`) 和阈值控制。
    *   可作为独立的 Overlay 模式叠加在漫反射上。
*   **Hatching (排线)**:
    *   双层纹理 (`_Hatch1`, `_Hatch2`) 用于明暗不同层次的排线。
    *   **Constant Scale**: 支持屏幕空间恒定大小的排线，不随物体远近而缩放。
    *   **Triplanar**: 部分实现支持三向贴图投影（需进一步确认代码）。
*   **Sketch / Paper**:
    *   **Paper Texture**: 叠加纸张纹理，模拟在纸上作画的效果。
    *   **Pure Sketch**: 纯素描模式，去色并强调线条和阴影。

## 4. Specular & Gloss (高光)
*   **Stylized Specular**: 支持色调分离 (Posterize) 的高光衰减。
*   **Specular Mask**: 使用遮罩纹理控制高光形状（如半调网点高光）。
*   **Anisotropic-like**: 支持 UV 旋转 (`_SpecularMaskRotation`) 和滚动，可制作动态高光。

## 5. Rim Light & Backlight (边缘光与背光)
*   **Rim Light**: 基于 Fresnel 的边缘光，支持分裂颜色 (`_RimSplitColor`)。
*   **Backlight**: 模拟背光效果，增强物体轮廓感。
*   **Side Shine**: 侧面光泽，增加体积感。

## 6. Artistic Controls (艺术控制)
*   **Diffuse Warp**: 扭曲漫反射光照，制作不规则的阴影边缘。
*   **UV Animation**: 支持纹理 UV 的自动滚动和旋转。
*   **Occlusion**: 支持 AO 贴图，增强阴影深度。
