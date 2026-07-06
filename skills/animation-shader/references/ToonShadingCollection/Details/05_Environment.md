# Environment & Rim (环境与边缘光)

## 1. Indirect Reflection (环境反射)

卡通渲染通常弱化物理真实的反射，转而追求风格化的金属质感。

### A. 极简 Reflection Probe / Cubemap
*   **做法**: 使用精度极低、模糊的 Cubemap 或 Reflection Probe。
*   **风格**: 避免写实环境的割裂感，仅提供基本的环境色倾向（如《战双》）。反射贴图通常极其简化（几道区域光）。

### B. MatCap 伪反射 (MatCap Reflection)
*   **做法**: 使用 MatCap 贴图模拟金属反射（如《原神》金属）。
*   **原理**: 
    ```glsl
    // View Space Normal based UV
    float3 viewNormal = mul((float3x3)UNITY_MATRIX_V, worldNormal);
    float2 uv = viewNormal.xy * 0.5 + 0.5;
    fixed3 reflection = tex2D(_MatCapTex, uv).rgb;
    ```
*   **优点**:
    *   **形状可控**: 美术直接绘制理想的高光/反射形状，不再依赖物理光源位置。
    *   **层次丰富**: 可以在 MatCap 中画出中心亮、边缘暗、最外层又亮的复杂层次。
*   **缺点**: 视角固定，无法反映真实环境变化（但风格化渲染通常忽略这一点）。

### C. 边缘光模拟反射
*   **做法**: 类似于《碧兰幻想》，利用边缘光（Rim Light）配合材质边缘压暗，模拟金属边缘的反光感，无需真正的反射计算。

## 2. Rim Light (边缘光/勾边光)

边缘光用于在物体边缘勾勒轮廓，常用于模拟逆光效果或提升角色与背景的对比度。

### A. 基础算法
基于菲涅尔效应 (Fresnel)。
*   **公式**: `rim = 1.0 - saturate(dot(viewDir, normal));`
*   **硬边化**: `rim = smoothstep(threshold, threshold + feather, rim);`

### B. 出现条件控制
*   **亮部/暗部限制**:
    *   **仅亮部**: `rim *= saturate(dot(normal, lightDir));` （增强受光面轮廓）。
    *   **仅暗部**: `rim *= (1.0 - saturate(dot(normal, lightDir)));` （模拟逆光透射）。
*   **方向性 (Directional Rim)**: 仅在主光方向（或特定方向）产生边缘光。
    ```glsl
    // 偏移法线采样
    float rimDot = dot(normal, lightDir + offsetDir);
    ```

### C. 颜色设计
*   **环境色**: 使用环境光颜色作为 Rim Color，使角色融入环境。
*   **补光色**: 使用主光的对补色。
*   **双色**: 左右两侧使用不同的边缘光颜色。

### D. 特殊问题处理
*   **双面渲染**: 对于双面渲染的物体（如裙摆内部），`dot(N, V)` 可能为负，导致全亮。
    *   *修正*: 使用 `1.0 - abs(dot(viewDir, normal))`。
*   **屏幕空间边缘光 (Screen Space Rim)**:
    *   **原理**: 类似于深度描边，通过偏移屏幕坐标采样深度图来计算边缘光。
    *   **优点**: **等宽**，不会像菲涅尔算法那样在平坦表面出现大面积反光（如《原神》的均匀边缘光）。
    *   **实现**: 向 View-Space 法线方向偏移 UV 采样深度，若深度差大于阈值则为边缘。

### E. 遮蔽 (Masking)
*   **AO 遮蔽**: 使用 AO 贴图遮蔽褶皱深处的边缘光，防止“发光褶皱”。
*   **Shadow 遮蔽**: 处于阴影（ShadowMap）中的物体是否应该有边缘光？通常保留，但需压暗。
