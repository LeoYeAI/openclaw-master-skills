# PBR & Painting Styles (PBR与绘画风)

随着技术发展，卡通渲染不再局限于传统的赛璐璐（Cel-Shading），而是开始融合 PBR（基于物理的渲染）以获得更丰富的材质质感，或追求手绘插画般的艺术效果。

## 1. PBR Integration (PBR 结合)

### 融合策略
1.  **降色阶 PBR (Banded PBR)**:
    *   直接使用 PBR 光照模型，但对最终的光照结果进行离散化（Step/Floor）。
    *   **案例**: 《重力眩晕》。缺点是可能显得“油腻”或“脏”，金属感不足。
2.  **写实手办风**:
    *   保留 PBR 的大部分特性（GGX 高光、IBL），仅对漫反射暗部做风格化调色。
    *   **案例**: 《闪耀暖暖》。
3.  **区域混合 (Zone-based Mixing)**:
    *   使用 Mask 贴图区分“卡通区”（皮肤、布料）和“PBR区”（金属、皮革）。
    *   卡通区使用 Ramp Shading，PBR 区使用 Standard Shading。
    *   **混合过渡**: 可以不完全切变，而是按权重混合两种光照结果，避免割裂感。例如，PBR 区域叠加一层卡通边缘光，或卡通区域叠加一层微弱的 PBR 反射。
4.  **魔改 PBR (Modified PBR)**:
    *   在 PBR 流程中插入 Ramp 映射。例如，将 Diffuse Term 中的 NdotL 替换为 Ramp 采样，但保留 Specular Term (GGX) 和 Indirect Specular (IBL)。
    *   **ShaderGraph 思路**: 修改 PBR Master Node 前的计算，将自定义的 Ramp 漫反射作为 Emission 输入，或修改底层光照函数。

### 关键技术点
*   **ACES 色调映射修正**: HDR 流程下的 ToneMapping 会导致色彩灰暗，不符合二次元的高饱和度审美。
    *   **反向补偿公式**: 拟合 ACES 的逆运算，预处理贴图颜色。
        $$ color = 3.4475 * color^3 - 2.7866 * color^2 + 1.2281 * color - 0.0056 $$
*   **环境反射解绑**: 为了风格化，角色的反射贴图（Reflection Probe）往往不使用真实的场景反射，而是使用定制的、简化的 Cubemap 或 MatCap，以保证画面干净。

## 2. Painting Styles (绘画风格化)

除了追求物理质感，另一种方向是极致的艺术化（NPR），模拟手绘笔触。

### A. 笔触纹理 (Brush Strokes)
*   **原理**: 使用多通道纹理存储不同方向的笔触图案。在光照过渡区（明暗交界处）采样这些笔触，打破平滑的渐变，模拟笔刷涂抹感。
*   **实现**: `Ramp + BrushMap`。根据光照强度选择不同的笔触通道混合。

### B. 素描与排线 (Hatching / Pencil Sketch)
*   **原理**: 使用一组 Tonal Art Maps (TAM)，分别代表不同密度的排线（6张或合并通道）。根据光照强度混合不同密度的纹理。
*   **注意**: 纹理必须对齐且具备包含关系（深色纹理应包含浅色纹理的笔触），否则动态变化时会闪烁。

### C. 油画与滤波 (Oil Painting / Filtering)
*   **Kuwahara Filter / SNN Filter**: 
    *   屏幕后处理滤镜，用于“涂抹”画面，去除高频噪点，产生类似油画的色块感。
    *   **SNN (Symmetric Nearest Neighbor)**: 对称近邻平滑滤波，保留边缘的同时平滑色块。
    *   **Kuwahara Logic**:
        ```glsl
        // Divide window into 4 subregions
        // Calculate mean and variance for each subregion
        // Output the mean of the subregion with the minimum variance
        float3 mean[4]; float3 var[4];
        // ... (Loop to calculate mean/var for 4 quadrants) ...
        // Find min variance
        float3 col = mean[min_var_index];
        ```
    *   **案例**: 《蓝色协议》、《破晓传说》用于背景渲染，使场景像手绘背景图一样。通常会把角色排除在滤镜之外以保持清晰（使用 Stencil 区分）。

### D. 漫画网点 (Halftone)
*   **原理**: 在屏幕空间生成网点图案（如圆形、方形），根据亮度控制网点大小或密度。常用于美漫风格或特殊过场（如《蜘蛛侠：平行宇宙》）。

## 3. Material Analysis (材质分析思路)

在做风格化材质时，应先分析原画意图，再拆解技术实现：

*   **金属**: 高对比度、锐利高光（Gouraud或各向异性）、MatCap 反射、边缘压暗。
*   **丝绸**: 各向异性高光、双层高光（底色+反光色）、菲涅尔边缘光。
*   **皮肤**: 次表面散射（Ramp图高饱和度交界线）、弱高光、AO 遮蔽、脸部SDF。
*   **丝袜**: 边缘强反射（菲涅尔），正面透肉色（漫反射），高光锐利。
*   **毛衣/编织物**: 使用 Substance Designer 生成高精度法线和 AO，模拟编织纹理。

利用 **Substance Designer** 等工具程序化生成风格化纹理是提升精度的关键。
