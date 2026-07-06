# Post-Processing (后处理)

后处理是营造“动画感”氛围的关键步骤，不仅仅是画面修饰，更是风格化的一部分。

## 1. Bloom (泛光)

卡通渲染的 Bloom 与物理真实的 Bloom 有所不同。物理 Bloom 基于亮度阈值，而卡通 Bloom 往往基于“艺术意图”。

### A. 痛点
*   **物理不兼容**: 为了保持高饱和度，卡通颜色的物理亮度往往不高（不发光），导致无法触发标准的 Bloom。
*   **过曝变白**: 强行提高亮度触发 Bloom 会导致颜色变白（ACES 特性），失去原本的高饱和度色相。

### B. 解决方案
*   **独立 Bloom 系数**: 不依赖 RGB 亮度，而是通过 Alpha 通道（或独立 Buffer）传递一个“Bloom 强度值”。
    *   *原理*: 将 Bloom 强度写入 RT 的 Alpha 通道。Bloom Pass 读取该通道决定发光强度，而非读取 RGB 亮度。
    *   *应用*: 让深色的衣服、不发光的头发也能产生微弱的柔光，增加空气感。
*   **色相偏移**: 在 Bloom 过程中对溢出的光进行色相偏移（如黄色光产生橙色光晕），丰富色彩层次。
*   **半透明处理**: 由于 Alpha 通道可能被占用，半透明物体可能需要单独 Pass 渲染，或在 Bloom 阶段进行特殊合成（如《原神》方案：不透明物体和半透明物体分离渲染，半透明物体不写入 Bloom 系数或单独处理）。

## 2. Tone Mapping (色调映射)

### A. ACES 的问题
标准 ACES 曲线会压低高饱和度颜色的亮度，并将高亮区域映射为白色（Desaturation）。这会导致二次元角色皮肤发灰、头发颜色变淡。

### B. 修正方案
*   **曲线魔改**: 修改 ACES 算法参数，减少对高饱和度颜色的“去色”倾向。
*   **贴图反向补偿**: 使用拟合公式预处理贴图，反向增加饱和度和对比度，以抵消 ACES 的影响。
*   **Gran Turismo 曲线**: 使用对高饱和度更友好的 GT ToneMapping 算法。
*   **关掉它**: 如果场景允许，直接在 LDR 线性空间下工作，完全绕过 Tone Mapping（但会牺牲特效的光感）。

## 3. Anime Effects (动画摄影后期)

模拟日本动画摄影（Compositing）阶段的特效。

### A. Flare (光晕渐变)
*   **效果**: 在屏幕上方叠加一层发光的渐变（通常是加法混合/Additive），模拟顶部光源的溢出。
    ```glsl
    // Simple Top Flare
    float flare = smoothstep(0.5, 1.0, uv.y); // Top of screen
    color += _FlareColor * flare * _FlareIntensity;
    ```
*   **作用**: 增加画面的“空气感”和明亮氛围。

### B. Para (压暗渐变)
*   **效果**: 在屏幕角落或底部叠加深色渐变（乘法混合/Multiply）。
    ```glsl
    // Vignette/Para Logic
    float2 d = abs(uv - 0.5) * _ParaScale;
    float para = smoothstep(0.0, 1.0, length(d));
    color *= lerp(1.0, _ParaColor, para);
    ```
*   **作用**: 压暗边缘，聚焦视线，增加画面厚重感。

### C. 案例
《蓝色协议》大量使用了这种全屏的色彩遮罩（Color Mask）来统一画面色调，使其看起来像经过后期合成的动画片。

## 4. Outline Post-Process (后处理描边)
（详见 [Outlines 章节](02_Outline.md)）

## 5. Ambient Occlusion (环境光遮蔽)
*   **争议**: 传统 SSAO 会产生脏脏的阴影，不符合赛璐璐的干净风格。
*   **改良**: 使用 HBAO+ 并允许设置 AO 颜色（如染成紫色而非黑色），或者仅在场景角落启用 AO（使用 Proxy Mesh 写入 AO Buffer），角色身上禁用或使用手绘 AO 贴图代替。
