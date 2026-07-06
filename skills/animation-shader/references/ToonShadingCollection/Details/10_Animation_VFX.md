# Animation & VFX (动画与特效)

卡通渲染不仅仅是静态的 Shader，还包括动态的动画表现和特效处理。

## 1. Visual Effects (特效表现)

### A. 运动模糊 (Motion Blur)
*   **问题**: 传统的全屏运动模糊会让画面变脏，不符合赛璐璐的清爽感。
*   **方案 (Smear Frames)**: 模拟 2D 动画中的“涂抹帧”。
    *   *网格变形*: 在 Vertex Shader 中沿运动方向拉伸顶点。
    *   *模型替换*: 也是《罪恶装备》方案。在攻击瞬间替换为专用的、夸张拉伸的“残影模型”，持续 1-2 帧。
    ```glsl
    // Smear Shader Logic
    float3 velocity = _ObjectPosition - _PreviousPosition; // 需要 C# 传递上一帧位置
    float noise = tex2Dlod(_NoiseMap, v.vertex.xy).r;
    v.vertex.xyz -= velocity * _SmearStrength * noise; // 反向拉伸顶点
    ```

### B. 不透明特效 (Opaque VFX)
*   **风格**: 很多卡通特效（如火焰、爆炸、刀光）倾向于使用**不透明**的模型+边缘光/溶解效果，而不是半透明粒子。
*   **优势**: 风格统一（像画出来的），且解决了半透明排序和过曝问题。

### C. 深度调整 (Depth Offset)
*   **格斗游戏技巧**: 在近战攻击时，强制将攻击者的深度前移（Z-Bias），防止手脚穿模到受击者身体里，保证视觉上的清晰打击感。

## 2. Animation (角色动画)

### A. 关节修正 (Joint Correction)
*   **辅助骨骼/BlendShape**: 当肘部或膝盖弯曲超过 90 度时，启动辅助骨骼或 BlendShape 修正模型体积，防止关节塌陷像“折断的管子”。

### B. 有限帧动画 (Limited Animation)
*   **抽帧 (Stepped Animation)**: 故意降低角色动画的更新频率（如每秒 12 帧或 15 帧），模拟传统 2D 动画的“一拍二”或“一拍三”节奏，而摄像机和特效保持 60 帧流畅。
    *   *实现*: 取消动画的线性插值（Linear Interpolation），改用阶跃（Step）更新。

### C. 夸张变形 (Deformation)
*   **骨骼缩放**: 在攻击瞬间瞬间放大拳头或武器（通过骨骼缩放），增强打击力度和透视感（勇者透视）。

## 3. Facial Expressions (表情动画)

### A. 方案选择
*   **BlendShape (形态键)**: 主流方案。适合制作特定的、非物理的 2D 夸张表情（如嘴巴移到侧面）。
*   **骨骼驱动**: 适合写实风格或需要复用的系统，但在表现极端“颜艺”时不如 BlendShape 灵活。
*   **贴图更换**: 适合 Q 版角色或特殊的漫符表情（如眼睛变成蚊香圈）。

### B. 视角修正 (View-Dependent Deformation)
*   **问题**: 二次元脸型在侧面或俯视时往往很难看（嘴巴突兀、眼睛变形）。
*   **方案**: 根据相机角度，动态调整面部骨骼或 BlendShape。
    *   *侧脸修正*: 当相机转到侧面时，将嘴巴向后移（收缩），使其不突兀；或将眼睛向后倾斜，保持“眉清目秀”的立体感。

## 4. FOV Adaptation (视角适应)

### A. 面部压扁
*   **原理**: 在透视投影下，鼻子和嘴巴容易显得过长（狗嘴效应）。
*   **Trick**: 在 Shader 中根据视角动态“压扁”面部的 Z 轴深度，模拟长焦镜头的平整感，同时保留边缘轮廓。

### B. 边缘畸变修正
*   **问题**: 在宽屏游戏中，屏幕边缘的角色会被透视拉伸变形（变胖）。
*   **方案 (Genshin Team UI)**: 修改投影矩阵（Projection Matrix），使边缘角色的透视中心向屏幕中心偏移。
    ```glsl
    // Unity Shader 代码示例
    float4x4 PMatrix = UNITY_MATRIX_P;
    PMatrix[0][2] = _ShiftX; // X方向偏移
    PMatrix[1][2] = _ShiftY; // Y方向偏移
    o.pos = mul(PMatrix, positionVS);
    ```
