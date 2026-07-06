# Double Shade with Feather

This is the standard shading mode of UTS2. It simulates the anime production workflow where colors are defined as "Base", "1st Shadow", and "2nd Shadow".

## 1. The Three Layers
The final color is a composition of three distinct states based on lighting intensity:

1.  **Base Color**: The fully lit area.
    *   **Properties**: `_BaseColor` (Tint), `_MainTex` (Texture).
    *   **Condition**: High light intensity (NdotL > Threshold).
2.  **1st Shade**: The primary shadow.
    *   **Properties**: `_1st_ShadeColor`, `_1st_ShadeMap`.
    *   **Condition**: Medium light intensity.
3.  **2nd Shade**: The darkest shadow (often used for occlusion or deep folds).
    *   **Properties**: `_2nd_ShadeColor`, `_2nd_ShadeMap`.
    *   **Condition**: Low light intensity.

## 2. Feathering & Steps
UTS2 uses a "Step" and "Feather" system to control the transition between these layers.

### Properties
*   **`_BaseColor_Step`**: The light threshold (0-1) where Base Color transitions to 1st Shade.
*   **`_BaseShade_Feather`**: The softness of this edge.
    *   `0.0001`: Sharp Anime Edge.
    *   `1.0`: Smooth Soft Shading.
*   **`_ShadeColor_Step`**: The threshold between 1st Shade and 2nd Shade.
*   **`_1st2nd_Shades_Feather`**: The softness of the 2nd shade transition.

## 3. Position Maps (Fixed Shadows)
To ensure characters look perfect (e.g., preventing ugly nose shadows), UTS2 allows fixing shadows to specific areas regardless of light direction.

*   **`_Set_1st_ShadePosition`**: 1st Shade Fix Map.
*   **`_Set_2nd_ShadePosition`**: 2nd Shade Fix Map.
*   **Principle**: These maps modify the *threshold* of the shading calculation. A black pixel in this map forces the shader to think the light intensity is lower than it actually is.

### Implementation Logic (Pseudo-Code)
The shader combines the dynamic NdotL (HalfLambert) with the static Position Map to calculate a mask.

**Call Site**: `fragDoubleShadeFeather` in `UniversalToonBodyDoubleShadeWithFeather.hlsl`.

```hlsl
// 1. Calculate Basic Light Response (Half Lambert)
// Ranges from 0 (Dark) to 1 (Lit)
float HalfLambert = 0.5 * dot(normal, lightDir) + 0.5;

// 2. Sample Position Map
// 1.0 (White) = Normal lighting behavior
// 0.0 (Black) = Force Shadow
float PosMap1 = tex2D(_Set_1st_ShadePosition, uv).r;

// 3. Calculate 1st Shade Mask
// This formula maps the Light Level and Position Map into a 0-1 mask
// based on the Step and Feather settings.
float shadowMask1 = saturate(
    (1.0 + ( (HalfLambert - (_BaseColor_Step - _BaseShade_Feather)) 
    * ((1.0 - PosMap1) - 1.0) ) 
    / (_BaseColor_Step - (_BaseColor_Step - _BaseShade_Feather)))
);

// 4. Calculate 2nd Shade Mask (Similar logic)
float PosMap2 = tex2D(_Set_2nd_ShadePosition, uv).r;
float shadowMask2 = saturate(
    (1.0 + ( (HalfLambert - (_ShadeColor_Step - _1st2nd_Shades_Feather)) 
    * ((1.0 - PosMap2) - 1.0) ) 
    / (_ShadeColor_Step - (_ShadeColor_Step - _1st2nd_Shades_Feather)))
);

// 5. Combine Layers
// If shadowMask1 is 1.0, we see Base Color. If 0.0, we see Shade.
float3 ColorWith1st = lerp(_1st_ShadeColor, _BaseColor, shadowMask1);
float3 FinalColor = lerp(_2nd_ShadeColor, ColorWith1st, shadowMask2);
```

## 4. System Shadows
UTS2 integrates with Unity's shadow system (Cast Shadows/Receive Shadows).
*   **`_Set_SystemShadowsToBase`**: Controls how much the received shadows (from other objects) affect the toon shading.
*   **`_Tweak_SystemShadowsLevel`**: Fine-tunes the intensity of received shadows.
*   **Implementation**: The `HalfLambert` value is multiplied by the system shadow attenuation (`shadowAttenuation`) before the mask calculation, effectively treating cast shadows as "darker light".
