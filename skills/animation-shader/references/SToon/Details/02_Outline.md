# Dynamic Outline (动态描边)

SToon 的描边功能通过一个专门的 Pass (`Pass "ExtraPrePass"`) 实现。它不仅支持传统的背面膨胀，还引入了基于柏林噪点（Perlin Noise）的动态抖动，模拟手绘线条的不稳定性。

## 1. Implementation Approach (实现方式)

*   **Technique**: Inverted Hull (背面膨胀)。
*   **Cull**: `Cull Front` (剔除正面，只渲染背面)。
*   **ZWrite**: `On`。
*   **Blend**: `One Zero` (覆盖)。

## 2. Dynamic Noise Logic (动态噪点逻辑)

这是该 Shader 最独特的部分。它在 Vertex Shader 中使用噪点函数偏移顶点位置或法线，使描边线条看起来在“抖动”或“游动”。

### Code Analysis (Vertex Function)
```glsl
VertexOutput VertexFunction( VertexInput v )
{
    // ...
    // 1. 计算时间偏移 UV
    // _OutlineDynamicSpeed 控制噪点滚动的速度
    float2 temp_cast_1 = (( ( _TimeParameters.x ) * _OutlineDynamicSpeed )).xx;
    float2 texCoord591 = v.ase_texcoord.xy * float2( 1,1 ) + temp_cast_1;
    
    // 2. 采样单纯形噪点 (Simplex Noise)
    // snoise 返回 -1 到 1，这里重映射到 0 到 1
    float simplePerlin2D590 = snoise( texCoord591 * _OutlineNoiseScale );
    simplePerlin2D590 = simplePerlin2D590 * 0.5 + 0.5;
    
    // 3. 应用噪点强度
    // staticSwitch606 是应用了噪点后的挤出方向向量
    #ifdef _USEDYNAMICOUTLINE_ON
        // 噪点值 * 强度 * 原始法线/位置
        float3 staticSwitch606 = ( ( simplePerlin2D590 * _OutlineNoiseIntesity ) * staticSwitch57 );
    #else
        float3 staticSwitch606 = staticSwitch57;
    #endif

    // 4. 应用距离自适应和宽度
    // lerpResult59 是基于 Adaptive Thickness 的缩放因子
    float3 staticSwitch365 = ( lerpResult59 * ( staticSwitch606 * _Thicnkess ) );

    // 5. 应用到顶点位置
    v.vertex.xyz += staticSwitch365;
    
    // ...
}
```

### Key Parameters (关键参数)
*   `_OutlineDynamicSpeed`: 控制 UV 滚动的速度。如果为 0，噪点是静止的（像一张固定的皱纸）。如果不为 0，线条会像 boiling lines (沸腾线) 动画一样动起来。
*   `_OutlineNoiseScale`: 噪点的频率。值越高，线条抖动越细碎；值越低，线条波浪越宽。
*   `_OutlineNoiseIntesity`: 抖动的幅度。

## 3. Outline Types (挤出类型)
通过 `_OutlineType` 关键字控制挤出方向 `staticSwitch57`：
1.  **Normal**: 沿法线方向挤出（最常用，适合平滑物体）。
2.  **Position**: 沿顶点位置方向挤出（适合原点在中心的球体状物体）。
3.  **UVBaked**: 使用 `TEXCOORD3` 的 xy 作为挤出方向。这允许美术在建模软件中将平滑法线烘焙到 UV3 中，从而解决硬边模型断裂的问题。

## 4. Fragment Shader
*   描边颜色 `_OutlineColor` 可以叠加纹理 `_MainTex` (通过 `_OutlineTextureStrength` 控制)，让描边不仅仅是纯色，可以带有材质原本的纹理细节。
