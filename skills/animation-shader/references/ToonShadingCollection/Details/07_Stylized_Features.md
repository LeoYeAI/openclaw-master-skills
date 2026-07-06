# Special Features & Materials (特殊部位与材质)

## 1. Stylized Face (面部特殊处理)

### A. 面部三角光 (Nose Triangle Light)
有些二次元画风会在鼻梁侧面加一道不科学的三角形高光，以强调鼻子的立体感。
*   **实现**: 使用一张专门的 Mask 配合高敏感度的菲涅尔（Fresnel）计算，当脸稍侧过去时出现高光。
    *   *原理*: 检测视线与面部朝向的夹角，在特定角度范围触发高光。
    ```glsl
    // 简化的三角光逻辑
    float faceDot = dot(normalize(HeadRightVector), viewDir); // 头部右向量点乘视线
    float triangleIntensity = smoothstep(0.4, 0.5, faceDot); // 当侧脸角度达到一定阈值
    float mask = tex2D(_FaceMap, uv).g; // 只有在鼻梁区域(G通道)生效
    float finalTriangle = triangleIntensity * mask;
    ```

### B. 面部高光与油光 (Face Highlight)
*   **争议**: 给脸部（颧骨、鼻尖）加高光容易显得“油腻”。
*   **推荐做法**: 仅在嘴唇（唇珠）和鼻尖点缀微弱高光。也可使用 MatCap 或 SDF 方案制作动态形状的高光。
*   **红晕 (Blush)**: 静态画在贴图上，或使用独立 Mask 通道动态控制强度（害羞/醉酒）。

### C. 颈部阴影 (Neck Shadow)
*   **问题**: 头部对脖子的投影很难完美，容易出现漏光或形状丑陋。
*   **方案**:
    *   **阴影贴图**: 直接在脖子贴图上画死阴影。
    *   **模型法线**: 调整脖子法线，使其更容易处于阴影中。
    *   **固定投影 (Cylinder Shadow)**: 如《战双》方案，头部产生一个简化的圆柱体阴影投射到脖子上。

## 2. Stylized Eyes (风格化眼睛)

眼睛是二次元角色的灵魂，结构和渲染方式非常多样。

### A. 建模结构
1.  **内凹式 (Concave)**: 瞳孔和虹膜向内凹陷。这是最常见的卡通做法，自带“追眼”效果（Parallax 视差错觉）。
2.  **外凸式 (Convex)**: 像真实眼球一样外凸，适合做高光反射，但需要视差贴图来模拟瞳孔深度。
3.  **复合式 (Composite)**: 如《新樱花大战》，外层是透明角膜（凸），内层是虹膜（凹），效果最精致但性能开销大。

### B. 渲染细节
*   **折射 (Refraction)**: 模拟角膜对瞳孔的折射。
    *   **Parallax Offset (视差偏移)**:
        ```glsl
        float2 offset = height * viewDirTangent.xy;
        offset.y = -offset.y;
        uv -= parallaxScale * offset;
        ```
    *   **Physically Based**: 计算折射向量 `refractedW`，根据前房深度 `height` 计算 UV 偏移。
*   **焦散 (Caustics)**: 在虹膜下方添加亮斑，模拟光线聚焦。使用 `Inverse Diffuse` 模拟，配合 Fresnel 亮度变化。
*   **动态高光**:
    *   **抖动**: 即使身体不动，眼球高光也应有微小的噪点抖动。
    *   **流光 (Flipbook)**: 使用序列帧动画表现眼里的“星星”或情绪变化。
*   **环境反射**: 使用 MatCap 给眼睛增加一层环境光泽，可配合球形法线修正。

### C. 透视眼 (Eyebrows through Hair)
当头发遮挡眼睛时，二次元通常要求眼睛能“透”出来。
1.  **Stencil 法 (模板测试)**:
    *   *Mask Pass*: 绘制眉毛/眼睛，写入 Stencil Ref (e.g., 1).
    *   *Hair Pass*: 绘制头发，`Stencil { Ref 1 Comp NotEqual }`。如果 Stencil 为 1，则丢弃头发片元（或绘制半透明头发）。
2.  **深度测试法 (Z-Test)**: 强制在头发之后再绘制一次眉毛/眼睛，使用 `ZTest Always` 或 `ZTest Greater`。
3.  **透明度排序**: 较难控制，容易出现排序错误。

## 3. Other Parts (其它部位)

### A. 丝袜渲染
*   **特征**: 边缘反光强（菲涅尔），中间透出肤色，高光锐利。
*   **实现**: 混合肤色贴图和丝袜贴图，Fresnel 越强的地方丝袜色越重，Fresnel 越弱的地方肤色越明显。

### B. 宝石与水晶
*   **MatCap**: 使用高对比度的 MatCap 模拟复杂折射。
*   **折射**: 使用 CommandBuffer 获取背景图（GrabPass）并扰动 UV，模拟透射。
