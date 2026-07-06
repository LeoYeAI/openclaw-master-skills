# Outline (描边)

RToon 使用经典的 **Inverted Hull (背面膨胀)** 技术来实现描边，并增加了一些独特的动态和噪点功能来模拟手绘感。

## 1. Properties (参数)

*   `_OutlineWidth` ("Width"): 全局描边宽度。
*   `_OutlineWidthControl` ("Width Control", 2D): 使用贴图控制局部描边宽度（如发梢变细）。
*   `_OutlineExtrudeMethod` ("Extrude Method"):
    *   **Normal**: 沿法线膨胀（标准做法，适合圆滑物体）。
    *   **Origin**: 沿物体中心膨胀（适合硬表面或分离的机械结构）。
*   `_OutlineOffset`: 整体偏移描边位置。
*   `_OutlineZPostionInCamera`: **[重要]** 调整描边在相机空间的 Z 值。用于解决描边遮挡物体本身的问题（Z-Fighting 或看起来像浮在表面）。
*   `_DoubleSidedOutline`: 是否双面渲染描边。
*   `_OutlineColor` ("Color"): 描边颜色。
*   `_MixMainTexToOutline`: 将主贴图颜色混合到描边中（让描边不那么生硬）。
*   `_LightAffectOutlineColor`: 描边颜色是否受光照影响（变暗）。

### 动态效果
*   `_NoisyOutlineIntensity`: 静态噪点强度，使线条看起来不直。
*   `_DynamicNoisyOutline`: **[特色]** 动态噪点，使线条像逐帧动画一样抖动。
*   `_OutlineWidthAffectedByViewDistance`: 随距离调整宽度（防止远处于变成一团黑，或近处太粗）。

## 2. Vertex Color Control (顶点色控制)

RToon 强依赖顶点色来微调描边：
*   **Blue Channel (蓝色通道)**: 控制描边宽度。
    *   值 `1.0` (白/蓝): 原始宽度。
    *   值 `0.0` (黑): 宽度为 0（隐藏描边）。
    *   *公式*: `FinalWidth = _OutlineWidth * (1.0 - vertexColor.b)` (注意：这里逻辑似乎是反的，或者是 `1.0` 代表受控程度？需看代码确认)。

## 3. Implementation (实现原理)

位于 `D_Default_URP.shader` 的 `Pass "Outline"`。

### Vertex Shader Logic

```glsl
Varyings LitPassVertex(Attributes input)
{
    // ... (DOTS / Instancing Setup) ...

    // 1. 距离缩放计算
    half RTD_OB_VP_CAL = distance(objPos.rgb, _WorldSpaceCameraPos);
    
    // 2. 顶点色宽度控制
    // 注意逻辑: 如果 vertexColor.b 越大，宽度越小 (1.0 - b)
    // 所以如果不涂色(0.0)，则是满宽度。涂了蓝色(1.0)，描边消失。
    half RTD_OL_VCRAOW_OO;
    if (!_VertexColorBlueAffectOutlineWitdh) {
        RTD_OL_VCRAOW_OO = _OutlineWidth;
    } else {
        RTD_OL_VCRAOW_OO = _OutlineWidth * (1.0 - output.vertexColor.b);
    }

    // 3. 视距修正
    half RTD_OL_OLWABVD_OO;
    if (!_OutlineWidthAffectedByViewDistance) {
        RTD_OL_OLWABVD_OO = RTD_OL_VCRAOW_OO;
    } else {
        // 随距离限制最大宽度
        RTD_OL_OLWABVD_OO = clamp(RTD_OL_VCRAOW_OO * RTD_OB_VP_CAL, RTD_OL_VCRAOW_OO, _FarDistanceMaxWidth);
    }

    // 4. 动态噪点 (Dynamic Noisy Outline)
    // 生成随机 UV 偏移
    #if N_F_DNO_ON
        // ... 计算 sin/cos 旋转 UV ...
        half2 RTD_OL_DNOL_OO = _8530; // 旋转后的 UV
    #else
        half2 RTD_OL_DNOL_OO = output.uv;
    #endif
    
    // 生成随机数 _1283
    // ...
    
    // 5. 最终挤出
    // 膨胀方向选择
    float3 _OEM = (!_OutlineExtrudeMethod) ? _LBS_CD_Normal : normalize(_LBS_CD_Position.xyz);
    
    // 计算最终宽度 (结合贴图控制 和 噪点)
    half RTD_OL = (RTD_OL_OLWABVD_OO * 0.01) * _OutlineWidthControl_var.r * lerp(1.0, _1283, _NoisyOutlineIntensity);
    
    // 应用挤出
    output.positionCS = mul(GetWorldToHClipMatrix(), mul(GetObjectToWorldMatrix(), float4((_LBS_CD_Position.xyz + _OutlineOffset.xyz * 0.01) + _OEM * RTD_OL, 1.0)));

    // 6. Z-Bias (防止穿模)
    output.positionCS.z -= _OutlineZPostionInCamera * 0.0005;

    return output;
}
```

### Fragment Shader Logic

*   **混色**:
    ```glsl
    // 混合主贴图
    half3 RTD_MMTTO_OO = _MixMainTexToOutline ? (_OutlineColor.rgb * _MainTex_var.rgb) : _OutlineColor.rgb;
    
    // 混合光照
    half3 RTD_OL_LAOC_OO = _LightAffectOutlineColor ? lerp(0, RTD_MMTTO_OO, lightColor.rgb) : RTD_MMTTO_OO;
    ```
*   **Fog**: 描边也会正确应用雾效。

## 4. Analysis (分析)

*   **反向控制**: 顶点色蓝色通道控制逻辑是 `1.0 - b`，这意味着**涂蓝色是消除描边**，默认黑色是保留描边。这符合直觉（默认不需要处理，特殊部位涂色消除）。
*   **动态噪点**: 通过在 Vertex Shader 中扰动挤出距离，实现了类似《Ed, Edd n Eddy》那种线条抖动的效果，非常适合手绘风格游戏。
*   **性能**: 单独 Pass 绘制，会增加 DrawCall 和顶点处理开销。
