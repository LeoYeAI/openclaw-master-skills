# Specular & Hair (高光)

卡通高光通常是对 PBR 高光或 Blinn-Phong 高光的风格化处理。

## 1. 基础高光 (Basic Specular)

### 风格化处理
*   **硬边化**: 使用 `step` 或 `smoothstep` 将高光计算结果截断，形成边缘清晰的光斑。
    ```glsl
    // Stylized Specular
    float spec = dot(N, H);
    float w = fwidth(spec); // 抗锯齿
    float stylizedSpec = smoothstep(threshold - w, threshold + w, spec);
    ```
*   **Gouraud 高光**: 在顶点着色器中计算高光，产生多边形风格的粗糙高光（如《原神》金属材质），既优化性能又有独特风格。
*   **双层高光**: 叠加一层锐利的硬高光和一层柔和的软高光（或使用多通道 Ramp 叠加），丰富层次。例如，内层高亮，外层一圈溢出的柔光（模拟 Bloom 或清漆散射）。

### 材质表现
*   **金属**: 通常使用高强度、硬边或各向异性的高光。可配合 MatCap 反射增强质感。
*   **丝绸/清漆**: 使用多层高光或 MatCap 模拟清漆涂层（Clear Coat）。能量守恒需注意（虽然卡通渲染常忽略）。
*   **皮肤**: 往往非常微弱或仅在特定区域（鼻尖、唇珠）出现，通常使用 Mask 控制。

## 2. 头发高光 (Hair Highlight / Angel Ring)

头发高光（天使环）是二次元渲染的重点，主要特征是各向异性（Anisotropic）。

### A. Kajiya-Kay 各向异性 (Anisotropic)
*   **原理**: 基于切线（Tangent）而非单纯法线计算高光，模拟发丝的光照反应。
    ```glsl
    // Kajiya-Kay Logic
    float3 T = normalize(i.tangent); // 也就是发丝方向
    float dotTH = dot(T, H);
    float sinTH = sqrt(1 - dotTH * dotTH);
    float spec = pow(sinTH, exponent);
    ```
*   **卡通化**: 结合 **Jitter Map**（抖动图/偏移贴图）偏移切线，形成参差不齐的“W”形高光带。
    ```glsl
    float shift = tex2D(_JitterMap, uv).r;
    T = ShiftTangent(T, N, shift); // 偏移切线
    ```
*   **优点**: 物理基础，随光照动态移动。
*   **缺点**: 容易显得“油腻”，对 UV 展开（需拉直）要求高。

### B. MatCap 伪高光
*   **原理**: 使用 View-Space 法线采样 MatCap 贴图（通常是一张画好的高光条）。
*   **优点**: 形状自由，可绘制定制形状。
*   **缺点**: 视角固定时高光位置不动，缺乏立体感。适合披肩长发，不适合刺猬头。

### C. 投影/UV 偏移方案 (Projection)
*   **原理**: 如 UTS2 的天使环，基于视口法线投影纹理。
*   **UV 偏移**: 通过控制 UV 坐标的上下移动来模拟高光的动态位置（如《樱花大战》）。UV 排列需整齐。

### D. 缩放方案 (Scaling)
*   **原理**: 《蓝色协议》方案。高光位置固定（画在贴图上或用 UV2 指定重心），但根据视距和角度动态缩放高光点的大小，避免远距离时的噪点和近距离的模糊。是一种“反向高光”思路（中心弱边缘强）。

### E. 形状控制
*   **反向高光**: 经典高光是中心强，有些画风（如《原神》）的高光是两头强中间弱。
*   **Mask 控制**: 使用 Mask 贴图强行限制高光出现的区域，防止在头顶等奇怪位置出现高光圈（Halo Artifact）。
